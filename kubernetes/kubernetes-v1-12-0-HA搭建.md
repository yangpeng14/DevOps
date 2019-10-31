---
参考链接:
```
https://cloud.tencent.com/developer/article/1115558  配置基础环境
http://blog.51cto.com/hequan/2106618 搭建ha k8s
https://mritd.me/2017/07/21/set-up-kubernetes-ha-cluster-by-binary/ 部署calico网络(1) 和 ha k8s 参考
http://blog.51cto.com/newfly/2062210 部署calico网络(2)
http://m635674608.iteye.com/blog/2344151 sdn比较
```
#### 一、服务器信息

- Centos7.4 系统 和 Docker version 18.06.1-ce

主机名 | IP | 备注
---|---|---
k8s-master1 | 192.168.1.126 | 主集群1,etcd1,node1
k8s-master2 | 192.168.1.127 | 主集群2,etcd2,node2
k8s-master3 | 192.168.1.128 | 主集群3,etcd3,node3
slb         | 192.168.1.129/39.105.81.231 | slb内网和外网ip地址，设置TCP监听，监听6443端口

##### Service 和 Pods ip段划分
名称  |  IP段  | 备注
---|---|---
service-cluster-ip | 10.10.0.0/16 | 可用地址 4094
pods-ip            | 10.20.0.0/16 | 可用地址 4094
集群dns            | 10.10.0.2    | 用于集群service域名解析

#### 二、环境初始化

##### 1.1 分别在3台主机设置主机名称

```
hostnamectl set-hostname k8s-master1
hostnamectl set-hostname k8s-master2
hostnamectl set-hostname k8s-master3
```

##### 1.2 配置主机映射 /etc/hosts/

```
192.168.1.126 k8s-master1 etcd1
192.168.1.127 k8s-master2 etcd2
192.168.1.128 k8s-master3 etcd3
```

##### 1.3 master1上执行ssh免密码登陆配置

```
ssh-keygen  #一路回车即可
ssh-copy-id  k8s-master02 #这里需要输入 yes和密码
ssh-copy-id  k8s-master03
```

##### 1.4 三台主机配置（基础环境）

```
# 停防火墙
systemctl stop firewalld
systemctl disable firewalld

#关闭Swap
swapoff -a 
sed -i 's/.*swap.*/#&/' /etc/fstab

#关闭Selinux
setenforce  0 
sed -i "s/^SELINUX=enforcing/SELINUX=disabled/g" /etc/sysconfig/selinux 
sed -i "s/^SELINUX=enforcing/SELINUX=disabled/g" /etc/selinux/config 
sed -i "s/^SELINUX=permissive/SELINUX=disabled/g" /etc/sysconfig/selinux 
sed -i "s/^SELINUX=permissive/SELINUX=disabled/g" /etc/selinux/config  

#加载br_netfilter
modprobe br_netfilter

#添加配置内核参数
cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
#加载配置
sysctl -p /etc/sysctl.d/k8s.conf

#查看是否生成相关文件
ls /proc/sys/net/bridge

# 添加K8S的国内yum源
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64/
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg https://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF

#安装依赖包以及相关工具
yum install -y epel-release
yum install -y yum-utils device-mapper-persistent-data lvm2 net-tools conntrack-tools wget vim  ntpdate libseccomp libtool-ltdl 

#配置ntp（配置完后建议重启一次）
systemctl enable ntpdate.service
echo '*/30 * * * * /usr/sbin/ntpdate time7.aliyun.com >/dev/null 2>&1' > /tmp/crontab2.tmp
crontab /tmp/crontab2.tmp
systemctl start ntpdate.service

# /etc/security/limits.conf 是 Linux 资源使用配置文件，用来限制用户对系统资源的使用
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf
echo "* soft nproc 65536"  >> /etc/security/limits.conf
echo "* hard nproc 65536"  >> /etc/security/limits.conf
echo "* soft  memlock  unlimited"  >> /etc/security/limits.conf
echo "* hard memlock  unlimited"  >> /etc/security/limits.conf
```

#### 三、K8S部署

```
1、安装Docker
2、自签TLS证书
3、部署Etcd集群
4、创建Node节点kubeconfig文件
5、获取K8S二进制包
6、运行Master组件
7、运行Node组件
8、查询集群状态
9、安装calico网络，使用IPIP模式
10、集群CoreDNS部署
11、集群dashboard、监控部署
12、调整集群参数,为node预留资源
```

##### 1.1 安装Docker

在k8s-master1、k8s-master2、k8s-master3操作
```
mkdir  /data/docker
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

sudo yum makecache fast
sudo yum -y install docker-ce

docker version
systemctl enable docker.service    
systemctl start docker.service

sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{"registry-mirrors": ["https://4xr1qpsp.mirror.aliyuncs.com"],"graph": "/data/docker"}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker
```

##### 1.2 自签TLS证书

组件  |  使用的证书
---|---
etcd   | ca.pem, server.pem, server-key.pem
calico | ca.pem, server.pem, server-key.pem
kube-apiserver | ca.pem, server.pem, server-key.pem
kube-controller-manager | ca.pem, ca-key.pem
kubelet | ca.pem, ca-key.pem
kube-proxy | ca.pem, kube-proxy.pem, kube-proxy-key.pem
kubectl | ca.pem, admin.pem, admin-key.pem

k8s-master1 安装证书生成工具cfssl：
```
mkdir /data/ssl -p

wget https://pkg.cfssl.org/R1.2/cfssl_linux-amd64
wget https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64
wget https://pkg.cfssl.org/R1.2/cfssl-certinfo_linux-amd64

chmod +x cfssl_linux-amd64 cfssljson_linux-amd64 cfssl-certinfo_linux-amd64

mv cfssl_linux-amd64 /usr/local/bin/cfssl
mv cfssljson_linux-amd64 /usr/local/bin/cfssljson
mv cfssl-certinfo_linux-amd64 /usr/bin/cfssl-certinfo

cd /data/ssl/
```

