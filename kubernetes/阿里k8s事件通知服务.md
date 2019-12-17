## 背景

在 Kubernetes 开源生态中，资源监控有 `metrics-server`、`Prometheus`等，但这些监控并不能实时推送 Kubernetes 事件，监控准确性也不足。当 kubernetes 集群中发生 Pod因为 OOM 、拉取不到镜像、健康检查不通过等错误导致重启，集群管理员其实是不知道的，因为 Kubernetes 有自我修复机制，Pod宕掉，可以重新启动一个。这样让集群管理员很难立即发现服务问题。


## Kubernetes 事件

Kubernetes中，事件分为两种：

- `Warning事件`：表示产生这个事件的状态转换是在非预期的状态之间产生的
- `Normal事件`：表示期望到达的状态，和目前达到的状态是一致的

例子：

```bash
$ kubectl get events

LAST SEEN   TYPE      REASON              OBJECT                                       MESSAGE
58m         Normal    ScalingReplicaSet   deployment/demo                     Scaled down replica set demo-8b85c64cb to 0
5m7s        Warning   Unhealthy           pod/demo-79844f78b8-nd5jz   Readiness probe failed: Get http://192.168.1.68:8080/healthCheck: dial tcp 192.168.1.68:8080: connect: connection refused
```

## 如何监听k8s事件并通知？

阿里云开源 Kubernetes 事件离线工具 `kube-eventer`，能很好的解决这个问题。


## kube-eventer 简介
`kube-eventer` 是一个事件发射器，它将 kubernetes 事件发送到接收器（例如dingtalk，sls，kafka，微信等）。kubernetes 的核心设计概念是`状态机`。因此，`Normal` 当转移到所需状态时会有事件 `Warning`。

## kube-eventer 架构图

![](/img/arch.png)

## 用法

下面是以 `钉钉` 做为接收器，通过钉钉机器人通知到相关人员或者相关群

- 获取钉钉群机器人 `Token`，如下图

    ![](/img/dingtalk-token.png)

- 安装事件处理程序并配置接收器

    ```yaml
    apiVersion: apps/v1beta2
    kind: Deployment
    metadata:
      labels:
        name: kube-eventer
      name: kube-eventer
      namespace: kube-system
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: kube-eventer
      template:
        metadata:
          labels:
            app: kube-eventer
          annotations:	
            scheduler.alpha.kubernetes.io/critical-pod: ''
        spec:
          dnsPolicy: ClusterFirstWithHostNet
          serviceAccount: kube-eventer
          containers:
            - image: registry.aliyuncs.com/acs/kube-eventer-amd64:v1.1.0-63e7f98-aliyun
              name: kube-eventer
              command:
                - "/kube-eventer"
                - "--source=kubernetes:https://kubernetes.default"
                ## .e.g,dingtalk sink demo
                - --sink=dingtalk:[your_webhook_url]&label=[your_cluster_id]&level=[Normal or Warning   (default)]
              env:
              # If TZ is assigned, set the TZ value as the time zone
              - name: TZ
                value: America/New_York
              volumeMounts:
                - name: localtime
                  mountPath: /etc/localtime
                  readOnly: true
                - name: zoneinfo
                  mountPath: /usr/share/zoneinfo
                  readOnly: true
              resources:
                requests:
                  cpu: 100m
                  memory: 100Mi
                limits:
                  cpu: 500m
                  memory: 250Mi
          volumes:
            - name: localtime
              hostPath:
                path: /etc/localtime
            - name: zoneinfo
              hostPath:
                path: /usr/share/zoneinfo
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRole
    metadata:
      name: kube-eventer
    rules:
      - apiGroups:
          - ""
        resources:
          - events
        verbs:
          - get
          - list
          - watch
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRoleBinding
    metadata:
      annotations:
      name: kube-eventer
    roleRef:
      apiGroup: rbac.authorization.k8s.io
      kind: ClusterRole
      name: kube-eventer
    subjects:
      - kind: ServiceAccount
        name: kube-eventer
        namespace: kube-system
    ---
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: kube-eventer
      namespace: kube-system
    ```


- 查看钉钉告警事件

    ![](/img/dingtalk.jpeg)

## 支持下列通知程序

程序名称 | 描述
---|:---
dingtalk | 钉钉机器人
sls | 阿里云sls服务
elasticsearch | elasticsearch 服务
honeycomb | honeycomb 服务
influxdb | influxdb 数据库
kafka | kafka 数据库
mysql | mysql 数据库
wechat | 微信

## 项目地址
> https://github.com/AliyunContainerService/kube-eventer

## 参考链接
- https://github.com/AliyunContainerService/kube-eventer    