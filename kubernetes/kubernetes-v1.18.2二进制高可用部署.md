## 一、环境

### 服务器信息

主机名 | IP | 备注
---|---|---
k8s-master1 | 192.168.0.216 | Master1,etcd1,node节点
k8s-master2 | 192.168.0.217 | Master2,etcd2,node节点
k8s-master3 | 192.168.0.218 | Master3,etcd3,node节点
slb | lb.ypvip.com.cn | 外网阿里slb域名

> 本环境使用阿里云，`API Server` 高可用通过`阿里云SLB`实现，如果环境不在云上，可以通过 Nginx + Keepalived，或者 HaProxy + Keepalived等实现。

### 服务版本与K8S集群说明

- `阿里slb`设置`TCP监听`，监听6443端口(通过四层负载到master apiserver)。
- 所有`阿里云ECS主机`使用 `CentOS 7.6.1810` 版本，并且内核都升到`5.x`版本。
- K8S 集群使用 `Iptables 模式`（kube-proxy 注释中预留 `Ipvs` 模式配置）
- Calico 使用 `IPIP` 模式
- 集群使用默认 `svc.cluster.local`
- `10.10.0.1` 为集群 kubernetes svc 解析ip
- Docker CE version 19.03.6
- Kubernetes Version 1.18.2
- Etcd Version v3.4.7
- Calico Version v3.14.0
- Coredns Version 1.6.7
- Metrics-Server Version v0.3.6

```bash
$ kubectl get svc

NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.10.0.1    <none>        443/TCP   6d23h
```

> PS：上面服务版本都是使用`当前最新版本`

### Service 和 Pods Ip 段划分

名称 | IP网段 | 备注
---|---|---
service-cluster-ip | 10.10.0.0/16 | 可用地址 65534
pods-ip | 10.20.0.0/16 | 可用地址 65534
集群dns | 10.10.0.2 | 用于集群service域名解析
k8s svc | 10.10.0.1 | 集群 kubernetes svc 解析ip

## 二、环境初始化

> 所有集群服务器都需要初始化

### 2.1 停止所有机器 firewalld 防火墙

```bash
$ systemctl stop firewalld
$ systemctl disable firewalld
```

### 2.2 关闭 swap

```bash
$ swapoff -a 
$ sed -i 's/.*swap.*/#&/' /etc/fstab
```

### 2.3 关闭 Selinux

```bash
$ setenforce  0 
$ sed -i "s/^SELINUX=enforcing/SELINUX=disabled/g" /etc/sysconfig/selinux 
$ sed -i "s/^SELINUX=enforcing/SELINUX=disabled/g" /etc/selinux/config 
$ sed -i "s/^SELINUX=permissive/SELINUX=disabled/g" /etc/sysconfig/selinux 
$ sed -i "s/^SELINUX=permissive/SELINUX=disabled/g" /etc/selinux/config 
```

### 2.4 设置主机名、升级内核、安装 Docker ce

运行下面 `init.sh` shell 脚本，脚本完成下面四项任务：

- 设置服务器 `hostname`
- 安装 `k8s依赖环境`
- `升级系统内核`（升级Centos7系统内核，解决Docker-ce版本兼容问题）
- 安装 `docker ce` 19.03.6 版本

在每台机器上运行 init.sh 脚本，示例如下：

> Ps：init.sh 脚本只用于 `Centos`，支持 `重复运行`。

```bash
# k8s-master1 机器运行，init.sh 后面接的参数是设置 k8s-master1 服务器主机名
$ chmod +x init.sh && ./init.sh k8s-master1

# 执行完 init.sh 脚本，请重启服务器
$ reboot
```

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
    yum -y install docker-ce-19.03.6 docker-ce-cli-19.03.6
    systemctl enable docker.service
    systemctl start docker.service
    systemctl stop docker.service
    echo '{"registry-mirrors": ["https://4xr1qpsp.mirror.aliyuncs.com"], "log-opts": {"max-size":"500m", "max-file":"3"}}' > /etc/docker/daemon.json
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

## 三、Kubernetes 部署

### 部署顺序

- 1、自签TLS证书
- 2、部署Etcd集群
- 3、创建 metrics-server 证书
- 4、获取K8S二进制包
- 5、创建Node节点kubeconfig文件
- 6、配置Master组件并运行
- 7、配置kubelet证书自动续期
- 8、配置Node组件并运行
- 9、安装calico网络，使用IPIP模式
- 10、集群CoreDNS部署
- 11、部署集群监控服务 Metrics Server
- 12、部署 Kubernetes Dashboard

### 3.1 自签TLS证书

> 在 `k8s-master1` 安装证书生成工具 cfssl，并生成相关证书

```bash
# 创建目录用于存放 SSL 证书
$ mkdir /data/ssl -p

# 下载生成证书命令
$ wget https://pkg.cfssl.org/R1.2/cfssl_linux-amd64
$ wget https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64
$ wget https://pkg.cfssl.org/R1.2/cfssl-certinfo_linux-amd64

# 添加执行权限
$ chmod +x cfssl_linux-amd64 cfssljson_linux-amd64 cfssl-certinfo_linux-amd64

# 移动到 /usr/local/bin 目录下
$ mv cfssl_linux-amd64 /usr/local/bin/cfssl
$ mv cfssljson_linux-amd64 /usr/local/bin/cfssljson
$ mv cfssl-certinfo_linux-amd64 /usr/bin/cfssl-certinfo
```

```bash
# 进入证书目录
$ cd /data/ssl/

# 创建 certificate.sh 脚本
$ vim  certificate.sh
```

> PS：证书有效期为 `10年`

