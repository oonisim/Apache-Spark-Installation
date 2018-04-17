#!/usr/bin/env bash
set -ue

DIR=$(realpath $(dirname $0))
cd ${DIR}

export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:?"Set AWS_ACCESS_KEY_ID"}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:?"Set AWS_SECRET_ACCESS_KEY"}
export EC2_KEYPAIR_NAME=${EC2_KEYPAIR_NAME:?"Set EC2_KEYPAIR_NAME"}
export TARGET_INVENTORY=${TARGET_INVENTORY:?"Set TARGET_INVENTORY"}


#--------------------------------------------------------------------------------
# Setup AWS and create master file which holds master node data in ${DIR}
# The master file is then used by run_k8s.sh
#--------------------------------------------------------------------------------
./maintenance.sh
cluster/ansible/aws/ec2/creation/scripts/main.sh ${TARGET_INVENTORY} ${EC2_KEYPAIR_NAME} ${DIR}

