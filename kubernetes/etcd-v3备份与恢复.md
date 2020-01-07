## ETCD 简介

`ETCD` 是用于共享配置和服务发现的分布式，一致性的KV存储系统。ETCD是CoreOS公司发起的一个开源项目，授权协议为Apache。

## ETCD 使用场景

ETCD 有很多使用场景，包括但不限于：

- 配置管理
- 服务注册于发现
- 选主
- 应用调度
- 分布式队列
- 分布式锁

## ETCD 存储 k8s 所有数据信息

ETCD 是k8s集群极为重要的一块服务，存储了集群所有的数据信息。同理，如果发生灾难或者 etcd 的数据丢失，都会影响集群数据的恢复。所以，本文重点讲如何备份和恢复数据。

## ETCD 一些查询操作

- 查看集群状态
    ```bash
    $ ETCDCTL_API=3 etcdctl --cacert=/opt/kubernetes/ssl/ca.pem --cert=/opt/kubernetes/ssl/server.pem --key=/opt/kubernetes/ssl/server-key.pem --endpoints=https://192.168.1.36:2379,https://192.168.1.37:2379,https://192.168.1.38:2379 endpoint health

    https://192.168.1.36:2379 is healthy: successfully committed proposal: took = 1.698385ms
    https://192.168.1.37:2379 is healthy: successfully committed proposal: took = 1.577913ms
    https://192.168.1.38:2379 is healthy: successfully committed proposal: took = 5.616079ms
    ```

- 获取某个 key 信息

    ```bash
    $ ETCDCTL_API=3 etcdctl --cacert=/opt/kubernetes/ssl/ca.pem --cert=/opt/kubernetes/ssl/server.pem --key=/opt/kubernetes/ssl/server-key.pem --endpoints=https://192.168.1.36:2379,https://192.168.1.37:2379,https://192.168.1.38:2379 get /registry/apiregistration.k8s.io/apiservices/v1.apps 
    ```

- 获取 etcd 版本信息

    ```bash
    $ ETCDCTL_API=3 etcdctl --cacert=/opt/kubernetes/ssl/ca.pem --cert=/opt/kubernetes/ssl/server.pem --key=/opt/kubernetes/ssl/server-key.pem --endpoints=https://192.168.1.36:2379,https://192.168.1.37:2379,https://192.168.1.38:2379 version 
    ```

- 获取 ETCD 所有的 key

    ```bash
    $ ETCDCTL_API=3 etcdctl --cacert=/opt/kubernetes/ssl/ca.pem --cert=/opt/kubernetes/ssl/server.pem --key=/opt/kubernetes/ssl/server-key.pem --endpoints=https://192.168.1.36:2379,https://192.168.1.37:2379,https://192.168.1.38:2379 get / --prefix --keys-only
    ```

## 环境

主机 | IP
---|---
k8s-master1 | 192.168.1.36
k8s-master2 | 192.168.1.37
k8s-master3 | 192.168.1.38

- ETCD version 3.2.12
- Kubernetes version v1.15.6 二进制安装

## 备份

`注意`：ETCD 不同的版本的 etcdctl 命令不一样，但大致差不多，本文备份使用 `napshot save` , 每次备份`一个节点`就行。

`命令备份`（k8s-master1 机器上备份）：

```bash
$ ETCDCTL_API=3 etcdctl --cacert=/opt/kubernetes/ssl/ca.pem --cert=/opt/kubernetes/ssl/server.pem --key=/opt/kubernetes/ssl/server-key.pem --endpoints=https://192.168.1.36:2379 snapshot save /data/etcd_backup_dir/etcd-snapshot-`date +%Y%m%d`.db
```

`备份脚本`（k8s-master1 机器上备份）：

```sh
#!/usr/bin/env bash

date;

CACERT="/opt/kubernetes/ssl/ca.pem"
CERT="/opt/kubernetes/ssl/server.pem"
EKY="/opt/kubernetes/ssl/server-key.pem"
ENDPOINTS="192.168.1.36:2379"

ETCDCTL_API=3 etcdctl \
--cacert="${CACERT}" --cert="${CERT}" --key="${EKY}" \
--endpoints=${ENDPOINTS} \
snapshot save /data/etcd_backup_dir/etcd-snapshot-`date +%Y%m%d`.db

# 备份保留30天
find /data/etcd_backup_dir/ -name *.db -mtime +30 -exec rm -f {} \;
```

