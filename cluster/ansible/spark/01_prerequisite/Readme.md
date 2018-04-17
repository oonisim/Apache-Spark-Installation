## Objective
This module is to setup the ansible pre-requisites on the ansible master and the target nodes.

## Structure
.
├── Readme.md
├── plays
│   ├── roles
│   │   └── python          <----- Setup ansible pre-requisite (python 2.x) on the target nodes.
│   └── site.yml
└── scripts
    ├── python_requirements <----- Python requirement to setup the ansible master.
    ├── _redhat.sh          <----- Setup RHEL/CentOS   ansible master
    ├── _ubuntu.sh          <----- Setup Debian/Ubuntu ansible master
    ├── setup.sh            <----- Setup the ansible master
    └── main.sh             <----- Setup the target nodes