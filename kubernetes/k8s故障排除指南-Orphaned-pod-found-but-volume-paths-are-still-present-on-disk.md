## 问题产生

在使用 Kubernetes 时，有时会遇到 Pod 状态一直处理 `Terminating`。Pod 一直没有正常退出，一般情况会使用命令 `kubectl delete pods pod-name --force --grace-period=0` 强制删除。

如果按照上面命令强制删除Pod，有一定概率会报 `Orphaned pod found - but volume paths are still present on disk` 错误。

## 问题排查

上面错误信息可以通过 `journalctl -u kubelet -f` 或者 `tail -f /var/log/messages` 命令查看到。

发现一直在报以下报错，从错误信息可以推测出，这台节点存在一个孤立的Pod，并且该Pod挂载了数据卷(volume)，阻碍了Kubelet对孤立的Pod正常回收清理。

![](/img/k8s-error-1.png)

kubelet 默认把一些数据信息存放在 `/var/lib/kubelet` 目录下，通过 `Pod Id`，能查找到 `9e6d9bdd-1554-45e6-8831-53e83f8ea263` pod 挂载的数据。

```bash
# 查看 pods 下面数据
$ ls /var/lib/kubelet/pods/9e6d9bdd-1554-45e6-8831-53e83f8ea263/

containers  etc-hosts  plugins  volumes
```

## 问题解决方法

把错误信息通过谷歌搜索，发现 kubernetes 项目中有一个 `issues` 提到这个问题。

Issue 链接：https://github.com/kubernetes/kubernetes/issues/60987

通过查看 `etc-hosts` 文件的 `pod name` 名称，查看集群中是否还有相关实例在运行，如果没有直接删除 `9e6d9bdd-1554-45e6-8831-53e83f8ea263` 目录。

> 注意：直接删除 pod 挂载目录有一定的 `危险性`，需要确认是否能删除，如果确认没有问题可以直接删除。

```bash
# 查看 etc-hosts 文件中 pod name 名称
$ cat /var/lib/kubelet/pods/9e6d9bdd-1554-45e6-8831-53e83f8ea263/etc-hosts

# 删除 9e6d9bdd-1554-45e6-8831-53e83f8ea263 目录
$ cd /var/lib/kubelet/pods/
$ rm -rf 9e6d9bdd-1554-45e6-8831-53e83f8ea263
```

现在在通过 `journalctl -u kubelet -f` 命令看kubelet日志，就没有 `Orphaned pod found - but volume paths are still present on disk` 报错了。

如果 pod 挂载目录不能删除，请参考上面 `Issue 链接` 查找更好的解决方法。