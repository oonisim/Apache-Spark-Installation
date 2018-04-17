import sys, time, copy, json, inspect
from sets import Set
try:
    import boto3
except ImportError:
    print "failed=True msg='boto required for this module'"
    sys.exit(1)
from utility import json_dump
import ec2_common, ec2_instance

#================================================================================
# Volume
#================================================================================
def monitor_volume(ticket):
    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"
    while(True):
        volumeIds = []
        for volume in ticket["volumes"]:
            volumeIds.extend([volume["volumeId"]])

        response = ec2_common.getEC2(ticket).meta.client.describe_volumes(
            VolumeIds = volumeIds
        )
        print "---------------------------------------------------"
        print json_dump(response)
        time.sleep(5)
    return None

def wait_volumes(ticket):
    """
    :param ticket: 
    {
        "regionName": "us-east-2", 
        "event": "volume_available", 
        "filters": [
            {
                "Name": "status", 
                "Values": [
                    "available"
                ]
            }
        ], 
        "volumes": [
            {
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
                "volumeId": "vol-0f11c4abffcf9521a", 
                "volumeType": "standard"
            }
        ]
    }

    :return: 
    """
    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"

    region = ticket["regionName"]
    volumeIds = []
    for volume in ticket["volumes"]:
        volumeIds.extend([volume["volumeId"]])

    wait_args = {}
    wait_args["VolumeIds"]  = volumeIds
    wait_args["Filters"]    = ticket.get("filters")
    ec2_common.wait_resource(region, ticket["event"], **wait_args)
    return(ec2_common.getEC2(ticket).meta.client.describe_volumes(
        VolumeIds=volumeIds
    ))

def list_volumes(ticket):
    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"

    volumes = ec2_common.getEC2(ticket).meta.client\
        .describe_volumes(
            Filters=ticket.get("filters")
        )
    return(volumes["Volumes"])


def list_instance_ebs_volumes(ticket):
    volumes = []

    instances = ec2_instance.list_instances(ticket)
    if instances is not None:
        for instance in instances:
            for device in instance["BlockDeviceMappings"]:
                if device.get("Ebs", None) is None:
                    # skip non-EBS volumes
                    continue
                else:
                    volumes.extend([device])
                    print "Found EBS volume %s on instance %s" % (
                        device["Ebs"]["VolumeId"],
                        instance["InstanceId"]
                    )
    # endif
    return volumes

def _extract_root_ebs_volumes(instances, invert=False):
    rootVolumes = []
    nonRootVolumes = []

    if instances is not None:
        for instance in instances:
            rootDevice = instance["RootDeviceName"]
            for device in instance["BlockDeviceMappings"]:
                if device.get("Ebs", None) is None:
                    # skip non-EBS volumes
                    continue
                else:
                    if(device.get("DeviceName") == rootDevice):
                        rootVolumes.extend([device])
                        print "Found EBS root volume %s on instance %s" % (
                            device["Ebs"]["VolumeId"],
                            instance["InstanceId"]
                        )
                    else:
                        nonRootVolumes.extend([device])
                        print "Found EBS non root volume %s on instance %s" % (
                            device["Ebs"]["VolumeId"],
                            instance["InstanceId"]
                        )
            # end-for
    # end-for
    if invert:
        return nonRootVolumes
    else:
        return rootVolumes

def list_instance_root_ebs_volumes(ticket):
    return(_extract_root_ebs_volumes(ec2_instance.list_instances(ticket), False))

def list_instance_nonroot_ebs_volumes(ticket):
    return(_extract_root_ebs_volumes(ec2_instance.list_instances(ticket), True))


#================================================================================
# Volume Detach
#================================================================================
def detach_volume(ticket):
    """
    :param ticket: A dictionary specification:
    
    {
        "regionName": "us-east-2", 
        "volumeId": "vol-00d95ca3ca22d9afb", 
    }
    
    :return: Reponse from the Boto3 API.
    {
        "ResponseMetadata": {
            "HTTPHeaders": {
                "content-type": "text/xml;charset=UTF-8", 
                "date": "Tue, 25 Jul 2017 06:32:07 GMT", 
                "server": "AmazonEC2", 
                "transfer-encoding": "chunked", 
                "vary": "Accept-Encoding"
            }, 
            "HTTPStatusCode": 200, 
            "RequestId": "e35dcbb1-5f21-4eee-a135-e660070a65df", 
            "RetryAttempts": 0
        }, 
        "VolumeId": "vol-00d95ca3ca22d9afb",
        "State": "detaching", 
        "Device": "/dev/sdf", 
        "InstanceId": "i-0cc705bce867c7fe6", 
        "AttachTime": "2017-07-25T00:27:57+00:00"
    }

    """
    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"
    response = ec2_common.getEC2(ticket).meta.client.detach_volume(
        VolumeId = ticket["volumeId"],
        Force = True
    )
    return(response)

