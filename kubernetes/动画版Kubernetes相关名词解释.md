## 前言

近几年，做为运维或者开发耳边都会听到`K8S`这个词，`K8S` 是 `Kubernetes` 简称。`Kubernetes` 这个单词中 k 与 s 中间有8个字母，所以简称为K8S。那什么是 `K8S` ？下文通过动画简单介绍 `K8S`。

## 作者

- Written by: Matt Butcher & Karen Chu
- Illustrated by: Bailey Beougher
- Designed by: Karen Chu 

## 什么是 Pod ?

![](/img/k8s-chahua-1.png)

![](/img/k8s-chahua-2.png)

![](/img/k8s-chahua-3.png)

![](/img/k8s-chahua-4.png)

在Kubernetes中，pod负责运行容器。每个Pod至少有一个容器，
并控制该容器的执行。当容器退出时，Pod也会死亡。


## 什么是 ReplicaSets ？

![](/img/k8s-chahua-5.png)

![](/img/k8s-chahua-6.png)

`ReplicaSets`：副本集确保一组相同配置的pod以所需的副本计数运行。如果一个 Pod 终止运行，ReplicaSets 会创建一个新的替换终止的Pod，始终达到与声明 replicas 相等的值。

## 什么是 Secrets ？

![](/img/k8s-chahua-7.png)

![](/img/k8s-chahua-8.png)

`Secrets`：用于存储非公共信息，如令牌、证书或密码。Secrets 可以在运行时附加到 Pods，以便将敏感的配置数据可以安全地存储在集群中。

## 什么是 Deployments ？

![](/img/k8s-chahua-9.png)

![](/img/k8s-chahua-10.png)

`Deployment`：是用来控制部署和维护一组 Pod(是将Pod实际部署到群集的方式)。在后台，它使用一个 ReplicaSet 来保持 Pod 的运行，而且为部署、更新和扩展集群中的 Pod 提供了高级功能。

## 什么是 DaemonSets ？

![](/img/k8s-chahua-11.png)

![](/img/k8s-chahua-12.png)

`DaemonSets`：提供了一种方法来确保 Pod 的副本在集群中的每个节点上运行。当集群发展或收缩时，DaemonSet 将这些有特殊标记的 Pods 部署到所有节点上。

## 什么是 Ingresses ？

![](/img/k8s-chahua-13.png)

![](/img/k8s-chahua-14.png)

`Ingresses`：提供一种负载均衡方法，用于将群集外部的访问，负载到群集内部相应目的 Pod。一个外部的 Ingresses 入口可以导向许多不同的内部服务。

## 什么是 CronJobs ？

![](/img/k8s-chahua-15.png)

![](/img/k8s-chahua-16.png)

`CronJobs`：提供了一种调度pod执行的方法。它们非常适合定期运行备份、报告和自动化测试等任务。

## 什么是 CRD ？

![](/img/k8s-chahua-17.png)

![](/img/k8s-chahua-18.png)

`CustomResourceDefinitions`：简称 `CRD` 它提供了一种扩展机制，集群的操作人员和开发人员可以使用它来创建自己的资源类型。

## 结束

“哦，” Phippy 满脸担忧地说，“看，午饭时间到了，我们该回家了。”

Zee 松了一口气。“回家的时候可以在库伯船长的奶昔店停一下吗？”

![](/img/k8s-chahua-19.png)

（Zee 恋恋不舍地走了，出门前，他回过头又看到了飞翔的蜥蜴）

![](/img/k8s-chahua-20.png)


> 完整的动画下载地址：https://azure.microsoft.com/mediahandler/files/resourcefiles/phippy-goes-to-the-zoo/Phippy%20Goes%20To%20The%20Zoo_MSFTonline.pdf

## 参考链接

- https://mp.weixin.qq.com/s/MRqQ6kAhAKAPb5b9zOH5Gw