#!/bin/bash
for node in $(cat nodes)
do
    export SSHPASS=$(openssl rsautl -decrypt -inkey ~/.ssh/private.pem -in .sshpass.bin)
    sshpass -e ssh-copy-id -oStrictHostKeyChecking=no ansible@${node}
done
