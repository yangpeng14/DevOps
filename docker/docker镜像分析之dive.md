## dive 简介
diev：用于`探索 docker 镜像层内容`以及`发现减小 docker 镜像大小`的方法工具。

## docker 命令分析镜像

- `docker inspect` 查看镜像的 Metadata 信息，例如：

    ```bash
    $ docker inspect node:alpine
    ```

    ```json
    "RootFS": {
        "Type": "layers",
        "Layers": [
            "sha256:77cae8ab23bf486355d1b3191259705374f4a11d483b24964d2f729dd8c076a0",
            "sha256:4322be3f308a4efbda17d7a42ab6e48f96cfbbf5e5b2d19b4208fc9d2690efa2",
            "sha256:15b7d94033f50c7416a9b85101bc0deced5b55bfa0e34b60a605bf7d5d95d602",
            "sha256:20d6ac69de87335a4bde7e05a80703347b5c902c40a9b92f40cdb37cf048f4d7"
        ]
    },
    "Metadata": {
        "LastTagTime": "0001-01-01T00:00:00Z"
    }
    ```

- `docker history` 查看镜像构建层命令

    ```bash
    # 可以通过添加 --no-trunc 参数显示每层详细构建命令
    $ docker history node:alpine

    IMAGE               CREATED             CREATED BY                                      SIZE                  COMMENT
    fac3d6a8e034        8 days ago          /bin/sh -c #(nop)  CMD ["node"]                 0B
    <missing>           8 days ago          /bin/sh -c #(nop)  ENTRYPOINT ["docker-entry…   0B
    <missing>           8 days ago          /bin/sh -c #(nop) COPY file:238737301d473041…   116B
    <missing>           8 days ago          /bin/sh -c apk add --no-cache --virtual .bui…   5.35MB
    <missing>           8 days ago          /bin/sh -c #(nop)  ENV YARN_VERSION=1.19.1      0B
    <missing>           8 days ago          /bin/sh -c addgroup -g 1000 node     && addu…   95MB
    <missing>           8 days ago          /bin/sh -c #(nop)  ENV NODE_VERSION=13.2.0      0B
    <missing>           6 weeks ago         /bin/sh -c #(nop)  CMD ["/bin/sh"]              0B
    <missing>           6 weeks ago         /bin/sh -c #(nop) ADD file:fe1f09249227e2da2…   5.55MB
    ```

- 虽然docker提供 `docker inspect` 和 `docker history` 两个命令查询镜像构建历史信息，但是这些信息对我们去分析一个镜像的具体每一层的组成来说还是不太够，不够清晰明了。下面通过 `dive` 工具来分析详细的每层信息。

## dive 结果展示

![](https://www.yp14.cn/img/dive-demo1.png)

## dive 基本功能

- `按层显示Docker镜像内容`：在左侧选择一个图层时，将显示该图层的内容以及右侧的所有先前图层。此外，您还可以使用箭头键全面浏览文件树。

- `指出每一层的变化`：文件树中指示已更改，修改，添加或删除的文件。可以对其进行调整以显示特定层的更改，或显示直到该层的汇总更改

- `估计“图像效率”`：左下方的窗格显示基本图层信息和实验指标，该指标将猜测图像所包含的浪费空间。这可能是由于跨层复制文件，跨层移动文件或没有完全删除文件。提供百分比“得分”和总浪费文件空间。

- `快速的构建/分析周期`：您可以构建一个Docker镜像并使用以下命令立即进行分析：`dive build -t some-tag .`。您只需要用`docker build` 相同的 `dive build` 命令替换命令即可。

## 支持多个镜像源和容器引擎

使用该 `--source` 选项，您可以选择从何处获取容器图像：

`dive <your-image> --source <source>`  

or  

`dive <source>://<your-image>`

`source` 选项支持：

- docker：Docker引擎（默认选项）
- docker-archive：来自磁盘的 Docker Tar 存档
- podman：Podman引擎（仅Linux）

## 安装

`Ubuntu/Debian`

```bash
$ wget https://github.com/wagoodman/dive/releases/download/v0.9.1/dive_0.9.1_linux_amd64.deb
$ sudo apt install ./dive_0.9.1_linux_amd64.deb
```

`RHEL/Centos`

```bash
$ curl -OL https://github.com/wagoodman/dive/releases/download/v0.9.1/dive_0.9.1_linux_amd64.rpm
$ sudo rpm -i dive_0.9.1_linux_amd64.rpm
```

`Mac`

```bash
$ brew install dive
```

`Docker 运行`

```bash
# 使用该镜像运行一个临时的容器，加上我们需要分析的镜像
$ docker run --rm -it \
    -v /var/run/docker.sock:/var/run/docker.sock \
    wagoodman/dive:latest <dive arguments...>
```

## 按键绑定

按键绑定 | 描述
---|---
<kbd>Ctrl + C</kbd>      | 退出
<kbd>Tab</kbd>           | 在层和文件树视图之间切换
<kbd>Ctrl + F</kbd>      | 筛选
<kbd>PageUp</kbd>        | 向上滚动页面
<kbd>PageDown</kbd>      | 向下滚动页面
<kbd>Ctrl + A</kbd>      | 镜像视图：查看聚合图像修改
<kbd>Ctrl + L</kbd>      | 镜像视图：查看当前图层修改
<kbd>Space</kbd>         | 文件树视图：折叠/取消折叠目录
<kbd>Ctrl + Space</kbd>  | 文件树视图：折叠/展开所有目录
<kbd>Ctrl + A</kbd>      | 文件树视图：显示/隐藏添加的文件
<kbd>Ctrl + R</kbd>      | 文件树视图：显示/隐藏已删除的文件
<kbd>Ctrl + M</kbd>      | 文件树视图：显示/隐藏修改的文件
<kbd>Ctrl + U</kbd>      | 文件树视图：显示/隐藏未修改的文件
<kbd>Ctrl + B</kbd>      | 文件树视图：显示/隐藏文件属性
<kbd>PageUp</kbd>        | Filetree视图：向上滚动页面
<kbd>PageDown</kbd>      | Filetree视图：向下滚动页面

## 项目地址
- https://github.com/wagoodman/dive

## 参考链接
- https://github.com/wagoodman/dive/blob/master/README.md