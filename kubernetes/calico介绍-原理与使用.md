## 什么是 Calico ？

`Calico` 是一套开源的网络和网络安全方案，用于容器、虚拟机、宿主机之前的网络连接，可以用在kubernetes、OpenShift、DockerEE、OpenStrack等PaaS或IaaS平台上。

## Calico 组件概述

![](/img/calico-1.png)

- `Felix`：calico的核心组件，运行在每个节点上。主要的功能有`接口管理`、`路由规则`、`ACL规则`和`状态报告`
    - `接口管理`：Felix为内核编写一些接口信息，以便让内核能正确的处理主机endpoint的流量。特别是主机之间的ARP请求和处理ip转发。
    - `路由规则`：Felix负责主机之间路由信息写到linux内核的FIB（Forwarding Information Base）转发信息库，保证数据包可以在主机之间相互转发。
    - `ACL规则`：Felix负责将ACL策略写入到linux内核中，保证主机endpoint的为有效流量不能绕过calico的安全措施。
    - `状态报告`：Felix负责提供关于网络健康状况的数据。特别是，它报告配置主机时出现的错误和问题。这些数据被写入etcd，使其对网络的其他组件和操作人员可见。
- `Etcd`：保证数据一致性的数据库，存储集群中节点的所有路由信息。为保证数据的可靠和容错建议至少三个以上etcd节点。
- `Orchestrator plugin`：协调器插件负责允许kubernetes或OpenStack等原生云平台方便管理Calico，可以通过各自的API来配置Calico网络实现无缝集成。如kubernetes的cni网络插件。
- `Bird`：BGP客户端，Calico在每个节点上的都会部署一个BGP客户端，它的作用是将Felix的路由信息读入内核，并通过BGP协议在集群中分发。当Felix将路由插入到Linux内核FIB中时，BGP客户端将获取这些路由并将它们分发到部署中的其他节点。这可以确保在部署时有效地路由流量。
- `BGP Router Reflector`：大型网络仅仅使用 BGP client 形成 mesh 全网互联的方案就会导致规模限制，所有节点需要 N^2 个连接，为了解决这个规模问题，可以采用 `BGP 的 Router Reflector` 的方法，使所有 BGP Client 仅与特定 RR 节点互联并做路由同步，从而大大减少连接数。
- `Calicoctl`： calico 命令行管理工具。

## Calico 网络模式

- `BGP 边界网关协议（Border Gateway Protocol, BGP）`：是互联网上一个核心的去中心化自治路由协议。BGP不使用传统的内部网关协议（IGP）的指标。
    - `Route Reflector 模式（RR）（路由反射）`：Calico 维护的网络在默认是（Node-to-Node Mesh）全互联模式，Calico集群中的节点之间都会相互建立连接，用于路由交换。但是随着集群规模的扩大，mesh模式将形成一个巨大服务网格，连接数成倍增加。这时就需要使用 Route Reflector（路由器反射）模式解决这个问题。
- `IPIP模式`：把 IP 层封装到 IP 层的一个 tunnel。作用其实基本上就相当于一个基于IP层的网桥！一般来说，普通的网桥是基于mac层的，根本不需 IP，而这个 ipip 则是通过两端的路由做一个 tunnel，把两个本来不通的网络通过点对点连接起来。

## BGP 概述

`BGP（border gateway protocol）是外部路由协议（边界网关路由协议）`，用来在AS之间传递路由信息是一种增强的距离矢量路由协议（应用场景），基本功能是在自治系统间自动交换无环路的路由信息，通过交换带有自治系统号序列属性的路径可达信息，来构造自治系统的拓扑图，从而消除路由环路并实施用户配置的路由策略。

（边界网关协议(BGP)，提供自治系统之间无环路的路由信息交换（无环路保证主要通过其AS-PATH实现），BGP是基于策略的路由协议，其策略通过丰富的路径属性(attributes)进行控制。BGP工作在应用层，在传输层采用可靠的TCP作为传输协议（BGP传输路由的邻居关系建立在可靠的TCP会话的基础之上）。在路径传输方式上，BGP类似于距离矢量路由协议。而BGP路由的好坏不是基于距离（多数路由协议选路都是基于带宽的），它的选路基于丰富的路径属性，而这些属性在路由传输时携带，所以我们可以把BGP称为路径矢量路由协议。如果把自治系统浓缩成一个路由器来看待，BGP作为路径矢量路由协议这一特征便不难理解了。除此以外，BGP又具备很多链路状态（LS）路由协议的特征，比如触发式的增量更新机制，宣告路由时携带掩码等。）

