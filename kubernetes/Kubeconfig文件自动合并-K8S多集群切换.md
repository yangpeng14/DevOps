## 前言

随着 Kubernetes 越来越流行，不管大公司还是小公司都往 Kubernetes 迁移，每个公司最少有两套集群（测试和生产），但是多个集群就有多个 `Kubeconfig` 用户授权文件。虽然官方文档中有介绍多个 `Kubeconfig` 文件合并成一个 `Kubeconfig`，但是对于一些新手来说，看得不是很明白。

本文介绍 `Kubeconfig` 文件结构，并推荐一个工具自动合并 `Kubeconfig`。

## Kubeconfig 用途

`kubectl` 命令行工具通过 `kubeconfig` 文件的配置来选择`集群`以及`集群API Server`通信的所有信息。`kubeconfig` 文件用来保存关于集群`用户`、`命名空间`和`身份验证机制`的信息。默认情况下 `kubectl` 读取 `$HOME/.kube/config` 文件，也可以通过设置环境变量 `KUBECONFIG` 或者 `--kubeconfig` 指定其他的配置文件。

## Kubeconfig 文件结构

`kubeconfig` 文件主要由下面几部分构成：

- 集群参数
- 用户参数
- 上下文参数
- 当前上下文

```yaml
apiVersion: v1
kind: Config
preferences: {}
 
clusters: # 集群参数
- cluster:
  name: {cluster-name}
 
users: # 用户参数
- name: {user-name}
 
contexts: # 上下文参数
- context:
    cluster: {cluster-name}
    user: {user-name}
current-context: kubernetes # 当前上下文
 ```

 ## kubeconfig 合并

通过 `kubecm` 工具合并多个 `kubeconfig` 文件

> 项目地址 https://github.com/sunny0826/kubecm

### kubecm 安装

```bash
$ export VERSION=v0.8.0

# linux x86_64 安装包
$ curl -Lo kubecm.tar.gz https://github.com/sunny0826/kubecm/releases/download/v${VERSION}/kubecm_${VERSION}_Linux_x86_64.tar.gz

# macos 安装包
$ curl -Lo kubecm.tar.gz https://github.com/sunny0826/kubecm/releases/download/v${VERSION}/kubecm_${VERSION}_Darwin_x86_64.tar.gz

# windows 安装包
$ curl -Lo kubecm.tar.gz https://github.com/sunny0826/kubecm/releases/download/v${VERSION}/kubecm_${VERSION}_Windows_x86_64.tar.gz

# # linux & macos 安装
$ tar -zxvf kubecm.tar.gz kubecm
$ cd kubecm
$ sudo mv kubecm /usr/local/bin/

# windows 安装
# Unzip kubecm.tar.gz
# Add the binary in to your $PATH
```

## 多个 kubeconfig 文件合并

把需要合并的 Kubeconfig 文件放到 all_kubeconfig 目录下，执行命令后会在当前路径下产生一个新的 kubeconfig 文件

```bash 
$ kubecm merge -f all_kubeconfig
```

直接把新生成的 kubeconfig 文件替换 `$HOME/.kube/config` 文件

```bash
$ kubecm merge -f all_kubeconfig -c
```

## 多集群切换

```bash
# 集群切换命令
$ kubecm switch
```
![集群切换](/img/kubecm-switch.gif)

## 小结

通过 `kubecm` 工具能快速的把多个 kubeconfig 文件合并到一个 kubeconfig 文件中，并且也提供集群切换。而不需要再下载 `kubectx` 工具来切换集群。

 ## 参考文档

 - https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/
 - https://github.com/sunny0826/kubecm