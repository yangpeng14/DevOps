## Portainer 简介
`Portainer`：是用于Docker的`轻量级`，`跨平台`，`开源管理UI`。Portainer 提供了Docker的详细概述，并允许您通过基于Web 简单仪表板管理容器、镜像、网络和卷。

## Portainer 安装
```bash
# 挂载 docker.sock 到Portainer容器中
$ docker run -d -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock portainer/portainer
```

## 使用方法
- 访问 http://IP_Address:9000/ UI界面，设置管理员账号，如果容器启动后，`5分钟之内`没有设置管理员密码就会自动停止容器

![](https://www.yp14.cn/img/portainer-01.png)


- 选择连接本地容器，容器启动时需要把 `/var/run/docker.sock` 挂载到容器中

![](https://www.yp14.cn/img/portainer-02.png)

- Portainer 概览

![](https://www.yp14.cn/img/portainer-03.png)