> 实际上，Calico 项目提供的 `BGP` 网络解决方案，与 `Flannel` 的 `host-gw` 模式几乎一样。也就是说，Calico也是基于路由表实现容器数据包转发，但不同于Flannel使用flanneld进程来维护路由信息的做法，而Calico项目使用BGP协议来自动维护整个集群的路由信息。

## BGP两种模式

### 全互联模式(node-to-node mesh)

`全互联模式` 每一个BGP Speaker都需要和其他BGP Speaker建立BGP连接，这样BGP连接总数就是N^2，如果数量过大会消耗大量连接。如果集群数量超过100台官方不建议使用此种模式。

### 路由反射模式Router Reflection（RR）

`RR模式` 中会指定一个或多个BGP Speaker为RouterReflection，它与网络中其他Speaker建立连接，每个Speaker只要与Router Reflection建立BGP就可以获得全网的路由信息。在calico中可以通过`Global Peer`实现RR模式。

## Calico BGP 概述

![](/img/calico-bgp-1.png)

### BGP 是怎么工作的？

这个也是跨节点之间的通信，与flannel类似，其实这张图相比于flannel，通过一个路由器来路由，flannel.1 就相比于vxlan模式去掉，所以会发现这里是没有网桥存在，完全就是通过路由来实现，这个数据包也是先从veth设备对另一口发出，到达宿主机上的cali开头的虚拟网卡上，到达这一头也就到达了宿主机上的网络协议栈，另外就是当创建一个pod时帮你先起一个infra containers的容器，调用calico的二进制帮你去配置容器的网络，然后会根据路由表决定这个数据包到底发送到哪里去，可以从ip route看到路由表信息，这里显示是目的cni分配的子网络和目的宿主机的网络，当进行跨主机通信的时候之间转发到下一跳地址走宿主机的eth0网卡出去，也就是一个直接的静态路由，这个下一跳就跟host-gw的形式一样，和host-gw最大的区别是calico使用BGP路由交换，而host-gw是使用自己的路由交换，BGP这个方案比较成熟，在大型网络中用的也比较多，所以要比flannel的方式好，而这些路由信息都是由BGP client传输。

### 为什么叫边界网关协议呢？

和 flannel host-gw 工作模式基本上一样，BGP是一个边界路由器，主要是在每个自治系统的最边界与其他自治系统的传输规则，而这些节点之间组成的BGP网络是一个全网通的网络，这个网络就称为一个`BGP Peer`。

启动文件放在 `/opt/cni/bin` 目录下，/etc/cni/net.d 目录下记录子网的相关配置信息。

```bash
$ cat /etc/cni/net.d/10-calico.conflist

{
  "name": "k8s-pod-network",
  "cniVersion": "0.3.0",
  "plugins": [
    {
      "type": "calico",
      "log_level": "info",
      "etcd_endpoints": "https://10.10.0.174:2379",
      "etcd_key_file": "/etc/cni/net.d/calico-tls/etcd-key",
      "etcd_cert_file": "/etc/cni/net.d/calico-tls/etcd-cert",
      "etcd_ca_cert_file": "/etc/cni/net.d/calico-tls/etcd-ca",
      "mtu": 1440,
      "ipam": {
          "type": "calico-ipam"
      },
      "policy": {
          "type": "k8s"
      },
      "kubernetes": {
          "kubeconfig": "/etc/cni/net.d/calico-kubeconfig"
      }
    },
    {
      "type": "portmap",
      "snat": true,
      "capabilities": {"portMappings": true}
    }
  ]
}
```

### Pod 1 访问 Pod 2 流程如下

1、数据包从 Pod1 出到达Veth Pair另一端（宿主机上，以cali前缀开头）

2、宿主机根据路由规则，将数据包转发给下一跳（网关）

3、到达 Node2，根据路由规则将数据包转发给 cali 设备，从而到达 Pod2。

其中，这里最核心的 `下一跳` 路由规则，就是由 `Calico` 的 `Felix` 进程负责维护的。这些路由规则信息，则是通过 BGP Client 中 BIRD 组件，使用 BGP 协议来传输。

