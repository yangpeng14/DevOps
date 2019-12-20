## 前言

> 如果你使用过 `kubeadm` 部署过 `Kubernetes` 的环境, `master` 主机节点上就一定会在相应的目录创建了一大批证书文件, 本篇文章就来说说 `kubeadm` 到底为我们生成了哪些证书。

在Kubernetes的部署中, 创建证书, 配置证书是一道绕不过去坎儿, 好在有kubeadm这样的自动化工具, 帮我们去生成, 配置这些证书. 对于只是想体验Kubernetes或只是想测试的亲来说, 这已经够了, 但是作为Kubernetes的集群维护者来说, kubeadm更像是一个黑盒, 本篇文章就来说说黑盒中关于证书的事儿~

使用kubeadm创建完Kubernetes集群后, 默认会在 `/etc/kubernetes/pki` 目录下存放集群中需要用到的证书文件, 整体结构如下图所示:

```bash
root@k8s-master:/etc/kubernetes/pki# tree
.
|-- apiserver.crt
|-- apiserver-etcd-client.crt
|-- apiserver-etcd-client.key
|-- apiserver.key
|-- apiserver-kubelet-client.crt
|-- apiserver-kubelet-client.key
|-- ca.crt
|-- ca.key
|-- etcd
|   |-- ca.crt
|   |-- ca.key
|   |-- healthcheck-client.crt
|   |-- healthcheck-client.key
|   |-- peer.crt
|   |-- peer.key
|   |-- server.crt
|   `-- server.key
|-- front-proxy-ca.crt
|-- front-proxy-ca.key
|-- front-proxy-client.crt
|-- front-proxy-client.key
|-- sa.key
`-- sa.pub

1 directory, 22 files
```

以上22个文件就是kubeadm为我们创建的所有证书相关的文件, 下面我们来一一解析

## 证书分组

`Kubernetes` 把证书放在了两个文件夹中

- /etc/kubernetes/pki
- /etc/kubernetes/pki/etcd

我们再将这22个文件按照更细的粒度去分组

## Kubernetes 集群根证书

Kubernetes 集群根证书CA(Kubernetes集群组件的证书签发机构)

- /etc/kubernetes/pki/ca.crt
- /etc/kubernetes/pki/ca.key

以上这组证书为签发其他 Kubernetes 组件证书使用的`根证书`, 可以认为是Kubernetes集群中证书签发机构之一。

由此根证书签发的证书有:

1. kube-apiserver 组件持有的服务端证书

- /etc/kubernetes/pki/apiserver.crt
- /etc/kubernetes/pki/apiserver.key

2. kubelet 组件持有的客户端证书, 用作 kube-apiserver 主动向 kubelet 发起请求时的客户端认证

- /etc/kubernetes/pki/apiserver-kubelet-client.crt
- /etc/kubernetes/pki/apiserver-kubelet-client.key

> 注意: Kubernetes集群组件之间的交互是双向的, kubelet 既需要主动访问 kube-apiserver, kube-apiserver 也需要主动向 kubelet 发起请求, 所以双方都需要有自己的根证书以及使用该根证书签发的服务端证书和客户端证书. 在 kube-apiserver 中, 一般明确指定用于 https 访问的服务端证书和带有CN 用户名信息的客户端证书. 而在 kubelet 的启动配置中, 一般只指定了 ca 根证书, 而没有明确指定用于 https 访问的服务端证书, 这是因为, 在生成服务端证书时, 一般会指定服务端地址或主机名, kube-apiserver 相对变化不是很频繁, 所以在创建集群之初就可以预先分配好用作 kube-apiserver 的 IP 或主机名/域名, 但是由于部署在 node 节点上的 kubelet 会因为集群规模的变化而频繁变化, 而无法预知 node 的所有 IP 信息, 所以 kubelet 上一般不会明确指定服务端证书, 而是只指定 ca 根证书, 让 kubelet 根据本地主机信息自动生成服务端证书并保存到配置的cert-dir文件夹中.

好了, 至此, Kubernetes集群根证书所签发的证书都在上面了, 算上根证书一共涉及到6个文件, 22-6=16, 我们还剩下16个文件

## 汇聚层证书

kube-apiserver 的另一种访问方式就是使用 `kubectl proxy` 来代理访问, 而该证书就是用来支持SSL代理访问的. 在该种访问模式下, 我们是以http的方式发起请求到代理服务的, 此时, 代理服务会将该请求发送给 kube-apiserver, 在此之前, 代理会将发送给 kube-apiserver 的请求头里加入证书信息, 以下两个配置

API Aggregation允许在不修改Kubernetes核心代码的同时扩展Kubernetes API. 开启 API Aggregation 需要在 kube-apiserver 中添加如下配置:

```
--requestheader-client-ca-file=<path to aggregator CA cert>
--requestheader-allowed-names=front-proxy-client
--requestheader-extra-headers-prefix=X-Remote-Extra-
--requestheader-group-headers=X-Remote-Group
--requestheader-username-headers=X-Remote-User
--proxy-client-cert-file=<path to aggregator proxy cert>
--proxy-client-key-file=<path to aggregator proxy key>
```

