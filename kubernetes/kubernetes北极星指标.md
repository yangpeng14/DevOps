## polaris 简介

`Polaris`：它会进行`各种检查`以确保`使用最佳实践`来配置 `Kubernetes pod` 和 `controllers` ，从而帮助您避免将来出现问题。

## Polaris 可以在几种不同的模式下运行：

- `作为 dashboard`：您可以审核集群内部正在运行的内容
- `作为 webhook`：您可以自动拒绝不遵守规定策略的工作负载
- `作为 命令行工具`：您可以测试本地YAML文件，例如，作为CI / CD流程的一部分