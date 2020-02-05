## Zabbix 简介[1]

`Zabbix` 是由 Alexei Vladishev 开发的一种网络监视、管理系统，基于 Server-Client 架构。可用于监视各种网络服务、服务器和网络机器等状态。

`Zabbix` 使用 MySQL、PostgreSQL、SQLite、Oracle 或 IBM DB2 储存资料。Server 端基于 C语言、Web 前端则是基于 PHP 所制作的。Zabbix 可以使用多种方式监视。可以只使用 Simple Check 不需要安装 Client 端，亦可基于 SMTP 或 HTTP 等各种协定做死活监视。在客户端如 UNIX、Windows 中安装 Zabbix Agent 之后，可监视 CPU 负荷、网络使用状况、硬盘容量等各种状态。而就算没有安装 Agent 在监视对象中，Zabbix 也可以经由 SNMP、TCP、ICMP检查，以及利用 IPMI、SSH、telnet 对目标进行监视。另外，Zabbix 包含 XMPP 等各种 Item 警示功能。

## Zabbix 功能和特性[2]

- 安装与配置简单
- 可视化web管理界面
- 免费开源
- 支持中文
- 自动发现
- 分布式监控
- 实时绘图

## 环境
- Kubernetes 版本 1.15.6
- Zabbix 版本 3.4.7 （镜像，在官方基础上修改，下文会具体介绍）
- Mariadb 版本 10.3.5

## Zabbix Dockerfile 修改

`zabbix-server-mysql`：Dockerfile 在官方基础上修改，添加 `python支持`，用于`支持python通知脚本环境`；时区修改为`上海时区`；

```
FROM zabbix/zabbix-server-mysql:alpine-3.4.7

RUN cp /etc/apk/repositories /etc/apk/repositories.bak \
  && echo "http://mirrors.aliyun.com/alpine/v3.4/main/" > /etc/apk/repositories \
  && apk add --update python python-dev py-pip build-base \
  && apk add -U tzdata \
  && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
  && pip install requests configparser \
  && touch /tmp/zabbix_dingding.log \
  && chown zabbix:zabbix /tmp/zabbix_dingding.log \
  && rm -rf /var/cache/apk/*

WORKDIR /var/lib/zabbix

EXPOSE 10051/TCP

VOLUME ["/usr/lib/zabbix/alertscripts", "/usr/lib/zabbix/externalscripts", "/var/lib/zabbix/enc", "/var/lib/zabbix/mibs", "/var/lib/zabbix/modules"]
VOLUME ["/var/lib/zabbix/snmptraps", "/var/lib/zabbix/ssh_keys", "/var/lib/zabbix/ssl/certs", "/var/lib/zabbix/ssl/keys", "/var/lib/zabbix/ssl/ssl_ca"]

ENTRYPOINT ["docker-entrypoint.sh"]
```

`zabbix-web-nginx-mysql`：Dockerfile 在官方基础上修改，添加中文字体，解决查看`web监控时中文乱码`；时区修改为`上海时区`；

`msyh.ttf` 字体，可以从下文已打好的镜像获取。

```
FROM zabbix/zabbix-web-nginx-mysql:alpine-3.4.7

COPY msyh.ttf /usr/share/fonts/ttf-dejavu/DejaVuSans.ttf

RUN cp /etc/apk/repositories /etc/apk/repositories.bak \
  && echo "http://mirrors.aliyun.com/alpine/v3.4/main/" > /etc/apk/repositories \
  && apk add -U tzdata \
  && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
  && rm -rf /var/cache/apk/*

EXPOSE 80/TCP 443/TCP
WORKDIR /usr/share/zabbix
VOLUME ["/etc/ssl/nginx"]

ENTRYPOINT ["docker-entrypoint.sh"]
```

## Zabbix K8S 部署

### 首先部署 Mariadb

PS：`NFS 提供存储`

`$ vim mariadb-pv.yaml`

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mariadb-pv
  namespace: kube-system
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  nfs:
    path: /nfs-data/mariadb_db_data
    server: 192.16.3.6
```

`$ vim mariadb-pvc.yaml`

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mariadb-pvc
  namespace: kube-system
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 100Gi
```

`$ vim mariadb-deploy.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mariadb-server
  namespace: kube-system
  labels:
    name: mariadb-server
spec:
  ports:
  - port: 3306
    targetPort: 3306
    protocol: TCP
  selector:
    name: mariadb-server

---

apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: mariadb-server
  namespace: kube-system
  labels:
    name: mariadb-server
spec:
  replicas: 1
  revisionHistoryLimit: 3
  strategy:
    rollingUpdate:
      maxSurge: 30%
      maxUnavailable: 30%
  template:
    metadata:
      labels:
        name: mariadb-server
    spec:
      volumes:
        - name: mariadb-storage
          persistentVolumeClaim:
            claimName: mariadb-pvc
      hostname: mariadb-server
      containers:
      - name: mariadb-server
        image: yangpeng2468/mariadb:10.3.5
        resources:
         limits:
           cpu: 400m
           memory: 1024Mi
         requests:
           cpu: 100m
           memory: 100Mi
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: "Password"
        volumeMounts:
          - name: mariadb-storage
            mountPath: /var/lib/mysql
```

```bash
# 部署 Mariadb

$ kubectl apply -f mariadb-pv.yaml
$ kubectl apply -f mariadb-pvc.yaml
$ kubectl apply -f mariadb-deploy.yaml
```

### 部署 Configmap 通知钉钉脚本

