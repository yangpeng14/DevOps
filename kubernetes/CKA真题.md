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

参考官方文档：https://kubernetes.io/docs/concepts/storage/volumes/


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

```
这个文档里面全都有，记住链接

https://kubernetes.io/docs/concepts/configuration/secret/
```

*   13.先将nginx:1.9的deployment，升级到nginx:1.11，记录下来(—record)，然后回滚到1.9

升级

```
kubectl set image deployments demo demo=nginx:1.11 --record


```

回滚

```
kubectl rollout undo deployment demo


```

*   14.使用ns lookup 查看service 和pod的dns

```
service和pod的创建用之前的yaml


```

```
查看dns

kubectl run -it --image busybox:1.28.4  dnstest --rm /bin/sh


sevice:

nslookup svc-demo.kube-system.svc.cluster.local


pod:

nslookup 1-2-3-4.default.pod.cluster.local


查看pod ip时，要把1.2.3.4换成1-2-3-4，否则会报错

对应的文档：https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/



```

```
ETCDCTL_API=3 etcdctl --endpoints ....snapshot save  xxx 根据-h提示写就行了

先声明环境变量ETCDCTL_API=3 ，不然etcdctl 是v2版本

这个文档：

文档地址：https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/



```

```

文档地址：https://kubernetes.io/docs/tasks/administer-cluster/static-pod/


找到--pod-manifest-path=/etc/kubelet.d/配置的位置，然后把pod的yaml放进去

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

先创建ns，在创建pod，和前面步骤类似

*   18.pv 类型hostpath 位置在/data ， 大小为1G , readonly模式

```
文档地址：

https://kubernetes.io/docs/concepts/storage/persistent-volumes/


```

*   20.给pod创建service
    
*   21.使用node selector，选择disk为ssd的机器调度
    

```
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

22.排查apiserver连接不上问题：

```
用的kubeadmin安装的，是kubelet的配置中目录地址有问题


```

*   23.把一个node弄成unavailable 并且把上边的pod重新调度去新的node上
    
    应该是直接drain，需要注意daemonset要强制删除，或者给节点打污点，taint，再去删掉
   