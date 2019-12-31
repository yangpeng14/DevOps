## Pod 概念
- Pod是kubernetes集群中最小的部署和管理的基本单元，协同寻址，协同调度。
- Pod是一个或多个容器的集合，是一个或一组服务（进程）的抽象集合。
- Pod中可以共享网络和存储（可以简单理解为一个逻辑上的虚拟机，但并不是虚拟机）。
- Pod被创建后用一个UID来唯一标识，当Pod生命周期结束，被一个等价Pod替代，UID将重新生成。

`Docker` 是 `Kubernetes Pod` 中最常用的容器运行时，但 `Pod` 也能支持其他的容器运行时，比如 rkt、podman等。

Kubernetes 集群中的 Pod 可被用于以下两个主要用途：

- `运行单个容器的 Pod`。“每个 Pod 一个容器”模型是最常见的 Kubernetes 用例；在这种情况下，可以将 Pod 看作单个容器的包装器，并且 Kubernetes 直接管理 Pod，而不是容器。
- `运行多个协同工作的容器的 Pod`。 Pod 可能封装由多个紧密耦合且需要共享资源的共处容器组成的应用程序。 这些位于同一位置的容器可能形成单个内聚的服务单元——一个容器将文件从共享卷提供给公众，而另一个单独的“挂斗”容器则刷新或更新这些文件。 Pod 将这些容器和存储资源打包为一个可管理的实体。

## Pod 控制器

控制器可以为您创建和管理多个 Pod，管理副本和上线，并在集群范围内提供自修复能力。 例如，如果一个节点失败，控制器可以在不同的节点上调度一样的替身来自动替换 Pod。

包含一个或多个 Pod 的控制器一些示例包括：

- Deployment  kubernetes中最常用的控制器，用于运行无状态应用
- StatefulSet  用于运行有状态应用
- DaemonSet  作用就像是计算机中的守护进程，它能够运行集群存储、日志收集和监控等『守护进程』

控制器通常使用您提供的 Pod 模板来创建它所负责的 Pod。

## Pod 故障归类

- Pod状态 一直处于 Pending
- Pod状态 一直处于 Waiting
- Pod状态 一直处于 ContainerCreating
- Pod状态 一直处于 ImagePullBackOff
- Pod状态 一直处于 CrashLoopBackOff
- Pod状态 一直处于 Error
- Pod状态 一直处于 Terminating
- Pod状态 一直处于 Unknown

上面是个人总结，如果不全请见谅！

## Pod 排查故障命令

- `kubectl get pod <pod-name> -o yaml` # 查看 Pod 配置是否正确
- `kubectl describe pod <pod-name>`  # 查看 Pod 详细事件信息
- `kubectl logs <pod-name> [-c <container-name>]` # 查看容器日志

## Pod 故障问题与解决方法

- Pod 一直处于 Pending 状态

Pending状态，这个状态意味着，Pod 的 YAML 文件已经提交给 Kubernetes，API 对象已经被创建并保存在 Etcd 当中。但是，这个 Pod 里有些容器因为某种原因而不能被顺利创建。比如，调度不成功（可以通过 kubectl describe pod 命令查看到当前 Pod 的事件，进而判断为什么没有调度）。可能原因： 资源不足，集群内所有的 Node 都不满足该 Pod 请求的 CPU、内存、GPU 等资源
HostPort 已被占用，通常推荐使用 Service 对外开放服务端口


## 参考链接
- https://kubernetes.io/zh/docs/concepts/workloads/pods/
- https://www.huweihuang.com/kubernetes-notes/concepts/pod/pod.html
- https://blog.csdn.net/fanren224/article/details/86318921