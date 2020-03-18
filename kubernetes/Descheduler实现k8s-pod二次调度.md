## 前言

Kubernetes中的调度是将待处理的pod绑定到节点的过程，由Kubernetes的一个名为`kube-scheduler`的组件执行。调度程序的决定，无论是否可以或不能调度容器，都由其可配置策略指导，该策略包括一组规则，称为`谓词`和`优先级`。调度程序的决定受到其在第一次调度时出现新pod时的Kubernetes集群视图的影响。由于Kubernetes集群非常动态且状态随时间而变化，因此可能需要将已经运行的pod重新调试到其它节点上，已达到节点使用资源平衡。

## kube-scheduler 简介

`kube-scheduler` 是 Kubernetes 集群的默认调度器，并且是集群 控制面 的一部分。

对每一个新创建的 Pod 或者是未被调度的 Pod，kube-scheduler 会选择一个最优的 Node 去运行这个 Pod。然而，Pod 内的每一个容器对资源都有不同的需求，而且 Pod 本身也有不同的资源需求。因此，Pod 在被调度到 Node 上之前，根据这些特定的资源调度需求，需要对集群中的 Node 进行一次过滤。

在一个集群中，满足一个 Pod 调度请求的所有 Node 称之为 _可调度节点_。如果没有任何一个 Node 能满足 Pod 的资源请求，那么这个 Pod 将一直停留在未调度状态直到调度器能够找到合适的 Node。

调度器先在集群中找到一个 Pod 的所有可调度节点，然后根据一系列函数对这些可调度节点打分，然后选出其中得分最高的 Node 来运行 Pod。之后，调度器将这个调度决定通知给 kube-apiserver，这个过程叫做 `绑定`。

在做调度决定时需要考虑的因素包括：单独和整体的资源请求、硬件/软件/策略限制、亲和以及反亲和要求、数据局域性、负载间的干扰等等。

## kube-scheduler 调度流程

kube-scheduler 给一个 pod 做调度选择包含两个步骤：

- `过滤`：过滤阶段会将所有满足 Pod 调度需求的 Node 选出来。例如，PodFitsResources 过滤函数会检查候选 Node 的可用资源能否满足 Pod 的资源请求。在过滤之后，得出一个 Node 列表，里面包含了所有可调度节点；通常情况下，这个 Node 列表包含不止一个 Node。如果这个列表是空的，代表这个 Pod 不可调度。
- `打分`：打分阶段，调度器会为 Pod 从所有可调度节点中选取一个最合适的 Node。根据当前启用的打分规则，调度器会给每一个可调度节点进行打分。最后，kube-scheduler 会将 Pod 调度到得分最高的 Node 上。如果存在多个得分最高的 Node，kube-scheduler 会从中随机选取一个。

> `kube-scheduler` 具体介绍参考 https://kubernetes.io/zh/docs/concepts/scheduling/kube-scheduler/

## 为什么需要二次调试 Pod

- 一些节点不足或过度使用。
- 原始调度决策不再适用，因为在节点中添加或删除了污点或标签，不再满足 pod/node 亲和性要求。
- 某些节点发生故障，其pod已移至其他节点
- 集群添加新节点

因此，可能会在群集中不太理想的节点上安排多个pod。`Descheduler`根据其政策，发现可以移动并移除它们的pod。请注意，在当前的实现中，Descheduler 不会安排更换被驱逐的pod，而是依赖于默认的调度程序。

## 解决节点上Pod不平衡方法

这就是本文想讲的 `Descheduler` 项目，根据该项目二次调度策略来解决上面所说的问题。具体策略说明如下：

### RemoveDuplicates 策略

该策略确保只有一个Pod与在同一节点上运行的副本集（RS），Replication Controller（RC），Deployment或Job相关联。如果还有更多，则将这些重复的容器逐出，以更好地在群集中扩展容器。如果某些节点由于任何原因而崩溃，并且它们上的Pod移至其他节点，导致多个与RS或RC关联的Pod（例如在同一节点上运行），则可能发生此问题。一旦出现故障的节点再次准备就绪，便可以启用此策略以驱逐这些重复的Pod。当前，没有与该策略关联的参数。要禁用此策略，策略应如下所示：

```yaml
apiVersion: "descheduler/v1alpha1"
kind: "DeschedulerPolicy"
strategies:
  "RemoveDuplicates":
     enabled: false
```

### LowNodeUtilization 策略

该策略发现未充分利用的节点，并且如果可能的话，从其他节点驱逐pod，希望在这些未充分利用的节点上安排被驱逐的pod的重新创建。此策略的参数配置在 `nodeResourceUtilizationThresholds`。

节点的利用率低是由可配置的阈值决定的 `thresholds`。`thresholds` 可以按百分比为cpu，内存和pod数量配置阈值 。如果节点的使用率低于所有（cpu，内存和pod数）的阈值，则该节点被视为未充分利用。目前，pods的请求资源需求被考虑用于计算节点资源利用率。

还有另一个可配置的阈值，`targetThresholds` 用于计算可以驱逐pod的潜在节点。任何节点，所述阈值之间，`thresholds` 并且 `targetThresholds` 被视为适当地利用，并且不考虑驱逐。阈值 `targetThresholds` 也可以按百分比配置为cpu，内存和pod数量。

这些阈值 `thresholds` 和 `targetThresholds` 可以根据您的集群要求进行调整。这是此策略的策略示例：

