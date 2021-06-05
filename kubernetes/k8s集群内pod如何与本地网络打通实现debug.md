## 前言

大家都知道，在没有K8S集群时，我们能直接连接测试环境服务实现debug。随着K8S到来，我们无法直接连接业务服务dubug，K8S Pod 分配的IP地址是集群内部网络，集群外部网络是无法直接访问到Pod，那有什么好的解决方法能直接连接Pod？下面介绍下开源 `Telepresence`。

## Telepresence 简介

Telepresence 是一种开源工具，可让您在本地运行单个服务，同时将该服务连接到远程 Kubernetes 集群。这使开发 multi-service 应用程序的开发人员能够：

- 对单个服务进行快速本地开发，即使该服务依赖于集群中的其他服务。对您的服务进行更改并保存，您可以立即看到正在运行的新服务。
- 使用本地安装的任何工具来 测试/调试/编辑 您的服务。例如，您可以使用调试器或 IDE！
- 让您的本地开发机器像 Kubernetes 集群的一部分一样运行。如果您的机器上有一个应用程序要针对集群中的服务运行——这很容易做到。

> 开源地址: https://github.com/telepresenceio/telepresence

## Telepresence 如何运行

Telepresence 在 Kubernetes 集群中运行的 pod 中部署双向网络代理。此 pod 将数据从您的 Kubernetes 环境（例如 TCP 连接、环境变量、卷）代理到本地进程。本地进程的网络被透明覆盖，以便 DNS 调用和 TCP 连接通过代理路由到远程 Kubernetes 集群。

这种方法给出：

- 您的本地服务可以完全访问远程集群中的其他服务
- 您的本地服务对 Kubernetes `environment`、`secrets`和 `ConfigMap` 的完全访问权限
- 您的远程服务可以完全访问您的本地服务

## Telepresence 支持的运行平台

- Mac OS X
- Linux

## Telepresence 安装

可使用 Homebrew、apt 或 dnf 安装

## Telepresence 使用报告

Telepresence 收集有关其用户的一些基本信息，以便它可以发送重要的客户通知，例如新版本可用性和安全公告。我们还使用这些信息匿名汇总基本使用情况分析。要禁用此行为，请设置环境变量 `SCOUT_DISABLE`：

```bash
export SCOUT_DISABLE=1
```

## Telepresence 使用方法

这里不在描述，具体参考 https://www.telepresence.io/tutorials/kubernetes

## 参考链接

- https://github.com/telepresenceio/telepresence
- https://www.telepresence.io/discussion/overview