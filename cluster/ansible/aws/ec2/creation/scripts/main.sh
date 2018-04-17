#!/bin/bash
#--------------------------------------------------------------------------------
# Run the ansible playbook.
#--------------------------------------------------------------------------------
set -eu
DIR=$(realpath $(dirname $0))
. ${DIR}/_utility.sh

if [ $# -eq 3 ]; then
    TARGET_INVENTORY=$1
    EC2_KEYPAIR_NAME=$2
    OUTPUT_DIR=$3
else
    echo "Target environment/inventory?"
    read TARGET_INVENTORY

    echo "EC2 keypair name?"
    read EC2_KEYPAIR_NAME

    echo "Output directory?"
    read OUTPUT_DIR
fi

PLAYBOOK_DIR=$(realpath "$(dirname $0)/../plays")
ARGS="\
    -e ENV_ID=${TARGET_INVENTORY} \
    -e EC2_KEYPAIR_NAME=${EC2_KEYPAIR_NAME} \
    -e OUTPUT_DIR=${OUTPUT_DIR}"

$(_locate ${DIR} '/' 'conductor.sh') ${PLAYBOOK_DIR} ${TARGET_INVENTORY} ${ARGS}
