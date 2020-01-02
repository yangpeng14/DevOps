## Pod 概念
- Pod是kubernetes集群中最小的部署和管理的基本单元，协同寻址，协同调度。
- Pod是一个或多个容器的集合，是一个或一组服务（进程）的抽象集合。
- Pod中可以共享网络和存储（可以简单理解为一个逻辑上的虚拟机，但并不是虚拟机）。
- Pod被创建后用一个UID来唯一标识，当Pod生命周期结束，被一个等价Pod替代，UID将重新生成。

`Docker` 是 `Kubernetes Pod` 中最常用的容器运行时，但 `Pod` 也能支持其他的容器运行，比如 rkt、podman等。

Kubernetes 集群中的 Pod 可被用于以下两个主要用途：

- `运行单个容器的 Pod`。“每个 Pod 一个容器”模型是最常见的 Kubernetes 用例；在这种情况下，可以将 Pod 看作单个容器的包装器，并且 Kubernetes 直接管理 Pod，而不是容器。
- `运行多个协同工作的容器的 Pod`。 Pod 可能封装由多个紧密耦合且需要共享资源的共处容器组成的应用程序。 这些位于同一位置的容器可能形成单个内聚的服务单元，一个容器将文件从共享卷提供给公众，而另一个单独的“挂斗”容器则刷新或更新这些文件。 Pod 将这些容器和存储资源打包为一个可管理的实体。

## Pod 控制器

控制器可以为您创建和管理多个 Pod，管理副本和上线，并在集群范围内提供自修复能力。 例如，如果一个节点失败，控制器可以在不同的节点上调度一样的替身来自动替换 Pod。

包含一个或多个 Pod 的控制器一些示例包括：

- `Deployment` kubernetes中最常用的控制器，用于运行无状态应用
- `StatefulSet` 用于运行有状态应用
- `DaemonSet` 作用就像是计算机中的守护进程，它能够运行集群存储、日志收集和监控等『守护进程』

控制器通常使用您提供的 Pod 模板来创建它所负责的 Pod。

## Pod 故障归类

- Pod状态 一直处于 Pending
- Pod状态 一直处于 Waiting
- Pod状态 一直处于 ContainerCreating
- Pod状态 处于 ImagePullBackOff
- Pod状态 处于 CrashLoopBackOff
- Pod状态 处于 Error
- Pod状态 一直处于 Terminating
- Pod状态 处于 Unknown

上面是个人总结，如果不全请见谅！

## Pod 排查故障命令

- `kubectl get pod <pod-name> -o yaml` # 查看 Pod 配置是否正确
- `kubectl describe pod <pod-name>`  # 查看 Pod 详细事件信息
- `kubectl logs <pod-name> [-c <container-name>]` # 查看容器日志

## Pod 故障问题与排查方法

- Pod 一直处于 `Pending` 状态

    Pending状态，这个状态意味着，Pod 的 YAML 文件已经提交给 Kubernetes，API 对象已经被创建并保存在 Etcd 当中。但是，这个 Pod 里有些容器因为某种原因而不能被顺利创建。比如，调度不成功（可以通过 `kubectl describe pod` 命令查看到当前 Pod 的事件，进而判断为什么没有调度）。可能原因： 资源不足（集群内所有的 Node 都不满足该 Pod 请求的 CPU、内存、GPU 等资源）；HostPort 已被占用（通常推荐使用 Service 对外开放服务端口）。

- Pod 一直处于 `Waiting` 或 `ContainerCreating` 状态

    首先还是通过 `kubectl describe pod` 命令查看到当前 `Pod` 的事件。可能的原因包括：

    1、`镜像拉取失败`，比如，镜像地址配置错误、拉取不了国外镜像源（gcr.io）、私有镜像密钥配置错误、镜像太大导致拉取超时（可以适当调整 kubelet 的 --image-pull-progress-deadline 和 --runtime-request-timeout 选项）等。

    2、CNI 网络错误，一般需要检查 CNI 网络插件的配置，比如：无法配置 Pod 网络、无法分配 IP 地址。

    3、容器无法启动，需要检查是否打包了正确的镜像或者是否配置了正确的容器参数。

    4、Failed create pod sandbox，查看kubelet日志，原因可能是磁盘坏道（input/output error）。

