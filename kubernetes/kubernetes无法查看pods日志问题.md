## 前言

最近使用二进制部署完 `Kubernetes 1.18.2` 版本，运行命令 `kubectl logs -n kube-system calico-node-mbjnm` 时，报下面错误。

![](/img/kubernetes-1.png)

`原因`：我们知道 Kubernetes 认证过程分为：`认证` --> `授权` --> `准入控制`，上面报错就是因为没有通过认证而被拒绝。

## 认证被拒绝解决方法

### 错误的解决方法

通过谷歌搜索时，发现很多博客文章使用下面方法来解决上面报错。修改 `kubelet.config` 配置，添加下面配置，开启匿名访问。问题虽然可以解决，但危害整个集群安全。所以作者不推荐这样操作。

```yaml
authentication:
  anonymous:
    enabled: true
```

### 正确的解决方法

![](/img/kubernetes-1-1.png)

从上图官方文档中我们能得出结论：

- `kube-apiserver` 配置需要添加 `--kubelet-client-certificate` 和 `--kubelet-client-key` 参数，具体配置如下：

    ![](/img/kubernetes-1-3.png)

- `kubelet` 配置需要添加 `--client-ca-file` 参数，并且为了集群安全，需要禁用匿名访问 `--anonymous-auth=false`，具体配置如下：

    ![](/img/kubernetes-1-2.png)


修改完 `kube-apiserver` 和 `kubelet` 配置，并重启 kube-apiserver 和 kubelet 服务，再次运行 `kubectl logs -n kube-system calico-node-mbjnm` 命令查看 Pod 日志，发现又报错了。具体见下图：

![](/img/kubernetes-2.png)

`分析`：从上图我们可以知道，Kubernetes 认证已经通过，但到授权时出现问题，因为没有查看 Pods 日志权限。

> 参考官方链接：https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet-authentication-authorization/

## 没有授权解决方法

### 错误的解决方法

将 `system:anonymous` 绑定到 `cluster-admin` 角色中并起一个 `cluster-system:anonymous` 名字。

```bash
$ kubectl create clusterrolebinding cluster-system:anonymous --clusterrole=cluster-admin --user=system:anonymous

clusterrolebinding.rbac.authorization.k8s.io/cluster-system:anonymous created
```

上面的解决方法，会严重危害集群安全，匿名访问拥有超级管理员权限，想想有多可怕。。。

### 正确的解决方法

> 注意：作者生成证书时使用 `kubernetes 用户`。

![](/img/kubernetes-2-1.png)

`解决思路`：从报错可以知道，`kubernetes 用户` 没有查看 Pods 日志权限，我们可以给 `kubernetes 用户` 绑定一个权限。

Kubernetes 集群默认提供一个 `system:kubelet-api-admin` 权限。

![](/img/kubernetes-2-2.png)

`解决方法`：把 `kubernetes 用户` 绑定到 `system:kubelet-api-admin` 权限。具体如下操作：

```bash
$ vim apiserver-to-kubelet-rbac.yml
```

```yaml
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: kubelet-api-admin
subjects:
- kind: User
  name: kubernetes
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: system:kubelet-api-admin
  apiGroup: rbac.authorization.k8s.io
```

```bash
$ kubectl apply -f apiserver-to-kubelet-rbac.yml
```

再次查看 Pod 日志，能正常输出日志了。

![](/img/kubernetes-2-3.png)