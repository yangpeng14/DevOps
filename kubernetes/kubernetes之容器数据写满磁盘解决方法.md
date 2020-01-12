## 磁盘写满引发的后果

容器数据磁盘写满造成的后果：

- Pod 不能删除 (一直 Terminating)
- Pod 不能被创建 (一直 ContainerCreating)

磁盘写满分两种情况：

- 磁盘空间全部使用完

    ```bash
    # 系统盘被占满
    $ df -Th

    文件系统       类型      容量  已用  可用 已用% 挂载点
    /dev/vda1    ext4      50G  50G   0G   100% /
    /dev/vdb1    ext4    100G  10G  90G   10% /data
    ```

- 磁盘 Inode 全部使用完

    ```bash
    # 数据盘 Inode 被占满
    $ df -i

    文件系统       Inode 已用(I) 可用(I) 已用(I)% 挂载点
    /dev/vda1    3276800  3276800 0      100% /
    ```

## 判断磁盘写满方法

下面命令能快速的排查磁盘占满问题：

- `docker info  | grep 'Docker Root Dir'` # 检查 Docker 存储目录
- `docker system df` # 查看容器磁盘使用情况
- `df -hT` # 检查宿主机 `磁盘空间` 使用情况
- `df -i`  # 检查宿主机 `Inode` 使用情况

## 解决方法

> PS：保证业务能正常使用为第一原则解决问题

- 标记 Node 为不可调度

    ```bash
    $ kubectl drain ${node-name}
    ```

- 查找那个容器输出日志占用最大

    ```bash
    $ for name in $(docker ps -a  | awk '{print $1}' | grep -v CONTAINER); do docker inspect $name | grep LogPath | awk '{print $NF}' | tr -d '",' |xargs du -sh;done

    5G	/var/lib/docker/containers/d0e330944a074268a1f0998fd66ee73f584642352a2fe77304c1fa49b819893a/d0e330944a074268a1f0998fd66ee73f584642352a2fe77304c1fa49b819893a-json.log
    ```

- 清空容器日志文件

    > `注意`：如果需要重启 docker服务，首先腾出一点磁盘空间，不然重启 docker 会失败。不能直接使用 `rm` 删除日志文件，这样磁盘空间是不会释放的。不小心这样操作，那只能通过 `systemctl restart docker` 重启 Docker 服务释放磁盘空间，如果磁盘还是没有释放，可以通过 `lsof | grep -i delete` 查找已删除的文件进程，找到后直接 `kill` 掉。

    ```bash
    # 通过 echo 命令 清空日志文件
    $ echo > /var/lib/docker/containers/d0e330944a074268a1f0998fd66ee73f584642352a2fe77304c1fa49b819893a/d0e330944a074268a1f0998fd66ee73f584642352a2fe77304c1fa49b819893a-json.log
    ```

- 清理节点不用的 `images`，释放磁盘空间

    ```bash
    # 查看 docker 镜像
    $ docker images

    # 删除不用的镜像
    $ docker rmi ${images_id}
    ```


上面步骤操作完后（上面清理日志方法，可能对于收集日志程序会丢失一些日志，但一半情况能接受），可以选择驱赶节点上所有pod（`kubectl drain ${node-name}` ）再优化Docker配置。也可以不驱赶节点上pod，在现基础上优化容器日志方法，优化配置后重启 Docker，这会导致节点上pod中断一会，如果前端反向代理具备重试机制一般不会影响业务正常访问。

优化完 Docker配置后，把节点加入到k8s集群中，正常服务。
```bash
# 取消不可调度的标记
$ kubectl uncordon ${node-name}
```

## 定位问题根本原因及解决思路

- 日志输出量大，导致磁盘写满
    - 减少日志输出，调整应用日志输出级别
    - 增大磁盘空间
    - 日志输出到统一日志收集中心

- 容器镜像占满磁盘
    - 配置k8s垃圾回收策略
    - 节点运行 images 定时清理脚本

- 可写层量大导致磁盘写满: 优化程序逻辑，不写文件到容器内或控制写入文件的大小与数量

## 具体优化方法

- 配置 Docker日志轮转，数据目录不要存放在系统盘
    ```bash
    $ vim /etc/docker/daemon.json

    {"registry-mirrors": ["https://4xr1qpsp.mirror.aliyuncs.com"], "graph": "/data/docker", "log-opts": {"max-size":"500m", "max-file":"3"}}
    ```

    配置解释：
    - registry-mirrors 镜像加速配置
    - graph 定义数据存储目录
    - max-size=500m 意味着一个容器日志大小上限是500M
    - max-file=3，意味着一个容器有三个日志，分别是id+.json、id+1.json、id+2.json

    配置完，重启 docker才能生效，日志轮转只对以后新创建的容器有效。


- 清理 docker images

    `定时清理脚本`
    ```bash
    $ vim docker_delete_image.sh
    #!/usr/bin/env bash

    for images_id in `docker images | grep 'harbor.example.com' | awk '{print $3}'`
    do
        docker rmi $images_id
    done

    # 清理 <none> images
    for images_id_1 in `docker images  | awk '$2 ~ "<none>"{print $3}'`
    do
        docker rmi $images_id_1
    done
    ```

    `kubernetes 垃圾回收配置`，这里不在细讲，具体参考官方配置文档 https://kubernetes.io/docs/concepts/workloads/controllers/garbage-collection/


## 参考链接
- https://kubernetes.io/docs/concepts/workloads/controllers/garbage-collection/