## Linux 平台信息

`下面简单列举一些`

- linux/amd64  目前最主流的 X86_64
- linux/arm64
- linux/arm
- linux/arm/v6
- linux/arm/v7

## 问题
Linux 有很多平台，有没有办法只构建一次就能构建出所有的平台镜像？答案是有的，下面介绍的工具刚好能解决这个问题。

## Docker Buildx
`Docker Buildx` 是一个`CLI插件`，扩展了docker命令，并完全支持 `Moby BuildKit` 构建器工具包提供的功能. 它提供了与 `docker build` 相同的用户体验，并具有许多新功能，例如：创建范围内的`构建器实例`和同时针对`多个节点进行构建`。

## 安装
- 直接安装 `Docker v19.03` 版本，该版本已包含 `Docker Buildx` 组件，因为目前还是`实验功能`，默认没有开启。通过设置 `DOCKER_CLI_EXPERIMENTAL` 环境变量来开启。

```bash
$ export DOCKER_CLI_EXPERIMENTAL=enabled
```

## 切换到 docker buildx 构建器
```bash
# 创建 mybuilder 构建器
$ docker buildx create --use --name mybuilder

# 验证构建器是否生效
$ docker buildx ls

NAME/NODE    DRIVER/ENDPOINT             STATUS  PLATFORMS
mybuilder *  docker-container
  mybuilder0 unix:///var/run/docker.sock running linux/amd64, linux/386
default      docker
  default    default                     running linux/amd64, linux/386
```

## 构建多平台镜像

- 创建 `Dockerfile`
```bash
# 使用node镜像，打印一个当前运行平台
$ vim Dockerfile

FROM --platform=$BUILDPLATFORM node:alpine AS build
ARG TARGETPLATFORM
ARG BUILDPLATFORM
RUN echo "I am running on $BUILDPLATFORM, building for $TARGETPLATFORM" > /log

FROM alpine
COPY --from=build /log /log
CMD ["cat", "/log"]
```

- 构成 linux/arm, linux/arm64, linux/amd64 镜像

```bash
# 构建前需要配置好推送的镜像仓库，目前构建的镜像不会保存在本地。这里我使用 dockerhub 镜像仓库 
$ docker buildx build -t yangpeng2468/test --platform=linux/arm,linux/arm64,linux/amd64 . --push

[+] Building 15.8s (17/17) FINISHED
 => [internal] load build definition from Dockerfile                                                                                    0.0s
 => => transferring dockerfile: 32B                                                                                                     0.0s
 => [internal] load .dockerignore                                                                                                       0.0s
 => => transferring context: 2B                                                                                                         0.0s
 => [linux/amd64 internal] load metadata for docker.io/library/alpine:latest                                                            0.9s
 => [linux/arm/v7 internal] load metadata for docker.io/library/alpine:latest                                                           2.1s
 => [linux/arm64 internal] load metadata for docker.io/library/alpine:latest                                                            2.1s
 => [linux/amd64 internal] load metadata for docker.io/library/node:alpine                                                              2.4s
 => [linux/amd64 build 1/2] FROM docker.io/library/node:alpine@sha256:bdf054f006078036f72de45553f3b11176c1c00d5451d8fc2af206636eb54d70  0.0s
 => => resolve docker.io/library/node:alpine@sha256:bdf054f006078036f72de45553f3b11176c1c00d5451d8fc2af206636eb54d70                    0.0s
 => [linux/arm64 stage-1 1/2] FROM docker.io/library/alpine@sha256:c19173c5ada610a5989151111163d28a67368362762534d8a8121ce95cf2bd5a     0.0s
 => CACHED [linux/amd64 build 2/2] RUN echo "I am running on linux/amd64, building for linux/arm64" > /log                              0.0s
 => CACHED [linux/arm64 stage-1 2/2] COPY --from=build /log /log                                                                        0.0s
 => [linux/arm/v7 stage-1 1/2] FROM docker.io/library/alpine@sha256:c19173c5ada610a5989151111163d28a67368362762534d8a8121ce95cf2bd5a    0.0s
 => CACHED [linux/amd64 build 2/2] RUN echo "I am running on linux/amd64, building for linux/arm/v7" > /log                             0.0s
 => CACHED [linux/arm/v7 stage-1 2/2] COPY --from=build /log /log                                                                       0.0s
 => [linux/amd64 stage-1 1/2] FROM docker.io/library/alpine@sha256:c19173c5ada610a5989151111163d28a67368362762534d8a8121ce95cf2bd5a     0.0s
 => => resolve docker.io/library/alpine@sha256:c19173c5ada610a5989151111163d28a67368362762534d8a8121ce95cf2bd5a                         0.0s
 => CACHED [linux/amd64 build 2/2] RUN echo "I am running on linux/amd64, building for linux/amd64" > /log                              0.0s
 => CACHED [linux/amd64 stage-1 2/2] COPY --from=build /log /log                                                                        0.0s
 => exporting to image                                                                                                                 13.4s
 => => exporting layers                                                                                                                 0.0s
 => => exporting manifest sha256:9691c28fd9a98d735f05c913f61165f1367323eca6784a852d457fa1f74dab84                                       0.0s
 => => exporting config sha256:0682fde125dbb5923e494a1dfd6c807bc59d2e9fc7120b57e49074cc7ae7e9f4                                         0.0s
 => => exporting manifest sha256:59c54d4c1b1bee1bd2c23f38f9f2bffc292d0236a4032fba7e9be26fbe0d2802                                       0.0s
 => => exporting config sha256:ac7414caf47ea7db5cc95e5fa9cf65bb98ff8def55f22c08377ad76da4f59260                                         0.0s
 => => exporting manifest sha256:8f73236eead90974fa8ec0b15b5ae1b193786adbfc2d612bb1ab0c272957d3f8                                       0.0s
 => => exporting config sha256:59cb995bf069ab54813fb32e9bd039cafb3830eadf04cc23cb960e134468eb25                                         0.0s
 => => exporting manifest list sha256:72d368f9a6696dc9551ec250d8a2e54bab85b8d0cb784e81cb4a7742090890a3                                  0.0s
 => => pushing layers                                                                                                                  10.7s
 => => pushing manifest for docker.io/yangpeng2468/test:latest
```

