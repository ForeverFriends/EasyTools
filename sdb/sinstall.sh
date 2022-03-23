#!/bin/bash 
function expect_dev()
{
    expect <<EOF
    set timeout 1000
    spawn $@
    expect {
        "(yes/no)?" {send "yes\r"; exp_continue}
        "assword*" {send "system\r"; exp_continue}
        eof
    }
EOF
}
function expect_root_remount_install()
{
    expect <<EOF
    set timeout 1
    spawn ssh developer@192.168.100.100
    expect {
        "(yes/no)?" {send "yes\r"; exp_continue}
        "assword*" {send "system\r"; exp_continue}
    }
    send "su \r"
    expect {
        "(yes/no)?" {send "yes\r"; exp_continue}
        "assword*" {send "system\r"; exp_continue}
    }
    expect -re ".*\[\$#\]"
    send "mount -o remount, rw / \r"
    expect -re ".*\[\$#\]"
    send "rpm -vih --force --nodeps /data/developer/$@ \r"
    expect eof
EOF
}

#expect -re ".*\[\$#\]"
#send "exit\r"
#expect -re ".*\[\$#\]"
#send "exit\r"
ssh-keygen -f "/home/$USER/.ssh/known_hosts" -R 192.168.100.100
expect_dev scp -r $1 developer@192.168.100.100:/data/developer/
expect_root_remount_install ${1##*/}

