## 一、部署要求

Apache Airflow 已通过以下测试：

|                      | Main version (dev)        | Stable version (2.1.4)   |
| -------------------- | ------------------------- | ------------------------ |
| Python               | 3.6, 3.7, 3.8, 3.9        | 3.6, 3.7, 3.8, 3.9       |
| Kubernetes           | 1.20, 1.19, 1.18          | 1.20, 1.19, 1.18         |
| PostgreSQL           | 9.6, 10, 11, 12, 13       | 9.6, 10, 11, 12, 13      |
| MySQL                | 5.7, 8                    | 5.7, 8                   |
| SQLite               | 3.15.0+                   | 3.15.0+                  |
| MSSQL(Experimental)  | 2017,2019                 |                          


**注意:** MySQL 5.x 版本不能或有运行多个调度程序的限制——请参阅调度程序文档。MariaDB 未经过测试/推荐。

**注意:** SQLite 用于 Airflow 测试。不要在生产中使用它。我们建议使用最新的 SQLite 稳定版本进行本地开发。

> PS：本文部署 `Airflow` 稳定版 `2.1.4`，`Kubernetes`使用`1.20.x`版本，`PostgreSQL`使用`12.x`，使用`Helm Charts`部署。

## 二、生成Helm Charts配置

> PS：使用 helm 3 版本部署

```bash
# 创建kubernetes airflow 命名空间
$ kubectl create namespace airflow

# 添加 airflow charts 仓库源
$ helm repo add apache-airflow https://airflow.apache.org

# 更新 aiarflow 源
$ helm repo update

# 查看 airflow charts 所有版本（这里选择部署charts 1.2.0，也就是airflow 2.1.4）
$ helm search repo apache-airflow/airflow -l

NAME                  	CHART VERSION	APP VERSION	DESCRIPTION
apache-airflow/airflow	1.3.0        	2.2.1      	The official Helm chart to deploy Apache Airflo...
apache-airflow/airflow	1.2.0        	2.1.4      	The official Helm chart to deploy Apache Airflo...
apache-airflow/airflow	1.1.0        	2.1.2      	The official Helm chart to deploy Apache Airflo...
apache-airflow/airflow	1.0.0        	2.0.2      	Helm chart to deploy Apache Airflow, a platform...

# 导出 airflow charts values.yaml 文件
$ helm show values apache-airflow/airflow --version 1.2.0 > airflow_1.2.4_values.yaml
```

## 三、修改airflow配置

### 3.1 配置持续存储 StorageClass

> PS: 使用阿里云`NAS极速存储`

```bash
# 编辑 StorageClass 文件
$ vim alicloud-nas-airflow-test.yaml

apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: alicloud-nas-airflow-test
mountOptions:
  - nolock,tcp,noresvport
  - vers=3
parameters:
  volumeAs: subpath
  server: "xxxxx.cn-beijing.extreme.nas.aliyuncs.com:/share/airflow/"
provisioner: nasplugin.csi.alibabacloud.com
reclaimPolicy: Retain

# 应用到K8S中
$ kubectl apply -f alicloud-nas-airflow-test.yaml
```

### 3.2 配置 airflow Dags 存储仓库 gitSshKey

```bash
# 编辑 airflow-ssh-secret.yaml 文件，首先需要把shh公钥添加到git项目仓库中
$ vim airflow-ssh-secret.yaml

apiVersion: v1
kind: Secret
metadata:
  name: airflow-ssh-secret
  namespace: airflow
data:
  # key needs to be gitSshKey
  gitSshKey: "ssh私钥，base64"

# 应用到K8S中
$ kubectl apply -f airflow-ssh-secret.yaml
```

### 3.3 Docker 部署 PostgreSQL 12

```bash
# 创建 postgresql 存储目录
$ mkdir /data/postgresql_data

# 创建启动文件 
$ vim docker-compose.yaml

version: "3"

services:
  airflow-postgres:
    image: postgres:12
    restart: always
    container_name: airflow-postgres
    environment:
      TZ: Asia/Shanghai
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: Airflow123
    volumes:
      - /data/postgresql_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

# 启动 postgresql docker
$ docker-compose up -d
```

### 3.4 修改 airflow_1.2.4_values.yaml 配置

> PS：本文 airflow_1.2.4_values.yaml 配置文件需要三个pvc，服务分别是 redis、worker(只部署1个worker，可以部署多个worker)、dags

因配置文件太长，不具体贴出，具体内容请参考下面链接：

[Airflow Charts 1.2.4 Values配置文件](../config_dir/airflow_1.2.4_values.yaml)

## 四、部署 Airfolw

```bash
# 第一次部署 Airflow
$ helm install airflow apache-airflow/airflow --namespace airflow --version 1.2.0 -f airflow_1.2.4_values.yaml

# 以后如果要修改airflow配置，请使用下面命令
$ helm upgrade --install airflow apache-airflow/airflow --namespace airflow --version 1.2.0 -f airflow_1.2.4_values.yaml
```

## 五、配置 Airflow Ingress Nginx 访问入口

```bash
# 生成 ingress nginx 配置文件
$ vim airflow-ingress.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: airflow
  namespace: airflow
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
spec:
  rules:
  - host: "airflow.example.com"
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: airflow-webserver
            port:
              number: 8080

# 应用到K8S中
$ kubectl apply -f airflow-ingress.yaml
```

## 六、参考链接

- 1、https://github.com/apache/airflow/tree/2.1.4
- 2、https://airflow.apache.org/docs/helm-chart/1.2.0/index.html