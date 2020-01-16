## Prometheus 监控简介

`Prometheus` 监控分为两种：

- `白盒监控`
- `墨盒监控`


`白盒监控`：是指我们日常监控主机的资源用量、容器的运行状态、数据库中间件的运行数据。 这些都是支持业务和服务的基础设施，通过白盒能够了解其内部的实际运行状态，通过对监控指标的观察能够预判可能出现的问题，从而对潜在的不确定因素进行优化。

`墨盒监控`：即以用户的身份测试服务的外部可见性，常见的黑盒监控包括 `HTTP探针`、`TCP探针`、`Dns`、`Icmp`等用于检测站点、服务的可访问性、服务的连通性，以及访问效率等。

`两者比较`：黑盒监控相较于白盒监控最大的不同在于黑盒监控是以故障为导向当故障发生时，黑盒监控能快速发现故障，而白盒监控则侧重于主动发现或者预测潜在的问题。一个完善的监控目标是要能够从白盒的角度发现潜在问题，能够在黑盒的角度快速发现已经发生的问题。

## 部署 Prometheus Blackbox 服务

### 环境：

- Prometheus Operator 版本 v0.29.0（[手动部署](https://www.yp14.cn/2019/08/29/prometheus-operator%E6%89%8B%E5%8A%A8%E9%83%A8%E7%BD%B2/)）
- Kubernetes 版本 1.15.6 （二进制部署）
- Blackbox Exporter 版本 v0.16.0

### Blackbox Exporter 部署

> `Exporter Configmap` 定义，可以参考下面两个链接 
https://github.com/prometheus/blackbox_exporter/blob/master/CONFIGURATION.md
https://github.com/prometheus/blackbox_exporter/blob/master/example.yml

首先得声明一个 Blackbox 的 Deployment，并利用 Configmap 来为 Blackbox 提供配置文件。

```
$ vim prometheus-blackbox.yaml
```

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: blackbox-config
  namespace: monitoring
data:
  blackbox.yml: |-
    modules:
      http_2xx:  # http 检测模块  Blockbox-Exporter 中所有的探针均是以 Module 的信息进行配置
        prober: http
        timeout: 10s
        http:
          valid_http_versions: ["HTTP/1.1", "HTTP/2"]
          valid_status_codes: [200]  # 默认 2xx，这里定义一个返回状态码，在grafana作图时，有明示。
          method: GET
          headers:
            Host: prometheus.smartstudy.tech
            Accept-Language: en-US
            Origin: smartstudy.tech
          preferred_ip_protocol: "ip4" # 首选IP协议
          no_follow_redirects: false # 关闭跟随重定向
      http_post_2xx: # http post 监测模块
        prober: http
        timeout: 10s
        http:
          valid_http_versions: ["HTTP/1.1", "HTTP/2"]
          method: POST
          # post 请求headers, body 这里可以不声明
          headers:  # 使用 json 格式
            Content-Type: application/json
          body: '{"text": "hello"}'
          preferred_ip_protocol: "ip4"
      tcp_connect:  # TCP 检测模块
        prober: tcp
        timeout: 10s
      dns_tcp:  # DNS 通过TCP检测模块
        prober: dns
        dns:
          transport_protocol: "tcp"  # 默认是 udp
          preferred_ip_protocol: "ip4"  # 默认是 ip6
          query_name: "kubernetes.default.svc.cluster.local" # 利用这个域名来检查 dns 服务器
          # query_type: "A"  # 如果是 kube-dns ，一定要加入这个，因为不支持Ipv6
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blackbox
  namespace: monitoring
spec:
  replicas: 1
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app: blackbox
  strategy:
    rollingUpdate:
      maxSurge: 30%
      maxUnavailable: 30%
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: blackbox
    spec:
      containers:
      - image: prom/blackbox-exporter:v0.16.0
        name: blackbox
        args:
        - --config.file=/etc/blackbox_exporter/blackbox.yml # ConfigMap 中的配置文件
        - --log.level=info  # 日志级别，可以把级别调到 error
        ports:
        - containerPort: 9115
        volumeMounts:
        - name: config
          mountPath: /etc/blackbox_exporter
      volumes:
      - name: config
        configMap:
          name: blackbox-config
---
apiVersion: v1
kind: Service
metadata:
  name: blackbox
  namespace: monitoring
spec:
  selector:
    app: blackbox
  ports:
  - port: 9115
    targetPort: 9115
```

```bash
# 部署
$ kubectl apply -f prometheus-blackbox.yaml

configmap/blackbox-config created
deployment.apps/blackbox created
service/blackbox created
```

## 定义 BlackBox 在 Prometheus 抓取设置

> 下面抓取设置，都存放在 `prometheus-additional.yaml` 文件中，设置可参考 https://github.com/prometheus/prometheus/blob/master/documentation/examples/prometheus-kubernetes.yml

### DNS 监控

```yaml
- job_name: "blackbox-k8s-service-dns"
  scrape_interval: 30s
  scrape_timeout: 10s
  metrics_path: /probe # 不是 metrics，是 probe
  params:
    module: [dns_tcp] # 使用 DNS TCP 模块
  static_configs:
  - targets:
    - kube-dns.kube-system:53  # 不要省略端口号
  relabel_configs:
  - source_labels: [__address__]
    target_label: __param_target
  - source_labels: [__param_target]
    target_label: instance
  - target_label: __address__
    replacement: blackbox:9115  # 服务地址，和上面的 Service 定义保持一致
```

> 更新 `additional-configs secrets`配置 ，`Prometheus` 会自动 reload

```bash
# 先删除，在重新创建
$ kubectl delete secrets -n monitoring additional-configs
$ kubectl create secret generic additional-configs --from-file=prometheus-additional.yaml -n monitoring
```

看到下面输出结果，说明 Prometheus 已重载
![](/img/prometheus-operator-load.png)


打开 Prometheus 的 Target 页面，就会看到 上面定义的 `blackbox-k8s-service-dns` 任务

![](/img/blackbox-k8s-service-dns.png)

### HTTP 监控（K8S 内部发现方法）

> 发现 `Service` 监控

```yaml
- job_name: 'kubernetes-http-services'
  metrics_path: /probe
  params:
    module: [http_2xx]  # 使用定义的http模块
  kubernetes_sd_configs:
  - role: service  # service 类型的服务发现
  relabel_configs:
  # 只有service的annotation中配置了 prometheus.io/http_probe=true 的才进行发现
  - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_http_probe]
    action: keep
    regex: true
  - source_labels: [__address__]
    target_label: __param_target
  - target_label: __address__
    replacement: blackbox:9115
  - source_labels: [__param_target]
    target_label: instance
  - action: labelmap
    regex: __meta_kubernetes_service_label_(.+)
  - source_labels: [__meta_kubernetes_namespace]
    target_label: kubernetes_namespace
  - source_labels: [__meta_kubernetes_service_name]
    target_label: kubernetes_name
