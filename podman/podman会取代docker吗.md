## Linux容器简介

`Linux容器` 是与系统其他部分隔离开的一系列进程。运行这些进程所需的所有文件都由另一个镜像提供，这意味着从开发到测试再到生产的整个过程中，Linux 容器都具有可移植性和一致性。因而，相对于依赖重复传统测试环境的开发渠道，容器的运行速度要快得多。容器比较普遍也易于使用，因此也成了 IT 安全方面的重要组成部分。[1]

## Docker简介

`Docker` 是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个可移植的容器中,然后发布到任何流行的Linux机器或Windows 机器上,也可以实现虚拟化,容器是完全使用沙箱机制,相互之间不会有任何接口。

一个完整的Docker有以下几个部分组成：

- Docker Client客户端
- Docker Daemon守护进程
- Docker Image镜像
- Docker Container容器  [2]

`Docker` 是目前最流行 `Linux容器解决方案`，但有两个不足之处：

- `Docker` 需要在你的系统上运行一个守护进程
- `Docker` 是以 `root` 身份在你的系统上运行该守护程序

这些缺点的存在可能有一定的安全隐患，为了解决这些问题，下一代容器化工具 `Podman` 出现了。 [3]

## Podman 简介

`Podman` 是一个开源的容器运行时项目，可在大多数 `Linux` 平台上使用。`Podman` 提供与 `Docker` 非常相似的功能。正如前面提到的那样，它不需要在你的系统上运行`任何守护进程`，并且它也可以在没有 `root` 权限的情况下运行。

`Podman` 可以管理和运行任何符合 `OCI（Open Container Initiative）`规范的容器和容器镜像。`Podman` 提供了一个与 `Docker` 兼容的命令行前端来管理 `Docker` 镜像。[3]

Podman 不足之处：

- 因为没有类似 `docker daemon` 守护进程，所以不支持 `--restart` 策略，不过使用 `k8s` 编排就不存在这个问题

`Centos8` 去除了 `Docker` 作为默认的容器化管理工具，使用 `Podman、Buildah、Skopeo` 进行了替换。 

## 安装

- CentOS 安装方式

    ```bash
    # 使用 yum 安装
    $ sudo yum install podman -y 
    ```

- MacOS 安装方式

    ```bash
    $ brew cask install podman
    ```

## podman info

```bash
host:
  BuildahVersion: 1.9.0
  Conmon:
    package: podman-1.4.4-4.el7.centos.x86_64
    path: /usr/libexec/podman/conmon
    version: 'conmon version 0.3.0, commit: unknown'
  Distribution:
    distribution: '"centos"'
    version: "7"
  MemFree: 14471168
  MemTotal: 512086016
  OCIRuntime:
    package: containerd.io-1.2.10-3.2.el7.x86_64
    path: /usr/bin/runc
    version: |-
      runc version 1.0.0-rc8+dev
      commit: 3e425f80a8c931f88e6d94a8c831b9d5aa481657
      spec: 1.0.1-dev
  SwapFree: 0
  SwapTotal: 0
  arch: amd64
  cpus: 1
  hostname: vps3
  kernel: 3.10.0-693.2.2.el7.x86_64
  os: linux
  rootless: false
  uptime: 4608h 6m 0.82s (Approximately 192.00 days)
registries:
  blocked: null
  insecure: null
  search:
  - registry.access.redhat.com
  - docker.io
  - registry.fedoraproject.org
  - quay.io
  - registry.centos.org
store:
  ConfigFile: /etc/containers/storage.conf
  ContainerStore:
    number: 0
  GraphDriverName: overlay
  GraphOptions: null
  GraphRoot: /var/lib/containers/storage
  GraphStatus:
    Backing Filesystem: extfs
    Native Overlay Diff: "true"
    Supports d_type: "true"
    Using metacopy: "false"
  ImageStore:
    number: 0
  RunRoot: /var/run/containers/storage
  VolumePath: /var/lib/containers/storage/volumes
```

## Podman 使用 [4]

- 下载镜像
    ```bash
    $ podman pull registry.fedoraproject.org/f27/httpd

    Trying to pull registry.fedoraproject.org/f27/httpd...Getting image source signatures
    Copying blob 2fc5c44251d4 [======>-------------------------------] 8.1MiB / 44.8MiB
    Copying blob ff3dab903f92 [===>----------------------------------] 8.5MiB / 80.7MiB
    Copying blob 9347d6e9d864 done
    ```

- 创建一个 httpd 容器

    ```bash
    $ podman run -dt -p 8080:8080/tcp \
        -e HTTPD_VAR_RUN=/var/run/httpd \
        -e HTTPD_MAIN_CONF_D_PATH=/etc/httpd/conf.d \
        -e HTTPD_MAIN_CONF_PATH=/etc/httpd/conf \
        -e HTTPD_CONTAINER_SCRIPTS_PATH=/usr/share/container-scripts/httpd/ \
        registry.fedoraproject.org/f27/httpd /usr/bin/run-httpd
    ```

- 列出本机所有容器

    ```bash
    $ podman ps -a
    ```

- 查看容器的日志

    ```bash
    $ sudo podman logs --latest

    10.88.0.1 - - [07/Feb/2018:15:22:11 +0000] "GET / HTTP/1.1" 200 612 "-" "curl/7.55.1" "-"
    10.88.0.1 - - [07/Feb/2018:15:22:30 +0000] "GET / HTTP/1.1" 200 612 "-" "curl/7.55.1" "-"
    10.88.0.1 - - [07/Feb/2018:15:22:30 +0000] "GET / HTTP/1.1" 200 612 "-" "curl/7.55.1" "-"
    10.88.0.1 - - [07/Feb/2018:15:22:31 +0000] "GET / HTTP/1.1" 200 612 "-" "curl/7.55.1" "-"
    10.88.0.1 - - [07/Feb/2018:15:22:31 +0000] "GET / HTTP/1.1" 200 612 "-" "curl/7.55.1" "-"
    ```

- 设置容器一个检查点
    ```bash
    $ sudo podman container checkpoint <container_id>
    ```

- 根据检查点位置恢复容器

    ```bash
    $ sudo podman container restore <container_id>
    ```

- 迁移容器

    要将容器从一个主机实时迁移到另一个主机，请在迁移的源系统上检查该容器的位置，然后将该容器转移到目标系统，然后在目标系统上还原该容器。传输检查点时，可以指定输出文件

    在源系统上：

    ```bash
    $ sudo podman container checkpoint <container_id> -e /tmp/checkpoint.tar.gz
    $ scp /tmp/checkpoint.tar.gz <destination_system>:/tmp
    ```

    在目标系统上：

    ```bash
    $ sudo podman container restore -i /tmp/checkpoint.tar.gz
    ```

## 总结

`Podman` 发展前景很好，是否能取代 `Docker`，暂时不知道，大家只能拭目以待！！！

## 参考链接
- [1] https://www.redhat.com/zh/topics/containers/whats-a-linux-container
- [2] https://baike.baidu.com/item/Docker
- [3] https://juejin.im/post/5d8b27f8e51d4577e86d0d4b
- [4] https://podman.io/getting-started/