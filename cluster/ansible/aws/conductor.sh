#!/bin/bash
#--------------------------------------------------------------------------------
# [Function]
# Go to the PLAYBOOK_DIR, setup Ansible inventory/cfg, invoke PALYER to play books
# against the ENVIRONMENT.
#--------------------------------------------------------------------------------
set -eu

DIR=$(realpath $(dirname $0))

if [ $# -lt 2 ] ; then
    echo "Insufficient argument"
    echo "$0 PLAYBOOK_DIR ENVIRONMENT"
    exit 1
fi

PLAY_DIR=$1
ENVIRONMENT=$2

shift 2
ARGS=$@

. ${PLAY_DIR}/../scripts/_utility.sh

CONF_DIR=$(_locate ${DIR} '/' 'cluster/conf')
TOOL_DIR=$(_locate ${DIR} '/' 'cluster/tools')
PLAYER=$(_locate ${DIR} '/' 'player.sh')

echo "PLAY_DIR=[${PLAY_DIR}]"
echo "CONF_DIR=[${CONF_DIR}]"
echo "PLAYER=[${PLAYER}]"
echo "ARGS=[$ARGS]"

source ${CONF_DIR}/env/${ENVIRONMENT}/env.properties
source ${CONF_DIR}/env/${ENVIRONMENT}/server.properties

#--------------------------------------------------------------------------------
# Go to the playbook directory.
#--------------------------------------------------------------------------------
cd ${PLAY_DIR}

#--------------------------------------------------------------------------------
# Setup the play ground for Ansible player.
#--------------------------------------------------------------------------------
rm -rf ${PLAY_DIR}/{callbacks,group_vars,ansible.cfg,hosts}

#cp -r  ${CONF_DIR}/ansible/inventories/${ENVIRONMENT}/inventory hosts
ln -sf ${CONF_DIR}/ansible/inventories/${ENVIRONMENT}/group_vars
ln -sf ${CONF_DIR}/ansible/ansible.cfg
ln -sf ${CONF_DIR}/ansible/callbacks

#--------------------------------------------------------------------------------
# Let the player play the books.
#--------------------------------------------------------------------------------
#VAULT_PASS_FILE=${CONF_DIR}/ansible/vaultpass.encrypted
#VAULT_PASS=$(${TOOL_DIR}/decrypt.sh ${DECRYPT_KEY_FILE} ${VAULT_PASS_FILE})
#${PLAYER} ${VAULT_PASS} ${ARGS}

#ansible-playbook -vvvv -i hosts ${ARGS} site.yml --vault-password-file ~/.secret/.vault_pass.txt
ansible-playbook -vvvv -i hosts ${ARGS} site.yml

#--------------------------------------------------------------------------------
# Clean up
#--------------------------------------------------------------------------------
rm -rf ${PLAY_DIR}/{callbacks,group_vars,ansible.cfg,hosts}
