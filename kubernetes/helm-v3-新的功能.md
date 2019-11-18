## Helm 是什么？
Helm 是一个命令行下的客户端工具。主要用于 Kubernetes 应用程序 Chart 的`创建`、`打包`、`发布`以及创建和管理本地和远程的 Chart 仓库。

## Helm 解决什么痛点？
- 如何统一管理、配置和更新分散的`k8s yaml`资源文件
- 如何分发和复用一套应用模板
- 如何将应用的一系列资源当做一个软件包管理
- 如何统一下架一个服务在k8s创建的所有资源

## Helm v3 与 v2 变化
- 最明显的变化删除 `Tiller`
![](https://www.yp14.cn/img/helm-v2-v3.jpeg)

- `Release` 不再是全局资源，而是存储在各自命名空间内

- `Helm 2`默认情况下使用`ConfigMaps`存储版本信息。在`Helm 3`中，将`Secrets`用作默认存储驱动程序

- 把`requirements.yaml`合并成`Chart.yaml`

- `helm install`需要提供名称，如果实在不想提供名称，指定参数`--generate-name`，在v2时可以不提供，不提供名称时将自动生成一个名称，这功能比较令人讨厌

- 去除用于本地临时搭建`Chart Repository`的`helm serve`命令

- `Values`支持`JSON Schema`校验器，自动检查所有输入的变量格式

- `helm cli`命令重命名
```bash
helm delete  重命名为 helm uninstall
helm delete  重命名为 helm uninstall
helm fetch   重命名为 helm pull
helm inspect 重命名为 helm show

以上命令虽然重命名，但旧命令仍然可用
```

- 命名空间不存在，`helm 2`会自动创建命名空间，`helm 3`会遵守`Kubernetes`行为，返回错误

## Helm 3 功能更强大，赶快来使用吧！

- [安装 Helm 文档](https://helm.sh/docs/intro/install/)
- [Helm v3文档](https://helm.sh/docs/)
- [从helm v2 迁移到 helm v3 文档](https://helm.sh/docs/topics/v2_v3_migration/)
- [帮助从 Helm 2 迁移到 Helm 3 的插件](https://github.com/helm/helm-2to3)