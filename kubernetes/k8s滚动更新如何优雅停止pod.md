## 何谓优雅停止?
`优雅停止(Graceful shutdown)` 这个说法来自于操作系统，我们执行关机之后都得 OS 先完成一些清理操作，而与之相对的就是硬中止(Hard shutdown)，比如拔电源。

到了分布式系统中，优雅停止就不仅仅是单机上进程自己的事了，往往还要与系统中的其它组件打交道。比如说我们起一个微服务，网关把一部分流量分给我们，这时:

- 假如我们一声不吭直接把进程杀了，那这部分流量就无法得到正确处理，部分用户受到影响。不过还好，通常来说网关或者服务注册中心会和我们的服务保持一个心跳，过了心跳超时之后系统会自动摘除我们的服务，问题也就解决了；这是硬中止，虽然我们整个系统写得不错能够自愈，但还是会产生一些抖动甚至错误;

- 假如我们先告诉网关或服务注册中心我们要下线，等对方完成服务摘除操作再中止进程，那不会有任何流量受到影响；这是优雅停止，将单个组件的启停对整个系统影响最小化;

按照惯例，SIGKILL 是硬终止的信号，而 SIGTERM 是通知进程优雅退出的信号，因此很多微服务框架会监听 SIGTERM 信号，收到之后去做反注册等清理操作，实现优雅退出。[4]


## 什么是Pod？

`Pod` 就像是豌豆荚一样，它由一个或者多个容器组成（例如Docker容器），它们共享容器存储、网络和容器运行配置项。Pod中的容器总是被同时调度，有共同的运行环境。你可以把单个Pod想象成是运行独立应用的“逻辑主机”——其中运行着一个或者多个紧密耦合的应用容器——在有容器之前，这些应用都是运行在几个相同的物理机或者虚拟机上。[1]


## 滚动更新会出现的问题
在 k8s 执行 `Rolling-Update` 的时，默认会向旧的 pod 发生一个 `SIGTERM` 信号，如果业务应用没有对 `SIGTERM` 信号做处理的话，有可能导致程序退出后也没有处理完请求，引起客户端访问异常。


## 简述滚动更新步骤

- 启动一个新的 pod
- 等待新的 pod 进入 Ready 状态
- 创建 Endpoint，将新的 pod 纳入负载均衡
- 移除与老 pod 相关的 Endpoint，并且将老 pod 状态设置为 Terminating，此时将不会有新的请求到达老 pod
- 给老 pod 发送 SIGTERM 信号，并且等待 terminationGracePeriodSeconds 这么长的时间。(默认为 30 秒)
- 超过 terminationGracePeriodSeconds 等待时间直接强制 kill 进程并关闭旧的 pod

`注意`：`SIGTERM` 信号如果进程没有处理就会导致进程被强杀，如果处理了但是超过 `terminationGracePeriodSeconds` 配置的时间也一样会被强杀，所以这个时间可以根据具体的情况去设置。 [2]

## 滚动更新图解 [3]

`注`：`绿色Pod` 为当前已运行Pod ， `紫色Pod` 为新创建Pod

- 当前 Service A 把流量分给4个 绿色Pod

	![](/img/rolling-update-1.png)

- 管理员更新完 `Deployment` 部署文件，触发 `Rolling-Update` 操作，根据 k8s 调度算法选出一个 Node ，在这台 Node上创建一个 紫色Pod

	![](/img/rolling-update-2.png)

- 当第一个 紫色Pod 创建完开始服务，k8s 会继续停止一个 绿色Pod，并创建一个 紫色Pod

	![](/img/rolling-update-3.png)

- 循环替换，直到把所有 绿色Pod 替换成 紫色Pod，紫色Pod 达到 Deployment 部署文件中定义的副本数，则滚动更新完成

	![](/img/rolling-update-4.png)


滚动更新允许以下操作：

- 将应用程序从准上线环境升级到生产环境（通过更新容器镜像）
- 回滚到以前的版本
- 持续集成和持续交付应用程序，无需停机

## 解决方法

- 通过容器生命周期 hook 来优雅停止

    Pod 停止前，会执行 `PreStop hook`，hook 可以执行一个 `HTTP GET请求` 或者 `exec命令`，并且它们执行是阻塞的，可以利用这个特性来做优雅停止。

    - 调用 HTTP GET
        ```yaml
		spec:
		  contaienrs:
		  - name: my-container
		    lifecycle:
		      preStop:
		        httpGet:
		          path: "/stop"
		          port: 8080
		          scheme: "HTTP"
        ```

    - 调用 exec
        ```yaml
		spec:
		  contaienrs:
		  - name: my-container
		    lifecycle:
		      preStop:
		        exec:
		          command: ["/bin/sh"，"-c"，"/pre-stop.sh"]
        ```


- 关于 PreStop 和 terminationGracePeriodSeconds

    - 如果有 `PreStop hook` 会执行 `PreStop hook`，`PreStop hook` 执行完成后会向 pod 发送 `SIGTERM` 信号。
    - 如果在 `terminationGracePeriodSeconds` 时间限制内，`PreStop hook` 还没有执行完，一样会直接发送 `SIGTERM` 信号，并且时间延长 `2秒`，最后强制 Kill 。

## 参考链接
- [1] https://jimmysong.io/kubernetes-handbook/concepts/pod.html
- [2] https://monkeywie.github.io/2019/07/11/k8s-graceful-shutdown/
- [3] https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/
- [4] https://aleiwu.com/post/tidb-opeartor-webhook/