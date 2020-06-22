## 问题

大家在使用 Kubernetes 时，会遇到创建Pod失败，这时会分析什么原因导致创建Pod失败？

## Pod status 状态解释 [1]

- `CrashLoopBackOff`：容器退出，kubelet正在将它重启
- `InvalidImageName`：无法解析镜像名称
- `ImageInspectError`：无法校验镜像
- `ErrImageNeverPull`：策略禁止拉取镜像
- `ImagePullBackOff`：镜像正在重试拉取
- `RegistryUnavailable`：连接不到镜像中心
- `ErrImagePull`：通用的拉取镜像出错
- `CreateContainerConfigError`：不能创建kubelet使用的容器配置
- `CreateContainerError`： 创建容器失败
- `m.internalLifecycle.PreStartContainer`：执行hook报错
- `RunContainerError`：启动容器失败
- `PostStartHookError`：执行hook报错 
- `ContainersNotInitialized`：容器没有初始化完毕
- `ContainersNotReady`：容器没有准备完毕 
- `ContainerCreating`：容器创建中
- `PodInitializing`：pod 初始化中 
- `DockerDaemonNotReady`：docker还没有完全启动
- `NetworkPluginNotReady`：网络插件还没有完全启动

## 容器 Exit Code

### 容器退出状态码的区间 [2]

- 必须在 `0-255` 之间
- 0 表示正常退出
- 外界中断将程序退出的时候状态码区间在 `129-255`，(操作系统给程序发送中断信号，比如 `kill -9` 是 `SIGKILL`，`ctrl+c` 是 `SIGINT`)
- 一般程序自身原因导致的异常退出状态区间在 `1-128` (这只是一般约定，程序如果一定要用129-255的状态码也是可以的)

> 注意：有时我们会看到代码中有 exit(-1)，这时会自动做一个转换，最终输出的结果还是会在 `0-255` 之间。

转换公式如下，`code` 表现退出的状态码：

当指定的退出时状态码为`负数`，转换公式如下：

```
256 - (|code| % 256)
```

当指定的退出时状态码为`正数`，转换公式如下：

```
code % 256
```

下面是异常状态码区间表，具体信息可以参考链接 http://tldp.org/LDP/abs/html/exitcodes.html

![](/img/pod-exit-code-2.png)

### 查看 Pod 退出状态码

```bash
$ kubectl describe pods ${pod-name}
```

下面 Pod 退出状态码是为0，说明容器是正常退出的。

![](/img/pod-exit-code-1.png)


### 常见的容器退出状态码解释 [3]

#### Exit Code 0

- 退出代码0表示特定容器没有附加前台进程
- 该退出代码是所有其他后续退出代码的例外
- 这不一定意味着发生了不好的事情。如果开发人员想要在容器完成其工作后自动停止其容器，则使用此退出代码。比如：`kubernetes job` 在执行完任务后正常退出码为 0

#### Exit Code 1

- 程序错误，或者Dockerfile中引用不存在的文件，如 entrypoint中引用了错误的包
- 程序错误可以很简单，例如 “除以0”，也可以很复杂，比如空引用或者其他程序 crash

#### Exit Code 137

- 表明容器收到了 `SIGKILL` 信号，进程被杀掉，对应kill -9
- 引发SIGKILL的是docker kill。这可以由用户或由docker守护程序来发起，手动执行：docker kill
- `137` 比较常见，如果 pod 中的limit 资源设置较小，会运行内存不足导致 `OOMKilled`，此时state 中的 ”OOMKilled” 值为true，你可以在系统的 `dmesg -T` 中看到 oom 日志

#### Exit Code 139

- 表明容器收到了 `SIGSEGV` 信号，无效的内存引用，对应kill -11
- 一般是代码有问题，或者 docker 的基础镜像有问题

#### Exit Code 143

- 表明容器收到了 `SIGTERM` 信号，终端关闭，对应kill -15
- 一般对应 `docker stop` 命令
- 有时docker stop也会导致Exit Code 137。发生在与代码无法处理 `SIGTERM` 的情况下，docker进程等待十秒钟然后发出 `SIGKILL` 强制退出。

#### 不常用的一些 Exit Code

- `Exit Code 126`: 权限问题或命令不可执行
- `Exit Code 127`: Shell脚本中可能出现错字且字符无法识别的情况
- `Exit Code 1 或 255`：因为很多程序员写异常退出时习惯用 exit(1) 或 exit(-1)，-1 会根据转换规则转成 255。这个一般是自定义 code，要看具体逻辑。

## 小结

在排查Pod为什么创建失败时，首先看 Pod 容器退出状态码是非常有用的，能快速的定位问题原因。

## 参考链接

- [1]https://blog.51cto.com/shunzi115/2449411
- [2]https://imroc.io/posts/kubernetes/analysis-exitcode/
- [3]http://www.xuyasong.com/?p=1802