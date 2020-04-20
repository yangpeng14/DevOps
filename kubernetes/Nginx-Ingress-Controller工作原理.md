> 原文链接：https://kubernetes.github.io/ingress-nginx/how-it-works/

## 前言

本文目的是阐述 `Nginx Ingress` 控制器的`工作原理`，尤其是 `NGINX模型` 的构建方式以及为什么需要这个模型。

![](/img/ingress-controller.png)

## Nginx 配置

Nginx Ingress 控制器的目标是构建（nginx.conf）配置文件。主要含义是在配置文件中进行任何更改后都需要重新加载 Nginx。不过需要特别注意的是，在只有 `upstream` 配置变更的时候我们不需要重新加载 Nginx（即当你部署的应用 Endpoints 变更时）。我们使用 [lua-nginx-module](https://github.com/openresty/lua-nginx-module) 实现这一目标。请查看下面的内容，以了解有关操作方法的更多信息。

## Nginx 模型

通常，Kubernetes 控制器利用[同步循环模式](https://coreos.com/kubernetes/docs/latest/replication-controller.html#the-reconciliation-loop-in-detail)来检查控制器中所需的状态是否已更新或需要更改。为此，我们需要使用集群中放入不同对象来构建模型，特别是 Ingresses、Services、Endpoints、Secrets 以及 Configmaps 来生成反映集群状态时间点的配置文件。

为了从集群中获取该对象，我们使用了[Kubernetes Informers](https://godoc.org/k8s.io/client-go/informers#NewFilteredSharedInformerFactory)，尤其是 `FilteredSharedInformer`。当一个新的对象添加、修改或者删除的时候，informers 允许通过 [回调](https://godoc.org/k8s.io/client-go/tools/cache#ResourceEventHandlerFuncs) 针对单个变更进行响应。不幸的是，没有办法知道特定的更改是否会影响最终的配置文件。因此，每次更改时，我们都必须根据集群的状态从头开始重建一个新模型，并将其与当前模型进行比较。如果新模型等于当前模型，那么我们避免生成新的Nginx配置并触发重新加载。否则，我们就通过 Endpoints 来检查不同，然后使用 HTTP POST 请求一个新的 Endpoints 列表发送给运行在 Nginx 中的 Lua 程序并且避免重新生成一个新的 NGINX 配置以及触发重新加载。如果运行的模型和当前的差异不仅仅是 Endpoints，我们则基于新的模型创建一个新的 NGINX 配置文件，替代当前的模型并触发一次重新加载。

该模型的用途之一是在状态没有变化时避免不必要的重新加载，并检测定义中的冲突。

Nginx 配置的最终表示是从 [Go template](https://github.com/kubernetes/ingress-nginx/blob/master/rootfs/etc/nginx/template/nginx.tmpl) 生成的，使用新模型作为模板所需变量的输入。

## 构建 Nginx 模型

建立模型是一项昂贵的操作，因此，必须使用同步循环。通过使用[工作队列](https://github.com/kubernetes/ingress-nginx/blob/master/internal/task/queue.go#L38)，可以不丢失变更并通过 [sync.Mutex](https://golang.org/pkg/sync/#Mutex) 移除来强制执行一次同步循环，此外，还可以在同步循环的开始和结束之间创建一个时间窗口，从而允许我们丢弃不必要的更新。重要的是要理解，集群中的任何变更都会生成事件，然后 informer 会发送给控制器，这也是使用 工作队列 的原因之一。

建立模型的操作方式：

- 按 `CreationTimestamp` 字段对 Ingress 规则排序，即先创建的规则优先。
- 如果在多个 Ingress 中为同一主机定义了相同路径，则先创建的规则优先。
- 如果多个 Ingress 包含同一 host 的 TLS 部分，则先创建的规则优先。
- 如果多个 Ingress 定义了一个 annotation 影响到 Server 块配置，则先创建的规则优先。
- 创建一个 NGINX Servers 列表（按主机名）。
- 创建一个 NGINX Upstreams 列表。
- 如果多个 Ingres Servers 定义了同一个 host 的不同路径，则 Ingress 控制器将合并这些规则。
- Annotations 被应用于这个 Ingress 的所有路径。
- 多个 Ingress 可以定义不同的 Annotations。这些定义在 Ingress 之间不共享。

## 重新加载

下面的列表描述了需要重新加载的情况：

- 已创建新的 Ingress 资源。
- TLS 部分已添加到现有 Ingress。
- Ingress annotations 的更改不仅仅影响 upstream 配置。例如，load-balance annotation 不需要重新加载。
- 已从 Ingress 添加/删除路径。
- 一个 Ingress、Service、Secret 被移除。
- 一些 Ingress 缺少可用的引用对象时，例如 Service 或 Secret。
- Secret 已更新。

## 避免重新加载

在某些情况下，有可能避免重新加载，尤其是在 endpoints 发生变化（即，Pod 启动 或 被替换）时。完全删除重新加载超出了Ingress 控制器的范围。这将需要大量工作，并且在某些时候没有任何意义。仅当 Nginx 更改了读取新配置的方式时，这时才可以更改，基本上，新的更改不会替代工作进程。

### 避免 Endpoints 变更时重新加载

在每个 endpoint 更改上，控制器从所有能看到的服务上获取 endpoints 并生成相应的后端对象。然后，将这些对象发送到在 Nginx 内部运行的 Lua 处理程序。Lua 代码又将这些后端存储在共享内存区域中。然后，对于在 balancer_by_lua 上下文中运行的每个请求，Lua代码将检测它应从哪些 endpoints 中选择对应 upstream 并应用已经配置的负载均衡算法。然后 Nginx 负责其余的工作。这样，我们避免在 endpoints 更改时重新加载 Nginx。请注意，这也包括仅影响 Nginx upstream 配置的 annoations 变更。

在具有频繁部署应用程序的相对较大的群集中，此功能可以节省大量 Nginx 重载，否则会影响响应延迟，负载平衡质量（每次重载Nginx 都会重置负载平衡状态）等等。

### 避免因错误的配置而中断

因为 ingress nginx  使用[同步循环模式工作](https://coreos.com/kubernetes/docs/latest/replication-controller.html#the-reconciliation-loop-in-detail)，所以它将配置应用于所有匹配的对象。如果某些Ingress 对象的配置损坏，例如 nginx.ingress.kubernetes.io/configuration-snippet annotation 中的语法错误，则生成的配置将变得无效，不会重新加载，因此将不再考虑其他 Ingress。

为了防止这种情况的发生，nginx ingress 控制器可以选择公开一个验证的 [准入Webhook服务器](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#validatingadmissionwebhook)，以确保传入的ingress对象的可靠性。此 Webhook 将传入的 ingress 对象追加到 ingresses 列表中，生成配置并调用 nginx 以确保配置没有语法错误。