```bash
cat > ca-config.json <<EOF
{
  "signing": {
    "default": {
      "expiry": "87600h"
    },
    "profiles": {
      "kubernetes": {
         "expiry": "87600h",
         "usages": [
            "signing",
            "key encipherment",
            "server auth",
            "client auth"
        ]
      }
    }
  }
}
EOF

cat > ca-csr.json <<EOF
{
    "CN": "kubernetes",
    "key": {
        "algo": "rsa",
        "size": 2048
    },
    "names": [
        {
            "C": "CN",
            "L": "Beijing",
            "ST": "Beijing",
              "O": "k8s",
            "OU": "System"
        }
    ]
}
EOF

cfssl gencert -initca ca-csr.json | cfssljson -bare ca -

#-----------------------

cat > server-csr.json <<EOF
{
    "CN": "kubernetes",
    "hosts": [
      "127.0.0.1",
      "192.168.0.216",
      "192.168.0.217",
      "192.168.0.218",
      "10.10.0.1",
      "lb.ypvip.com.cn",
      "kubernetes",
      "kubernetes.default",
      "kubernetes.default.svc",
      "kubernetes.default.svc.cluster",
      "kubernetes.default.svc.cluster.local"
    ],
    "key": {
        "algo": "rsa",
        "size": 2048
    },
    "names": [
        {
            "C": "CN",
            "L": "BeiJing",
            "ST": "BeiJing",
            "O": "k8s",
            "OU": "System"
        }
    ]
}
EOF

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes server-csr.json | cfssljson -bare server

#-----------------------

cat > admin-csr.json <<EOF
{
  "CN": "admin",
  "hosts": [],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "L": "BeiJing",
      "ST": "BeiJing",
      "O": "system:masters",
      "OU": "System"
    }
  ]
}
EOF

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes admin-csr.json | cfssljson -bare admin

#-----------------------

cat > kube-proxy-csr.json <<EOF
{
  "CN": "system:kube-proxy",
  "hosts": [],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "L": "BeiJing",
      "ST": "BeiJing",
      "O": "k8s",
      "OU": "System"
    }
  ]
}
EOF

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-proxy-csr.json | cfssljson -bare kube-proxy
```

根据自己环境修改 `certificate.sh` 脚本

```bash
      "192.168.0.216",
      "192.168.0.217",
      "192.168.0.218",
      "10.10.0.1",
      "lb.ypvip.com.cn",
```

修改完脚本，然后执行

```bash
$ bash certificate.sh
```

### 3.2 部署Etcd集群

> k8s-master1 机器上操作，把执行文件copy到 k8s-master2 k8s-master3

二进制包下载地址：https://github.com/etcd-io/etcd/releases/download/v3.4.7/etcd-v3.4.7-linux-amd64.tar.gz

```bash
# 创建存储etcd数据目录
$ mkdir /data/etcd/

# 创建 k8s 集群配置目录
$ mkdir /opt/kubernetes/{bin,cfg,ssl}  -p

# 下载二进制etcd包，并把执行文件放到 /opt/kubernetes/bin/ 目录
$ cd /data/etcd/
$ wget https://github.com/etcd-io/etcd/releases/download/v3.4.7/etcd-v3.4.7-linux-amd64.tar.gz
$ tar zxvf etcd-v3.4.7-linux-amd64.tar.gz
$ cd etcd-v3.4.7-linux-amd64
$ cp -a etcd etcdctl /opt/kubernetes/bin/

# 把 /opt/kubernetes/bin 目录加入到 PATH
$ echo 'export PATH=$PATH:/opt/kubernetes/bin' >> /etc/profile
$ source /etc/profile
```

> 登陆到 `k8s-master2` 和 `k8s-master3` 服务器上操作

```bash
# 创建 k8s 集群配置目录
$ mkdir /data/etcd
$ mkdir /opt/kubernetes/{bin,cfg,ssl}  -p

# 把 /opt/kubernetes/bin 目录加入到 PATH
$ echo 'export PATH=$PATH:/opt/kubernetes/bin' >> /etc/profile
$ source /etc/profile
```

> 登陆到 `k8s-master1` 操作

```bash
# 进入 K8S 集群证书目录
$ cd /data/ssl

# 把证书 copy 到 k8s-master1 机器 /opt/kubernetes/ssl/ 目录
$ cp ca*pem  server*pem /opt/kubernetes/ssl/

# 把etcd执行文件与证书 copy 到 k8s-master2  k8s-master3 机器 
scp -r /opt/kubernetes/*  root@k8s-master2:/opt/kubernetes
scp -r /opt/kubernetes/*  root@k8s-master3:/opt/kubernetes
```

```bash
$ cd /data/etcd

# 编写 etcd 配置文件脚本
$ vim etcd.sh
```

```bash
#!/bin/bash

ETCD_NAME=${1:-"etcd01"}
ETCD_IP=${2:-"127.0.0.1"}
ETCD_CLUSTER=${3:-"etcd01=https://127.0.0.1:2379"}

cat <<EOF >/opt/kubernetes/cfg/etcd.yml
name: ${ETCD_NAME}
data-dir: /var/lib/etcd/default.etcd
listen-peer-urls: https://${ETCD_IP}:2380
listen-client-urls: https://${ETCD_IP}:2379,https://127.0.0.1:2379

advertise-client-urls: https://${ETCD_IP}:2379
initial-advertise-peer-urls: https://${ETCD_IP}:2380
initial-cluster: ${ETCD_CLUSTER}
initial-cluster-token: etcd-cluster
initial-cluster-state: new

client-transport-security:
  cert-file: /opt/kubernetes/ssl/server.pem
  key-file: /opt/kubernetes/ssl/server-key.pem
  client-cert-auth: false
  trusted-ca-file: /opt/kubernetes/ssl/ca.pem
  auto-tls: false

peer-transport-security:
  cert-file: /opt/kubernetes/ssl/server.pem
  key-file: /opt/kubernetes/ssl/server-key.pem
  client-cert-auth: false
  trusted-ca-file: /opt/kubernetes/ssl/ca.pem
  auto-tls: false

debug: false
logger: zap
log-outputs: [stderr]
EOF

cat <<EOF >/usr/lib/systemd/system/etcd.service
[Unit]
Description=Etcd Server
Documentation=https://github.com/etcd-io/etcd
Conflicts=etcd.service
After=network.target
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
LimitNOFILE=65536
Restart=on-failure
RestartSec=5s
TimeoutStartSec=0
ExecStart=/opt/kubernetes/bin/etcd --config-file=/opt/kubernetes/cfg/etcd.yml

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable etcd
systemctl restart etcd
```

