## Kui 简介

`Kui` 为构建云原生应用程序提供了新的开发经验。Kui使您能够操作复杂的 `JSON` 和 `YAML` 数据模型，集成不同的工具，并提供对操作数据的聚合视图快速访问。

## 演示

```bash
# 查看 monitoring 命名空间中 pods
$ kubectl kui get pods -n monitoring --ui
```

![](/img/kui-pods.png)

```bash
# 查看 deployment 概要
$ kubectl kui get deployment -n monitoring --ui
```

![](/img/kui-deployment.png)

如果没有该 `--ui` 选项，`Kui` 将直接在您的终端中显示输出；您会发现输出与 `kubectl` 相同，并添加了语法颜色。使用`Kui`，您可以以优美而灵活的方式在这些模式之间导航。

## 支持平台

- Linux
- MacOS
- Windows

## 安装

```bash
# MacOS 安装
$ curl -L https://macos-tarball.kui-shell.org/ | tar jxf -
$ open Kui-darwin-x64/Kui.app
```

其它平台安装方式，参考 `https://github.com/IBM/kui/blob/master/docs/installation.md`


## 项目地址

> https://github.com/IBM/kui

## 参考链接

> https://github.com/IBM/kui