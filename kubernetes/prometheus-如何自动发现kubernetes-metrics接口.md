## 前提
很多同学搭建完`Prometheus Operator`后，并不知道`Prometheus`是如何发现`Kubernetes`提供的`Metrics`接口

## Prometheus 配置方式有两种
- `命令行:` 用来配置不可变命令参数，主要是Prometheus运行参数，比如数据存储位置、数据存储时长 (命令行这里就不讲了)
- `配置文件:` 用来配置Prometheus应用参数，比如数据采集、报警对接

## 服务重载方式
- 对进程发送信号`SIGHUP`
- `HTTP POST`请求，需要开启`--web.enable-lifecycle`选项，`curl -X POST http://localhost:9091/-/reload`

## 配置文件
使用`yaml`格式，下面是文件中一级配置项。自动发现`K8s Metrics`接口是通过`scrape_configs:`配置
```yaml
＃全局配置
global:

＃规则配置主要是配置报警规则
rule_files:

＃抓取配置，主要配置抓取客户端相关
scrape_configs:

＃报警配置
alerting:

＃用于远程存储写配置
remote_write:

＃用于远程读配置
remote_read:
```

## 举例说明
下面是获取`Pod`中`metrics`接口例子，同理`Prometheus`可以用这种类似的方式获取   Kubernetes `kube-apiserver、kube-controller-manager、kube-scheduler`等组件 Metrics 数据

- Kubernetes Deployment 配置
```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: hello
  namespace: test
  labels:
    app: hello
    name: hello
spec:
  strategy:
    type: RollingUpdate
  revisionHistoryLimit: 3
  template:
    metadata:
      labels:
        app: hello
        name: hello
      annotations:
        prometheus.io/scrape: 'true'
        prometheus.io/path: '/metrics'
        prometheus.io/port: '8080'
    spec:
      containers:
      - name: hello
        image: hello:v1
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
```

- Prometheus yaml 配置
```yaml
global:
  # 间隔时间
  scrape_interval: 30s
  # 超时时间
  scrape_timeout: 10s
  # 另一个独立的规则周期，对告警规则做定期计算
  evaluation_interval: 30s
  # 外部系统标签
  external_labels:
    prometheus: monitoring/k8s
    prometheus_replica: prometheus-k8s-1

# 拉取数据配置，在配置字段内可以配置拉取数据的对象(Targets)，job以及实例
scrape_configs: 
  # 定义job名称，是一个拉取单元 
  - job_name: hello-metrics
    # Prometheus支持的服务发现类，还支持很多种，具体这里不展示
    kubernetes_sd_configs:
    # 角色为pod
    - role: pod
      # 只针对 test namespaces
      namespaces:
        names:
        - test
    # 重新贴标签
    relabel_configs:
    # 源标签
    - source_labels:
      # 匹配来自 pod annotationname prometheus.io/scrape 字段
      - __meta_kubernetes_pod_annotation_prometheus_io_scrape
      # 动作 删除 regex 与串联不匹配的目标 source_labels
      action: keep
      # 通过正式表达式匹配 true
      regex: true
    - source_labels:
      # 匹配来自 pod annotationname prometheus.io/path 字段
      - __meta_kubernetes_pod_annotation_prometheus_io_path
      # regex与串联的匹配source_labels。然后，设置 target_label于replacement与匹配组的引用（${1}，${2}，...）中replacement可以通过值取代。如果regex 不匹配，则不会进行替换
      action: replace
      # 匹配目标指标路径
      target_label: __metrics_path__
      # 匹配全路径
      regex: (.+)
    - source_labels:
      # 匹配出 Pod ip地址和 Port
      - __address__
      - __meta_kubernetes_pod_annotation_prometheus_io_port
      action: replace
      regex: ([^:]+)(?::\d+)?;(\d+)
      replacement: $1:$2
      target_label: __address__
    - source_labels:
      # 元标签 服务对象的名称空间
      - __meta_kubernetes_namespace
      action: replace
      target_label: kubernetes_namespace
    - source_labels:
      # pod对象的名称
      - __meta_kubernetes_pod_name
      action: replace
      target_label: kubernetes_pod_name
```

- 从上面配置可以得出结论， Prometheus 是通过 K8S Deployment 配置中 `Pod annotations` 来匹配出 `Metrics URL 接口`。 例： `http://172.16.10.7:8080/metrics`


## 总结
Prometheus 可以通过匹配 `Pod annotations` 来获取想要的信息，这只是一种方法。还有其它方法，比如通过 `Kubernetes label`、`Kubernetes endpoints`、`Kubernetes service`等

## 参考文档
- 官方文档 https://prometheus.io/docs/prometheus/latest/configuration/configuration/
- Prometheus 配置详解 https://www.li-rui.top/2018/11/12/monitor/Prometheus%20%E9%85%8D%E7%BD%AE%E8%AF%A6%E8%A7%A3/