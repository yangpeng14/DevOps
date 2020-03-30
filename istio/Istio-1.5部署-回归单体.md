## 前言

Istio 架构又换了，从 1.5 开始，把控制平面的所有组件组合并成一个单体结构叫 `istiod`，对于运维部署来说省去很大麻烦。`Mixer` 组件被移除，新版本的 HTTP 遥测默认基于 `in-proxy Stats filter`，同时可使用 `WebAssembly` 开发 `in-proxy` 扩展。

下面展示 Istio 架构图`前世`与`今生`：

### 前世

![前世](/img/istio-1.png)


### 今生

![今生](/img/istio-2.jpeg)

## 环境要求 [1]

### Kubernetes 版本支持

- 按官方话来说，Istio 1.5 已在以下 Kubernetes 发布版本测试过：1.14, 1.15, 1.16。

## Kubernetes Pod 和 Service 要求

作为 Istio 服务网格中的一部分，Kubernetes 集群中的 Pod 和 Service 必须满足以下要求：

- 命名的服务端口: Service 的端口必须命名。端口名键值对必须按以下格式：`name: <protocol>[-<suffix>]`。更多说明请参看[协议选择](https://istio.io/zh/docs/ops/configuration/traffic-management/protocol-selection/)。
- Service 关联: 每个 Pod 必须至少属于一个 Kubernetes Service，不管这个 Pod 是否对外暴露端口。如果一个 Pod 同时属于多个 [Kubernetes Service](https://kubernetes.io/docs/concepts/services-networking/service/)， 那么这些 Service 不能同时在一个端口号上使用不同的协议（比如：HTTP 和 TCP）。
- 带有 app 和 version 标签（label） 的 Deployment: 我们建议显式地给 Deployment 加上 app 和 version 标签。给使用 Kubernetes Deployment 部署的 Pod 部署配置中增加这些标签，可以给 Istio 收集的指标和遥测信息中增加上下文信息。
    - app 标签：每个部署配置应该有一个不同的 app 标签并且该标签的值应该有一定意义。app label 用于在分布式追踪中添加上下文信息。
    - version 标签：这个标签用于在特定方式部署的应用中表示版本。
- 应用 UID: 确保你的 Pod 不会以用户 ID（UID）为 1337 的用户运行应用。
- NET_ADMIN 功能: 如果你的集群执行 Pod 安全策略，必须给 Pod 配置 NET_ADMIN 功能。如果你使用 [Istio CNI](https://istio.io/zh/docs/setup/additional-setup/cni/) 插件 可以不配置。要了解更多 NET_ADMIN 功能的知识，请查看[所需的 Pod 功能](https://istio.io/zh/docs/ops/deployment/requirements/#required-pod-capabilities)。

### 下载 Istio 1.15 版本

> 注意：Linux 操作系统

1.下载 Istio 1.15.1 安装包

```bash
$ cd /usr/local/src/
$ wget https://github.com/istio/istio/releases/download/1.5.1/istio-1.5.1-linux.tar.gz
$ tar xf istio-1.5.1-linux.tar.gz
```

2.切换 Istio 包所在目录

```bash
$ cd istio-1.5.1
```
安装目录包含如下内容：
- install/kubernetes 目录下，有 Kubernetes 相关的 YAML 安装文件
- samples/ 目录下，有示例应用程序
- bin/ 目录下，包含 istioctl 的客户端文件。istioctl 工具用于手动注入 Envoy sidecar 代理。

3.将 istioctl 命令添加到环境变量中

```bash
# 在 ~/.bashrc 中添加一行
$ vim ~/.bashrc

PATH="$PATH:/usr/local/src/istio-1.5.1/bin"

# 应用生效
$ source ~/.bashrc
```

4.配置 istioctl 参数自动补全

```bash
$ vim ~/.bashrc

source /usr/local/src/istio-1.5.1/tools/istioctl.bash

# 应用生效
$ source ~/.bashrc
```

## 部署

istioctl 提供了多种安装配置文件，它们之间差异：

![](/img/istio-3.png)

### 安装配置提要：

- `default` 基础上开启 `Grafana`、`istio-tracing`、`kiali` 附加组件
- `cni` 配置关闭，但相关参数已配置
- 全局禁用 `TLS`
- `Grafana`、`istio-tracing`、`kiali`、`prometheus` 通过 `istio-ingressgateway` 暴露
- 排除 `192.168.16.0/20,192.168.32.0/20` k8s svc 和 k8s pod 两个网段
- `Ingress Gateway` 与 `pilot` 开启2个pod（默认1个pod）
- Pod 绑定节点标签 `zone: sz`
- `Ingress Gateway` 使用 `HostNetwork` 模式暴露
- `overlays` 字段用来修改对应组件的各个资源对象的 `manifest`
- 调整 `PDB` 配置
- 安装前需要创建 `grafana` 和 `kiali` secret，用于登陆
- `Ingress Gateway` 从安全的角度来考虑，不应该暴露那些不必要的端口，对于 Ingress Gateway 来说，只需要暴露 HTTP、HTTPS 和 metrics 端口就够了

### 配置 `grafana` 和 `kiali` secret

创建 istio-system namespaces
```bash
$ kubectl create ns istio-system
```

配置 kiali secret
```bash
$ KIALI_USERNAME=$(echo -n 'admin' | base64)
$ KIALI_PASSPHRASE=$(echo -n 'admin' | base64)
$ NAMESPACE=istio-system

$ cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: kiali
  namespace: $NAMESPACE
  labels:
    app: kiali
type: Opaque
data:
  username: $KIALI_USERNAME
  passphrase: $KIALI_PASSPHRASE
EOF
```

配置 grafana secret
```bash
$ GRAFANA_USERNAME=$(echo -n 'admin' | base64)
$ GRAFANA_PASSPHRASE=$(echo -n 'admin' | base64)
$ NAMESPACE=istio-system

$ cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: grafana
  namespace: $NAMESPACE
  labels:
    app: grafana
type: Opaque
data:
  username: $GRAFANA_USERNAME
  passphrase: $GRAFANA_PASSPHRASE
EOF
```

### 推荐使用 `Operator` 方式进行部署，这里使用 `default` 配置部署（default 也是用于生产环境）

创建 Istio Operator yaml 配置
``` bash
$ vim istio-1.5.1.yaml
```

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  namespace: istio-system
  name: istio-1.5.1-controlplane
spec:
  hub: docker.io/istio
  profile: default # 使用默认配置
  tag: 1.5.1

  addonComponents:
    grafana:
      enabled: true # 默认 false
      k8s:
        replicaCount: 1
    kiali:
      enabled: true # 默认 false
      k8s:
        replicaCount: 1
    prometheus:
      enabled: true # 默认 true
      k8s:
        replicaCount: 1
    tracing:
      enabled: true # 默认 false

  values:
    global:
      imagePullPolicy: IfNotPresent # 镜像拉取策略
      mtls:
        enabled: false # 全局禁用安全性
      defaultResources: # 声明默认容器资源
        requests:
          cpu: 30m
          memory: 50Mi
      proxy:
        accessLogFile: "/dev/stdout"
        includeIPRanges: 192.168.16.0/20,192.168.32.0/20
        autoInject: disabled # 是否开启自动注入功能，取值enabled则该pods只要没有被注解为sidecar.istio.io/inject: "false",就会自动注入。如果取值为disabled，则需要为pod设置注解sidecar.istio.io/inject: "true"才会进行注入
        clusterDomain: cluster.local # 集群DNS域
        resources:
          requests:
            cpu: 30m # 默认 100m
            memory: 50Mi # 默认 128Mi
          limits:
            cpu: 400m # 默认 2000m
            memory: 500Mi # 默认 1024Mi
      proxy_init:
        resources:
          limits:
            cpu: 100m
            memory: 50Mi
          requests:
            cpu: 30m # 默认 10m
            memory: 50Mi # 默认 10Mi
    sidecarInjectorWebhook:
      enableNamespacesByDefault: false # 变量为true，就会为所有命名空间开启自动注入功能。如果赋值为false，则只有标签为istio-injection的命名空间才会开启自动注入功能
      rewriteAppHTTPProbe: false # 如果是 true，webhook 或 istioctl injector 将为活性健康检查重写 PodSpec 以重定向请求到 sidecar。这使得即使在启用 mTLS 时，活性检查也可以工作
    cni:
      excludeNamespaces: # 开启cni功能时，下面namespaces被排除
        - istio-system
        - kube-system
        - monitoring
        - kube-node-lease
        - kube-public
        - kubernetes-dashboard
        - ingress-nginx
      logLevel: info
    pilot:
      autoscaleEnabled: true
      autoscaleMax: 5
      autoscaleMin: 1
      cpu:
        targetAverageUtilization: 80
    prometheus:
      contextPath: /prometheus # 默认 /prometheus
      hub: docker.io/prom
      resources: # 默认无限制
        requests:
          cpu: 30m
          memory: 50Mi
        limits:
          cpu: 500m
          memory: 1024Mi
      nodeSelector:
        zone: "sz"
      retention: 7d # 默认 6h
      scrapeInterval: 15s
      security:
        enabled: true
      tag: v2.15.1
    grafana:
      contextPath: /grafana  # 默认 /grafana
      accessMode: ReadWriteMany
      image:
        repository: grafana/grafana
        tag: 6.5.2
      resources:
        requests:
          cpu: 30m
          memory: 50Mi
        limits:
          cpu: 300m
          memory: 500Mi
      nodeSelector:
        zone: "sz"
      security: # 默认关闭认证
        enabled: true # 默认 false
        passphraseKey: passphrase # 首先创建 grafana secret
        secretName: grafana
        usernameKey: username # 首先创建 grafana secret
    kiali:
      contextPath: /kiali  # 默认 /kiali
      createDemoSecret: false
      dashboard:
        grafanaInClusterURL: http://grafana.example.com # 默认 http://grafana:3000
        jaegerInClusterURL: http://tracing.example.com # 默认 http://tracing/jaeger
        passphraseKey: passphrase # 首先创建 kiali secret
        secretName: kiali
        usernameKey: username # 首先创建 kiali secret
        viewOnlyMode: false
      hub: kiali  # 默认 quay.io/kiali
      resources:
        limits:
          cpu: 300m
          memory: 900Mi
        requests:
          cpu: 30m
          memory: 50Mi
      nodeSelector:
        zone: "sz"
      tag: v1.14
    tracing:
      provider: jaeger # 选择跟踪服务
      jaeger:
        accessMode: ReadWriteMany
        hub: docker.io/jaegertracing
        tag: "1.16"
        resources:
          limits:
            cpu: 300m
            memory: 900Mi
          requests:
            cpu: 30m
            memory: 100Mi
      nodeSelector:
        zone: "sz"
      opencensus:
        exporters:
          stackdriver:
            enable_tracing: true
        hub: docker.io/omnition
        resources:
          limits:
            cpu: "1"
            memory: 2Gi
          requests:
            cpu: 100m # 默认 200m
            memory: 300Mi # 默认 400Mi
        tag: 0.1.9
      zipkin:
        hub: docker.io/openzipkin
        javaOptsHeap: 700
        maxSpans: 500000
        node:
          cpus: 2
        resources:
          limits:
            cpu: 300m
            memory: 900Mi
          requests:
            cpu: 30m # 默认 150m
            memory: 100Mi # 默认 900Mi
        tag: 2.14.2

  components:
    cni:
      enabled: false # 默认不启用cni功能
    ingressGateways:
    - enabled: true
      k8s:
        hpaSpec:
          minReplicas: 2 # 默认最小为1个pod
        service:
          type: ClusterIP # 默认类型为 LoadBalancer
        resources:
          limits:
            cpu: 1000m # 默认 2000m
            memory: 1024Mi # 默认 1024Mi
          requests:
            cpu: 100m # 默认 100m
            memory: 128Mi # 默认 128Mi
        strategy:
          rollingUpdate:
            maxSurge: 100%
            maxUnavailable: 25%
        nodeSelector:
          zone: "sz"
        overlays: 
        - apiVersion: apps/v1 # 使用 hostNetwork 模式暴露 ingressGateways
          kind: Deployment
          name: istio-ingressgateway
          patches:
          - path: spec.template.spec.hostNetwork
            value:
              true
          - path: spec.template.spec.dnsPolicy
            value:
              ClusterFirstWithHostNet
        - apiVersion: v1 # 从安全的角度来考虑，不应该暴露那些不必要的端口，对于 Ingress Gateway 来说，只需要暴露 HTTP、HTTPS 和 metrics 端口就够了
          kind: Service
          name: istio-ingressgateway
          patches:
          - path: spec.ports
            value:
            - name: status-port
              port: 15020
              targetPort: 15020
            - name: http2
              port: 80
              targetPort: 80
            - name: https
              port: 443
              targetPort: 443
    pilot:
      enabled: true
      k8s:
        hpaSpec:
          minReplicas: 2 # 默认最小为1个pod
        resources:
          limits:
            cpu: 1000m # 默认不限制
            memory: 1024Mi # 默认不限制
          requests:
            cpu: 100m # 默认 500m
            memory: 300Mi # 默认 2048Mi
        strategy:
          rollingUpdate:
            maxSurge: 100%
            maxUnavailable: 25%
        nodeSelector:
          zone: "sz"
        overlays: # 调整PDB配置
        - apiVersion: policy/v1beta1
          kind: PodDisruptionBudget
          name: istiod
          patches:
          - path: spec.selector.matchLabels
            value:
              app: istiod
              istio: pilot
```

部署 Istio 
```bash
$ istioctl manifest apply -f istio-1.5.1.yaml
```

设置 `Grafana`、`istio-tracing`、`kiali`、`prometheus` 通过 `istio-ingressgateway` 暴露

```bash
$ vim istio-addon-components-gateway.yaml
```

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: istio-addon-components-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway # use istio default controller
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "grafana.example.com"
    - "tracing.example.com"
    - "kiali.example.com"
    - "prometheus.example.com"
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: istio-grafana
  namespace: istio-system
spec:
  hosts:
  - "grafana.example.com"
  gateways:
  - istio-addon-components-gateway
  http:
  - route:
    - destination:
        host: grafana
        port:
          number: 3000
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: istio-tracing
  namespace: istio-system
spec:
  hosts:
  - "tracing.example.com"
  gateways:
  - istio-addon-components-gateway
  http:
  - route:
    - destination:
        host: tracing
        port:
          number: 80
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: istio-kiali
  namespace: istio-system
spec:
  hosts:
  - "kiali.example.com"
  gateways:
  - istio-addon-components-gateway
  http:
  - route:
    - destination:
        host: kiali
        port:
          number: 20001
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: istio-prometheus
  namespace: istio-system
spec:
  hosts:
  - "prometheus.example.com"
  gateways:
  - istio-addon-components-gateway
  http:
  - route:
    - destination:
        host: prometheus
        port:
          number: 9090
```

部署 `Grafana`、`istio-tracing`、`kiali`、`prometheus` 服务 Gateway 和 VirtualService
```bash
$ kubectl apply -f istio-addon-components-gateway.yaml
```

部署完成后，查看各组件状态：
```bash
$ kubectl get svc,pod,hpa,pdb,Gateway,VirtualService -n istio-system
```
![](/img/istio-4.png)

## 参考链接

- [1]https://istio.io/zh/docs/ops/deployment/requirements/
- https://istio.io/docs/setup/install/standalone-operator/
- https://www.danielstechblog.io/high-available-control-plane-with-istio-1-5-on-azure-kubernetes-service/