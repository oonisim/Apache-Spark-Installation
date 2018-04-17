#!/bin/bash
sudo yum update -qy
sudo yum install -y gcc libffi-devel python-devel openssl-devel python-pip python-wheel
sudo yum install -y expect git
sudo easy_install pip
