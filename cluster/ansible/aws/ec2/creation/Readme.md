## Objective
Create AWS environment to install K8S.

## AWS Cloud Provider of K8S
K8S AWS cloud provider requires specific tagging and they are handled here.

## Structure
```
`.
├── Readme.md
├── plays
│   ├── roles
│   │   ├── create   <---- Create VPC, Security Group, EC2 instances, and tags.
│   │   └── list     <---- not used
│   ├── site.yml
│   ├── master.yml   <---- Create VPC, Security Group, and a EC2 instance for a master
│   └── worker.yml   <---- Create EC2 instances for workers
└── scripts
    ├── _utility.sh
    └── main.sh      <---- Execution script for the module
```

