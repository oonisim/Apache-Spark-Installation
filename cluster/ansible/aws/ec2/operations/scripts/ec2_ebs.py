import sys, time, copy, json, inspect
from sets import Set
try:
    import boto3
except ImportError:
    print "failed=True msg='boto required for this module'"
    sys.exit(1)
from utility import json_dump
import ec2_common, ec2_instance, ec2_volume

#================================================================================
# EBS Snapshot
#================================================================================

def list_snapshot(ticket):
    """
    http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_snapshots
    response = client.describe_snapshots(
        Filters=[
            {
                'Name': 'string',
                'Values': [
                    'string',
                ]
            },
        ],
        MaxResults=123,
        NextToken='string',
        OwnerIds=[
            'string',
        ],
        RestorableByUserIds=[
            'string',
        ],
        SnapshotIds=[
            'string',
        ],
        DryRun=True|False
    )
    [Bash]
    snapshots_to_delete=($(aws --region us-east-1 ec2 describe-snapshots --owner-ids ***** --query 'Snapshots[?StartTime< `2017-07-25`].SnapshotId' --output text))
    echo "List of snapshots to delete: $snapshots_to_delete"
    
    # actual deletion
    for snap in $snapshots_to_delete; do
        echo $snap
    done

    :param ticket: 
    :return: 
    """

exitStates = Set(["completed", "error"])
def wait_snapshot(ec2, snapshot):
    #    while snapshot.state not in exitStates :
    #        print snapshot.progress
    #        time.sleep(delay)
    #        snapshot.load()
    #
    #    if snapshot.state == "error":
    #        print "snapshot ERROR"
    #        raise RuntimeError("Snapshot [" + snapshot.id + "] failed.")
    #        quit()
    waiter = ec2_common.getEC2(ticket).meta.client.get_waiter("snapshot_completed")

    # Set the timeout
    # Waiter timeout is 10 min (Boto default is delay=15 * max_attempts=40).
    waiter.config.delay = delay
    waiter.config.max_attempts = max_attempts
    waiter.wait(
        SnapshotIds=[
            snapshot.id
        ],
    )

def wait_snapshots(ticket):
    """
    
    :param ticket: 
    {
        "regionName": "us-east-2", 
        "snapshotIds": [
            "snap-0bc1e37dfead231be"
        ], 
    }

    :return: 
    """

    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"

    wait_args = {}
    wait_args["SnapshotIds"]  = ticket["snapshotIds"]
    ec2_common.wait_resource(ticket["regionName"], "snapshot_completed", **wait_args)
    return(ec2_common.getEC2(ticket).meta.client.describe_snapshots(
        SnapshotIds = ticket["snapshotIds"]
    ))

def create_snapshot(ticket):
    volume = ticket["volume"]
    snapshot = ec2_common.getEC2(ticket).create_snapshot(
        VolumeId    = volume["volumeId"],
        #Description = ticket.get("desc")
    )
    print "Snapshot [" + snapshot.id + "] under creation in " + ticket.get("regionName")

    #wait_snapshot(ticket)
    ec2_common.tag(ticket["regionName"], snapshot.id, volume["tags"])
    return(snapshot)

def create_snapshots(ticket):
    """
    :param ticket: Dictionary specification.
    {
        "regionName": "us-east-2",
        "volumes": [
            {
                "deviceName": "/dev/sdc", 
                "volumeId": "vol-0f67c39f4f875f7b4", 
                "tags": [
                    {
                        "Value": "/dev/sdc", 
                        "Key": "origin-deviceName"
                    }, 
                    ...
                ]
            }, 
            ...
        ], 
    }
    :return: 
    """

    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"
    snapshotIds = []
    ticket = copy.deepcopy(ticket)

    volumes = ticket["volumes"]
    if (volumes is not None and len(volumes) > 0):
        print "Volumes to snapshot " + json_dump(volumes)
        for volume in volumes:
            order = {}
            order["regionName"] = ticket["regionName"]
            order["volume"]     = volume

            snapshot = create_snapshot(order)
            snapshotIds.extend([snapshot.id])
            volume["snapshotId"] = snapshot.id

        ticket["snapshotIds"] = snapshotIds
        json_dump(wait_snapshots(ticket))

        return(ticket)
    else:
        return(None)


def copy_snapshot(ticket):
    # EC2 resource of the destination region.
    response = ec2_common.getEC2(ticket).meta.client.copy_snapshot(
        # See https://github.com/boto/boto3/issues/886
        # DestinationRegion is not used actually.
        #DestinationRegion   = ticket["regionName"],
        SourceRegion        = ticket["srcRegionName"],
        SourceSnapshotId    = ticket["snapshot"]["snapshotId"],
    )
    target = ec2_common.getEC2(ticket).Snapshot(response.get("SnapshotId"))
    target.reload()
    print "Snapshot [" + target.id + "] under creation in " + ticket.get("regionName")
    ec2_common.tag(ticket["regionName"], target.id, ticket["snapshot"]["tags"])
    return(target)

