## 前言

在容器化时代，容器应用的日志管理和传统应用存在很大的区别，为了顺应容器化应用，Docker 和 Kubernetes 提供了一套完美的日志解决方案。本文从 Docker 到 Kubernetes 逐步介绍在容器化时代日志的管理机制，以及在 Kubernetes 平台下有哪些最佳的日志收集方案。涉及到的话题有 Docker 日志管理机制、Kubernetes 日志管理机制、Kubernetes 集群日志收集方案。本文结构如下：

- Docker 日志管理机制
    - Docker 的日志种类
    - 基于日志驱动（loging driver）的日志管理机制
    - Docker 日志驱动（loging driver）配置
    - Docker 默认的日志驱动 json-file
- Kubernetes 日志管理机制
    - 应用 Pod 日志
    - Kuberntes 集群组件日志
- Kubernetes 集群日志收集方案
    - 节点级日志代理方案
    - sidecar 容器方案
    - 应用程序直接将日志传输到日志平台

## Docker 日志管理机制

### Docker 的日志种类

在 Docker 中日志分为两大类：

- Docker 引擎日志；
- 容器日志；

#### Docker 引擎日志

Docker 引擎日志就是 docker 服务的日志，即 dockerd 守护进程的日志，在支持 Systemd 的系统中可以通过 `journal -u docker` 查看日志。

![](/img/docker-systemd.png)

#### 容器日志

容器日志指的是每个容器打到 stdout 和 stderr 的日志，而不是容器内部的日志文件。docker 管理所有容器打到 stdout 和 stderr 的日志，其他来源的日志不归 docker 管理。我们通过 `docker logs` 命令查看容器日志都是读取容器打到 stdout 和 stderr 的日志。

## 基于日志驱动（loging driver）的日志管理机制

Docker 提供了一套通用、灵活的日志管理机制，Docker 将所有容器打到 stdout 和 stderr 的日志都统一通过日志驱动重定向到某个地方。

Docker 支持的日志驱动有很多，比如 local、json-file、syslog、journald 等等，类似插件一样，不同的日志驱动可以将日志重定向到不同的地方，这体现了 Docker 日志管理的灵活性，以热插拔的方式实现日志不同目的地的输出。

Dokcer 默认的日志日志驱动是 `json-file`，该驱动将将来自容器的 stdout 和 stderr 日志都统一以 json 的形式存储到本地磁盘。日志存储路径格式为：`/var/lib/docker/containers/<容器 id>/<容器 id>-json.log`。所以可以看出在 `json-file` 日志驱动下，Docker 将所有容器日志都统一重定向到了 `/var/lib/docker/containers/` 目录下，这为日志收集提供了很大的便利。

> 注意：只有日志驱动为：local、json-file 或者 journald 时，docker logs 命令才能查看到容器打到 stdout/stderr 的日志。

![](/img/docker-logging-arch.png)

下面为官方支持的日志驱动列表：

![](/img/docker-log-1.png)

### Docker 日志驱动（loging driver）配置

上面我们已经知道 Docker 支持多种日志驱动类型，我们可以修改默认的日志驱动配置。日志驱动可以全局配置，也可以给特定容器配置。

- 查看 Docker 当前的日志驱动配置

    ```bash
    $ docker  info |grep  "Logging Driver"
    ```

- 查看单个容器的设置的日志驱动

    ```bash
    $ docker inspect  -f '{{.HostConfig.LogConfig.Type}}'   容器id
    ```

- Docker 日志驱动全局配置，全局配置意味所有容器都生效，编辑 /etc/docker/daemon.json 文件（如果文件不存在新建一个），添加日志驱动配置。
示例：配置 Docker 引擎日志驱动为 syslog

    ```json
    {
      "log-driver": "syslog"
    }
    ```

- 给特定容器配置日志驱动，在启动容器时指定日志驱动 `--log-driver` 参数。示例：启动 nginx 容器，日志驱动指定为 journald

    ```bash
    $ docker  run --name nginx -d --log-driver journald nginx
    ```

### Docker 默认的日志驱动 json-file

son-file 日志驱动记录所有容器的 STOUT/STDERR 的输出 ，用 JSON 的格式写到文件中，每一条 json 日志中默认包含 `log`, `stream`, `time` 三个字段，示例日志如下：
文件路径为：
`/var/lib/docker/containers/40f1851f5eb9e684f0b0db216ea19542529e0a2a2e7d4d8e1d69f3591a573c39/40f1851f5eb9e684f0b0db216ea19542529e0a2a2e7d4d8e1d69f3591a573c39-json.log`

```json
{"log":"14:C 25 Jul 2019 12:27:04.072 * DB saved on disk\n","stream":"stdout","time":"2019-07-25T12:27:04.072712524Z"}
```

那么打到磁盘的 json 文件该如何配置轮转，防止撑满磁盘呢？每种 Docker 日志驱动都有相应的配置项日志轮转，比如根据单个文件大小和日志文件数量配置轮转。json-file 日志驱动支持的配置选项如下：

![](/img/docker-log-2.png)

## Kubernetes 日志管理机制

在 Kubernetes 中日志也主要有两大类：

- 应用 Pod 日志；
- Kuberntes 集群组件日志；

### 应用 Pod 日志

Kubernetes Pod 的日志管理是基于 Docker 引擎的，Kubernetes 并不管理日志的轮转策略，日志的存储都是基于 Docker 的日志管理策略。k8s 集群调度的基本单位就是 Pod，而 Pod 是一组容器，所以 k8s 日志管理基于 Docker 引擎这一说法也就不难理解了，最终日志还是要落到一个个容器上面。

