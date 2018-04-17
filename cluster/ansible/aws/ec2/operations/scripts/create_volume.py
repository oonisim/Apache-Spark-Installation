#!/usr/bin/python
import boto3, time, copy, json
from sets import Set
from utility import json_dump
import ec2_common, ec2_instance, ec2_volume, ec2_ebs

#--------------------------------------------------------------------------------
# Detach volumes from the taget instances
#--------------------------------------------------------------------------------
ticket = {
    "regionName": "us-east-2",
    "filters"      : [
        {
            "Name": "tag:Name",
            "Values": ["gitlab-dr"],
        },
        {
            "Name": "instance-id",
            "Values": ["i-0cc705bce867c7fe6"],
        },
    ]
}

devices = ec2_volume.list_instance_nonroot_ebs_volumes(ticket)
#devices = ec2_volume.list_instance_root_ebs_volumes(ticket)
print "Non root volumes is " + json_dump(devices)

volumes = []
for device in devices:
    volume = {}
    volume["instanceId"]    = "i-0cc705bce867c7fe6"
    volume["deviceName"]    = device["DeviceName"]
    volume["volumeId"]      = device["Ebs"]["VolumeId"]
    volumes.extend([volume])

if len(volumes) <= 0:
    print "No devices"
    quit()

ticket["volumes"] = volumes
response = ec2_volume.detach_volumes(ticket)
print "Detach response " + json_dump(response)


#--------------------------------------------------------------------------------
# Create volumes
#--------------------------------------------------------------------------------

ticket = {
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


reply = ec2_ebs.create_volumes_from_snapshots(ticket)
print "--------------------------------------------------------------------------------"
print "create_volume reply "  + json_dump(reply)

"""
{
    "event": "volume_available",
    "filters": [
        {
            "Name": "status",
            "Values": [
                "available"
            ]
        }
    ],
    "regionName": "us-east-2",
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
"""

#--------------------------------------------------------------------------------
# Attach volumes ticket
#--------------------------------------------------------------------------------
"""
"regionName": "us-east-2",
"volumes": [
    {
        "deviceName": "/dev/sdc",
        "instanceId": "i-0cc705bce867c7fe6",
        "volumeId": "vol-0f67c39f4f875f7b4"
    },
    ...
]

"""

ticket = copy.deepcopy(reply)
volumes = ticket['volumes']
for v in volumes:
    v['instanceId'] = 'i-0cc705bce867c7fe6'

response = ec2_volume.attach_volumes(ticket)
print json_dump(response)

