#!/usr/bin/python
import boto3, time, copy, json
from sets import Set
from utility import json_dump

import ec2_common, ec2_instance, ec2_volume

#--------------------------------------------------------------------------------
# Stop instances
#--------------------------------------------------------------------------------
ticket = {
    "regionName": "us-east-2",
    "instanceIds" : [
        "i-0cc705bce867c7fe6"
    ]
}

response = ec2_instance.stop_instances(ticket)
print json_dump(response)

#--------------------------------------------------------------------------------
# Detach volumes
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
# Attach volumes
#--------------------------------------------------------------------------------
response = ec2_volume.attach_volumes(ticket)
print "Attach response " + json_dump(response)

#--------------------------------------------------------------------------------
# Start instances
#--------------------------------------------------------------------------------
ticket = {
    "regionName": "us-east-2",
    "instanceIds" : [
        "i-0cc705bce867c7fe6"
    ]
}

response = ec2_instance.start_instances(ticket)
print json_dump(response)

quit()

#--------------------------------------------------------------------------------
# Delete volumes
#--------------------------------------------------------------------------------
response = ec2_volume.delete_volumes(ticket)
print json_dump(response)