```bash
# 执行 etcd.sh 生成配置脚本
$ chmod +x etcd.sh
$ ./etcd.sh etcd01 192.168.0.216 etcd01=https://192.168.0.216:2380,etcd02=https://192.168.0.217:2380,etcd03=https://192.168.0.218:2380

# 查看 etcd 是否启动正常
$ ps -ef | grep etcd 
$ netstat -ntplu | grep etcd

tcp        0      0 192.168.0.216:2379      0.0.0.0:*               LISTEN      1558/etcd
tcp        0      0 127.0.0.1:2379          0.0.0.0:*               LISTEN      1558/etcd
tcp        0      0 192.168.0.216:2380      0.0.0.0:*               LISTEN      1558/etcd

# 把 etcd.sh 脚本  copy 到 k8s-master2 k8s-master3 机器上
$ scp /data/etcd/etcd.sh  root@k8s-master2:/data/etcd/
$ scp /data/etcd/etcd.sh  root@k8s-master3:/data/etcd/
```

> 登陆到 `k8s-master2` 操作

```bash
# 执行 etcd.sh 生成配置脚本
$ chmod +x etcd.sh
$ ./etcd.sh etcd02 192.168.0.217 etcd01=https://192.168.0.216:2380,etcd02=https://192.168.0.217:2380,etcd03=https://192.168.0.218:2380

# 查看 etcd 是否启动正常
$ ps -ef | grep etcd 
$ netstat -ntplu | grep etcd
```

> 登陆到 `k8s-master3` 操作

```bash
# 执行 etcd.sh 生成配置脚本
$ chmod +x etcd.sh
$ ./etcd.sh etcd03 192.168.0.218 etcd01=https://192.168.0.216:2380,etcd02=https://192.168.0.217:2380,etcd03=https://192.168.0.218:2380

# 查看 etcd 是否启动正常
$ ps -ef | grep etcd 
$ netstat -ntplu | grep etcd
```

```bash
# 随便登陆一台master机器，查看 etcd 集群是否正常
$ ETCDCTL_API=3 etcdctl --write-out=table \
--cacert=/opt/kubernetes/ssl/ca.pem --cert=/opt/kubernetes/ssl/server.pem --key=/opt/kubernetes/ssl/server-key.pem \
--endpoints=https://192.168.0.216:2379,https://192.168.0.217:2379,https://192.168.0.218:2379 endpoint health

+---------------------------------+--------+-------------+-------+
|            ENDPOINT             | HEALTH |    TOOK     | ERROR |
+---------------------------------+--------+-------------+-------+
| https://192.168.0.216:2379      |   true | 38.721248ms |       |
| https://192.168.0.217:2379      |   true | 38.621248ms |       |
| https://192.168.0.218:2379      |   true | 38.821248ms |       |
+---------------------------------+--------+-------------+-------+
```

### 3.3 创建 metrics-server 证书

创建 metrics-server 使用的证书

> 登陆到 `k8s-master1` 操作

```bash
$ cd /data/ssl/

# 注意: "CN": "system:metrics-server" 一定是这个，因为后面授权时用到这个名称，否则会报禁止匿名访问
$ cat > metrics-server-csr.json <<EOF
{
  "CN": "system:metrics-server",
  "hosts": [],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "BeiJing",
      "L": "BeiJing",
      "O": "k8s",
      "OU": "system"
    }
  ]
}
EOF
```

生成 metrics-server 证书和私钥

```bash
# 生成证书
$ cfssl gencert -ca=/opt/kubernetes/ssl/ca.pem -ca-key=/opt/kubernetes/ssl/ca-key.pem -config=/opt/kubernetes/ssl/ca-config.json -profile=kubernetes metrics-server-csr.json | cfssljson -bare metrics-server

# copy 到 /opt/kubernetes/ssl 目录
$ cp metrics-server-key.pem metrics-server.pem /opt/kubernetes/ssl/

# copy 到 k8s-master2 k8s-master3 机器上
$ scp metrics-server-key.pem metrics-server.pem root@k8s-master2:/opt/kubernetes/ssl/
$ scp metrics-server-key.pem metrics-server.pem root@k8s-master3:/opt/kubernetes/ssl/
```

### 3.4 获取K8S二进制包

> 登陆到 `k8s-master1` 操作

> v1.18 下载页面 https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.18.md

```bash
# 创建存放 k8s 二进制包目录
$ mkdir /data/k8s-package
$ cd /data/k8s-package

# 下载 v1.18.2 二进制包
$ wget https://dl.k8s.io/v1.18.2/kubernetes-server-linux-amd64.tar.gz

$ tar xf kubernetes-server-linux-amd64.tar.gz
```

master 节点需要用到：
- kubectl
- kube-scheduler
- kube-apiserver
- kube-controller-manager

node 节点需要用到：
- kubelet
- kube-proxy

> PS：本文master节点也做为一个node节点，所以需要用到 kubelet kube-proxy 执行文件

```bash
# 进入解压出来二进制包bin目录
$ cd /data/k8s-package/kubernetes/server/bin

# cpoy 执行文件到 /opt/kubernetes/bin 目录
$ cp -a kube-apiserver kube-controller-manager kube-scheduler kubectl kubelet kube-proxy /opt/kubernetes/bin

# copy 执行文件到 k8s-master2 k8s-master3 机器 /opt/kubernetes/bin 目录
$ scp kube-apiserver kube-controller-manager kube-scheduler kubectl kubelet kube-proxy root@k8s-master2:/opt/kubernetes/bin/
$ scp kube-apiserver kube-controller-manager kube-scheduler kubectl kubelet kube-proxy root@k8s-master3:/opt/kubernetes/bin/
```