```

按上面方法重载 Prometheus，打开 Prometheus 的 Target 页面，就会看到 上面定义的 `blackbox-k8s-http-services` 任务
![](/img/blackbox-k8s-http-services-1.png)

> 自定义发现 `Service` 监控 `端口` 和 `路径`，可以如下设置：

```yaml
- job_name: 'blackbox-k8s-http-services'
  scrape_interval: 30s
  scrape_timeout: 10s
  metrics_path: /probe
  params:
    module: [http_2xx]  # 使用定义的http模块
  kubernetes_sd_configs:
  - role: service  # service 类型的服务发现
  relabel_configs:
  # 只有service的annotation中配置了 prometheus.io/http_probe=true 的才进行发现
  - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_http_probe]
    action: keep
    regex: true
  - source_labels: [__meta_kubernetes_service_name, __meta_kubernetes_namespace, __meta_kubernetes_service_annotation_prometheus_io_http_probe_port, __meta_kubernetes_service_annotation_prometheus_io_http_probe_path]
    action: replace
    target_label: __param_target
    regex: (.+);(.+);(.+);(.+)
    replacement: $1.$2:$3$4
  - target_label: __address__
    replacement: blackbox:9115
  - source_labels: [__param_target]
    target_label: instance
  - action: labelmap
    regex: __meta_kubernetes_service_label_(.+)
  - source_labels: [__meta_kubernetes_namespace]
    target_label: kubernetes_namespace
  - source_labels: [__meta_kubernetes_service_name]
    target_label: kubernetes_name
