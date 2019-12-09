## 什么是 k9s
`K9s`：提供了一个基于`curses`的终端`UI`来与您的 Kubernetes 集群 `进行交互`。该项目的目的是简化`浏览`，`观察`和`管理应用程序`的过程。K9s 持续监视 Kubernetes 的更改，并提供后续命令以与观察到的Kubernetes资源进行交互。


## K9s 输出展示

- 展示 Pods
![](/img/k9s-pod.png)

- 展示 Logs
![](/img/k9s-logs.png)

- 展示 Deployments
![](/img/k9s-dp.png)

- 展示 Deployments yaml 配置
![](/img/k9s-dp-yaml.png)

## 安装前检查

K9s 使用 `256色` 终端模式。在`Nix系统上`，确保已相应设置 `TERM`。

```bash
$ export TERM=xterm-256color
```

## 安装

- Mac OSX
```bash
$ brew install derailed/k9s/k9s
```

- Linux，Windows 和 Mac 都可以通过二进制安装

    访问 `releases` 资源页面下载安装  `https://github.com/derailed/k9s/releases`

## 项目地址
- https://github.com/derailed/k9s

## 参考链接
- https://github.com/derailed/k9s/blob/master/README.md