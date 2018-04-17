#!/bin/bash
#--------------------------------------------------------------------------------
# Run the ansible playbook.
#--------------------------------------------------------------------------------
set -eu

DIR=$(dirname $(realpath $0))
. ${DIR}/_utility.sh

#--------------------------------------------------------------------------------
# ENVRIONMENT: Target environment id
# HOSTFILE:    hosts file to be created.
# TASK       : List
#--------------------------------------------------------------------------------

PLAYBOOK_DIR=$(realpath "$(dirname $0)/../plays")
TASK=list

if [ $# -eq 2 ]; then
    ENVIRONMENT=$1
    HOSTFILE=$2
else
    echo "Taget environment?"
    read ENVIRONMENT

    echo "host file to create?"
    read HOSTFILE
fi

ARGS="\
  -e ENV_ID=${ENVIRONMENT}\
  -e HOSTFILE=${HOSTFILE}"

ln -sf ${PLAYBOOK_DIR}/${TASK}.yml ${PLAYBOOK_DIR}/site.yml
$(_locate ${DIR} '/' 'conductor.sh') ${PLAYBOOK_DIR} ${ENVIRONMENT} ${ARGS}
rm -f  ${PLAYBOOK_DIR}/site.yml
