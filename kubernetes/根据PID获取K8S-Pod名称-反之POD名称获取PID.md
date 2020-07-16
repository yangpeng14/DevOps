## 背景

随着 Kubernetes 越来越火爆，运维人员排查问题难度越来越大。比如我们收到监控报警，某台 Kubernetes Node 节点负载高。通过 `top` 或者 `pidstat` 命令获取 `Pid`，问题来了，这个 `Pid` 对应那个 Kubernetes Pod 呢？

下面是作者写的两个小工具，可以帮助运维同胞们快速定位问题。

## 根据 Pid 获取 K8s Pod 名称

### 脚本工具

```bash
$ vim pod_name_info.sh

#!/usr/bin/env bash

Check_jq() {
  which jq &> /dev/null
  if [ $? != 0 ];then
    echo -e "\033[32;32m 系统没有安装 jq 命令，请参考下面命令安装！  \033[0m \n"
    echo -e "\033[32;32m Centos 或者 RedHat 请使用命令 yum install jq -y 安装 \033[0m"
    echo -e "\033[32;32m Ubuntu 或者 Debian 请使用命令 apt-get install jq -y 安装 \033[0m"
    exit 1
  fi
}

Pod_name_info() {
  CID=`cat /proc/${pid}/cgroup | head -1 | awk -F '/' '{print $5}'`
  CID=$(echo ${CID:0:8})
  docker inspect $CID | jq '.[0].Config.Labels."io.kubernetes.pod.name"'
}

pid=$1
Check_jq
Pod_name_info
```

上面 `Shell` 脚本需要服务器上安装 `jq` 命令，因为脚本依赖 `jq` 来处理 `json` 格式。

### 简单介绍下 `jq` 和 `json`

有些小伙伴们可能没有听说过 `jq` 命令，下面简单介绍下 `jq` 和 `json` ：

`JSON` 是一种轻量级的数据交换格式。其采用完全独立于语言的文本格式，具有方便人阅读和编写，同时也易于机器的解析和生成。这些特性决定了 `JSON` 格式越来越广泛的应用于现代的各种系统中。作为系统管理员，在日常的工作中无论是编辑配置文件或者通过 `http` 请求查询信息，我们都不可避免的要处理 `JSON` 格式的数据。

`jq` 是一款命令行下处理 `JSON 数据的工具`。其可以接受`标准输入`，`命令管道`或者`文件中的 JSON 数据`，经过一系列的过滤器(filters)和表达式的转后形成我们需要的数据结构并将结果输出到标准输出中。`jq` 的这种特性使我们可以很容易地在 `Shell` 脚本中调用它。

### 演示

#### 运行方式

```bash
# 通过 Pid 获取 Pod 名称
$ ./pod_name_info.sh Pid
```

#### 下面展示输出结果

![通过 Pid 获取 Pod 名称](/img/pod-name-pid-1.png)

上面脚本是根据 Pid 来获取 Pod 名称，但有时想通过 Pod 名称来获取 Pid，这又怎么获取了，接着看下文。

## 根据 Pod 名称获取 Pid

### 脚本工具

```bash
$ vim pod_pid_info.sh

#!/usr/bin/env bash

Check_jq() {
  which jq &> /dev/null
  if [ $? != 0 ];then
    echo -e "\033[32;32m 系统没有安装 jq 命令，请参考下面命令安装！  \033[0m \n"
    echo -e "\033[32;32m Centos 或者 RedHat 请使用命令 yum install jq -y 安装 \033[0m"
    echo -e "\033[32;32m Ubuntu 或者 Debian 请使用命令 apt-get install jq -y 安装 \033[0m"
    exit 1
  fi
}

Pid_info() {
  docker_storage_location=`docker info  | grep 'Docker Root Dir' | awk '{print $NF}'`

  for docker_short_id in `docker ps | grep ${pod_name} | grep -v pause | awk '{print $1}'`
  do
    docker_long_id=`docker inspect ${docker_short_id} | jq ".[0].Id" | tr -d '"'`
    cat ${docker_storage_location}/containers/${docker_long_id}/config.v2.json | jq ".State.Pid"
  done
}

pod_name=$1
Check_jq
Pid_info
```

### 演示

#### 运行方式

```bash
# 通过 Pod名称 获取 Pid 
$ ./pod_pid_info.sh Pod名称
```

#### 下面展示输出结果

![通过 Pod名称 获取 Pid](/img/pod-name-pid-2.png)