## Kubernetes v1.16 发布

Kubernetes v1.16 于 2019 年 9 月发布，大家需要最关注的是`部分API将弃用`。

## v1.16.0 对以下四种类型资源的 API 做出调整
- NetworkPolicy

- PodSecurityPolicies
- Ingress
- DaemonSet, Deployment, StatefulSet 和 ReplicaSet

## API 具体调整细节如下
- `DaemonSet, Deployment, StatefulSet 和 ReplicaSet` 从 `extensions/v1beta1` 改用 `apps/v1`；`apps/v1` 从 v1.9 版本开始提供API。

- `NetworkPolicies` 从 `extensions/v1beta1` 改用 `networking.k8s.io/v1`；`networking.k8s.io/v1` 从 v1.8 版本开始提供API。
- `PodSecurityPolicies` 从 `extensions/v1beta1` 改用 `policy/v1beta1`；`policy/v1beta1` 从  v1.10 版本开始提供API。
- `Ingress` 从 `extensions/v1beta1` 改用 `networking.k8s.io/v1beta1`；`networking.k8s.io/v1beta1` 从v1.14开始可以提供API。

`默认情况`不在提供上面API，如果实在要临时启用，可使用 `--runtime-config` apiserver 标志临时启用这些API

- `apps/v1beta1=true`

- `apps/v1beta2=true`
- `extensions/v1beta1/daemonsets=true,extensions/v1beta1/deployments=true,extensions/v1beta1/replicasets=true,extensions/v1beta1/networkpolicies=true,extensions/v1beta1/podsecuritypolicies=true`

`注意`：上面提供的 API 将在 `v1.18` 完全删除。

## 下面列举部分 API 弃用预告
- `extensions/v1beta1` 从 v1.20 开始将不再提供 Ingress 资源。`networking.k8s.io/v1beta1` 从 v1.14 开始提供API。可以通过 `networking.k8s.io/v1beta1` API 检索现有的持久数据。

- `scheduling.k8s.io/v1beta1` 和 `scheduling.k8s.io/v1alpha1` 从 v1.17 起不再提供 `PriorityClass` 资源。改用 `scheduling.k8s.io/v1` API，自 v1.14 起可用。可以通过 `scheduling.k8s.io/v1` API 检索现有的持久数据。
- `export` 自 v1.14 起已弃用，将在 v1.18 删除。
- 不推荐使用的节点条件类型 `OutOfDisk` 已被删除。使用 `DiskPressure` 条件代替。
- `GA PodPriority` 功能现在默认情况下处于打开状态，无法禁用。功能将在 v1.18 中删除。
- `alpha.service-controller.kubernetes.io/exclude-balancer` 不推荐使用云负载平衡器中排除节点的节点标签（使用Service Type = LoadBalancer），而推荐使用 `node.kubernetes.io/exclude-balancer`。`alpha.service-controller.kubernetes.io/exclude-balancer` 将在 v1.18 删除。
- `admissionregistration.k8s.io/v1beta1` 版本 `MutatingWebhookConfiguration` `和ValidatingWebhookConfiguration` 已过时，将在 v1.19 移除。使用 `admissionregistration.k8s.io/v1` 替代。

## 升级到 v1.16.0 之前需要做什么？
- 更改 YAML 文件以引用新的 API

- 更新自定义集成和控制器来调用新的 API
- 更新第三方工具（ingress controllers、持续交付系统）来调用新的 API

## 测试

可以通过配置 `--runtime-config` apiserver 来测试集群，以模拟即将进行的删除。在 apiserver 启动参数中添加以下标志：

```bash
--runtime-config=apps/v1beta1=false,apps/v1beta2=false,extensions/v1beta1/daemonsets=false,extensions/v1beta1/deployments=false,extensions/v1beta1/replicasets=false,extensions/v1beta1/networkpolicies=false,extensions/v1beta1/podsecuritypolicies=false
```

## 更多

关于升级到 v1.16.0 更多详情请见 `https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG-1.16.md`

## 参考链接
- https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG-1.16.md
- https://zhuanlan.zhihu.com/p/74626407
- https://moelove.info/2019/07/22/K8S-%E7%94%9F%E6%80%81%E5%91%A8%E6%8A%A5-2019-07-15~2019-07-21/