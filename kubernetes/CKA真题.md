## 1.列出pod并排序

```bash
# 题目一般都是按名字排序

$ kubectl get pod --sort-by .metadata.name
```

## 2.找出pod中的错误日志

```bash
# 要求是把错误内容输出到某个文件中，可以粘贴，也可以直接重定向文件

$ kubectl logs mypod-798fcd9949-lk9rc | grep error > xx.log
```

## 3.创建一个pod ，并调度到某个节点上

```bash
$ cat > pod.yaml << EOF
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    env: test
spec:
  containers:
  - name: nginx
    image: nginx
    imagePullPolicy: IfNotPresent
  nodeSelector:
    disktype: ssd
EOF

$ kubectl create -f pod.yaml
```

## 4.列出正常节点的个数

```bash
$ kubectl get node | grep -w Ready
```

## 5.pod中挂载volume

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pd
spec:
  containers:
  - image: k8s.gcr.io/test-webserver
    name: test-container
    volumeMounts:
    - mountPath: /cache
      name: cache-volume
  volumes:
  - name: cache-volume
    emptyDir: {}
```

更详细用法参考官方文档：https://kubernetes.io/docs/concepts/storage/volumes/


## 6.提供一个pod，添加init-container ,在container中添加一个空文件，启动的时候。在另一个containre中检测是否有这个文件，否则退出


```yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: nginx-pod
  name: nginx-pod
spec:
  containers:
  - image: nginx
    name: nginx-pod
    command: ['sh','-c','if [ -f "a.txt" ]; then  echo xx ;fi']
    ports:
    - containerPort: 80
    resources: {}
    volumeMounts:
    - name: workdir
      mountPath: /usr/nginx/html
  dnsPolicy: ClusterFirst
  initContainers:
  - image: busybox
    name: initcheck
    command: ['sh','-c','touch /tmp/index.html']
    volumeMounts:
    - name: workdir
      mountPath: /tmp
  volumes:
  - name: workdir
    emptyDir: {}
```

## 7.创建pod，再创建一个service

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nats
  labels:
    app: nats
spec:
  containers:
    - name: nats
      image: nats

---
apiVersion: v1
kind: Service
metadata:
  name: nats
spec:
  selector:
    app: nats
  ports:
    - port: 4222
      nodePort: 32222
  type: NodePort
```

## 8.在一个pod中创建2个容器，如redis+nginx

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo
spec:
  containers:
  - image: nginx
    name: nginx
  - image: redis
    name: redis
```

## 9.找到指定service下的pod中，cpu利用率按高到底排序
    
```bash
$ kubectl top pods --selector="app=demo" | grep -v NAME | sort -k 2 -nr
```

## 10.创建一个简单的daemonset

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-elasticsearch
  namespace: kube-system
  labels:
    k8s-app: fluentd-logging
spec:
  selector:
    matchLabels:
      name: fluentd-elasticsearch
  template:
    metadata:
      labels:
        name: fluentd-elasticsearch
    spec:
      tolerations:
      # this toleration is to have the daemonset runnable on master nodes
      # remove it if your masters can't run pods
      - key: node-role.kubernetes.io/master
        effect: NoSchedule
      containers:
      - name: fluentd-elasticsearch
        image: quay.io/fluentd_elasticsearch/fluentd:v2.5.2
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      terminationGracePeriodSeconds: 30
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

## 11.deployment的扩容 ，scale命令

```bash
$ kubectl scale --replicas=4 deployment demo
```

## 12 创建secret，有一个paasword字段（手动base64加密），创建两个pod引用该secret，一个用env ,一个用volume来调用

```bash
$ echo -n 'admin' | base64

YWRtaW4=

$ echo -n '1f2d1e2e67df' | base64

MWYyZDFlMmU2N2Rm
```

现在可以像这样写一个 `secret` 对象：

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
data:
  username: YWRtaW4=
  password: MWYyZDFlMmU2N2Rm
```

使用 kubectl apply 创建 secret：

```bash
$ kubectl apply -f ./secret.yaml
```

`Pod` 中使用 `Secret` 作为`环境变量`的示例：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-env-pod
spec:
  containers:
  - name: mycontainer
    image: redis
    env:
      - name: SECRET_USERNAME
        valueFrom:
          secretKeyRef:
            name: mysecret
            key: username
      - name: SECRET_PASSWORD
        valueFrom:
          secretKeyRef:
            name: mysecret
            key: password
  restartPolicy: Never
