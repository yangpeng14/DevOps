## 问题描述

有两个（或多个）运行在不同节点上的`pod`，通过一个`svc`提供服务，如下：

```bash
root@master1:~# kubectl get pod -o wide
NAME          READY   STATUS    RESTARTS   AGE   IP            NODE
kubia-nwjcc   1/1     Running   0          33m   10.244.1.27   worker1
kubia-zcpbb   1/1     Running   0          33m   10.244.2.11   worker2

root@master1:~# kubectl get svc kubia
NAME         TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)   AGE
kubia        ClusterIP   10.98.41.49   <none>        80/TCP    34m
```

当透过其他`pod`访问该`svc`时（_使用命令`k exec kubia-nwjcc -- curl http://10.98.41.49`_），出现了只能访问到和自己同处于一个节点的`pod`的问题，访问到其他节点上的`pod`时会出现`command terminated with exit code 7`的问题，如下：

**正常访问到相同节点的`pod`**

```bash
root@master1:~# kubectl exec kubia-nwjcc -- curl http://10.98.41.49
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    23    0    23    0     0   8543      0 --:--:-- --:--:-- --:--:-- 11500
You've hit kubia-nwjcc
```

**无法访问其他节点的`pod`**

```bash
root@master1:~# kubectl exec kubia-nwjcc -- curl http://10.98.41.49   
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
curl: (7) Failed to connect to 10.98.41.49 port 80: No route to host
command terminated with exit code 7
```

本问题随机发生，如下：

```bash
root@master1:~# kubectl exec kubia-nwjcc -- curl http://10.98.41.49   
You've hit kubia-nwjcc
root@master1:~# kubectl exec kubia-nwjcc -- curl http://10.98.41.49  
command terminated with exit code 7
root@master1:~# kubectl exec kubia-nwjcc -- curl http://10.98.41.49  
command terminated with exit code 7
root@master1:~# kubectl exec kubia-nwjcc -- curl http://10.98.41.49   
You've hit kubia-nwjcc
```

## 问题原因

