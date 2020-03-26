## 发布徽标

![](/img/k8s-v1.18.png)


## Kubernetes v1.18 新增功能

### Kubernetes拓扑管理器（Topology Manager ） 升级到Beta版 ！

[拓扑管理器功能](https://github.com/nolancon/website/blob/f4200307260ea3234540ef13ed80de325e1a7267/content/en/docs/tasks/administer-cluster/topology-manager.md)是 1.18 版中 Kubernetes 的 `beta` 功能，它使 `CPU` 和 `设备`（例如SR-IOV VF）的 `NUMA` 对齐方式能够使您的工作负载在针对低延迟而优化的环境中运行。在引入拓扑管理器之前，CPU和设备管理器将做出彼此独立的资源分配决策。这可能会导致在多套接字（ multi-socket ）系统上分配不良，从而导致关键型应用程序的性能下降。

### Serverside Apply引入Beta 2版本

Serverside Apply 在 1.16 中升级为 Beta，但现在在 1.18 中引入了第二个 Beta。这个新版本将跟踪和管理所有新Kubernetes 对象的字段更改，从而使你知道更改了什么资源以及何时更改的。

### 使用 IngressClass 扩展 Ingress 并用 IngressClass 替换不推荐使用的注释

在 Kubernetes 1.18 中，Ingress 有两个重要的补充：一个新 `pathType` 字段和一个新 `IngressClass` `资源。该pathType` 字段允许指定路径应如何匹配。除了默认 `ImplementationSpecific` 类型外，还有 `new Exact` 和 `Prefixpath` 类型。

该 `IngressClass` 资源用于描述 Kubernetes 集群中的 Ingress 类型。入口可以通过 `ingressClassName` 在入口上使用新字段来指定与它们关联的类。此新资源和字段替换了不建议使用的 `kubernetes.io/ingress.class` 注释。

### SIG-CLI 引入 kubectl debug 命令

SIG CLI 已经讨论了调试实用程序的需求已经有一段时间。随着[临时容器](https://kubernetes.io/docs/concepts/workloads/pods/ephemeral-containers/)的发展，我们可以通过在 kubectl exec 。该 kubectl debug [命令的添加](https://github.com/kubernetes/enhancements/blob/master/keps/sig-cli/20190805-kubectl-debug.md)（它是Alpha，但欢迎您提供反馈），使开发人员可以轻松地在集群中调试其 Pod。我们认为这种增加是无价的。此命令允许创建一个临时容器，该容器在要检查的Pod旁边运行，并且还附加到控制台以进行交互式故障排除。

### 为 Kubernetes 引入 Windows CSI 支持 Alpha版本

随着 Kubernetes 1.18 的发布，用于 Windows 的 CSI代理 的Alpha版本也已发布。CSI代理使非特权（预先批准）的容器能够在Windows 上执行特权存储操作。现在，可以利用CSI代理在Windows中支持CSI驱动程序。SIG存储在1.18版本中取得了很大进步。

## API 相关弃用

- 所有资源的 API `apps/v1beta1` 和 `apps/v1beta2` 都将弃用，请改用 `apps/v1` 替代。
- `daemonsets`, `deployments`, `replicasets` 资源的 API `extensions/v1beta1` 将被弃用，请改用 apps/v1 替代。
- `networkpolicies` 资源的 API `extensions/v1beta1` 将被弃用，请改用 networking.k8s.io/v1 替代。
- `podsecuritypolicies` 资源的 API `extensions/v1beta1` 将被弃用，请使用 `policy/v1beta1` 替代。

## 总结

上面内容是作者感觉需要关注或者注意的部分，其它功能请参考官方 https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.18.md

## 参考链接

- https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.18.md