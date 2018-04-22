Spark standalone cluster deployment with kubeadm using Ansible
=========
Build a standalone Spark in AWS (CentOS or RHEL).

AWS Network Topology
------------

Simple 1 master + 2 workers (can be increased by a parameter) in a VPC subnet, to be created by the Ansible playbooks.

<img src="https://github.com/oonisim/Apache-Spark-Installation/blob/master/Images/AWS.png" width="500">

Repository Structure
------------

### Overview

Ansible playbooks and inventories under the Git repository.

```
.
├── cluster         <---- Spark cluster installation home (AWS+Spark)
│   ├── ansible     <---- Ansible playbook directory
│   │   ├── aws
│   │   │   ├── ec2
│   │   │   │   ├── creation         <---- Module to setup AWS
│   │   │   │   └── operations
│   │   │   ├── conductor.sh
│   │   │   └── player.sh
│   │   └── spark
│   │       ├── 01_prerequisite      <---- Module to setup Ansible pre-requisites
│   │       ├── 02_os                <---- Module to setup OS to install Spark
│   │       ├── 03_spark_setup         <---- Module to setup Spark cluster
│   │       ├── 10_datadog           <---- Module to setup datadog monitoring (option)
│   │       ├── conductor.sh         <---- Script to conduct playbook executions
│   │       └── player.sh            <---- Playbook player
│   ├── conf
│   │   └── ansible          <---- Ansible configuration directory
│   │       ├── ansible.cfg  <---- Configurations for all plays
│   │       └── inventories  <---- Each environment has it inventory here
│   │           ├── aws      <---- AWS/Spark environment inventory
│   │           └── template
│   └── tools
├── master      <---- Spark master node data for run_Spark.s created by run_aws.sh or update manally.
├── run.sh      <---- Run run_aws.sh and run_Spark.sh
├── run_aws.sh  <---- Run AWS setups
└── run_Spark.sh  <---- Run Spark setups
```

#### Module and structure

Module is a set of playbooks and roles to execute a specific task e.g. 03_Spark_setup is to setup a Spark cluster. Each module directory has the same structure having Readme, Plays, and Scripts.
```
03_Spark_setup/
├── Readme.md         <---- description of the module
├── plays
│   ├── roles
│   │   ├── common    <---- Common tasks both for master and workers
│   │   ├── master    <---- Setup master node
│   │   ├── user      <---- Setup Spark administrative users on master
│   │   ├── worker    <---- Setup worker nodes
│   ├── site.yml
│   ├── masters.yml   <--- playbook for master node
│   └── workers.yml   <--- playbook for worker nodes
└── scripts
    └── main.sh       <---- script to run the module (each module can run separately/repeatedly)
```
---

Preparations
------------

### Git

Clone this.

### For AWS

Have AWS access key_id, secret, and an AWS SSH keypair PEM file. MFA should not be used (or make sure to establish a session before execution).

### On Ansible master host

#### AWS CLI
Install AWS CLI and set the environment variables.

* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* EC2_KEYPAIR_NAME
* REMOTE_USER        <---- AWS EC2 user (centos for CentOs, ec2-user for RHEL)

#### Ansible
Have Ansible (2.4.1 or later) and Boto to be able to run AWS ansible features. If the host is RHEL/CentOS/Ubuntu, run below will do the job.

```
(cd ./cluster/ansible/Spark/01_prerequisite/scripts && ./setup.sh)
```

Test the Ansible dynamic inventory script.
```
conf/ansible/inventories/aws/inventory/ec2.py
```

#### SSH
Configure ssh-agent and/or .ssh/config with the AWS SSH PEM to be able to SSH into the targets without providing pass phrase. Create a test EC2 instance and test.

```
eval $(ssh-agent)
ssh-add <AWS SSH pem>
ssh ${REMOTE_USER}@<EC2 server> sudo ls  # no prompt for asking password

```

