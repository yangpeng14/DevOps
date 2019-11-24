## kubeadm 概述
`Kubeadm` 是一个工具，它提供了 `kubeadm init` 以及 `kubeadm join` 这两个命令作为快速创建 `kubernetes 集群`的最佳实践。

## 环境
- 阿里云两台`CentOS 7.7 64位 ECS`
- 安装 `K8S v1.16.3` 版本
- `pod-network-cidr` 地址段划分为 `10.96.0.0/12`
- `service-cluster-ip-range` 地址段划分为 `10.244.0.0/16`

名称 | 内部IP | 系统配制
---|---|---
k8s-master1 | 172.17.94.205 | 2核CPU，4G内存
k8s-node1 | 172.17.94.206 | 2核CPU，4G内存 

## 主机用途划分
名称 | 用途
---|---
k8s-master1 | etcd kubeadm kube-apiserver kube-scheduler kube-controller-manager kubelet flanneld docker
k8s-node1 | kubeadm kubelet flanneld docker

## 初始化基础环境
运行下面 `init.sh` shell 脚本，脚本完成下面`四项任务`
- 设置服务器 `hostname`
- 安装 `k8s依赖环境`
- `升级系统内核`（升级Centos7系统内核，解决Docker-ce版本兼容问题）
- 安装 `docker ce` 最新版本

```bash
# 添加脚本执行权限并初始化 k8s-master1 机器
$ chmod +x init.sh && ./init.sh k8s-master1
````

```bash
#!/usr/bin/env bash

function Check_linux_system(){
    linux_version=`cat /etc/redhat-release`
    if [[ ${linux_version} =~ "CentOS" ]];then
        echo -e "\033[32;32m 系统为 ${linux_version} \033[0m \n"
    else
        echo -e "\033[32;32m 系统不是CentOS,该脚本只支持CentOS环境\033[0m \n"
        exit 1
    fi
}

function Set_hostname(){
    if [ -n "$HostName" ];then
      grep $HostName /etc/hostname && echo -e "\033[32;32m 主机名已设置，退出设置主机名步骤 \033[0m \n" && return
      case $HostName in
      help)
        echo -e "\033[32;32m bash init.sh 主机名 \033[0m \n"
        exit 1
      ;;
      *)
        hostname $HostName
        echo "$HostName" > /etc/hostname
        echo "`ifconfig eth0 | grep inet | awk '{print $2}'` $HostName" >> /etc/hosts
      ;;
      esac
    else
      echo -e "\033[32;32m 输入为空，请参照 bash init.sh 主机名 \033[0m \n"
      exit 1
    fi
}

function Install_depend_environment(){
    rpm -qa | grep nfs-utils &> /dev/null && echo -e "\033[32;32m 已完成依赖环境安装，退出依赖环境安装步骤 \033[0m \n" && return
    yum install -y nfs-utils curl yum-utils device-mapper-persistent-data lvm2 net-tools conntrack-tools wget vim  ntpdate libseccomp libtool-ltdl telnet
    echo -e "\033[32;32m 升级Centos7系统内核到5版本，解决Docker-ce版本兼容问题\033[0m \n"
    rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org && \
    rpm -Uvh http://www.elrepo.org/elrepo-release-7.0-3.el7.elrepo.noarch.rpm && \
    yum --disablerepo=\* --enablerepo=elrepo-kernel repolist && \
    yum --disablerepo=\* --enablerepo=elrepo-kernel install -y kernel-ml.x86_64 && \
    yum remove -y kernel-tools-libs.x86_64 kernel-tools.x86_64 && \
    yum --disablerepo=\* --enablerepo=elrepo-kernel install -y kernel-ml-tools.x86_64 && \
    grub2-set-default 0
    modprobe br_netfilter
    cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
    sysctl -p /etc/sysctl.d/k8s.conf
    ls /proc/sys/net/bridge
}

function Install_docker(){
    rpm -qa | grep docker && echo -e "\033[32;32m 已安装docker，退出安装docker步骤 \033[0m \n" && return
    yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
    yum makecache fast
    yum -y install docker-ce
    systemctl enable docker.service
    systemctl start docker.service
    systemctl stop docker.service
    echo '{"registry-mirrors": ["https://4xr1qpsp.mirror.aliyuncs.com"]}' > /etc/docker/daemon.json
    systemctl daemon-reload
    systemctl start docker
}

