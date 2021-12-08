## 阿里云ACK是什么

阿里云容器服务Kubernetes版（Alibaba Cloud Container Service for Kubernetes，简称容器服务ACK）是全球首批通过Kubernetes一致性认证的服务平台，提供高性能的容器应用管理服务，支持企业级Kubernetes容器化应用的生命周期管理，让您轻松高效地在云端运行Kubernetes容器化应用。

## Service几种暴露方式

Kubernetes Service 支持下面一些暴露方式：

- `NodePort`：通过每个节点上的 IP 和静态端口（NodePort）暴露服务。 NodePort 服务会路由到自动创建的 ClusterIP 服务。 通过请求 <节点 IP>:<节点端口>，你可以从集群的外部访问一个 NodePort 服务。
- `hostNetwork: true`：Pod中运行的应用程序可以直接看到pod启动主机网络接口。
- `hostPort`：是直接将容器端口与所调度节点上的端口路由，这样用户就可以通过宿主机IP加端口来访问Pod。
- `LoadBalancer`：使用云提供商的负载均衡器向外部暴露服务。 外部负载均衡器可以将流量路由到自动创建的 NodePort 服务和 ClusterIP 服务上。
- `ExternalName`：通过返回 CNAME 和对应值，可以将服务映射到 externalName 字段的内容（例如，foo.bar.example.com）。 无需创建任何类型代理。
- `Ingress`：是自kubernetes1.1版本后引入的资源类型。必须要部署Ingress controller才能创建Ingress资源，Ingress controller是以一种插件的形式提供。Ingress controller 是部署在Kubernetes之上的Docker容器。它的Docker镜像包含一个像nginx或HAProxy的负载均衡器和一个控制器守护进程。控制器守护程序从Kubernetes接收所需的Ingress配置。它会生成一个nginx或HAProxy配置文件，并重新启动负载平衡器进程以使更改生效。换句话说，Ingress controller是由Kubernetes管理的负载均衡器。

## 需求

使用阿里云`ACK容器服务`时，我们Service默认就支持缓存`LoadBalancer`，大家有可能第一种念想，每个Service绑定一个SLB，这样会不会太浪费SLB。也可以通过`Ingress`来实现外部用户访问K8S集群内部。

Ingress是可以实现，但如果我们业务中有很多不是80或者443端口访问的，并且还在一个域名，比如下面：

- www.example.com:8888
- www.example.com:8080
- www.example.com:8081

这种一般不推荐使用Ingress来实现，因为这样Ingress会开放很多端口，以后不便于维护。

那有没有在SLB充分利用前提下，实现上面的需求。方法当然有的，`阿里云ACK支持多个Service绑定一个SLB多个端口`。

## 多个Service绑定一个SLB多个端口用法

> PS: `前提条件`：需要提前在SLB控制台创建SLB，SLB需要和K8S在同一个VPC网络下

### Service声明TCP协议

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-force-override-listeners: "true"
    # 仅支持TCP和UDP协议。如需设置连接优雅中断，以下两项Annotation必选
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-connection-drain: "on"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-connection-drain-timeout: "30"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-delete-protection: "on"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-modification-protection: "ConsoleProtection"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-id: "slb-id"
    # ACK是Terway网络模式下，通过annotation：service.beta.kubernetes.io/backend-type："eni"将Pod直接挂载到SLB后端，提升网络转发性能。
    service.beta.kubernetes.io/backend-type: "eni"
  name: nginx
spec:
  externalTrafficPolicy: Cluster
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: nginx
  type: LoadBalancer
```

### Service声明使用https协议

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-protocol-port: "https:8888"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-health-check-flag: "on"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-health-check-type: "http"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-health-check-uri: "/health"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-healthy-threshold: "4"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-unhealthy-threshold: "4"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-health-check-timeout: "10"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-health-check-interval: "3"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-cert-id: "证书id"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-force-override-listeners: "true"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-delete-protection: "on"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-modification-protection: "ConsoleProtection"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-id: "slb-id"
    # ACK是Terway网络模式下，通过annotation：service.beta.kubernetes.io/backend-type："eni"将Pod直接挂载到SLB后端，提升网络转发性能。
    service.beta.kubernetes.io/backend-type: eni
  name: nginx
spec:
  externalTrafficPolicy: Cluster
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: nginx
  type: LoadBalancer
```

### Service声明使用http协议

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-protocol-port: "http:8080"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-health-check-flag: "on"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-health-check-type: "http"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-health-check-uri: "/health"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-healthy-threshold: "4"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-unhealthy-threshold: "4"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-health-check-timeout: "10"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-health-check-interval: "3"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-force-override-listeners: "true"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-delete-protection: "on"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-modification-protection: "ConsoleProtection"
    service.beta.kubernetes.io/alibaba-cloud-loadbalancer-id: "slb-id"
    # ACK是Terway网络模式下，通过annotation：service.beta.kubernetes.io/backend-type："eni"将Pod直接挂载到SLB后端，提升网络转发性能。
    service.beta.kubernetes.io/backend-type: eni
  name: nginx
  namespace: default
spec:
  externalTrafficPolicy: Cluster
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    run: nginx
  type: LoadBalancer
```

## 参考链接

- https://help.aliyun.com/document_detail/86531.html?spm=5176.21213303.J_6704733920.7.c5983eda1xJwdH&scm=20140722.S_help%40%40%E6%96%87%E6%A1%A3%40%4086531.S_0%2Bos0.ID_86531-RL_serviceDOTbetaDOTkubernetes-OR_helpmain-V_2-P0_0
- https://help.aliyun.com/document_detail/181517.html
- https://kubernetes.io/zh/docs/concepts/services-networking/service/#externalname