def copy_snapshots(ticket):
    """
    
    :param ticket: 
    {
        "regionName":    "us-east-1",  <---------- Destination region. 
        "srcRegionName": "us-east-2"
        "snapshots": [
            {
                "deviceName": "/dev/sdc", 
                "snapshotId": "snap-01fa27fbf0498c739", 
                "tags": [
                    {
                        "Key": "origin-region", 
                        "Value": "us-east-2"
                    }, 
                    {
                        "Key": "origin-deviceName", 
                        "Value": "/dev/sdc"
                    }, 
                    ...
\                ], 
                "volumeId": "vol-0f67c39f4f875f7b4"
            },
            ...
        ], 
    }

    :return: 
    {
        "regionName": "us-west-2", 
        "srcRegionName": "us-east-2",

        "regionName": "us-west-2",    <---- Destination region where snapshots have been created by copy
        "snapshotIds": [              <---- Snapshots created by copy at the destination region.
            "snap-0838814c3a4b5d88f", 
            "snap-0cd05a68e534644ac"
        ], 
        "snapshots": [
            {
                "dstSnapshotId": "snap-0838814c3a4b5d88f", <----- Snapshot created by copy
                "snapshotId": "snap-01fa27fbf0498c739",    <----- Source snapshot for copy.
                "volumeId": "vol-0f67c39f4f875f7b4"        <----- Source volume of the source snapshot
                "deviceName": "/dev/sdc",                  <----- device name of the source volume
                "tags": [
                    {
                        "Key": "origin-region", 
                        "Value": "us-east-2"
                    }, 
                    {
                        "Key": "origin-deviceName", 
                        "Value": "/dev/sdc"
                    }, 
                    ...
                ], 
            }, 
            ...
    }

    """
    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"
    ticket = copy.deepcopy(ticket)
    dstSnapshotIds = []

    snapshots = ticket["snapshots"]
    if (snapshots is not None and len(snapshots) > 0):
        print "Snapshots to copy " + json_dump(snapshots)
        for snapshot in snapshots:
            order = {}
            order["srcRegionName"]  = ticket["srcRegionName"]
            order["regionName"]  = ticket["regionName"]
            order["snapshot"]       = snapshot
            target = copy_snapshot(order)

            dstSnapshotIds.extend([target.id])
            snapshot["dstSnapshotId"] = target.id

        ticket["regionName"]  = ticket["regionName"]
        ticket["snapshotIds"] = dstSnapshotIds
        print json_dump(wait_snapshots(ticket))

        for target in snapshots:
            ec2_common.tag(ticket["regionName"], target["dstSnapshotId"], target["tags"])

        return(ticket)
    else:
        return(None)

def create_volumes_from_snapshots(ticket):
    """
    Creates an EBS volume from a snapshot that can be attached to an instance in the same Availability Zone. 
    http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-creating-volume.html
    volume = ec2.create_volume(
        AvailabilityZone='string',
        Encrypted=True|False,
        KmsKeyId='string',
        Size=123,
        SnapshotId='string',
        VolumeType='standard'|'io1'|'gp2'|'sc1'|'st1',
        TagSpecifications=[
            {
                'ResourceType': 'instance'|'volume',
                'Tags': [
                    {
                        'Key': 'string',
                        'Value': 'string'
                    },
                ]
            },
        ]
    )
    :param ticket: 
    {
        "regionName": "us-east-2", 
        "snapshots": [
            {
                "deviceName": "/dev/sdb", 
                "snapshotId": "snap-03a49438c6485a4e1", 
                "srcSnapshotId": "snap-0e2f318bc176804e7", 
                "srcVolumeId": "vol-094812e2e62d7845e", 
                "volumeType": "standard",
                "availabilityZone": "us-east-2c", 
                "tags": [
                    {
                        "Key": "origin-region", 
                        "Value": "us-east-1"
                    }, 
                    {
                        "Key": "origin-device", 
                        "Value": "/dev/sdb"
                    }, 
                    {
                        "Key": "origin-volumeId", 
                        "Value": "vol-094812e2e62d7845e"
                    }
                ], 
            }
        ]
    }
    :return: 
    {
        "regionName": "us-east-2", 
        "volumes": [
            {
                "volumeId": "vol-0f11c4abffcf9521a", <---- Volume created
                "volumeType": "standard"
                "availabilityZone": "us-east-2c", 
                "deviceName": "/dev/sdb", 
                "snapshotId": "snap-03a49438c6485a4e1", 
                "srcSnapshotId": "snap-0e2f318bc176804e7", 
                "srcVolumeId": "vol-094812e2e62d7845e", 
                "tags": [
                    {
                        "Key": "origin-region", 
                        "Value": "us-east-1"
                    }, 
                    {
                        "Key": "origin-device", 
                        "Value": "/dev/sdb"
                    }, 
                    {
                        "Key": "origin-volumeId", 
                        "Value": "vol-094812e2e62d7845e"
                    }
                ], 
            }
        ]
    }
    """

    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"
    volumeIds = []

    ticket = copy.deepcopy(ticket)
    snapshots = ticket["snapshots"]
    for s in snapshots:
        volume = ec2_common.getEC2(ticket).create_volume(
            SnapshotId          = s["snapshotId"],
            AvailabilityZone    = s["availabilityZone"],
            VolumeType          = s["volumeType"],
            TagSpecifications=[
                {
                    'ResourceType': "volume",
                    'Tags': s["tags"]
                },
            ]
        )
        s["volumeId"] = volume.id
        volumeIds.extend([volume.id])

    ticket["volumes"] = ticket.pop("snapshots")
    ticket["event"] = "volume_available"
    ticket["filters"]= [
        {
            "Name" : "status",
            "Values": [
                "available"
            ]
        }
    ]
    print json_dump(ec2_volume.wait_volumes(ticket))
    return(ticket)


def delete_snapshot(ticket):
    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"
    snapshots = ticket["snapshots"]
    for s in snapshots:
        response = ec2_common.getEC2(ticket).meta.client.delete_snapshot(
            SnapshotId          = s["snapshotId"],
#            AvailabilityZone    = s["availabilityZone"],
#            VolumeType          = s["volumeType"],
#            TagSpecifications=[
#                {
#                    'ResourceType': "volume",
#                    'Tags': s["tags"]
#                },
#            ]
        )

