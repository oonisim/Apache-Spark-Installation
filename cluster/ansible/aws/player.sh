#!/usr/bin/expect -d
exp_internal -f expect.log 1
log_user 1

#!/usr/bin/expect
#log_user 0

#--------------------------------------------------------------------------------
# [Function]
# Run ansible plays with valut password provision via expect
#--------------------------------------------------------------------------------
# [Debug] Use below at the top of this file.
#!/usr/bin/expect -d
#exp_internal -f expect.log 1
#log_user 1
#--------------------------------------------------------------------------------

set timeout 600

#--------------------------------------------------------------------------------
# Get args
#--------------------------------------------------------------------------------
set password  [lindex $argv 0];
set args      [lrange $argv 1 end];

#--------------------------------------------------------------------------------
# Run playbook
# http://stackoverflow.com/questions/26487625
# https://www.tcl.tk/man/tcl8.4/TclCmd/lrange.htm
#--------------------------------------------------------------------------------
spawn ansible-playbook -vv -i hosts {*}$args --ask-vault-pass site.yml
expect "Vault password:"
send "$password\n"

#--------------------------------------------------------------------------------
# Output ansible executions.
#--------------------------------------------------------------------------------
# https://stackoverflow.com/questions/16914342/expect-utility-is-not-working-when-executing-from-jenkins
# Since Jenkins doesn't run it from an actual terminal, interact doesn't work, since there can't actually
# be any user interaction there.
#interact
expect eof
wait
