## 前言

最近，我开始了 Kubernetes 之旅，希望更好地了解其内部。下面简单介绍下吧！

## 容器

在我们尝试了解 Kubernetes 之前，让我们花一点时间来澄清什么是容器，以及为什么它们如此受欢迎。毕竟，在不知道容器是什么的情况下谈论容器编排器（Kubernetes）毫无意义。

![容器](/img/1_lus49PaFI90rVMd23fV86A.png)

`容器`：是一个用来存放您放入的所有物品的容器。

像您的应用程序代码，依赖库及其依赖关系一直到内核。这里的关键概念是隔离。将所有内容与其余内容隔离开，以便您更好地控制它们。容器提供三种隔离类型：

- 工作区隔离（进程，网络）
- 资源隔离（CPU，内存）
- 文件系统隔离（联合文件系统）


考虑一下像VM一样的容器。它们精简，快速（启动）且体积小。而且，所有这些都没有建立起来。取而代之的是，他们使用linux系统中存在的构造（例如cgroups，名称空间）在其上构建了一个不错的抽象。

现在我们知道什么是容器了，很容易理解为什么它们很受欢迎。不仅可以仅分发应用程序二进制/代码，还可以以实用的方式分发运行应用程序所需的整个环境，因为可以将容器构建为非常小的单元。解决“在我的机器上工作”问题的完美解决方案。

## 什么时候使用Kubernetes？

容器一切都很好，软件开发人员的生活现在要好很多。那么，为什么我们需要另一项技术，例如 Kubernetes 这样的容器编排工具呢？

![](/img/1_QDhBk9xFa77T4n3-5lHIsg.png)

进入此状态时，需要使用它，那里的容器太多，无法管理

问：我的前端容器在哪里，我要运行几个？

答：很难说。使用容器编排工具

问：如何使前端容器与新创建的后端容器对话？

答：对IP进行硬编码。或者，使用容器编排工具

问：如何进行滚动升级？

答：在每个步骤中手动升级。或者，使用容器编排工具

## 为什么我更喜欢 Kubernetes

有多个编排工具，例如 `docker swarm`，`Mesos`和`Kubernetes`。我的选择是Kubernetes（因此是本文），因为Kubernetes是……

![](/img/1_eHVk7p4I2LuSnVwvYaHbyw.png)

就像乐高积木一样。它不仅具有大规模运行容器协调器所需的组件，而且还具有使用自定义组件灵活地交换不同组件的灵活性。想要拥有一个自定义的调度程序，请确保将其插入。需要具有新的资源类型，编写一个CRD。此外，社区非常活跃，并且工具迅速发展。

## Kubernetes 架构

![](/img/1_xYujRQjcpd-mQbNTwEbukA.png)

每个Kubernetes集群都有两种类型的节点。Master 和 Node。顾名思义，Master 是在工作程序运行有效负载（应用程序）的地方控制和监视群集。

群集可以与单个主节点一起使用。但是最好拥有三个以实现高可用性（称为HA群集）
让我们仔细看一下 Master节点及其组成。

![](/img/1_qgogo7I03e5kyNWKVWtFYg.png)

`etcd`：用于存储有关 kubernetes 对象，其当前状态，访问信息和其他集群配置信息的所有数据的数据库。

`API Server`： `RESTful API` 服务器，公开端点以操作集群。主节点和工作节点中的几乎所有组件都与此服务通信以执行其职责。

`Scheduler`：负责决定哪些有效负载需要在哪台机器上运行。

`Control Manager`：这是一个控制循环，监视集群的状态（通过调用API Server来获取此数据），并采取措施将其置于预期状态。

![](/img/1_sHmUG1htz-brFTGPz3HXXQ.png)

`kubelet`：是工作程序节点的心脏。它与主节点 API Server 通信，并负责该宿主机容器的启停。

`kube-proxy`：使用 Iptables / IPVS 处理Pod的网络需求，提供 Service 服务发现。

