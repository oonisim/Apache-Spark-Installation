#!/usr/bin/env bash
ansible-playbook -vvvv -i inventory --private-key=~/.ssh/aws_maonishi_us-west-1pem.pem --vault-password-file ~/.vault_pass.txt ec2_test.yml