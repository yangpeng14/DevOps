1. etcd v3 查询k8s数据
```
ETCDCTL_API=3 etcdctl \
--cacert="/opt/kubernetes/ssl/ca.pem" --cert="/opt/kubernetes/ssl/server.pem" --key="/opt/kubernetes/ssl/server-key.pem" \
--endpoints=[172.17.94.200:2379] \
get /registry --prefix
```

2. 快照键空间
```
ETCDCTL_API=3 etcdctl \
--cacert="/opt/kubernetes/ssl/ca.pem" --cert="/opt/kubernetes/ssl/server.pem" --key="/opt/kubernetes/ssl/server-key.pem" \
--endpoints=[172.17.94.200:2379] \
snapshot save snapshot-`date +%Y%m%d`.db
```

