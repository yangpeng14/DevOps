一 背景
====

1.1 配置中心问题
----------

在云原生中配置中心，例如：`Configmap`和`Secret`对象，虽然可以进行直接更新资源对象

*   对于引用这些有些不变的配置是可以打包到镜像中的，那可变的配置呢？
*   信息泄漏，很容易引发安全风险，尤其是一些敏感信息，比如密码、密钥等。
*   每次配置更新后，都要重新打包一次，升级应用。镜像版本过多，也给镜像管理和镜像中心存储带来很大的负担。
*   定制化太严重，可扩展能力差，且不容易复用。

1.2 使用方式
--------

`Configmap`或`Secret`使用有两种方式，一种是`env`系统变量赋值，一种是`volume`挂载赋值，env写入系统的configmap是不会热更新的，而volume写入的方式支持热更新！

*   对于env环境的，必须要滚动更新pod才能生效，也就是删除老的pod，重新使用镜像拉起新pod加载环境变量才能生效。
*   对于volume的方式，虽然内容变了，但是需要我们的应用直接监控configmap的变动，或者一直去更新环境变量才能在这种情况下达到热更新的目的。

应用不支持热更新，可以在业务容器中启动一个sidercar容器，监控configmap的变动，更新配置文件，或者也滚动更新pod达到更新配置的效果。

二 解决方案
======

ConfigMap 和 Secret 是 Kubernetes 常用的保存配置数据的对象，你可以根据需要选择合适的对象存储数据。通过 Volume 方式挂载到 Pod 内的，kubelet 都会定期进行更新。但是通过环境变量注入到容器中，这样无法感知到 ConfigMap 或 Secret 的内容更新。

目前如何让 Pod 内的业务感知到 ConfigMap 或 Secret 的变化，还是一个待解决的问题。但是我们还是有一些 Workaround 的。

如果业务自身支持 reload 配置的话，比如nginx -s reload，可以通过 inotify 感知到文件更新，或者直接定期进行 reload（这里可以配合我们的 readinessProbe 一起使用）。

如果我们的业务没有这个能力，考虑到不可变基础设施的思想，我们是不是可以采用滚动升级的方式进行？没错，这是一个非常好的方法。目前有个开源工具Reloader，它就是采用这种方式，通过 watch ConfigMap 和 Secret，一旦发现对象更新，就自动触发对 Deployment 或 StatefulSet 等工作负载对象进行滚动升级。

三 reloader简介
============

3.1 reloader简介
--------------

`Reloader` 可以观察 ConfigMap 和 Secret 中的变化，并通过相关的 deploymentconfiggs、 deploymentconfiggs、 deploymonset 和 statefulset 对 Pods 进行滚动升级。

3.2 reloader安装
--------------

*   helm安装

```yaml
$ helm repo add stakater https://stakater.github.io/stakater-charts
$ helm repo update
$ helm install stakater/reloader
```

*   Kustomize

```yaml
$ kubectl apply -k https://github.com/stakater/Reloader/deployments/kubernetes
```

*   资源清单安装

```yaml
$ kubectl apply -f https://raw.githubusercontent.com/stakater/Reloader/master/deployments/kubernetes/reloader.yaml

clusterrole.rbac.authorization.k8s.io/reloader-reloader-role created
clusterrolebinding.rbac.authorization.k8s.io/reloader-reloader-role-binding created
deployment.apps/reloader-reloader created
serviceaccount/reloader-reloader created


NAME                                     READY   STATUS    RESTARTS   AGE
pod/reloader-reloader-66d46d5885-nx64t   1/1     Running   0          15s

NAME                                READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/reloader-reloader   1/1     1            1           16s

NAME                                           DESIRED   CURRENT   READY   AGE
replicaset.apps/reloader-reloader-66d46d5885   1         1         1       16s
```

`reloader` 能够配置忽略cm或者secrets资源，可以通过配置在reader deploy中的spec.template.spec.containers.args，如果两个都忽略，那就缩小deploy为0，或者不部署reoader。

| Args | Description |
| --- | --- |
| \--resources-to-ignore=configMaps | To ignore configMaps |
| \--resources-to-ignore=secrets | To ignore secrets |


3.3 配置
------

### 3.3.1 自动更新

`reloader.stakater.com/search` 和 `reloader.stakater.com/auto` 并不在一起工作。如果你在你的部署上有一个 reloader.stakater.com/auto : "true"的注释，该资源对象引用的所有configmap或这secret的改变都会重启该资源，不管他们是否有 reloader.stakater.com/match : "true"的注释。

```yaml
kind: Deployment
metadata:
  annotations:
    reloader.stakater.com/auto: "true"
spec:
  template: metadata:
```

### 3.3.2 制定更新

