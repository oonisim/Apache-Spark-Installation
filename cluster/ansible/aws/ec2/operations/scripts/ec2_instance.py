import sys, time, copy, json, inspect
from sets import Set
try:
    import boto3
except ImportError:
    print "failed=True msg='boto required for this module'"
    sys.exit(1)
from utility import json_dump
from ec2_common import getEC2, wait_resource

#================================================================================
# Instance
#================================================================================
def list_instances(ticket):
    """
    :param ticket: 
    {
        "regionName": "us-east-2",
        "filters": [
            {
                "Name": "tag:Name", 
                "Values": [
                    "gitlab-dr"
                ]
            }, 
            {
                "Name": "instance-id",
                "Values": [
                    "i-0cc705bce867c7fe6"
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

    reservations = getEC2(ticket).meta.client.describe_instances(
        Filters = ticket.get("filters")
    )["Reservations"]
    instances = sum(
        [
            [i for i in r["Instances"]]
            for r in reservations
        ],
        []
    )
    return(instances)

def wait_instances(ticket):
    """
    
    :param ticket: 
    {
        "regionName": "us-east-2",
        "event": "instance_running", 
        "instanceIds": [
            "i-0cc705bce867c7fe6"
        ], 
    }
    :return: 
    """
    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"

    wait_args = {}
    wait_args["InstanceIds"]  = ticket["instanceIds"]
    wait_resource(ticket["regionName"], ticket["event"], **wait_args)
    return(getEC2(ticket).meta.client.describe_instances(
        InstanceIds = ticket["instanceIds"]
    ))

def start_instances(ticket):
    """
    
    :param ticket: 
    {
        "instanceIds": [
            "i-0cc705bce867c7fe6"
        ], 
        "regionName": "us-east-2"
    }
    :return: 
    """
    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"

    order = copy.copy(ticket)
    order["event"] = "instance_running"
    getEC2(ticket).meta.client.start_instances(
        InstanceIds = order["instanceIds"],
    )
    return(wait_instances(order))

def stop_instances(ticket):
    """
    :param ticket: 
    {
        "regionName": "us-east-2",
        "instanceIds": [
            "i-0cc705bce867c7fe6"
        ], 
        "event": "instance_stopped"
    }
    :return: 
    """
    print "--------------------------------------------------------------------------------"
    print inspect.stack()[0][3] + " ticket: " + json_dump(ticket)
    print "--------------------------------------------------------------------------------"

    order = copy.copy(ticket)
    order["event"] = "instance_stopped"
    getEC2(ticket).meta.client.stop_instances(
        InstanceIds = order["instanceIds"],
    )
    return(wait_instances(order))


