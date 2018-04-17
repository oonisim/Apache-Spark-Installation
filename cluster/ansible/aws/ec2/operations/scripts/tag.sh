#!/bin/bash
#--------------------------------------------------------------------------------
# Run the ansible playbook.
#--------------------------------------------------------------------------------
set -eu

DIR=$(dirname $(realpath $0))
. ${DIR}/_utility.sh

#--------------------------------------------------------------------------------
# ENVRIONMENT: Target environment id
# RESULT_PATH: Location to place results.
# TASK       : tag
#--------------------------------------------------------------------------------

PLAYBOOK_DIR=$(realpath "$(dirname $0)/../plays")
TASK=tag

if [ $# -eq 2 ]; then
    ENVIRONMENT=$1
    RESULT_PATH=$2
else
    echo "Taget environment?"
    read ENVIRONMENT
fi

ARGS="-e ENV_ID=${ENVIRONMENT}"

ln -sf ${PLAYBOOK_DIR}/${TASK}.yml ${PLAYBOOK_DIR}/site.yml
$(_locate ${DIR} '/' 'conductor.sh') ${PLAYBOOK_DIR} ${ENVIRONMENT} "${ARGS}"
rm -f  ${PLAYBOOK_DIR}/site.yml