指定一个特定的configmap或者secret，只有在我们指定的配置图或秘密被改变时才会触发滚动升级，这样，它不会触发滚动升级所有配置图或秘密在部署，后台登录或状态设置中使用。

一个制定deployment资源对象，在引用的configmap或者secret种，只有`reloader.stakater.com/match: "true"`为true才会出发更新，为false或者不进行标记，该资源对象都不会监视配置的变化而重启。

```yaml
kind: Deployment
metadata:
  annotations:
    reloader.stakater.com/search: "true"
spec:
  template:
```

cm配置

```yaml
kind: ConfigMap
metadata:
  annotations:
    reloader.stakater.com/match: "true"
data:
  key: value
```

### 3.3.3 指定cm

如果一个deployment挂载有多个cm或者的场景下，我们只希望更新特定一个cm后，deploy发生滚动更新，更新其他的cm，deploy不更新，这种场景可以将cm在deploy中指定为单个或着列表实现。

例如：一个deploy有挂载nginx-cm1和nginx-cm2两个configmap，只想nginx-cm1更新的时候deploy才发生滚动更新，此时无需在两个cm中配置注解，只需要在deploy中写入`configmap.reloader.stakater.com/reload:nginx-cm1`，其中nginx-cm1如果发生更新，deploy就会触发滚动更新。

如果多个cm直接用逗号隔开

```yaml
# configmap对象
kind: Deployment
metadata:
  annotations:
    configmap.reloader.stakater.com/reload: "nginx-cm1"
spec:
  template: metadata:
```

```yaml
# secret对象
kind: Deployment
metadata:
  annotations:
    secret.reloader.stakater.com/reload: "foo-secret"
spec:
  template: metadata:
```

> 无需在cm或secret中添加注解，只需要在引用资源对象中添加注解即可。

四 测试
====

4.1 deploy
----------

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:   
    reloader.stakater.com/search: "true"
  labels:
    run: nginx
  name: nginx
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      run: nginx
  template:
    metadata:
      labels:
        run: nginx
    spec:
      containers:
      - image: nginx
        name: nginx
        volumeMounts:       
        - name: nginx-cm
          mountPath: /data/cfg
          readOnly: true
      volumes:      
      - name: nginx-cm
        configMap:          
          name: nginx-cm
          items:          
          - key: config.yaml        
            path: config.yaml
            mode: 0644 
```

4.2 configmap
-------------

```yaml
apiVersion: v1
data:
  config.yaml: |
    # project settings
    DEFAULT_CONF:
      port: 8888 
    UNITTEST_TENCENT_ZONE: ap-chongqing-1
kind: ConfigMap
metadata:
  name: nginx-cm
  annotations:
    reloader.stakater.com/match: "true"
```

4.3 测试
------

```shell
$ kubectl  get pod
NAME                     READY   STATUS    RESTARTS   AGE
nginx-68c9bf4ff7-9gmg6   1/1     Running   0          10m

$ kubectl  get cm
NAME       DATA   AGE
nginx-cm   1      28m

# 更新cm内容

$ kubectl edit cm nginx-cm 

configmap/nginx-cm edited

# 查看po发生了滚动更新，重新加载配置文件
$ kubectl get pod

NAME                     READY   STATUS              RESTARTS   AGE
nginx-66c758b548-9dllm   0/1     ContainerCreating   0          4s
nginx-68c9bf4ff7-9gmg6   1/1     Running             0          10m
```

五 Reloader 使用注意事项
======

*   Reloader 为全局资源对象，建议部署在一个公共服务的ns下，然后其他ns也可以正常使用reloader特性。
    
*   Reloader.stakater.com/auto : 如果配置configmap或者secret在 deploymentconfigmap/deployment/daemonsets/Statefulsets
    
*   secret.reloader.stakater.com/reload 或者 configmap.reloader.stakater.com/reload 注释中被使用，那么 true 只会重新加载 pod，不管使用的是 configmap 还是 secret。
    
*   reloader.stakater.com/search 和 reloader.stakater.com/auto 不能同时使用。如果你在你的部署上有一个 reloader.stakater.com/auto : "true"的注释，那么它总是会在你修改了 configmaps 或者使用了机密之后重新启动，不管他们是否有 reloader.stakater.com/match : "true"的注释。
    

六 反思
====

Reloader通过 watch ConfigMap 和 Secret，一旦发现对象更新，就自动触发对 Deployment 或 StatefulSet 等工作负载对象进行滚动升级。

如果我们的应用内部没有去实时监控配置文件，利用该方式可以非常方便的实现配置的热更新。


参考链接
====

- https://github.com/stakater/Reloader

> - 作者: kaliarch
> - 原文出处: https://juejin.cn/post/6897882769624727559