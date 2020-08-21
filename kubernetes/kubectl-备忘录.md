## Kubectl 备忘录

### Kubectl 自动补全

`BASH` 环境下设置

```bash
# Centos 或者 RedHat 需要安装 bash-completion 包命令
$ yum install -y bash-completion

# Ubuntu 或者 Debian 需要安装 bash-completion 包命令
$ apt install -y bash-completion

# 写入当前用户 .bashrc 文件中
$ echo "source /usr/share/bash-completion/bash_completion" >> ~/.bashrc
$ echo "source <(kubectl completion bash)" >> ~/.bashrc

# 让当前终端生效
$ source ~/.bashrc
```

`ZSH` 环境设置

```bash
# 写入当前用户 .zshrc 文件中
$ echo "if [ $commands[kubectl] ]; then source <(kubectl completion zsh); fi" >> ~/.zshrc

# 让当前终端生效
$ source ~/.zshrc
```

### Kubeconfig 格式介绍

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
  name: kubernetes # 集群上下文名称
current-context: kubernetes # 当前上下文
```

多个集群 `kubeconfig` 文件，请参考 [Kubeconfig文件自动合并-实现K8S多集群切换](https://www.yp14.cn/2020/06/21/Kubeconfig%E6%96%87%E4%BB%B6%E8%87%AA%E5%8A%A8%E5%90%88%E5%B9%B6-%E5%AE%9E%E7%8E%B0K8S%E5%A4%9A%E9%9B%86%E7%BE%A4%E5%88%87%E6%8D%A2/)

### Kubectl apply -f . 或者  kubectl create -f . 执行顺序

下面是 `kube-prometheus` 项目 `setup` 目录

```bash
$ ls -lsh setup

0namespace-namespace.yaml
prometheus-operator-0alertmanagerCustomResourceDefinition.yaml
prometheus-operator-0podmonitorCustomResourceDefinition.yaml
prometheus-operator-0prometheusCustomResourceDefinition.yaml
prometheus-operator-0prometheusruleCustomResourceDefinition.yaml
prometheus-operator-0servicemonitorCustomResourceDefinition.yaml
prometheus-operator-0thanosrulerCustomResourceDefinition.yaml
prometheus-operator-clusterRole.yaml
prometheus-operator-clusterRoleBinding.yaml
prometheus-operator-deployment.yaml
prometheus-operator-service.yaml
prometheus-operator-serviceAccount.yaml
```

通过上面可以观察到 `0namespace-namespace.yaml` 文件前面添加了一个 `0`，这个yaml文件会优先执行。

执行顺序如下：

> 按 `yaml文件` 首个字母或者数字来排序

- 首先，数字从小到大顺序执行，比如： 0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 ...
- 然后，按字母排序顺序执行，比如：a -> b -> c -> d -> e -> f -> g ...

### Kubectl 查询资源 [1]

```bash
# 查询k8s支持的 api 版本
$ kubectl api-versions

# 查询k8s支持的 resources 类型
$ kubectl api-resources

# resources 类型详细操作
$ kubectl api-resources --namespaced=true      # 所有命名空间作用域的资源
$ kubectl api-resources --namespaced=false     # 所有非命名空间作用域的资源
$ kubectl api-resources -o name                # 用简单格式列举所有资源（仅显示资源名称）
$ kubectl api-resources -o wide                # 用扩展格式列举所有资源（又称 "wide" 格式）
$ kubectl api-resources --verbs=list,get       # 支持 "list" 和 "get" 请求动词的所有资源
$ kubectl api-resources --api-group=extensions # "extensions" API 组中的所有资源
```

### kubectl get --raw 使用

`kubectl get --raw`：从 kubernetes 集群请求的原始 URI

例子：

```bash
# 查询 kubernetes metrics 信息
$ kubectl get --raw "/apis/metrics.k8s.io/v1beta1" | jq

{
  "kind": "APIResourceList",
  "apiVersion": "v1",
  "groupVersion": "metrics.k8s.io/v1beta1",
  "resources": [
    {
      "name": "nodes",
      "singularName": "",
      "namespaced": false,
      "kind": "NodeMetrics",
      "verbs": [
        "get",
        "list"
      ]
    },
    {
      "name": "pods",
      "singularName": "",
      "namespaced": true,
      "kind": "PodMetrics",
      "verbs": [
        "get",
        "list"
      ]
    }
  ]
}
```

### Kubectl 日志输出和调试 [1]

Kubectl 日志输出详细程度是通过 `-v` 或者 `--v` 来控制的，参数后跟一个`数字`表示`日志的级别`。具体解释请看下面列表：

日志级别 | 描述
---|---
--v=0 | 用于那些应该 始终 对运维人员可见的信息，因为这些信息一般很有用。
--v=1 | 如果您不想要看到冗余信息，此值是一个合理的默认日志级别。
--v=2 | 输出有关服务的稳定状态的信息以及重要的日志消息，这些信息可能与系统中的重大变化有关。这是建议大多数系统设置的默认日志级别。
--v=3 | 包含有关系统状态变化的扩展信息。
--v=4 | 包含调试级别的冗余信息。
--v=6 | 显示所请求的资源。
--v=7 | 显示 HTTP 请求头。
--v=8 | 显示 HTTP 请求内容。
--v=9 | 显示 HTTP 请求内容而且不截断内容。

## 参考链接

- [1] https://kubernetes.io/zh/docs/reference/kubectl/cheatsheet/