# 初始化顺序
HostName=$1
Check_linux_system && \
Set_hostname && \
Install_depend_environment && \
Install_docker
```

`注意：` 脚本只支持 `Centos` 系统，支持`重复运行`，下面是脚本`第二次运行结果`
```bash
$  ./init.sh k8s-master1

 系统为 CentOS Linux release 7.7.1908 (Core)

k8s-master1
 主机名已设置，退出设置主机名步骤

 已完成依赖环境安装，退出依赖环境安装步骤

docker-ce-cli-19.03.5-3.el7.x86_64
docker-ce-19.03.5-3.el7.x86_64
 已安装docker，退出安装docker步骤
```

## k8s 部署
- 配置 `k8s源`
```bash
# k8s-master1 和 k8s-node1 机器都需要操作
# 添加 k8s yum 源
$ cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
EOF

# 重建 yum缓存
$ yum makecache fast
```

- 安装 `kubeadm、kubelet、kubectl`

```bash
# k8s-master1 机器上操作
# 安装 kubeadm、kubelet、kubectl v1.16.3 版本，设置 kubelet 开机启动

$ yum install -y kubeadm-1.16.3 kubectl-1.16.3 kubelet-1.16.3 --disableexcludes=kubernetes && systemctl enable --now kubelet
```

- 换国内镜像源拉取镜像
```bash
# k8s-master1 机器上操作
# 查看镜像版本
$ kubeadm config images list

k8s.gcr.io/kube-apiserver:v1.16.3
k8s.gcr.io/kube-controller-manager:v1.16.3
k8s.gcr.io/kube-scheduler:v1.16.3
k8s.gcr.io/kube-proxy:v1.16.3
k8s.gcr.io/pause:3.1
k8s.gcr.io/etcd:3.3.15-0
k8s.gcr.io/coredns:1.6.2

# 使用如下脚本下载国内镜像，并修改tag为google的tag
$ vim kubeadm.sh

#!/bin/bash

set -e

KUBE_VERSION=v1.16.3
KUBE_PAUSE_VERSION=3.1
ETCD_VERSION=3.3.15-0
CORE_DNS_VERSION=1.6.2

GCR_URL=k8s.gcr.io
ALIYUN_URL=registry.cn-hangzhou.aliyuncs.com/google_containers

images=(kube-proxy:${KUBE_VERSION}
kube-scheduler:${KUBE_VERSION}
kube-controller-manager:${KUBE_VERSION}
kube-apiserver:${KUBE_VERSION}
pause:${KUBE_PAUSE_VERSION}
etcd:${ETCD_VERSION}
coredns:${CORE_DNS_VERSION})

for imageName in ${images[@]} ; do
  docker pull $ALIYUN_URL/$imageName
  docker tag  $ALIYUN_URL/$imageName $GCR_URL/$imageName
  docker rmi $ALIYUN_URL/$imageName
done

# 运行脚本，拉取镜像
$ bash kubeadm.sh
```

- master 节点安装
```bash
# k8s-master1 机器上操作
$ sudo kubeadm init \
 --apiserver-advertise-address 172.17.94.205 \
 --kubernetes-version=v1.16.3 \
 --pod-network-cidr=10.244.0.0/16

# 返回结果
# 下面是添加节点需要执行以下命令

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 172.17.94.205:6443 --token g59i0k.4ccldean82uvhuq2 \
    --discovery-token-ca-cert-hash sha256:2d815a28094ac4c4659407117b5975c6a7dc8aa1cfd003660cb270e4e58ff6fd

# 添加 k8s config 文件到 .kube 目录
$ mkdir -p $HOME/.kube
$ sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
$ sudo chown $(id -u):$(id -g) $HOME/.kube/config

# 需要安装多个master节点，则使用下面初始化命令
$ kubeadm init  --apiserver-advertise-address 172.17.94.205 --control-plane-endpoint 172.17.94.205  --kubernetes-version=v1.16.3  --pod-network-cidr=10.244.0.0/16  --upload-certs

# 添加master节点命令
# 注：这里的token会不同，不要直接复制。kubeadm init成功后会输出添加 master节点的命令
$ kubeadm join 172.17.94.205:6443 --token g34zaa.ur84appk8h9r3yik --discovery-token-ca-cert-hash sha256:abe426020f2c6073763a3697abeb14d8418c9268288e37b8fc25674153702801     --control-plane --certificate-key 9b9b001fdc0959a9decef7d812a2f006faf69ca44ca24d2e557b3ea81f415afe
```

- Node 节点安装
```bash
# k8s-node1 机器上操作
# 安装 kubeadm kubelet
$ yum install -y kubeadm-1.16.3 kubectl-1.16.3 kubelet-1.16.3 --disableexcludes=kubernetes && systemctl enable --now kubelet

