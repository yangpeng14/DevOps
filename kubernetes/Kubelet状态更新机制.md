## 概览
当 Kubernetes 中 Node 节点出现状态异常的情况下，节点上的 Pod 会被重新调度到其他节点上去，但是有的时候我们会发现节点 Down 掉以后，Pod 并不会立即触发重新调度，这实际上就是和 Kubelet 的状态更新机制密切相关的，Kubernetes 提供了一些参数配置来触发重新调度到嗯时间，下面我们来分析下 Kubelet 状态更新的基本流程。

1. kubelet 自身会定期更新状态到 apiserver，通过参数 `--node-status-update-frequency` 指定上报频率，默认是 10s 上报一次。
2. kube-controller-manager 会每隔 `--node-monitor-period` 时间去检查 kubelet 的状态，默认是 5s。
3. 当 node 失联一段时间后，kubernetes 判定 node 为 `notready` 状态，这段时长通过 `--node-monitor-grace-period` 参数配置，默认 40s。
4. 当 node 失联一段时间后，kubernetes 判定 node 为 `unhealthy` 状态，这段时长通过 `--node-startup-grace-period` 参数配置，默认 1m0s。
5. 当 node 失联一段时间后，kubernetes 开始删除原 node 上的 pod，这段时长是通过 `--pod-eviction-timeout` 参数配置，默认 5m0s
> kube-controller-manager 和 kubelet 是异步工作的，这意味着延迟可能包括任何的网络延迟、apiserver 的延迟、etcd 延迟，一个节点上的负载引起的延迟等等。因此，如果 `--node-status-update-frequency` 设置为5s，那么实际上 etcd 中的数据变化会需要 6-7s，甚至更长时间。Kubelet在更新状态失败时，会进行 `nodeStatusUpdateRetry` 次重试，默认为 `5 次`。

Kubelet 会在函数 `tryUpdateNodeStatus` 中尝试进行状态更新。Kubelet 使用了 Golang 中的 `http.Client()` 方法，但是没有指定超时时间，因此，如果 API Server 过载时，当建立 TCP 连接时可能会出现一些故障。

因此，在 `nodeStatusUpdateRetry * --node-status-update-frequency` 时间后才会更新一次节点状态。

同时，Kubernetes 的 controller manager 将尝试每 `--node-monitor-period` 时间周期内检查`nodeStatusUpdateRetry` 次。在 `--node-monitor-grace-period` 之后，会认为节点 unhealthy，然后会在`--pod-eviction-timeout` 后删除 Pod。

kube proxy 有一个 watcher API，一旦 Pod 被驱逐了，kube proxy 将会通知更新节点的 iptables 规则，将 Pod 从 Service 的 Endpoints 中移除，这样就不会访问到来自故障节点的 Pod 了。


## 配置

对于这些参数的配置，需要根据不通的集群规模场景来进行配置。

### 社区默认的配置

参数 | 说明 | 值
---|:---|:---
–node-status-update-frequency | kubelet 间隔多少时间向apiserver上报node status信息 | 10s
–node-monitor-period | kube-controller-manager 间隔多少时间后从apiserver同步node status信息 | 5s
–node-monitor-grace-period | kube-controller-manager 间隔多少时间之后，把node状态设置为NotReady | 40s
–pod-eviction-timeout | kube-controller-manager 在第一次kubelet notReady事件之后的多少时间后，开始驱逐pod。并不是CM把node状态设置为notready之后再等待 `pod-eviction-timeout` 时间 | 5m

### 快速更新和快速响应

参数 | 说明 | 值
---|:---|:---
–node-status-update-frequency | kubelet 间隔多少时间向apiserver上报node status信息 | 4s
–node-monitor-period | kube-controller-manager 间隔多少时间后从apiserver同步node status信息 | 2s
–node-monitor-grace-period | kube-controller-manager 间隔多少时间之后，把node状态设置为NotReady | 20s
–pod-eviction-timeout | kube-controller-manager 在第一次kubelet notReady事件之后的多少时间后，开始驱逐pod。并不是CM把node状态设置为notready之后再等待 `pod-eviction-timeout` 时间 | 30s

在这种情况下，Pod 将在 50s 被驱逐，因为该节点在 20s 后被视为Down掉了，`--pod-eviction-timeout` 在 30s 之后发生，Kubelet将尝试每4秒更新一次状态。因此，在Kubernetes控制器管理器考虑节点的不健康状态之前，它将是 (20s / 4s * 5) = 25 次尝试，但是，这种情况会给 etcd 产生很大的开销，因为每个节点都会尝试每 2s 更新一次状态。

如果环境有1000个节点，那么每分钟将有(60s / 4s * 1000) = 15000次节点更新操作，这可能需要大型 etcd 容器甚至是 etcd 的专用节点。

> 如果我们计算尝试次数，则除法将给出5，但实际上每次尝试的 nodeStatusUpdateRetry 尝试将从3到5。 由于所有组件的延迟，尝试总次数将在15到25之间变化。

### 中等更新和平均响应

参数 | 说明 | 值
---|:---|:---
–node-status-update-frequency | kubelet 间隔多少时间向apiserver上报node status信息 | 20s
–node-monitor-period | kube-controller-manager 间隔多少时间后从apiserver同步node status信息 | 5s
–node-monitor-grace-period | kube-controller-manager 间隔多少时间之后，把node状态设置为NotReady | 2m
–pod-eviction-timeout | kube-controller-manager 在第一次kubelet notReady事件之后的多少时间后，开始驱逐pod。并不是CM把node状态设置为notready之后再等待 `pod-eviction-timeout` 时间 | 1m

这种场景下会，Pod 将在 3m 被驱逐。 Kubelet将尝试每20秒更新一次状态。因此，在Kubernetes控制器管理器考虑节点的不健康状态之前，它将是 (2m 60 / 20s 5) = 30 次尝试

如果有 1000 个节点，1分钟之内就会有 (60s / 20s * 1000) = 3000 次的节点状态更新操作。


### 低更新和慢响应

参数 | 说明 | 值
---|:---|:---
–node-status-update-frequency | kubelet 间隔多少时间向apiserver上报node status信息 | 1m
–node-monitor-period | kube-controller-manager 间隔多少时间后从apiserver同步node status信息 | 5s
–node-monitor-grace-period | kube-controller-manager 间隔多少时间之后，把node状态设置为NotReady | 5m
–pod-eviction-timeout | kube-controller-manager 在第一次kubelet notReady事件之后的多少时间后，开始驱逐pod。并不是CM把node状态设置为notready之后再等待 `pod-eviction-timeout` 时间 | 1m

这种场景下会，Pod 将在 6m 被驱逐。 Kubelet将尝试每1分钟更新一次状态。因此，在Kubernetes控制器管理器考虑节点的不健康状态之前，它将是 (5m / 1m * 5) = 25 次尝试

如果有 1000 个节点，1分钟之内就会有 (1m / 60s * 1000) = 1000 次的节点状态更新操作。


## 参考链接

- https://github.com/kubernetes-sigs/kubespray/blob/master/docs/kubernetes-reliability.md
- https://github.com/Kevin-fqh/learning-k8s-source-code/blob/master/kubelet/(05)kubelet%E8%B5%84%E6%BA%90%E4%B8%8A%E6%8A%A5%26Evition%E6%9C%BA%E5%88%B6.md

## 原文出处
> 作者：icyboy

> http://team.jiunile.com/blog/2019/08/k8s-kubelet-sync-node-status.html