### 3.5 创建Node节点kubeconfig文件

> 登陆到 `k8s-master1` 操作

- 创建TLS Bootstrapping Token
- 创建kubelet kubeconfig
- 创建kube-proxy kubeconfig

```bash
$ cd /data/ssl/

# 修改第10行 KUBE_APISERVER 地址
$ vim kubeconfig.sh
```

```bash
# 创建 TLS Bootstrapping Token
export BOOTSTRAP_TOKEN=$(head -c 16 /dev/urandom | od -An -t x | tr -d ' ')
cat > token.csv <<EOF
${BOOTSTRAP_TOKEN},kubelet-bootstrap,10001,"system:kubelet-bootstrap"
EOF

#----------------------

# 创建kubelet bootstrapping kubeconfig
export KUBE_APISERVER="https://lb.ypvip.com.cn:6443"

# 设置集群参数
kubectl config set-cluster kubernetes \
  --certificate-authority=./ca.pem \
  --embed-certs=true \
  --server=${KUBE_APISERVER} \
  --kubeconfig=bootstrap.kubeconfig

# 设置客户端认证参数
kubectl config set-credentials kubelet-bootstrap \
  --token=${BOOTSTRAP_TOKEN} \
  --kubeconfig=bootstrap.kubeconfig

# 设置上下文参数
kubectl config set-context default \
  --cluster=kubernetes \
  --user=kubelet-bootstrap \
  --kubeconfig=bootstrap.kubeconfig

# 设置默认上下文
kubectl config use-context default --kubeconfig=bootstrap.kubeconfig

#----------------------

# 创建kube-proxy kubeconfig文件

kubectl config set-cluster kubernetes \
  --certificate-authority=./ca.pem \
  --embed-certs=true \
  --server=${KUBE_APISERVER} \
  --kubeconfig=kube-proxy.kubeconfig

kubectl config set-credentials kube-proxy \
  --client-certificate=./kube-proxy.pem \
  --client-key=./kube-proxy-key.pem \
  --embed-certs=true \
  --kubeconfig=kube-proxy.kubeconfig

kubectl config set-context default \
  --cluster=kubernetes \
  --user=kube-proxy \
  --kubeconfig=kube-proxy.kubeconfig

kubectl config use-context default --kubeconfig=kube-proxy.kubeconfig
```

```bash
# 生成证书
$ sh kubeconfig.sh

# 输出下面结果
kubeconfig.sh   kube-proxy-csr.json  kube-proxy.kubeconfig
kube-proxy.csr  kube-proxy-key.pem   kube-proxy.pem bootstrap.kubeconfig
```

```bash
# copy *kubeconfig 文件到 /opt/kubernetes/cfg 目录
$ cp *kubeconfig /opt/kubernetes/cfg

# copy 到 k8s-master2 k8s-master3 机器上
$ scp *kubeconfig root@k8s-master2:/opt/kubernetes/cfg
$ scp *kubeconfig root@k8s-master3:/opt/kubernetes/cfg
```

### 3.6 配置Master组件并运行

> 登陆到 `k8s-master1` `k8s-master2` `k8s-master3` 操作

```bash
# 创建 /data/k8s-master 目录，用于存放 master 配置执行脚本
$ mkdir /data/k8s-master
```

> 登陆到 `k8s-master1`

```bash
$ cd /data/k8s-master

# 创建生成 kube-apiserver 配置文件脚本
$ vim apiserver.sh
```

```bash
#!/bin/bash

MASTER_ADDRESS=${1:-"192.168.0.216"}
ETCD_SERVERS=${2:-"http://127.0.0.1:2379"}

cat <<EOF >/opt/kubernetes/cfg/kube-apiserver
KUBE_APISERVER_OPTS="--logtostderr=false \\
--v=2 \\
--log-dir=/var/log/kubernetes \\
--etcd-servers=${ETCD_SERVERS} \\
--bind-address=0.0.0.0 \\
--secure-port=6443 \\
--advertise-address=${MASTER_ADDRESS} \\
--allow-privileged=true \\
--service-cluster-ip-range=10.10.0.0/16 \\
--enable-admission-plugins=NamespaceLifecycle,LimitRanger,ServiceAccount,DefaultStorageClass,DefaultTolerationSeconds,MutatingAdmissionWebhook,ValidatingAdmissionWebhook,ResourceQuota,NodeRestriction \\
--authorization-mode=RBAC,Node \\
--kubelet-https=true \\
--enable-bootstrap-token-auth=true \\
--token-auth-file=/opt/kubernetes/cfg/token.csv \\
--service-node-port-range=30000-50000 \\
--kubelet-client-certificate=/opt/kubernetes/ssl/server.pem \\
--kubelet-client-key=/opt/kubernetes/ssl/server-key.pem \\
--tls-cert-file=/opt/kubernetes/ssl/server.pem  \\
--tls-private-key-file=/opt/kubernetes/ssl/server-key.pem \\
--client-ca-file=/opt/kubernetes/ssl/ca.pem \\
--service-account-key-file=/opt/kubernetes/ssl/ca-key.pem \\
--etcd-cafile=/opt/kubernetes/ssl/ca.pem \\
--etcd-certfile=/opt/kubernetes/ssl/server.pem \\
--etcd-keyfile=/opt/kubernetes/ssl/server-key.pem \\
--requestheader-client-ca-file=/opt/kubernetes/ssl/ca.pem \\
--requestheader-extra-headers-prefix=X-Remote-Extra- \\
--requestheader-group-headers=X-Remote-Group \\
--requestheader-username-headers=X-Remote-User \\
--proxy-client-cert-file=/opt/kubernetes/ssl/metrics-server.pem \\
--proxy-client-key-file=/opt/kubernetes/ssl/metrics-server-key.pem \\
--runtime-config=api/all=true \\
--audit-log-maxage=30 \\
--audit-log-maxbackup=3 \\
--audit-log-maxsize=100 \\
--audit-log-truncate-enabled=true \\
--audit-log-path=/var/log/kubernetes/k8s-audit.log"
EOF

cat <<EOF >/usr/lib/systemd/system/kube-apiserver.service
[Unit]
Description=Kubernetes API Server
Documentation=https://github.com/kubernetes/kubernetes

[Service]
EnvironmentFile=-/opt/kubernetes/cfg/kube-apiserver
ExecStart=/opt/kubernetes/bin/kube-apiserver \$KUBE_APISERVER_OPTS
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable kube-apiserver
systemctl restart kube-apiserver
```

