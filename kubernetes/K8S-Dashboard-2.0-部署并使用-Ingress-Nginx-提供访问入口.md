## 前言

Kubernetes Dashboard 终于发布 `2.0` 正式版本，从 `Betat版本` 到 `v2.0.0正式版本` 发布，历时一年多。

## 环境与依赖服务

### 环境

- 需要安装 [Ingress Nginx 部署](https://www.yp14.cn/2019/11/19/K8s-Ingress-Nginx-%E6%94%AF%E6%8C%81-Socket-io/)
- Kubernetes `Version v1.18.2`

### 依赖服务

- 需要K8S集群部署 [metrics-server](https://www.yp14.cn/2019/08/29/Metrics-Server-v0-3-2%E7%89%88%E6%9C%AC%E5%AE%89%E8%A3%85/)，这样才能正常查看 Dashboard 查看监控指标。

> 注意：如果集群有1.7+以下旧版本，请确保删除`kubernetes-dashboard`服务帐户的群集角色绑定，否则Dashboard将具有对该群集的`完全管理员访问权限`。

## 部署

### 自定义证书

下面是生成 `k8s dashboard` 域名证书方法，任何一种都可以。

- 通过 `https://freessl.cn` 网站，在线生成免费1年的证书。
- 通过 `Let’s Encrypt` 生成 `90天` 免费证书
- 通过 `Cert-Manager` 服务来生成和管理证书

> 注意：自定义证书 `kubernetes-dashboard-certs` secret 必须存储在与`Kubernetes仪表板`相同的 Namespaces。

### 创建 kubernetes-dashboard-certs secret

按上面方法，生成证书，证书生成存放到 `$HOME/certs` 目录中

```bash
# 证书
$ ls $HOME/certs

k8s-dashboard.yp14.cn.crt  k8s-dashboard.yp14.cn.key

# 创建 kubernetes-dashboard-certs secret
$ kubectl create secret generic kubernetes-dashboard-certs --from-file=$HOME/certs -n kubernetes-dashboard
```

### 下载 dashboard yaml 文件

```bash
$ wget https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
```

### 修改 dashboard yaml 文件

具体修改见下面配置

```bash
$ vim recommended.yaml

# 把创建 kubernetes-dashboard-certs Secret 注释掉，前面已通过命令创建。

#apiVersion: v1
#kind: Secret
#metadata:
#  labels:
#    k8s-app: kubernetes-dashboard
#  name: kubernetes-dashboard-certs
#  namespace: kubernetes-dashboard
#type: Opaque

# 添加ssl证书路径，关闭自动更新证书，添加多长时间登出。
# 注意：--tls-key-file --tls-cert-file 引用名称，要与上面创建 kubernetes-dashboard-certs Secret 引用的证书文件名称一样。

          args:
            #- --auto-generate-certificates
            - --namespace=kubernetes-dashboard
            - --tls-key-file=k8s-dashboard.yp14.cn.key
            - --tls-cert-file=k8s-dashboard.yp14.cn.crt
            - --token-ttl=3600
```

### 部署 dashboard

```bash
$ kubectl  apply -f recommended.yaml
```

### 查看 dashboard 

```bash
$ kubectl  get pods -n kubernetes-dashboard

NAME                                         READY   STATUS    RESTARTS   AGE
dashboard-metrics-scraper-6b4884c9d5-lx8dw   1/1     Running   0          14h
kubernetes-dashboard-b75f6b5d6-r22nq         1/1     Running   0          14h
```

## 创建登陆用户

### 创建 admin-user 管理员 yaml 配置

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

创建
```bash
$ kubectl apply -f create-admin.yaml
```

查看登陆 `token`

```bash
$ kubectl -n kubernetes-dashboard describe secret $(kubectl -n kubernetes-dashboard get secret | grep admin-user | awk '{print $1}')
```

## 配置 Ingress Nginx 提供访问入口

```bash
$ cd $HOME/certs

# 创建 k8s-dashboard.yp14.cn 域名 Ingress nginx https 证书
$ kubectl create secret tls k8s-dashboard --key k8s-dashboard.yp14.cn.key --cert k8s-dashboard.yp14.cn.crt -n kubernetes-dashboard
```

```bash
$ vim k8s-dashboard-ingress.yaml
```

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: k8s-dashboard-ingress
  namespace: kubernetes-dashboard
  annotations:
    kubernetes.io/ingress.class: "nginx"
    # 开启use-regex，启用path的正则匹配
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/rewrite-target: /
    # 默认为 true，启用 TLS 时，http请求会 308 重定向到https
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    # 默认为 http，开启后端服务使用 proxy_pass https://协议
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
spec:
  rules:
  - host: k8s-dashboard.yp14.cn
    http:
      paths:
      - path: /
        backend:
          serviceName: kubernetes-dashboard
          servicePort: 443
  tls:
  - secretName: k8s-dashboard
    hosts:
    - k8s-dashboard.yp14.cn
```

`访问入口域名`：https://k8s-dashboard.yp14.cn

把上文查看的登陆 `token` 填入到下图画红圈中

![](/img/k8s-dashboard-1.png)

## Dashboard 中文设置

> 下面演示使用 `谷歌浏览器`

Kubernetes Dashboard 2.0 已经支持中文界面了，但是你需要做一下浏览器设置，如下图：

![](/img/k8s-dashboard-2.png)