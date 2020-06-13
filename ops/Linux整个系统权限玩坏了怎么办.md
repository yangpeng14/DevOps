## 前言

作者以前就遇到过Linux整个系统文件权限都被设置为`777`。并且系统没有权限备份，当时服务器也不是云主机，所以没有快照备份。

遇到这种情况怎么办？下面分享下作者个人恢复方法。

## 万能的百度搜索

通过百度搜索，搜索到一个权限备份与恢复工具：

- `getfacl`：备份Linux文件或者目录权限
- `setfacl`：恢复Linux文件或者目录权限

## 问题

虽然有 `getfacl` 与 `setfacl` 工具，但是遇到一个问题，权限损坏的机器并没有权限备份，导致权限无法恢复？

## 解决问题

### 注意

如果Linux整个系统文件权限都被设置为`777`，请不要重启系统，因为很多同学认为`万能的重启`能解决98%的问题。重启后权限就能恢复。但这次请不要重启系统，如果重启系统，系统直接损坏。

### 解决思路

虽然损坏的服务器没有权限备份，但是可以找一台与这台损坏的服务器`系统版本一样`的机器进行整个系统权限备份。在把备份文件拷贝到损坏的服务器上进行权限恢复。

### 具体操作

> 注意：这里所有操作，需要使用 root 用户来执行

1、找一个系统版本一样的服务器上操作权限备份

```bash
# 备份整个系统权限
$ getfacl -R / > /data/system-all-permissions.facl
```

2、恢复整个系统权限，在损坏的机器上操作

```bash
# 拷贝备份权限文件
$ scp root@192.168.1.10:/data/system-all-permissions.facl /data/

# 恢复整个系统权限
$ setfacl --restore=/data/system-all-permissions.facl

# 权限恢复完，可以找一个业务低峰重启机器
$ reboot
```

## 演示

故意把 `test` 目录权限全部设置成 `777`，然后对 `test` 目录做权限恢复。

1、首先备份 `test` 目录权限

```bash
# test 目录结构
$ tree test

test/
└── test1
    └── test1-1
        ├── hello1
        └── hello2

# 备份 test 目录权限
$ getfacl -R ./test/ > test-permissions.facl

# 查看 test 目录权限，权限都是正常的
$ cat test-permissions.facl

# file: test/
# owner: root
# group: root
user::rwx
group::r-x
other::r-x

# file: test//test1
# owner: root
# group: root
user::rwx
group::r-x
other::r-x

# file: test//test1/test1-1
# owner: root
# group: root
user::rwx
group::r-x
other::r-x

# file: test//test1/test1-1/hello2
# owner: root
# group: root
user::rw-
group::r--
other::r--

# file: test//test1/test1-1/hello1
# owner: root
# group: root
user::rw-
group::r--
other::r--
```

2、破坏 `test` 目录权限

```bash
# 破坏 test 目录权限，执行这种命令，一定要看清楚，千万别不看就执行了
$ chmod 777 -R ./test

# 查看 test 目录权限
$ ls -l test

drwxrwxrwx 3 root root 4096 6月  13 23:44 test1

$ ls -l test/test1/

drwxrwxrwx 2 root root 4096 6月  13 23:45 test1-1

$ ls -l test/test1/test1-1/

-rwxrwxrwx 1 root root 0 6月  13 23:45 hello1
-rwxrwxrwx 1 root root 0 6月  13 23:45 hello2
```

3、`test` 目录权限都被设置成 777，现在我们来恢复下权限

```bash
# 恢复 test 目录权限
$ setfacl --restore=test-permissions.facl

# 查看 test 目录权限，权限都正常恢复
$ ls -lsh test

4.0K drwxr-xr-x 3 root root 4.0K 6月  13 23:44 test1

$ ls -lsh test/test1/

4.0K drwxr-xr-x 2 root root 4.0K 6月  13 23:45 test1-1

$ ls -lsh test/test1/test1-1/

0 -rw-r--r-- 1 root root 0 6月  13 23:45 hello1
0 -rw-r--r-- 1 root root 0 6月  13 23:45 hello2
```

## 总结

为了防患于未然，对于自建机房的服务器一定要做好整个系统权限备份。如果使用云主机，每天也需要定时做快照备份。