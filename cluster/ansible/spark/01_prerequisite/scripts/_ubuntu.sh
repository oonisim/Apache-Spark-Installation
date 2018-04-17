#!/bin/bash
sudo apt-get update -qy
sudo apt-get install -y build-essential libssl-dev libffi-dev python-dev python-setuptools
sudo apt-get install -y expect git whois
sudo easy_install pip