## QoS（Quality of Service） 简介
QoS（Quality of Service），大部分译为 `“服务质量等级”`，又译作 `“服务质量保证”`，是作用在 Pod 上的一个配置，当 Kubernetes 创建一个 Pod 时，它就会给这个 Pod 分配一个 QoS 等级，可以是以下等级之一：

- `Guaranteed`：Pod 里的每个容器都必须有内存/CPU 限制和请求，而且值必须相等。如果一个容器只指明limit而未设定request，则request的值等于limit值。
- `Burstable`：Pod 里至少有一个容器有内存或者 CPU 请求且不满足 Guarantee 等级的要求，即内存/CPU 的值设置的不同。
- `BestEffort`：容器必须没有任何内存或者 CPU 的限制或请求。

该配置不是通过一个配置项来配置的，而是通过配置 CPU/MEM的 `limits` 与 `requests` 值的大小来确认`服务质量等级`。

下面是 `Guaranteed` 例子：
```yaml
    spec:
      containers:
      - name: demo
        image: mritd/demo
        resources:
          limits:
            cpu: 100m
            memory: 100Mi
          requests:
            cpu: 100m
            memory: 100Mi
        ports:
        - containerPort: 80
```

下面是 `Burstable` 例子：
```yaml
    spec:
      containers:
      - name: demo
        image: mritd/demo
        resources:
          limits:
            cpu: 100m
            memory: 100Mi
          requests:
            cpu: 10m
            memory: 10Mi
        ports:
        - containerPort: 80
```

下面是 `BestEffort` 例子：
```yaml
    spec:
      containers:
      - name: demo
        image: mritd/demo
        ports:
        - containerPort: 80
```

## 资源限制 Limits 和 资源需求 Requests

`对于CPU`：如果pod中服务使用CPU超过设置的 limits，pod不会被kill掉但会被限制。如果没有设置limits，pod可以使用全部空闲的cpu资源。

`对于内存`：当一个pod使用内存超过了设置的 limits，pod中 `container` 的进程会被 `kernel` 因`OOM kill`掉。当container因为OOM被kill掉时，系统倾向于在其原所在的机器上重启该container或本机或其他重新创建一个pod。

## 下面是三个资源限制，作用域在不同点上

- 针对 `Node` 节点资源预留，在 `kubelet` 组件中配置

```bash
# 下面配置根据实际情况调整

--system-reserved=cpu=500m,memory=1.5Gi \
--eviction-hard=memory.available<1.5Gi,nodefs.available<20Gi,imagefs.available<15Gi \
--eviction-soft=memory.available<2Gi,nodefs.available<25Gi,imagefs.available<10Gi \
--eviction-soft-grace-period=memory.available=2m,nodefs.available=2m,imagefs.available=2m \
--eviction-max-pod-grace-period=30 \
--eviction-minimum-reclaim=memory.available=200Mi,nodefs.available=5Gi,imagefs.available=5Gi
```

- 针对 `namespace` 限制配置

```yaml
apiVersion: "v1"
kind: "LimitRange"
metadata:
  name: "test-resource-limits"
  namespace: test
spec:
  limits:
    - type: "Pod"
      max:
        cpu: "2"
        memory: "2Gi"
      min:
        cpu: "30m"
        memory: "50Mi"
    - type: "Container"
      max:
        cpu: "2"
        memory: "2Gi"
      min:
        cpu: "30m"
        memory: "50Mi"
      default:
        cpu: "300m"
        memory: "600Mi"
      defaultRequest:
        cpu: "30m"
        memory: "50Mi"
      maxLimitRequestRatio:
        cpu: "30"
```

- 针对 `Pod` 限制，可以通过 `Deployment` 配置

```yaml
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  name: demo-deployment
spec:
  replicas: 1
  template:
    metadata:
      annotations:
        sidecar.istio.io/inject: "false"
      labels:
        app: demo
    spec:
      containers:
      - name: demo
        image: mritd/demo
        resources:
          limits:
            cpu: 100m
            memory: 100Mi
          requests:
            cpu: 10m
            memory: 10Mi
        ports:
        - containerPort: 80
```

## QoS 优先级

`三种 QoS 优先级，从高到低（从左往右）`

Guaranteed --> Burstable -->  BestEffort

## Kubernetes 资源回收策略

`Kubernetes 资源回收策略`：当集群监控到 `node` 节点内存或者CPU资源耗尽时，为了保护node正常工作，就会启动资源回收策略，通过驱逐节点上Pod来减少资源占用。

`三种 QoS 策略被驱逐优先级，从高到低（从左往右）`

BestEffort --> Burstable --> Guaranteed

## 使用建议

- 如果资源充足，可以将 pod QoS 设置为 Guaranteed
- 不是很关键的服务 pod QoS 设置为 Burstable 或者 BestEffort。比如 filebeat、logstash、fluentd等

建议：k8s 安装时，建议把 `Swap` 关闭，虽然 `Swap` 可以解决内存不足问题，但当内存不足使用`Swap`时，系统负载会出现过高，原因是 `swap` 大量 `占用磁盘IO`。

## 参考链接

- https://jimmysong.io/kubernetes-handbook/concepts/qos.html
- http://dockone.io/article/2592