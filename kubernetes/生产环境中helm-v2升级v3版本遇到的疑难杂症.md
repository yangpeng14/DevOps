## 前言

Helm `V3` 与 `V2` 版本架构变化较大，数据迁移也比较麻烦，官方为了解决数据迁移问题，提供一个 `helm-2to3` 工具，本文基于 `helm-2to3` 工具来迁移 `V2` 版本中的数据。

Helm `V3` 与 `V2` 变化，请参考 [Helm v3 新的功能](https://www.yp14.cn/2019/11/18/Helm-v3-%E6%96%B0%E7%9A%84%E5%8A%9F%E8%83%BD/)

> 注意：Helm `V2` 升级 `V3` 版本，Kubernetes 集群中 Deployment、Service、Pod等都不会重新创建，所以迁移过程是不会影响线上在跑的服务。

## 安装 Helm V3 命令

下载 helm 最新 v3.2.3 版本

```bash
$ wget https://get.helm.sh/helm-v3.2.3-linux-amd64.tar.gz -O /tmp/helm-v3.2.3-linux-amd64.tar.gz
```

解压并移动到 `/usr/local/bin/` 目录下

```bash
# 解压
$ tar xf /tmp/helm-v3.2.3-linux-amd64.tar.gz

# 移动
$ cd /tmp/linux-amd64
$ mv helm /usr/local/bin/helm3
```

## 安装 2to3 插件

一键安装

```bash
$ helm3 plugin install https://github.com/helm/helm-2to3
```

检查 2to3 插件是否安装成功

```bash
$ helm3 plugin list

NAME	VERSION	DESCRIPTION
2to3	0.5.1  	migrate and cleanup Helm v2 configuration and releases in-place to Helm v3
```

## 迁移 Helm V2 配置

下面操作主要迁移：

- Helm 插件
- Chart 仓库
- Chart starters

```bash
$ helm3 2to3 move config
```

检查 `repo` 和 `plugin`

```bash
# 检查 repo
$ helm3 repo list

NAME      	URL
stable    	https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts

# 更新 repo
$ helm3 repo update

Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "stable" chart repository

# 检查 plugin
$ helm3 plugin list

NAME	VERSION	DESCRIPTION
2to3	0.5.1  	migrate and cleanup Helm v2 configuration and releases in-place to Helm v3
```

## 迁移 Heml V2 Release

### 查看 2to3 插件中 `convert` 子命令选项

```bash
$ helm3 2to3 convert --help

migrate Helm v2 release in-place to Helm v3

Usage:
  2to3 convert [flags] RELEASE

Flags:
      --delete-v2-releases         v2 release versions are deleted after migration. By default, the v2 release versions are retained
      --dry-run                    simulate a command
  -h, --help                       help for convert
      --kube-context string        name of the kubeconfig context to use
      --kubeconfig string          path to the kubeconfig file
  -l, --label string               label to select Tiller resources by (default "OWNER=TILLER")
  -s, --release-storage string     v2 release storage type/object. It can be 'secrets' or 'configmaps'. This is only used with the 'tiller-out-cluster' flag (default "secrets")
      --release-versions-max int   limit the maximum number of versions converted per release. Use 0 for no limit (default 10)
  -t, --tiller-ns string           namespace of Tiller (default "kube-system")
      --tiller-out-cluster         when  Tiller is not running in the cluster e.g. Tillerless
```

- `--dry-run`：模拟迁移但不做真实迁移操作，建议每次迁移都先带上这个参数测试下效果，没问题的话再去掉这个参数做真实迁移
- `--tiller-ns`：通常 `tiller` 部署在k8s集群中，但不在 `kube-system` 命名空间才指定
- `--tiller-out-cluster`：如果你的 Helm V2 是 tiller 在集群外面 (tillerless) 的安装方式，请带上这个参数

### 迁移 helm v2 数据

查看 helm v2 的 release

```bash
$ helm ls

NAME     REVISION    UPDATED                     STATUS      CHART          APP VERSION    NAMESPACE
redis    1           Mon Sep 16 19:46:58 2020    DEPLOYED    redis-9.1.3    5.0.5          default
```

使用 `--dry-run` 预演效果

```bash
$ helm3 2to3 convert redis --dry-run

NOTE: This is in dry-run mode, the following actions will not be executed.
Run without --dry-run to take the actions described below:

Release "redis" will be converted from Helm 2 to Helm 3.
[Helm 3] Release "redis" will be created.
[Helm 3] ReleaseVersion "redis.v1" will be created.
```

没有报错，去掉 `--dry-run` 开始迁移

```bash
$ helm3 2to3 convert redis

Release "redis" will be converted from Helm 2 to Helm 3.
[Helm 3] Release "redis" will be created.
[Helm 3] ReleaseVersion "redis.v1" will be created.
[Helm 3] ReleaseVersion "redis.v1" created.
[Helm 3] Release "redis" created.
Release "redis" was converted successfully from Helm 2 to Helm 3. Note: the v2 releases still remain and should be removed to avoid conflicts with the migrated v3 releases.
```

检查迁移结果

```bash
# 查看 helm v2 release
$ helm ls

NAME     REVISION    UPDATED                     STATUS      CHART          APP VERSION    NAMESPACE
redis    1           Mon Sep 16 19:46:58 2020    DEPLOYED    redis-9.1.3    5.0.5          default

# 检查 helm v3 release
$ helm3 list -A

NAME  	NAMESPACE	REVISION	UPDATED       STATUS  	CHART      APP VERSION
redis   default    	1       	2020-06-15 18:19:12.409578018 +0800 CST	deployed	redis-9.1.3	1
```

> helm v3 release 区分命名空间，需要带上 `-A` 参数，显示所有命名空间


## 更新 helm charts

### 通过 `lint` 检查 chart 语法

`helm v2 chart` 声明：

```
  {{- if .Values.route.tls }}
  tls:
  {{ toYaml .Values.route.tls | indent 2 }}
  {{- end -}}
```

在 helm v2 版本中，`lint` 是没有问题的，但是使用 helm v3 版本 `lint` 报：`mapping values are not allowed in this context` 错误

上面 chart 需要调整，下面给出 `helm v3` 正确 chart 模板

```
  {{- if .Values.route.tls }}
  tls:
  {{ toYaml .Values.route.tls | indent 2 }}
  {{- end }}
```

> 参考链接：https://github.com/helm/helm/issues/6251

### Chart v3 变动

- 需要把 `requirements.yaml` 文件配置合并到 `Chart.yaml` 配置中
- 需要把 `Chart.yaml` 配置中 `apiVersion:` v1 修改成 v2

## 清理 Helm V2 Release

使用 `--dry-run` 参数，helm v2 清理预演，不会清理 Release 数据

```bash
$ helm3 2to3 cleanup --dry-run

2019/11/14 15:06:59 NOTE: This is in dry-run mode, the following actions will not be executed.
2019/11/14 15:06:59 Run without --dry-run to take the actions described below:
2019/11/14 15:06:59
WARNING: "Helm v2 Configuration" "Release Data" "Release Data" will be removed.
This will clean up all releases managed by Helm v2. It will not be possible to restore them if you haven't made a backup of the releases.
Helm v2 may not be usable afterwards.

[Cleanup/confirm] Are you sure you want to cleanup Helm v2 data? [y/N]: y
2019/11/14 15:07:01
Helm v2 data will be cleaned up.
2019/11/14 15:07:01 [Helm 2] Releases will be deleted.
2019/11/14 15:07:01 [Helm 2] ReleaseVersion "postgres.v1" will be deleted.
2019/11/14 15:07:01 [Helm 2] ReleaseVersion "redis.v1" will be deleted.
2019/11/14 15:07:01 [Helm 2] Home folder "/Users/rimasm/.helm" will be deleted.
```

如果上面命令执行完没有问题，这次清理 V2 Release 数据

```bash
$ helm3 2to3 cleanup
```

执行完后，`Tiller` Pod 会被删除，并且 `kube-system` 命名空间中 `configmaps` 历史版本信息也会被清理。

## 参考链接

- https://helm.sh/blog/migrate-from-helm-v2-to-helm-v3/