```bash
# 创建生成 kube-controller-manager 配置文件脚本
$ vim controller-manager.sh
```

```bash
#!/bin/bash

MASTER_ADDRESS=${1:-"127.0.0.1"}

cat <<EOF >/opt/kubernetes/cfg/kube-controller-manager
KUBE_CONTROLLER_MANAGER_OPTS="--logtostderr=true \\
--v=2 \\
--master=${MASTER_ADDRESS}:8080 \\
--leader-elect=true \\
--bind-address=0.0.0.0 \\
--service-cluster-ip-range=10.10.0.0/16 \\
--cluster-name=kubernetes \\
--cluster-signing-cert-file=/opt/kubernetes/ssl/ca.pem \\
--cluster-signing-key-file=/opt/kubernetes/ssl/ca-key.pem  \\
--service-account-private-key-file=/opt/kubernetes/ssl/ca-key.pem \\
--experimental-cluster-signing-duration=87600h0m0s \\
--feature-gates=RotateKubeletServerCertificate=true \\
--feature-gates=RotateKubeletClientCertificate=true \\
--allocate-node-cidrs=true \\
--cluster-cidr=10.20.0.0/16 \\
--root-ca-file=/opt/kubernetes/ssl/ca.pem"
EOF

cat <<EOF >/usr/lib/systemd/system/kube-controller-manager.service
[Unit]
Description=Kubernetes Controller Manager
Documentation=https://github.com/kubernetes/kubernetes

[Service]
EnvironmentFile=-/opt/kubernetes/cfg/kube-controller-manager
ExecStart=/opt/kubernetes/bin/kube-controller-manager \$KUBE_CONTROLLER_MANAGER_OPTS
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable kube-controller-manager
systemctl restart kube-controller-manager
```

```bash
# 创建生成 kube-scheduler 配置文件脚本
$ vim scheduler.sh
```

```bash
#!/bin/bash

MASTER_ADDRESS=${1:-"127.0.0.1"}

cat <<EOF >/opt/kubernetes/cfg/kube-scheduler
KUBE_SCHEDULER_OPTS="--logtostderr=true \\
--v=2 \\
--master=${MASTER_ADDRESS}:8080 \\
--address=0.0.0.0 \\
--leader-elect"
EOF

cat <<EOF >/usr/lib/systemd/system/kube-scheduler.service
[Unit]
Description=Kubernetes Scheduler
Documentation=https://github.com/kubernetes/kubernetes

[Service]
EnvironmentFile=-/opt/kubernetes/cfg/kube-scheduler
ExecStart=/opt/kubernetes/bin/kube-scheduler \$KUBE_SCHEDULER_OPTS
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable kube-scheduler
systemctl restart kube-scheduler
```

```bash
# 添加执行权限
$ chmod +x *.sh

$ cp /data/ssl/token.csv /opt/kubernetes/cfg/

# copy token.csv 和 master 配置到 k8s-master2 k8s-master3 机器上
$ scp /data/ssl/token.csv root@k8s-master2:/opt/kubernetes/cfg
$ scp /data/ssl/token.csv root@k8s-master3:/opt/kubernetes/cfg
$ scp apiserver.sh controller-manager.sh scheduler.sh root@k8s-master2:/data/k8s-master
$ scp apiserver.sh controller-manager.sh scheduler.sh root@k8s-master3:/data/k8s-master

# 生成 master配置文件并运行
$ ./apiserver.sh 192.168.0.216 https://192.168.0.216:2379,https://192.168.0.217:2379,https://192.168.0.218:2379 
$ ./controller-manager.sh 127.0.0.1
$ ./scheduler.sh 127.0.0.1

# 查看master三个服务是否正常运行
$ ps -ef | grep kube
$ netstat -ntpl | grep kube-
```

> 登陆到 `k8s-master2` 操作

```bash
$ cd /data/k8s-master

# 生成 master配置文件并运行
$ ./apiserver.sh 192.168.0.217 https://192.168.0.216:2379,https://192.168.0.217:2379,https://192.168.0.218:2379 
$ ./controller-manager.sh 127.0.0.1
$ ./scheduler.sh 127.0.0.1

# 查看master三个服务是否正常运行
$ ps -ef | grep kube
$ netstat -ntpl | grep kube-
```

> 登陆到 `k8s-master3` 操作

```bash
$ cd /data/k8s-master

# 生成 master配置文件并运行
$ ./apiserver.sh 192.168.0.218 https://192.168.0.216:2379,https://192.168.0.217:2379,https://192.168.0.218:2379 
$ ./controller-manager.sh 127.0.0.1
$ ./scheduler.sh 127.0.0.1

# 查看master三个服务是否正常运行
$ ps -ef | grep kube
$ netstat -ntpl | grep kube-
```

```bash
# 随便登陆一台master查看集群健康状态
$ kubectl  get cs

NAME                 STATUS    MESSAGE             ERROR
scheduler            Healthy   ok
controller-manager   Healthy   ok
etcd-2               Healthy   {"health":"true"}
etcd-1               Healthy   {"health":"true"}
etcd-0               Healthy   {"health":"true"}
```

### 3.7 配置kubelet证书自动续期

创建自动批准相关 CSR 请求的 ClusterRole

```bash
$ vim tls-instructs-csr.yaml 
```

```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: system:certificates.k8s.io:certificatesigningrequests:selfnodeserver
rules:
- apiGroups: ["certificates.k8s.io"]
  resources: ["certificatesigningrequests/selfnodeserver"]
  verbs: ["create"]
```

