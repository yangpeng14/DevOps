## 前言

关于 Gitlab CE 部署 与 Gitlab CI 搭建请参考下文

- [Docker Compose 部署 Gitlab-CE](https://www.yp14.cn/2019/08/29/Gitlab-Docker-Compose-%E5%90%AF%E5%8A%A8%E9%85%8D%E7%BD%AE/)
- [Gitlab CI 搭建持续集成环境](https://www.yp14.cn/2019/11/07/Gitlab-CI-%E6%90%AD%E5%BB%BA%E6%8C%81%E7%BB%AD%E9%9B%86%E6%88%90%E7%8E%AF%E5%A2%83/)

## 环境 与 概述

- 一个 hello-world nodejs 项目
- Dockerfile 和 app.dev.yaml（k8s deploy 文件） 存放在业务代码中
- Gitlab CI Build 机器需要安装 `envsubst` 命令
- 构建一个 Docker 业务镜像发布到 Kubernetes 中
- 本项目部署 K8S Service 、HPA 和 Deployment
- `$CI_COMMIT_REF_SLUG` `$CI_COMMIT_SHA` 变量都是 Gitlab CI 内置的变量
- 把 hello-world 项目部署到 Kubernetes default 命名空间中，`NODE_ENV` 使用 `development`

## 演示

### 编写 .gitlab-ci.yml 文件

```bash
$ vim .gitlab-ci.yml
```

```yaml
stages:  # 阶段
  - deploy

deploy_dev:
  stage: deploy
  only:  # 目前 CI 只对 develop、以 feature/.* 开头 和 以 feature-.* 开头分支有效
    - develop
    - /^feature\/.*$/
    - /^feature-.*$/
  tags: # CI tag 名称
    - dev
  script: # 构建命令
    - envsubst < Dockerfile | docker build -t $IMAGE -f - .
    - docker push $IMAGE
    - envsubst < app.dev.yaml | kubectl apply -f -
  variables: # 声明环境变量
    IMAGE: harbor.example.com/default/hello-world-$CI_COMMIT_REF_SLUG:$CI_COMMIT_SHA
    SERVICE_NAME: hello-world-$CI_COMMIT_REF_SLUG
    NAMESPACE: default
    NODE_ENV: development
```

### 编写 app.dev.yaml 文件

```bash
$ vim app.dev.yaml
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: $SERVICE_NAME
  namespace: $NAMESPACE
  labels:
    app: $SERVICE_NAME
spec:
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
  selector:
    app: $SERVICE_NAME

---

apiVersion: autoscaling/v2beta1
kind: HorizontalPodAutoscaler
metadata:
  name: $SERVICE_NAME
  namespace: $NAMESPACE
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: $SERVICE_NAME
  minReplicas: 2
  maxReplicas: 4
  metrics:
  - type: Resource
    resource:
      name: cpu
      targetAverageUtilization: 80
  - type: Resource
    resource:
      name: memory
      targetAverageUtilization: 80

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: $SERVICE_NAME
  namespace: $NAMESPACE
  labels:
    app: $SERVICE_NAME
spec:
  replicas: 1
  revisionHistoryLimit: 3
  strategy:
    rollingUpdate:
      maxSurge: 30%
      maxUnavailable: 30%
  selector:
    matchLabels:
      app: $SERVICE_NAME
  template:
    metadata:
      labels:
        app: $SERVICE_NAME
    spec:
      containers:
      - name: $SERVICE_NAME
        image: $IMAGE
        imagePullPolicy: IfNotPresent
        resources:
          limits:
            cpu: 400m
            memory: 600Mi
          requests:
            cpu: 400m
            memory: 600Mi
        env:
        - name: NODE_ENV
          value: $NODE_ENV
        - name: PORT
          value: "8080"
        livenessProbe:
          httpGet:
            path: /HealthCheck
            port: 8080
            scheme: HTTP
          initialDelaySeconds: 30
          timeoutSeconds: 5
          periodSeconds: 30
          successThreshold: 1
          failureThreshold: 5
        readinessProbe:
          httpGet:
            path: /HealthCheck
            port: 8080
            scheme: HTTP
          initialDelaySeconds: 30
          timeoutSeconds: 5
          periodSeconds: 10
          successThreshold: 1
          failureThreshold: 5
        ports:
        - containerPort: 8080
      imagePullSecrets:
        - name: harbor-certification
```

### 编写 Dockerfile 文件

```bash
$ vim Dockerfile
```

```yaml
FROM harbor.example.com/public/alpine-node:8.11.4

ADD --chown=node:node . /app

USER node

RUN cd /app \
    && yarn install

WORKDIR /app

EXPOSE 8080

CMD ["pm2-docker", "index.js", "--auto-exit", "--watch"]
```

## CI/CD 构建展示

CI 构建

![](/img/gitlab-ci-1.png)

![](/img/gitlab-ci-2.png)

![](/img/gitlab-ci-3.png)

查看部署到 Kubernetes 项目

![](/img/gitlab-ci-4.png)