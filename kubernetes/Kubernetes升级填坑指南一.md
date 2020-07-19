## 前言

下面 “坑” 都是作者升级 Kubernetes 遇到的问题并给出解决方法，目的就是避免读者不要在掉进同样的坑中。

## 第一个坑

### 升级 Calico 网络组件

#### 要求

Calico `v3.2.3` 升级到 `v3.14.0`

#### 遇到的问题

`Readiness probe failed: caliconode is not ready: BIRD is not ready: BGP not established with 172.18.0.1`

#### 问题原因

通过 `calicoctl node status` 命令排查，能看到 Calico 自动发现网卡出错。Calico 默认自动会识别第一个网卡，但是后面因为在宿主机使用 `docker-compose` 创建新的服务并且也会创建一个新的网卡，Calico 重启后自动识别 `docker-compose` 创建的网卡。导致集群 node 节点不能相互通信，就会报上面错误。

#### 解决方法

`临时解决方法`：

把 `docker-compose` 创建的服务直接使用 `docker run` 来创建，这样就不会创建一个新的网卡。

`最终解决方法`：

Calico 是通过 Kubernetes yaml 文件部署的，所以直接在 yaml 文件中添加下面配置，在 `calico-node` DaemonSet `env` 中添加环境变量，定义网卡发现规则。

```yaml
            # 定义ipv4自动发现网卡规则
            - name: IP_AUTODETECTION_METHOD
              value: "interface=eth.*"
            # 定义ipv6自动发现网卡规则
            - name: IP6_AUTODETECTION_METHOD
              value: "interface=eth.*"
```

## 第二个坑

### Calico 组件配置

#### 环境

Kubernetes master 与 node 节点分别在不同云厂商

#### 遇到的问题

`[ERROR][8] startup/startup.go 146: failed to query kubeadm’s config map error=Get https://10.10.0.1:443/api/v1/namespaces/kube-system/configmaps/kubeadm-config?timeout=2s: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)`

#### 问题原因

Node工作节点连接不到 `apiserver` 地址，检查一下calico配置文件，要把apiserver的IP和端口配置上，如果不配置的话，calico默认将设置默认的calico网段和443端口。字段名：`KUBERNETES_SERVICE_HOST`、`KUBERNETES_SERVICE_PORT`、`KUBERNETES_SERVICE_PORT_HTTPS`。

#### 解决方法

Calico 是通过 Kubernetes yaml 文件部署的，所以直接在 yaml 文件中添加下面配置，在 `calico-node` DaemonSet `env` 中添加环境变量。

```yaml
- name: KUBERNETES_SERVICE_HOST
  value: "kube-apiserver"  # master apiserver 地址
- name: KUBERNETES_SERVICE_PORT
  value: "6443"
- name: KUBERNETES_SERVICE_PORT_HTTPS
  value: "6443"
```

## 第三个坑

### Etcd v3.3.9 升级到 v3.4.7

#### 环境

flannel 使用 v0.10.0 版本

#### 遇到的问题

`Etcd` 需要升级到 `v3.4.7` 版本，从 `v3.3.9` 直接升级到 `v3.4.7` 是没有问题的。但升级完成后，在查看 `flannel` 日志时，发现日志不断报 `E0714 14:49:48.309007    2887 main.go:349] Couldn't fetch network config: client: response is invalid json. The endpoint is probably not valid etcd cluster endpoint.` 错误。刚才开始以为是 flannel 版本过低导致，后面把 flannel 升级到最新版本 `v0.12.0`，但是问题还是一样。

#### 问题原因

后面仔细通过排查，发现是连接不上 `Etcd`，当时很疑惑 Etce 连接不上，可 `kube-apiserver` 连接是正常的，后面才想起来，`kube-apiserver` 使用 Etcd `v3接口`，而 `flannel` 使用 `v2接口`。怀疑在升级 Etcd 时默认没有开启 `v2接口`。最后查阅官方 Etcd v3.4 发布说明，从 3.4 版本开始，默认已经关闭 v2 接口协议，才导致上面报错。

#### 解决方法

直接在 Etcd 启动参数添加 `--enable-v2 'true'`

## 预告

明天分享下作者近期 Kubernetes 从 `v1.15.3` 升级到 `v1.18.5` 心得。大家可以关注我的公众号。即时收到明天的 Kubernetes 升级心得哈 ^v^。