```bash
# 部署
$ kubectl apply -f tls-instructs-csr.yaml
```

自动批准 kubelet-bootstrap 用户 TLS bootstrapping 首次申请证书的 CSR 请求

```bash
$ kubectl create clusterrolebinding node-client-auto-approve-csr --clusterrole=system:certificates.k8s.io:certificatesigningrequests:nodeclient --user=kubelet-bootstrap
```

自动批准 system:nodes 组用户更新 kubelet 自身与 apiserver 通讯证书的 CSR 请求

```bash
$ kubectl create clusterrolebinding node-client-auto-renew-crt --clusterrole=system:certificates.k8s.io:certificatesigningrequests:selfnodeclient --group=system:nodes
```

自动批准 system:nodes 组用户更新 kubelet 10250 api 端口证书的 CSR 请求

```bash
$ kubectl create clusterrolebinding node-server-auto-renew-crt --clusterrole=system:certificates.k8s.io:certificatesigningrequests:selfnodeserver --group=system:nodes
```

### 3.8 配置Node组件并运行

首先我们先了解下 `kubelet` 中 `kubelet.kubeconfig` 配置是如何生成？

`kubelet.kubeconfig` 配置是通过 `TLS Bootstrapping` 机制生成，下面是生成的流程图。

![](/img/bootstrap-1.png)

> 登陆到 `k8s-master1` `k8s-master2` `k8s-master3` 操作

```bash
# 创建 node 节点生成配置脚本目录
$ mkdir /data/k8s-node
```

> 登陆到 `k8s-master1` 操作

```bash
# 创建生成 kubelet 配置脚本
$ vim kubelet.sh
```

```bash
#!/bin/bash

DNS_SERVER_IP=${1:-"10.10.0.2"}
HOSTNAME=${2:-"`hostname`"}
CLUETERDOMAIN=${3:-"cluster.local"}

cat <<EOF >/opt/kubernetes/cfg/kubelet.conf
KUBELET_OPTS="--logtostderr=true \\
--v=2 \\
--hostname-override=${HOSTNAME} \\
--kubeconfig=/opt/kubernetes/cfg/kubelet.kubeconfig \\
--bootstrap-kubeconfig=/opt/kubernetes/cfg/bootstrap.kubeconfig \\
--config=/opt/kubernetes/cfg/kubelet-config.yml \\
--cert-dir=/opt/kubernetes/ssl \\
--network-plugin=cni \\
--cni-conf-dir=/etc/cni/net.d \\
--cni-bin-dir=/opt/cni/bin \\
--pod-infra-container-image=yangpeng2468/google_containers-pause-amd64:3.2"
EOF

cat <<EOF >/opt/kubernetes/cfg/kubelet-config.yml
kind: KubeletConfiguration # 使用对象
apiVersion: kubelet.config.k8s.io/v1beta1 # api版本
address: 0.0.0.0 # 监听地址
port: 10250 # 当前kubelet的端口
readOnlyPort: 10255 # kubelet暴露的端口
cgroupDriver: cgroupfs # 驱动，要于docker info显示的驱动一致
clusterDNS:
  - ${DNS_SERVER_IP}
clusterDomain: ${CLUETERDOMAIN}  # 集群域
failSwapOn: false # 关闭swap

# 身份验证
authentication:
  anonymous:
    enabled: false
  webhook:
    cacheTTL: 2m0s
    enabled: true
  x509:
    clientCAFile: /opt/kubernetes/ssl/ca.pem

# 授权
authorization:
  mode: Webhook
  webhook:
    cacheAuthorizedTTL: 5m0s
    cacheUnauthorizedTTL: 30s

# Node 资源保留
evictionHard:
  imagefs.available: 15%
  memory.available: 1G
  nodefs.available: 10%
  nodefs.inodesFree: 5%
evictionPressureTransitionPeriod: 5m0s

# 镜像删除策略
imageGCHighThresholdPercent: 85
imageGCLowThresholdPercent: 80
imageMinimumGCAge: 2m0s

# 旋转证书
rotateCertificates: true # 旋转kubelet client 证书
featureGates:
  RotateKubeletServerCertificate: true
  RotateKubeletClientCertificate: true

maxOpenFiles: 1000000
maxPods: 110
EOF

cat <<EOF >/usr/lib/systemd/system/kubelet.service
[Unit]
Description=Kubernetes Kubelet
After=docker.service
Requires=docker.service

[Service]
EnvironmentFile=-/opt/kubernetes/cfg/kubelet.conf
ExecStart=/opt/kubernetes/bin/kubelet \$KUBELET_OPTS
Restart=on-failure
KillMode=process

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable kubelet
systemctl restart kubelet
```

```bash
# 创建生成 kube-proxy 配置脚本
$ vim proxy.sh
```

```bash
#!/bin/bash

HOSTNAME=${1:-"`hostname`"}

cat <<EOF >/opt/kubernetes/cfg/kube-proxy.conf
KUBE_PROXY_OPTS="--logtostderr=true \\
--v=2 \\
--config=/opt/kubernetes/cfg/kube-proxy-config.yml"
EOF

cat <<EOF >/opt/kubernetes/cfg/kube-proxy-config.yml
kind: KubeProxyConfiguration
apiVersion: kubeproxy.config.k8s.io/v1alpha1
address: 0.0.0.0 # 监听地址
metricsBindAddress: 0.0.0.0:10249 # 监控指标地址,监控获取相关信息 就从这里获取
clientConnection:
  kubeconfig: /opt/kubernetes/cfg/kube-proxy.kubeconfig # 读取配置文件
hostnameOverride: ${HOSTNAME} # 注册到k8s的节点名称唯一
clusterCIDR: 10.10.0.0/16 # service IP范围
mode: iptables # 使用iptables模式

# 使用 ipvs 模式
#mode: ipvs # ipvs 模式
#ipvs:
#  scheduler: "rr"
#iptables:
#  masqueradeAll: true
EOF

cat <<EOF >/usr/lib/systemd/system/kube-proxy.service
[Unit]
Description=Kubernetes Proxy
After=network.target

[Service]
EnvironmentFile=-/opt/kubernetes/cfg/kube-proxy.conf
ExecStart=/opt/kubernetes/bin/kube-proxy \$KUBE_PROXY_OPTS
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable kube-proxy
systemctl restart kube-proxy
```

