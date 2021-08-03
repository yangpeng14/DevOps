Kubernetes使用Users和Service Account进行权限控制的相关工作，User 通过密钥和证书对Kuberntes API的访问进行认证，任何来自集群外的访问都需要被Kubernetes认证。通常使用X.509生成的证书对请求进行认证。

首先我们要再次重申Kubernetes没有通过数据库或者其他介质存储用户名和密码。相反，Kubenetes更希望对用户的管理可以由集群的外的程序来管理。借助Kubernetes的认证模块，可以将Kubernetes的认证我委托给第三方代理（如OpenID和Active Directory）。

X.509证书用于对Kubernetes外部请求的认证，Service accounts用于对集群内部请求的认证。Service Accounts与Pods相关，主要用于对集群内部API Server访问请求的认证。

在Kubernetes集群中，每一个运行的Pods都有一个叫default的默认用户。同时，为了使Pods可以访问内部的API Server端点，集群中有一个叫做Kubernetes的ClusterIP Server。

```bash
$ kubectl get serviceaccounts
```

![](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2019/9/3/16cf76cd089a5dff~tplv-t2oaga2asx-image.image)

```bash
$ kubectl get svc
```

![](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2019/9/3/16cf76d273674416~tplv-t2oaga2asx-image.image)

为了更好的阐释相关内容，接下来我将通过Busybox镜像启动一个Pod，在Pod中使用curl命令做相关操作。

**1\. 使用Busybox镜像启动Pod**

```bash
$ kubectl run -i --tty --rm curl-tns --image=radial/busyboxplus:curl
```

![](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2019/9/3/16cf778b1e77e041~tplv-t2oaga2asx-image.image)

在Busybox的shell命令行中，我们尝试使用curl命令连接API Server端点。

```bash
$ curl https://kubernetes:8443/api
```

由于在请求中缺少相关的token，因此上面的请求并没有任何返回，接下来我将尝试获取token，并将token嵌入到请求的header中。

**2\. 获取token**

我们已经已经讲过，token是通过secret的形式嵌入到Pod中。进入文件夹 /var/run/secrets/kubernetes.io/serviceaccount 后即可发现token。

```bash
$ cd /var/run/secrets/kubernetes.io/serviceaccount
```

![](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2019/9/3/16cf7812614d3e49~tplv-t2oaga2asx-image.image)

为了更方便的curl命令，接下来我将设置一些环境变量：

```bash
$ CA_CERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
$ TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
$ NAMESPACE=$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)
```

获取Kubectl API Service的url:

```bash
kubectl config view -o jsonpath='{"Cluster name\tServer\n"}{range .clusters[*]}{.name}{"\t"}{.cluster.server}{"\n"}{end}'
```

![](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2019/9/3/16cf7c0436b85ee9~tplv-t2oaga2asx-image.image)

下面的命令将会获取default namespace下所有的serices，我们一起看看api service的返回结果。

```bash
$ curl --cacert $CA_CERT -H "Authorization: Bearer $TOKEN" "https://35.203.146.149:6443/api/v1/namespaces/$NAMESPACE/services/"
```

![](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2019/9/3/16cf7c601e526c6c~tplv-t2oaga2asx-image.image)

惊奇的发现default service account竞然没有获取相同namespace下services的权限。

在这里我们还要重申下Kubernetes遵循由关到开的准则，这就意味着默认的user或者service account并不具备任何权限。

**3\. 对service account进行授权**

为了完成请求，我们需要通过role binding将相关的role绑定到default service account。这个过程与通过role binding将具有list pod权限的role绑定到Bob上的例子很像。

退出pod，执行下面的命令创建role后并将role绑定到default service account上。

```bash
$ kubectl create rolebinding default-view \
  --clusterrole=view \
  --serviceaccount=default:default \
  --namespace=default
```

![](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2019/9/3/16cf7d2b1d0d4a05~tplv-t2oaga2asx-image.image)

如果你对集群中的cluster role好奇，执行下面的命令:

```bash
$ kubectl get clusterroles
```

**4\. 再次验证**

再次启动运行BusyBox镜像的Pod后请求API Server

```bash
$ kubectl run -i --tty --rm curl-tns --image=radial/busyboxplus:curl
```

![](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2019/9/3/16cf778b1e77e041~tplv-t2oaga2asx-image.image)

为了更方便的curl命令，接下来我将设置一些环境变量：

```bash
$ CA_CERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
$ TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
$ NAMESPACE=$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)
```

获取Kubectl API Service的url:

```bash
$ kubectl config view -o jsonpath='{"Cluster name\tServer\n"}{range .clusters[*]}{.name}{"\t"}{.cluster.server}{"\n"}{"end"}'
```

![](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2019/9/3/16cf7c0436b85ee9~tplv-t2oaga2asx-image.image)

下面的命令将会获取default namespace下所有的serices，我们一起看看api service的返回结果。

```bash
$ curl --cacert $CA_CERT -H "Authorization: Bearer $TOKEN" "https://35.203.146.149:6443/api/v1/namespaces/$NAMESPACE/services/"
```

![](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2019/9/4/16cf7db4fe8a7e12~tplv-t2oaga2asx-image.image)

你也可以自定义一些role通过RBAC授权default service account更多的操作。

> - 作者：spursyy
> - 原文链接：https://juejin.cn/post/6844903952870293511