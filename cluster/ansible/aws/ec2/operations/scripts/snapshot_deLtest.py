#!/usr/bin/python
import boto3, time, copy, json
from sets import Set
from utility import json_dump
import ec2_common, ec2_instance, ec2_volume, ec2_ebs

DESCRIPTION                 = "Created by automated DR scri Test DR script on (DATE)"
SOURCE_REGION               = "us-east-1"
SOURCE_INSTANCE_ID          = "i-0a67bd361a2d14cd1"
SOURCE_INSTANCE_ID_FILTER   = "instance-id"
SOURCE_INSTANCE_NAME        = "test"
SOURCE_INSTANCE_NAME_FILTER = "tag:Name"
SOURCE_AVAILABILITY_ZONE    = "us-east-1d"

TARGET_REGION               = "us-east-2"
TARGET_INSTANCE_ID          = "i-0752254010c00f709"
TARGET_INSTANCE_ID_FILTER   = "instance-id"
TARGET_INSTANCE_NAME        = "test"
TARGET_INSTANCE_NAME_FILTER = "tag:Name"
TARGET_VOLUME_TYPE          = "standard"
TARGET_AVAILABILITY_ZONE    = "us-east-2b"

TSTMP=now.strftime("%Y-%m-%d %H:%M")

print "--------------------------------------------------------------------------------"
print "# List the non root EBS volumes to take snapshots of at source."
print "--------------------------------------------------------------------------------"
ticketSourceVolumes = {
    "regionName"    : SOURCE_REGION,
    "filters"       : [     # To identify the volumes to take snapshot of
        {
            "Name": SOURCE_INSTANCE_NAME_FILTER,
            "Values": [SOURCE_INSTANCE_NAME],
        },
        {
            "Name": SOURCE_INSTANCE_ID_FILTER,
            "Values": [SOURCE_INSTANCE_ID],
        },
    ]
}

sourceVolumes = ec2_volume.list_instance_nonroot_ebs_volumes(ticketSourceVolumes)
print "Non root volumes is " + json_dump(sourceVolumes)

print "--------------------------------------------------------------------------------"
print "# Take snapshots of the source instance volumes."
print "--------------------------------------------------------------------------------"
"""
{
    "regionName": "us-east-1", 
    "volumes": [
        {
            "volumeId": "vol-094812e2e62d7845e",
            "deviceName": "/dev/sdb", 
            "tags": [
                {
                    "Key": "source-region", 
                    "Value": "us-east-1"
                }, 
                {
                    "Key": "source-name", 
                    "Value": "CC-2980"
                }, 
                {
                    "Key": "source-instanceId", 
                    "Value": "i-0fe3843e324aff337"
                }, 
                {
                    "Key": "source-device", 
                    "Value": "/dev/sdb"
                }, 
                {
                    "Key": "source-volumeId", 
                    "Value": "vol-094812e2e62d7845e"
                }
            ], 
        }
    ]
}
"""
ticketCreateSrcSnapshots = {
    "regionName"    : SOURCE_REGION,
}
volumes = []
for device in sourceVolumes:

    # volume to take a snapshot of
    volume = {}
    volume["deviceName"]    = device["DeviceName"]
    volume["volumeId"]      = device["Ebs"]["VolumeId"]

    # tags for the volume
    tags = []

    tag = {}
    tag["Key"]     = "Name"
    tag["Value"]    = SOURCE_INSTANCE_NAME + ":" + volume["deviceName"]
    tags.extend([tag])

    tag = {}
    tag["Key"]     = "description"
    tag["Value"]    = DESCRIPTION + " on " + SOURCE_INSTANCE_NAME + ":" + volume["deviceName"] + " at " + SOURCE_REGION
    tags.extend([tag])

    tag = {}
    tag["Key"]     = "source-region"
    tag["Value"]    = ticketCreateSrcSnapshots["regionName"]
    tags.extend([tag])

    tag = {}
    tag["Key"]     = "source-name"
    tag["Value"]    = SOURCE_INSTANCE_NAME
    tags.extend([tag])

    tag = {}
    tag["Key"]     = "source-instanceId"
    tag["Value"]    = SOURCE_INSTANCE_ID
    tags.extend([tag])

    tag = {}
    tag["Key"]     = "source-device"
    tag["Value"]    = volume["deviceName"]
    tags.extend([tag])

    tag = {}
    tag["Key"]     = "source-volumeId"
    tag["Value"]    = volume["volumeId"]
    tags.extend([tag])

    volume["tags"] = tags
    volumes.extend([volume])


if len(volumes) <= 0:
    print "No devices"
    quit()
else:
    ticketCreateSrcSnapshots["volumes"] = volumes
    responseCreateSrcSnapshots = ec2_ebs.create_snapshots(ticketCreateSrcSnapshots)

    ticket_deleteSourceSnapshots = copy.deepcopy(ticketCreateSrcSnapshots)
    ticket_deleteSourceSnapshots['snapshots'] = responseCreateSrcSnapshots['volumes']
    print json_dump(responseCreateSrcSnapshots)
    print "snapshot READY"


print "#--------------------------------------------------------------------------------"
print "# Delete source snapshots"
print "#--------------------------------------------------------------------------------"
print json_dump(ec2_ebs.delete_snapshot(ticket_deleteSourceSnapshots))