```bash
# 生成 node 配置文件
$ ./kubelet.sh 10.10.0.2 k8s-master1 cluster.local
$ ./proxy.sh k8s-master1

# 查看服务是否启动
$ netstat -ntpl | egrep "kubelet|kube-proxy"

# copy kubelet.sh proxy.sh 脚本到 k8s-master2 k8s-master3 机器上
$ scp kubelet.sh  proxy.sh  root@k8s-master2:/data/k8s-node
$ scp kubelet.sh  proxy.sh  root@k8s-master3:/data/k8s-node
```

> 登陆到 `k8s-master2` 操作

```bash
$ cd /data/k8s-node

# 生成 node 配置文件
$ ./kubelet.sh 10.10.0.2 k8s-master2 cluster.local
$ ./proxy.sh k8s-master2

# 查看服务是否启动
$ netstat -ntpl | egrep "kubelet|kube-proxy"
```

> 登陆到 `k8s-master3` 操作

```bash
$ cd /data/k8s-node

# 生成 node 配置文件
$ ./kubelet.sh 10.10.0.2 k8s-master3 cluster.local
$ ./proxy.sh k8s-master3

# 查看服务是否启动
$ netstat -ntpl | egrep "kubelet|kube-proxy"
```

```bash
# 随便登陆一台master机器查看node节点是否添加成功
$ kubectl get node

NAME       STATUS   ROLES    AGE    VERSION
k8s-master1   NoReady    <none>   4d4h   v1.18.2
k8s-master2   NoReady    <none>   4d4h   v1.18.2
k8s-master3   NoReady    <none>   4d4h   v1.18.2
```
> 上面 Node 节点处理 `NoReady` 状态，是因为目前还没有安装网络组件，下文安装网络组件。

### 3.9 安装calico网络，使用IPIP模式

> 登陆到 `k8s-master1` 操作

下载 `Calico Version v3.14.0` Yaml 文件

```bash
# 存放etcd yaml文件
$ mkdir -p ~/yaml/calico

$ cd ~/yaml/calico

# 注意：下面是基于自建etcd做为存储的配置文件
$ curl https://docs.projectcalico.org/manifests/calico-etcd.yaml -O
```

#### `calico-etcd.yaml` 需要修改如下配置：

##### Secret 配置修改

```yaml
apiVersion: v1
kind: Secret
type: Opaque
metadata:
  name: calico-etcd-secrets
  namespace: kube-system
data:
  etcd-key: (cat /opt/kubernetes/ssl/server-key.pem | base64 -w 0) # 将输出结果填写在这里
  etcd-cert: (cat /opt/kubernetes/ssl/server.pem | base64 -w 0) # 将输出结果填写在这里
  etcd-ca: (cat /opt/kubernetes/ssl/ca.pem | base64 -w 0) # 将输出结果填写在这里
```

##### `ConfigMap` 配置修改

```yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: calico-config
  namespace: kube-system
data:
  etcd_endpoints: "https://192.168.0.216:2379,https://192.168.0.217:2379,https://192.168.0.218:2379"
  etcd_ca: "/calico-secrets/etcd-ca"
  etcd_cert: "/calico-secrets/etcd-cert"
  etcd_key: "/calico-secrets/etcd-key"
```

关于ConfigMap部分主要参数如下：
- `etcd_endpoints`：Calico使用etcd来保存网络拓扑和状态，该参数指定etcd的地址，可以使用K8S Master所用的etcd，也可以另外搭建。
- `calico_backend`：Calico的后端，默认为bird。
- `cni_network_config`：符合CNI规范的网络配置，其中type=calico表示，Kubelet从 CNI_PATH(默认为/opt/cni/bin)找名为calico的可执行文件，用于容器IP地址的分配。
- etcd 如果配置`TLS安全认证`，则还需要指定相应的`ca`、`cert`、`key`等文件

##### 修改 Pods 使用的 `IP 网段`，默认使用 `192.168.0.0/16` 网段

```yaml
            - name: CALICO_IPV4POOL_CIDR
              value: "10.20.0.0/16"
```

##### 配置网卡自动发现规则

在 DaemonSet calico-node `env` 中添加网卡发现规则

```yaml
            # 定义ipv4自动发现网卡规则
            - name: IP_AUTODETECTION_METHOD
              value: "interface=eth.*"
            # 定义ipv6自动发现网卡规则
            - name: IP6_AUTODETECTION_METHOD
              value: "interface=eth.*"
```

##### Calico 模式设置

```yaml
            # Enable IPIP
            - name: CALICO_IPV4POOL_IPIP
              value: "Always"
```

Calico 有两种网络模式：`BGP` 和 `IPIP`
- 使用 `IPIP` 模式时，设置 `CALICO_IPV4POOL_IPIP="always"`，IPIP 是一种将各Node的路由之间做一个`tunnel`，再把两个网络连接起来的模式，启用IPIP模式时，Calico将在各Node上创建一个名为 `tunl0` 的虚拟网络接口。
- 使用 `BGP` 模式时，设置 `CALICO_IPV4POOL_IPIP="off"`

##### 错误解决方法

`错误`： [ERROR][8] startup/startup.go 146: failed to query kubeadm's config map error=Get https://10.10.0.1:443/api/v1/namespaces/kube-system/configmaps/kubeadm-config?timeout=2s: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)

`原因`：Node工作节点连接不到 `apiserver` 地址，检查一下calico配置文件，要把apiserver的IP和端口配置上，如果不配置的话，calico默认将设置默认的calico网段和443端口。字段名：`KUBERNETES_SERVICE_HOST`、`KUBERNETES_SERVICE_PORT`、`KUBERNETES_SERVICE_PORT_HTTPS`。

