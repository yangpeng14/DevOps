## k8s v1.17.0 新增功能

- `Kubernetes Volume Snapshot`：功能现已在 Kubernetes v1.17 中处于 beta 版。它在 Kubernetes v1.12 中作为 Alpha 引入，第二个 Alpha 在 Kubernetes v1.13 中具有重大变化。

    `什么是 Volume Snapshot？`

    许多存储系统（如 Google Cloud Persistent Disks、Amazon Elastic Block Storage 和许多本地存储系统）都可以创建     Persistent Volume（持久卷）的“快照”。快照表示 Volume 的时间点副本，可用于设置新的 Volume（预填充快照数据）或将现有  Volume 还原到先前状态（由快照表示）。

    `为什么要将 Volume Snapshot 添加到 K8s？`

    Kubernetes Volume 插件系统提供强大的抽象功能，可以自动配置、附加和挂载块和文件存储。

    这些功能都基于 Kubernetes 的工作负载可移植性：Kubernetes 的目标是在分布式系统应用程序和底层集群之间创建一个抽象层，以   便应用程序可以不知道底层集群的具体情况，且在部署时不需要“特定于集群”的知识。

    Kubernetes Storage SIG 将快照操作确定为许多有状态工作负载的关键功能。例如，在进行数据库操作之前，数据库管理员可能需要   对数据库卷进行快照。通过提供一种在 Kubernetes API 中触发快照操作的标准方式，Kubernetes 用户现在可以轻松应对上述场景，  而不必使用 Kubernetes API 手动执行针对存储系统的特定操作。

    Kubernetes 用户现在被授权以与集群无关的方式，将快照操作合并到他们的工具和策略中，并且可以放心地知道它将针对任意的   Kubernetes 集群，而不需要在意底层存储是什么。

    此外，这些 Kubernetes 快照原语是基本的构建块，可用于为 Kubernetes 开发高级的企业级存储管理功能，如应用程序级或集群级    的备份解决方案。 了解更多 `https://kubernetes.io/blog/2019/12/09/   kubernetes-1-17-feature-cis-volume-snapshot-beta/`

- `云提供商标签达到一般可用性`：v1.17 作为 v1.2 中的 beta 功能添加，可以看到云提供商标签的一般可用性。

- `CSI 迁移测试版`：容器存储接口（CSI）迁移基础结构的 Kubernetes 存储插件现在是 Kubernetes v1.17 中 beta 版。CSI 迁移在 Kubernetes v1.14 中作为 Alpha 引入。

## 已知问题

- 容器具有特权时，`volumeDevices` 映射将被忽略

- 在 `Should recreate evicted statefulset` 一致性测试失败，因为 `Pod ss-0 expected to be re-created at least once`。这是由 `Predicate PodFitsHostPorts failed` 计划错误引起的。根本原因是 port 的主机端 21017 端口冲突。该端口正在由节点上运行的另一个应用程序用作临时端口。这将在 1.18 版本中进行探讨。

## 升级说明

- `集群生命周期`： Kubeadm：kubelet-finalize 作为 init 工作流程的一部分，添加一个新阶段，并添加一个实验性子阶段，以在主控制平面节点上启用自动 `kubelet客户端证书轮换`。在 1.17 之前以及对于 `kubeadm init` 希望轮换使用 kubelet客户端证书的情况下创建的现有节点，必须进行修改 /etc/kubernetes/kubelet.conf 以指向要旋转的PEM符号链接： client-certificate:/var/lib/kubelet/pki/kubelet-client-current.pem 和 client-key:/var/lib/kubelet/pki/kubelet-client-current.pem，以替换嵌入式客户端证书和密钥

- `EndpointSlices`：如果升级已启用 EndpointSlices 的群集，则应由 EndpointSlice 控制器管理的所有 EndpointSlices 的 `http://endpointslice.kubernetes.io/managed-by` 标签应设置为 `endpointslice-controller.k8s.io`。

- Kubeadm：添加额外的 apiserver 授权模式时，默认值 `Node,RBAC` 不再位于生成的静态 Pod 清单中，并且允许完全覆盖。（＃82616，@ghouscht）

- 存储：在升级 Kubernetes 集群之前，`所有 Node 上 Pod 都需要迁移走`，因为在此版本中`更改了用于 block volumes 的路径`，因此不允许在线升级节点。（＃74026，@mkimuram）

## 列出部分弃用 和 移除

- `kubeadm.k8s.io/v1beta1` 已被弃用，则应更新配置以使用较新的未弃用的 API版本。（＃83276，@克拉文）

- `弃用默认服务IP CIDR`。以前的默认设置 `10.0.0.0/24` 将在 6个月/2个发行版中删除。集群管理员必须通过`--service-cluster-ip-range` 在 `kube-apiserver` 上使用来指定自己想要的值。（＃81668，@darshanime）

- 删除不推荐使用的 `include-uninitialized` 标志。

- `rbac.authorization.k8s.io/v1alpha1` 和 `rbac.authorization.k8s.io/v1beta1` API组中的`所有资源均已弃用`，改用 `rbac.authorization.k8s.io/v1`，并不在 v1.20 提供。

- 从1.17版（＃84282，@tedyu）开始，删除了内置的 `system:csi-external-provisioner` 和`system:csi-external-attacher` 群集角色。

- kubeadm 不赞成使用 `hyperkube` 镜像


## 二进制包

- `crictl` 在发行中添加了 `Windows二进制文件` 和 `Linux 32位二进制文​​件`

## 主要变化

- `添加 IPv4/IPv6 双协议栈支持`：允许将 IPv4 和 IPv6 地址分配给 Pods 和服务。

## 其它显著变化

- `服务的拓扑感知路由（Alpha）`：让 Service 可以`实现就近原则转发`，而不是所有 Endpoint `等概率转发`；

- 将 `Windows RunAsUserName` 功能移动到 beta

## 更多详细信息见 GitHub 和 官方博客

- https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG-1.17.md

- https://kubernetes.io/blog/2019/12/09/kubernetes-1-17-release-announcement/