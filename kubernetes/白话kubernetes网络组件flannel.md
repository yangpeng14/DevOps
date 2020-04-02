## 前言

今天来聊聊 `Flannel`，`Flannel` 是 `Kubernetes` 默认网络组件，在聊 `Flannel` 时，我们得先明白一个叫 `CNI` 东东，`CNI` 是什么？做什么用的？下文会做出解释。

## CNI 简单介绍

`CNI`（Container Network Interface）是CNCF旗下的一个项目，由一组用于配置Linux容器的网络接口的规范和库组成，同时还包含了一些插件。CNI仅关心容器创建时的网络分配和当容器被删除时释放网络资源。Kubernetes 中已经内置了 `CNI`。

`Container Runtime` 在创建容器时，先创建好 `network namespace`，然后调用CNI插件为这个 `network namespace` 配置网络，其后再启动容器内的进程。已成为 `CNCF` 一员，成为 `CNCF` 主推的网络模型。

> `CNI` 项目地址 https://github.com/containernetworking/cni

Kubernetes Pod 中的其他容器都是Pod所属 `Pause` 容器的网络，创建过程为：

- 1. kubelet 先创建pause容器生成network namespace
- 2. 调用网络CNI driver
- 3. CNI driver 根据配置调用具体的cni 插件
- 4. cni 插件给pause 容器配置网络
- 5. pod 中其他的容器都使用 pause 容器的网络

## Flannel 简介

`Flannel` 是CoreOS团队针对 Kubernetes 设计的一个网络规划服务，简单来说，它的功能是让集群中的不同节点主机创建的Docker 容器都具有全集群唯一的虚拟IP地址。它基于Linux TUN/TAP，使用UDP封装IP包来创建overlay网络，并借助etcd维护网络的分配情况。


## Flannel 原理

Flannel 实质上是一种 `覆盖网络(overlay network)`，也就是将TCP数据包装在另一种网络包里面进行路由转发和通信，目前已经支持 `UDP`、`VxLAN`、`Host Gw`、`AWS VPC`、`GCE`和 `Ali Vpc`路由等数据转发方式。

- `udp`：使用用户态udp封装，默认使用8285端口。由于是在用户态封装和解包，性能上有较大的损失
- `vxlan`：vxlan封装，需要配置VNI，Port（默认8472）和GBP
- `host-gw`：直接路由的方式，将容器网络的路由信息直接更新到主机的路由表中，仅适用于二层直接可达的网络 推荐使用，效率极高
- `aws-vpc`：使用 Amazon VPC route table 创建路由，适用于AWS上运行的容器
- `gce`：使用Google Compute Engine Network创建路由，所有instance需要开启IP forwarding，适用于GCE上运行的容器
- `ali-vpc`：使用阿里云VPC route table 创建路由，适用于阿里云上运行的容器

本文介绍下 `vxlan` 和 `host-gw` 数据转发方式

### Vxlan 模式

VXLAN 是Linux内核本身支持的一种网络虚拟化技术，是内核的一个模块，在内核态实现封装解封装，构建出覆盖网络，其实就是一个由各宿主机上的Flannel.1设备组成的虚拟二层网络，由于VXLAN由于额外的封包解包，导致其性能较差。

![](/img/flannel-vxlan.png)

### Host-gw 模式

在主机路由表中创建到其它主机 subnet 路由条目，从而实现容器跨主机通信

![](/img/flannel-host-gw.png)

### Vxlan Directrouting 模式

VXLAN 还有另外一种功能，VXLAN 也支持类似 host-gw 的模式，如果两个节点在同一网段时使用 host-gw 通信，如果不在同一网段中，即当前pod所在节点与目标pod所在节点中间有路由器，就使用VXLAN这种方式，使用叠加网络。

结合了 Host-gw 和 VXLAN ，这就是 VXLAN 的 Directrouting 模式。

```
$ etcdctl set /coreos.com/network/config'{"Network": "172.16.0.0/16", "Backend": {"Type": "VxLAN","Directrouting": true}}'
```

## 与 Docker集成

```bash
$ source /run/flannel/subnet.env
$ docker daemon --bip=${FLANNEL_SUBNET} --mtu=${FLANNEL_MTU} &
```

## 与 CNI 集成

CNI flannel 插件会将flannel网络配置转换为`bridge`插件配置，并调用`bridge`插件给容器 network namespace 配置网络。比如下面的flannel配置

```json
{
    "name": "mynet",
    "type": "flannel",
    "delegate": {
        "bridge": "mynet0",
        "mtu": 1400
    }
}
```

会被cni flannel插件转换为

```json
{
    "name": "mynet",
    "type": "bridge",
    "mtu": 1472,
    "ipMasq": false,
    "isGateway": true,
    "ipam": {
        "type": "host-local",
        "subnet": "10.1.17.0/24"
    }
}
```

## 与 Kubernetes 集成



## 参考链接

- https://github.com/coreos/flannel
- https://sdn.feisky.xyz/rong-qi-wang-luo/index/index/index
- https://sdn.feisky.xyz/rong-qi-wang-luo/index/index/index-1
- https://www.wqblogs.com/2019/11/29/flannel%E5%B7%A5%E4%BD%9C%E5%8E%9F%E7%90%86