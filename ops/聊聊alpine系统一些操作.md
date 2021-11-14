# 一、简介

`Alpine` 操作系统是一个面向安全的轻型 `Linux` 发行版。它不同于通常 `Linux` 发行版，`Alpine` 采用了 `musl libc` 和 `busybox` 以减小系统的体积和运行时资源消耗，但功能上比 `busybox` 又完善的多，因此得到开源社区越来越多的青睐。在保持瘦身的同时，`Alpine` 还提供了自己的包管理工具 `apk`，可以通过 `https://pkgs.alpinelinux.org/packages` 网站上查询包信息，也可以直接通过 `apk` 命令直接查询和安装各种软件。

`Alpine` 由非商业组织维护的，支持广泛场景的 `Linux`发行版，它特别为资深/重度`Linux`用户而优化，关注安全，性能和资源效能。`Alpine` 镜像可以适用于更多常用场景，并且是一个优秀的可以适用于生产的基础系统/环境。

`Alpine` Docker 镜像也继承了 `Alpine Linux` 发行版的这些优势。相比于其他 `Docker` 镜像，它的容量非常小，仅仅只有 **5 MB** 左右（对比 `Ubuntu` 系列镜像接近 `200 MB`），且拥有非常友好的包管理机制。官方镜像来自 `docker-alpine` 项目。

目前 Docker 官方已开始推荐使用 `Alpine` 替代之前的 `Ubuntu` 做为基础镜像环境。这样会带来多个好处。包括镜像下载速度加快，镜像安全性提高，主机之间的切换更方便，占用更少磁盘空间等。



官方网站：https://alpinelinux.org/

Github：https://github.com/alpinelinux/docker-alpine

Dockerhub：https://hub.docker.com/_/alpine



# 二、APK包管理器

可在包管理中心查看支持的包：https://pkgs.alpinelinux.org/packages

## 1、apk命令详解

### 命令格式

```bash
apk 子命令 参数项
```

### 全局参数项

```bash
-h, --help              Show generic help or applet specific help
-p, --root DIR          Install packages to DIR
-X, --repository REPO   Use packages from REPO
-q, --quiet             Print less information
-v, --verbose           Print more information (can be doubled)
-i, --interactive       Ask confirmation for certain operations
-V, --version           Print program version and exit
-f, --force             Enable selected --force-* (deprecated)
--force-binary-stdout   Continue even if binary data is to be output
--force-broken-world    Continue even if 'world' cannot be satisfied
--force-non-repository  Continue even if packages may be lost on reboot
--force-old-apk         Continue even if packages use unsupported features
--force-overwrite       Overwrite files in other packages
--force-refresh         Do not use cached files (local or from proxy)
-U, --update-cache      Alias for --cache-max-age 1
--progress              Show a progress bar
--progress-fd FD        Write progress to fd
--no-progress           Disable progress bar even for TTYs
--purge                 Delete also modified configuration files (pkg removal) and uninstalled packages from cache (cache clean)
--allow-untrusted       Install packages with untrusted signature or no signature
--wait TIME             Wait for TIME seconds to get an exclusive repository lock before failing
--keys-dir KEYSDIR      Override directory of trusted keys
--repositories-file REPOFILE Override repositories file
--no-network            Do not use network (cache is still used)
--no-cache              Do not use any local cache path
--cache-dir CACHEDIR    Override cache directory
--cache-max-age AGE     Maximum AGE (in minutes) for index in cache before refresh
--arch ARCH             Use architecture with --root
--print-arch            Print default arch and exit
```

commit参数项

```bash
-s, --simulate          Show what would be done without actually doing it
--clean-protected       Do not create .apk-new files in configuration dirs
--overlay-from-stdin    Read list of overlay files from stdin
--no-scripts            Do not execute any scripts
--no-commit-hooks       Skip pre/post hook scripts (but not other scripts)
--initramfs-diskless-boot Enables options for diskless initramfs boot (e.g. skip hooks)
```

### 子命令

#### ①安装与删除

- add：安装包

  ```bash
  --initdb                Initialize database
  -u, --upgrade           Prefer to upgrade package
  -l, --latest            Select latest version of package (if it is not pinned), and print error if it cannot be installed due to other
                          dependencies
  -t, --virtual NAME      Instead of adding all the packages to 'world', create a new virtual package with the listed dependencies and add that to 'world'; the actions of the command are easily reverted by deleting the virtual package
  ```
  
- del：卸载并删除包

  ```bash
  -r, --rdepends          Recursively delete all top-level reverse dependencies too
  ```

#### ②包的元信息管理

- fix：在不改动主要的依赖的情况下进行包的修复或者升级

  ```bash
  -d, --depends           Fix all dependencies too
  -r, --reinstall         Reinstall the package (default)
  -u, --upgrade           Prefer to upgrade package
  -x, --xattr             Fix packages with broken xattrs
  --directory-permissions Reset all directory permissions
  ```

- update：从远程仓库获取信息更新本地仓库索引

- upgrade：令升级系统已安装的所以软件包（一般包括内核），当然也可指定仅升级部分软件包（通过-u或–upgrade选择指定

  ```bash
  -a, --available         Resets versioned world dependencies, and changes to prefer replacing or downgrading packages (instead of holding
                            them) if the currently installed package is no longer available from any repository
  -l, --latest            Select latest version of package (if it is not pinned), and print error if it cannot be installed due to other
                            dependencies
  --no-self-upgrade       Do not do early upgrade of 'apk-tools' package
  --self-upgrade-only     Only do self-upgrade
  ```

