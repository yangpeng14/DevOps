## 升级原因

Kubernetes 容器节点漏洞 `(CVE-2020-8558)` 绕过本地主机边界通告。

具体参考链接：https://mp.weixin.qq.com/s/4w8kMJpHEV3E2uP6frToUw

## 要求

Kubernetes `二进制`从 `v1.15.3` 升级到目前最新版本 `v1.18.5`。

## 准备工作

准备升级 Kubernetes 前，作者查阅了官方 `v1.16`、`v1.17`、`v1.18` 每个大版本发布说明，最大变化是在 v1.16 弃用一些api。这是本次升级最大的困难，项目中有很多 `Deployment`、`Ingress`、`DaemonSet`和 `StatefulSet` 都使用 `extensions/v1beta1` 接口。

`v1.16` 具体`弃用api`说明，下面例举出来：

- `DaemonSet`, `Deployment`, `StatefulSet` 和 `ReplicaSet` 从 `extensions/v1beta1` 改用 `apps/v1`；`apps/v1` 从 `v1.9` 版本开始提供API。
- `NetworkPolicies` 从 `extensions/v1beta1` 改用 `networking.k8s.io/v1`；`networking.k8s.io/v1` 从 `v1.8` 版本开始提供API。
- `PodSecurityPolicies` 从 `extensions/v1beta1` 改用 `policy/v1beta1`；`policy/v1beta1` 从 `v1.10` 版本开始提供API。
- `Ingress` 从 `extensions/v1beta1` 改用 `networking.k8s.io/v1beta1`；`networking.k8s.io/v1beta1` 从v1.14 版本开始提供API。

> `注意`：上面提供的 API 将在 `v1.18` 完全删除。

Kubernetes 大版本发布说明：

- https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.16.md
- https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.17.md
- https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.18.md

## 调查官方是否提供工具快速替换弃用的 API

通过谷歌发现官方 `kubectl` 命令，提供一个 `convert` 参数，支持 `API versions` 配置转换。

但是在使用 `kubectl convert` 过程中，命令报出 `convert` 参数未来会弃用，当时就在想，官方是否提供了更好的工具，否则 `convert` 参数不会在未来会弃用。

后面通过谷歌发现，Kubernetes 升级到 `v1.18` 版本时，会自动把 Kubernetes 在运行的服务 `API versions` 版本替换为最新版本。

> `注意`：作者这里直接把 Kubernetes 从 `v1.15.3` 升级到 `v1.18.5`，`API versions` 会自动替换，但请注意，在更新 `kubelet` 组件时，`node节点`上所有使用容器都会`原地重启`一次，`Pod创建时间不会改变`。所以在升级过程中，最好流量低峰时操作。

## 升级前备份工作

- 备份 Etcd，请参考 [Etcd v3备份与恢复](https://www.yp14.cn/2019/08/29/Etcd-v3%E5%A4%87%E4%BB%BD%E4%B8%8E%E6%81%A2%E5%A4%8D/)
- 备份 Kubernetes 集群业务，请参考 [K8S备份、恢复、迁移神器 Velero](https://www.yp14.cn/2020/06/23/K8S%E5%A4%87%E4%BB%BD-%E6%81%A2%E5%A4%8D-%E8%BF%81%E7%A7%BB%E7%A5%9E%E5%99%A8-Velero/)

## 作者一点点经验

升级 Kubernetes 到最新版本 `v1.18.5`时，先需要把 Kubernetes 各个组件升级（Etcd、Calico或者flannel、Coredns、Metrics-Server）到`目前最新`或者`比较靠前`版本。

这里是作者环境当前版本和准备升级到的版本，供读者参考：

服务名称 | 当前版本 | 准备升级版本
---|---|---
Docker ce | v18.04.0 | v19.03.6 
Etcd | v3.3.9 | v3.4.7
Calico | v3.2.3 | v3.14.0
flannel | v0.10.0 | v0.12.0
Metrics Server | v0.3.4 | v0.3.7
Coredns | 1.5 | 1.7.0

## 小结

升级 Kubernetes 版本一定要在流量低峰操作。如果有条件的话，最好把集群环境上的服务迁移到另一个集群中，这样升级操作不会影响业务。如果没有这种环境或者公司考虑成本原因与时间原因，不可能单独搭建另一个集群，那线上环境升级一定要在流量低峰，并且一定要找一个测试环境预演，提前发现升级过程中遇到的问题。