`官方警告: 除非你了解保护 CA 使用的风险和机制, 否则不要在不通上下文中重用已经使用过的 CA`

如果 kube-proxy 没有和 API server 运行在同一台主机上，那么需要确保启用了如下 apiserver 标记：`--enable-aggregator-routing=true`

```
客户端 ---发起请求---> 代理 ---Add Header:发起请求---> kube-apiserver
                   (客户端证书)                        (服务端证书)
```

kube-apiserver 代理根证书(客户端证书)


用在 `requestheader-client-ca-file` 配置选项中, kube-apiserver 使用该证书来验证客户端证书是否为自己所签发

- /etc/kubernetes/pki/front-proxy-ca.crt
- /etc/kubernetes/pki/front-proxy-ca.key

由此根证书签发的证书只有一组:

代理层(如汇聚层aggregator)使用此套代理证书来向 kube-apiserver 请求认证

1. 代理端使用的客户端证书, 用作代用户与 kube-apiserver 认证

- /etc/kubernetes/pki/front-proxy-client.crt
- /etc/kubernetes/pki/front-proxy-client.key

`参考文档`:

- kube-apiserver 配置参数: https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver
- 使用汇聚层扩展 Kubernetes API: https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/apiserver-aggregation
- 配置汇聚层: https://kubernetes.io/docs/tasks/access-kubernetes-api/configure-aggregation-layer


至此, 刨除代理专用的证书外, 还剩下 16-4=12 个文件

## etcd 集群根证书

etcd集群所用到的证书都保存在 `/etc/kubernetes/pki/etcd` 这路径下, 很明显, 这一套证书是用来专门给etcd集群服务使用的, 设计以下证书文件

etcd 集群根证书CA(etcd 所用到的所有证书的签发机构)

- /etc/kubernetes/pki/etcd/ca.crt
- /etc/kubernetes/pki/etcd/ca.key

由此根证书签发机构签发的证书有:

1. etcd server 持有的服务端证书

- /etc/kubernetes/pki/etcd/server.crt
- /etc/kubernetes/pki/etcd/server.key

2. peer 集群中节点互相通信使用的客户端证书

- /etc/kubernetes/pki/etcd/peer.crt
- /etc/kubernetes/pki/etcd/peer.key

注: Peer：对同一个etcd集群中另外一个Member的称呼

3. pod 中定义 Liveness 探针使用的客户端证书

kubeadm 部署的 Kubernetes 集群是以 pod 的方式运行 etcd 服务的, 在该 pod 的定义中, 配置了 `Liveness` 探活探针

- /etc/kubernetes/pki/etcd/healthcheck-client.crt
- /etc/kubernetes/pki/etcd/healthcheck-client.key

当你 describe etcd 的 pod 时, 会看到如下一行配置:

```bash
Liveness:  exec [/bin/sh -ec ETCDCTL_API=3 etcdctl --endpoints=https://[127.0.0.1]:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get foo] delay=15s timeout=15s period=10s #success=1 #failure=8
```

4. 配置在 kube-apiserver 中用来与 etcd server 做双向认证的客户端证书

- /etc/kubernetes/pki/apiserver-etcd-client.crt
- /etc/kubernetes/pki/apiserver-etcd-client.key

至此, 介绍了涉及到 etcd 服务的10个证书文件, 12-10=2, 仅剩两个没有介绍到的文件啦, 胜利在望, 坚持一下~


## Serveice Account秘钥

最后介绍的这组”证书”其实不是证书, 而是一组`秘钥`. 看着后缀名是不是有点眼熟呢, 没错, 这组秘钥对儿其实跟我们在Linux上创建, 用于免密登录的密钥对儿原理是一样的~

> 这组的密钥对儿仅提供给 kube-controller-manager 使用. kube-controller-manager 通过 sa.key 对 token 进行签名, master 节点通过公钥 sa.pub 进行签名的验证

- /etc/kubernetes/pki/sa.key
- /etc/kubernetes/pki/sa.pub

至此, kubeadm 工具帮我们创建的所有证书文件都已经介绍完了, 整个 Kubernetes&etcd 集群中所涉及到的绝大部分证书都差不多在这里了. 有的行家可能会看出来, 至少还少了一组证书呀, 就是 kube-proxy 持有的证书怎么没有自动生成呀. 因为 kubeadm 创建的集群, kube-proxy 是以 pod 形式运行的, 在 pod 中, 直接使用 service account 与 kube-apiserver 进行认证, 此时就不需要再单独为 kube-proxy 创建证书了. 如果你的 kube-proxy 是以守护进程的方式直接运行在宿主机的, 那么你就需要为它创建一套证书了. 创建的方式也很简单, 直接使用上面第一条提到的 `Kubernetes 集群根证书` 进行签发就可以了(注意CN和O的设置)

`参考文档`：

- https://kubernetes.io/docs/setup/certificates/
- https://kubernetes.io/docs/setup/independent/setup-ha-etcd-with-kubeadm/
- docs.lvrui.io

## 原文出处

> 作者：icyboy

> http://team.jiunile.com/blog/2018/12/k8s-kubeadm-ca-desc.html