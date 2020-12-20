## 一、kubectl 命令参数自动补全

使用 Kubernetes，就一定会使用 Kubectl 命令，默认安装好 Kubectl 命令不支持自动补全参数。下面配置 Kubectl 命令参数自动补全方法：

### Linux 上，比如 Centos

```bash
$ yum install -y bash-completion
$ source /usr/share/bash-completion/bash_completion
$ source <(kubectl completion bash)
$ echo "source <(kubectl completion bash)" >> ~/.bashrc
```

### MAC 上

```bash
$ brew install bash-completion
$ source $(brew --prefix)/etc/bash_completion
$ source <(kubectl completion zsh)
$ echo 'source <(kubectl completion zsh)' >> ~/.zshrc
```

### Kubectl 常用操作 [1]

1、如何查找非 running 状态的 Pod 呢？

```bash
$ kubectl get pods -A --field-selector=status.phase!=Running | grep -v Complete
```

2、如何查找 running 状态的 Pod 呢？

```bash
$ kubectl get pods -A --field-selector=status.phase=Running | grep -v Complete
```

3、获取节点列表，其中包含运行在每个节点上的 Pod 数量？

```bash
$ kubectl get po -o json --all-namespaces |    jq '.items | group_by(.spec.nodeName) | map({"nodeName": .[0].spec.nodeName, "count": length}) | sort_by(.count)'

[
  {
    "nodeName": "service1",
    "count": 6
  },
  {
    "nodeName": "service3",
    "count": 13
  }
]
```

4、使用 kubectl top 获取 Pod 列表并根据其消耗的 CPU 或 内存进行排序

```bash
# 获取 cpu
$ kubectl top pods -A | sort --reverse --key 3 --numeric

# 获取 memory
$ kubectl top pods -A | sort --reverse --key 4 --numeric
```

## 二、添加Namespace默认CPU和内存限制

有时候 Pod 没有做资源限制，会因为个别 Pod 使用量超出，影响整个宿主机应用。下面给出一个具体例子，可以根据实际情况来调整相关参数。

```yaml
apiVersion: "v1"
kind: "LimitRange"
metadata:
  name: "resource-limits"
  namespace: default
spec:
  limits:
    - type: "Pod"
      max:
        cpu: "4"
        memory: "4Gi"
      min:
        cpu: "100m"
        memory: "100Mi"
    - type: "Container"
      max:
        cpu: "4"
        memory: "4Gi"
      min:
        cpu: "100m"
        memory: "100Mi"
      default:
        cpu: "500m"
        memory: "500Mi"
      defaultRequest:
        cpu: "100m"
        memory: "100Mi"
      maxLimitRequestRatio:
        cpu: "60"
```

## 三、利用 Kubelet 给 Node 预留资源

```yaml
evictionHard:
  imagefs.available: 15%
  memory.available: 1G
  nodefs.available: 10%
  nodefs.inodesFree: 5%
```

## 四、利用 Kubernetes RBAC 划分好权限

多个团队部署应用到一个kubernetes集群时，情况就可能变得很复杂。切记不要把管理员权限开放给每个人。个人建议是，根据命名空间来区分隔离每个团队，然后使用RBAC策略只允许各自团队访问各自的命名空间。

如果我们把管理员权限开放给每个人，那么在pod级上进行读取、创建和删除访问时，可能让人抓狂，因为误操作的情况会经常发生。为此，应该只允许管理员有权访问，从而将管理集群和部署集群的人员权限区分开。

## 五、充分利用 PodDisruptionBudget 控制器

如何保证在 kubernetes 集群中的应用程序总能正常运行？

答案：是使用 `PodDisruptionBudget` 控制器。

在进行 `kubectl drain` 操作时，kubernetes 会根据 `PodDisruptionBudget` 控制器判断应用Pod集群数量，进而保证在业务不中断或业务SLA不降级的情况下进行应用Pod销毁。PDB(PodDisruptionBudget)应该放在每个拥有一个以上实例的deployment上。我们可以使用简单yaml为集群创建PDB，并使用标签选择器确定PDB应该作用在哪些带有标签的资源上。

> `注意`：PDB只考虑`主动中断`，`硬件故障`之类的情况不在PDB考虑范围内。

例子：

```yaml
apiVersion: policy/v1beta1
kind: PodDisruptionBudget
metadata:
  name: zk-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: zookeeper
```

## 六、使用探针来检测应用的状态

Kubernetes中支持配置探针。kubelet 使用探针来确定Pod中应用程序是否健康。K8S 提供了两种类型来实现这一功能，`Readiness` 探针和 `Liveiness` 探针。

- `Readiness`：探针用于确定容器何时准备好接收流量。
- `Liveiness`：探针用于确定容器是否健康，如果不健康根据策略判断是否重新部署一个新的容器来替换。

例子：

```ymal
    readinessProbe:
      tcpSocket:
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 10
    livenessProbe:
      tcpSocket:
        port: 8080
      initialDelaySeconds: 15
      periodSeconds: 20
```

## 参考链接

- [1] https://mp.weixin.qq.com/s/fJpSlVOywrgIhejsWSvhbw
- [2] https://zhuanlan.zhihu.com/p/81666500