创建certificate.sh

```
# vim  certificate.sh

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
      "192.168.1.126",
      "192.168.1.127",
      "192.168.1.128",
      "10.10.0.1",
      "192.168.1.129",
      "39.105.81.231",
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

上个脚本，根据实际情况修改如下，然后执行
```
 50       "192.168.1.126",
 51       "192.168.1.127",
 52       "192.168.1.128",
 53       "10.10.0.1",
 54       "192.168.1.129",
 55       "39.105.81.231",
```

##### 1.3 部署Etcd集群
k8s-master1机器上操作，在把执行文件copy到k8s-master2 k8s-master3
```
二进制包下载地址： https://github.com/etcd-io/etcd/releases/tag/v3.3.9

3个节点

mkdir /data/etcd/
cd /data/etcd/

mkdir /opt/kubernetes/{bin,cfg,ssl}  -p
tar zxvf etcd-v3.3.9-linux-amd64.tar.gz
cd etcd-v3.3.9-linux-amd64/
cp etcd etcdctl  /opt/kubernetes/bin/

echo 'export PATH=$PATH:/opt/kubernetes/bin' >> /etc/profile

source /etc/profile

cd /data/ssl
cp ca*pem  server*pem  /opt/kubernetes/ssl/

scp -r /opt/kubernetes/*  root@k8s-master2:/opt/kubernetes
scp -r /opt/kubernetes/*  root@k8s-master3:/opt/kubernetes
```

```
cd /data/etcd
# vim  etcd.sh

#!/bin/bash

ETCD_NAME=${1:-"etcd01"}
ETCD_IP=${2:-"127.0.0.1"}
ETCD_CLUSTER=${3:-"etcd01=http://127.0.0.1:2379"}

cat <<EOF >/opt/kubernetes/cfg/etcd
#[Member]
ETCD_NAME="${ETCD_NAME}"
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
ETCD_LISTEN_PEER_URLS="https://${ETCD_IP}:2380"
ETCD_LISTEN_CLIENT_URLS="https://${ETCD_IP}:2379"

#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://${ETCD_IP}:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://${ETCD_IP}:2379"
ETCD_INITIAL_CLUSTER="${ETCD_CLUSTER}"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="new"
EOF

cat <<EOF >/usr/lib/systemd/system/etcd.service
[Unit]
Description=Etcd Server
After=network.target
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
EnvironmentFile=-/opt/kubernetes/cfg/etcd
ExecStart=/opt/kubernetes/bin/etcd \\
--name=\${ETCD_NAME} \\
--data-dir=\${ETCD_DATA_DIR} \\
--listen-peer-urls=\${ETCD_LISTEN_PEER_URLS} \\
--listen-client-urls=\${ETCD_LISTEN_CLIENT_URLS},http://127.0.0.1:2379 \\
--advertise-client-urls=\${ETCD_ADVERTISE_CLIENT_URLS} \\
--initial-advertise-peer-urls=\${ETCD_INITIAL_ADVERTISE_PEER_URLS} \\
--initial-cluster=\${ETCD_INITIAL_CLUSTER} \\
--initial-cluster-token=\${ETCD_INITIAL_CLUSTER_TOKEN} \\
--initial-cluster-state=new \\
--cert-file=/opt/kubernetes/ssl/server.pem \\
--key-file=/opt/kubernetes/ssl/server-key.pem \\
--peer-cert-file=/opt/kubernetes/ssl/server.pem \\
--peer-key-file=/opt/kubernetes/ssl/server-key.pem \\
--trusted-ca-file=/opt/kubernetes/ssl/ca.pem \\
--peer-trusted-ca-file=/opt/kubernetes/ssl/ca.pem
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable etcd
systemctl restart etcd
```

```
chmod +x etcd.sh
master1:   ./etcd.sh  etcd01 192.168.1.126  etcd01=https://192.168.1.126:2380,etcd02=https://192.168.1.127:2380,etcd03=https://192.168.1.128:2380
master2:   ./etcd.sh  etcd02 192.168.1.127  etcd01=https://192.168.1.126:2380,etcd02=https://192.168.1.127:2380,etcd03=https://192.168.1.128:2380
master3:   ./etcd.sh  etcd03 192.168.1.128  etcd01=https://192.168.1.126:2380,etcd02=https://192.168.1.127:2380,etcd03=https://192.168.1.128:2380

# 检查etcd集群是否健康，如下输出集群是健康的
cd /opt/kubernetes/ssl
ETCDCTL_API=3 /opt/kubernetes/bin/etcdctl \
--cacert=ca.pem --cert=server.pem --key=server-key.pem \
--endpoints="https://192.168.1.126:2379,https://192.168.1.127:2379,https://192.168.1.128:2379" \
endpoint health

# 输出结果
https://192.168.1.128:2379 is healthy: successfully committed proposal: took = 1.467801ms
https://192.168.1.127:2379 is healthy: successfully committed proposal: took = 1.678981ms
https://192.168.1.126:2379 is healthy: successfully committed proposal: took = 1.714306ms
```

##### 1.4 创建Node节点kubeconfig文件

k8s-master1节点操作

- 创建TLS Bootstrapping Token
- 创建kubelet kubeconfig
- 创建kube-proxy kubeconfig

```
cd /data/ssl/
vim kubeconfig.sh          ##修改第10行 ip

# 创建 TLS Bootstrapping Token
export BOOTSTRAP_TOKEN=$(head -c 16 /dev/urandom | od -An -t x | tr -d ' ')
cat > token.csv <<EOF
${BOOTSTRAP_TOKEN},kubelet-bootstrap,10001,"system:kubelet-bootstrap"
EOF

#----------------------

# 创建kubelet bootstrapping kubeconfig
export KUBE_APISERVER="https://192.168.1.129:6443"

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

```
##  kubectl   软件在kubernetes-server-linux-amd64.tar.gz  里面,可从官网下载,下面的部署也需要这个软件包

mv kubectl  /opt/kubernetes/bin
chmod +x /opt/kubernetes/bin/kubectl

sh kubeconfig.sh
# 输出下面结果
kubeconfig.sh   kube-proxy-csr.json  kube-proxy.kubeconfig
kube-proxy.csr  kube-proxy-key.pem   kube-proxy.pem bootstrap.kubeconfig

cp *kubeconfig /opt/kubernetes/cfg
```

```
scp *kubeconfig root@k8s-master2:/opt/kubernetes/cfg
scp *kubeconfig root@k8s-master3:/opt/kubernetes/cfg
```

##### 1.5 获取K8S二进制包

```
https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG-1.12.md  # v1.12.0

mkdir /data/k8s
cd /data/k8s
wget https://dl.k8s.io/v1.12.0/kubernetes-server-linux-amd64.tar.gz
tar xf kubernetes-server-linux-amd64.tar.gz
```

master 需要用到
- kubectl
- kube-scheduler
- kube-apiserver
- kube-controller-manager

node 需要用到
- kubelet
- kube-proxy

```
mkdir /data/k8s-master
cd /data/k8s-master

vim   apiserver.sh

#!/bin/bash

MASTER_ADDRESS=${1:-"192.168.1.126"}
ETCD_SERVERS=${2:-"http://127.0.0.1:2379"}

cat <<EOF >/opt/kubernetes/cfg/kube-apiserver

KUBE_APISERVER_OPTS="--logtostderr=true \\
--v=4 \\
--etcd-servers=${ETCD_SERVERS} \\
--insecure-bind-address=127.0.0.1 \\
--bind-address=${MASTER_ADDRESS} \\
--insecure-port=8080 \\
--secure-port=6443 \\
--advertise-address=${MASTER_ADDRESS} \\
--allow-privileged=true \\
--service-cluster-ip-range=10.10.0.0/16 \\
--admission-control=NamespaceLifecycle,LimitRanger,SecurityContextDeny,ServiceAccount,ResourceQuota,NodeRestriction \
--authorization-mode=RBAC,Node \\
--kubelet-https=true \\
--enable-bootstrap-token-auth \\
--token-auth-file=/opt/kubernetes/cfg/token.csv \\
--service-node-port-range=30000-50000 \\
--tls-cert-file=/opt/kubernetes/ssl/server.pem  \\
--tls-private-key-file=/opt/kubernetes/ssl/server-key.pem \\
--client-ca-file=/opt/kubernetes/ssl/ca.pem \\
--service-account-key-file=/opt/kubernetes/ssl/ca-key.pem \\
--etcd-cafile=/opt/kubernetes/ssl/ca.pem \\
--etcd-certfile=/opt/kubernetes/ssl/server.pem \\
--etcd-keyfile=/opt/kubernetes/ssl/server-key.pem"

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

```
vim controller-manager.sh

#!/bin/bash

MASTER_ADDRESS=${1:-"127.0.0.1"}

cat <<EOF >/opt/kubernetes/cfg/kube-controller-manager

KUBE_CONTROLLER_MANAGER_OPTS="--logtostderr=true \\
--v=4 \\
--master=${MASTER_ADDRESS}:8080 \\
--leader-elect=true \\
--address=0.0.0.0 \\
--service-cluster-ip-range=10.10.0.0/16 \\
--cluster-name=kubernetes \\
--horizontal-pod-autoscaler-use-rest-clients=false \\
--cluster-signing-cert-file=/opt/kubernetes/ssl/ca.pem \\
--cluster-signing-key-file=/opt/kubernetes/ssl/ca-key.pem  \\
--service-account-private-key-file=/opt/kubernetes/ssl/ca-key.pem \\
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

```
vim scheduler.sh

#!/bin/bash

MASTER_ADDRESS=${1:-"127.0.0.1"}

cat <<EOF >/opt/kubernetes/cfg/kube-scheduler

KUBE_SCHEDULER_OPTS="--logtostderr=true \\
--v=4 \\
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

##### 1.6 运行Master组件

在k8s-master1 操作
```
cd /data/k8s/kubernetes/server/bin
mv kube-apiserver kube-controller-manager kube-scheduler kubectl /opt/kubernetes/bin
chmod +x /opt/kubernetes/bin/*
chmod +x *.sh

cp ssl/token.csv /opt/kubernetes/cfg/

ls /opt/kubernetes/ssl/
# 输出结果
ca-key.pem  ca.pem  server-key.pem  server.pem

# k8s-master1 运行
./apiserver.sh 192.168.1.126 https://192.168.1.126:2379,https://192.168.1.127:2379,https://192.168.1.128:2379
./scheduler.sh 127.0.0.1
./controller-manager.sh 127.0.0.1

PS: controller-manager 配置中设置为 --horizontal-pod-autoscaler-use-rest-clients=false 调用老的监控接口

scp -r /data/ssl/token.csv k8s-master2:/opt/kubernetes/cfg
scp -r /data/ssl/token.csv k8s-master3:/opt/kubernetes/cfg
scp -r /opt/kubernetes/bin/kube* k8s-master2:/opt/kubernetes/bin/
scp -r /opt/kubernetes/bin/kube* k8s-master3:/opt/kubernetes/bin/
scp -r /data/k8s-master k8s-master2:/data/
scp -r /data/k8s-master k8s-master3:/data/

# k8s-master2 运行
./apiserver.sh 192.168.1.127 https://192.168.1.126:2379,https://192.168.1.127:2379,https://192.168.1.128:2379
./scheduler.sh 127.0.0.1
./controller-manager.sh 127.0.0.1

# k8s-master3 运行
./apiserver.sh 192.168.1.128 https://192.168.1.126:2379,https://192.168.1.127:2379,https://192.168.1.128:2379
./scheduler.sh 127.0.0.1
./controller-manager.sh 127.0.0.1
```

- 登陆七牛云或者阿里云slb控制台设置slb，前后监控都为6443端口，TCP方式（本文使用七牛云ECS搭建,他们slb有内网和外网地址，阿里云只显示外网地址）
- k8s-master1 上创建node授权用户

```
kubectl create clusterrolebinding  kubelet-bootstrap --clusterrole=system:node-bootstrapper  --user=kubelet-bootstrap

```
- 检查集群

```
[root@k8s-master1 k8s-master]# kubectl get cs
NAME                 STATUS    MESSAGE             ERROR
controller-manager   Healthy   ok
scheduler            Healthy   ok
etcd-2               Healthy   {"health":"true"}
etcd-1               Healthy   {"health":"true"}
etcd-0               Healthy   {"health":"true"}
```

##### 1.7 运行Node组件

在k8s-master1 操作
```
mkdir /data/k8s-node
cd /data/k8s-node

vim  kubelet.sh

#!/bin/bash

NODE_ADDRESS=${1:-"192.168.1.126"}
DNS_SERVER_IP=${2:-"10.10.0.2"}

cat <<EOF >/opt/kubernetes/cfg/kubelet

KUBELET_OPTS="--logtostderr=true \\
--v=4 \\
--address=${NODE_ADDRESS} \\
--hostname-override=${NODE_ADDRESS} \\
--kubeconfig=/opt/kubernetes/cfg/kubelet.kubeconfig \\
--experimental-bootstrap-kubeconfig=/opt/kubernetes/cfg/bootstrap.kubeconfig \\
--cert-dir=/opt/kubernetes/ssl \\
--allow-privileged=true \\
--cluster-dns=${DNS_SERVER_IP} \\
--cluster-domain=cluster.local \\
--fail-swap-on=false \\
--pod-infra-container-image=registry.cn-hangzhou.aliyuncs.com/google-containers/pause-amd64:3.0"

EOF

cat <<EOF >/usr/lib/systemd/system/kubelet.service
[Unit]
Description=Kubernetes Kubelet
After=docker.service
Requires=docker.service

[Service]
EnvironmentFile=-/opt/kubernetes/cfg/kubelet
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

```
vim proxy.sh

#!/bin/bash

NODE_ADDRESS=${1:-"192.168.1.126"}

cat <<EOF >/opt/kubernetes/cfg/kube-proxy

KUBE_PROXY_OPTS="--logtostderr=true \
--v=4 \
--hostname-override=${NODE_ADDRESS} \
--kubeconfig=/opt/kubernetes/cfg/kube-proxy.kubeconfig"

EOF

cat <<EOF >/usr/lib/systemd/system/kube-proxy.service
[Unit]
Description=Kubernetes Proxy
After=network.target

[Service]
EnvironmentFile=-/opt/kubernetes/cfg/kube-proxy
ExecStart=/opt/kubernetes/bin/kube-proxy \$KUBE_PROXY_OPTS
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable kube-proxy
systemctl restart kube-proxy
```

```
cd /data/k8s/kubernetes/server/bin
mv kubelet kube-proxy /opt/kubernetes/bin
chmod +x *.sh

scp -r /opt/kubernetes/bin/kube-proxy /opt/kubernetes/bin/kubelet k8s-master2:/opt/kubernetes/bin/
scp -r /opt/kubernetes/bin/kube-proxy /opt/kubernetes/bin/kubelet k8s-master3:/opt/kubernetes/bin/
scp -r /data/k8s-node k8s-master2:/data/
scp -r /data/k8s-node k8s-master3:/data/

# k8s-master1 操作
./kubelet.sh 192.168.1.126 10.10.0.2
./proxy.sh 192.168.1.126

# k8s-master2 操作
./kubelet.sh 192.168.1.127 10.10.0.2
./proxy.sh 192.168.1.127

# k8s-master3 操作
./kubelet.sh 192.168.1.128 10.10.0.2
./proxy.sh 192.168.1.128

# k8s-master1 操作

$ kubectl get csr

NAME                                                   AGE       REQUESTOR           CONDITION
node-csr-OBBWrBrJEDjmG2Cnu62ZGfRPfElYXbzrBOdwZoNP9GY   2m        kubelet-bootstrap   Pending

$ kubectl  certificate approve node-csr-OBBWrBrJEDjmG2Cnu62ZGfRPfElYXbzrBOdwZoNP9GY

certificatesigningrequest "node-csr-OBBWrBrJEDjmG2Cnu62ZGfRPfElYXbzrBOdwZoNP9GY" approved

$ kubectl get csr

NAME                                                   AGE       REQUESTOR           CONDITION
node-csr-OBBWrBrJEDjmG2Cnu62ZGfRPfElYXbzrBOdwZoNP9GY   3m        kubelet-bootstrap   Approved,Issued

$ kubectl get node
NAME            STATUS   ROLES    AGE    VERSION
192.168.1.126   Ready    <none>   2d4h   v1.12.0-rc.2
192.168.1.127   Ready    <none>   2d4h   v1.12.0-rc.2
192.168.1.128   Ready    <none>   2d4h   v1.12.0-rc.2
```

##### 1.8 查看集群状态

```
kubectl get componentstatus
kubectl get node
kubectl cluster-info
```

##### 1.9 安装calico网络，使用IPIP模式

- calico介绍

```
Calico组件：

     Felix：Calico agent     运行在每台node上，为容器设置网络信息：IP,路由规则，iptable规则等

     etcd：calico后端存储

     BIRD:  BGP Client： 负责把Felix在各node上设置的路由信息广播到Calico网络( 通过BGP协议)。

     BGP Route Reflector： 大规模集群的分级路由分发。

     calico： calico命令行管理工具

```

- 为各Node部署calico的步骤如下：

1、下载部署的yaml文件（在k8s-master1操作）：

```
# 参照官方文档：https://docs.projectcalico.org/v2.6/getting-started/kubernetes/installation/hosted/hosted 

wget https://docs.projectcalico.org/v2.6/getting-started/kubernetes/installation/rbac.yaml
wget https://docs.projectcalico.org/v2.6/getting-started/kubernetes/installation/hosted/calico.yaml
```

2、对于RBAC文件，不用做修改，直接创建即可：

```
# kubectl create -f calico-rbac.yaml 

# 输出结果
clusterrole "calico-kube-controllers" created
clusterrolebinding "calico-kube-controllers" created
clusterrole "calico-node" created
clusterrolebinding "calico-node" created
```

3、配置calico

```
# vim calico.yaml

data:
  # Configure this with the location of your etcd cluster.
  etcd_endpoints: "https://192.168.1.126:2379,https://192.168.1.127:2379,https://192.168.1.128:2379"
  
  # If you're using TLS enabled etcd uncomment the following.
  # You must also populate the Secret below with these files.  
  etcd_ca: "/calico-secrets/etcd-ca"   #取消原来的注释即可
  etcd_cert: "/calico-secrets/etcd-cert"
  etcd_key: "/calico-secrets/etcd-key"
  
  
apiVersion: v1
kind: Secret
type: Opaque
metadata:
  name: calico-etcd-secrets
  namespace: kube-system
data:  
  etcd-key: (cat /opt/kubernetes/ssl/server-key.pem | base64 | tr -d '\n') #将输出结果填写在这里
  etcd-cert: (cat /opt/kubernetes/ssl/server.pem | base64 | tr -d '\n') #将输出结果填写在这里
  etcd-ca: (cat /opt/kubernetes/ssl/ca.pem | base64 | tr -d '\n') #将输出结果填写在这里 #将输出结果填写在这里
   #如果etcd没用启用tls则为null 
  #上面是必须要修改的参数，文件中有一个参数是设置pod network地址的，根据实际情况做修改：
   - name: CALICO_IPV4POOL_CIDR
     value: "10.20.0.0/16"
```

```
关于ConfigMap部分主要参数如下：

    etcd_endpoints：Calico使用etcd来保存网络拓扑和状态，该参数指定etcd的地址，可以使用K8S Master所用的etcd，也可以另外搭建。

    calico_backend：Calico的后端，默认为bird。

    cni_network_config：符合CNI规范的网络配置，其中type=calico表示，Kubelet从 CNI_PATH(默认为/opt/cni/bin)找名为calico的可执行文件，用于容器IP地址的分配。

etcd如果配置了TLS安全认证，则还需要指定相应的ca、cert、key等文件



关于通过DaemonSet部署的calico-node服务的主要参数：

      该POD中主包括如下两个容器：

          calico-node：calico服务程序，用于设置Pod的网络资源，保证pod的网络与各Node互联互通，它还需要以HostNetwork模式运行，直接使用宿主机网络。

          install-cni：在各Node上安装CNI二进制文件到/opt/cni/bin目录下，并安装相应的网络配置文件到/etc/cni/net.d目录下。

    

      calico-node服务的主要参数：

         CALICO_IPV4POOL_CIDR： Calico IPAM的IP地址池，Pod的IP地址将从该池中进行分配。

         CALICO_IPV4POOL_IPIP：是否启用IPIP模式，启用IPIP模式时，Calico将在node上创建一个tunl0的虚拟隧道。

         FELIX_LOGSEVERITYSCREEN： 日志级别。

         FELIX_IPV6SUPPORT ： 是否启用IPV6。

      IP Pool可以使用两种模式：BGP或IPIP。使用IPIP模式时，设置 CALICO_IPV4POOL_IPIP="always"，不使用IPIP模式时，设置为"off"，此时将使用BGP模式。

      IPIP是一种将各Node的路由之间做一个tunnel，再把两个网络连接起来的模式，启用IPIP模式时，Calico将在各Node上创建一个名为"tunl0"的虚拟网络接口。
```

4、创建：

```
# kubectl create -f calico.yaml 

# 输出结果
configmap "calico-config" created
secret "calico-etcd-secrets" created
daemonset "calico-node" created
deployment "calico-kube-controllers" created
deployment "calico-policy-controller" created
serviceaccount "calico-kube-controllers" created
serviceaccount "calico-node" created

# 查看是否创建成功
# kubectl get deployment,pod -n kube-system 

# 输出结果
NAME                              DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
deploy/calico-kube-controllers    1         1         1            1           4m
deploy/calico-policy-controller   0         0         0            0           4m

NAME                                           READY     STATUS    RESTARTS   AGE
po/calico-kube-controllers-56d9f8c44c-6hftd    1/1       Running   0          4m
po/calico-node-6k827                           2/2       Running   0          4m
po/calico-node-wfbpz                           2/2       Running   0          4m

#calico-node用的是daemonset，会在每个node上启动一个
```

```
 DaemonSet： 
     name: calico-node 这个pod里运行两个容器
	 hostNetwork: true
	 serviceAccountName: calico-node
	 两个容器：
	      name: calico-node
	      image: quay.io/calico/node:v2.6.5
	
	      name: install-cni
	      image: quay.io/calico/cni:v1.11.2
	      command: ["/install-cni.sh"]

  Deployment
      name ---calico-kube-controllers replicas: 1   #网络策略控制器
      serviceAccountName: calico-kube-controllers
      containers：        
        - name: calico-kube-controllers
          image: quay.io/calico/kube-controllers:v1.0.2
```

5、修改kubelet配置：

```
设置各node上Kubelet服务的启动参数： --network-plugin=cni， 可能还要加上这两个参数：

       --cni-conf-dir  CNI插件的配置文件目录，默认为/etc/cni/net.d 该目录下的配置文件内容需要符合CNI规范

       --cni-bin-dir： CNI插件的可执行文件目录，默认为/opt/cni/bin

    设置 master上的kube-apiserver服务的启动参数: --allow-privileged=true (因为calico-node需要以特权模式运行在各node上)
    
    设置好后，重新启动kubelet。

这样通过calico就完成了Node间容器网络的设置 ，在后续的pod创建过程中，Kubelet将通过CNI接口调用 calico进行Pod的网络设置包括IP地址，路由规则，Iptables规则 
```

```
# 本文修改后的 kubelet 配置

vim /opt/kubernetes/cfg/kubelet

KUBELET_OPTS="--logtostderr=true \
--v=4 \
--address=192.168.1.126 \
--hostname-override=192.168.1.126 \
--kubeconfig=/opt/kubernetes/cfg/kubelet.kubeconfig \
--experimental-bootstrap-kubeconfig=/opt/kubernetes/cfg/bootstrap.kubeconfig \
--cert-dir=/opt/kubernetes/ssl \
--allow-privileged=true \
--cluster-dns=10.10.0.2 \
--cluster-domain=cluster.local \
--fail-swap-on=false \
--network-plugin=cni \
--cni-conf-dir=/etc/cni/net.d \
--cni-bin-dir=/opt/cni/bin \
--pod-infra-container-image=registry.cn-hangzhou.aliyuncs.com/google-containers/pause-amd64:3.0"
```

6，验证各Node间网络联通性:

```
kubelet启动后主机上就生成了一个tunl0接口。
#第一台Node查看：
root@k8s-master1# ip route
10.20.4.192/26 via 192.168.1.128 dev tunl0 proto bird onlink
10.20.6.0/26 via 192.168.1.127 dev tunl0 proto bird onlink

#第二台Node查看：
root@k8s-master2# ip route
10.20.1.0/26 via 192.168.1.126 dev tunl0 proto bird onlink
10.20.4.192/26 via 192.168.1.128 dev tunl0 proto bird onlink

#第三台Node查看：
root@k8s-master3# ip route
10.20.1.0/26 via 192.168.1.126 dev tunl0 proto bird onlink
10.20.6.0/26 via 192.168.1.127 dev tunl0 proto bird onlink

# 每台node上都自动设置了到其它node上pod网络的路由，去往其它节点的路都是通过tunl0接口，这就是IPIP模式。
# 注意，发现每个node ip段子网掩码是26位，这样可用ip地址只有62个，大家可以放心如果一台node地址用完62个ip地址后，calico会在分配一个62位子网掩码用于使用

```

```
# 如果设置CALICO_IPV4POOL_IPIP="off" ，即不使用IPIP模式，则Calico将不会创建tunl0网络接口，路由规则直接使用物理机网卡作为路由器转发。
```

##### 1.10 集群CoreDNS部署

1、下载coredns部署包（k8s-master机器上操作）

```
# 参考链接：https://my.oschina.net/u/2306127/blog/1788566

mkdir -p /root/yaml/coredns
git clone https://github.com/coredns/deployment.git
cd deployment/kubernetes/

# deploy.sh是一个便捷的脚本，用于生成用于在当前运行标准kube-dns的集群上运行CoreDNS的清单。使用coredns.yaml.sed文件作为模板，它创建一个ConfigMap和一个CoreDNS  deployment，然后更新 Kube-DNS service selector以使用CoreDNS deployment。 通过重新使用现有服务，服务请求不会中断。
```

2、部署CoreDNS

```
# 默认情况下CLUSTER_DNS_IP是自动获取kube-dns的集群ip的，但是由于没有部署kube-dns所以只能手动指定一个集群ip了
# 修改 deploy.sh 脚本

120 if [[ -z $CLUSTER_DNS_IP ]]; then
121   # Default IP to kube-dns IP
122   #CLUSTER_DNS_IP=$(kubectl get service --namespace kube-system kube-dns -o jsonpath="{.spec.clusterIP}" $KUBECONFIG)
123   CLUSTER_DNS_IP=10.10.0.2

# 把 CLUSTER_DNS_IP 注释掉，添加 CLUSTER_DNS_IP=10.10.0.2 

# 查看执行效果，并未开始部署 （10.10.0.0/16 是service-cluster-ip段ip地址）
./deploy.sh 10.10.0.0/16 cluster.local

# 执行部署
./deploy.sh 10.10.0.0/16 cluster.local | kubectl apply -f -

# 查看命令
kubectl get svc,pods -n kube-system
```

3、测试dns解析
```
dig kube-dns.kube-system.svc.cluster.local @10.10.0.2    #能解析出ip就说明dns部署成功
```

##### 1.11 集群dashboard、监控部署
```
参考链接：
https://www.kubernetes.org.cn/3834.html Kubernetes1.10中部署dashboard以及常见问题解析
https://github.com/kubernetes/dashboard/wiki/Installation 官方dashboard安装指南
https://blog.csdn.net/hekanhyde/article/details/78618190 k8s dashboard 安装账号密码登陆设置方法
https://juejin.im/entry/5a615bbb6fb9a01cb42c6d9a 权限讲解
```

1、拷贝*.yp14.cn证书

```
# 通过Let's Encrypt 免费获取通配符证书实现Https

$ mkdir /root/certs/
$ ls -lsh certs/

yp14.cn.crt  yp14.cn.key
```

2、创建认证secret
```
kubectl create secret generic kubernetes-dashboard-certs --from-file=$HOME/certs -n kube-system
```

3、创建相关yaml配置文件

```
# mkdir -p /root/yaml/kubernetes-dashboard
# vim kubernetes-dashboard.yaml

# Copyright 2017 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Configuration to deploy release version of the Dashboard UI compatible with
# Kubernetes 1.8.
#
# Example usage: kubectl create -f <this_file>

# ------------------- Dashboard Secret ------------------- #

#apiVersion: v1
#kind: Secret
#metadata:
#  labels:
#    k8s-app: kubernetes-dashboard
#  name: kubernetes-dashboard-certs
#  namespace: kube-system
#type: Opaque

---
# ------------------- Dashboard Service Account ------------------- #

apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kube-system

---
# ------------------- Dashboard Role & Role Binding ------------------- #

kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: kubernetes-dashboard-minimal
  namespace: kube-system
rules:
  # Allow Dashboard to create 'kubernetes-dashboard-key-holder' secret.
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["create"]
  # Allow Dashboard to create 'kubernetes-dashboard-settings' config map.
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["create"]
  # Allow Dashboard to get, update and delete Dashboard exclusive secrets.
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["kubernetes-dashboard-key-holder", "kubernetes-dashboard-certs"]
  verbs: ["get", "update", "delete"]
  # Allow Dashboard to get and update 'kubernetes-dashboard-settings' config map.
- apiGroups: [""]
  resources: ["configmaps"]
  resourceNames: ["kubernetes-dashboard-settings"]
  verbs: ["get", "update"]
  # Allow Dashboard to get metrics from heapster.
- apiGroups: [""]
  resources: ["services"]
  resourceNames: ["heapster"]
  verbs: ["proxy"]
- apiGroups: [""]
  resources: ["services/proxy"]
  resourceNames: ["heapster", "http:heapster:", "https:heapster:"]
  verbs: ["get"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: kubernetes-dashboard-minimal
  namespace: kube-system
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: kubernetes-dashboard-minimal
subjects:
- kind: ServiceAccount
  name: kubernetes-dashboard
  namespace: kube-system

---
# ------------------- Dashboard Deployment ------------------- #

kind: Deployment
apiVersion: apps/v1beta2
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kube-system
spec:
  replicas: 1
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      k8s-app: kubernetes-dashboard
  template:
    metadata:
      labels:
        k8s-app: kubernetes-dashboard
    spec:
      containers:
      - name: kubernetes-dashboard
        image: k8s.gcr.io/kubernetes-dashboard-amd64:v1.10.0
        ports:
        - containerPort: 8443
          protocol: TCP
        args:
          - --tls-key-file=yp14.cn.key
          - --tls-cert-file=yp14.cn.crt
          - --token-ttl=3600
          # - --authentication-mode=basic
          # - --auto-generate-certificates
          # Uncomment the following line to manually specify Kubernetes API server Host
          # If not specified, Dashboard will attempt to auto discover the API server and connect
          # to it. Uncomment only if the default does not work.
          # - --apiserver-host=http://my-address:port
        volumeMounts:
        - name: kubernetes-dashboard-certs
          mountPath: /certs
          # Create on-disk volume to store exec logs
        - mountPath: /tmp
          name: tmp-volume
        livenessProbe:
          httpGet:
            scheme: HTTPS
            path: /
            port: 8443
          initialDelaySeconds: 30
          timeoutSeconds: 30
      volumes:
      - name: kubernetes-dashboard-certs
        secret:
          secretName: kubernetes-dashboard-certs
      - name: tmp-volume
        emptyDir: {}
      serviceAccountName: kubernetes-dashboard
      # Comment the following tolerations if Dashboard must not be deployed on master
      tolerations:
      - key: node-role.kubernetes.io/master
        effect: NoSchedule

---
# ------------------- Dashboard Service ------------------- #

kind: Service
apiVersion: v1
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kube-system
spec:
  ports:
    - port: 443
      targetPort: 8443
      nodePort: 30000
  type: NodePort
  selector:
    k8s-app: kubernetes-dashboard
```

```
kubectl apply -f kubernetes-dashboard.yaml
```

```
# vim heapster-rbac.yaml

kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: heapster
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:heapster
subjects:
- kind: ServiceAccount
  name: heapster
  namespace: kube-system
  

# vim heapster.yaml

apiVersion: v1
kind: ServiceAccount
metadata:
  name: heapster
  namespace: kube-system
---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: heapster
  namespace: kube-system
spec:
  replicas: 1
  template:
    metadata:
      labels:
        task: monitoring
        k8s-app: heapster
    spec:
      serviceAccountName: heapster
      containers:
      - name: heapster
        image: k8s.gcr.io/heapster-amd64:v1.4.2
        imagePullPolicy: IfNotPresent
        command:
        - /heapster
        - --source=kubernetes:https://kubernetes.default
        - --sink=influxdb:http://monitoring-influxdb.kube-system.svc:8086
---
apiVersion: v1
kind: Service
metadata:
  labels:
    task: monitoring
    # For use as a Cluster add-on (https://github.com/kubernetes/kubernetes/tree/master/cluster/addons)
    # If you are NOT using this as an addon, you should comment out this line.
    kubernetes.io/cluster-service: 'true'
    kubernetes.io/name: Heapster
  name: heapster
  namespace: kube-system
spec:
  ports:
  - port: 80
    targetPort: 8082
  selector:
    k8s-app: heapster


```

```
kubectl apply -f heapster-rbac.yaml -f heapster.yaml
```

```
# vim influxdb.yaml

apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: monitoring-influxdb
  namespace: kube-system
spec:
  replicas: 1
  template:
    metadata:
      labels:
        task: monitoring
        k8s-app: influxdb
    spec:
      containers:
      - name: influxdb
        image: gcr.io/google-containers/heapster-influxdb-amd64:v1.3.3
        volumeMounts:
        - mountPath: /data
          name: influxdb-storage
      volumes:
      - name: influxdb-storage
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  labels:
    task: monitoring
    # For use as a Cluster add-on (https://github.com/kubernetes/kubernetes/tree/master/cluster/addons)
    # If you are NOT using this as an addon, you should comment out this line.
    kubernetes.io/cluster-service: 'true'
    kubernetes.io/name: monitoring-influxdb
  name: monitoring-influxdb
  namespace: kube-system
spec:
  ports:
  - port: 8086
    targetPort: 8086
  selector:
    k8s-app: influxdb
```

```
kubectl apply -f influxdb.yaml
```

```
# vim grafana.yaml

apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: monitoring-grafana
  namespace: kube-system
spec:
  replicas: 1
  template:
    metadata:
      labels:
        task: monitoring
        k8s-app: grafana
    spec:
      containers:
      - name: grafana
        image: gcr.io/google-containers/heapster-grafana-amd64:v4.4.3
        ports:
        - containerPort: 3000
          protocol: TCP
        volumeMounts:
        - mountPath: /etc/ssl/certs
          name: ca-certificates
          readOnly: true
        - mountPath: /var
          name: grafana-storage
        env:
        - name: INFLUXDB_HOST
          value: monitoring-influxdb
        - name: GF_SERVER_HTTP_PORT
          value: "3000"
          # The following env variables are required to make Grafana accessible via
          # the kubernetes api-server proxy. On production clusters, we recommend
          # removing these env variables, setup auth for grafana, and expose the grafana
          # service using a LoadBalancer or a public IP.
        - name: GF_AUTH_BASIC_ENABLED
          value: "false"
        - name: GF_AUTH_ANONYMOUS_ENABLED
          value: "true"
        - name: GF_AUTH_ANONYMOUS_ORG_ROLE
          value: Admin
        - name: GF_SERVER_ROOT_URL
          # If you're only using the API Server proxy, set this value instead:
          # value: /api/v1/namespaces/kube-system/services/monitoring-grafana/proxy
          value: /
      volumes:
      - name: ca-certificates
        hostPath:
          #path: /etc/ssl/certs
          path: /root/certs
      - name: grafana-storage
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  labels:
    # For use as a Cluster add-on (https://github.com/kubernetes/kubernetes/tree/master/cluster/addons)
    # If you are NOT using this as an addon, you should comment out this line.
    kubernetes.io/cluster-service: 'true'
    kubernetes.io/name: monitoring-grafana
  name: monitoring-grafana
  namespace: kube-system
spec:
  # In a production setup, we recommend accessing Grafana through an external Loadbalancer
  # or through a public IP.
  # type: LoadBalancer
  # You could also use NodePort to expose the service at a randomly-generated port
  type: NodePort
  ports:
  - port: 80
    targetPort: 3000
    nodePort: 30001
  selector:
    k8s-app: grafana
```

```
kubectl apply -f grafana.yaml
```

```
# 查看部署是否成功

kubectl get deployments,svc,pods -n kube-system
```

##### 1.12 调整集群参数,为node预留资源

```
# 设置node保留资源配置(机器配置2核4G，参数只是参考，并不是唯一) 参考 https://blog.8mi.net/Kubernetes/75.html


KUBELET_OPTS="--logtostderr=true \
--v=4 \
--address=192.168.1.126 \
--hostname-override=192.168.1.126 \
--kubeconfig=/opt/kubernetes/cfg/kubelet.kubeconfig \
--experimental-bootstrap-kubeconfig=/opt/kubernetes/cfg/bootstrap.kubeconfig \
--cert-dir=/opt/kubernetes/ssl \
--allow-privileged=true \
--cluster-dns=10.10.0.2 \
--cluster-domain=cluster.local \
--fail-swap-on=false \
--network-plugin=cni \
--cni-conf-dir=/etc/cni/net.d \
--cni-bin-dir=/opt/cni/bin \
--system-reserved=cpu=500m,memory=1Gi \
--eviction-hard=memory.available<1Gi,nodefs.available<3Gi,imagefs.available<4Gi \
--eviction-soft=memory.available<1.2Gi,nodefs.available<5Gi,imagefs.available<6Gi \
--eviction-soft-grace-period=memory.available=2m,nodefs.available=2m,imagefs.available=2m \
--eviction-max-pod-grace-period=30 \
--eviction-minimum-reclaim=memory.available=200Mi,nodefs.available=1Gi,imagefs.available=1Gi \
--pod-infra-container-image=registry.cn-hangzhou.aliyuncs.com/google-containers/pause-amd64:3.0"
```

```
systemctl restart kubelet
```
