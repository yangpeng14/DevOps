## Lens 介绍

`Lens` 是一个强大的 kubernetes IDE。可以实时查看 kubernetes 集群状态，比如 Pod实时日志查看、集群Events实时查看、集群故障排查等。有了 Lens，不在需要敲打很长的 kubectl 命令，只要使用鼠标点击几下，非常便捷。

`Lens` 支持多平台安装，目前支持 `Linux`、`MacOS`、`Windows`。

## Lens 优势

- 用户体验性和可用性非常好
- 多集群管理；支持数百个集群
- 独立应用程序；无需在集群中安装任何东西
- 集群状态实时可视化
- 内置 `Prometheus` 提供资源利用率图表和历史趋势图表
- 提供终端访问节点和容器
- 性能经过优化，可应用于大规模集群（已在25k pod的集群进行了测试）
- 完全支持 Kubernetes `RBAC`

## Lens 安装

- MacOS：直接下载最新`v3.5.0`版本安装包 https://github.com/lensapp/lens/releases/download/v3.5.0/Lens-3.5.0.dmg
- Windows：直接下载`v3.5.0`版本安装包 https://github.com/lensapp/lens/releases/download/v3.5.0/Lens-Setup-3.5.0.exe
- Linux：访问安装文档 https://snapcraft.io/docs/installing-snapd，根据不同 Linux 版本安装不同程序

## Lens 体验

### 添加 kubernetes 集群

点击 `+`  ，选择通过 `config` 文件导入。`config` 可以通过 `cat ~/.kube/config` 命令查看到。

![](/img/Lens-1.png)

### 查看集群

![](/img/Lens-2.png)

### 登陆 Pod 或者 查看 Pod 日志

![](/img/Lens-5.png)

### 查看集群事件

![](/img/Lens-6.png)

### 支持查看 helm 部署的 Resources

![](/img/Lens-7.png)

Lens 内置了 helm 模板商店，可直接点击安装

![](/img/Lens-8.png)

### Lens 内置 kubectl 命令，不需要你机器环境中安装 kubectl 命令。

![](/img/Lens-9.png)

## 总结

`Lens` 是一个非常强大的 IDE，可以给大家带来很多便利，值得尝试使用它。

## 参考链接

- https://github.com/lensapp/lens