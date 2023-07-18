#!/usr/bin/env python
# coding=utf-8
#! /usr/bin/python
# -*- coding: utf-8 -*-

import click
import os
import pexpect
import sys
import time


def wait_device():
    expect_list = [
        'error: no devices/emulators found',
        pexpect.EOF,
        pexpect.TIMEOUT,
    ]
    process = pexpect.spawn("adb wait-for-device", [], 300)
    index = process.expect(expect_list)
    if index == 1:
        return 1
    else:
        print("error: no devices/emulators found")
        return 0

def root():
    expect_list = [
        'no devices/emulators found',
        pexpect.EOF,
        pexpect.TIMEOUT,
    ]
    process = pexpect.spawn("adb root",[], 100)
    #print(f'adb root return {process.before}')
    index = process.expect(expect_list)
    #print(f'root 匹配到: {index} => {expect_list[index]}')
    if index == 1:
        return 1
    elif index == 0:
        time.sleep(1)
        print("no devices, loop root")
        return root()
    else:
        print("root error {expect_list[index]}")
        exit(0)

def enter_android():
    expect_list = [
        '#',
        'no devices/emulators found',
        pexpect.EOF,
        pexpect.TIMEOUT,
    ]
    process = pexpect.spawn("adb shell", [], 10)
    #print(f'adb shell return {process.before}')
    index = process.expect(expect_list)
    #print(f'enter 匹配到: {index} => {expect_list[index]}')
    if index == 0:
        process.sendline()
        return process
    elif index == 1:
        print('no devices/emulators found')
        time.sleep(1)
        return enter_android()
    else:
        print("enter error {expect_list[index]}")
    return 

def enter_qnx_nocheck(process):
    expect_list = [
        'login',
        'Network is unreachable',
        pexpect.EOF,
        pexpect.TIMEOUT,
    ]
    process.sendline("telnet cdc-qnx")
    index = process.expect(expect_list)
    #print(f'telnet return {process.before}')
    #print({process.after})
    #print(f'telnet read return {process.read()}')
    #print(f'enterqnx 匹配到: {index} => {expect_list[index]}')
    if index == 0:
        process.sendline("root")
    elif index == 1:
        print(f'Network is unreachable')
        time.sleep(1)
        return enter_qnx_nocheck(process)
    else:
        print(f'telnet error {expect_list[index]}')

def enter_qnx(process):
    expect_list = [
        'login',
        'Network is unreachable',
        'Logging',
        pexpect.EOF,
        pexpect.TIMEOUT,
    ]
    process.sendline("telnet cdc-qnx")
    while 1 :
        index = process.expect(expect_list)
        if index == 0:
            process.sendline("root")
            continue;
        elif index == 1:
            return enter_qnx(process)
        elif index == 2:
            return 0;
        else:
            print(f'telnet error {expect_list[index]}')
            return -1

def push_android(files):
    for file in files:
        cmd_line = "adb push %s /data"%(file)
        (command_output, exitstatus) = pexpect.run(cmd_line, withexitstatus=1)
        print(command_output.strip().decode('UTF-8'))

### push_android()

def push(files, path):
    wait_device()
    root()
    push_android(files)
    push_qnx(files, path)

### push()

def push_qnx(files, path):
    process = enter_android()
    if process != None:
        process.sendline('start mount_ota')
        for file in files:
            cmd_line = "mv /data/%s /ota/"%file
            process.sendline(cmd_line)
        enter_qnx(process)
        for file in files:
            cmd_line = "mv /ota/android/%s %s"%(file, path)
            process.sendline(cmd_line)
        process.interact()
    return
### push_qnx()


def qsh(interact = True):
    if 1 == wait_device():
        if 1 == root():
            process = enter_android()
            if process != None:
                enter_qnx(process)
                if interact:
                    process.interact()
                else:
                    return process
### qsh()

def exec_cmd(cmd, interact = True):
    print("exec cmd is ", cmd)
    process = qsh(False)
    if process != None:
        process.sendline(cmd)
        if interact:
            process.interact()
        else:
            return process
### exec_cmd()