# 添加 node 节点，暂时先忽略错误
$ kubeadm join 172.17.94.205:6443 --token g59i0k.4ccldean82uvhuq2 \
    --discovery-token-ca-cert-hash sha256:2d815a28094ac4c4659407117b5975c6a7dc8aa1cfd003660cb270e4e58ff6fd \
    --ignore-preflight-errors=all

# 如果添加节点失败，或是想重新添加，可以使用命令，不要在 master 节点使用
$ kubeadm reset
```

- 安装网络组件 flanneld
```bash
# k8s-master1
# 下载flannel配置文件
$ wget https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

```bash
# k8s-master1 和 k8s-node1 机器都需要操作
# 更换源，使用国内镜像源下载，再修改tag
$ vim flanneld.sh

#!/bin/bash

set -e

FLANNEL_VERSION=v0.11.0

# 在这里修改源
QUAY_URL=quay.io/coreos
QINIU_URL=quay-mirror.qiniu.com/coreos

images=(flannel:${FLANNEL_VERSION}-amd64
flannel:${FLANNEL_VERSION}-arm64
flannel:${FLANNEL_VERSION}-arm
flannel:${FLANNEL_VERSION}-ppc64le
flannel:${FLANNEL_VERSION}-s390x)

for imageName in ${images[@]} ; do
  docker pull $QINIU_URL/$imageName
  docker tag  $QINIU_URL/$imageName $QUAY_URL/$imageName
  docker rmi $QINIU_URL/$imageName
done

# 运行脚本
$ bash flanneld.sh
```

```bash
# k8s-master1 机器上操作
# 拷贝 master 机器 kube-proxy pause coredns 镜像
$ docker save -o pause.tar k8s.gcr.io/pause:3.1
$ docker save -o kube-proxy.tar k8s.gcr.io/kube-proxy:v1.16.3
$ docker save -o coredns.tar k8s.gcr.io/coredns:1.6.2

# 使用 scp 或者 rsync 命令 拷贝 pause.tar kube-proxy.tar coredns.tar
$ scp pause.tar kube-proxy.tar coredns.tar k8s-node1:/root/

# k8s-node1 机器上操作
$ docker load -i pause.tar 
$ docker load -i kube-proxy.tar
$ docker load -i coredns.tar
```

```bash
# k8s-master1
# 安装 flanneld
$ kubectl apply -f kube-flannel.yml

# 查看 node 节点 和 所有pods 是否正常
$ kubectl  get node

NAME          STATUS   ROLES    AGE   VERSION
k8s-master1   Ready    master   38m   v1.16.3
k8s-node1     Ready    <none>   19m   v1.16.3

$ kubectl  get pods -A -o wide

NAMESPACE     NAME                                  READY   STATUS    RESTARTS   AGE     IP              NODE          NOMINATED NODE   READINESS GATES
kube-system   coredns-5644d7b6d9-gfzg7              1/1     Running   0          37m     10.244.1.2      k8s-node1     <none>           <none>
kube-system   coredns-5644d7b6d9-prgkc              1/1     Running   0          37m     10.244.1.3      k8s-node1     <none>           <none>
kube-system   etcd-k8s-master1                      1/1     Running   0          36m     172.17.94.205   k8s-master1   <none>           <none>
kube-system   kube-apiserver-k8s-master1            1/1     Running   0          36m     172.17.94.205   k8s-master1   <none>           <none>
kube-system   kube-controller-manager-k8s-master1   1/1     Running   0          36m     172.17.94.205   k8s-master1   <none>           <none>
kube-system   kube-flannel-ds-amd64-8x9qp           1/1     Running   0          5m32s   172.17.94.205   k8s-master1   <none>           <none>
kube-system   kube-flannel-ds-amd64-ffffg           1/1     Running   0          5m32s   172.17.94.206   k8s-node1     <none>           <none>
kube-system   kube-proxy-dd6l4                      1/1     Running   0          18m     172.17.94.206   k8s-node1     <none>           <none>
kube-system   kube-proxy-pwtkt                      1/1     Running   0          37m     172.17.94.205   k8s-master1   <none>           <none>
kube-system   kube-scheduler-k8s-master1            1/1     Running   0          36m     172.17.94.205   k8s-master1   <none>           <none>
```