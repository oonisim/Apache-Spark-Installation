#!/bin/bash
#--------------------------------------------------------------------------------
# Run the ansible playbook to start instances.
# See https://c-scope.atlassian.net/wiki/display/CC/DevOps+-+CC+-+2.0+-+Environment+-+AWS+-+Instance+Management
#--------------------------------------------------------------------------------
set -eu

DIR=$(dirname $(realpath $0))
. ${DIR}/_utility.sh

#--------------------------------------------------------------------------------
# ENVRIONMENT: Target environment id
# TASK       : start
#--------------------------------------------------------------------------------

PLAYBOOK_DIR=$(realpath "$(dirname $0)/../plays")
TASK=start

if [ $# -eq 1 ]; then
    ENVIRONMENT=$1
else
    echo "Taget environment?"
    read ENVIRONMENT
fi

ARGS="-e ENV_ID=${ENVIRONMENT}"

ln -sf ${PLAYBOOK_DIR}/${TASK}.yml ${PLAYBOOK_DIR}/site.yml
$(_locate ${DIR} '/' 'conductor.sh') ${PLAYBOOK_DIR} ${ENVIRONMENT} ${ARGS}
rm -f  ${PLAYBOOK_DIR}/site.yml
