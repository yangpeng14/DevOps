## 前言

Kubernetes 集群备份一直是我们的痛点。虽然可以通过[备份ETCD](https://www.yp14.cn/2019/08/29/Etcd-v3%E5%A4%87%E4%BB%BD%E4%B8%8E%E6%81%A2%E5%A4%8D/)来实现K8S集群备份，但是这种备份很难恢复单个 `Namespace`。

今天推荐 `Velero` 工具，它提供以下功能：

- `灾备场景`：提供备份恢复k8s集群的能力
- `迁移场景`：提供拷贝集群资源到其他集群的能力（复制同步开发，测试，生产环境的集群配置，简化环境配置）


Velero 项目地址：https://github.com/vmware-tanzu/velero

Velero 阿里云插件地址：https://github.com/AliyunContainerService/velero-plugin

## Velero 架构

Velero 分为两部分：

- `服务端`：部署在目标 k8s 集群中
- `客户端`：运行在本地环境中，需要已配置好 `kubectl` 及集群 `kubeconfig` 的机器上

## 环境准备

> K8S 集群版本为 v1.18.2

阿里云 Velero 自定义 `RAM策略`

```json
{
    "Version": "1",
    "Statement": [
        {
            "Action": [
                "ecs:DescribeSnapshots",
                "ecs:CreateSnapshot",
                "ecs:DeleteSnapshot",
                "ecs:DescribeDisks",
                "ecs:CreateDisk",
                "ecs:Addtags",
                "oss:PutObject",
                "oss:GetObject",
                "oss:DeleteObject",
                "oss:GetBucket",
                "oss:ListObjects"
            ],
            "Resource": [
                "*"
            ],
            "Effect": "Allow"
        }
    ]
}
```

- 创建阿里云 `OSS`（对象存储）`Bucket`
    - 创建 `OSS Bucket` 请访问 https://www.aliyun.com/product/oss?spm=a2c6h.12873639.0.0.5f49340drYAEk0

- 创建阿里云 `创建RAM用户`，并自定义策略，把自定义策略加入到新创建的`RAM用户`中
    - 创建自定义策略（策略在上方），请访问链接 https://ram.console.aliyun.com/policies
    ![](/img/velero-2.png)
    - 创建 `RAM用户`并把`AK信息`复制出来为后面使用做准备，请参考链接 https://www.alibabacloud.com/help/zh/doc-detail/93720.htm
    ![](/img/velero-1.png)
    ![](/img/velero-3.png)

- 下载官方 velero 客户端 （https://github.com/vmware-tanzu/velero/releases）


## 部署 velero 插件服务端

> 项目地址 https://github.com/AliyunContainerService/velero-plugin

### 下载 velero 阿里云插件服务端

```bash
# 拉取 velero 阿里云插件服务端
$ git clone https://github.com/AliyunContainerService/velero-plugin.git

# 进入 velero-plugin 目录
$ cd velero-plugin
```

### 设置阿里云AK信息

把上面创建的 `RAM用户` AK 信息填写到 `credentials-velero` 文件中

```bash
$ vim install/credentials-velero

ALIBABA_CLOUD_ACCESS_KEY_ID=<ALIBABA_CLOUD_ACCESS_KEY_ID>
ALIBABA_CLOUD_ACCESS_KEY_SECRET=<ALIBABA_CLOUD_ACCESS_KEY_SECRET>
```

### 设置备份 OSS Bucket 与 可用区 并部署 velero

1、设置备份 OSS Bucket 和 可用区 环境变量

```bash
# OSS Bucket 名称
$ BUCKET=<YOUR_BUCKET>

# OSS 所在可用区
$ REGION=<YOUR_REGION>
```

2、创建 velero 命名空间 和 阿里云 secret

```bash
# 创建 velero 命名空间
$ kubectl create namespace velero

# 创建阿里云 secret
$ kubectl create secret generic cloud-credentials --namespace velero --from-file cloud=install/credentials-velero
```

3、部署 velero CRD 和 替换 OSS Bucket 与 OSS 所在可用区

```bash
# 部署 velero CRD
$ kubectl apply -f install/00-crds.yaml

# 替换 OSS Bucket 与 OSS 所在可用区
$ sed -i "s#<BUCKET>#$BUCKET#" install/01-velero.yaml
$ sed -i "s#<REGION>#$REGION#" install/01-velero.yaml
```

注意，本文把 velero 生成的备份都存放在 OSS `velero-k8s-backu` Bucket `huawei-k8s` 目录中，具体如下配置：

```bash
# 下面是本文的修改
$ git diff  install/01-velero.yaml

@@ -31,10 +31,10 @@ metadata:
   namespace: velero
 spec:
   config:
-    region: <REGION>
+    region: cn-beijing
   objectStorage:
-    bucket: <BUCKET>
-    prefix: ""
+    bucket: velero-k8s-backup
+    prefix: "huawei-k8s"
   provider: alibabacloud

 ---
@@ -47,11 +47,11 @@ metadata:
   namespace: velero
 spec:
   config:
-    region: <REGION>
+    region: cn-beijing
   provider: alibabacloud

 ---
-apiVersion: extensions/v1beta1
+apiVersion: apps/v1
 kind: Deployment
 metadata:
   name: velero
```

4、部署 velero

```bash
# 部署 velero
$ kubectl apply -f install/01-velero.yaml

# 查看 velero
$ kubectl  get pods -n velero

NAME                      READY   STATUS    RESTARTS   AGE
velero-6d4c7d4c9b-5zwll   1/1     Running   0          3h5m
```

## 备份与恢复演示

1、部署一个测试 nginx 服务

```bash
$ kubectl apply -f examples/base.yaml
```

2、使用 velero 创建备份

```bash
# 备份 nginx-example 整个命名空间，当前命名空间只有一个nginx服务
$ velero backup create nginx-backup --include-namespaces nginx-example --wait

Backup request "nginx-backup" submitted successfully.
Waiting for backup to complete. You may safely press ctrl-c to stop waiting - your backup will continue in the background.
.
Backup completed with status: Completed. You may check for more information using the commands `velero backup describe nginx-backup` and `velero backup logs nginx-backup`.
```

下面是通过阿里云 OSS 控制台查看，nginx-backup 已成功创建

![](/img/velero-4.png)

3、删除 nginx 服务

```bash
$ kubectl delete -f examples/base.yaml

deployment.apps "nginx-deployment" deleted
service "my-nginx" deleted
```

4、恢复 nginx 服务

```bash
# 使用 velero 恢复 nginx 服务
$ velero restore create --from-backup nginx-backup --wait

Restore request "nginx-backup-20200623174649" submitted successfully.
Waiting for restore to complete. You may safely press ctrl-c to stop waiting - your restore will continue in the background.

Restore completed with status: Completed. You may check for more information using the commands `velero restore describe nginx-backup-20200623174649` and `velero restore logs nginx-backup-20200623174649`.

# 查看 nginx 服务 是否成功恢复
$ kubectl  get pods -n nginx-example

NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-5bf87f5f59-gs2cs   1/1     Running   0          27s
nginx-deployment-5bf87f5f59-vts6d   1/1     Running   0          27s
```

> 注意：`velero restore` 恢复不会覆盖`已有的资源`，只恢复当前集群中`不存在的资源`。已有的资源不会回滚到之前的版本，如需要回滚，需在restore之前提前删除现有的资源。

## 带有持久卷备份与恢复

### 持久卷备份

```bash
$ velero backup create nginx-backup-volume --snapshot-volumes --include-namespaces nginx-example
```

> 注意：该备份会在集群所在region给云盘创建快照（当前还不支持NAS和OSS存储），快照恢复云盘只能在同region完成。

### 持久卷恢复

```bash
$ velero  restore create --from-backup nginx-backup-volume --restore-volumes
```

## velero 更多命令使用

查看备份位置

```bash
$ velero get backup-locations

NAME      PROVIDER       BUCKET/PREFIX                  ACCESS MODE
default   alibabacloud   velero-k8s-backup/huawei-k8s   ReadWrite
```

查看已有的备份

```bash
$ velero get backup
```

查看已有的恢复

```bash
$ velero get restores
```

查看 velero 插件

```bash
$ velero get plugins
```

删除 velero 备份

```bash
$ velero backup delete nginx-backup
```

创建集群所有namespaces备份，但排除 velero,metallb-system 命名空间

```bash
$ velero backup create all-ns-backup --snapshot-volumes=false --exclude-namespaces velero,metallb-system
```

恢复集群所有namespaces备份（对已经存在的服务不会覆盖）

```bash
$ velero restore create --from-backup all-ns-backup
```

恢复集群 default,nginx-example namespaces备份

```bash
$ velero restore create --from-backup all-ns-backup --include-namespaces default,nginx-example
```

## 高级备份功能

### 周期性定时备份

```bash
# 每日3点进行备份
$ velero schedule create <SCHEDULE NAME> --schedule "0 3 * * *"

# 每日3点进行备份，备份保留48小时，默认保留30天
$ velero schedule create <SCHEDULE NAME> --schedule "0 3 * * *" --ttl 48

# 每6小时进行一次备份
$ velero create schedule <SCHEDULE NAME> --schedule="@every 6h"

# 每日对 web namespace 进行一次备份
$ velero create schedule <SCHEDULE NAME> --schedule="@every 24h" --include-namespaces web
```

### 添加指定的标签备份时被排除

```bash
# 添加标签
$ kubectl label -n <ITEM_NAMESPACE> <RESOURCE>/<NAME> velero.io/exclude-from-backup=true

# 为 default namespace 添加标签
$ kubectl label -n default namespace/default velero.io/exclude-from-backup=true
```

## 迁移场景

和集群恢复场景类似，velero 可以帮助我们把一个k8s集群的resource导出并导入到另外一个集群，只要将每个Velero实例指向同一个云对象存储位置，Velero就可以帮助我们将资源从一个集群移植到另一个集群，请注意，Velero不支持跨云提供商迁移持久卷。当前使用velero迁移集群功能最完善的场景是在同一个云厂商的同一个region，可以恢复集群的应用和数据卷。

### 在集群1上做一个备份：

```bash
$ velero backup create <BACKUP-NAME> --snapshot-volumes
```

### 在集群2上做一个恢复：

```bash
$ velero restore create --from-backup <BACKUP-NAME> --restore-volumes
```

## velero 清理

```bash
$ kubectl delete namespace/velero clusterrolebinding/velero
$ kubectl delete crds -l component=velero
```

## 总结

Velero 作为一个免费的开源组件，其能力基本可以满足容器服务的灾备和迁移的场景，推荐用户将velero日常备份作为运维的一部分，未雨绸缪，防患未然。

## 参考链接

- https://developer.aliyun.com/article/705007
- https://github.com/AliyunContainerService/velero-plugin