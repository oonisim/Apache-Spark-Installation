#!/usr/bin/env bash
set -eu
DIR=$(realpath $(dirname $0))
cd ${DIR}

#--------------------------------------------------------------------------------
# Target environment/inventory and Ansibe remote_user to use
#--------------------------------------------------------------------------------
if [ -z ${TARGET_INVENTORY+x} ]; then
    echo "What is TARGET_INVENTORY?"
    read TARGET_INVENTORY
else
    echo "TARGET_INVENTORY is ${TARGET_INVENTORY}"
fi

if [ -z ${REMOTE_USER+x} ]; then
    echo "What is REMOTE_USER?"
    read REMOTE_USER
else
    echo "REMOTE_USER is ${REMOTE_USER}"
fi

#--------------------------------------------------------------------------------
# AWS information
# Not asking to type credentials from command line.
#--------------------------------------------------------------------------------
export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:?"Set AWS_ACCESS_KEY_ID"}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:?"Set AWS_SECRET_ACCESS_KEY"}

#--------------------------------------------------------------------------------
# Master node information
#--------------------------------------------------------------------------------
if [ -f ./master ] ; then
    source master
fi

if [ -z ${MASTER_HOSTNAME+x} ]; then
    echo "What is MASTER_HOSTNAME?"
    read MASTER_HOSTNAME
else
    echo "MASTER_HOSTNAME is ${MASTER_HOSTNAME}"
fi

if [ -z ${MASTER_NODE_IP+x} ]; then
    echo "What is MASTER_NODE_IP?"
    read MASTER_NODE_IP
else
    echo "MASTER_NODE_IP is ${MASTER_NODE_IP}"
fi

#--------------------------------------------------------------------------------
# Generate hosts file (/etc/hosts) from the EC2 instances created.
#--------------------------------------------------------------------------------
#HOSTFILE="${DIR}/cluster/ansible/spark/02_os/plays/roles/hosts/files/hosts"
#./cluster/ansible/aws/ec2/operations/scripts/generate_hosts_file.sh ${TARGET_INVENTORY} ${HOSTFILE}
cp hosts   ${DIR}/cluster/ansible/spark/02_os/plays/roles/hosts/files/hosts
cp workers ${DIR}/cluster/ansible/spark/03_spark_setup/plays/roles/master/files/workers

#--------------------------------------------------------------------------------
# Run Spark setup
#--------------------------------------------------------------------------------
./maintenance.sh
for module in $(find ./cluster/ansible/spark -type d -maxdepth 1 -mindepth 1)
do
    if [ "${module##*/}" == "10_datadog" ] ; then
        continue
    fi

    ${module}/scripts/main.sh \
        ${TARGET_INVENTORY} \
        ${REMOTE_USER} \
        -e MASTER_HOSTNAME=${MASTER_HOSTNAME} \
        -e MASTER_NODE_IP=${MASTER_NODE_IP}

    if [ "${module##*/}" == "02_os" ] ; then
        echo "waiting sever restarts"
        sleep 10
    fi
done
