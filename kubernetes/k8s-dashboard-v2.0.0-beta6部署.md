## 什么是 Kubernetes Dashboard

`Kubernetes Dashboard`：是Kubernetes集群基于`Web的通用UI`。它允许用户`管理集群中运行的应用程序`并对其进行故障排除，以及`管理集群本身`。

## k8s Dashboard V2.0.0 Beta6 效果图展示

![](https://www.yp14.cn/img/k8s-dashboard-v2.png)

## V2.0.0 相比 V1.x.x 优势

- 监控信息不需要通过 `Heapster` 来提供，而是通过 `Metrics Server` 来提供，`Metrics Scraper`服务来采集，不需要单独维护 `Heapster`
- 支持暗黑主题
- 监控图显示更细节化
- 编辑支持 `yaml`  和 `json`

## v2.0.0-beta6 兼容性

Kubernetes版本 | 兼容性
---|---
1.12 | ?
1.13 | ?
1.14 | ?
1.15 | ?
1.16 | ✓

- `✓` 完全支持的版本范围
- `?` 由于 Kubernetes API 版本之间的重大更改，某些功能可能无法在仪表板中正常使用

## 环境

- k8s v1.16.3
- k8s 集群需要安装 `Metrics Server`，否则没有监控数据

## 生成证书

`下面是生成 k8s dashboard 域名证书方法，任何一种都可以`

- 通过 `https://freessl.cn` 网站，在线生成免费`1年`的证书
- 通过 `Let’s Encrypt` 生成 `90天` 免费证书
- 通过 `Cert-Manager` 服务来生成和管理证书

## 部署

- v2.0.0 单独放一个 namespace，下面是创建 kubernetes-dashboard namespace

```bash
$ kubectl  create namespace kubernetes-dashboard
```

- 把生成的免费证书存放在 $HOME/certs 目录下，取名为 tls.crt 和 tls.key

```bash
$ mkdir $HOME/certs
```

- 创建 ssl 证书 secret

```bash
$ kubectl create secret generic kubernetes-dashboard-certs --from-file=$HOME/certs -n kubernetes-dashboard
```

- 拉取 k8s dashboard yaml 配置

```bash
$ wget https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0-beta6/aio/deploy/recommended.yaml
```

- 修改 Deployment yaml 配置，具体修改见下面配置

```bash
$ vim recommended.yaml

# 把创建 kubernetes-dashboard-certs Secret 注释掉，前面已通过命令创建

#apiVersion: v1
#kind: Secret
#metadata:
#  labels:
#    k8s-app: kubernetes-dashboard
#  name: kubernetes-dashboard-certs
#  namespace: kubernetes-dashboard
#type: Opaque

# 添加ssl证书路径，关闭自动更新证书，添加多长时间登出

      containers:
      - args:
        #- --auto-generate-certificates
        - --tls-cert-file=/tls.crt
        - --tls-key-file=/tls.key
        - --token-ttl=3600
```

- 部署 k8s dashboard

```bash
$ kubectl  apply -f recommended.yaml
```

- 查看

```bash
$ kubectl  get pods -n kubernetes-dashboard

NAME                                         READY   STATUS    RESTARTS   AGE
dashboard-metrics-scraper-6c554969c6-5dk7f   1/1     Running   0          3h25m
kubernetes-dashboard-c4d9c67bf-xfxvl         1/1     Running   0          3h25m
```

## 创建登陆用户

- 创建 `admin-user` 管理员 yaml 配置

```bash
$ vim create-admin.yaml
```

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard

---

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
```

- 创建

```bash
$ kubectl apply -f create-admin.yaml
```

- 查看登陆 `token`

```bash
$ kubectl -n kubernetes-dashboard describe secret $(kubectl -n kubernetes-dashboard get secret | grep admin-user | awk '{print $1}')
```

## 参考链接

- https://github.com/kubernetes/dashboard/blob/master/docs/user/installation.md
- https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/creating-sample-user.md
