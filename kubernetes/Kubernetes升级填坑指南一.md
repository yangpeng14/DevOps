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

把 `docker-compose` 创建的服务直接使用 `docker run` 来操作，这样就不会创建一个新的网卡。

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