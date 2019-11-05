# 一、prometheus-operator 介绍和功能

## prometheus-operator 介绍
当今Cloud Native概念流行，对于容器、服务、节点以及集群的监控变得越来越重要。Prometheus 作为 Kubernetes 监控的事实标准，有着强大的功能和良好的生态。但是它不支持分布式，不支持数据导入、导出，不支持通过 API 修改监控目标和报警规则，所以在使用它时，通常需要写脚本和代码来简化操作。

Prometheus Operator 为监控 Kubernetes service、deployment、daemonsets 和 Prometheus 实例的管理提供了简单的定义等，简化在 Kubernetes 上部署、管理和运行 Prometheus 和 Alertmanager 集群。

## prometheus-operator 功能
1. `创建/销毁`：在 Kubernetes namespace 中更加容易地启动一个 Prometheues 实例，一个特定应用程序或者团队可以更容易使用 Prometheus Operator。
2. `便捷配置`：通过 Kubernetes 资源配置 Prometheus 的基本信息，比如版本、存储、副本集等。
3. `通过标签标记目标服务`： 基于常见的 Kubernetes label 查询自动生成监控目标配置；不需要学习 Prometheus 特定的配置语言。


# 二、下载 prometheus-operator 配置

## 下载官方prometheus-operator v0.29.0版本代码，官方把所有文件都放在一起，这里我分类下
```
$ git clone https://github.com/coreos/prometheus-operator.git -b release-0.29
$ cd contrib/kube-prometheus/manifests/

# 新建对应的服务目录
$ mkdir -p operator node-exporter alertmanager grafana kube-state-metrics prometheus serviceMonitor adapter

# 把对应的服务配置文件移动到相应的服务目录
$ mv *-serviceMonitor* serviceMonitor/
$ mv 0prometheus-operator* operator/
$ mv grafana-* grafana/
$ mv kube-state-metrics-* kube-state-metrics/
$ mv alertmanager-* alertmanager/
$ mv node-exporter-* node-exporter/
$ mv prometheus-adapter* adapter/
$ mv prometheus-* prometheus/

# 新创建了两个目录，存放钉钉配置和其它配置
mkdir other dingtalk-hook
```
 
上面配置都存放到我个人github私有仓库中 `https://github.com/yangpeng14/prometheus-operator-configure`


# 三、部署operator

## 默认镜像下载需要翻墙，下面是提供我个人的dockerhub地址
官方镜像地址 | 个人 DockerHub 地址
---|---
quay.io/coreos/configmap-reload:v0.0.1             | yangpeng2468/configmap-reload:v0.0.1
quay.io/coreos/k8s-prometheus-adapter-amd64:v0.4.1 | yangpeng2468/k8s-prometheus-adapter-amd64:v0.4.1
quay.io/coreos/kube-rbac-proxy:v0.4.1              | yangpeng2468/kube-rbac-proxy:v0.4.1
quay.io/coreos/kube-state-metrics:v1.5.0           | yangpeng2468/kube-state-metrics:v1.5.0
quay.io/prometheus/prometheus:latest               | yangpeng2468/prometheus:latest
quay.io/prometheus/node-exporter:v0.17.0           | yangpeng2468/node-exporter:v0.17.0
quay.io/coreos/prometheus-operator:v0.29.0         | yangpeng2468/prometheus-operator:v0.29.0
quay.io/coreos/prometheus-config-reloader:v0.29.0  | yangpeng2468/prometheus-config-reloader:v0.29.0
quay.io/prometheus/prometheus:v2.7.2               | yangpeng2468/prometheus:v2.7.2
quay.io/prometheus/alertmanager:v0.16.1            | yangpeng2468/alertmanager:v0.16.1
k8s.gcr.io/addon-resizer:1.8.4                     | yangpeng2468/addon-resizer:1.8.4


## 首先创建namespace monitoring
`kubectl apply -f 00namespace-namespace.yaml`
 
## 部署operator
`kubectl apply -f operator/`
 
## 查看是否正常部署
```bash
$ kubectl -n monitoring get pod

NAME                                   READY     STATUS    RESTARTS   AGE
prometheus-operator-56954c76b5-qm9ww   1/1       Running   0          24s
```
 
## 查看是否正常部署自定义资源定义(CRD)
```bash
$ kubectl get crd -n monitoring

NAME                                    CREATED AT
alertmanagers.monitoring.coreos.com     2019-04-16T06:22:20Z
prometheuses.monitoring.coreos.com      2019-04-16T06:22:20Z
prometheusrules.monitoring.coreos.com   2019-04-16T06:22:20Z
servicemonitors.monitoring.coreos.com   2019-04-16T06:22:21Z
```

# 四、部署整套CRD

