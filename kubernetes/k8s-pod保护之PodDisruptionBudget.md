## 前言

在 `Kubernetes` 中，为了保证业务不中断或业务SLA不降级，需要将应用进行集群化部署。通过`PodDisruptionBudget` 控制器可以设置应用POD集群处于运行状态最低个数，也可以设置应用POD集群处于运行状态的最低百分比，这样可以保证在主动销毁应用POD的时候，不会一次性销毁太多的应用POD，从而保证业务不中断或业务SLA不降级。

## PodDisruptionBudget 简介

`Pod Disruption Budget` (pod 中断 预算) 简称`PDB`，含义其实是终止pod前通过 `labelSelector` 机制获取正常运行的`pod`数目的限制，目的是对`自愿中断`的保护措施。

> Kubernetes version >= 1.7 才支持 `PodDisruptionBudget`

## PDB 应用场景

- 节点维护或升级时 ( kubectl drain )

> 注意：如果 Node 状态处于 `not ready`，PDB 是不会生效，因为 PDB 只能针对`自愿中断`生效，什么叫 `自愿中断` 下文介绍。

## 自愿中断和非自愿中断 [1]

Pod 不会消失，直到有人（人类或控制器）将其销毁，或者当出现不可避免的硬件或系统软件错误。

我们把这些不可避免的情况称为应用的`非自愿性中断`。例如：

- 后端节点物理机的硬件故障
- 集群管理员错误地删除虚拟机（实例）
- 云提供商或管理程序故障使虚拟机消失
- 内核恐慌（kernel panic）
- 节点由于集群网络分区而从集群中消失
- 由于节点[资源不足](https://kubernetes.io/docs/tasks/administer-cluster/out-of-resource)而将容器逐出

除资源不足的情况外，大多数用户应该都熟悉以下这些情况；它们不是特定于 Kubernetes 的。

我们称这些情况为`自愿中断`。包括由应用程序所有者发起的操作和由集群管理员发起的操作。典型的应用程序所有者操作包括：

- 删除管理该 pod 的 Deployment 或其他控制器
- 更新了 Deployment 的 pod 模板导致 pod 重启
- 直接删除 pod（意外删除）

集群管理员操作包括：

- [排空（drain）节点](https://kubernetes.io/docs//tasks/administer-cluster/safely-drain-node)进行修复或升级。
- 从集群中排空节点以缩小集群（了解[集群自动调节](https://kubernetes.io/docs/tasks/administer-cluster/cluster-management/#cluster-autoscaler)）。
- 从节点中移除一个 pod，以允许其他 pod 使用该节点。

这些操作可能由集群管理员直接执行，也可能由集群管理员或集群托管提供商自动执行。


## PDB 关键参数与注意事项

- `.spec.minAvailable`：表示发生`自愿中断`的过程中，要保证至少可用的Pods数或者比例
- `.spec.maxUnavailable`：表示发生`自愿中断`的过程中，要保证最大不可用的Pods数或者比例

上面配置只能用来对应 `Deployment`，`RS`，`RC`，`StatefulSet`的Pods，推荐优先使用 `.spec.maxUnavailable`。

`注意`：

- 同一个 PDB Object 中不能同时定义 `.spec.minAvailable` 和 `.spec.maxUnavailable`。
- 前面提到，应用滚动更新时Pod的`delete`和`unavailable`虽然也属于`自愿中断`，但是实际上滚动更新有自己的策略控制（`marSurge` 和 `maxUnavailable`），因此PDB不会干预这个过程。
- PDB 只能保证`自愿中断`时的副本数，比如 `evict pod`过程中刚好满足 `.spec.minAvailable` 或 `.spec.maxUnavailable`，这时某个本来正常的Pod突然因为`Node Down`(非自愿中断)挂了，那么这个时候实际Pods数就比PDB中要求的少了，因此PDB不是万能的！

使用上，如果设置 `.spec.minAvailable` 为 `100%` 或者 `.spec.maxUnavailable` 为 `0%`，意味着会完全阻止 `evict pods` 的过程（ `Deployment`和`StatefulSet`的`滚动更新除外` ）。

## PDB 例子

- 下面的例子使用了 `minAvailable` 参数：

    ```yaml
    apiVersion: policy/v1beta1
    kind: PodDisruptionBudget
    metadata:
      name: nginx-pdb
      namespace: default
    spec:
      minAvailable: 2
      selector:
        matchLabels:
          app: nginx
    ```

- 下面的例子使用了 `maxUnavailable` 参数：

    ```yaml
    apiVersion: policy/v1beta1
    kind: PodDisruptionBudget
    metadata:
      name: nginx-pdb
      namespace: default
    spec:
      maxUnavailable: 30%
      selector:
        matchLabels:
          app: nginx
    ```

## 参考链接

- [1] https://jimmysong.io/kubernetes-handbook/concepts/pod-disruption-budget.html
- https://blog.csdn.net/horsefoot/article/details/76496496
- https://cloud.tencent.com/developer/article/1096947