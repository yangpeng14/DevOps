## Pod Eviction 简介

`Pod Eviction` 是k8s一个特色功能，它在某些场景下应用，如节点NotReady、Node节点资源不足，把pod驱逐至其它Node节点。

从发起模块的角度，pod eviction 可以分为两类：

- Kube-controller-manager: 周期性检查所有节点状态，当节点处于 NotReady 状态超过一段时间后，驱逐该节点上所有 pod。
- Kubelet: 周期性检查本节点资源，当资源不足时，按照优先级驱逐部分 pod。

## Kube-controller-manger 触发的驱逐

`Kube-controller-manager` 周期性检查节点状态，每当节点状态为 NotReady，并且超出 podEvictionTimeout 时间后，就把该节点上的 pod 全部驱逐到其它节点，其中具体驱逐速度还受驱逐速度参数，集群大小等的影响。提供了以下启动参数控制eviction。

- `pod-eviction-timeout`：即当节点宕机该事件间隔后，开始eviction机制，驱赶宕机节点上的Pod，默认为5min
- `node-eviction-rate`: 驱赶速率，即驱赶Node的速率，由令牌桶流控算法实现，默认为0.1，即每秒驱赶0.1个节点，注意这里不是驱赶Pod的速率，而是驱赶节点的速率。相当于每隔10s，清空一个节点
- `secondary-node-eviction-rate`: 二级驱赶速率，当集群中宕机节点过多时，相应的驱赶速率也降低，默认为0.01
- `unhealthy-zone-threshold`：不健康zone阈值，会影响什么时候开启二级驱赶速率，默认为0.55，即当该zone中节点宕机数目超过55%，而认为该zone不健康
- `large-cluster-size-threshold`：大集群法制，当该zone的节点多余该阈值时，则认为该zone是一个大集群。大集群节点宕机数目超过55%时，则将驱赶速率降为0.0.1，假如是小集群，则将速率直接降为0


## Kubelet 触发的驱逐

在讲 Kubelet 驱逐之前，首先得知道 kubelet node 预留，具体介绍，请参考我上篇文章 [Kubernetes Node资源预留](https://www.yp14.cn/2020/01/09/Kubernetes-Node%E8%B5%84%E6%BA%90%E9%A2%84%E7%95%99/)。


Kubelet 周期性检查本节点的内存和磁盘资源，当可用资源低于阈值时，则按照优先级驱逐 pod，具体检查的资源如下：

- memory.available
- nodefs.available
- nodefs.inodesFree
- imagefs.available
- imagefs.inodesFree

kubelet 只支持两种文件系统分区：

- `nodefs` 文件系统，kubelet 将其用于卷和守护程序日志等。
- `imagefs` 文件系统，容器运行时用于保存镜像和容器可写层，imagefs 是可选的参数。

以内存资源为例，当内存资源低于阈值时，驱逐的优先级大体为 `BestEffort > Burstable > Guaranteed`，具体的顺序可能因实际使用量有所调整。当发生驱逐时，kubelet 支持 `soft` 和 `hard` 两种模式，`soft` 模式表示缓期一段时间后驱逐，`hard` 模式表示立刻驱逐。

### Kubelet 软驱逐阈值

`软驱逐阈值` 使用一对由驱逐阈值和管理员必须指定的宽限期组成的配置对。在超过宽限期前，kubelet不会采取任何动作回收和驱逐信号关联的资源。如果没有提供宽限期，kubelet启动时将报错。

此外，如果达到了软驱逐阈值，操作员可以指定从节点驱逐 pod 时，在宽限期内允许结束的 pod 的最大数量。如果指定了 pod.Spec.TerminationGracePeriodSeconds 值，kubelet将使用它和宽限期二者中较小的一个。如果没有指定，kubelet将立即终止 pod，而不会优雅结束它们。

软驱逐阈值的配置支持下列标记：

- `eviction-soft` 描述了驱逐阈值的集合（例如 memory.available<1.5Gi），如果在宽限期之外满足条件将触发 pod 驱逐。
- `eviction-soft-grace-period` 描述了驱逐宽限期的集合（例如 memory.available=1m30s），对应于在驱逐 pod 前软驱逐阈值应该被控制的时长。
- `eviction-max-pod-grace-period` 描述了当满足软驱逐阈值并终止 pod 时允许的最大宽限期值（秒数）。

### Kubelet 硬驱逐阈值

硬驱逐阈值没有宽限期，一旦触发，kubelet将立即采取行动回收关联的短缺资源。如果满足硬驱逐阈值，kubelet将立即结束 pod 而不是优雅终止。

硬驱逐阈值的配置支持下列标记：

- `eviction-hard` 描述了驱逐阈值的集合（例如 memory.available<1Gi），如果满足条件将触发 pod 驱逐。


## 对上篇 Kubernetes Node资源预留 参数解释

- --system-reserved=memory=3Gi,storage=5Gi # 设置预留系统服务的资源
- --eviction-hard=memory.available<1Gi,nodefs.available<10Gi,imagefs.available<15Gi # 硬驱逐阈值，描述了驱逐阈值的集合，如果满足条件将触发 pod 驱逐
- --eviction-soft=memory.available<1.5Gi,nodefs.available<15Gi,imagefs.available<20Gi # 软驱逐阈值，描述了驱逐阈值的集合，如果在宽限期之外满足条件将触发 pod 驱逐
- --eviction-soft-grace-period=memory.available=2m,nodefs.available=2m,imagefs.available=2m # 软驱逐阈值，描述了驱逐宽限期的集合，对应用在驱逐 pod 前软驱逐阈值应该被控制的时长
- --eviction-max-pod-grace-period=30 # 描述了当满足软驱逐阈值并终止 pod 时允许的最大宽限期值（秒数）
- --eviction-minimum-reclaim=memory.available=200Mi,nodefs.available=5Gi,imagefs.available=5Gi # 最小驱逐，默认值为 0

## 总结

对于 kubelet 触发的驱逐，往往是资源不足导致，它优先驱逐 BestEffort 类型的容器，这些容器多为离线批处理类业务，对可靠性要求低。驱逐后释放资源，减缓节点压力，弃卒保帅，保护了该节点的其它容器。无论是从其设计出发，还是实际使用情况，该特性非常 nice。

对于由 kube-controller-manager 触发的驱逐，效果需要商榷。正常情况下，计算节点周期上报心跳给 master，如果心跳超时，则认为计算节点 NotReady，当 NotReady 状态达到一定时间后，kube-controller-manager 发起驱逐。配置参数要按集群规模合理设置。

## 参考链接

- https://kubernetes.io/zh/docs/tasks/administer-cluster/out-of-resource/
- http://wsfdl.com/kubernetes/2018/05/15/node_eviction.html
- https://blog.csdn.net/redenval/article/details/84237654