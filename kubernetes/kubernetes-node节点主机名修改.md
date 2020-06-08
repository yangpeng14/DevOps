## 背景

Kubernetes 集群环境中，有时候需要修改 Node 节点主机名，这时我们应该如何操作？

有些同学，在更改了 `kubelet.conf` 配置中 `hostname-override` 参数，也更改了 `kube-proxy-config.yml` 配置中 `hostnameOverride` 参数，删除 Node 节点并且重启 `kubelet` 和 `kube-proxy` 服务，但主机名并没有修改，这是为什么？下文会给出解释。

> 环境是使用 二进制搭建的 kubernetes v1.18.2 版本

## 准备工作

大家要知道一点，Node节点主机名更改，需要先`删除Node节点`，在删除节点前，我们需要把该节点上的Pod应用服务驱逐到其它节点上。

> 注意，如果集群中只有一个Node节点，不能使用驱逐命令，因为使用驱逐命令后，所有Pod会处于 `Pending` 状态。

```bash
# 通过以下命令驱逐节点上pod应用
$ kubectl drain service2 --delete-local-data --ignore-daemonsets

# 查看node节点，service2 上应用服务驱逐完后会标记为不可调度
$ kubectl get node

NAME       STATUS                     ROLES    AGE   VERSION
service2   Ready,SchedulingDisabled   <none>   24d   v1.18.2
service3   Ready                      <none>   24d   v1.18.2

# 删除 service2 节点
$ kubectl delete node service2
```

## 修改 Node节点主机名

### 修改 kubelet 和 kube-proxy 服务配置文件

登陆 service2 机器，修改 kubelet 和 kube-proxy 服务配置文件，具体按如下修改：

> 本次演示，把主机名从 service2 修改为 service2-test

```bash
# 停止 kubelet 和 kube-proxy 服务
$ systemctl stop kubelet
$ systemctl stop kube-proxy

# 修改 kubelet.conf 配置文件中 hostname-override 参数
$ vim /opt/kubernetes/cfg/kubelet.conf

# 修改完后，查看
$ grep hostname-override /opt/kubernetes/cfg/kubelet.conf

--hostname-override=service2-test \

# 修改 kube-proxy.kubeconfig 配置文件中 hostnameOverride 参数
$ vim /opt/kubernetes/cfg/kube-proxy-config.yml

# 修改完后，查看
$ grep hostnameOverride /opt/kubernetes/cfg/kube-proxy-config.yml

hostnameOverride: service2-test # 注册到k8s的节点名称唯一
```

### 删除  kubelet 服务生成的认证文件和客户端证书

> 这里回答`背景`提到的问题，如果不删除 kubelet 服务生成的`认证文件`和`客户端证书`，那么修改的节点主机名是不会生效。

```bash
# 删除 kubelet 服务生成的认证文件和客户端证书
$ rm -f /opt/kubernetes/cfg/kubelet.kubeconfig
$ rm -f /opt/kubernetes/ssl/kubelet*

# 重新启动 kubelet 和 kube-proxy 服务
$ systemctl start kubelet
$ systemctl start kube-proxy
```

### 验证

```bash
# 登陆到 k8s-master 机器上查看 csr，如何没有自动授权 Node加入，需要执行下面命令
$ kubectl  certificate approve csr-xhjk5

NAME        AGE   SIGNERNAME                                    REQUESTOR           CONDITION
csr-xhjk5   31m   kubernetes.io/kube-apiserver-client-kubelet   kubelet-bootstrap   Pending

# 执行上面命令成功后，会看到下面结果
$ kubectl get csr

NAME        AGE   SIGNERNAME                                    REQUESTOR           CONDITION
csr-xhjk5   31m   kubernetes.io/kube-apiserver-client-kubelet   kubelet-bootstrap   Approved,Issued

# 查看 node 节点，成功加入node节点，并且主机名也修改成功
$ kubectl get node

NAME            STATUS   ROLES    AGE   VERSION
service2-test   Ready    <none>   31m   v1.18.2
service3        Ready    <none>   24d   v1.18.2
```

## 总结

修改 Node节点主机名顺序如下：

- 1、使用 `kubectl drain` 命令驱逐节点上Pod
- 2、使用 `kubectl delete node` 命令删除需要改名的节点
- 3、停止 `kubelet` 和 `kube-proxy` 服务
- 4、修改 `kubelet.conf` 和 `kube-proxy-config.yml` 配置
- 5、删除 kubelet 服务生成的`认证文件`和`客户端证书`
- 6、启动 `kubelet` 和 `kube-proxy` 服务
- 7、使用命令 `kubectl  get csr` 和 `kubectl  certificate approve` 命令授权 node节点加入