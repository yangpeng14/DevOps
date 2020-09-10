## 故障一

### 故障现象

kubelet 启动不了，通过命令 `journalctl -u kubelet` 查看日志，报 `Failed to start ContainerManager failed to initialize top level QOS containers: failed to update top level Burstable QOS cgroup : failed to set supported cgroup subsystems for cgroup [kubepods burstable]: failed to find subsystem mount for required subsystem: pids`

### 故障分析

根据报错，有用的信息是 `failed to find subsystem mount for required subsystem: pids`，通过命令 `ls -l /sys/fs/cgroup/systemd/kubepods/burstable/` 查看，该目录下没有 `pids` 目录。

`SupportPodPidsLimit` 在 kubernetes `1.14+` 默认开启。 SupportNodePidsLimit 在 `1.15+` 默认开启。

> 相关Issues：https://github.com/kubernetes/kubernetes/issues/79046

### 解决方法

- 方法一：编辑 kubelet 配置文件，添加 `--feature-gates=SupportPodPidsLimit=false,SupportNodePidsLimit=false` 参数，后面在重启 kubelet 服务。
- 方法二：可以升级系统内核 `5+` 版本

## 故障二

### 故障现象

Docker daemon oci 故障，日志报 `docker: Error response from daemon: OCI runtime create failed: container_linux.go:348: starting container process caused "process_linux.go:301: running exec setns process for init caused \"exit status 40\"": unknown.`

### 解决方法

```bash
# 清理缓存
$ echo 1 > /proc/sys/vm/drop_caches

# 永久生效
$ echo "vm.min_free_kbytes=1048576" >> /etc/sysctl.conf
$ sysctl -p

# 重启 docker 服务，让 docker 应用内核设置
$ systemctl restart docker
```

## 故障三

### 报错现象

kubelet 日志报 `network plugin is not ready: cni config uninitialized`

### 解决方法

网络插件（flannel 或者 calico）没有安装或者安装失败。

## 故障四

### 故障现象

kubelet 日志报 `Failed to connect to apiserver: the server has asked for the client to provide credentials` 

### 故障分析

从上面 kubelet 日志信息能得出，kubelet 客户端证书已过期，导致 Node节点状态处于 `NotReady`。

也可以通过命令 `openssl x509 -noout -enddate -in {证书路径}` 来查看证书到期日期。

### 解决方法

#### kubeadm 部署的 Kubernetes 解决方法

kubernetes 1.15+ 版本可以直接通过命令 `kubeadm alpha certs renew <cert_name>` 更新。

kubernetes 小于 1.15 版本的，可以参考 `https://github.com/yuyicai/update-kube-cert` 项目更新

#### 二进制部署的 Kubernetes 解决方法

```bash
# 删除旧的 kubelet 证书文件
$ rm -f  /opt/kubernetes/ssl/kubelet*

# 删除 kubelet kubeconfig 文件
$ rm -f /opt/kubernetes/cfg/kubelet.kubeconfig

# 重启 kubelet 服务，让 master 重新颁发客户端证书
$ systemctl restart kubelet
```

## 参考链接
- https://adoyle.me/Today-I-Learned/k8s/k8s-deployment.html