不难发现，Calico 项目实际上将集群里的所有节点，都当作是边界路由器来处理，它们一起组成了一个全连通的网络，互相之间通过 BGP 协议交换路由规则。这些节点，我们称为 `BGP Peer`。

而 `Flannel host-gw` 和 `Calico` 的唯一不一样的地方就是当数据包下一跳到达node2节点容器时发生变化，并且出数据包也发生变化，知道它是从veth的设备流出，容器里面的数据包到达宿主机上，这个数据包到达node2之后，它又根据一个特殊的路由规则，这个会记录目的通信地址的cni网络，然后通过cali设备进去容器，这个就跟网线一样，数据包通过这个网线发到容器中，这也是一个`二层的网络互通才能实现`。

## Route Reflector 模式（RR）（路由反射）

> 设置方法请参考官方链接 https://docs.projectcalico.org/master/networking/bgp

Calico 维护的网络在默认是 `（Node-to-Node Mesh）全互联模式`，Calico集群中的节点之间都会相互建立连接，用于路由交换。但是随着集群规模的扩大，mesh模式将形成一个巨大服务网格，连接数成倍增加。这时就需要使用 Route Reflector（路由器反射）模式解决这个问题。确定一个或多个Calico节点充当路由反射器，让其他节点从这个RR节点获取路由信息。

在BGP中可以通过calicoctl node status看到启动是 node-to-node mesh 网格的形式，这种形式是一个全互联的模式，默认的BGP在k8s的每个节点担任了一个BGP的一个喇叭，一直吆喝着扩散到其他节点，随着集群节点的数量的增加，那么上百台节点就要构建上百台链接，就是全互联的方式，都要来回建立连接来保证网络的互通性，那么增加一个节点就要成倍的增加这种链接保证网络的互通性，这样的话就会使用大量的网络消耗，所以这时就需要使用Route reflector，也就是找几个大的节点，让他们去这个大的节点建立连接，也叫RR，也就是公司的员工没有微信群的时候，找每个人沟通都很麻烦，那么建个群，里面的人都能收到，所以要找节点或着多个节点充当路由反射器，建议至少是2到3个，一个做备用，一个在维护的时候不影响其他的使用。

## IPIP 模式概述

![](/img/calico-ipip-1.png)

`IPIP` 是linux内核的驱动程序，可以对数据包进行隧道，上图可以看到两个不同的网络 vlan1 和 vlan2。基于现有的以太网将原始包中的原始IP进行一次封装，通过tunl0解包，这个tunl0类似于ipip模块，和Flannel vxlan的veth很类似。

### Pod1 访问 Pod2 流程如下：

1、数据包从 Pod1 出到达Veth Pair另一端（宿主机上，以cali前缀开头）。

2、进入IP隧道设备（tunl0），由Linux内核IPIP驱动封装，把源容器ip换成源宿主机ip，目的容器ip换成目的主机ip，这样就封装成 Node1 到 Node2 的数据包。

```yaml
此时包的类型：
  原始IP包：
  源IP：10.244.1.10
  目的IP：10.244.2.10

   TCP：
   源IP: 192.168.31.62
   目的iP：192.168.32.63
```

3、数据包经过路由器三层转发到 Node2。

4、Node2 收到数据包后，网络协议栈会使用IPIP驱动进行解包，从中拿到原始IP包。

5、然后根据路由规则，将数据包转发给cali设备，从而到达 Pod2。

### 实际查看路由情况

跨宿主机之间容器访问：

环境：

Pod 名称 | Pod IP | 宿主机 IP
---|---|---
zipkin-dependencies-production | 10.20.169.155 | 192.168.162.248
zipkin-production | 10.20.36.85 | 192.168.163.40

zipkin-dependencies-production 访问 zipkin-production 过程如下：

登录 zipkin-dependencies-production 容器中，查看路由信息，可以看到 0.0.0.0 指向了 169.254.1.1（eth0），查看容器ip地址。

![](/img/calico-ipip-2.png)

`eth0@if1454` 为在宿主机上创建的虚拟网桥的一端，另一端为 `calic775b4c8175`

![](/img/calico-ipip-3.png)

