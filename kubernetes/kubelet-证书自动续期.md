# 一、问题现象和原因

## Kubernetes 日志错误
当 Kubernetes 集群日志中出现 `certificate has expired or is not yet valid` 错误信息时，表明证书过期

## 证书过期原因
- 服务器时间不对，导致证书过期
- 确实证书过期了

证书过期，很多同学会很疑惑，我证书明明`签署10年`有效期或者`更久`，怎么刚`1年就过期了`，下面就来解惑。

## Kubernetes 集群证书
集群分为两种证书：一、用于集群 `Master、Etcd`等通信的证书。 二、用于集群 `Kubelet` 组件证书

## Kubernetes 集群中 Kubelet 组件坑
我们在搭建 Kubernetes 集群时，一般只声明用于集群 `Master、Etcd`等通信的证书 为 `10年` 或者 `更久`，但未声明集群 `Kubelet 组件证书` ，`Kubelet 组件证书` 默认有效期为`1年`。集群运行1年以后就会导致报 `certificate has expired or is not yet valid` 错误，导致`集群 Node`不能于`集群 Master`正常通信。

# 二、 解决方法

## 添加参数
- 修改 `kubelet 组件配置`，具体添加下面参数
```
--feature-gates=RotateKubeletServerCertificate=true
--feature-gates=RotateKubeletClientCertificate=true
# 1.8版本以上包含1.8都支持证书更换自动重载，以下版本只能手动重启服务
--rotate-certificates
```

- 修改 `controller-manager 组件配置`，具体添加下面参数

```
# 证书有效期为10年
--experimental-cluster-signing-duration=87600h0m0s
--feature-gates=RotateKubeletServerCertificate=true
```

## 创建自动批准相关 CSR 请求的 ClusterRole
- `vim tls-instructs-csr.yaml  && kubectl apply -f tls-instructs-csr.yaml`

```
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: system:certificates.k8s.io:certificatesigningrequests:selfnodeserver
rules:
- apiGroups: ["certificates.k8s.io"]
  resources: ["certificatesigningrequests/selfnodeserver"]
  verbs: ["create"]
```

- 自动批准 kubelet-bootstrap 用户 TLS bootstrapping 首次申请证书的 CSR 请求

```
kubectl create clusterrolebinding node-client-auto-approve-csr --clusterrole=system:certificates.k8s.io:certificatesigningrequests:nodeclient --user=kubelet-bootstrap
```

- 自动批准 system:nodes 组用户更新 kubelet 自身与 apiserver 通讯证书的 CSR 请求

```
kubectl create clusterrolebinding node-client-auto-renew-crt --clusterrole=system:certificates.k8s.io:certificatesigningrequests:selfnodeclient --group=system:nodes
```

- 自动批准 system:nodes 组用户更新 kubelet 10250 api 端口证书的 CSR 请求

```
kubectl create clusterrolebinding node-server-auto-renew-crt --clusterrole=system:certificates.k8s.io:certificatesigningrequests:selfnodeserver --group=system:nodes
```

## 重启kube-controller-manager 和 kubelet 服务
```
$ systemctl restart kube-controller-manager

# 进入到ssl配置目录，删除 kubelet 证书
$ rm -f kubelet-client-current.pem kubelet-client-2019-05-10-09-57-21.pem kubelet.key kubelet.crt

# 重启启动，启动正常后会颁发有效期10年的ssl证书
$ systemctl restart kubelet


# 进入到ssl配置目录，查看证书有效期
$ openssl x509 -in kubelet-client-current.pem -noout -text | grep "Not"

Not Before: May 13 02:36:00 2019 GMT
Not After : May 10 02:36:00 2029 GMT
```