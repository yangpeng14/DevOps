## Kubernetes 简介

微服务框架的流行，使得服务越来越精细化，服务也变的越来越多，对于发布和管理而言产生了巨大的挑战，而 `Docker` 的诞生，给与微服务的资源治理和控制提供了很好的基础。容器化可以解决各个不同语言环境部署、移植性高、跨平台部署等。但是 `Docker` 对于容器服务的编排没有那么方便，因为 `Docker` 这方面不足，而诞生 `Kubernetes`，`Kubernetes` 是一个可移植的、可扩展的开源平台，用于管理容器化的工作负载和服务，可促进声明式配置和自动化。

## 使用 Kubernetes 带来那些方便

- 快速部署应用
- 很容易实现 水平伸缩 或 垂直伸缩
- 无缝发布新的应用版本
- 资源使用最大化
- 应用停止自动重启

## Kubernetes 特点

- 可移植：支持公有云、私有云、混合云、多重云（multi-cloud）
- 可扩展：模块化、插件化、可挂载、可组合
- 自动化：自动部署、自动重启、自动复制、自动伸缩/扩展

## 为什么需要 Kubernetes，它能做什么?

容器是打包和运行应用程序的好方式。在生产环境中，您需要管理运行应用程序的容器，并确保不会停机。例如，如果一个容器发生故障，则需要启动另一个容器。如果系统处理此行为，会不会更容易？

这就是 Kubernetes 的救援方法！Kubernetes 为您提供了一个可弹性运行分布式系统的框架。Kubernetes 会满足您的扩展要求、故障转移、部署模式等。

Kubernetes 为您提供：

- `服务发现和负载均衡`：Kubernetes 可以使用 DNS 名称或自己的 IP 地址公开容器，如果到容器的流量很大，Kubernetes 可以负载均衡并分配网络流量，从而使部署稳定。

- `存储编排`：Kubernetes 允许您自动挂载您选择的存储系统，例如本地存储、公共云提供商等。

- `自动部署和回滚`：您可以使用 Kubernetes 描述已部署容器的所需状态，它可以以受控的速率将实际状态更改为所需状态。例如，您可以自动化 Kubernetes 来为您的部署创建新容器，删除现有容器并将它们的所有资源用于新容器。

- `容器资源配额`：Kubernetes 允许您指定每个容器所需 CPU 和内存（RAM）。当容器指定了资源请求时，Kubernetes 可以做出更好的决策来管理容器的资源。

- `自我修复`：Kubernetes 重新启动失败的容器、替换容器、杀死不响应用户定义的运行状况检查的容器，并且在准备好服务之前不将其通告给客户端。

- `密钥与配置管理`：Kubernetes 允许您存储和管理敏感信息，例如密码、OAuth 令牌和 ssh 密钥。您可以在不重建容器镜像的情况下部署和更新密钥和应用程序配置，也无需在堆栈配置中暴露密钥。

- `配置文件`：Kubernetes 可以通过 ConfigMap 来存储配置。


## Kubernetes 基础资源定义和理解

一切皆为资源，一切即可描述，一切皆可管理。

### NameSpaces

命名空间，在一个 Kubernetes 集群中可以使用namespace创建多个“虚拟集群”，这些namespace之间可以完全隔离，也可以通过某种方式，让一个namespace中的service可以访问到其他的namespace中的服务。

### Deployment

Deployment 为 Pod 和 ReplicaSet 提供了一个声明式定义(declarative)方法，用来替代以前的 `ReplicationController` 来方便的管理应用。典型的应用场景包括：

- 定义Deployment来创建Pod和ReplicaSet
- 滚动升级和回滚应用
- 扩容和缩容
- 暂停和继续Deployment

### Service

Kubernetes Service 定义了这样一种抽象：一个 Pod 的逻辑分组，一种可以访问它们的策略 —— 通常称为`微服务`。 这一组 Pod 能够被 Service 访问到，通常是通过 Label Selector实现的。

### Ingress

Ingress 是从 Kubernetes集群外部访问集群内部服务的入口。比如官方维护的 `Ingress Nginx`。`ingress traefik`、`ingress haproxy`等。

### Pod

Pod 是 kubernetes 中你可以创建和部署的最小也是最简的单位。Pod代表着集群中运行的进程。

Pod中封装着应用的容器（有的情况下是好几个容器），存储、独立的网络IP，管理容器如何运行的策略选项。Pod代表着部署的一个单位：kubernetes中应用的一个实例，可能由一个或者多个容器组合在一起共享资源。

### ConfigMap

ConfigMap API 资源用来保存 key-value pair配置数据，这个数据可以在pods里使用，或者被用来为像controller一样的系统组件存储配置数据。虽然 ConfigMap 跟 Secrets 类似，但是ConfigMap更方便的处理不含敏感信息的字符串。 注意：ConfigMaps不是属性配置文件的替代品。ConfigMaps只是作为多个properties文件的引用。你可以把它理解为Linux系统中的/etc目录，专门用来存储配置文件的目录。

### Secret

Secret 解决了密码、token、密钥等敏感数据的配置问题，而不需要把这些敏感数据暴露到镜像或者Pod Spec中。Secret 可以以Volume或者环境变量的方式使用。

Secret有三种类型：

- `Service Account` ：用来访问Kubernetes API，由Kubernetes自动创建，并且会自动挂载到Pod的/run/secrets/kubernetes.io/serviceaccount目录中；
- `Opaque` ：base64编码格式的Secret，用来存储密码、密钥等；
- `kubernetes.io/dockerconfigjson` ：用来存储私有docker registry的认证信息。

### PV 和 PVC

用于数据持续存储，Pod中，容器销毁，所有数据都会被销毁，如果需要保留数据，这里就需要用到 PV存储卷，PVC存储卷申明。

PVC 常用于 Deployment 做数据持久存储。实现持久化存储还需要理解 Volume 概念。

### Volume

容器磁盘上的文件的生命周期是短暂的，这就使得在容器中运行重要应用时会出现一些问题。首先，当容器崩溃时，kubelet 会重启它，但是容器中的文件将丢失——容器以干净的状态（镜像最初的状态）重新启动。其次，在 Pod 中同时运行多个容器时，这些容器之间通常需要共享文件。Kubernetes 中的 Volume 抽象就很好的解决了这些问题。

### Labels 和 Selectors

`标签` 和 `选择器`。作用用于给每个容器打标签，然后各个控制器通过 Selector 匹配容器，并管理。比如 Deployment 或 Service 都是通过这种方式匹配相应的 Pod。

## 自述

以上只是介绍 Kubernetes 几种常用的资源概念和作用，具体介绍可以查阅[Kubernetes 官方文档](https://kubernetes.io/docs/home/)。

## 参考链接

- https://kubernetes.io/docs/home/
- https://jimmysong.io/kubernetes-handbook
- https://www.jianshu.com/p/b5b9041e8d7b