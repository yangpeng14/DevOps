## 前言

在使用 Kubernetes 时，可能会遇到一些网络问题。当通过检查配置与日志无法排查错误时，这时就需要抓取网络数据包，但是Pod内一般不会安装`tcpdump`命令，那有没有方法可以直接通过宿主机抓取Pod网络数据包？

当然有，本文介绍 `nsenter` 命令，能够进入Pod容器 `net` 命令空间。并且本文提供一个快速进入Pod容器 `net` 命令空间脚本，方便大家使用。

## nsenter 使用参数

```
nsenter [options] [program [arguments]]

options:
-t, --target pid：指定被进入命名空间的目标进程的pid
-m, --mount[=file]：进入mount命令空间。如果指定了file，则进入file的命令空间
-u, --uts[=file]：进入uts命令空间。如果指定了file，则进入file的命令空间
-i, --ipc[=file]：进入ipc命令空间。如果指定了file，则进入file的命令空间
-n, --net[=file]：进入net命令空间。如果指定了file，则进入file的命令空间
-p, --pid[=file]：进入pid命令空间。如果指定了file，则进入file的命令空间
-U, --user[=file]：进入user命令空间。如果指定了file，则进入file的命令空间
-G, --setgid gid：设置运行程序的gid
-S, --setuid uid：设置运行程序的uid
-r, --root[=directory]：设置根目录
-w, --wd[=directory]：设置工作目录

如果没有给出program，则默认执行 $SHELL。
```

> 除了进入 `net` 命名空间，`nsenter` 还可以进入 `mnt`, `uts`, `ipc`, `pid`, `user` 命名空间，以及指定根目录和工作目录。

## Pod 容器抓包演示

> 发现某个服务网络不通，建议把这个服务副本数调为1个Pod，并且找到这个副本Pod所在`宿主机`和`Pod名称`。

查看Pod所在 `宿主机` 和 `Pod名称`。

```bash
$ kubectl get pods -n test -o wide
```

登陆Pod所在 `宿主机`，创建一个 `e_net.sh` Shell 脚本。

```bash
$ vim e_net.sh
```

```bash
#!/usr/bin/env bash

function e_net() {
  set -eu
  pod=`kubectl get pod ${pod_name} -n ${namespace} -o template --template='{{range .status.containerStatuses}}{{.containerID}}{{end}}' | sed 's/docker:\/\/\(.*\)$/\1/'`
  pid=`docker inspect -f {{.State.Pid}} $pod`
  echo -e "\033[32m Entering pod netns for ${namespace}/${pod_name} \033[0m\n"
  cmd="nsenter -n -t ${pid}"
  echo -e "\033[32m Execute the command: ${cmd} \033[0m"
  ${cmd}
}

# 运行函数
pod_name=$1
namespace=${2-"default"}
e_net
```

> 脚本依赖命令：宿主机上需要已安装 `kubectl`、`docker`、`nsenter`、`sed`、`echo` 命令。

```bash
# 添加脚本执行权限
$ chmod +x e_net.sh
```

本例抓取 `test` 命名空间中 `demo2-deployment-5f5f4fbd9b-92gd4` Pod `8080` 端口请求包。

```bash
# 进入 Pod demo2-deployment-5f5f4fbd9b-92gd4 net 命名空间
$ ./e_net.sh demo2-deployment-5f5f4fbd9b-92gd4 test

# 下面是脚本执行完输出结果
 Entering pod netns for test/demo2-deployment-5f5f4fbd9b-92gd4

 Execute the command: nsenter -n -t 44762
```

现在使用 `ip addr` 或者 `ifconfig` 查看，发现网卡配置只有 `demo2-deployment-5f5f4fbd9b-92gd4` Pod 网卡配置。

```bash
$ ifconfig
```

![](/img/k8s-nsenter-1.png)

使用 `tcpdump` 抓取 `eth0` 网卡上 `8080` 端口 数据包。

```bash
$ tcpdump -nnnvv -As 0 -i eth0 port 80 -w demo2.pcap

tcpdump: listening on eth0, link-type EN10MB (Ethernet), capture size 262144 bytes
63 packets captured
63 packets received by filter
0 packets dropped by kernel
```

下载 `demo2.pcap` 到本机，使用 `wireshark` 查看包。

![](/img/k8s-nsenter-2.png)

## 原理

`namespace` 是Linux中一些进程的属性的作用域，使用命名空间，可以隔离不同的进程。

Linux在不断的添加命名空间，目前有：

- `mount`：挂载命名空间，使进程有一个独立的挂载文件系统，始于Linux 2.4.19
- `ipc`：ipc命名空间，使进程有一个独立的ipc，包括消息队列，共享内存和信号量，始于Linux 2.6.19
- `uts`：uts命名空间，使进程有一个独立的hostname和domainname，始于Linux 2.6.19
- `net`：network命令空间，使进程有一个独立的网络栈，始于Linux 2.6.24
- `pid`：pid命名空间，使进程有一个独立的pid空间，始于Linux 2.6.24
- `user`：user命名空间，是进程有一个独立的user空间，始于Linux 2.6.23，结束于Linux 3.8
- `cgroup`：cgroup命名空间，使进程有一个独立的cgroup控制组，始于Linux 4.6

Linux的每个进程都具有命名空间，可以在 `/proc/PID/ns` 目录中看到命名空间的文件描述符。

![](/img/k8s-nsenter-3.png)

## nsenter

`nsenter` 命令相当于在[setns](http://www.man7.org/linux/man-pages/man2/setns.2.html)之上做了一层封装，使我们无需指定命名空间的`文件描述符`，而是指定`进程号`即可。

指定`进程号PID`以及需要进入的`命名空间`后，`nsenter`会帮我们找到对应的命名空间文件描述符`/proc/PID/ns/FD`，然后使用该命名空间运行新的程序。

## 参考链接

- https://staight.github.io/2019/09/23/nsenter%E5%91%BD%E4%BB%A4%E7%AE%80%E4%BB%8B/
- https://tencentcloudcontainerteam.github.io/tke-handbook/skill/capture-packets-in-container.html