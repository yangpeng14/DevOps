## 前言

`Kubernetes` 在 `1.24` 版本里弃用并移除 `docker shim`，这导致 `1.24` 版本开始不在支持 `docker` 运行时。大部分用户会选择使用 `Containerd` 做为Kubernetes运行时。

> PS: `docker-ce` 底层就是 `Containerd`

使用 Containerd 时，kubelet 不需要通过 `docker shim` 调用，直接通过 `Container Runtime Interface (CRI)` 与容器运行时交互。减少调用层，并且也减少很多bug产生。

下面来讲讲 docker 与 Containerd 使用有那些方面不同。

## Docker 和 Containerd 常用命令比较

镜像相关操作 | Docker | Containerd
--|--|--
显示本地镜像列表 | docker images | crictl images
下载镜像 | docker pull | crictl pull
上传镜像 | docker push | 无
删除本地镜像 | docker rmi | crictl rmi
查看镜像详情 | docker inspect IMAGE-ID | crictl inspect IMAGE-ID

容器相关操作 | Docker | Containerd
--|--|--
显示容器列表 |	docker ps |	crictl ps
创建容器 | docker create | crictl create
启动容器 | docker start | crictl start
停止容器 | docker stop | crictl stop
删除容器 | docker rm | crictl rm
查看容器详情 | docker inspect | crictl inspect
attach | docker attach | crictl attach
exec | docker exec | crictl exec
logs | docker logs | crictl logs
stats | docker stats | crictl stats

Pods相关操作 | Docker | Containerd
--|--|--
显示POD列表 | 无 | crictl pods
查看POD详情 | 无 | crictl inspectp
运行POD | 无 | crictl runp
停止POD | 无 | crictl stopp

## 容器日志和相关参数配置差异

功能 | Docker | Containerd
--|--|--
存储路径 | 如果 Docker 作为 K8S 容器运行时，容器日志的落盘将由 docker 来完成，保存在类似`/var/lib/docker/containers/$CONTAINERID` 目录下。Kubelet 会在 `/var/log/pods 和 /var/log/containers` 下面建立软链接，指向 `/var/lib/docker/containers/$CONTAINERID` 该目录下的容器日志文件。 | 如果 Containerd 作为 K8S 容器运行时， 容器日志的落盘由 Kubelet 来完成，保存至 `/var/log/pods/$CONTAINER_NAME` 目录下，同时在 `/var/log/containers` 目录下创建软链接，指向日志文件。
配置参数 | 在 docker 配置文件中指定：`"log-driver": "json-file", "log-opts": {"max-size": "100m","max-file": "5"}` | `方法一`：在 kubelet 参数中指定：`--container-log-max-files=5 --container-log-max-size="100Mi"` ；`方法二`：在 KubeletConfiguration 中指定：`"containerLogMaxSize": "100Mi", "containerLogMaxFiles": 5`
容器日志保存到数据盘 | 把数据盘挂载到 "data-root"（缺省是 `/var/lib/docker`）即可。| 创建一个软链接 `/var/log/pods` 指向数据盘挂载点下的某个目录 或者 通过挂载目录，把 `/var/log/pods` 目录挂载到数据盘上。

## CNI 网络

功能 | Docker | Containerd
--|--|--
谁负责调用 CNI | Kubelet 内部的 docker-shim | Containerd 内置的 cri-plugin（containerd 1.1 以后）
如何配置 CNI | Kubelet 参数 `--cni-bin-dir` 和 `--cni-conf-dir` | Containerd 配置文件（toml）： `[plugins.cri.cni]` `bin_dir = "/opt/cni/bin"` `conf_dir = "/etc/cni/net.d"`

## 参考链接

- https://cloud.tencent.com/document/product/457/35747