`解决方法`：

在 DaemonSet calico-node `env` 中添加环境变量

```yaml
            - name: KUBERNETES_SERVICE_HOST
              value: "lb.ypvip.com.cn"
            - name: KUBERNETES_SERVICE_PORT
              value: "6443"
            - name: KUBERNETES_SERVICE_PORT_HTTPS
              value: "6443"
```

修改完 `calico-etcd.yaml` 后，执行部署

```bash
# 部署
$ kubectl apply -f calico-etcd.yaml

# 查看 calico pods
$ kubectl  get pods -n kube-system  | grep calico

# 查看 node 是否正常，现在 node 服务正常了
$ kubectl get node

NAME       STATUS   ROLES    AGE    VERSION
k8s-master1   Ready    <none>   4d4h   v1.18.2
k8s-master2   Ready    <none>   4d4h   v1.18.2
k8s-master3   Ready    <none>   4d4h   v1.18.2
```

### 3.10 集群CoreDNS部署

> 登陆到 `k8s-master1` 操作

`deploy.sh` 是一个便捷的脚本，用于生成coredns yaml 配置。

```bash
# 安装依赖 jq 命令
$ yum install jq -y

$ cd ~/yaml

# 下载 CoreDNS 项目
$ git clone https://github.com/coredns/deployment.git
$ cd coredns/deployment/kubernetes
```

默认情况下 `CLUSTER_DNS_IP` 是自动获取kube-dns的集群ip的，但是由于没有部署kube-dns所以只能手动指定一个集群ip。

```yaml
111 if [[ -z $CLUSTER_DNS_IP ]]; then
112   # Default IP to kube-dns IP
113   # CLUSTER_DNS_IP=$(kubectl get service --namespace kube-system kube-dns -o jsonpath="{.spec.clusterIP}")
114   CLUSTER_DNS_IP=10.10.0.2
```

```bash
# 查看执行效果，并未开始部署
$ ./deploy.sh

# 执行部署
$ ./deploy.sh | kubectl apply -f -

# 查看 Coredns
$ kubectl get svc,pods -n kube-system| grep coredns
```

测试 Coredns 解析

```bash
# 创建一个 busybox Pod
$ vim busybox.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: busybox
  namespace: default
spec:
  containers:
  - name: busybox
    image: busybox:1.28.4
    command:
      - sleep
      - "3600"
    imagePullPolicy: IfNotPresent
  restartPolicy: Always
```

```bash
# 部署
$ kubectl apply -f busybox.yaml

# 测试解析，下面是解析正常
$ kubectl exec -i busybox -n default nslookup kubernetes

Server:    10.10.0.2
Address 1: 10.10.0.2 kube-dns.kube-system.svc.cluster.local

Name:      kubernetes
Address 1: 10.10.0.1 kubernetes.default.svc.cluster.local
```

### 3.11 部署集群监控服务 Metrics Server

> 登陆到 `k8s-master1` 操作

```bash
$ cd ~/yaml

# 拉取 v0.3.6 版本
$ git clone https://github.com/kubernetes-sigs/metrics-server.git -b v0.3.6
$ cd metrics-server/deploy/1.8+
```

只修改 `metrics-server-deployment.yaml` 配置文件

```bash
# 下面是修改前后比较差异
$ git diff metrics-server-deployment.yaml

diff --git a/deploy/1.8+/metrics-server-deployment.yaml b/deploy/1.8+/metrics-server-deployment.yaml
index 2393e75..2139e4a 100644
--- a/deploy/1.8+/metrics-server-deployment.yaml
+++ b/deploy/1.8+/metrics-server-deployment.yaml
@@ -29,8 +29,19 @@ spec:
         emptyDir: {}
       containers:
       - name: metrics-server
-        image: k8s.gcr.io/metrics-server-amd64:v0.3.6
-        imagePullPolicy: Always
+        image: yangpeng2468/metrics-server-amd64:v0.3.6
+        imagePullPolicy: IfNotPresent
+        resources:
+          limits:
+            cpu: 400m
+            memory: 1024Mi
+          requests:
+            cpu: 50m
+            memory: 50Mi
+        command:
+        - /metrics-server
+        - --kubelet-insecure-tls
+        - --kubelet-preferred-address-types=InternalIP
         volumeMounts:
         - name: tmp-dir
           mountPath: /tmp
```

```bash
# 部署
$ kubectl apply -f .

# 验证
$ kubectl top node

NAME       CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
k8s-master1   72m          7%     1002Mi          53%
k8s-master2   121m         3%     1852Mi          12%
k8s-master3   300m         3%     1852Mi          20%

# 内存单位 Mi=1024*1024字节  M=1000*1000字节
# CPU单位 1核=1000m 即 250m=1/4核
```

### 3.12 部署 Kubernetes Dashboard

Kubernetes Dashboard 部署，请参考 [K8S Dashboard 2.0 部署](https://www.yp14.cn/2020/05/16/K8S-Dashboard-2-0-%E9%83%A8%E7%BD%B2%E5%B9%B6%E4%BD%BF%E7%94%A8-Ingress-Nginx-%E6%8F%90%E4%BE%9B%E8%AE%BF%E9%97%AE%E5%85%A5%E5%8F%A3/) 文章。

## 结束语

Kubernetes v1.18.2 二进制部署，作者测试过无坑。这篇部署文章完成可以直接用于生产环境部署。全方位包含整个 Kubernetes 组件部署。

## 参考链接

- https://blog.51cto.com/1014810/2474723
- https://docs.projectcalico.org/getting-started/kubernetes/installation/config-options#customizing-application-layer-policy-manifests
- https://docs.projectcalico.org/reference/node/configuration
- https://webcache.googleusercontent.com/search?q=cache:ihRi-OM5WboJ:https://www.cnblogs.com/Christine-ting/p/12837403.html+&cd=1&hl=zh-CN&ct=clnk