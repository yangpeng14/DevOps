## 前言

对于K8S新手来说，`K8S RBAC` 不能很好的掌握，今天推荐一款非常不错的 `K8S RBAC` 配置工具 `permission-manager`，小白都能配置，并且提供 `Web UI` 界面。

## permission-manager 简介

`permission-manager` 是一个用于 Kubernetes RBAC 和 用户管理工具。

## permission-manager 部署

- 项目地址

    `https://github.com/sighupio/permission-manager`

- 部署依赖

    ```bash
    $ kubectl apply -f k8s/k8s-seeds/namespace.yml
    $ kubectl apply -f k8s/k8s-seeds
    ```

- 设置必填 `Env` 参数

    Env 名称 | 描述
    ---|---
    PORT | 服务器暴露的端口
    CLUSTER_NAME | 在生成kubeconfig文件中使用的集群名称
    CONTROL_PLANE_ADDRESS | 在生成kubeconfig文件中的k8s api 地址
    BASIC_AUTH_PASSWORD | WEB UI 登陆密码（默认用户名为 admin）

- 部署

    ```bash
    $ kubectl apply -f k8s/deploy.yaml
    ```

- 访问 WEB UI

    ```bash
    $ kubectl port-forward svc/permission-manager-service 4000 --namespace permission-manager
    ```

## 如何添加新权限模板

默认只有 `developer` 和 `operation` 模板，模板都是以 `template-namespaced-resources___` 为开头。添加新的权限模板，可以参考 `k8s/k8s-seeds/seed.yml` 文件。

## WEB UI 展示

- 首页

![](/img/first-page.png)

- 创建一个用户

![](/img/permission-manager-2.png)

- 创建的用户摘要

![](/img/permission-manager-3.png)

- 用户 `Kubeconfig` 文件预览

![](/img/permission-manager-4.png)