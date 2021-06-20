## 前言

大家都知道，数据量小的备份都使用 mysqldump 命令来备份，最近本人从阿里云RDS实例备份博客数据，并再次把备份出来的数据导入到RDS实例时，会遇到错误 ` [Err] 1227 - Access denied; you need (at least one of) the SUPER privilege(s) for this operation`。

> PS：阿里云RDS实例版本：`5.6`

遇到上面错误感觉很奇怪，为什么没有权限写入，使用的账号是高级账号，为什么没有权限了？？？

## 错误原因

通过上面报错，查找阿里云帮助文档，最后找到答案，下面是具体解决方法。

- 导入RDS MySQL 实例：SQL 语句中含有需要 Supper 权限才可以执行的语句，而 RDS MySQL不提供 Super 权限，因此需要去除这类语句。
- 本地 MySQL 实例没有启用 GTID。

## 解决方法

1、去除 DEFINER 子句

检查 SQL 文件，去除下面类似的子句

```
DEFINER=`root`@`%` 
```

在 Linux 平台下，可以尝试使用下面的语句去除：

```
$ sed -e 's/DEFINER[ ]*=[ ]*[^*]*\*/\*/ ' your.sql > your_revised.sql
```

2、去除 GTID_PURGED 子句

```
检查 SQL 文件，去除下面类似的语句
```

```
SET @@GLOBAL.GTID_PURGED='d0502171-3e23-11e4-9d65-d89d672af420:1-373,
d5deee4e-3e23-11e4-9d65-d89d672a9530:1-616234';
```

在 Linux 平台，可以使用下面的语句去除

```
$ awk '{ if (index($0,"GTID_PURGED")) { getline; while (length($0) > 0) { getline; } } else { print $0 } }' your.sql | grep -iv 'set @@' > your_revised.sql
```

3、检查修改后的文件

修改完毕后，通过下面的语句检查是否合乎要求。

```
$ egrep -in "definer|set @@" your_revised.sql
```

> 如果上面的语句没有输出，说明 SQL 文件符合要求。

## 参考链接

- 阿里云文档：https://developer.aliyun.com/article/66463