## 恢复

### 准备工作

- 停止所有 Master 上 `kube-apiserver` 服务

    ```bash
    $ systemctl stop kube-apiserver

    # 确认 kube-apiserver 服务是否停止
    $ ps -ef | grep kube-apiserver
    ```

- 停止集群中所有 ETCD 服务

    ```bash
    $ systemctl stop etcd
    ```

- 移除所有 ETCD 存储目录下数据

    ```bash
    $ mv /var/lib/etcd/default.etcd /var/lib/etcd/default.etcd.bak
    ```

- 拷贝 ETCD 备份快照

    ```bash
    # 从 k8s-master1 机器上拷贝备份
    $ scp /data/etcd_backup_dir/etcd-snapshot-20191222.db root@k8s-master2:/data/etcd_backup_dir/
    $ scp /data/etcd_backup_dir/etcd-snapshot-20191222.db root@k8s-master3:/data/etcd_backup_dir/
    ```

### 恢复备份

```bash
# k8s-master1 机器上操作
$ ETCDCTL_API=3 etcdctl snapshot restore /data/etcd_backup_dir/etcd-snapshot-20191222.db \
  --name etcd-0 \
  --initial-cluster "etcd-0=https://192.168.1.36:2380,etcd-1=https://192.168.1.37:2380,etcd-2=https://192.168.1.38:2380" \
  --initial-cluster-token etcd-cluster \
  --initial-advertise-peer-urls https://192.168.1.36:2380 \
  --data-dir=/var/lib/etcd/default.etcd
  
# k8s-master2 机器上操作
$ ETCDCTL_API=3 etcdctl snapshot restore /data/etcd_backup_dir/etcd-snapshot-20191222.db \
  --name etcd-1 \
  --initial-cluster "etcd-0=https://192.168.1.36:2380,etcd-1=https://192.168.1.37:2380,etcd-2=https://192.168.1.38:2380"  \
  --initial-cluster-token etcd-cluster \
  --initial-advertise-peer-urls https://192.168.1.37:2380 \
  --data-dir=/var/lib/etcd/default.etcd
  
# k8s-master3 机器上操作
$ ETCDCTL_API=3 etcdctl snapshot restore /data/etcd_backup_dir/etcd-snapshot-20191222.db \
  --name etcd-2 \
  --initial-cluster "etcd-0=https://192.168.1.36:2380,etcd-1=https://192.168.1.37:2380,etcd-2=https://192.168.1.38:2380"  \
  --initial-cluster-token etcd-cluster \
  --initial-advertise-peer-urls https://192.168.1.38:2380 \
  --data-dir=/var/lib/etcd/default.etcd
```

上面三台 ETCD 都恢复完成后，依次登陆三台机器启动 ETCD

```bash
$ systemctl start etcd
```

三台 ETCD 启动完成，检查 ETCD 集群状态

```bash
$ ETCDCTL_API=3 etcdctl --cacert=/opt/kubernetes/ssl/ca.pem --cert=/opt/kubernetes/ssl/server.pem --key=/opt/kubernetes/ssl/server-key.pem --endpoints=https://192.168.1.36:2379,https://192.168.1.37:2379,https://192.168.1.38:2379 endpoint health
```

三台 ETCD 全部健康，分别到每台 Master 启动 kube-apiserver

```bash
$ systemctl start kube-apiserver
```

检查 Kubernetes 集群是否恢复正常

```bash
$ kubectl get cs
```

## 总结

Kubernetes 集群备份主要是备份 ETCD 集群。而恢复时，主要考虑恢复整个顺序：

`停止kube-apiserver --> 停止ETCD --> 恢复数据 --> 启动ETCD --> 启动kube-apiserve`

`注意`：备份ETCD集群时，只需要备份一个ETCD就行，恢复时，拿同一份备份数据恢复。

## 参考链接

- https://yq.aliyun.com/articles/11035
- https://www.jianshu.com/p/8b483ed49f26