## 什么是 ctop

`ctop`：为多个容器提供了一个简洁凝练的实时指标概览。它是一个类 `top` 的针对容器指标的界面。

## ctop 展示如下容器指标
- CPU 利用率

- 内存利用率
- CID 容器ID
- 网络发送（TX - 服务器发送)
- 网络接收（RX - 服务器接收）

## ctop 运行展示
![](https://cdm.yp14.cn/img/ctop.png)

## 安装
- Linux

```bash
$ sudo wget https://github.com/bcicen/ctop/releases/download/v0.7.2/ctop-0.7.2-linux-amd64 -O /usr/local/bin/ctop
$ sudo chmod +x /usr/local/bin/ctop
```

- Mac OS X

```bash
$ brew install ctop
```

or 

```bash
$ sudo curl -Lo /usr/local/bin/ctop https://github.com/bcicen/ctop/releases/download/v0.7.2/ctop-0.7.2-darwin-amd64
$ sudo chmod +x /usr/local/bin/ctop
```

- Docker

```bash
$ docker run --rm -ti \
  --name=ctop \
  --volume /var/run/docker.sock:/var/run/docker.sock:ro \
  quay.io/vektorlab/ctop:latest
```

## 键绑定

键 | 解释
---|---
\<enter\> | 打开容器菜单
a | 切换所有（运行和非运行）容器的显示
f | 过滤显示的容器（esc 清除过滤）
H | 切换ctop标头
h | 帮助
s | 选择容器排序字段
r | 反向容器排序顺序
o | 打开单一视图
l | 查看容器日志（t 打开切换时间戳）
e | 退出 Shell
S | 保存当前配置文件
q | 退出 ctop

## 参考链接
- https://github.com/bcicen/ctop/blob/master/README.md

## 项目地址
- https://github.com/bcicen/ctop