def pull(files, path):
    files_no_path = []
    # enter qnx
    process = qsh(False)
    if process == None:
        print("enter qnx error !!!")
        return
    # mv files to /ota/androd
    for file in files:
        files_no_path.append(os.path.basename(file))
        cmd_line = "cp %s /ota/android"%file
        process.sendline(cmd_line)
    # move files to /data/
    process.sendline("exit")
    process.sendline("start mount_ota")
    for file in files_no_path:
        cmd_line = "mv /ota/%s /data"%file
        process.sendline(cmd_line)

    process.sendline("exit")
    # adb pull
    for file in files_no_path:
        cmd_line = "adb pull /data/%s %s"%(file, path)
        (command_output, exitstatus) = pexpect.run(cmd_line, withexitstatus=1)
        print(command_output.strip().decode('UTF-8'))

### pull()

def show_log(keys):
    cmd_line = "slog2info "
    for key in keys:
        cmd_line += "-b %s "%key
    cmd_line += " -w"
    exec_cmd(cmd_line)

### show_log()

def ota(pkg):
    wait_device()
    cmd_line = "adb push %s /data/ota.zip"%(pkg)
    (command_output, exitstatus) = pexpect.run(cmd_line, withexitstatus=1)
    print(command_output.strip().decode('UTF-8'))
    process = enter_android()
    if process == None:
        print("enter android error !!!")
        return
    process.sendline("setenforce 0")
    process.sendline("msg_center_test -t update/action/req \'{\"filename\":\"/data/ota_package/ota.zip\",\"action\":7,\"force\":true}\'")
    process.sendline("msg_center_test -r update/state/notify")
    process.interact()

#### ota()

commands = [
        'push', 
        'pull', 
        'reset', 
        'fastboot', 
        '9008', 
        'enable_full_dump', 
        'disable_full_dump', 
        'enable_mini_dump', 
        'disable_mini_dump', 
        'enable_gcore', 
        'disable_gcore', 
        'enable_secpolgenerate',
        'disable_secpolgenerate',
        'log',
        'ota',
        'safe_reset'
        ]

def get_env_vars(ctx, args, incomplete):
    return [k for k in commands if incomplete in k]

def get_file(ctx, args, incomplete):
    obj = []
    if args[0] == "ota" or args[0] == "push":
        for root, dirs, files in os.walk(".", topdown=False):
            for name in files:
                obj.append(os.path.join(root, name))
            for name in dirs:
                obj.append(os.path.join(root, name))
    return [k for k in obj if incomplete in k]

@click.command()
@click.argument("cmd", type=click.STRING, default="qsh", autocompletion=get_env_vars)
@click.argument("args", nargs = -1, autocompletion=get_file)
def main(cmd, args):
    if cmd == 'qsh':
        qsh()
    elif cmd == commands[0]:            # push
        push(args[0:-1], args[-1])
    elif cmd == commands[1]:            # pull
        pull(args[0:-1], args[-1])
    elif cmd == commands[2]:            # reset
        exec_cmd("reset")
    elif cmd == commands[3]:            # fastboot
        exec_cmd("reset -f")
    elif cmd == commands[4]:            # 9008
        exec_cmd("enter_9008_mod.sh")
    elif cmd == commands[5]:            # enable full dump
        pass
    elif cmd == commands[6]:            # disable full dump
        pass
    elif cmd == commands[7]:            # enable mini dump
        pass
    elif cmd == commands[8]:            # disable mini dump
        pass
    elif cmd == commands[9]:            # enable gcore
        pass
    elif cmd == commands[10]:           # disable gcore
        pass
    elif cmd == commands[11]:           # enable secpolgenerate
        process = exec_cmd("touch /var/enable_mini_rawdump", False)
        process.sendline("reset")
    elif cmd == commands[12]:           # disable secpolgenerate
        process = exec_cmd("rm /var/enable_mini_rawdump", False)
        process.sendline("reset")
    elif cmd == commands[13]:           # log
        show_log(args)
    elif cmd == commands[14]:           # ota
        ota(args)
    elif cmd == commands[15]:           # mcu reset soc
        exec_cmd("safely_reset.sh")

### main()

if __name__ == '__main__':
    main()

