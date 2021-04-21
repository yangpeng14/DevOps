## 什么是 cluster-autoscaler

`Cluster Autoscaler` （CA）是一个独立程序，是用来弹性伸缩kubernetes集群的。在使用kubernetes集群经常问到的一个问题是，应该保持多大的节点规模来满足应用需求呢？ cluster-autoscaler 出现解决了这个问题，它可以自动根据部署应用所请求资源量来动态的伸缩集群。

> 项目地址：https://github.com/kubernetes/autoscaler

## Cluster Autoscaler 什么时候伸缩集群？

在以下情况下，集群自动扩容或者缩放：

- `扩容`：由于资源不足，某些Pod无法在任何当前节点上进行调度
- `缩容`: Node节点资源利用率较低时，且此node节点上存在的pod都能被重新调度到其他node节点上运行

## 什么时候集群节点不会被 CA 删除？

- 节点上有pod被 `PodDisruptionBudget` 控制器限制。
- 节点上有命名空间是 `kube-system` 的pods。
- 节点上的pod不是被控制器创建，例如不是被deployment, replica set, job, stateful set创建。
- 节点上有pod使用了本地存储
- 节点上pod驱逐后无处可去，即没有其他node能调度这个pod
- 节点有注解：`"cluster-autoscaler.kubernetes.io/scale-down-disabled": "true"` （在CA 1.0.3或更高版本中受支持）

## Horizo​​ntal Pod Autoscaler 如何与 Cluster Autoscaler 一起使用？

Horizo​​ntal Pod Autoscaler 会根据当前CPU负载更改部署或副本集的副本数。如果负载增加，则HPA将创建新的副本，集群中可能有足够的空间，也可能没有足够的空间。如果没有足够的资源，CA将尝试启动一些节点，以便HPA创建的Pod可以运行。如果负载减少，则HPA将停止某些副本。结果，某些节点可能变得利用率过低或完全为空，然后CA将终止这些不需要的节点。

## 如何防止节点被CA删除?

从`CA 1.0`开始，节点可以打上以下标签：

```bash
"cluster-autoscaler.kubernetes.io/scale-down-disabled": "true"
```

可以使用 `kubectl` 将其添加到节点（或从节点删除）：

```bash
$ kubectl annotate node <nodename> cluster-autoscaler.kubernetes.io/scale-down-disabled=true
```

## 运行Cluster Autoscaler 最佳实践？

- 不要直接修改属于自动伸缩节点组的节点。同一节点组中的所有节点应该具有相同的容量、标签和在其上运行的系统pod
- Pod 声明 requests 资源限制
- 使用 `PodDisruptionBudgets` 可以防止突然删除Pod（如果需要）
- 再为节点池指定最小/最大设置之前，请检查您的云提供商的配额是否足够大
- 不要运行任何其他节点组自动缩放器（尤其是来自您的云提供商的自动缩放器）

## Cluster Autoscaler 支持那些云厂商?

- `GCE` https://kubernetes.io/docs/concepts/cluster-administration/cluster-management/
- `GKE` https://cloud.google.com/container-engine/docs/cluster-autoscaler
- `AWS` https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/README.md
- `Azure` https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/azure/README.md
- `Alibaba Cloud` https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/alicloud/README.md
- `OpenStack Magnum` https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/magnum/README.md
- `DigitalOcean` https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/digitalocean/README.md
- `CloudStack` https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/cloudstack/README.md
- `Exoscale` https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/exoscale/README.md
- `Packet` https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/packet/README.md
- `OVHcloud` https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/ovhcloud/README.md
- `Linode` https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/linode/README.md
- `Hetzner` https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/hetzner/README.md
- `Cluster API` https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/clusterapi/README.md

## Cluster Autoscaler 部署 和 更多实践

请参考链接：https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/FAQ.md

## 参考链接：

- https://github.com/kubernetes/autoscaler
- https://blog.csdn.net/hello2mao/article/details/80418625
