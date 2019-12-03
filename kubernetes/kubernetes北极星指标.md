## polaris 简介

`Polaris`：它会进行`各种检查`以确保`使用最佳实践`来配置 `Kubernetes pod` 和 `controllers` ，从而帮助您避免将来出现的问题。

## Polaris Dashboard 展示
![](https://www.yp14.cn/img/dashboard-polaris.png)

## Polaris 可以在几种不同的模式下运行

- `作为 dashboard`：您可以审核集群内部正在运行的内容
- `作为 webhook`：您可以自动拒绝不遵守规定策略的工作负载
- `作为 命令行工具`：您可以测试本地YAML文件，例如，作为 CI/CD 流程的一部分

## Polaris 检查分为以下几类

- Health Checks
- Images
- Networking
- Resources
- Security

## Dashboard 快速入门
```bash
$ kubectl apply -f https://github.com/FairwindsOps/polaris/releases/latest/download/dashboard.yaml

$ kubectl port-forward --namespace polaris svc/polaris-dashboard 8080:80

# 浏览器访问 http://localhost:8080
```

## Dashboard Helm 安装
```bash
$ helm repo add reactiveops-stable https://charts.reactiveops.com/stable

$ helm upgrade --install polaris reactiveops-stable/polaris --namespace polaris

$ kubectl port-forward --namespace polaris svc/polaris-dashboard 8080:80
```

## Webhook 安装
```bash
# kubectl 安装
$ kubectl apply -f https://github.com/fairwindsops/polaris/releases/latest/download/webhook.yaml

# Helm 安装
$ helm repo add reactiveops-stable https://charts.reactiveops.com/stable

$ helm upgrade --install polaris reactiveops-stable/polaris --namespace polaris \
  --set webhook.enable=true --set dashboard.enable=false
```

## CLI 安装 和 使用CI/CD运行

- 请参考链接 https://github.com/FairwindsOps/polaris/blob/master/docs/usage.md

## 项目地址

- https://github.com/FairwindsOps/polaris

## 参考链接

- https://github.com/FairwindsOps/polaris
- https://github.com/FairwindsOps/polaris/blob/master/docs/usage.md