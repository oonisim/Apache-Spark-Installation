import sys, time, copy, json
from sets import Set
try:
    import boto3
except ImportError:
    print "failed=True msg='boto required for this module'"
    sys.exit(1)

from utility import json_dump

EC2_LABEL_DEVICE_NAME   = "DeviceName"
EC2_LABEL_INSTANCES     = "Instances"
EC2_LABEL_RESERVATIONS  = "Reservations"


#================================================================================
# Resouce Common
#================================================================================
def getEC2(ticket):
    """
    :param ticket: 
    {
        regionName: "us-east-1"
    }
    :return: 
    """

    if ticket.get("regionName") is None:
        print "No regionName is set"
        quit()

    ec2 = boto3.resource(
        "ec2",
        region_name = ticket.get("regionName")
    )
    return(ec2)

delay= 10
max_attempts = 720


def wait_resource(region, event, **wait_args):
    print "-----------------------------------------------------------"
    print "waiting for [" + event + "] on " + json_dump(wait_args)
    print "-----------------------------------------------------------"
    waiter = boto3.client("ec2", region).get_waiter(event)
    waiter.config.delay = delay
    waiter.config.max_attempts = max_attempts

    waiter.wait(**wait_args)


#================================================================================
# Tag
#================================================================================
def tag(region, resourceId, tags):
    ec2 = boto3.resource(
        "ec2",
        region_name = region
    )
    response = ec2.create_tags(
        Resources=[
            resourceId
        ],
        Tags = tags
    )
    return(response)