`Pod`：是 kubernetes 最小单元。如果没有Pod的抽象，就不能在kubernetes中运行容器。Pod添加了对kuberenetes容器之间的联网方式至关重要的功能。

![快乐的Pod](/img/1_c80mIDN0Wz7b2xb5Qfxerw.png)

一个 Pod 可以有多个容器，并且在这些容器中运行的所有服务都可以将彼此视为本地主机。这使得将应用程序的不同方面分离为单独的容器，并将它们全部作为一个容器加载在一起非常方便。有不同的吊舱模式，例如 Sidecar，Proxy 和 ambassador，可以满足不同的需求。[查看本文以了解有关它们的更多信息](https://matthewpalmer.net/kubernetes-app-developer/articles/multi-container-pod-design-patterns.html)。

Pod 网络接口提供了一种将其与同一节点和其他工作程序节点中的其他Pod联网的机制。

![](/img/1_F2wfrW5zO6Y36Yr_jL014g.png)

而且，每个Pod都将分配有自己的IP地址，kube-proxy 会使用该IP地址来路由流量。而且此IP地址仅在群集中可见。

所有容器也可以看到安装在容器内的卷，有时这些卷可用于在容器之间进行异步通信。例如，假设您的应用是照片上传应用（例如instagram），它可以将这些文件保存在一个卷中，而同一容器中的另一个容器可以监视该卷中的新文件，并开始对其进行处理以创建多种尺寸，将它们上传到云存储。

## Controllers

在kubernetes中，有很多控制器，例如 `ReplicaSet`，`Replication Controllers`，`Deployment`，`StatefulSets`和`Service`。这些是以一种或另一种方式控制吊舱的对象。让我们看一些重要的。

## ReplicaSet

![ReplicaSet 做自己擅长的事情，复制 Pod](/img/1_CrG3p2FUcjiHhwLyGQzQ2Q.png)

该控制器的主要职责是创建给定Pod的副本。如果某个吊舱因某种原因死亡，则会通知该控制器，并立即采取行动以创建新的吊舱。

## Deployment

![试图控制 ReplicaSet 的部署（头发凌乱）](/img/1_6qQCQLV8cIBkMY7K4GKrig.png)

部署是一个高阶对象，它使用 ReplicaSet 来管理副本。它提供了通过扩大滚动升级新 ReplicaSet 和比例下降（最终删除）现有 ReplicaSet。

## Service

![表示为无人机的服务，将数据包传递到相应的Pod](/img/1_oAF5BE2RplGHtGmcC0L5Ew.png)

Service 是一个控制器对象，其主要职责是在将“数据包”分发到相应节点时充当负载平衡器。基本上，它是一种控制器构造，用于在工作节点之间对相似的容器（通常由容器标签标识）进行分组。

假设您的“前端”应用程序想与“后端”应用程序通信，则每个应用程序可能有许多正在运行的实例。您不必担心对每个后端Pod的IP进行硬编码，而是将数据包发送到后端服务，然后由后端服务决定如何进行负载平衡并相应地转发。

> PS：请注意，服务更像是一个虚拟实体，因为所有数据包路由都由 IPtables/ IPVS / CNI插件 处理。它只是使它更容易被视为一个真正的实体，让他们脱颖而出以了解其在kubernetes 生态系统中的作用。

## Ingress

![进入一个浮动平台，所有数据包都通过该平台流入集群](/img/1_FEufKCJPNrCwkrJkwtjQWQ.png)

Ingress 是与外界联系的服务，可以与集群中运行的所有服务进行对话。这使我们可以轻松地在单个位置设置安全策略，监控甚至记录日志.

> PS：Kubernetes 中还有许多其他控制器对象，例如 `DaemonSets`，`StatefulSets` 和`Jobs`。还有一些诸如 `Secrets`，`ConfigMaps` 之类的对象，用于存储应用程序的机密和配置。

## 文章出处

> - 作者：Sudhakar Rayavaram
> - 原文：https://medium.com/tarkalabs/know-kubernetes-pictorially-f6e6a0052dd0