> - 作者：Happiness
> - 链接：https://blog.k8s.fit

![](/img/a53db783-02b7-4038-9062-c4006a77b19d.jpg)


## 背景: 

最近接收到新任务，需要在公司内部部署一个harbor仓库， 我这里介绍的是在k8s里部署harbor，之所以没有选择使用 `docker-compose` 来部署是想统一管理，如果内部既有docker环境又有k8s环境，对于维护者来说很复杂不利于维护，工作量也大大加重，所以选择了在k8s里部署harbor。

本片文章介绍在k8s里搭建harbor（很多朋友都有过类似经历，在k8s里搭建harbor后, docker login 失败）一直也没有解决办法，那么本文主要详解 `docker login失败解决办法`。

## 环境准备：这里是在 `kubeadm` 搭建的 `v1.16.7` 版本下进行部署

> kubeadm 安装略

## 步骤一

安装helm包管理工具，我这里使用 v3.1.1
```bash
$ wget https://get.helm.sh/helm-v3.1.1-linux-amd64.tar.gz
$ tar xf helm-v3.1.1-linux-amd64.tar.gz
$ cp linux-amd64/helm /usr/local/bin/
$ helm version
```

## 步骤二

配置 `nfs` 后端存储的 `StorageClass`，这里依旧使用的是 `helm` 安装

```bash
# 添加repo
$ helm repo add stable https://kubernetes-charts.storage.googleapis.com

# 将nfs-client-provisioner下拉到本地编辑其配置文件
$ helm pull stable/nfs-client-provisioner --untar
$ cd nfs-client-provisioner/
$ vim values.yaml

# 你可以下载好我已经写完的配置文件
http://nextcloud.k8s.fit/s/eRiMQLwzEdbqTmg

# 安装nfs-client-provisioner
$ helm install nfs -f values.yaml stable/nfs-client-provisioner

# 验证
[root@k8s-master nfs-client-provisioner]# helm ls

NAME	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART                       	APP VERSION
nfs 	default  	1       	2020-04-03 13:23:31.919532882 +0800 CST	deployed	nfs-client-provisioner-1.2.8	3.1.0  

[root@k8s-master nfs-client-provisioner]# kubectl get sc

NAME         PROVISIONER                                AGE
nfs-harbor   cluster.local/nfs-nfs-client-provisioner   48s
```

## 步骤三

我这里使用`自创建证书`(并非CNAME方式)

```bash
$ openssl genrsa -out tls.key 2048
$ openssl req -new -x509 -days 3650 -key tls.key -out tls.crt -subj /C=CN/ST=Beijingshi/L=Beijing/O=devops/CN=cn
$ kubectl create secret tls harbor-tls --cert=tls.crt --key=tls.key -n harbor

# 验证
$ kubectl get secret -n harbor

[root@k8s-master ~]# kubectl get secret -n harbor

NAME                  TYPE                                  DATA   AGE
default-token-gsnxz   kubernetes.io/service-account-token   3      89s
harbor-tls            kubernetes.io/tls                     2      86s
```

## 步骤四

配置 harbor 配置文件并指定后端存储
```bash
# 添加repo
$ helm repo add harbor https://helm.goharbor.io

# 将harbor下拉到本地编辑其配置文件
$ helm pull harbor/harbor --untar
$ cd harbor
$ vim values.yaml

# 你可以下载好我已经写完的配置文件
http://nextcloud.k8s.fit/s/ZpnqoD2LBpx4tMY

# 安装harbor
$ helm install harbor -f values.yaml harbor/harbor -n harbor

# 验证
$ kubectl get pod,svc -n harbor

[root@k8s-master ~]# kubectl get pod,svc -n harbor

NAME                                               READY   STATUS    RESTARTS   AGE
pod/harbor-harbor-chartmuseum-64b5c4b8df-9l8n9     1/1     Running   0          65m
pod/harbor-harbor-clair-654dcfd8bf-4tjpv           2/2     Running   5          65m
pod/harbor-harbor-core-6fc8bfb9cd-22cwv            1/1     Running   10         65m
pod/harbor-harbor-database-0                       1/1     Running   0          65m
pod/harbor-harbor-jobservice-5cb8958667-tljt8      1/1     Running   12         65m
pod/harbor-harbor-notary-server-5fb6ddd869-s9nrv   1/1     Running   13         65m
pod/harbor-harbor-notary-signer-c5c564f78-vmsh7    1/1     Running   7          65m
pod/harbor-harbor-portal-5cbc6d5897-j5lvh          1/1     Running   0          65m
pod/harbor-harbor-redis-0                          1/1     Running   0          65m
pod/harbor-harbor-registry-654c7df9f4-pcx9f        2/2     Running   0          65m

NAME                                  TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)             AGE
service/harbor-harbor-chartmuseum     ClusterIP   10.244.96.40     <none>        80/TCP              65m
service/harbor-harbor-clair           ClusterIP   10.244.120.183   <none>        8080/TCP            65m
service/harbor-harbor-core            ClusterIP   10.244.83.246    <none>        80/TCP              65m
service/harbor-harbor-database        ClusterIP   10.244.77.98     <none>        5432/TCP            65m
service/harbor-harbor-jobservice      ClusterIP   10.244.102.222   <none>        80/TCP              65m
service/harbor-harbor-notary-server   ClusterIP   10.244.78.39     <none>        4443/TCP            65m
service/harbor-harbor-notary-signer   ClusterIP   10.244.68.129    <none>        7899/TCP            65m
service/harbor-harbor-portal          ClusterIP   10.244.80.37     <none>        80/TCP              65m
service/harbor-harbor-redis           ClusterIP   10.244.95.197    <none>        6379/TCP            65m
service/harbor-harbor-registry        ClusterIP   10.244.123.224   <none>        5000/TCP,8080/TCP   65m
```

## 步骤五

上面 harbor 已经安装完成，这时候使用`docker login https://harbor.k8s.fit` 登陆失败

> 解决办法如下：

修改hosts文件，因为用的是 `ingress` 方式，所以要配置上ingress对应节点的IP

接下来修改docker的配置

```bash
$ vim /etc/docker/daemon.json

在"insecure-registries"行内添加上harbor仓库的url 如下：

{
  "registry-mirrors": ["https://dockerhub.azk8s.cn","https://quay.azk8s.cn"],
  "insecure-registries": ["10.244.0.0/16","https://harbor.k8s.fit"],
  "max-concurrent-downloads": 10,
  "log-driver": "json-file",
  "log-level": "warn",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
    },
  "data-root": "/var/lib/docker",
  "exec-opts": ["native.cgroupdriver=systemd"],
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ]
}
```

接下来重启docker

```bash
$ systemctl restart docker
```

再次尝试 `docker login https://harbor.k8s.fit`

```bash
[root@k8s-master harbor]# docker login https://harbor.k8s.fit

Authenticating with existing credentials...
WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded
```

## 结束语

经过两天的折腾，终于可以成功登陆自创建证书的 harbor了，经测试 `docker login` 、`docker push`等命令都是正常使用的，本文章之所以可以成功是因为关键的`步骤五`一定要注意！

本篇文章适用于公司内部自建的harbor！只用ingress方式的话，默认harbor会自动创建证书，但是证书有效期是多少我就不清楚了，没有做测试，所以我上面使用了`openssl`自创建了`10年的证书`！