def detach_volumes(ticket):
    """
    :param ticket: 
    {
        "regionName": "us-east-2", 
        "volumes": [
            {
                "deviceName": "/dev/sdc", 
                "instanceId": "i-0cc705bce867c7fe6", 
                "volumeId": "vol-0f67c39f4f875f7b4"
            }, 
            ...
        ]
    }
    :return: Boto3 API response.
    {
        "ResponseMetadata": {
            "HTTPHeaders": {
                "content-type": "text/xml;charset=UTF-8", 
                "date": "Tue, 25 Jul 2017 06:43:00 GMT", 
                "server": "AmazonEC2", 
                "transfer-encoding": "chunked", 
                "vary": "Accept-Encoding"
            }, 
            "HTTPStatusCode": 200, 
            "RequestId": "f8b2abb2-d670-435a-b1fb-b04e951d3ac5", 
            "RetryAttempts": 0
        }, 
        "Volumes": [
            {
                "Attachments": [], 
                "AvailabilityZone": "us-east-2c", 
                "CreateTime": "2017-07-20T04:39:14.088000+00:00", 
                "Encrypted": true, 
                "KmsKeyId": "arn:aws:kms:us-east-2:752398066937:key/****", 
                "Size": 8, 
                "SnapshotId": "", 
                "State": "available", 
                "VolumeId": "vol-0f67c39f4f875f7b4", 
                "VolumeType": "standard"
            }, 
            ...
        ]
    }

    """
    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"

    volumes = ticket["volumes"]
    if (volumes is not None and len(volumes) > 0):
        print "Volumes to detach " + json_dump(volumes)
        for volume in volumes:
            order = copy.copy(ticket)
            order["volumeId"] = volume["volumeId"]
            response = detach_volume(order)

        print "Detach volumes response: " + json_dump(response)

        ticket["event"] = "volume_available"
        ticket["filters"]= [
            {
                "Name" : "status",
                "Values": [
                    "available"
                ]
            }
        ]
        return(wait_volumes(ticket))
    else:
        print "No volume to detach."
        return []

#================================================================================
# Volume Attach
#================================================================================
def attach_volume(ticket):
    """
    :param ticket: Dictionary specification.
    {
        "regionName": "us-east-2", 
        "volumeId": "vol-0f67c39f4f875f7b4", 
        "deviceName": "/dev/sdc", 
        "instanceId": "i-0cc705bce867c7fe6", 
    }
    :return: Reponse from the Boto3 API.
    {
        "ResponseMetadata": {
            "HTTPHeaders": {
                "content-type": "text/xml;charset=UTF-8", 
                "date": "Tue, 25 Jul 2017 06:32:11 GMT", 
                "server": "AmazonEC2", 
                "transfer-encoding": "chunked", 
                "vary": "Accept-Encoding"
            }, 
            "HTTPStatusCode": 200, 
            "RequestId": "c18fa293-c407-41fa-aa9a-e6a9e02b4b03", 
            "RetryAttempts": 0
        }, 
        "InstanceId": "i-0cc705bce867c7fe6", 
        "VolumeId": "vol-0f67c39f4f875f7b4"
        "Device": "/dev/sdc", 
        "State": "attaching", 
        "AttachTime": "2017-07-25T06:32:11.828000+00:00"
    }

    """
    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"
    volume = ec2_common.getEC2(ticket).Volume(ticket["volumeId"])
    try:
        response = volume.attach_to_instance(
            Device      = ticket["deviceName"],
            InstanceId  = ticket["instanceId"]
        )
        volume.load()
        return(response)

    except Exception as e:
        print e
#        print("Attach eexception %s: %s" % (e.error_code, e.error_message))

