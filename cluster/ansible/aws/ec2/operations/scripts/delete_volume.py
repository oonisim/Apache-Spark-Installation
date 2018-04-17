#!/usr/bin/python
import boto3, time, copy, json
from sets import Set
from utility import json_dump

import ec2_common, ec2_instance, ec2_volume

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
    ],
    "volumes": [
        {
            "volumeId": "vol-0f11c4abffcf9521a"
        },
    ]
}

#--------------------------------------------------------------------------------
# Delete volumes
#--------------------------------------------------------------------------------
response = ec2_volume.delete_volumes(ticket)
print json_dump(response)
