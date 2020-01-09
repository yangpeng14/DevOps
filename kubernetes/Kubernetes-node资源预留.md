## Node 为什么需要资源预留?

Kubernetes 的节点可以按照 `Capacity` 调度。默认情况下 pod 能够使用节点全部可用容量。这是个问题，因为节点自己通常运行了不少驱动 OS 和 Kubernetes 的系统守护进程（system daemons）。除非为这些系统守护进程留出资源，否则它们将与 pod 争夺资源并导致节点资源短缺问题。

按照是否为 Pod，可以把计算节点的进程分为两类：

- Pod 类进程：容器内部的进程，这些容器由 K8S 创建
- 非 Pod 类进程：系统进程，如内核，systemd 等；K8S 管理进程，如 Docker, Kubelet, Kube-proxy 等

如果没有资源预留，K8S 认为宿主机上所有的资源(RAM, CPU)都是可以分配给 Pod 类进程。因为非 Pod 类进程也需要占用一定的资源，当 Pod 创建很多时，就有可能出现资源不足的情况。宿主机中 kubelet、kube-proxy等进程被kill掉，最后导致整个 Node 节点不可用。

我们知道，当 Pod 里面内存不足时，会触发 Cgroup 把 Pod 里面的进程杀死；当系统内存不足时，就有可能触发系统 OOM，这时候根据 oom score 来确定优先杀死哪个进程，而 oom_score_adj 又是影响 oom score 的重要参数，其值越低，表示 oom 的优先级越低。在计算节点中，进程的 oom_score_adj 如下：

![](/img/oom-1.png)

所以，很大概率上，OOM 的优先级如下：

`BestEffort Pod > 其它进程 > Guarantee Pod > kubelet,docker,kube-proxy等 > sshd 等`

那么问题来了，如果节点没有 BestEffort 类型的 pod，那么其它进程就有可能被 OOM，包括系统进程等，后果可想而知。所以，预留一定的资源给系统和 K8S 管理服务，非常有必要。

## 预留多少资源

K8S 1.5 支持 CPU 和 RAM 两种资源的预留，更高版本支持 Disk 资源的预留。

`以下参考设置是个人建议`

- CPU：作为可压缩资源，超配的后果是运行变慢，影响较小，为了充分发挥节点性能，CPU 不预留
- RAM：8GB < RAM <= 16GB 预留 3GB; RAM > 16G 预留 4GB; (以上机器只跑k8s服务，没有额外应用服务)
- Disk：磁盘可预留 5% 至 10% 左右

## 如何预留

`kubelet` 公开了一个名为 `Node Allocatable` 的特性，有助于为系统守护进程预留计算资源。Kubernetes 推荐集群管理员按照每个节点上的工作负载密度配置 `Node Allocatable`。

Node Allocatable（节点可分配资源）：

```
      Node Capacity
---------------------------
|     kube-reserved       |
|-------------------------|
|     system-reserved     |
|-------------------------|
|    eviction-threshold   |
|-------------------------|
|                         |
|      allocatable        |
|   (available for pods)  |
|                         |
|                         |
---------------------------
```

Kubernetes 节点上的 `Allocatable` 被定义为 pod 可用计算资源量。调度器不会超额申请 `Allocatable`。目前支持 `CPU`, `memory` 和 `storage` 这几个参数。

Node Allocatable 暴露为 API 中 `v1.Node` 对象的一部分，也是 CLI 中 `kubectl describe node` 的一部分。

在 `kubelet` 中，可以为两类系统守护进程预留资源。

- 启用 QoS 和 Pod 级别的 cgroups

    为了恰当的在节点范围实施 `node allocatable`，您必须通过 `--cgroups-per-qos` 标志启用新的 cgroup 层次结构。这个标志是默认启用的。启用后，`kubelet` 将在其管理的 cgroup 层次结构中创建所有终端用户的 pod。

- 配置 cgroup 驱动

    `kubelet` 支持在主机上使用 cgroup 驱动操作 cgroup 层次结构。驱动通过 `--cgroup-driver` 标志配置。

    支持的参数值如下：

    - `cgroupfs` 是默认的驱动，在主机上直接操作 cgroup 文件系统以对 cgroup 沙箱进行管理。
    - `systemd` 是可选的驱动，使用 init 系统支持的资源的瞬时切片管理 cgroup 沙箱。

    取决于相关容器运行时（container runtime）的配置，操作员可能需要选择一个特定的 cgroup 驱动来保证系统正常运行。例如如果操作员使用 `docker` 运行时提供的 cgroup 驱动时，必须配置 `kubelet` 使用 `systemd cgroup` 驱动。


K8S 把计算节点资源分为 4 个部分：

- Kube Reserved：预留给 K8S 管理进程的资源，如 Kubelet，Docker Daemon 等
- System Reserved：预留给系统资源，如 kernel，sshd，udev 等
- Eviction Thresholds：驱逐（Eviction）的阈值，只支持 memory 和 storage。
- Allocatable(available for pods)：pods 可以使用的资源

官方文档示例：

这是一个用于说明节点分配计算方式的示例：

- 节点拥有 `32Gi 内存`，`16 核 CPU` 和 `100Gi 存储`
- `--kube-reserved` 设置为 `cpu=1,memory=2Gi,ephemeral-storage=1Gi`
- `--system-reserved` 设置为 `cpu=500m,memory=1Gi,ephemeral-storage=1Gi`
- `--eviction-hard` 设置为 `memory.available<500Mi,nodefs.available<10%`

在这个场景下，`Allocatable` 将会是 `14.5 CPUs`、`28.5Gi` 内存以及 `88Gi` 本地存储。 调度器保证这个节点上的所有 pod 请求的内存总量不超过 `28.5Gi`，存储不超过 `88Gi`。 当 pod 的内存使用总量超过 `28.5Gi` 或者磁盘使用总量超过 `88Gi` 时，Kubelet 将会驱逐它们。如果节点上的所有进程都尽可能多的使用 CPU，则 pod 加起来不能使用超过 `14.5 CPUs` 的资源。

当没有执行 `kube-reserved` 或 `system-reserved` 且系统守护进程使用量超过其预留时，如果`节点内存`用量高于 `31.5Gi` 或`存储`大于 `90Gi`，kubelet 将会驱逐 pod。

`小结`：为了简化管理，建议不对 kube-reserved/system-reserved 做区分，直接使用 `--system-reserved`做系统预留。在 kubelet 配置文件中设置如下参数：

`--system-reserved=memory=4Gi`

效果如下：

```bash
$ kubectl describe nodes node1

Name:           node1
......
Capacity:
 memory:                65759080Ki
Allocatable:
 memory:                61564776Ki
```

## 其它

Kubelet 还支持使用 cgroup 从物理上限制预留资源，这需要给 K8S 管理进程和系统进程分别设置 cgroup，复杂度相对较高，并且不好维护，个人不推荐这种方法。

## 参考链接

- https://kubernetes.io/zh/docs/tasks/administer-cluster/out-of-resource/#
- https://kubernetes.io/zh/docs/tasks/administer-cluster/reserve-compute-resources/
- http://wsfdl.com/kubernetes/2017/12/18/k8s%E8%B5%84%E6%BA%90%E9%A2%84%E7%95%99.html