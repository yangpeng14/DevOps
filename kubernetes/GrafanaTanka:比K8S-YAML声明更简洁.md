## 前言

`Grafana Tanka` 是 Kubernetes 集群的配置工具，由 `Jsonnet` 数据模板语言实现。

使用它比使用 `Yaml` 来定义 Kubernetes 资源`更简洁`。`Jsonnet` 高度可重用，使你能通过组合现成的库来实现你的技术栈。

## Grafana Tanka 亮点

- `干净`：使用 `Jsonet` 语言表示你的Kubernetes应用，比YAML更简洁。
- `可重用`：构建应用程序库，将它们导入任何地方，甚至在GitHub上共享它们！
- `简洁`：使用Kubernetes库，不再需要模板。
- `变化`：以轻松地知道确切的变化。
- `生产环境Ready`：Tanka 部署了 Grafana Cloud 和更多生产设置。
- `开源`：就像广受欢迎的 `Grafana` 和 `Loki` 项目一样，Tanka 是完全开源的。

## K8S Yaml 与 Tanka 方式对比

### K8S Yaml 声明

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
spec:
  selector:
    matchLabels:
      name: grafana
  template:
    metadata:
      labels:
        name: grafana
    spec:
      containers:
        - image: grafana/grafana
          name: grafana
          ports:
            - containerPort: 3000
              name: ui
```

### Tanka 方式声明

```json
local k = import "k.libsonnet";

{
    grafana: k.apps.v1.deployment.new(
        name="grafana",
        replicas=1,
        containers=[k.core.v1.container.new(
            name="grafana",
            image="grafana/grafana",
        )]
    )
}
```

> - 官方文档：https://tanka.dev/
> - GitHub地址：https://github.com/grafana/tanka