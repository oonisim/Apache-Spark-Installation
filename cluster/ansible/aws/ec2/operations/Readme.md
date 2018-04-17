## Objective
Operate AWS environment.

## AWS Cloud Provider of K8S
K8S AWS cloud provider requires specific tagging and they are handled here.

## Structure
```
.
├── Readme.md
├── plays
│   ├── list.yml
│   ├── roles
│   │   ├── site.list
│   │   ├── site.start
│   │   ├── site.stop
│   │   └── site.tag
│   ├── start.yml
│   ├── stop.yml
│   └── tag.yml
└── scripts
    ├── generate_hosts_file.sh  <---- Create hosts file (to be /etc/hosts) from the EC2 instances tagged with **environment** set to ENV_ID.
    ├── create_volume.py        <---- Boto3 script to create EBS volumes.
    ├── delete_volume.py        <---- Boto3 script to delete EBS volumes.
    ├── detach_attach.py        <---- Boto3 script to detach/attach EBS volumes.
    ├── ec2_common.py
    ├── ec2_ebs.py
    ├── ec2_instance.py
    ├── ec2_volume.py
    ├── snapshot_deLtest.py
    ├── start_instances.sh
    ├── stop_instances.sh
    ├── tag.sh
    └── utility.py
```

