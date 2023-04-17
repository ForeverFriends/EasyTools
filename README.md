# EasyTools
***Record some tools for work easily***



| Name | Description     | Use                                                          | Author |
| ---- | --------------- | ------------------------------------------------------------ | ------ |
| mdb  | qnx系统简易传输工具    | qdb       | zyp |
| dlt  | dlt文件转换工具 | dltconvert | gxx    |



## qdb

使用 expect 完成自动push、pull等操作，免输密码，自动交互。

**依赖项：**
- expect (sudo apt-get install expect)
- adb (sudo apt-get install adb)

**安装方法：**
```shell 
cd mdb

sudo install.sh
```
**常用命令：**

qdb : 通过adb的方式链接到 QNX 系统（无参数）


其他参数说明：
- push：
```shell
# file 文件名称，path：QNX 系统下的目标路径
qdb push file1 file2 ... filen path 
# 将 test 文件拷贝到 QNX 系统下的 /data 目录下
qdb push ./test /data 
```
 - pull：
 ```shell
 # file: QNX 系统下的文件或者文件夹； path： 目标位置
 qdb pull file path
 # 将 QNX 系统下 /data/test 文件拷贝到当前路径下
 qdb pull /data/test ./
 ```
 - 9008:
 ```shell
 # QNX 系统进入9008模式
 qdb 9008
 ```
 - fastboot:
 ```shell
 # QNX 系统进入fastboot模式
 qdb reset -f
 ```
 - screen:
 ```shell
 # 唤醒屏幕，系统进入active
 qdb screen
 ```
 - reset:
 ```shell
 # 重启 QNX 系统
 qdb reset
 ```
 - cmd:
 ```shell
 # QNX 系统下执行指定命令
 qdb ls
 ```

## dltconvert

转换 **.dlt** 格式的log

**依赖项：**

- pyton3
- python3-setuptools
- dlt-convert (sudo apt-get install dlt-tools)

**安装方法**

```shell
cd dlt
sudo python3 setup.py install
```
***注意*** 如果没有安装setuptools模块，请先安装。
```
# ubuntu
sudo apt-get install python3-setuptools

```

**使用方法：**

```shell
megadltconvert #遍历当前目录下所有文件并解析
megadltconvert -f file/path #解析指定文件或路径下的文件
```



