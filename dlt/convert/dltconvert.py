#!/usr/bin/env python
# coding=utf-8
#! /usr/bin/python
# -*- coding: utf-8 -*-

from distutils import text_file
import os
import sys
import subprocess
import tarfile
import gzip
import argparse

def run_cmd2file(cmd, out_file):
    fdout = open(out_file,'a')
    p = subprocess.Popen(cmd, stdout=fdout,  shell=True)
    if p.poll():
       return
    p.wait()
    return

def execute_cmd(command, simulate=True, ignore_fail=False):
    print(command)
    if simulate:
        return "OK"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    (output, err) = process.communicate()
    if process.wait() != 0:
        #print(output)
        error = "execute_cmd() error: cmd %s " % command
        if not ignore_fail:
            raise Exception(error)
        else:
            print(error)
            return "NOT_OK"
    return output

def unTar(file):
    tar = tarfile.open(file,'r')
    tar.extractall()
    tar.close()

def un_gz(file_name):
    
    # 获取文件的名称，去掉后缀名
    f_name = file_name.replace(".gz", "")
    # 开始解压
    g_file = gzip.GzipFile(file_name)
    #读取解压后的文件，并写入去掉后缀名的同名文件（即得到解压后的文件）
    open(f_name, "wb+").write(g_file.read())
    g_file.close()
    return f_name

def getFileName(path):
    ''' 获取指定目录下的所有指定后缀的文件名 '''

    #f_list = os.listdir(path)
    f_list = []

    for root, dirs, files in os.walk(path):  # 获取所有文件
            for file in files:  # 遍历所有文件名
                f_list.append(os.path.join(root, file))  # 拼接绝对路径并放入列表

    for f in f_list:
        print(f)
        convertFile(f)
'''
    # for .gz
    for i in f_list:
        if os.path.splitext(i)[1] == '.gz':
            print(i)
            un_gz(i)
        
    # for .tar
    for i in f_list:
        if os.path.splitext(i)[1] == '.tar':
            print(i)
            unTar(i)

    f_list = os.listdir(path)
    for i in f_list:
        # os.path.splitext():分离文件名与扩展名
        if os.path.splitext(i)[1] == '.dlt':
            file_name,suffix=i.split('.')
            print(file_name)
            text_file = file_name + ".txt"
            
            cmd="dlt-convert -a %s" % i
            run_cmd2file(cmd,text_file)
            os.remove(i)
'''

def convertFile(path):
    file_ext = path.replace('./', '')
    if os.path.splitext(file_ext)[1] == '.gz':
        print(file_ext)
        file_ext = un_gz(file_ext)
        print(file_ext)

    if os.path.splitext(file_ext)[1] == '.tar':
        print(file_ext)
        unTar(file_ext)

    if os.path.splitext(file_ext)[1] == '.dlt':
            file_name,suffix=file_ext.split('.')
            print(file_name)
            text_file = file_name + ".txt"
            
            print(text_file)
            cmd="dlt-convert -a %s" % file_ext
            run_cmd2file(cmd,text_file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--path",
                    help="file or path",
                    default=os.getcwd())

    args = parser.parse_args()
    if os.path.isdir(args.path):
        getFileName(args.path)
    else:
        convertFile(args.path)

if __name__ == '__main__':

    top_dir = os.getcwd()
    getFileName(top_dir)

