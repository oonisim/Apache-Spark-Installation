## Objective
This module is to setup the target operating system environment to be ready install K8S.

## NOTE
Read the readme.md of user.admin for the assumptions.

## Structure
.
├── Readme.md
├── plays
│   ├── roles
│   │   ├── docker       <---- Setup docker group/users (beware the risk), not install package here.
│   │   ├── firewalld    <---- Disable firewalld so as to use iptables
│   │   ├── iptable      <---- K8S uses iptable, e.g kube proxy to route pod network.
│   │   ├── hosts
│   │   ├── ntp          <---- NTP setup
│   │   ├── packages     <---- Software package installations
│   │   ├── selinux      <---- Turn off SELinux (as this is not for produciton but for quick startup)
│   │   ├── swapoff      <---- K8S does not support swap anymore and cause errors if it is there
│   │   └── user.admin   <---- Setup administrative userse
│   └── site.yml
└── scripts
    └── main.sh          <---- Execution script for the module
