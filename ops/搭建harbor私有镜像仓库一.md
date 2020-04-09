> - 作者：Happiness
> - 链接：https://blog.k8s.fit

## 背景

最近接收到新任务，需要在公司内部部署一个harbor仓库 ，我这里介绍的是在k8s里部署harbor，之所以没有选择使用`docker-compose`来部署是想统一管理。如果内部既有docker环境又有k8s环境，对于维护者来说很复杂不利于维护，工作量也大大加重，所以选择了在k8s里部署harbor。这篇文章只适用学习范围，因为我这里使用的是内网穿透(因为没有云主机，只好模拟暴露在公网上即CNAME方式) 来完成的证书验证。

在本篇文章中你将学到如何为你的应用服务自动创建可受信任的https证书，以及如何搭建harbor。

## 环境准备：

这里是在 `kubeadm` 搭建的 `v1.16.7` 版本下部署

> kubeadm 安装略


## 步骤一

安装helm包管理工具，我这里使用 `v3.1.1`

```bash
$ wget https://get.helm.sh/helm-v3.1.1-linux-amd64.tar.gz
$ tar xf helm-v3.1.1-linux-amd64.tar.gz
$ cp linux-amd64/helm /usr/local/bin/
$ helm version
```
## 步骤二

配置可信任的证书，我这里使用helm部署

```bash
# 部署前需要一些 crd
$ kubectl apply --validate=false -f https://raw.githubusercontent.com/jetstack/cert-manager/v0.13.1/deploy/manifests/00-crds.yaml

# 为ce​​rt-manager创建名称空间
$ kubectl create namespace cert-manager

# 添加Jetstack Helm存储库
$ helm repo add jetstack https://charts.jetstack.io

# 更新本地Helm存储库缓存
$ helm repo update

# 安装cert-manager
$ helm install \
  cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v0.13.1

# 验证安装
# 你可以通过检查cert-manager运行Pod的名称空间来验证它是否已正确部署：

[root@master harbor]# kubectl get pods --namespace cert-manager
NAME                                       READY   STATUS    RESTARTS   AGE
cert-manager-7cb745cb4f-87hnv              1/1     Running   0          17h
cert-manager-cainjector-778cc6bd68-2bvvp   1/1     Running   0          17h
cert-manager-webhook-69894d5869-j88fg      1/1     Running   0          17h
```

## 步骤三

helm 安装 harbor ，默认使用的是`ingress`，所以在这里我们不用配置ingress，只要配置上证书颁发者和证书创建者即可。

> 详情见：https://blog.k8s.fit/articles/2020/02/28/1582892559454.html

```yaml
apiVersion: cert-manager.io/v1alpha2
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: 15xxxxxxxx0@163.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
---
apiVersion: cert-manager.io/v1alpha2
kind: Certificate
metadata:
  name: harbor
  namespace: harbor
spec:
  secretName: harbor-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  duration: 2160h
  renewBefore: 360h
  keyEncoding: pkcs1
  dnsNames:
  - harbor.k8s.fit
```

## 步骤四

证书准备工作都做完了接下来部署 harbor

添加 helm repo

```bash
$ helm repo add harbor https://helm.goharbor.io
$ helm pull harbor/harbor --untar 
$ cd harbor

# 编辑values.yaml文件
# 你可以直接下载我已经写好的values.yaml文件
# 注意：你要提前创建好 storageclasses

http://nextcloud.k8s.fit/s/DHwoajRB7oY9xpm

# 安装harbor

$ helm install harbor -f values.yaml harbor/harbor -n harbor

# 验证
[root@master harbor]# kubectl get pod -n harbor

NAME                                           READY   STATUS    RESTARTS   AGE
harbor-harbor-chartmuseum-86dc568455-f58wm     1/1     Running   0          36m
harbor-harbor-clair-654dcfd8bf-t59tb           2/2     Running   2          36m
harbor-harbor-core-6b7bf8c458-lqz5z            1/1     Running   0          36m
harbor-harbor-database-0                       1/1     Running   0          36m
harbor-harbor-jobservice-65cfd9668-dh7pz       1/1     Running   0          36m
harbor-harbor-notary-server-956744d56-4n9z7    1/1     Running   0          36m
harbor-harbor-notary-signer-6449bb8ff7-8mp24   1/1     Running   0          36m
harbor-harbor-portal-5cbc6d5897-vd5cn          1/1     Running   0          36m
harbor-harbor-redis-0                          1/1     Running   0          36m
harbor-harbor-registry-76dccf66f4-29fll        2/2     Running   0          36m
```

## 验证

```
docker login https://harbor.k8s.fit

Authenticating with existing credentials...
WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded
```

## 结束语

`docker login` 或者 `docker push` 等命令都是要验证harbor的证书的，所以我这里选择了`可信任的证书`CNAME方式。你也可以使用`不受信任的证书`修改docker的配置文件来完成 `docker login` 或者 `docker push` 等操作(详情见下篇文章)。