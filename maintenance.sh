#!/usr/bin/env bash
#--------------------------------------------------------------------------------
# Set the exec permission to scripts in the repository.
#--------------------------------------------------------------------------------
cd $(dirname $0)
find . -name '*.sh' | xargs -I % /bin/bash -c "git add %; "
find . -name '*.sh' | xargs -I % /bin/bash -c "chmod u+x %; "
find . -name '*.sh' | xargs -I % /bin/bash -c "git update-index --chmod=+x % "
find . -type f \( -name 'site.retry' -o -name 'ansible.log' \) | xargs rm
