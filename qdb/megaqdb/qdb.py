#!/usr/bin/env python
# coding=utf-8
#! /usr/bin/python
# -*- coding: utf-8 -*-

import click
import os
import pexpect
import sys
import time
import subprocess

NFS_PATH = "/qlog/"
NFS_PATH_QNX = "/log/qlog/"
USER = "root"
PASSWORD = "root"

tel_retry = 0

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

def remount():
    expect_list = [
        'no devices/emulators found',
        pexpect.EOF,
        pexpect.TIMEOUT,
    ]
    process = pexpect.spawn("adb remount",[], 100)
    index = process.expect(expect_list)
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
    process = pexpect.spawn("adb shell", [], 1000)
    #print(f'adb shell return {process.before}')
    index = process.expect(expect_list)
    #print(f'enter 匹配到: {index} => {expect_list[index]}')
    if index == 0:
        return process
    elif index == 1:
        print('no devices/emulators found')
        time.sleep(1)
        return enter_android()
    else:
        print("enter error {expect_list[index]}")
    return 

def get_qnx_ip():
    qnx_ip = "192.168.1.1"
    hosts_content = subprocess.check_output(['adb', 'shell', 'cat', '/etc/hosts']).decode('utf-8')
    lines = hosts_content.split('\n')
    for line in lines:
        if "cdc-qnx" in line:
            parts = line.split()
            if parts:
                qnx_ip = parts[0]
    return qnx_ip

######## get_qnx_ip ######



def enter_android_qnx(interact = True):
    expect_list = [
        '#',
        'no devices/emulators found',
        pexpect.EOF,
        pexpect.TIMEOUT,
    ]
    expect_list2 = [
        'login',
        'Network is unreachable',
        'Logging',
        'No address associated with hostname',
        '#',
        pexpect.EOF,
        pexpect.TIMEOUT,
    ]
    key = 0
    retry = 0
    process = pexpect.spawn("adb shell", [], 10)
    index = process.expect(expect_list)
    if index == 0:
        process.sendline("telnet cdc-qnx")
        while 1 :
            if retry > 10:
                break
            index = process.expect(expect_list2)
            if index == 0:
                if key == 0:
                    process.sendline("root")
                    key = 1
            elif index == 1:
                time.sleep(1)
                print('Network is unreachable')
                process.sendline("telnet cdc-qnx")
                retry += 1
                continue
            elif index == 2:
                if interact :
                    process.interact()
                else:
                    return process
            elif index == 3:
                process.sendline("telnet 192.168.1.1")
                retry += 1
                continue
            elif index == 4:
                process.sendline("telnet cdc-qnx")
                retry += 1
                continue
            else:
                return process
    elif index == 1:
        print('no devices/emulators found')
        time.sleep(1)
        return enter_android_qnx()
    else:
        print("enter error {expect_list[index]}")
    return process

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
    global tel_retry
    tel_retry += 1
    expect_list = [
        'login',
        'Network is unreachable',
        'Logging',
        pexpect.EOF,
        pexpect.TIMEOUT,
    ]
    key = 0
    cmd_lin = "telnet %s"%(get_qnx_ip())
    process.sendline(cmd_lin)
    while 1 :
        index = process.expect(expect_list)
        if index == 0:
            if key == 0:
                process.sendline("root")
                key = 1
        elif index == 1:
            if tel_retry > 10:
                tel_retry = 0
                return -1
            print('Network is unreachable')
            return enter_qnx(process)
        elif index == 2:
            break
        else:
            print(f'telnet error {expect_list[index]}')
            break

    tel_retry = 0
    return

def push_android(files):
    for file in files:
        cmd_line = "adb push %s /data"%(file)
        (command_output, exitstatus) = pexpect.run(cmd_line, withexitstatus=1)
        print(command_output.strip().decode('UTF-8'))

### push_android()

def push_by_curl(files, path):
    wait_device()
    root()
    remount()
    push_android(files)
    # push_qnx(files, path)
    curl_to_qnx(files, path)

def push(files, path):
    wait_device()
    root()
    remount()
    push_android(files)
    push_qnx(files, path)


### push()

