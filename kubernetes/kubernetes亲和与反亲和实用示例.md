## K8S亲和与反亲和简介 [1]

nodeSelector 提供了一种非常简单的方法来将 pod 约束到具有特定标签的节点上。亲和/反亲和功能极大地扩展了你可以表达约束的类型。关键的增强点是

- (1) 语言更具表现力（不仅仅是“完全匹配的 AND”）
- (2) 你可以发现规则是“软”/“偏好”，而不是硬性要求，因此，如果调度器无法满足该要求，仍然调度该 pod
- (3) 你可以使用节点上（或其他拓扑域中）的 pod 的标签来约束，而不是使用节点本身的标签，来允许哪些 pod 可以或者不可以被放置在一起

亲和功能包含两种类型的亲和，即

- 节点亲和
- pod 间亲和/反亲和

节点亲和就像现有的 nodeSelector（但具有上面列出的前两个好处），然而 pod 间亲和/反亲和约束 pod 标签而不是节点标签（在上面列出的第三项中描述，除了具有上面列出的第一和第二属性）。

## 节点亲和 [1]

节点亲和概念上类似于 nodeSelector，它使你可以根据节点上的标签来约束 pod 可以调度到哪些节点。

目前有两种类型的节点亲和：

- requiredDuringSchedulingIgnoredDuringExecution
- preferredDuringSchedulingIgnoredDuringExecution

第一种可以视它们为`硬亲和`，第二种以视它们为`软亲和`，意思是，第一种指定了将 pod 调度到一个节点上`必须满足的规则`（就像 nodeSelector 但使用更具表现力的语法），第二种指定调度器将尝试执行但`不能保证一定调度该节点`。

名称的 `IgnoredDuringExecution` 部分意味着，类似于 `nodeSelector` 的工作原理，如果节点的标签在运行时发生变更，从而不再满足 pod 上的亲和规则，那么 pod 将仍然继续在该节点上运行。

## pod 间亲和与反亲和 [1]

pod 间亲和与反亲和使你可以`基于已经在节点上运行的 pod 的标签`来约束 pod 可以调度到的节点，而不是基于节点上的标签。规则的格式为如果 X 节点上已经运行了一个或多个 满足规则 Y 的pod，则这个 pod 应该（或者在非亲和的情况下不应该）运行在 X 节点。Y 表示一个具有可选的关联命令空间列表的 `LabelSelector`；与节点不同，因为 pod 是命名空间限定的（因此 pod 上的标签也是命名空间限定的），因此作用于 pod 标签的标签选择器必须指定选择器应用在哪个命名空间。从概念上讲，X 是一个拓扑域，如节点，机架，云供应商地区，云供应商区域等。你可以使用 `topologyKey` 来表示它，`topologyKey` 是节点标签的键以便系统用来表示这样的拓扑域。

> 注意：Pod 间亲和与反亲和需要大量的处理，这可能会显著减慢大规模集群中的调度。我们不建议在超过数百个节点的集群中使用它们。

> 注意：Pod 反亲和需要对节点进行一致的标记，即集群中的每个节点必须具有适当的标签能够匹配 `topologyKey`。如果某些或所有节点缺少指定的 `topologyKey` 标签，可能会导致意外行为。

与节点亲和一样，当前有两种类型的 pod 亲和与反亲和，即 `requiredDuringSchedulingIgnoredDuringExecution` 和 `preferredDuringSchedulingIgnoredDuringExecution`，分表表示“硬性”与“软性”要求。请参阅前面节点亲和部分中的描述。requiredDuringSchedulingIgnoredDuringExecution 亲和的一个示例是“将服务 A 和服务 B 的 pod 放置在同一区域，因为它们之间进行大量交流”，而 `preferredDuringSchedulingIgnoredDuringExecution` 反亲和的示例将是“将此服务的 pod 跨区域分布”（硬性要求是说不通的，因为你可能拥有的 pod 数多于区域数）。

Pod 间亲和通过 PodSpec 中 `affinity` 字段下的 podAffinity 字段进行指定。而 pod 间反亲和通过 PodSpec 中 affinity 字段下的 `podAntiAffinity` 字段进行指定。


## 实用示例

### 例一

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - image: nginx
        name: nginx
        ports:
        - containerPort: 80
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: zone
                operator: In
                values:
                - bj
```
`例一` 表示使用节点亲和规则，nginx pod 只能放置具有标签键为 `zone` 且 标签值为 `bj` 的节点上。

> `operator` 操作符支持 `In`，`NotIn`，`Exists`，`DoesNotExist`，`Gt`，`Lt`。

### 例二

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - image: nginx
        name: nginx
        ports:
        - containerPort: 80
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: zone
                operator: In
                values:
                - bj
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 1
            preference:
              matchExpressions:
              - key: environment
                operator: In
                values:
                - dev
```
`例二` 表示使用节点亲和规则，nginx pod 只能放置具有标签键为 `zone` 且 标签值为 `bj` 的节点上。另外，在满足这些标准的节点中，具有标签键为 `environment` 且标签值为 `dev` 的节点应该优先使用。

> `preferredDuringSchedulingIgnoredDuringExecution` 中的 `weight` 字段值的范围是 `1-100`。对于每个符合所有调度要求（资源请求，RequiredDuringScheduling 亲和表达式等）的节点，调度器将遍历该字段的元素来计算总和，并且如果节点匹配对应的MatchExpressions，则添加`权重`到总和。然后将这个评分与该节点的其他优先级函数的评分进行组合。总分最高的节点是最优选的。

### 例三

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - image: nginx
        name: nginx
        ports:
        - containerPort: 80
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: zone
                operator: In
                values:
                - bj
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - nginx
              topologyKey: "kubernetes.io/hostname"
```

`例三` 表示 nginx pod 只能放置具有标签键为 `zone` 且 标签值为 `bj` 的节点上。另外，如果节点上已经存在 `labelSelector` 为 `app: nginx`，此节点就不能再调度。（通俗的说，每个节点只能放一个nginx pod）

### 例四

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - image: nginx
        name: nginx
        ports:
        - containerPort: 80
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: zone
                operator: In
                values:
                - bj
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 10
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - nginx
              topologyKey: "kubernetes.io/hostname"
```

`例四` 表示 nginx pod 只能放置具有标签键为 `zone` 且 标签值为 `bj` 的节点上。另外，尽量先放没有 `labelSelector` 为 `app: nginx` 节点。（通俗的说，一个节点尽量不要放两个nginx pod）


## 参考链接

- [1] https://kubernetes.io/zh/docs/concepts/configuration/assign-pod-node/