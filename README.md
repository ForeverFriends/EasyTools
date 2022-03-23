# EasyTools
***Record some tools for work easily***



| Name | Description     | Use                                                          | Author |
| ---- | --------------- | ------------------------------------------------------------ | ------ |
| sdb  | 简易传输工具    | sdb       | unknow |
| dlt  | dlt文件转换工具 | dltconvert | gxx    |



## sdb

使用 expect 完成自动push、pull、ssh等操作，免输密码。

## dltconvert

转换 **.dlt** 格式的log

**依赖项：**

- pyton3
- dlt-convert (sudo apt-install dlt-tools)

**安装方法**

```shell
cd dlt
sudo python3 setup.py install
```

**使用方法：**

```shell
megadltconvert #遍历当前文件下所有文件并解析
megadltconvert -f file/path #解析指定文件或路径下的文件
```



