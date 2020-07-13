## 问题

使用阿里云ECS搭建 `Harbor` 服务（docker-compose 部署）遇到网络地址冲突，导致Harbor云主机ECS无法访问其它VPC网段云主机，这是为什么？

使用 `docker-compose` 部署过Harbor同学都知道，在创建 Harbor 时，默认会创建 `5个` 网段，见下图。

![](/img/docker-network-route-1.png)

问题来了，因为使用阿里云 `VPC网络`，网段为 `172.16.0.0/12` ，下面是网络拓扑图。

![](/img/vpc-switch-1.png)

从上面两张图可以发现，网络地址段有重叠，会导致部署Harbor的云主机无法与其它VPC可用区云主机通信。

## Docker 网络驱动介绍 [1]

Docker的网络子系统使用驱动程序是可插拔的。默认情况下存在几个驱动程序，并提供核心网络功能：

- `bridge`: 默认的网络驱动程序。 如果您未指定驱动程序，则这是您正在创建的网络类型。当您的应用程序在需要通信的独立容器中运行时，通常会使用网桥网络。
- `host`: 对于独立容器，去掉容器和Docker主机之间的网络隔离，直接使用主机的网络。host仅可用于Docker 17.06及更高版本上的集群服务。
- `overlay`: overlay网络将多个Docker守护程序连接在一起，并使群集服务能够相互通信。您还可以使用overlay网络来促进群集服务和独立容器之间或不同Docker守护程序上的两个独立容器之间的通信。这种策略消除了在这些容器之间进行操作系统级路由的需要。
- `macvlan`: Macvlan网络允许您将MAC地址分配给容器，使其在网络上显示为物理设备。 Docker守护程序通过其MAC地址将流量路由到容器。 在处理希望直接连接到物理网络而不是通过Docker主机的网络堆栈进行路由的传统应用程序时，使用macvlan驱动程序有时是最佳选择。
- `none`: 对于此容器，禁用所有联网。 通常与自定义网络驱动程序一起使用。`none` 不适用于swarm services。
- `网络插件`：您可以在Docker中安装和使用第三方网络插件。 这些插件可从Docker Hub或第三方供应商处获得。 有关安装和使用给定网络插件的信息，请参阅供应商的文档。


## 问题解决方案

这边docker使用 `bridge` 默认网络驱动，可以通过下面命令查看。

```bash 
$ docker network ls

NETWORK ID          NAME                        DRIVER              SCOPE
d272f62d6c83        bridge                      bridge              local
cbea675a9b55        harbor_harbor               bridge              local
00ad661b240e        harbor_harbor-chartmuseum   bridge              local
71141a653963        harbor_harbor-clair         bridge              local
f3c6a8011e1c        harbor_harbor-notary        bridge              local
7da474653425        harbor_notary-sig           bridge              local
0f0da1e208cc        host                        host                local
bc296f30386f        none                        null                local
```

### 解决思路

把 `docker0` 指定其它网段，不要使用 `172.16.0.0/12` 网段。并且也控制 `docker-compose` 创建网段配置范围。这里不直接在 `docker-compose` 配置声明，而是修改 docker 配置来实现。

### 解决方法

修改 docker 配置 `/etc/docker/daemon.json` 文件，具体如下修改：

```bash
# 添加下面配置
$ vim /etc/docker/daemon.json

{"bip": "10.50.0.1/16", "default-address-pools": [{"base": "10.51.0.1/16", "size": 24}]}

# 重启 docker 服务
$ systemctl restart docker
```

上面配置意思：设置 `docker0` 使用 `10.50.0.1/16` 网段，`docker0` 为 `10.50.0.1`。后面服务再创建地址池使用 `10.51.0.1/16` 网段范围划分，每个子网掩码划分为 `255.255.255.0`。具体划分看下面 harbor 创建例子。

![](/img/docker-network-route-2.png)

最后，重新规划 docker 网络，这样就不会影响云主机内网通信。

## 参考文章

- [1] https://juejin.im/post/5e4f6d006fb9a07c8e6a2ca1