- 查看 linux/arm, linux/arm64, linux/amd64 镜像
```bash
$ docker buildx imagetools inspect yangpeng2468/test

Name:      docker.io/yangpeng2468/test:latest
MediaType: application/vnd.docker.distribution.manifest.list.v2+json
Digest:    sha256:72d368f9a6696dc9551ec250d8a2e54bab85b8d0cb784e81cb4a7742090890a3

Manifests:
  Name:      docker.io/yangpeng2468/test:latest@sha256:9691c28fd9a98d735f05c913f61165f1367323eca6784a852d457fa1f74dab84
  MediaType: application/vnd.docker.distribution.manifest.v2+json
  Platform:  linux/arm/v7

  Name:      docker.io/yangpeng2468/test:latest@sha256:59c54d4c1b1bee1bd2c23f38f9f2bffc292d0236a4032fba7e9be26fbe0d2802
  MediaType: application/vnd.docker.distribution.manifest.v2+json
  Platform:  linux/arm64

  Name:      docker.io/yangpeng2468/test:latest@sha256:8f73236eead90974fa8ec0b15b5ae1b193786adbfc2d612bb1ab0c272957d3f8
  MediaType: application/vnd.docker.distribution.manifest.v2+json
  Platform:  linux/amd64
```

## 测试多平台镜像

由于我的环境是 `linux/amd64`，如果测试其它平台镜像，需要开启 `binfmt_misc` 功能

- `binfmt_misc` 开启方法
```bash
$ docker run --rm --privileged docker/binfmt:66f9012c56a8316f9244ffd7622d7c21c1f6f28d
```

- 查看 `binfmt_misc` 设置是否正确
```bash
$ ls -al /proc/sys/fs/binfmt_misc/

drwxr-xr-x 2 root root 0 11月 29 18:29 .
dr-xr-xr-x 1 root root 0 11月 11 19:15 ..
-rw-r--r-- 1 root root 0 11月 29 18:45 qemu-aarch64
-rw-r--r-- 1 root root 0 11月 29 18:45 qemu-arm
-rw-r--r-- 1 root root 0 11月 29 18:45 qemu-ppc64le
-rw-r--r-- 1 root root 0 11月 29 18:45 qemu-s390x
--w------- 1 root root 0 11月 29 18:29 register
-rw-r--r-- 1 root root 0 11月 29 18:29 status
```

- 验证 linux/arm, linux/arm64, linux/amd64 镜像
```bash
$ docker run -it --rm docker.io/yangpeng2468/test:latest@sha256:9691c28fd9a98d735f05c913f61165f1367323eca6784a852d457fa1f74dab84

I am running on linux/amd64, building for linux/arm/v7

$ docker run -it --rm docker.io/yangpeng2468/test:latest@sha256:59c54d4c1b1bee1bd2c23f38f9f2bffc292d0236a4032fba7e9be26fbe0d2802

I am running on linux/amd64, building for linux/arm64

$ docker run -it --rm docker.io/yangpeng2468/test:latest@sha256:8f73236eead90974fa8ec0b15b5ae1b193786adbfc2d612bb1ab0c272957d3f8

I am running on linux/amd64, building for linux/amd64
```

## 总结

未来，`buildx` 很有可能成为 `docker build` 命令一部分，大家一起期待吧！

## 参考链接
- https://docs.docker.com/buildx/working-with-buildx/
- https://www.infoq.cn/article/V9Qj0fJj6HsGYQ0LpHxg