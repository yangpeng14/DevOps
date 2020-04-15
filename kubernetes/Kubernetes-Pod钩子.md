> - 作者：jasonminghao
> - 链接：https://www.cnblogs.com/jasonminghao/p/12681352.html?utm_source=tuicool&utm_medium=referral

## 目录导航

- 1、Pod容器钩子最终目的
- 2、何为Pod容器钩子
- 3、基于PostStart演示
- 4、基于PreStop演示
- 5、优雅停止Java应用

## 1、Pod容器钩子最终目的

之前在生产环境中使用`dubbo框架`，由于服务更新的过程中，容器直接被停止了，部分请求仍会被分发到终止的容器，导致有用户会访问服务出现`500错误`，这部分错误请求数据占用的比较少，因为Pod是滚动一对一更新。由于这个问题出现了，考虑使用优雅的终止方式，将错误请求将至到最低，直至滚动更新完全不会影响到用户。

### 简单分析一下 `优雅的停止Pod`

微服务中，网关会把流量分配给每个Pod节点，如：我们线上更新Pod的时候

1、如果我们直接把Pod给杀死，那这部分流量就无法得到正确的处理，会影响到部分用户访问，一般来说网关或者注册中心会将我们的服务保持一个心跳，过了心跳超时后就会自动摘除我们的服务，但是有一个问题就是超时时间可能是10s、30s、甚至是60s，虽然不会大规模的影响我们业务系统，但是一定会对用户产生轻微的抖动。

2、如果我们在停止服务前执行一条命令，通知网关或注册中心摘掉这台Pod，即服务进行下线，那么注册中心就会标记这个Pod服务已经下线，不进行流量转发，用户也就不会有任何的影响，这就是优雅停止，将滚动更新的影响最小化。

## 2、何为Pod容器钩子

Kubernetes 最小调度单位为 `Pod`，它为Pod中的容器提供了生命周期钩子，钩子能够使得容器感知其生命周期内的所有事件，并且当相应的生命周期的钩子被调用时运行执行的代码，而Pod 钩子是由Kubelet发起的。

容器钩子两类触发点：

- `PostStart`：容器创建后
- `PreStop`：容器终止前

### PostStart

这个钩子在容器创建后立即执行。但是，并不能保证钩子将在容器 `ENTRYPOINT` 之前运行。没有参数传递给处理程序。

容器 `ENTRYPOINT` 和 `钩子` 执行是`异步操作`。如果钩子花费太长时间以至于容器不能运行或者挂起，容器将不能达到running状态。

### PreStop

这个钩子在容器终止之前立即被调用。它是`阻塞的`，意味着它是同步的，所以它必须在删除容器调用发出之前完成。

如果钩子在执行期间挂起，Pod阶段将停留在running状态并且永不会达到failed状态。

如果 `PostStart` 或者 `PreStop` 钩子失败，容器将会被 `kill`。

用户应该使它们的钩子处理程序尽可能的`轻量`。

## 3、基于PostStart演示

如果 `PostStart` 或者 `PreStop` 钩子失败，它会杀死容器。所以我们应该让钩子函数尽可能的轻量。当然有些情况下，长时间运行命令是合理的，比如在停止容器之前预先保留状态。

1、我们echo一段话追加到/tmp/message，在Pod启动前操作

```bash
$ cat >>hook_test.yaml<<EOF
apiVersion: v1
kind: Pod
metadata:
  name: hook-demo1
spec:
  containers:
  - name: hook-demo1
    image: nginx
    lifecycle:
      postStart:
        exec:
          command: ["/bin/sh", "-c", "echo 1 > /tmp/message"]
EOF
```

2、应用 hook_test.yaml

```bash
$ kubectl apply -f  hook_test.yaml
```

3、可以通过下面查看结果

```bash
$ kubectl get pods | grep hook-demo1

hook-demo1                 1/1     Running   0          49s

$ kubectl exec -it hook-demo1 /bin/bash
root@hook-demo1:/# cat /tmp/message

1
```

## 4、基于PreStop演示

下面示例中，定义一个Nginx Pod，设置了PreStop钩子函数，即在容器退出之前，优雅的关闭Nginx。

```bash
$ cat >>hook_test.yaml<<EOF
apiVersion: v1
kind: Pod
metadata:
  name: hook-demo2
spec:
  containers:
  - name: hook-demo2
    image: nginx
    lifecycle:
      preStop:
        exec:
          command: ["/usr/sbin/nginx","-s","quit"]
EOF
```

## 5、优雅停止Java应用

我们都知道java应用的启动和停止都需要时间，为了更加优雅的停止，可以通过 `pidof` 获取到java进程ID，循环通过kill命令往PID发送 `SIGTERM` 信号。

```yaml
    lifecycle:
      preStop:
        exec:
          command: ["/bin/bash","-c","PID=`pidof java` && kill -SIGTERM $PID && while ps -p $PID > /dev/null;do sleep 1; done;"]
```