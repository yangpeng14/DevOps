---
参考链接:
---
https://skyao.gitbooks.io/learning-etcd3/content/documentation/op-guide/recovery.html
https://github.com/coreos/etcd/blob/master/Documentation/op-guide/recovery.md

#### 一、灾难恢复

etcd 被设计为能承受机器失败。etcd 集群自动从临时失败(例如，机器重启)中恢复，而且对于一个有 N 个成员的集群能容许 (N-1)/2 的持续失败。当一个成员持续失败时，不管是因为硬件失败或者磁盘损坏，它丢失到集群的访问。如果集群持续丢失超过 (N-1)/2 的成员，则它只能悲惨的失败，无可救药的失去法定人数(quorum)。一旦法定人数丢失，集群无法达到一致而因此无法继续接收更新。
为了从灾难失败中恢复，etcd v3 提供快照和修复工具来重建集群而不丢失 v3 键数据。要恢复 v2 的键，参考v2 管理指南.

#### 二、快照键空间

恢复集群首先需要来自 etcd 成员的键空间的快照。快速可以是用 etcdctl snapshot save 命令从活动成员获取，或者是从 etcd 数据目录复制 member/snap/db 文件. 例如，下列命令快照在 $ENDPOINT 上服务的键空间到文件 snapshot.db:

```
$ etcdctl --endpoints $ENDPOINT snapshot save snapshot.db
```

#### 三、恢复集群

为了恢复集群，需要的只是一个简单的快照 "db" 文件。使用 etcdctl snapshot restore 的集群恢复创建新的 etcd 数据目录;所有成员应该使用相同的快照恢复。恢复覆盖某些快照元数据(特别是，成员ID和集群ID);成员丢失它之前的标识。这个元数据覆盖防止新的成员不经意间加入已有的集群。因此为了从快照启动集群，恢复必须启动一个新的逻辑集群。

在恢复时快照完整性的检验是可选的。如果快照是通过 etcdctl snapshot save 得到的，它将有一个被 etcdctl snapshot restore 检查过的完整性hash。如果快照是从数据目录复制而来，没有完整性hash，因此它只能通过使用 --skip-hash-check 来恢复。
恢复初始化新集群的新成员，带有新的集群配置，使用 etcd 的集群配置标记，但是保存 etcd 键空间的内容。继续上面的例子，下面为一个3成员的集群创建新的 etcd 数据目录(m1.etcd, m2.etcd, m3.etcd):

```
$ etcdctl snapshot restore snapshot.db \
  --name m1 \
  --initial-cluster m1=http:/host1:2380,m2=http://host2:2380,m3=http://host3:2380 \
  --initial-cluster-token etcd-cluster-1 \
  --initial-advertise-peer-urls http://host1:2380 \
  --data-dir=/var/lib/etcd/default.etcd
  
$ etcdctl snapshot restore snapshot.db \
  --name m2 \
  --initial-cluster m1=http:/host1:2380,m2=http://host2:2380,m3=http://host3:2380 \
  --initial-cluster-token etcd-cluster-1 \
  --initial-advertise-peer-urls http://host2:2380 \
  --data-dir=/var/lib/etcd/default.etcd
  
$ etcdctl snapshot restore snapshot.db \
  --name m3 \
  --initial-cluster m1=http:/host1:2380,m2=http://host2:2380,m3=http://host3:2380 \
  --initial-cluster-token etcd-cluster-1 \
  --initial-advertise-peer-urls http://host3:2380 \
  --data-dir=/var/lib/etcd/default.etcd
```

#### 四、用新的数据目录启动 etcd :

```
$ etcd \
  --name m1 \
  --listen-client-urls http://host1:2379 \
  --advertise-client-urls http://host1:2379 \
  --listen-peer-urls http://host1:2380 \
  --data-dir=/var/lib/etcd/default.etcd &
$ etcd \
  --name m2 \
  --listen-client-urls http://host2:2379 \
  --advertise-client-urls http://host2:2379 \
  --listen-peer-urls http://host2:2380 \
  --data-dir=/var/lib/etcd/default.etcd &
$ etcd \
  --name m3 \
  --listen-client-urls http://host3:2379 \
  --advertise-client-urls http://host3:2379 \
  --listen-peer-urls http://host3:2380 \
  --data-dir=/var/lib/etcd/default.etcd &
```
现在恢复的集群可以使用并提供来自快照的键空间服务.
