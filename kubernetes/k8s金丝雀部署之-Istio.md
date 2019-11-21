## 什么是金丝雀发布?
`金丝雀发布（Canary）`：也是一种发布策略，和国内常说的灰度发布是同一类策略。蓝绿部署是准备两套系统，在两套系统之间进行切换，金丝雀策略是只有一套系统，逐渐替换这套系统。

## 什么是 Istio ?
使用云平台可以为组织提供丰富的好处。然而，不可否认的是，采用云可能会给 DevOps 团队带来压力。开发人员必须使用微服务以满足应用的可移植性，同时运营商管理了极其庞大的混合和多云部署。Istio 允许您`连接、保护、控制和观测服务`。

在较高的层次上，Istio 有助于降低这些部署的复杂性，并减轻开发团队的压力。它是一个完全开源的服务网格，可以透明地分层到现有的分布式应用程序上。它也是一个平台，包括允许它集成到任何日志记录平台、遥测或策略系统的 API。Istio 的多样化功能集使您能够成功高效地运行分布式微服务架构，并提供保护、连接和监控微服务的统一方法。

## 为什么要使用 Istio ?
Istio 提供一种简单的方式来为已部署的服务建立网络，该网络具有负载均衡、服务间认证、监控等功能，只需要对服务的代码进行一点或不需要做任何改动。想要让服务支持 Istio，只需要在您的环境中部署一个特殊的 sidecar 代理，使用 Istio 控制平面功能配置和管理代理，拦截微服务之间的所有网络通信：

- HTTP、gRPC、WebSocket 和 TCP 流量的自动负载均衡。
- 通过丰富的路由规则、重试、故障转移和故障注入，可以对流量行为进行细粒度控制。
- 可插入的策略层和配置 API，支持访问控制、速率限制和配额。
- 对出入集群入口和出口中所有流量的自动度量指标、日志记录和追踪。
- 通过强大的基于身份的验证和授权，在集群中实现安全的服务间通信。

Istio 旨在实现可扩展性，满足各种部署需求

## Istio 架构
Istio 服务网格逻辑上分为`数据平面`和`控制平面`。

- `数据平面`：由一组以 sidecar 方式部署的智能代理`（Envoy）`组成。这些代理可以调节和控制微服务及 `Mixer `之间所有的网络通信。
- `控制平面`：负责管理和配置代理来路由流量。此外控制平面配置 Mixer 以`实施策略`和`收集遥测数据`。

下图显示了构成每个面板的不同组件：
![](https://www.yp14.cn/img/istio.png)


## Istio 金丝雀部署

- 定义 service 服务
```yaml
apiVersion: v1
kind: Service
metadata:
  name: demo4
  namespace: test1
  labels:
    app: demo4
spec:
  ports:
    - port: 80
      targetPort: http
      protocol: TCP
      name: http
  selector:
    app: demo4
```

- 定义两个版本的 deploy 文件，两个版本都包含服务选择标签 app：demo4
```yaml
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  name: demo4-deployment-v1
  namespace: test1
spec:
  replicas: 1
  template:
    metadata:
      annotations:
        # 允许注入 sidecar
        sidecar.istio.io/inject: "true"
      labels:
        app: demo4
        version: v1
    spec:
      containers:
      - name: demo4-v1
        image: mritd/demo
        livenessProbe:
          httpGet:
            path: /
            port: 80
            scheme: HTTP
          initialDelaySeconds: 30
          timeoutSeconds: 5
          periodSeconds: 10
          successThreshold: 1
          failureThreshold: 5
        readinessProbe:
          httpGet:
            path: /
            port: 80
            scheme: HTTP
          initialDelaySeconds: 30
          timeoutSeconds: 5
          periodSeconds: 10
          successThreshold: 1
          failureThreshold: 5
        ports:
          - name: http
            containerPort: 80
            protocol: TCP

---

apiVersion: apps/v1beta1
kind: Deployment
metadata:
  name: demo4-deployment-v2
  namespace: test1
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: demo4
        version: v2
      annotations:
        sidecar.istio.io/inject: "true"
    spec:
      containers:
      - name: demo4-v2
        image: mritd/demo
        livenessProbe:
          httpGet:
            path: /
            port: 80
            scheme: HTTP
          initialDelaySeconds: 30
          timeoutSeconds: 5
          periodSeconds: 10
          successThreshold: 1
          failureThreshold: 5
        readinessProbe:
          httpGet:
            path: /
            port: 80
            scheme: HTTP
          initialDelaySeconds: 30
          timeoutSeconds: 5
          periodSeconds: 10
          successThreshold: 1
          failureThreshold: 5
        ports:
          - name: http
            containerPort: 80
            protocol: TCP
```

上面定义和普通k8s定义蓝绿部署是一样的


- 设置路由规则来控制流量分配。如将 10％ 的流量发送到金丝雀版本（v2）。后面可以渐渐的把所有流量都切到金丝雀版本（v2），只需要修改`weight: 10`参数，注意`v1和v2版本和一定要等于100`

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: demo4-vs
  namespace: test1
spec:
  hosts:
  - demo4.a.com
  gateways:
  - demo4-gateway
  http:
  - route:
    - destination:
        host: demo4.test1.svc.cluster.local
        subset: v1
      weight: 90
    - destination:
        host: demo4.test1.svc.cluster.local
        subset: v2
      weight: 10

---

apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: demo4
  namespace: test1
spec:
  host: demo4.test1.svc.cluster.local
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

当规则设置生效后，Istio 将确保只有 `10%` 的请求发送到金丝雀版本，无论每个版本的运行副本数量是多少。

## 高层次的金丝雀部署

- 只允许特定网站上`50％`的用户流量路由到金丝雀（v2）版本，而其他用户则不受影响

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: demo4-vs
  namespace: test1
spec:
  hosts:
  - demo4.a.com
  gateways:
  - demo4-gateway
  http:
  - match:
    - headers:
        cookie:
          regex: "^(.*?;)?(email=[^;]*@some-company-name.com)(;.*)?$"
    route:
    - destination:
        host: demo4.test1.svc.cluster.local
        subset: v1
        weight: 50
    - destination:
        host: demo4.test1.svc.cluster.local
        subset: v2
        weight: 50
  - route:
    - destination:
        host: demo4.test1.svc.cluster.local
        subset: v1
```

## VirtualService 与 DestinationRule 解释
- Istio Virtual Service，用于控制当前deployment和金丝雀deployment流量分配的权重
- Istio Destination Rule，包含当前deployment和金丝雀deployment的子集（subset）
- Istio Gateway（可选），如果服务需要从容器集群外被访问则需要搭建gateway

## 总结
本文中，我们看到了 Istio 如何支持通用可扩展的金丝雀部署。Istio 服务网格提供了管理流量分配所需的基础控制，并完全独立于部署缩放。这允许简单而强大的方式来进行金丝雀测试和上线。

支持金丝雀部署的智能路由只是 Istio 的众多功能之一，它将使基于大型微服务的应用程序的生产部署变得更加简单。查看 `istio.io` 了解更多信息。

## 参考链接
- https://archive.istio.io/v1.2/zh/docs/concepts/what-is-istio/
- https://archive.istio.io/v1.2/zh/docs/tasks/traffic-management/request-routing/
- https://archive.istio.io/v1.2/zh/blog/2017/0.1-canary/