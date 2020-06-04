## 前言

一般在机房或者云上使用ECS自建Kubernetes集群是无法使用 `LoadBalancer` 类型的 `Service` 。因为 Kubernetes 本身没有为裸机群集提供网络负载均衡器的实现。

自建的 Kubernetes 集群暴露让外网访问，目前只能使用 `NodePort` 或 `Ingress` 的方法进行服务暴露。`NodePort` 缺点是每个暴露的服务需要占用所有节点的某个端口。`Ingress` 是一个不错的解方法。

有没有方法，让自建的 Kubernetes 集群也能使用 `LoadBalancer` 类型的 `Service` ？

当然有方法可以实现，今天介绍一个 `MetalLB` 应用，可以实现这个功能。

## 什么是 MetalLB

`MetalLB` 是一个负载均衡器，专门解决裸金属 Kubernetes 集群中无法使用 `LoadBalancer` 类型服务的痛点。`MetalLB` 使用标准化的路由协议，以便裸金属 Kubernetes 集群上的外部服务也尽可能地工作。即 MetalLB 能够帮助你在裸金属 Kubernetes 集群中创建 LoadBalancer 类型的 Kubernetes 服务，该项目发布于 2017 年底，当前处于 `Beta` 阶段。

> 注意：`MetalLB` 项目还是处于 `Beta` 阶段，暂时不推荐用于生产环境。

> 项目地址：https://github.com/danderson/metallb

## MetalLB 概念

`MetalLB` 会在 Kubernetes 内运行，监控服务对象的变化，一旦监测到有新的 `LoadBalancer` 服务运行，并且没有可申请的负载均衡器之后，就会完成地址分配和外部声明两部分的工作。


### 地址分配

在云厂商提供的 Kubernetes 集群中，Service 声明使用 LoadBalancer时，云平台会自动分配一个负载均衡器的IP地址给你，应用可以通过这个地址来访问。

使用 MetalLB 时，MetalLB 会自己为用户的 LoadBalancer 类型 Service 分配 IP 地址，当然该 IP 地址不是凭空产生的，需要用户在配置中提供一个 IP 地址池，Metallb 将会在其中选取地址分配给服务。

### 外部声明

一旦 MetalLB 为服务分配了IP地址，它需要对外宣告此 IP 地址，并让外部主机可以路由到此 IP。

外部声明有两种模式：

- Layer 2 模式
- BGP 模式

1、Layer 2 模式

Layer 2 模式下，每个 Service 会有集群中的一个 Node 来负责。服务的入口流量全部经由单个节点，然后该节点的 Kube-Proxy 会把流量再转发给服务的 Pods。也就是说，该模式下 MetalLB 并没有真正提供负载均衡器。尽管如此，MetalLB 提供了故障转移功能，如果持有 IP 的节点出现故障，则默认 10 秒后即发生故障转移，IP 会被分配给其它健康的节点。

Layer 2 模式 优点 与 缺点：

优点：

- 是它的通用性：它可以在任何以太网网络上运行，不需要特殊的硬件。

缺点：

- Layer 2 模式下存在单节点瓶颈，服务所有流量都经过一个Node节点。这意味着服务的入口带宽被限制为单个节点的带宽。
- 由于 Layer 2 模式需要 ARP/NDP 客户端配合，当故障转移发生时，MetalLB 会发送 ARP 包来宣告 MAC 地址和 IP 映射关系的变化，地址分配略为繁琐。

2、BGP 模式

BGP 模式下，集群中所有node都会跟上联路由器建立BGP连接，并且会告知路由器应该如何转发service的流量。

BGP 模式 优点 与 缺点：

优点：

- BGP模式下才是一个真正的 LoadBalancer，通过BGP协议正确分布流量，不再需要一个Leader节点。

缺点：

- 不能优雅处理故障转移，当持有服务的节点宕掉后，所有活动连接的客户端将收到 Connection reset by peer。
- 需要上层路由器支持BGP。而且因为BGP单session的限制，如果Calico也是使用的BGP模式，就会有冲突从而导致metallb无法正常工作。

## MetalLB 环境要求

`MetalLB` 需要以下环境才能运行：

- Kubernetes 1.13.0 版本或更高版本的集群。
- Kubernetes 集群网络组件需要支持 `MetalLB` 服务，具体参考: https://metallb.universe.tf/installation/network-addons/
- `MetalLB` 需要能分配IPv4地址。
- 根据操作模式的不同，可能需要一个或多个能够使用[BGP](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)的路由器。

MetalLB 目前支持网络插件范围：