```

`Pod` 中使用 `volume` 挂在 `secret` 的例子：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
  - name: mypod
    image: redis
    volumeMounts:
    - name: foo
      mountPath: "/etc/foo"
      readOnly: true
  volumes:
  - name: foo
    secret:
      secretName: mysecret
```

> 官方链接：https://kubernetes.io/docs/concepts/configuration/secret/


## 13.先将nginx:1.9的deployment，升级到nginx:1.11，记录下来(—record)，然后回滚到1.9

升级

```bash
$ kubectl set image deployments demo demo=nginx:1.11 --record
```

回滚

```bash
$ kubectl rollout undo deployment demo
```

## 14.使用 nslookup 查看service 和pod的dns

> service 和pod 的创建用之前的 yaml

```bash
# 查看 dns
$ kubectl run -it --image busybox:1.28.4  dnstest --rm /bin/sh

# 查看 sevice
$ nslookup svc-demo.kube-system.svc.cluster.local

# 查看 pod
# 查看pod ip时，要把1.2.3.4换成1-2-3-4，否则会报错
$ nslookup 1-2-3-4.default.pod.cluster.local
```
> 参考文档：https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/

## 15.etcdctl 来 备份etcd

```bash
# 先声明环境变量ETCDCTL_API=3 ，不然etcdctl 是v2版本
$ ETCDCTL_API=3 etcdctl --cacert=/opt/kubernetes/ssl/ca.pem --cert=/opt/kubernetes/ssl/server.pem --key=/opt/kubernetes/ssl/server-key.pem --endpoints=https://192.168.1.36:2379 snapshot save /data/etcd_backup_dir/etcd-snapshot-`date +%Y%m%d`.db
```

> 参考文档地址：https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/


## 16.static pod 的使用

找到 `--pod-manifest-path=/etc/kubelet.d/` 配置的位置，然后把 pod 的 yaml 放进去

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: static-web
  labels:
    role: myrole
spec:
  containers:
    - name: web
      image: nginx
      ports:
        - name: web
          containerPort: 80
          protocol: TCP
```

> 参考文档地址：https://kubernetes.io/docs/tasks/administer-cluster/static-pod/

## 17.在一个新的namespace创建pod

先创建 ns

```bash
# 创建 ns
$ kubectl create namespace test
```

再创建 pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo
  namespace: test
spec:
  containers:
  - image: nginx
    name: nginx
```

## 18.pv 类型 hostpath 位置在/data，大小为1G, readonly 模式

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: example-pv
spec:
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes:
  - ReadOnlyMany
  persistentVolumeReclaimPolicy: Delete
  local:
    path: /data
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - test-node
```
> 参考文档地址：https://kubernetes.io/docs/concepts/storage/persistent-volumes/


## 20.给pod创建service

Pod 配置文件

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx
    imagePullPolicy: IfNotPresent
```

service 配置文件，通过 `labels app=nginx` 关联 pod

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  ports:
  - port: 80
    protocol: TCP
  selector:
    app: nginx
```
    
## 21.使用node selector，选择disk为ssd的机器调度
    
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    env: test
spec:
  containers:
  - name: nginx
    image: nginx
    imagePullPolicy: IfNotPresent
  nodeSelector:
    disktype: ssd
```

## 22.排查apiserver连接不上问题：

下面例举一些可能导致的原因：

- 1、apiserver 有负载均衡，负载均衡服务有问题，或者负载均衡服务连接不上后端apiserver
- 2、TLS证书过期，分两种情况：
  - 2.1、整个集群证书过期
  - 2.2、ETCD证书和K8S集群证书分开颁发，只有ETCD集群证书过期，或者k8s内部证书过期
- 3、apiserver 服务连接过多，导致连接不上
- 4、k8s集群规则大，导致etcd集群响应慢，apiserver接口服务也受到影响（因为 apiserver 是k8s集群唯一数据查询与写入口）

还有其它原因，本文只例举这些。

## 23.把一个node弄成unavailable 并且把上边的pod重新调度去新的node上
    
```bash
$ kubectl drain ${node-name} --delete-local-data=true --ignore-daemonsets=true
```

## 真题日期

- 日期：2019年5月
- 版本：k8s 1.13

## 参考链接

- https://www.jianshu.com/p/f81d191ee03b