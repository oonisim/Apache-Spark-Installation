## Objective
Create administrative users for
* System administration (SYS_USER)
* Package installation  (PKG_USER)
* K8S administration    (SPARK_ADMIN)

## Assumptions
The same users exist in the ansible master where the playbooks run and copy its public key authentication stuff from their .ssh directory.

*       - "/home/{{ SYS_USER }}/.ssh/id_rsa.pub"
*       - "/home/{{ PKG_USER }}/.ssh/id_rsa.pub"