#### Datadog (optional)
Create a Datadog trial account and set the environment variable DATADOG_API_KEY to the [Datadog account API_KEY](https://app.datadoghq.com/account/settings#api). The Datadog module setups the monitors/metrics to verify that Spark is up and running, and can start monitoring and setup alerts right away.

#### Ansible inventory

Set environment (or shell) variable TARGET_INVENTORY=aws. The variable identifies the Ansible inventory **aws**  (same with ENV_ID in env.yml) to use.

Let's try
------------

Run ./run.sh to run all at once (create AWS IAM policy/role, VPC, subnet, router, SG, EC2, ..., setup Spark cluster and applications)  or go through the configurations and executions step by step below.

---

Configurations
------------

### Parameters

Parameters for an environment are all isolated in group_vars of the environment inventory. Go through the group_vars files to set values.

```
.
├── conf
│   └── ansible
│      ├── ansible.cfg
│      └── inventories
│           └── aws
│               ├── group_vars
│               │   ├── all             <---- Configure properties in the 'all' group vars
│               │   │   ├── env.yml     <---- Enviornment parameters e.g. ENV_ID to identify and to tag configuration items
│               │   │   ├── server.yml  <---- Server parameters e.g. location of kubelet configuration file
│               │   │   ├── aws.yml     <---- e.g. AMI image id, volume type, etc
│               │   │   ├── spark.yml   <---- Spark configurations
│               │   │   └── datadog.yml
│               │   ├── masters         <---- For master group specifics
│               │   └── workers
│               └── inventory
│                   ├── ec2.ini
│                   ├── ec2.py
│                   └── hosts           <---- Target node(s) using tag values (set upon creating AWS env)
```

#### EC2_KEYPAIR_NAME

Set the AWS SSH keypair nameto **EC2_KEYPAIR_NAME** enviornment variable and in aws.yml.

#### REMOTE_USER
Set the default Linux account (centos for CentOS EC2) that can sudo without password as the Ansible remote_user to run the playbooks If using another account, configure it and make sure it can sudo without password and configure .ssh/config.

#### ENV_ID

Set the inventory name _aws_ to ENV_ID in env.yml which is used to tag the configuration items in AWS (e.g. EC2). The tags are then used to identify configuration items that belong to the enviornment, e.g. EC2 dynamic inventory hosts.

#### Master node information
Set **private** AWS DNS name and IP of the master node instance. If run_aws.sh is used, it creates a file **master** which includes them and run_Spark.sh uses them. Otherwise set them in env.yml and as environment variables after having created the AWS instances.

* MASTER_HOSTNAME
* MASTER_NODE_IP

#### SPARK_ADMIN and LINUX_USERS
Set an account name to SPARK_ADMIN in server.yml. The account is created by a playbook via LINUX_USERS in server.yml. Set an encrypted password in the corresponding field. Use [mkpasswd as explained in Ansible document](http://docs.ansible.com/ansible/latest/faq.html#how-do-i-generate-crypted-passwords-for-the-user-module).


Executions
------------
Make sure the environment variables are set, and

Environment variables:
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* EC2_KEYPAIR_NAME
* REMOTE_USER
* DATADOG_API_KEY

Set TARGET_INVENTORY=aws variable which identifies the Ansible inventory **aws**  (same with ENV_ID) to use.

### AWS

```
.
├── cluster
├── maintenance.sh
├── master
├── run.sh
├── run_aws.sh   <--- Run this script.
└── run_spark.sh
```

### Spark
In the directory, run run_Spark.sh. If DATADOG_API_KEY is not set, the 10_datadog module will cause errors.

```
.
├── cluster
├── maintenance.sh
├── master       <---- Make sure master node information is set in this file
├── run.sh
├── run_aws.sh
└── run_spark.sh   <---- Run this script
```

Alternatively, run each module one by one, and skip 10_datadog if not using.
```
pushd ansible/Spark/<module>/scripts && ./main.sh or
ansible/Spark/<module>/scripts/main.sh aws <ansible remote_user>
```

Modules are:
```
├── 01_prerequisite      <---- Module to setup Ansible pre-requisites
├── 02_os                <---- Module to setup OS to install Spark
├── 03_Spark_setup         <---- Module to setup Spark cluster
├── 10_datadog           <---- Module to setup datadog monitoring (option)
├── conductor.sh         <---- Script to conduct playbook executions
└── player.sh            <---- Playbook player
```


