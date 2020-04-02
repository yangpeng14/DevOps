## 前言

今天来聊聊 `Flannel`，`Flannel` 是 `Kubernetes` 默认网络组件，再聊 `Flannel` 时，我们得先明白一个叫 `CNI` 东东，`CNI` 是什么？能有什么用？下文会做出解释。

## CNI 简单介绍

`CNI`（Container Network Interface）是 `CNCF` 旗下的一个项目，由一组用于配置Linux容器网络接口的规范和库组成，同时还包含了一些插件。`CNI` 仅关心容器创建时的网络分配和当容器被删除时释放网络资源。Kubernetes 中已经内置了 `CNI`。

`Container Runtime` 在创建容器时，先创建好 `network namespace`，然后调用CNI插件为这个 `network namespace` 配置网络，其后再启动容器内的进程。`CNI` 已成为 `CNCF` 一员，成为 `CNCF` 主推的网络模型。

> `CNI` 项目地址 https://github.com/containernetworking/cni

Kubernetes Pod 中的其他容器都是Pod所属 `Pause` 容器的网络，创建过程为：

- 1.kubelet 先创建pause容器生成network namespace
- 2.调用网络CNI driver
- 3.CNI driver 根据配置调用具体的cni 插件
- 4.cni 插件给pause 容器配置网络
- 5.pod 中其他的容器都使用 pause 容器的网络

## Flannel 简介

`Flannel` 是CoreOS团队针对 Kubernetes 设计的一个网络规划服务，简单来说，它的功能是让集群中的不同节点主机创建的Docker 容器都具有全集群唯一的虚拟IP地址。它基于Linux TUN/TAP，使用UDP封装IP包来创建overlay网络，并借助etcd维护网络的分配情况。

## Flannel 原理

Flannel 实质上是一种 `覆盖网络(overlay network)`，也就是将TCP数据包装在另一种网络包里面进行路由转发和通信，目前已经支持 `UDP`、`VxLAN`、`Host Gw`、`AWS VPC`、`GCE`和 `Ali Vpc`路由等数据转发方式。

- `udp`：使用用户态udp封装，默认使用8285端口。由于是在用户态封装和解包，性能上有较大的损失，不推荐使用。
- `vxlan`：vxlan封装，需要配置VNI，Port（默认8472）和 [GBP](https://github.com/torvalds/linux/commit/3511494ce2f3d3b77544c79b87511a4ddb61dc89)。
- `host-gw`：直接路由的方式，将容器网络的路由信息直接更新到主机的路由表中，仅适用于二层直接可达的网络。推荐使用，效率极高。
- `aws-vpc`：使用 Amazon VPC route table 创建路由，适用于AWS上运行的容器。
- `gce`：使用Google Compute Engine Network创建路由，所有instance需要开启IP forwarding，适用于GCE上运行的容器。
- `ali-vpc`：使用阿里云VPC route table 创建路由，适用于阿里云上运行的容器。

## Flannel 架构简介

本文主要介绍下 `vxlan` 和 `host-gw` 数据转发方式

### Vxlan 模式

![](/img/flannel-vxlan.png)

flannel默认使用 `8285` 端口作为 `UDP` 封装报文的端口，`VxLan` 使用 `8472` 端口。

> 两个节点中容器是如何相互通信的呢？

- 1.假如 Frontend1 Pod(10.1.15.2/24) 要访问 Backend Service1 Pod(10.1.20.2/24)，默认会通过容器内部的 eth0 发送出去
- 2.报文通过 `veth pair` 被发送到 `vethXXX`
- 3.`vethXXX` 是直接连接到虚拟交换机 `docker0` 网卡，报文通过虚拟 `bridge docker0` 网卡发送出去
- 4.查找路由表，外部容器ip的报文都会转发到 `flannel0` 虚拟网卡，这是一个 `P2P` 虚拟网卡，然后报文就被转发到监听在另一端的 `flanneld`
- 5.`flanneld` 通过 `etcd` 维护了各个节点之间的路由表，把原来的报文 `UDP` 封装一层，通过配置的 `iface` 发送出去
- 6.报文通过主机之间的网络找到目标Backend Service1 Pod(10.1.20.2/24)主机
- 7.报文继续往上，到传输层，交给监听在8285端口的 `flanneld` 程序处理
- 8.数据被解包，然后发送给 `flannel0` 虚拟网卡
- 9.查找本机路由表，发现对应容器的报文要交给 `docker0`
- 10.`docker0` 找到 Backend Service1 Pod(10.1.20.2/24)，把报文发送过去
- 11.Backend Service1 Pod 处理完报文，按上面相同的步骤发送给 Frontend1 Pod

### Host-gw 模式

![](/img/flannel-host-gw-1.png)

在主机路由表中创建到其它主机 subnet 路由条目，从而实现容器跨主机通信。

`Host-gw` 是把每个节点都当成一个网关，它会加入其它节点并设成网关，当数据包到达这个节点的时候，就根据路由表发送到下一跳，也就是节点IP，`各个节点必须是同一个网段`，直接通过2层把这个数据转发到另一个节点上，另一个节点再根据本机路由规则转发到docker0网桥，docker0网桥根据2层又转发到容器里面。一个是数据的流入，就是当数据包到达这个节点之后，然后发给谁，这是流入数据包。一个是数据包的流出，当从节点出来的数据包，应该转发到哪个node上，这些都是由flannel去维护的。

`局限`：每个node节点在2层都能通信，否则下一跳转发不过去，但是它的性能要比vxlan的性能高很多，不需要封包解封包，这种接近原生，性能也是最好的。

### Vxlan Directrouting 模式

VXLAN 还有另外一种功能，VXLAN 也支持类似 host-gw 的模式，如果两个节点在同一网段时使用 host-gw 通信，如果不在同一网段中，即当前pod所在节点与目标pod所在节点中间有路由器，就使用VXLAN这种方式，使用叠加网络。

结合了 Host-gw 和 VXLAN ，这就是 VXLAN 的 Directrouting 模式。

```
$ etcdctl set /coreos.com/network/config '{"Network": "172.16.0.0/16", "Backend": {"Type": "VxLAN","Directrouting": true}}'
```

## 总结

在 Kubernetes 中，网络插件选择 `Flannel` 时。所有节点都在同一个网段，并且二层网络可能通信，可以考虑选择 `Host-gw` 模式。反之节点之间不能通过二层网络通信，可能在不同 `vlan` 中，可以考虑选择 `Vxlan` 模式，也可以考虑使用 `Vxlan Directrouting` 模式(默认是 false)。

## 参考链接

- https://github.com/coreos/flannel
- https://sdn.feisky.xyz/rong-qi-wang-luo/index/index/index
- https://sdn.feisky.xyz/rong-qi-wang-luo/index/index/index-1
- https://blog.51cto.com/14143894/2462379