#!/bin/bash
#--------------------------------------------------------------------------------
# https://github.com/enginyoyen/ansible-best-practises/blob/master/extensions/setup/setup.sh
# Based on MIT License.
#--------------------------------------------------------------------------------
set -eu

COLOR_END='\e[0m'
COLOR_RED='\e[0;31m' # Red
COLOR_YEL='\e[0;33m' # Yellow

# This current directory.
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
msg_exit() {
    printf "$COLOR_RED$@$COLOR_END"
    printf "\n"
    printf "Exiting...\n"
    exit 1
}

msg_warning() {
    printf "$COLOR_YEL$@$COLOR_END"
    printf "\n"
}

echo "--------------------------------------------------------------------------------"
echo " Install pre-requisite packages for Ansible on master (Not target)...           "
echo "--------------------------------------------------------------------------------"
system=$(uname)
if [ "$system" == "Linux" ]; then
    #lsb_release may not be installed in RedHat/CentOS
    #distro=$(lsb_release -i)
    distro=$(cat /etc/os-release | grep '^NAME=' | sed -n 's/^NAME=\"\(.*\)\"$/\1/p')
    if [[ ${distro:0:3} == "Ubu" ]] || [[ $distro == "Deb" ]] ;then
        . ${DIR}/_ubuntu.sh
    elif [[ ${distro:0:3} == "Red" ]] || [[ $distro == "Cen" ]] ;then
        . ${DIR}/_redhat.sh
    else
        msg_exit "Your linux system was not test"
    fi
fi

echo "--------------------------------------------------------------------------------"
echo " Install/upgrade Ansible on master...                                           "
echo "--------------------------------------------------------------------------------"
sudo -H pip install --no-cache-dir  --upgrade --requirement "${DIR}/python_requirements"