- cache：对缓存进行操作，比如对缺失的包进行缓存或者对于不需要的包进行缓存删除

  ```bash
  -u, --upgrade           Prefer to upgrade package
  -l, --latest            Select latest version of package (if it is not pinned), and print error if it cannot be installed due to other
   dependencies
  
  ```

#### ③查询搜索包

- info：列出所有已安装的软件包

  ```bash
  -L, --contents          List contents of the PACKAGE
  -e, --installed         Check if PACKAGE is installed
  -W, --who-owns          Print the package owning the specified file
  -R, --depends           List packages that the PACKAGE depends on
  -P, --provides          List virtual packages provided by PACKAGE
  -r, --rdepends          List all packages depending on PACKAGE
  --replaces              List packages whom files PACKAGE might replace
  -i, --install-if        List the PACKAGE's install_if rule
  -I, --rinstall-if       List all packages having install_if referencing PACKAGE
  -w, --webpage           Show URL for more information about PACKAGE
  -s, --size              Show installed size of PACKAGE
  -d, --description       Print description for PACKAGE
  --license               Print license for PACKAGE
  -t, --triggers          Print active triggers of PACKAGE
  -a, --all               Print all information about PACKAGE
  ```

- list：按照指定条件进行包的列表信息显示

  ```bash
  -I, --installed         List installed packages only
  -O, --orphaned          List orphaned packages only
  -a, --available         List available packages only
  -u, --upgradable        List upgradable packages only
  -o, --origin            List packages by origin
  -d, --depends           List packages by dependency
  -P, --providers         List packages by provider  
  ```

- search：查询相关的包的详细信息，支持正则

  ```bash
  -a, --all               Show all package versions (instead of latest only)
  -d, --description       Search package descriptions (implies -a)
  -x, --exact             Require exact match (instead of substring match)
  -e                      Synonym for -x (deprecated)
  -o, --origin            Print origin package name instead of the subpackage
  -r, --rdepends          Print reverse dependencies of package
  --has-origin            List packages that have the given origin
  ```

  

- dot：生成依赖之间的关联关系图（使用箭头描述）

  ```bash
  --errors                Output only parts of the graph which are considered erroneous: e.g. cycles and missing packages
  --installed             Consider only installed packages
  
  ```

- policy：显示包的仓库策略信息


#### ④源管理

- stats：显示仓库和包的安装相关的统计信息

- index：使用文件生成仓库索引文件

  ```bash
  -o, --output FILE       Write the generated index to FILE
  -x, --index INDEX       Read INDEX to speed up new index creation by reusing the information from an old index
  -d, --description TEXT  Embed TEXT as description and version information of the repository index
  --rewrite-arch ARCH     Use ARCH as architecture for all packages
  ```

- fetch：从全局仓库下载包到本地目录

  ```bash
  -L, --link              Create hard links if possible
  -R, --recursive         Fetch the PACKAGE and all its dependencies
  --simulate              Show what would be done without actually doing it
  -s, --stdout            Dump the .apk to stdout (incompatible with -o, -R, --progress)
  -o, --output DIR        Directory to place the PACKAGEs to
  
  ```

- verify：验证包的完整性和签名信息

- manifest：显示package各组成部分的checksum


## 2、操作

### ①安装软件

```bash
FROM alpine:3.11.5
RUN sed -i "s/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g" /etc/apk/repositories \
    && apk add --no-cache git
```

### ②替换Alpine的软件源

常见国内Alpine软件源：

- 阿里云

  ```bash
  FROM alpilne:3.11.5
  RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
  ```

- 中科大

  ```bash
  FROM alpilne:3.11.5
  RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories
  ```

### ③安装bash

```bash
FROM alpine:3.11.5
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add --no-cache bash bash-doc bash-completion 
```

### ④安装telnet

```bash
FROM alpine:3.11.5
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add --no-cache busybox-extras
```

### ⑤安装Docker Client和Make

```bash
FROM alpine:3.11.5
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add --no-cache docker-cli make
```

### ⑥修改用户的所属用户组

```bash
FROM alpine:3.11.5
RUN sed -i 's/1001/0/g' /etc/passwd
```

### ⑦设置系统语言为“en_US.UTF-8”，以防中文乱码

```bash
FROM alpine:3.11.5
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8
    
RUN apk --no-cache add ca-certificates \ 
    && wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub \ 
    && wget -q https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.29-r0/glibc-2.29-r0.apk \ 
    && wget -q https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.29-r0/glibc-bin-2.29-r0.apk \
    && wget -q https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.29-r0/glibc-i18n-2.29-r0.apk \
    && apk add glibc-2.29-r0.apk glibc-bin-2.29-r0.apk glibc-i18n-2.29-r0.apk \
    && rm -rf /usr/lib/jvm glibc-2.29-r0.apk glibc-bin-2.29-r0.apk  glibc-i18n-2.29-r0.apk \
    && /usr/glibc-compat/bin/localedef --force --inputfile POSIX --charmap UTF-8 "$LANG" || true \
    && echo "export LANG=$LANG" > /etc/profile.d/locale.sh \
    && apk del glibc-i18n
```

**参考**：

1. https://github.com/gliderlabs/docker-alpine/issues/144
2. https://gist.github.com/alextanhongpin/aa55c082a47b9a1b0060a12d85ae7923

### ⑧设置时区

```bash
FROM alpine:3.11.5
ENV TZ=Asia/Shanghai
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add --no-cache tzdata \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone
```

### 参考

1. https://yeasy.gitbooks.io/docker_practice/cases/os/alpine.html
2. https://blog.csdn.net/liumiaocn/article/details/87603628


> 原文出处：https://gitbook.curiouser.top/origin/docker-alpine.html#