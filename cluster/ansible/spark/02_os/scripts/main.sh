#!/bin/bash
#--------------------------------------------------------------------------------
# Run the ansible playbook.
#--------------------------------------------------------------------------------
set -eu

#--------------------------------------------------------------------------------
# PLAYBOOK_DIR: ../plays as convention
# TARGET:       Target environment
# REMOTE_USER:  SSH user on the remote server
#--------------------------------------------------------------------------------
DIR=$(realpath $(dirname $0))
PLAYBOOK_DIR=$(realpath "$(dirname $0)/../plays")
if [ $# -ge 2 ]; then
    TARGET=$1
    REMOTE_USER=$2

    shift 2
    ARGS="$@"
else
    echo "Target inventory?"
    read TARGET

    echo "Remote user to use in the target servers?"
    read REMOTE_USER

    echo "args?"
    read ARGS
fi

. ${DIR}/_utility.sh
. ${DIR}/_pretask.sh

echo "#--------------------------------------------------------------------------------"
echo "# starting ansible playbook (it may take a while in case of EC2)..."
echo "#--------------------------------------------------------------------------------"

$(_locate ${DIR} '/' 'conductor.sh') \
  ${PLAYBOOK_DIR} \
  ${TARGET} \
  ${REMOTE_USER} \
  ${ARGS}

. ${DIR}/_posttask.sh