def attach_volumes(ticket):
    """
    :param ticket: 
    {
        "regionName": "us-east-2", 
        "volumes": [
            {
                "deviceName": "/dev/sdc", 
                "instanceId": "i-0cc705bce867c7fe6", 
                "volumeId": "vol-0f67c39f4f875f7b4"
            }, 
            ...
        ]
    }
    :return: 
    {
        "ResponseMetadata": {
            "HTTPHeaders": {
                "content-type": "text/xml;charset=UTF-8", 
                "date": "Tue, 25 Jul 2017 06:43:10 GMT", 
                "server": "AmazonEC2", 
                "transfer-encoding": "chunked", 
                "vary": "Accept-Encoding"
            }, 
            "HTTPStatusCode": 200, 
            "RequestId": "07484fe4-71b3-4cad-9584-0badabf5ea35", 
            "RetryAttempts": 0
        }, 
        "Volumes": [
            {
                "Attachments": [
                    {
                        "AttachTime": "2017-07-25T06:43:02+00:00", 
                        "DeleteOnTermination": false, 
                        "Device": "/dev/sdc", 
                        "InstanceId": "i-0cc705bce867c7fe6", 
                        "State": "attached", 
                        "VolumeId": "vol-0f67c39f4f875f7b4"
                    }
                ], 
                "AvailabilityZone": "us-east-2c", 
                "CreateTime": "2017-07-20T04:39:14.088000+00:00", 
                "Encrypted": true, 
                "KmsKeyId": "arn:aws:kms:us-east-2:752398066937:key/6fc8edd5-c63d-4ceb-9483-573d3f543240", 
                "Size": 8, 
                "SnapshotId": "", 
                "State": "in-use", 
                "VolumeId": "vol-0f67c39f4f875f7b4", 
                "VolumeType": "standard"
            }, 
            ...
        ]
    }
    """

    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"
    volumeIds = []

    volumes = ticket["volumes"]
    if (volumes is not None and len(volumes) > 0):
        print "Volumes to attach " + json_dump(volumes)
        for volume in volumes:
            order = copy.copy(ticket)
            order["instanceId"] = volume["instanceId"]
            order["volumeId"] = volume["volumeId"]
            order["deviceName"] = volume["deviceName"]
            response = attach_volume(order)
            print "Attach response: " + json_dump(response)

        ticket["event"] = "volume_available"
        ticket["filters"]=  [
            {
                "Name": "status",
                "Values": [
                    "in-use"
                ]
            }
        ]
        # Boto3 waiter Not working ...
        #return(wait_volumes(ticket))
        for volume in volumes:
            volumeIds.extend([volume["volumeId"]])
            v = ec2_common.getEC2(ticket).Volume(volume["volumeId"])
            while v.state != "in-use":
                v.load()

            loop = True
            while loop:
                loop = False

                v = ec2_common.getEC2(ticket).Volume(volume["volumeId"])
                v.load()
                attachments = v.attachments
                for attachment in attachments:
                    if attachment["Device"] == volume["deviceName"]:
                        if attachment["State"] != "attached":
                            print "Volume " + attachment["VolumeId"]+ " on " + attachment["Device"] + " is in " + attachment["State"]
                            loop = True
                            time.sleep(5)



        return(ec2_common.getEC2(ticket).meta.client.describe_volumes(
            VolumeIds=volumeIds
        ))

    else:
        print "No volume to attach."
        return []

#================================================================================
# Volume Delete
#================================================================================
def delete_volumes(ticket):
    """
    :param ticket: 
    {
        "regionName": "us-east-2", 
        "volumes": [
            {
                "volumeId": "vol-00d95ca3ca22d9afb"
            },
            ...
        ]
    }
    :return: 
    
    """
    ticket = copy.deepcopy(ticket)

    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"

    volumes = ticket["volumes"]
    if (volumes is not None and len(volumes) > 0):
        print "Volumes to delete " + json_dump(volumes)
        for volume in volumes:
            response = ec2_common.getEC2(ticket).meta.client.delete_volume(
                VolumeId = volume["volumeId"],
            )
            print "Delete response: " + json_dump(response)

        ticket["event"] = "volume_available"
        ticket["filters"]= [
            {
                "Name" : "status",
                "Values": [
                    "deleted"
                ]
            }
        ]
#        print json_dump(wait_volumes(ticket))
        return (ticket)

    else:
        print "No volume to detach."
        return None