`$ vim zabbix-dingding-conf-configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: zabbix-dingding-conf
  namespace: kube-system
data:
  dingding.conf: |
    [config]
    #此文件注意权限
    log=/tmp/zabbix_dingding.log
    webhook=https://oapi.dingtalk.com/robot/send?access_token=${钉钉机器人token}
```

`$ vim zabbix-dingding-script-configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: zabbix-dingding-script
  namespace: kube-system
data:
  zabbix_dingding.py: |
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    import requests
    import json
    import sys
    import time
    import configparser

    Headers = {'Content-Type': 'application/json'}
    Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    config = configparser.ConfigParser()
    config.read('/usr/lib/zabbix/externalscripts/dingding.conf')
    # config.read('/etc/zabbix/dingding.conf')

    log_file = config.get('config', 'log')
    api_url = config.get('config', 'webhook')


    def log(info):
        #注意权限,否则写不进去日志
        with open(log_file, 'a+') as infile:
            infile.write(info)

    def msg(text,user):
        json_text = {
         "msgtype": "text",
            "text": {
                "content": text
            },
            "at": {
                "atMobiles": [
                    user
                ],
                "isAtAll": False
            }
        }

        r = requests.post(api_url, data=json.dumps(json_text), headers=Headers).json()
        code = r["errcode"]
        if code == 0:
            log(Time + ":消息发送成功 返回码:" + str(code) + "\n")
        else:
            log(Time + ":消息发送失败 返回码:" + str(code) + "\n")
            exit(3)

    if __name__ == '__main__':
        text = sys.argv[3]
        user = sys.argv[1]
        msg(text, user)
```

```bash
# 部署

$ kubectl apply -f zabbix-dingding-conf-configmap.yaml zabbix-dingding-script-configmap.yaml
```

### 部署 zabbix-server

`$ vim zabbix-server-deploy.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: zabbix-server
  namespace: kube-system
  labels:
    app: zabbix-server
spec:
  type: NodePort
  ports:
  - port: 10051
    targetPort: 10051
    nodePort: 30017
    protocol: TCP
  selector:
    app: zabbix-server

---

apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: zabbix-server
  namespace: kube-system
  labels:
    app: zabbix-server
spec:
  replicas: 1
  revisionHistoryLimit: 3
  strategy:
    rollingUpdate:
      maxSurge: 30%
      maxUnavailable: 30%
  template:
    metadata:
      labels:
        app: zabbix-server
    spec:
      hostname: zabbix-server
      volumes:
        - name: zabbix-dingding-script
          configMap:
            name: zabbix-dingding-script
            defaultMode: 0775
        - name: zabbix-dingding-conf
          configMap:
            name: zabbix-dingding-conf
            defaultMode: 0664
      containers:
      - name: zabbix-server
        image: yangpeng2468/zabbix-server-mysql:3.4.7
        imagePullPolicy: IfNotPresent
        resources:
         limits:
           cpu: 400m
           memory: 1024Mi
         requests:
           cpu: 100m
           memory: 100Mi
        ports:
        - containerPort: 10051
        env:
        - name: DB_SERVER_HOST
          value: "mariadb-server"
        - name: MYSQL_USER
          value: "zabbix"
        - name: MYSQL_PASSWORD
          value: "zabbix"
        - name: MYSQL_DATABASE
          value: "zabbix"
        - name: ZBX_CACHESIZE
          value: "1024M"
        - name: TZ
          value: "Asia/Shanghai"
        volumeMounts:
          - name: zabbix-dingding-script
            mountPath: /usr/lib/zabbix/alertscripts
          - name: zabbix-dingding-conf
            mountPath: /usr/lib/zabbix/externalscripts
```

```bash
# 部署

$ kubectl apply -f zabbix-server-deploy.yaml
```

### 部署 zabbix-web

`$ vim zabbix-web-deploy.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: zabbix-web
  namespace: kube-system
  labels:
    app: zabbix-web
spec:
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
  selector:
    app: zabbix-web

---

apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: zabbix-web
  namespace: kube-system
  labels:
    app: zabbix-web
spec:
  replicas: 1
  revisionHistoryLimit: 3
  strategy:
    rollingUpdate:
      maxSurge: 30%
      maxUnavailable: 30%
  template:
    metadata:
      labels:
        app: zabbix-web
    spec:
      hostname: zabbix-web
      containers:
      - name: zabbix-web
        image: yangpeng2468/zabbix-web-nginx-mysql:3.4.7
        imagePullPolicy: IfNotPresent
        resources:
         limits:
           cpu: 300m
           memory: 600Mi
         requests:
           cpu: 100m
           memory: 100Mi
        ports:
        - containerPort: 80
        env:
        - name: DB_SERVER_HOST
          value: "mariadb-server"
        - name: ZBX_SERVER_HOST
          value: "zabbix-server"
        - name: MYSQL_USER
          value: "zabbix"
        - name: MYSQL_PASSWORD
          value: "zabbix"
        - name: TZ
          value: "Asia/Shanghai"
        - name: PHP_TZ
          value: "Asia/Shanghai"
```

```bash
# 部署

$ kubectl apply -f zabbix-web-deploy.yaml
```

### 部署 zabbix-agent

zabbix-agent 这里不在细讲，如果使用 Docker或者k8s 部署，可以使用官方镜像 `zabbix/zabbix-agent:alpine-3.4.7`。也可直接下载官方安装包，部署在宿主机上，这里根据自己实际需要部署客户端。

## Zabbix Dashboard

上面部署成功后，根据自己实际环境，设置外网访问k8s集群入口，Zabbix Dashboard 如下展示：

![](/img/zabbix-dashboard.png)

## 参考链接

- [1]https://zh.wikipedia.org/wiki/Zabbix
- [2]https://yq.aliyun.com/articles/525926