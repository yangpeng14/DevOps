## 前言

基于 [Kubernetes v1.18.2 二进制高可用部署](https://www.yp14.cn/2020/05/19/Kubernetes-v1-18-2-%E4%BA%8C%E8%BF%9B%E5%88%B6%E9%AB%98%E5%8F%AF%E7%94%A8%E9%83%A8%E7%BD%B2/) 基础上添加 `Node节点`。

## 注意事项

- 脚本中 `SSL证书` 下载链接 `https://.../k8s-v1.18.2-ssl.tar.gz` 需要`自己提供`，因为每个集群 `SSL证书` 不一样。
- `k8s-v1.18.2-ssl.tar.gz` 包文件目录结构如下：

```
k8s-v1.18.2-ssl
├── bootstrap.kubeconfig
├── ca-key.pem
├── ca.pem
├── kube-proxy.kubeconfig
├── server-key.pem
└── server.pem

0 directories, 6 files
```

- `k8s-v1.18.2.tar.gz` 包文件目录结构如下：

```
k8s-v1.18.2
├── kubernetes-configure
│   └── k8s-node
│       ├── kubelet.sh
│       └── proxy.sh
└── kubernetes-package
    ├── kubelet
    └── kube-proxy

3 directories, 4 files
```

## 添加 Node 节点

```bash
# 创建Node节点初始化脚本
$ vim Init_Node.sh
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
        echo "`ifconfig eth0 | grep -w inet | awk '{print $2}'` $HostName" >> /etc/hosts
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
    # 设置 iptables file表中 FORWARD 默认链规则为 ACCEPT
    sed  -i '/ExecStart=/i ExecStartPost=\/sbin\/iptables -P FORWARD ACCEPT' /usr/lib/systemd/system/docker.service
    systemctl enable docker.service
    systemctl start docker.service
    systemctl stop docker.service
    echo '{"registry-mirrors": ["https://4xr1qpsp.mirror.aliyuncs.com"], "log-opts": {"max-size":"500m", "max-file":"3"}}' > /etc/docker/daemon.json
    systemctl daemon-reload
    systemctl start docker
}

function Install_k8s_node(){
    ps aux | grep kube | grep -v grep &> /dev/null && echo -e "\033[32;32m k8s node服务已启动，退出初始化node服务步骤 \033[0m \n" && return
    mkdir -p /opt/kubernetes/{bin,cfg,ssl} /data/k8s-node
    cd /data/k8s-node
    # 添加更换为自己集群SSL证书下载地址
    wget https://.../k8s-v1.18.2-ssl.tar.gz
    tar zxvf k8s-v1.18.2-ssl.tar.gz
    cd k8s-v1.18.2-ssl/
    cp ca*pem server*pem /opt/kubernetes/ssl/
    cp *kubeconfig /opt/kubernetes/cfg/
    cd /data/k8s-node
    wget https://cdm.yp14.cn/k8s-script/k8s-v1.18.2.tar.gz
    tar zxvf k8s-v1.18.2.tar.gz
    cd k8s-v1.18.2/kubernetes-package/
    cp -a kubelet kube-proxy /opt/kubernetes/bin/
    chmod +x /opt/kubernetes/bin/kubelet /opt/kubernetes/bin/kube-proxy
    echo 'export PATH=$PATH:/opt/kubernetes/bin' >> ~/.bashrc
    source ~/.bashrc
    # 删除 tar 包
    rm -f /data/k8s-node/k8s-v1.18.2-ssl.tar.gz /data/k8s-node/k8s-v1.18.2.tar.gz
    cd /data/k8s-node/k8s-v1.18.2/kubernetes-configure/k8s-node
    # kubelet.sh 后面接的参数分别为：集群dns地址、Node节点主机名、集群域名后辍
    bash kubelet.sh 10.10.0.2 $HostName cluster.local
    # proxy.sh 后面接的参数分别为：Node节点主机名
    bash proxy.sh $HostName
}

# 初始化顺序
HostName=$1
Check_linux_system && \
Set_hostname && \
Install_depend_environment && \
Install_docker && \
Install_k8s_node
```

```bash
# 给脚本添加执行权限
$ chmod +x Init_Node.sh

# 执行添加Node节点脚本，需要传入 主机名 参数
$ ./Init_Node.sh k8s-node1

# 成功添加好Node节点，需要把Node节点重启，使用新的内核
$ reboot
```