def curl_to_qnx(files, path):
    process = enter_android()
    if process != None:
        process.timeout = 10
        for file in files:
            cmd_line = "curl ftp://%s/%s/ -u root:root -T /data/%s "%(get_qnx_ip(), path, os.path.basename(file))
            print(cmd_line)
            print("========== Sending..... ==========")
            process.sendline(cmd_line)
            index = process.expect([pexpect.EOF, pexpect.TIMEOUT, "#"])

            # 根据匹配的情况获取结果
            if index == 2:  
                result = process.before.decode('utf-8')
                print(result)
                print("============== End ==============")
            else:  # 如果是TIMEOUT
                print("Timed out waiting for command to finish.")
        enter_qnx(process)
        process.interact()
    return
### curl_to_qnx()

def push_qnx(files, path):
    process = enter_android()
    if process != None:
        process.sendline('start mount_qlog')
        process.expect([pexpect.EOF, pexpect.TIMEOUT, "#"])
        time.sleep(1)
        for file in files:
            cmd_line = "mv -f /data/%s %s"%(os.path.basename(file), NFS_PATH)
            process.sendline(cmd_line)
            index = process.expect([pexpect.EOF, pexpect.TIMEOUT, "#", "No such file or directory"])
            if index == 3:
                print("some errors occur when push to qnx....")
                exit(1)

            process.sendline("sync")
        enter_qnx(process)
        for file in files:
            cmd_line = "mv -f %s%s %s"%(NFS_PATH_QNX, os.path.basename(file), path)
            process.sendline(cmd_line)
            process.expect([pexpect.EOF, pexpect.TIMEOUT, "#"])
            result = process.before.decode('utf-8')
            print(result)
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
            #  return enter_android_qnx(interact)
    return None
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
        cmd_line = "cp %s %s"%(file, NFS_PATH)
        process.sendline(cmd_line)
    # move files to /data/
    process.sendline("exit")
    process.sendline("start mount_qlog")
    for file in files_no_path:
        cmd_line = "mv %s%s /data"%(NFS_PATH, file)
        process.sendline(cmd_line)

    process.sendline("exit")
    # adb pull
    for file in files_no_path:
        cmd_line = "adb pull /data/%s %s"%(file, path)
        (command_output, exitstatus) = pexpect.run(cmd_line, withexitstatus=1)
        print(command_output.strip().decode('UTF-8'))

### pull()

def pull_by_curl(files, path):
    files_no_path = []
    process = enter_android()
    process.sendline("cd /data/")
    process.expect([pexpect.EOF, pexpect.TIMEOUT, "#"])
    if process != None:
        process.timeout = 10
        for file in files:
            files_no_path.append(os.path.basename(file))
            cmd_line = "curl ftp://%s/%s -u root:root -O "%(get_qnx_ip(), file)
            print(cmd_line)
            process.sendline(cmd_line)
            index = process.expect([pexpect.EOF, pexpect.TIMEOUT, "#"])

            # 根据匹配的情况获取结果
            if index == 2:  
                result = process.before.decode('utf-8')
                print("========== Sending..... ==========")
                print(result)
                print("============== End ==============")
            else:  # 如果是TIMEOUT
                print("Timed out waiting for command to finish.")

    for file in files_no_path:
        cmd_line = "adb pull /data/%s %s"%(file, path)
        (command_output, exitstatus) = pexpect.run(cmd_line, withexitstatus=1)
        print(command_output.strip().decode('UTF-8'))
    return

### pull_by_curl()

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

def exec_qnx_cmd(cmd, args):
    cmd_line = "%s "%cmd 
    for arg in args:
        cmd_line+=arg
    exec_cmd(cmd_line)

### exec_qnx_cmd

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
        'safe_reset',
        'curl_push', 
        'curl_pull'
        ]

def get_env_vars(ctx, args, incomplete):
    return [k for k in commands if incomplete in k]

def get_file(ctx, args, incomplete):
    obj = []
    if args[0] == "ota" or args[0] == "push" or args[0] == "curl_push":
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
        # process = exec_cmd("echo 0 > /dev/pdbg/memorydump/trace_status", False)
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
    elif cmd == commands[16]:           # curl_push
        push_by_curl(args[0:-1], args[-1])
    elif cmd == commands[17]:           # curl_pull
        pull_by_curl(args[0:-1], args[-1])
    else:
        exec_qnx_cmd(cmd, args)

### main()

if __name__ == '__main__':
    main()