原因是因为，我是用的`VirtualBox`虚拟化出了两台 ubuntu 主机搭建的 k8s ，详见 [virtualbox 虚拟机组网](https://www.jianshu.com/p/e6684182471b) 。在组网的过程中，我采用了双网卡方案，**网卡1使用NAT地址转换用来访问互联网，网卡2使用`Host-only`来实现虚拟机互相访问**。`flannel`默认使用了网卡1的 ip 地址，而网卡1的NAT地址转换是无法访问其他虚拟机的，从而导致的问题的产生。

## 解决方案

因为是`flannel`使用的默认网卡1导致了这个问题的产生，所以我们需要使用`--iface`参数手动指定它使用网卡2来进行通信，这就需要修改`flannel`的配置文件，执行如下命令即可进行修改：

```bash
$ sudo kubectl edit daemonset kube-flannel-ds-amd64 -n kube-system
```

如果你执行后出现了`Error from server (NotFound): daemonsets.extensions "kube-flannel-ds-amd64" not found`的问题，按照下列步骤找到其配置文件名称：

**查找`flannel`配置文件名**

首先输入`kubectl get po -n kube-system`，然后找到正在运行的`flannel`pod。

```bash
root@master1:~# kubectl get po -n kube-system
NAME                              READY   STATUS    RESTARTS   AGE
coredns-bccdc95cf-69zrw           1/1     Running   1          2d1h
coredns-bccdc95cf-77bg4           1/1     Running   1          2d1h
etcd-master1                      1/1     Running   6          2d1h
kube-apiserver-master1            1/1     Running   6          2d1h
kube-controller-manager-master1   1/1     Running   2          2d1h

# 下面这四个都可以
kube-flannel-ds-amd64-8c2lc       1/1     Running   4          2d1h 
kube-flannel-ds-amd64-dflsl       1/1     Running   9          23h
kube-flannel-ds-amd64-hgp55       1/1     Running   1          2d1h
kube-flannel-ds-amd64-jb79v       1/1     Running   33         26h
kube-proxy-2lz7f                  1/1     Running   0          23h
kube-proxy-hqsdn                  1/1     Running   4          2d1h
kube-proxy-rh92r                  1/1     Running   1          2d1h
kube-proxy-tv4mt                  1/1     Running   0          26h
kube-scheduler-master1            1/1     Running   2          2d1h
```

然后使用`flannel`的 pod 名来查看其配置`yaml`。使用命令`kubectl get po -n kube-system kube-flannel-ds-amd64-8c2lc -o yaml`，注意修改其中的 pod 名称。在输出的内容开头可以找到`ownerReferences`字段，其下的`name`属性就是要找的配置文件名。如下:

```bash
root@master1:~# kubectl get po -n kube-system kube-flannel-ds-amd64-8c2lc -o yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: "2019-07-01T07:53:25Z"
  generateName: kube-flannel-ds-amd64-
  labels:
    app: flannel
    controller-revision-hash: 7c75959b75
    pod-template-generation: "1"
    tier: node
  name: kube-flannel-ds-amd64-8c2lc
  namespace: kube-system
  ownerReferences:
  - apiVersion: apps/v1
    blockOwnerDeletion: true
    controller: true
    kind: DaemonSet
    name: kube-flannel-ds-amd64
    uid: df09fb4c-5390-4498-b539-74cb5d90f66d
  resourceVersion: "126940"
  selfLink: /api/v1/namespaces/kube-system/pods/kube-flannel-ds-amd64-8c2lc
  uid: 31d11bc6-b8f3-492a-9f92-abac1d330663
```

将找到的配置文件名填入`sudo kubectl edit daemonset &lt;配置文件名&gt; -n kube-system`并执行即可打开配置文件。

**修改配置文件，指定目标网卡**

在打开的配置文件中找到`spec.template.spec.containers[0].args`字段，如下：


```yaml
...
spec:
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      app: flannel
      tier: node
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: flannel
        tier: node
    spec:
      containers:
      # 看这里
      - args:
        - --ip-masq
        - --kube-subnet-mgr
        command:
        - /opt/bin/flanneld
        env:
...
```

这个字段表示了`flannel`启动时都要附加那些参数，我们要手动添加参数`--iface=网卡名`来进行指定，如下：

```yaml
- args:
  - --ip-masq
  - --kube-subnet-mgr
  - --iface=enp0s8
```

这里的`enp0s8`是我的网卡名，你可以通过`ifconfig`来找到自己的网卡名。

修改完成之后输入`:wq`保存退出。命令行会提示:


```bash
daemonset.extensions/kube-flannel-ds-amd64 edited
```

这就说明保存成功了。然后就要重启所有已经存在的`flannel`。使用`kubectl delete pod -n kube-system <pod名1> <pod名2> ...`把所有的`flannel`删除即可。k8s 会自动按照你修改好的`yaml`配置重建`flannel`。

```bash
root@master1:~# kubectl delete pod -n kube-system \
kube-flannel-ds-amd64-8c2lc \
kube-flannel-ds-amd64-dflsl \
kube-flannel-ds-amd64-hgp55 \
kube-flannel-ds-amd64-jb79v 

pod "kube-flannel-ds-amd64-8c2lc" deleted
pod "kube-flannel-ds-amd64-dflsl" deleted
pod "kube-flannel-ds-amd64-hgp55" deleted
pod "kube-flannel-ds-amd64-jb79v" deleted
```

然后再次`kubectl get pod -n kube-system | grep flannel`就发现所有`flannel`都已经重启成功了：

```bash
root@master1:~# kubectl get pod -n kube-system | grep flannel
kube-flannel-ds-amd64-2d6tb       1/1     Running   0          89s
kube-flannel-ds-amd64-kp5xs       1/1     Running   0          86s
kube-flannel-ds-amd64-l9728       1/1     Running   0          92s
kube-flannel-ds-amd64-r87qc       1/1     Running   0          91s
```

然后再随便找个`pod`试一下就可以看到问题解决了：

```bash
root@master1:~# k exec kubia-d7kjl -- curl -s http://10.103.214.110  
You've hit kubia-d7kjl
root@master1:~# k exec kubia-d7kjl -- curl -s http://10.103.214.110
You've hit kubia-d7kjl
root@master1:~# k exec kubia-d7kjl -- curl -s http://10.103.214.110
You've hit kubia-kdjgf
root@master1:~# k exec kubia-d7kjl -- curl -s http://10.103.214.110
You've hit kubia-d7kjl
```

## 问题发现

这里记录一下问题的发现经过，希望对大家有所帮助。当我一开始遇到这个问题的时候还以为是`svc`的问题，但是在查看了对应`svc`的`endpoint`之后，并没有发现有什么显式的问题出现，如下，可以看到`svc`正确的识别到了已存在的两个`pod`：

```bash
root@master1:~# kubectl get ep kubia 
NAME    ENDPOINTS                         AGE
kubia   10.244.1.5:8080,10.244.3.4:8080   8h
```

> **什么是`endpoint`?**

> `endpoint`可以简单理解成路由导向的终点，因为 svc 是将许多个动态的 ip 映射成一个静态的 ip。那么就可以把这些动态的 pod ip 称为 svc 的`endpoint`。

继续说，因为在测试过程中向 svc 发了很多请求，也可以察觉到其实 svc 已经随机的将你的请求分发到了不同的 pod，只是目标 pod 不在当前节点的时候就会返回`exit code 7`。然后尝试一下绕过 svc 直接请求 pod，首先新建出来一个 pod，然后使用`kubectl get po -o wide`查看 pod ip。

```bash
root@master1:~# kubectl get po -o wide
NAME          READY   STATUS    RESTARTS   AGE   IP           NODE      NOMINATED NODE   READINESS GATES
kubia-d7kjl   1/1     Running   0          8h    10.244.1.5   worker1   <none>           <none>
kubia-kdjgf   1/1     Running   0          9h    10.244.3.4   worker2   <none>           <none>
kubia-kn45c   1/1     Running   0          13s   10.244.1.6   worker1   <none>           <none>
```

可以看到 k8s 把新的 pod 放在了`worker1`上，所以我们就拿这个新的 pod 去直接访问其他两个 pod。_这里不能在主机上直接 `ping` pod ip，因为 pod 都是开放在虚拟网络`10.244.x.x`上的，在主机上访问不到_：

**访问相同节点上的 pod**

```bash
root@master1:~# k exec -it kubia-d7kjl -- ping 10.244.1.6     
PING 10.244.1.6 (10.244.1.6): 56 data bytes
64 bytes from 10.244.1.6: icmp_seq=0 ttl=64 time=0.377 ms
64 bytes from 10.244.1.6: icmp_seq=1 ttl=64 time=0.114 ms
...
```

**访问不同节点上的 pod**

```bash
root@master1:~# k exec -it kubia-d7kjl -- ping 10.244.3.4
PING 10.244.3.4 (10.244.3.4): 56 data bytes
# 没反应了
# 死一般寂静
```

这么看的话其实问题不在`svc`上，而是两个节点之间的网络联通出现了问题。而`10.244.x.x`虚拟网段是通过`flannel`搭建的，所以问题自然就是出在它上。在翻阅了官方文档后可以发现，官方明确指出了在`vagrant`类型的虚拟机上运行时要注意默认网卡的问题，再结合自己的网络情况，问题就已经很明确了了。

![](/img/13523736-ad5203365295fc69.png)

## 参考
  
- [flannel - Troubleshooting](https://links.jianshu.com/go?to=https%3A%2F%2Fcoreos.com%2Fflannel%2Fdocs%2Flatest%2Ftroubleshooting.html)
- [Kubernetes with Flannel — Understanding the Networking — Part 1 (Setup the demo).](https://links.jianshu.com/go?to=https%3A%2F%2Fmedium.com%2F%40anilkreddyr%2Fkubernetes-with-flannel-understanding-the-networking-part-1-7e1fe51820e4)
- [k8s svc can not find pod in other worker node](https://links.jianshu.com/go?to=https%3A%2F%2Fstackoverflow.com%2Fquestions%2F56862188%2Fk8s-svc-can-not-find-pod-in-other-worker-node)