![](/img/k8s-logging-arch.png)

假设 Docker 日志驱动为 `json-file`，那么在 k8s 每个节点上，kubelet 会为每个容器的日志创建一个软链接，软连接存储路径为：`/var/log/containers/`，软连接会链接到 `/var/log/pods/` 目录下相应 pod 目录的容器日志，被链接的日志文件也是软链接，最终链接到 Docker 容器引擎的日志存储目录：`/var/lib/docker/container` 下相应容器的日志。另外这些软链接文件名称含有 k8s 相关信息，比如：Pod id，名字空间，容器 ID 等信息，这就为日志收集提供了很大的便利。

举例：我们跟踪一个容器日志文件，证明上述的说明，跟踪一个 kong Pod 日志，Pod 副本数为 1

```
/var/log/containers/kong-kong-d889cf995-2ntwz_kong_kong-432e47df36d0992a3a8d20ef6912112615ffeb30e6a95c484d15614302f8db03.log
------->
/var/log/pods/kong_kong-kong-d889cf995-2ntwz_a6377053-9ca3-48f9-9f73-49856908b94a/kong/0.log
------->
/var/lib/docker/containers/432e47df36d0992a3a8d20ef6912112615ffeb30e6a95c484d15614302f8db03/432e47df36d0992a3a8d20ef6912112615ffeb30e6a95c484d15614302f8db03-json.log
```

![](/img/docker-k8s-logging-arch.png)


### Kuberntes 集群组件日志

Kuberntes 集群组件日志分为两类：

- 运行在容器中的 Kubernetes scheduler 和 kube-proxy。
- 未运行在容器中的 kubelet 和容器 runtime，比如 Docker。

在使用 systemd 机制的服务器上，kubelet 和容器 runtime 写入日志到 journald。如果没有 systemd，他们写入日志到 /var/log 目录的 .log 文件。容器中的系统组件通常将日志写到 /var/log 目录，在 kubeadm 安装的集群中它们以静态 Pod 的形式运行在集群中，因此日志一般在 /var/log/pods 目录下。

## Kubernetes 集群日志收集方案

Kubernetes 本身并未提供集群日志收集方案，k8s 官方文档给了三种日志收集的建议方案：

- 使用运行在每个节点上的节点级的日志代理
- 在应用程序的 pod 中包含专门记录日志 sidecar 容器
- 应用程序直接将日志传输到日志平台

### 节点级日志代理方案

从前面的介绍我们已经了解到，k8s 每个节点都将容器日志统一存储到了 /var/log/containers/ 目录下，因此可以在每个节点安装一个日志代理，将该目录下的日志实时传输到日志存储平台。

由于需要每个节点运行一个日志代理，因此日志代理推荐以 DaemonSet 的方式运行在每个节点。官方推荐的日志代理是 fluentd，当然也可以使用其他日志代理，比如 filebeat，logstash 等。

![](/img/k8s-logging-arch1.png)

### sidecar 容器方案

有两种使用 sidecar 容器的方式：

- sidecar 容器重定向日志流
- sidecar 容器作为日志代理

#### sidecar 容器重定向日志流

这种方式基于节点级日志代理方案，sidecar 容器和应用容器在同一个 Pod 运行，这个容器的作用就是读取应用容器的日志文件，然后将读取的日志内容重定向到 stdout 和 stderr，然后通过节点级日志代理统一收集。这种方式不推荐使用，缺点就是日志重复存储了，导致磁盘使用会成倍增加。比如应用容器的日志本身打到文件存储了一份，sidecar 容器重定向又存储了一份（存储到了 /var/lib/docker/containers/ 目录下）。这种方式的应用场景是应用本身不支持将日志打到 stdout 和 stderr，所以才需要 sidecar 容器重定向下。

![](/img/k8s-logging-arch2.png)

#### sidecar 容器作为日志代理

这种方式不需要节点级日志代理，和应用容器在一起的 sidecar 容器直接作为日志代理方式运行在 Pod 中，sidecar 容器读取应用容器的日志，然后直接实时传输到日志存储平台。很显然这种方式也存在一个缺点，就是每个应用 Pod 都需要有个 sidecar 容器作为日志代理，而日志代理对系统 CPU、和内存都有一定的消耗，在节点 Pod 数很多的时候这个资源消耗其实是不小的。另外还有个问题就是在这种方式下由于应用容器日志不直接打到 stdout 和 stderr，所以是无法使用 kubectl logs 命令查看 Pod 中容器日志。

![](/img/k8s-logging-arch3.png)


### 应用程序直接将日志传输到日志平台

这种方式就是应用程序本身直接将日志打到统一的日志收集平台，比如 Java 应用可以配置日志的 appender，打到不同的地方，很显然这种方式对应用程序有一定的侵入性，而且还要保证日志系统的健壮性，从这个角度看应用和日志系统还有一定的耦合性，所以个人不是很推荐这种方式。

`总结`：综合对比上述三种日志收集方案优缺点，更推荐使用节点级日志代理方案，这种方式对应用没有侵入性，而且对系统资源没有额外的消耗，也不影响 kubelet 工具查看 Pod 容器日志。

## 相关文档

- https://juejin.im/entry/5c03f8bb5188251ba905741d | Docker 日志驱动配置
- https://www.cnblogs.com/operationhome/p/10907591.html | Docker容器日志管理最佳实践
- https://www.cnblogs.com/cocowool/p/Docker_Kubernetes_Log_Location.html | 谈一下Docker与Kubernetes集群的日志和日志管理
- https://kubernetes.io/docs/concepts/cluster-administration/logging/ | Kubernetes 日志架构