```

然后，需要在 `Service` 中配置这样的 `annotation` ：

```yaml
annotation:
  prometheus.io/http-probe: "true"
  prometheus.io/http-probe-port: "8080"
  prometheus.io/http-probe-path: "/healthCheck"
```

按上面方法重载 Prometheus，打开 Prometheus 的 Target 页面，就会看到 上面定义的 `blackbox-k8s-http-services` 任务
![](/img/blackbox-k8s-http-services-2.png)

> 发现 Ingress 

```yaml
- job_name: 'blackbox-k8s-ingresses'
  scrape_interval: 30s
  scrape_timeout: 10s
  metrics_path: /probe
  params:
    module: [http_2xx]  # 使用定义的http模块
  kubernetes_sd_configs:
  - role: ingress  # ingress 类型的服务发现
  relabel_configs:
  # 只有ingress的annotation中配置了 prometheus.io/http_probe=true 的才进行发现
  - source_labels: [__meta_kubernetes_ingress_annotation_prometheus_io_http_probe]
    action: keep
    regex: true
  - source_labels: [__meta_kubernetes_ingress_scheme,__address__,__meta_kubernetes_ingress_path]
    regex: (.+);(.+);(.+)
    replacement: ${1}://${2}${3}
    target_label: __param_target
  - target_label: __address__
    replacement: blackbox:9115
  - source_labels: [__param_target]
    target_label: instance
  - action: labelmap
    regex: __meta_kubernetes_ingress_label_(.+)
  - source_labels: [__meta_kubernetes_namespace]
    target_label: kubernetes_namespace
  - source_labels: [__meta_kubernetes_ingress_name]
    target_label: kubernetes_name
```

按上面方法重载 Prometheus，会出现下面报错，报权限不足
![](/img/prometheus-erro.png)

解决方法：在 `prometheus-clusterRole.yaml` 后面添加下面内容

```yaml
- apiGroups:
  - extensions
  resources:
  - ingresses
  verbs:
  - get
  - list
  - watch
```

```bash
$ kubectl apply -f prometheus-clusterRole.yaml
```

打开 Prometheus 的 Target 页面，就会看到 上面定义的 `blackbox-k8s-ingresses` 任务
![](/img/blackbox-k8s-ingresses.png)


### HTTP 监控（监控外部域名）

```yaml
- job_name: "blackbox-external-website"
  scrape_interval: 30s
  scrape_timeout: 15s
  metrics_path: /probe
  params:
    module: [http_2xx]
  static_configs:
  - targets:
    - https://www.example.com # 要检查的网址
    - https://test.example.com
  relabel_configs:
  - source_labels: [__address__]
    target_label: __param_target
  - source_labels: [__param_target]
    target_label: instance
  - target_label: __address__
    replacement: blackbox:9115
```

打开 Prometheus 的 Target 页面，就会看到 上面定义的 `blackbox-external-website` 任务
![](/img/blackbox-external-website.png)

### HTTP Post 监控（监控外部域名）

```yaml
- job_name: 'blackbox-http-post'
  metrics_path: /probe
  params:
    module: [http_post_2xx]
  static_configs:
    - targets:
      - https://www.example.com/api # 要检查的网址
  relabel_configs:
    - source_labels: [__address__]
      target_label: __param_target
    - source_labels: [__param_target]
      target_label: instance
    - target_label: __address__
      replacement: blackbox:9115
```

打开 Prometheus 的 Target 页面，就会看到 上面定义的 `blackbox-http-post` 任务
![](/img/blackbox-http-post.png)

## 小结

Prometheus Blackbox 除了支持对 HTTP 协议进行网络探测以外，Blackbox 还支持对 TCP、DNS、ICMP 等其他网络协议，大家感兴趣的可以从 Blackbox 的 [Github项目](https://github.com/prometheus/blackbox_exporter)中获取更多使用方法。

## 参考链接

- https://github.com/prometheus/blackbox_exporter/blob/master/CONFIGURATION.md
- https://github.com/prometheus/blackbox_exporter/blob/master/example.yml
- https://www.qikqiak.com/post/blackbox-exporter-on-prometheus/
- https://blog.fleeto.us/post/blackbox-monitor-dns-web/