> - 作者：Happiness
> - 链接：https://blog.k8s.fit/articles/2020/03/16/1584340450004.html

## 背景

假如你的k8s环境中运行的容器较多，单靠可视化插件 `kubernetes-dashboard` 来观察总是有些不尽人意，毕竟kubernetes-dashboard用来做可视化也是捉襟见肘的。加上我最近一直在学习helm的使用方式，（就是想多找几个项目练习一下对helm的使用熟练度）然后在github的海洋中翻来覆去，飘来飘去，找到了 `Weave Scope` 这个项目，觉得很有意思，接下来部署 `Weave Scope`。

## 组件功能解析：

`Weave Scope` 可以监控k8s集群中一系列资源的状态、扩缩容、拓扑图、资源使用率、Describe、exec等众多操作，并且都是在web终端完成的。

`Weave Scope` 提供的功能如下：

- 过滤/搜索功能
- 容器排错功能
- 实时监控功能
- 拓扑界面
- 图形或者表格展示功能

## 组成模式：

Weave Scope 由 `frontend-weave` 和 `cluster-agent-weave` 组成：

- `frontend-weave` 负责处理来自cluster-agent-weave获取的信息，生成可视化拓扑界面
- `cluster-agent-weave` 负责收集容器/宿主机的信息，并传送给frontend-weave(cluster-agent-weave收集的是每台node节点，所以这里是ds控制器)

## helm部署：

```bash
# 添加Weave Scope的repo源
$ helm repo add stable https://kubernetes-charts.storage.googleapis.com

# 将Weave Scope pull到本地进行修改
$ helm pull stable/weave-scope --untar 

# 我这里使用的是ingress进行访问的,因此,当你看到这篇文章的时候要保证你的集群里安装了nginx-ingress-controller或者traefik,如果没有安装可以把Service改为NodePort
# 配置文件下载： http://nextcloud.k8s.fit/s/iD6MXTyZPRiYTnW

# 安装：
$ helm install weave -f values.yaml ./

# 查看是否正常运行
$ kubectl get pod 

NAME                                              READY   STATUS    RESTARTS   AGE
weave-scope-agent-weave-747z4                     1/1     Running   0          61m
weave-scope-agent-weave-jjq59                     1/1     Running   0          61m
weave-scope-agent-weave-nx7sw                     1/1     Running   0          61m
weave-scope-cluster-agent-weave-7db5f4d9d-b8pdg   1/1     Running   0          61m
weave-scope-frontend-weave-566d9cb79b-wv4cn       1/1     Running   0          61m
```

## 使用Weave Scope

配置好本地的hosts文件解析，浏览器打开`http://weave.k8s.fit/`

简单举个使用例子：

- 图表模式：

    ![](/img/4f7d7345-f275-40b4-88a7-c2dcd7895a13.png)

- 表格模式：

    ![](/img/c98b1359-2c46-4e5f-9beb-f231b5c3ca9a.png)

- 日志模式：

    ![](/img/1394b5e8-0d2f-4ba5-87cf-73b87424e700.png)

- Exec shell:

    ![](/img/d835c979-9b69-40e2-9d05-0cb9271a1ef3.png)

- 扩缩容模式：

    ![](/img/76e844e7-5f04-475a-8fc9-004194e89180.png)

## 总结：

对于 Docker 或者 Kubernetes 而言`Weave Scope`是一款非常优秀的可视化工具，在拓扑图中实时显示查看你的应用程序。第一次使用会有摸不着头脑的感觉，多折腾几次就明白Weave Scope的基本操作了。

### 参考链接：

- https://github.com/weaveworks/scope
- https://www.weave.works/docs/