去往容器 zipkin-production 的数据包，由zipkin-dependencies-production 容器里经过网桥设备转发到 zipkin-dependencies-production 所在的宿主机上，在宿主机上查看路由表。

![](/img/calico-ipip-4.png)

可以看到 zipkin-production (pod-ip 10.20.36.85) 的下一跳是 192.168.163.40，也就是 zipkin-production 所在的宿主机ip地址，网络接口是 tunl0

> tunl0 设备是一个ip隧道（ip tunnel）设备，技术原理是IPIP，ip包进入ip隧道后会被linux内核的IPIP驱动接管并重新封装（伪造）成去宿主机网络的ip包，然后发送出去。这样原始ip包经过封装后下一跳地址就是 192.168.163.40

数据包到达 zipkin-production 的宿主机 192.168.163.40 后，经过解包查找 10.20.36.85 的路由为网桥设备 cali0393db3e4a6 

![](/img/calico-ipip-5.png)

最终 10.20.36.85 经过网桥设备 cali0393db3e4a6 被转发到容器 zipkin-production 内部，返回的数据包路径也是一样。

![](/img/calico-ipip-6.png)

## Calico 优势 与 劣势

### 优势

- Calico `BGP模式`下没有封包和解包过程，完全基于两端宿主机的路由表进行转发。
- 可以配合使用 `Network Policy` 做 pod 和 pod 之前的访问控制。

### 劣势

- 要求宿主机处于同一个2层网络下，也就是连在一台交换机上
- 路由的数目与容器数目相同，非常容易超过路由器、三层交换、甚至node的处理能力，从而限制了整个网络的扩张。(可以使用大规模方式解决)
- 每个node上会设置大量（海量)的iptables规则、路由，运维、排障难度大。
- 原理决定了它不可能支持VPC，容器只能从calico设置的网段中获取ip。

## Calico 管理工具

calicoctl 工具安装

```bash
# 下载工具：https://github.com/projectcalico/calicoctl/releases

$ wget -O /usr/local/bin/calicoctl https://github.com/projectcalico/calicoctl/releases/download/v3.13.3/calicoctl

$ chmod +x /usr/local/bin/calicoctl
```

```bash
# 查看集群节点状态

$ calicoctl node status
```

如果使用 `calicoctl get node`，需要指定 calicoctl 配置，默认使用 `/etc/calico/calicoctl.cfg`

```bash
# 设置 calicoctl 配置文件
$ vim /etc/calico/calicoctl.cfg

apiVersion: projectcalico.org/v3
kind: CalicoAPIConfig
metadata:
spec:
  datastoreType: "etcdv3"
  etcdEndpoints: https://10.10.0.174:2379
  etcdKeyFile: /opt/kubernetes/ssl/server-key.pem
  etcdCertFile: /opt/kubernetes/ssl/server.pem
  etcdCACertFile: /opt/kubernetes/ssl/ca.pem

# 查看 calico 节点
$ calicoctl get nodes

# 查看 IPAM的IP地址池
$ calicoctl get ippool -o wide

# 查看bgp网络配置情况
$ calicoctl get bgpconfig

# 查看ASN号，一个编号就是一个自治系统
$ calicoctl get nodes --output=wide

# 查看 bgp peer
$ calicoctl get bgppeer
```

## CNI 网络方案优缺点及最终选择

先考虑几个问题：

1、需要细粒度网络访问控制？

这个flannel是不支持的，calico支持，所以做多租户网络方面的控制ACL，那么要选择 calico。

2、追求网络性能？

选择 `flannel host-gw` 模式 和 `calico BGP` 模式。

3、服务器之前是否可以跑BGP协议？

很多的公有云是不支持跑BGP协议，那么使用calico的BGP模式自然是不行的。

4、集群规模多大？

如果规模不大，100以下节点可以使用flannel，优点是维护比较简单。

5、是否有维护能力？

calico的路由表很多，而且走BGP协议，一旦出现问题排查起来也比较困难，上百台的，路由表去排查也是很麻烦，这个具体需求需要根据自己的情况而定。

## 参考链接

- https://kuaibao.qq.com/s/20200111AZOTQ200?refer=spider
- https://blog.csdn.net/zhonglinzhang/article/details/97613927
- https://blog.51cto.com/14143894/2463392
- https://blog.csdn.net/x503809622/article/details/82629474