#!/usr/bin/python
import boto3, time, copy, json, datetime
from sets import Set
from utility import json_dump
import ec2_common, ec2_instance, ec2_volume, ec2_ebs

START_TIME = datetime.datetime.now()
START_TIMESTAMP=START_TIME.strftime("%Y-%m-%d %H:%M")

DESCRIPTION                 = "Created by automated DR script on Jenkins at " + START_TIMESTAMP
SOURCE_REGION               = "us-east-1"
SOURCE_INSTANCE_ID          = "i-0f85649afd9bcc5cd"
SOURCE_INSTANCE_ID_FILTER   = "instance-id"
SOURCE_INSTANCE_NAME        = "jenkins"
SOURCE_INSTANCE_NAME_FILTER = "tag:Name"
SOURCE_AVAILABILITY_ZONE    = "us-east-1d"

TARGET_REGION               = "us-east-2"
TARGET_INSTANCE_ID          = "i-064f170a9a18338f2"
TARGET_INSTANCE_ID_FILTER   = "instance-id"
TARGET_INSTANCE_NAME        = "jenkins_dr"
TARGET_INSTANCE_NAME_FILTER = "tag:Name"
TARGET_VOLUME_TYPE          = "standard"
TARGET_AVAILABILITY_ZONE    = "us-east-2a"



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
    tag["Key"]     = "timestamp"
    tag["Value"]    = START_TIMESTAMP
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
print "# Copy snapshots"
print "#--------------------------------------------------------------------------------"
"""
{
    "regionName": "us-east-2", 
    "srcRegionName": "us-east-1",
    "snapshots": [
        {
            "deviceName": "/dev/sdb", 
            "snapshotId": "snap-07b8c6de8626656ba", 
            "volumeId": "vol-094812e2e62d7845e",
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
ticketCopySnapshots = {
    "regionName"    : TARGET_REGION,
    "srcRegionName" : SOURCE_REGION,
}
ticketCopySnapshots['snapshots'] = responseCreateSrcSnapshots['volumes']

responseCopySnapshots = ec2_ebs.copy_snapshots(ticketCopySnapshots)
print json_dump(responseCopySnapshots)

print "#--------------------------------------------------------------------------------"
print "# Delete source snapshots"
print "#--------------------------------------------------------------------------------"
print json_dump(ec2_ebs.delete_snapshot(ticket_deleteSourceSnapshots))

print "#--------------------------------------------------------------------------------"
print "# Create volumes from snapshots"
print "#--------------------------------------------------------------------------------"
"""
{
    "regionName": "us-east-2", 
    "snapshotIds": [
        "snap-00ef652aade869a48"
    ], 
    "snapshots": [
        {
            "availabilityZone": "us-east-2c", 
            "deviceName": "/dev/sdb", 
            "snapshotId": "snap-00ef652aade869a48", 
            "srcSnapshotId": "snap-07b8c6de8626656ba", 
            "srcVolumeId": "vol-094812e2e62d7845e", 
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
            "volumeType": "standard"
        }
    ]
}
"""
ticketCreateVolumes = copy.deepcopy(responseCopySnapshots)
del ticketCreateVolumes["srcRegionName"]

snapshots = ticketCreateVolumes['snapshots']
for s in snapshots:
    s['srcSnapshotId']      = s.pop("snapshotId")
    s['srcVolumeId']        = s.pop("volumeId")
    s['snapshotId']         = s.pop("dstSnapshotId")
    s['volumeType']         = TARGET_VOLUME_TYPE
    s['availabilityZone']   = TARGET_AVAILABILITY_ZONE

responseCreateVolumes = ec2_ebs.create_volumes_from_snapshots(ticketCreateVolumes)
print json_dump(responseCreateVolumes)

print "#--------------------------------------------------------------------------------"
print "# Delete snapshots at target after creating volumes"
print "#--------------------------------------------------------------------------------"
print json_dump(ec2_ebs.delete_snapshot(ticketCreateVolumes))

#--------------------------------------------------------------------------------
# Stop target instances
#--------------------------------------------------------------------------------
ticketStopTargetInstance = {
    "regionName": TARGET_REGION,
    "instanceIds" : [
        TARGET_INSTANCE_ID
    ]
}

responseStopTargetInstance = ec2_instance.stop_instances(ticketStopTargetInstance)
print json_dump(responseStopTargetInstance)

print "--------------------------------------------------------------------------------"
print "# List volumes of the target instance."
print "--------------------------------------------------------------------------------"
ticketTargetVolumes = {
    "regionName": TARGET_REGION,
    "filters": [
        {
            "Name": TARGET_INSTANCE_NAME_FILTER,
            "Values": [TARGET_INSTANCE_NAME],
        },
        {
            "Name": TARGET_INSTANCE_ID_FILTER,
            "Values": [TARGET_INSTANCE_ID],
        },
    ]
}
targetDevices = ec2_volume.list_instance_nonroot_ebs_volumes(ticketTargetVolumes)
print "Non root volumes is " + json_dump(targetDevices)


print "--------------------------------------------------------------------------------"
print "# Detach volumes of the target instance. (Can be recreated from snapshot)"
print "--------------------------------------------------------------------------------"
volumes = []
for device in targetDevices:
    volume = {}
    volume["instanceId"]    = TARGET_INSTANCE_ID
    volume["deviceName"]    = device["DeviceName"]
    volume["volumeId"]      = device["Ebs"]["VolumeId"]
    volumes.extend([volume])

ticketTargetVolumes["volumes"] = volumes
if len(ticketTargetVolumes["volumes"]) <= 0:
    print "No devices"
else:
    responseDetachVolumes = ec2_volume.detach_volumes(ticketTargetVolumes)
    print "Detach response " + json_dump(responseDetachVolumes)


print "#--------------------------------------------------------------------------------"
print "# Attach volumes at target"
print "#--------------------------------------------------------------------------------"
"""
{
    "regionName": "us-east-2", 
    "volumes": [
        {
            "volumeId": "vol-05485d50a1b15be4e", 
            "instanceId": "i-0cc705bce867c7fe6", 
            "deviceName": "/dev/sdb", 
            "availabilityZone": "us-east-2c", 
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
ticketAttachVolumes = copy.deepcopy(responseCreateVolumes)
volumes = ticketAttachVolumes['volumes']
for v in volumes:
    v['instanceId'] = TARGET_INSTANCE_ID

responseAttachVolumes = ec2_volume.attach_volumes(ticketAttachVolumes)
print "attach_volume responseAttachVolumes " + json_dump(responseAttachVolumes)

print "#--------------------------------------------------------------------------------"
print "# Start instances at target"
print "#--------------------------------------------------------------------------------"
ticket = {
    "regionName": TARGET_REGION,
    "instanceIds" : [
        TARGET_INSTANCE_ID
    ]
}

# Do not start.
#response = ec2_instance.start_instances(ticket)
#print json_dump(response)


print "--------------------------------------------------------------------------------"
print "# Delete volumes detached from the target. (Can be recreated from snapshot)"
print "--------------------------------------------------------------------------------"
if len(ticketTargetVolumes["volumes"]) <= 0:
    print "No devices"
else:
    response = ec2_volume.delete_volumes(ticketTargetVolumes)
    print json_dump(response)