网络插件 | 兼容性
---|---
Calico | 部分支持（[有附加条件](https://metallb.universe.tf/configuration/calico/)）
Canal | 支持
Cilium | 支持
Flannel | 支持
Kube-router | 部分支持（[有附加条件](https://metallb.universe.tf/configuration/kube-router/)）
Romana | 部分支持（[有附加条件](https://metallb.universe.tf/configuration/romana/)）
Weave Net | 部分支持（[有附加条件](https://metallb.universe.tf/configuration/weave/)）

> MetalLB 可以在Kubenetes 1.13 或更高版本的 Kube-Proxy 中使用 IPVS 模式。但是,它尚未明确测试，因此风险自负。具体内容可参考：https://github.com/google/metallb/issues/153

## MetalLB 部署

### 注意

如果环境是 Kubernetes v1.14.2+ 使用 IPVS模式，必须启用ARP模式。

编辑集群中kube-proxy配置

```bash
$ kubectl edit configmap -n kube-system kube-proxy
```

下面是具体设置

```yaml
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: "ipvs"
ipvs:
  strictARP: true
```


### 使用 YAML 文件部署

```bash
# 安装目前最新版本 v0.9.3

# 创建 namespaces
$ kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.9.3/manifests/namespace.yaml

# 首次安装需要设置 memberlist secret
$ kubectl create secret generic -n metallb-system memberlist --from-literal=secretkey="$(openssl rand -base64 128)"

# 部署
$ kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.9.3/manifests/metallb.yaml

# 查看
$ kubectl  get svc,pod -n metallb-system

NAME                              READY   STATUS    RESTARTS   AGE
pod/controller-57f648cb96-2pfq6   1/1     Running   0          5m42s
pod/speaker-l6xh2                 1/1     Running   0          5m35s
pod/speaker-pmd42                 1/1     Running   0          5m39s
```

部署完，YAML 文件中主要包含以下一些组件：

- `metallb-system/controller`：负责IP地址的分配，以及service和endpoint的监听
- `metallb-system/speaker`：负责保证service地址可达，例如Layer 2模式下，speaker会负责ARP请求应答
- `Controller` 和 `Speaker` 的 `Service Accounts`，以及组件需要运行的 `RBAC` 权限。

> 注意，部署后，还需要根据具体的地址通告方式，配置 configmap `metallb-system/config`。controller 会读取该configmap，并reload配置。

### 使用 Helm 部署

```bash
$ helm install --name metallb stable/metallb
```

> 通过 Helm 安装时，MetalLB 读取的 ConfigMap 名为 metallb-config 。

## 配置 MetalLB

### 配置 MetalLB 为 Layer 2模式 （使用 yaml 文件部署）

```bash
$ vim MetalLB-Layer2-Configmap.yaml
```

```yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: config
  namespace: metallb-system
data:
  config: |
    address-pools:
    - name: default
      protocol: layer2
      addresses:
      - 192.168.0.100-192.168.0.200
```

上面际例子，将配置一个由 MetalLB 二层模式控制的 service 外部 IP 段为 192.168.0.100 - 192.168.0.200。

> 注意：IP段根据自己实际情况来设置

```bash
# 部署 configmap
$ kubectl apply -f MetalLB-Layer2-Configmap.yaml
```

#### 测试

下面我们创建一个服务类型为 `LoadBalancer` 的 Nginx 服务 Demo 来演示

```bash
$ vim demo1.deploy.yml
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: demo1
  namespace: default
  labels:
    app: demo1
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: http
      protocol: TCP
      name: http
  selector:
    app: demo1

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo1-deployment
  namespace: default
  labels:
    app: demo1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: demo1
  template:
    metadata:
      labels:
        app: demo1
    spec:
      containers:
      - name: demo1
        image: mritd/demo
        ports:
          - name: http
            containerPort: 80
            protocol: TCP
```

```bash
# 部署
$ kubectl apply -f demo1.deploy.yml

# 查看
kubectl  get svc,pod -n default

NAME                 TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)        AGE
service/demo1        LoadBalancer   10.10.241.163   192.168.0.100   80:39916/TCP   34s

NAME                                    READY   STATUS    RESTARTS   AGE
pod/demo1-deployment-64f769965b-m28cn   1/1     Running   0          34s
pod/demo1-deployment-64f769965b-wp2gg   1/1     Running   0          34s
```

从输出结果，可以看到 `LoadBalancer` 类型的服务，并且分配外部 IP 地址是地址池中的第一个 IP `192.168.0.100`。

直接访问下 LoadBalancer IP `192.168.0.100`，下面访问成功。

```bash
$ wget -SO /dev/null 192.168.0.100

--2020-06-04 20:52:03--  http://192.168.0.100/
正在连接 192.168.0.100:80... 已连接。
已发出 HTTP 请求，正在等待回应...
  HTTP/1.1 200 OK
  Server: nginx/1.17.1
  Date: Thu, 04 Jun 2020 12:52:03 GMT
  Content-Type: text/html
  Content-Length: 557
  Last-Modified: Sun, 28 Apr 2019 12:25:48 GMT
  Connection: keep-alive
  ETag: "5cc59bcc-22d"
  Accept-Ranges: bytes
长度：557 [text/html]
正在保存至: “/dev/null”

100%[===========================================================================================================================================>] 557         --.-K/s 用时 0s

2020-06-04 18:52:03 (205 MB/s) - 已保存 “/dev/null” [557/557])
```

### 配置 MetalLB 为 BGP 模式

test

## 参考链接

- https://mp.weixin.qq.com/s/Z49-5WlhfmxKscmjoZk52Q
- https://zhuanlan.zhihu.com/p/103717169