```
# 把etcd证书保存到secrets中
kubectl -n monitoring create secret generic etcd-certs --from-file=/opt/kubernetes/ssl/server.pem --from-file=/opt/kubernetes/ssl/server-key.pem --from-file=/opt/kubernetes/ssl/ca.pem
 
# 加载自定义配置
cd other
kubectl create secret generic additional-configs --from-file=prometheus-additional.yaml -n monitoring
 
kubectl apply -f adapter/
kubectl apply -f alertmanager/
kubectl apply -f node-exporter/
kubectl apply -f kube-state-metrics/
kubectl apply -f grafana/
kubectl apply -f prometheus/
kubectl apply -f serviceMonitor/
 
 
# 查看是否正常部署
kubectl -n monitoring get all -o wide
```

# 五、部署遇到的坑

## 坑一
`二进制部署k8s管理组件和新版本kubeadm部署的都会发现在prometheus server的页面上发现kube-controller和kube-schedule的target为0/0。因为serviceMonitor是根据label去选取svc的，可以查看对应的serviceMonitor是选取的ns范围是kube-system`

```
# 解决方法
kubectl apply -f other/kube-controller-manager-svc-ep.yaml
kubectl apply -f other/kube-scheduler-svc-ep.yaml

# vim kube-controller-manager-svc-ep.yaml
apiVersion: v1
kind: Service
metadata:
  namespace: kube-system
  name: kube-controller-manager
  labels:
    k8s-app: kube-controller-manager
spec:
  type: ClusterIP
  clusterIP: None
  ports:
  - name: http-metrics
    port: 10252
    targetPort: 10252
    protocol: TCP

---
apiVersion: v1
kind: Endpoints
metadata:
  labels:
    k8s-app: kube-controller-manager
  name: kube-controller-manager
  namespace: kube-system
subsets:
- addresses:
  - ip: 172.16.3.9   # master ip 地址
  ports:
  - name: http-metrics
    port: 10252
    protocol: TCP
    
# vim kube-scheduler-svc-ep.yaml
apiVersion: v1
kind: Service
metadata:
  namespace: kube-system
  name: kube-scheduler
  labels:
    k8s-app: kube-scheduler
spec:
  type: ClusterIP
  clusterIP: None
  ports:
  - name: http-metrics
    port: 10251
    targetPort: 10251
    protocol: TCP

---
apiVersion: v1
kind: Endpoints
metadata:
  labels:
    k8s-app: kube-scheduler
  name: kube-scheduler
  namespace: kube-system
subsets:
- addresses:
  - ip: 172.16.3.9 # master ip 地址
  ports:
  - name: http-metrics
    port: 10251
    protocol: TCP
```

## 坑二
`访问prometheus server的web页面发现即使创建了svc和注入对应ep的信息在target页面还是被prometheus server请求被拒绝`

1. 修改  kube-controller-manager 配置文件
`把 --address=127.0.0.1 换成  --address=0.0.0.0`
 
2. 修改 kube-scheduler 配置文件
`把 --address=127.0.0.1 换成  --address=0.0.0.0`
 
3. 修改完后重启这两个服务


## 坑三
`prometheus targets 页面查看  monitoring/coredns/0 没有监控项，是因为 kube-dns service中没有设置监控端口 9153`

```
# 解决方法 添加监控端口 9153

$ kubectl edit svc -n kube-system kube-dns
 
  - name: metrics
    port: 9153
    protocol: TCP
    targetPort: 9153
```

# 六、数据持续存储、监控etcd集群、监控自动发化、自定义报警

## 参考下面文章链接配置
1. 自定义报警

`使用钉钉推送消息安装配置方法` https://github.com/yangpeng14/prometheus-operator-configure/tree/master/dingtalk-hook

2. 自定义报警

`配置自定义报警配置并加载` https://www.qikqiak.com/post/prometheus-operator-custom-alert/
```bash
# 创建配置
$ vim prometheus-additional.yaml

- job_name: 'crm'
  scrape_interval: 5s
  metrics_path: '/api/private/metrics'
  static_configs:
    - targets: ['www.example.com']

# 加载配置
$ kubectl create secret generic additional-configs --from-file=prometheus-additional.yaml -n monitoring

# 钉钉推送消息安装配置方法
https://github.com/yangpeng14/prometheus-operator-configure/tree/master/dingtalk-hook
```

3. prometheus 和 alertmanager 使用NFS存储

`Prometheus Operator 自动发现以及数据持久化` https://www.qikqiak.com/post/prometheus-operator-advance/ 


预先安装 nfs 和 nfs-client-provisioner

`nfs-client-provisioner 安装配置` https://github.com/yangpeng14/prometheus-operator-configure/tree/master/nfs-client-provisioner


4. 监控etcd

`Prometheus Operator 监控 etcd 集群` https://www.qikqiak.com/post/prometheus-operator-monitor-etcd/

集群是二进制方式独立部署的 etcd 集群，同样将对应的证书保存到集群中的一个 secret 对象中去即可

`kubectl -n monitoring create secret generic etcd-certs --from-file=/opt/kubernetes/ssl/server.pem --from-file=/opt/kubernetes/ssl/server-key.pem --from-file=/opt/kubernetes/ssl/ca.pem`