#### 一、下载prometheus-operator配置

---
```
参考链接:
http://www.servicemesher.com/blog/prometheus-operator-manual/
https://github.com/coreos/kube-prometheus/tree/master/manifests   # 官方把手动部署配置迁移到这个地址上，这里没有使用helm部署
```
---

```
# 下载官方prometheus-operator代码，官方把所有文件都放在一起，这里我分类下
git clone https://github.com/coreos/prometheus-operator.git
cd contrib/kube-prometheus/manifests/
mkdir -p operator node-exporter alertmanager grafana kube-state-metrics prometheus serviceMonitor adapter
mv *-serviceMonitor* serviceMonitor/
mv 0prometheus-operator* operator/
mv grafana-* grafana/
mv kube-state-metrics-* kube-state-metrics/
mv alertmanager-* alertmanager/
mv node-exporter-* node-exporter/
mv prometheus-adapter* adapter/
mv prometheus-* prometheus/
 
 
# 上面这些操作文件我都存放在个人github私有仓库中 https://github.com/yangpeng14/prometheus-operator-configure
# 并新创建了两个目录
mkdir other dingtalk-hook
```

#### 二、部署operator
```
# 默认镜像地址需要翻墙，我把默认镜像地址更换成个人在dockerhub地址，下面是对应列表

quay.io/coreos/configmap-reload:v0.0.1              yangpeng2468/configmap-reload:v0.0.1
quay.io/coreos/k8s-prometheus-adapter-amd64:v0.4.1  yangpeng2468/k8s-prometheus-adapter-amd64:v0.4.1
quay.io/coreos/kube-rbac-proxy:v0.4.1               yangpeng2468/kube-rbac-proxy:v0.4.1
quay.io/coreos/kube-state-metrics:v1.5.0            yangpeng2468/kube-state-metrics:v1.5.0
quay.io/prometheus/prometheus:latest                yangpeng2468/prometheus:latest
quay.io/prometheus/node-exporter:v0.17.0            yangpeng2468/node-exporter:v0.17.0
quay.io/coreos/prometheus-operator:v0.29.0          yangpeng2468/prometheus-operator:v0.29.0
quay.io/coreos/prometheus-config-reloader:v0.29.0   yangpeng2468/prometheus-config-reloader:v0.29.0
quay.io/prometheus/prometheus:v2.7.2                yangpeng2468/prometheus:v2.7.2
quay.io/prometheus/alertmanager:v0.16.1             yangpeng2468/alertmanager:v0.16.1
k8s.gcr.io/addon-resizer:1.8.4                      yangpeng2468/addon-resizer:1.8.4

# 首先创建namespace monitoring
kubectl apply -f 00namespace-namespace.yaml
 
 
# 部署operator
kubectl apply -f operator/
 
 
# 查看是否正常部署
$ kubectl -n monitoring get pod
NAME                                   READY     STATUS    RESTARTS   AGE
prometheus-operator-56954c76b5-qm9ww   1/1       Running   0          24s
 
 
# 查看是否正常部署自定义资源定义
$ kubectl get crd -n monitoring
NAME                                    CREATED AT
alertmanagers.monitoring.coreos.com     2019-04-16T06:22:20Z
prometheuses.monitoring.coreos.com      2019-04-16T06:22:20Z
prometheusrules.monitoring.coreos.com   2019-04-16T06:22:20Z
servicemonitors.monitoring.coreos.com   2019-04-16T06:22:21Z
```

#### 三、部署整套CRD

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

#### 四、部署遇到的坑
### 1、坑一
```
# 这里要注意有一个坑，二进制部署k8s管理组件和新版本kubeadm部署的都会发现在prometheus server的页面上发现kube-controller和kube-schedule的target为0/0也就是下图所示。这是因为serviceMonitor是根据label去选取svc的，我们可以看到对应的serviceMonitor是选取的ns范围是kube-system

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
  - ip: 172.16.3.9
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
  - ip: 172.16.3.9
  ports:
  - name: http-metrics
    port: 10251
    protocol: TCP
```

### 2、坑二
```
# 访问prometheus server的web页面我们发现即使创建了svc和注入对应ep的信息在target页面发现prometheus server请求被拒绝。

# 修改  kube-controller-manager 配置文件
把  --address=127.0.0.1 换成  --address=0.0.0.0
 
# 修改 kube-scheduler 配置文件
把  --address=127.0.0.1 换成  --address=0.0.0.0
 
# 修改完后重启这两个服务
```

### 3、坑三
```
# 在 prometheus targets 页面查看  monitoring/coredns/0 没有监控项，是因为 kube-dns service中没有设置监控端口 9153


# 解决方法 添加监控端口 9153
kubectl edit svc -n kube-system kube-dns
 
 
  - name: metrics
    port: 9153
    protocol: TCP
    targetPort: 9153
```

#### 五、数据持续存储、监控etcd集群、监控自动发化、自定义报警
```
1、自定义报警
https://github.com/yangpeng14/prometheus-operator-configure/tree/master/dingtalk-hook #  使用钉钉推送消息安装配置方法
https://www.qikqiak.com/post/prometheus-operator-custom-alert/ # Prometheus Operator 自定义报警 

# 加载自定义报警配置
kubectl create secret generic additional-configs --from-file=prometheus-additional.yaml -n monitoring

# vim prometheus-additional.yaml
- job_name: 'crm'
  scrape_interval: 5s
  metrics_path: '/api/private/metrics'
  static_configs:
    - targets: ['prom.crm2.smartstudy.tech']

2、prometheus 和 alertmanager 数据持续存储使用StorageClass，预先安装 nfs 和 nfs-client-provisioner
nfs-client-provisioner 安装配置 https://github.com/yangpeng14/prometheus-operator-configure/tree/master/nfs-client-provisioner

https://www.qikqiak.com/post/prometheus-operator-advance/  # Prometheus Operator 自动发现以及数据持久化

3、监控etcd
https://www.qikqiak.com/post/prometheus-operator-monitor-etcd/ # Prometheus Operator 监控 etcd 集群

独立的二进制方式启动的 etcd 集群，同样将对应的证书保存到集群中的一个 secret 对象中去即可

kubectl -n monitoring create secret generic etcd-certs --from-file=/opt/kubernetes/ssl/server.pem --from-file=/opt/kubernetes/ssl/server-key.pem --from-file=/opt/kubernetes/ssl/ca.pem
```