- Pod 一直处于 `ImagePullBackOff` 状态

    通常是`镜像名称配置错误`或者`私有镜像的密钥配置错误导致`。这种情况可以使用 `docker pull` 来验证镜像是否可以正常拉取。

    如果私有镜像密钥配置错误或者没有配置，按下面检查：

    1、查询 docker-registry 类型的 Secret
    ```bash
    # 查看 docker-registry Secret 
    $ kubectl  get secrets my-secret -o yaml | grep 'dockerconfigjson:' | awk '{print $NF}' | base64 -d
    ```
    
    2、创建 docker-registry 类型的 Secret
    ```bash
    # 首先创建一个 docker-registry 类型的 Secret
    $ kubectl create secret docker-registry my-secret --docker-server=DOCKER_REGISTRY_SERVER --docker-username=DOCKER_USER --docker-password=DOCKER_PASSWORD --docker-email=DOCKER_EMAIL

    # 然后在 Deployment 中引用这个 Secret
    spec:
      containers:
      - name: private-reg-container
        image: <your-private-image>
      imagePullSecrets:
      - name: my-secret
    ```

- Pod 一直处于 `CrashLoopBackOff` 状态

    `CrashLoopBackOff` 状态说明容器曾经启动了，但又异常退出。此时可以先查看一下容器的日志。

    通过命令 `kubectl logs` 和 `kubectl logs --previous` 可以发现一些容器退出的原因，比如：容器进程退出、健康检查失败退出、此时如果还未发现线索，还可以到容器内执行命令来进一步查看退出原因（kubectl exec cassandra – cat /var/log/cassandra/system.log），如果还是没有线索，那就需要 SSH 登录该 Pod 所在的 Node 上，查看 `Kubelet` 或者 `Docker` 的日志进一步排查。

- Pod 处于 `Error` 状态

    通常处于 Error 状态说明 Pod 启动过程中发生了错误。常见的原因包括：依赖的 `ConfigMap`、`Secret` 或者 `PV` 等不存在；请求的资源超过了管理员设置的限制，比如超过了 `LimitRange` 等；违反集群的安全策略，比如违反了 `PodSecurityPolicy` 等；容器无权操作集群内的资源，比如开启 `RBAC` 后，需要为 `ServiceAccount` 配置角色绑定;

- Pod 处于 Terminating 或 Unknown 状态

    从 v1.5 开始，Kubernetes 不会因为 Node 失联而删除其上正在运行的 Pod，而是将其标记为 `Terminating` 或 `Unknown` 状态。想要删除这些状态的 Pod 有三种方法：

    1、从集群中删除该 Node。使用公有云时，kube-controller-manager 会在 VM 删除后自动删除对应的 Node。而在物理机部署的集群中，需要管理员手动删除 Node（如 kubectl delete node ）。

    2、Node 恢复正常。Kubelet 会重新跟 kube-apiserver 通信确认这些 Pod 的期待状态，进而再决定删除或者继续运行这些 Pod。用户强制删除。用户可以执行 `kubectl delete pods pod-name --grace-period=0 --force` 强制删除 Pod。除非明确知道 Pod 的确处于停止状态（比如 Node 所在 VM 或物理机已经关机），否则不建议使用该方法。特别是 `StatefulSet` 管理的 Pod，强制删除容易导致脑裂或者数据丢失等问题。

    3、Pod 行为异常，这里所说的行为异常是指 Pod 没有按预期的行为执行，比如没有运行 `podSpec` 里面设置的命令行参数。这一般是 podSpec yaml 文件内容有误，可以尝试使用 `--validate` 参数重建容器，比如:

    `kubectl delete pod mypod` 和 `kubectl create --validate -f mypod.yaml`，也可以查看创建后的 podSpec 是否是对的，比如：`kubectl get pod mypod -o yaml`，修改静态 Pod 的 `Manifest` 后未自动重建，Kubelet 使用 inotify 机制检测 /etc/kubernetes/manifests 目录（可通过 Kubelet 的 --pod-manifest-path 选项指定）中静态 Pod 的变化，并在文件发生变化后重新创建相应的 Pod。但有时也会发生修改静态 Pod 的 Manifest 后未自动创建新 Pod 的情景，此时一个简单的修复方法是重启 Kubelet。

    `Unknown` 这是一个异常状态，意味着 Pod 的状态不能持续地被 kubelet 汇报给 kube-apiserver，这很有可能是主从节点（Master 和 Kubelet）间的通信出现了问题。


## 参考链接
- https://kubernetes.io/zh/docs/concepts/workloads/pods/
- https://kubernetes.io/docs/tasks/debug-application-cluster/debug-application/
- https://www.huweihuang.com/kubernetes-notes/concepts/pod/pod.html
- https://blog.csdn.net/fanren224/article/details/86318921
- https://zhuanlan.zhihu.com/p/34332367
