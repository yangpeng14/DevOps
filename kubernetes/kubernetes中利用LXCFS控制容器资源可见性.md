## 背景

Linux 利用 `Cgroup` 实现了对容器的资源限制，但在容器内部依然缺省挂载了宿主机上的 `procfs` 的 `/proc` 目录，其包含如：`meminfo`、`cpuinfo`、`stat`、`uptime` 等资源信息。一些监控工具如 `free`、`top` 或 `业务应用`还依赖上述文件内容获取资源配置和使用情况。当它们在容器中运行时，就会把宿主机的资源状态读取出来，导致资源设置不对。

上面提到的问题，可以通过 `LXCFS` 方法来解决。

## LXCFS 简介

社区中常见的做法是利用 `lxcfs` 来提供容器中的资源可见性。`lxcfs` 是一个开源的FUSE（用户态文件系统）实现来支持LXC容器，它也可以支持Docker容器。

LXCFS通过用户态文件系统，在容器中提供下列 `procfs` 的文件。

```
/proc/cpuinfo
/proc/diskstats
/proc/meminfo
/proc/stat
/proc/swaps
/proc/uptime
```

LXCFS的示意图如下：

![](/img/lxcfs-1.png)

比如，把宿主机的 `/var/lib/lxcfs/proc/memoinfo` 文件挂载到 Docker 容器的 `/proc/meminfo` 位置后。容器中进程读取相应文件内容时，`LXCFS` 的 `FUSE` 实现会从容器对应的 `Cgroup` 中读取正确的内存限制。从而使得应用获得正确的资源约束设定。

## LXCFS 在 Kubernetes 中实践

### 注意

在网上搜索到很多文章使用 `https://github.com/denverdino/lxcfs-initializer` 项目，但是在 Kubernetes 1.14+ 版本中就不支持 `initializers` 方法。并且这个项目已归档，不在维护，所以不推荐使用这个项目。

社区推出另一个项目 `https://github.com/denverdino/lxcfs-admission-webhook` 通过 `Admission Webhook` 给 Pod 注入 LXCFS 设置。

### 依赖

集群内所有 `CentOS` 节点需要安装 `fuse-libs` 包，否则会报 `/usr/local/bin/lxcfs: error while loading shared libraries: libfuse.so.2: cannot open shared object file: No such file or directory` 错误。

```bash
$ yum install -y fuse-libs
```

### 前提条件

> 演示环境是 Kubernetes version 1.18.2 二进制部署

1、Kubernetes api-versions 需要启用 `admissionregistration.k8s.io/v1beta1`。（Kubernetes 1.9.0+ 版本默认都启用）

```bash
# 查看是否开启
$ kubectl api-versions | grep 'admissionregistration.k8s.io/v1beta1'

admissionregistration.k8s.io/v1beta1
```

2、`kube-apiserver` 配置中，需要配置 `MutatingAdmissionWebhook` 和 `ValidatingAdmissionWebhook`。并且添加顺序要正确。

```bash
$ grep MutatingAdmissionWebhook /opt/kubernetes/cfg/kube-apiserver

--enable-admission-plugins=NamespaceLifecycle,LimitRanger,ServiceAccount,DefaultStorageClass,DefaultTolerationSeconds,MutatingAdmissionWebhook,ValidatingAdmissionWebhook,ResourceQuota,NodeRestriction \
```

### 部署 LXCFS

下载 lxcfs-admission-webhook 项目

```bash
$ gti clone https://github.com/denverdino/lxcfs-admission-webhook.git
$ cd lxcfs-admission-webhook
```

修改 `deployment/lxcfs-daemonset.yaml` 配置文件，因为 `apps/v1beta2` 在 1.18.2 版本已经弃用

```bash
$ git diff 

diff --git a/deployment/lxcfs-daemonset.yaml b/deployment/lxcfs-daemonset.yaml
index 5f58120..ea67e8a 100644
--- a/deployment/lxcfs-daemonset.yaml
+++ b/deployment/lxcfs-daemonset.yaml
@@ -1,4 +1,4 @@
-apiVersion: apps/v1beta2
+apiVersion: apps/v1
```

部署 lxcfs

```bash
$ kubectl apply -f deployment/lxcfs-daemonset.yaml

# 查看 lxcfs 是否部署成功
$ kubectl  get pods -n default  | grep lxcfs

lxcfs-4crr4    1/1     Running   0  153m
lxcfs-jmzpk    1/1     Running   0  155m
```

部署 lxcfs-admission-webhook injector

```bash
# 执行 shell 部署脚本
$ deployment/install.sh

# 查看
$ kubectl get secrets,pods,svc,mutatingwebhookconfigurations
```

### 测试

启用需要注入的 lxcfs namespace，命名空间下所有 pod 都会被注入 lxcfs

```bash
$ kubectl label namespace default lxcfs-admission-webhook=enabled
```

部署一个 apache 服务来测试

```bash
# 部署 apache 
$ kubectl apply -f deployment/web.yaml

# 查看
$ kubectl  get pods | grep web-

web-596d5565b8-n79b8                                 1/1     Running   0          125m
web-596d5565b8-s49nv                                 1/1     Running   0          133m

# 查看内存限制是否生效，下面显示内存 256Mi 就是 limits 设置的值
$ kubectl  exec -it web-596d5565b8-n79b8 bash

root@web-596d5565b8-n79b8:/usr/local/apache2# free  -m

             total       used       free     shared    buffers     cached
Mem:           256          7        248          0          0          0
-/+ buffers/cache:          6        249
Swap:            0          0          0
```

### 清理

清理 lxcfs-admission-webhook 

```bash
$ deployment/uninstall.sh
```

清理 lxcfs

```bash
$ kubectl delete -f deployment/lxcfs-daemonset.yaml
```

## 总结

`lxcfs` 支持容器镜像 `Centos系统`、`Ubuntu系统`、`Debian系统`，但是不支持容器镜像 `Alpine系统`。

## 参考链接

- https://yq.aliyun.com/articles/566208