```yaml
apiVersion: "descheduler/v1alpha1"
kind: "DeschedulerPolicy"
strategies:
  "LowNodeUtilization":
     enabled: true
     params:
       nodeResourceUtilizationThresholds:
         thresholds:
           "cpu" : 20
           "memory": 20
           "pods": 20
         targetThresholds:
           "cpu" : 50
           "memory": 50
           "pods": 50
```

与该 `LowNodeUtilization` 策略相关的另一个参数称为 `numberOfNodes`。仅当未充分利用的节点数大于配置的值时，才可以配置此参数以激活策略。这在大型群集中很有用，其中一些节点可能会频繁使用或短期使用不足。默认情况下，`numberOfNodes`设置为0。

### RemovePodsViolatingInterPodAntiAffinity 策略

该策略可确保从节点中删除违反Interpod反亲和关系的pod。例如，如果某个节点上有`podA`，并且`podB`和`podC`（在同一节点上运行）具有禁止它们在同一节点上运行的反亲和规则，则`podA`将被从该节点逐出，以便`podB`和`podC`正常运行。当 `podB` 和 `podC` 已经运行在节点上后，反亲和性规则被创建就会发送这样的问题。目前，没有与该策略关联的参数。要禁用此策略，策略应如下所示：

```yaml
apiVersion: "descheduler/v1alpha1"
kind: "DeschedulerPolicy"
strategies:
  "RemovePodsViolatingInterPodAntiAffinity":
     enabled: false
```

### RemovePodsViolatingNodeAffinity 策略

此策略可确保从节点中删除违反节点关联的pod。例如，在nodeA上调度了podA，它在调度时满足节点关联性规则`requiredDuringSchedulingIgnoredDuringExecution`，但随着时间的推移，nodeA不再满足该规则，那么如果另一个节点nodeB可用，它满足节点关联性规则，那么podA将被逐出nodeA。策略文件如下所示：

```yaml
apiVersion: "descheduler/v1alpha1"
kind: "DeschedulerPolicy"
strategies:
  "RemovePodsViolatingNodeAffinity":
    enabled: true
    params:
      nodeAffinityType:
      - "requiredDuringSchedulingIgnoredDuringExecution"
```

### RemovePodsViolatingNodeTaints 策略

该策略可以确保从节点中删除违反 `NoSchedule` 污点的 `Pod`。例如，有一个名为 `podA` 的 `Pod`，通过配置容忍 `key=value:NoSchedule` 允许被调度到有该污点配置的节点上，如果节点的污点随后被更新或者删除了，则污点将不再被 `Pod` 的容忍满足，然后将被驱逐，策略文件如下所示：

```yaml
apiVersion: "descheduler/v1alpha1"
kind: "DeschedulerPolicy"
strategies:
  "RemovePodsViolatingNodeTaints":
    enabled: true
```

## Pod 驱逐机制

当 `Descheduler` 程序决定从节点驱逐 Pod 时，它采用以下常规机制：

- [关键Pod](https://kubernetes.io/docs/tasks/administer-cluster/guaranteed-scheduling-critical-addon-pods/)（priorityClassName 设置为 system-cluster-critical 或 system-node-critical）不会被驱逐。
- 永远不会驱逐不属于RC，RS，Deployment或Job的Pod（静态或镜像 Pod 或 独立Pod），因为不会重新创建这些Pod。
- 与 DaemonSets 关联的Pod不会被逐出。
- 永远不会驱逐具有本地存储的 Pod。
- 首先驱逐 `Best-Effort`，再驱逐 `Burstable`、最后驱逐 `Guaranteed` 的优先级。
- 带有注释 `descheduler.alpha.kubernetes.io/evict` 的所有类型的Pod都会被逐出。该注释用于覆盖防止驱逐的检查，用户可以选择驱逐哪个 Pod。用户应该知道如何以及是否可以重新创建容器。

> 注意：`PDB` 不受 `Descheduler` 控制

## 版本兼容性

![](/img/Descheduler.png)

## 部署

`Descheduler` 可以在k8s集群中作为 `Job` 或`CronJob` 运行。它的优点是可以多次运行而无需用户干预。该调度程序容器在 `kube-system` 命名空间中作为关键容器运行，以避免被自身或kubelet逐出。

### `Job` 运行

```bash
$ kubectl create -f kubernetes/rbac.yaml
$ kubectl create -f kubernetes/configmap.yaml
$ kubectl create -f kubernetes/job.yaml
```

### `CronJob` 运行

```bash
$ kubectl create -f kubernetes/rbac.yaml
$ kubectl create -f kubernetes/configmap.yaml
$ kubectl create -f kubernetes/cronjob.yaml
```

> 注意：上面说到的五种策略都以 `ConfigMap` 形式配置

例如：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: descheduler-policy-configmap
  namespace: kube-system
data:
  policy.yaml: |
    apiVersion: "descheduler/v1alpha1"
    kind: "DeschedulerPolicy"
    strategies:
      "RemoveDuplicates":
         enabled: true
      "RemovePodsViolatingInterPodAntiAffinity":
         enabled: true
      "LowNodeUtilization":
         enabled: true
         params:
           nodeResourceUtilizationThresholds:
             thresholds:
               "cpu" : 20
               "memory": 20
               "pods": 20
             targetThresholds:
               "cpu" : 50
               "memory": 50
               "pods": 50
```

## 参考链接

- https://kubernetes.io/zh/docs/concepts/scheduling/kube-scheduler/
- https://github.com/kubernetes-sigs/descheduler
- https://zhuanlan.zhihu.com/p/73689369