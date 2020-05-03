## 前言

创建 Pod 时，可以为其下的容器设置启动时要执行的命令及其参数。如果要设置命令，就填写在配置文件的 `command` 字段下，如果要设置命令的参数，就填写在配置文件的 `args` 字段下。一旦 Pod 创建完成，该命令及其参数就无法再进行更改了。

## 启动优先级

下表给出了 Docker 与 Kubernetes 中对应的字段名称：

描述 | Docker字段名称 | Kubernetes字段名称
---|---|---
容器执行的命令 | Entrypoint | command
传给命令的参数| Cmd | args

如果要覆盖Docker容器默认的 `Entrypoint` 与 `Cmd`，需要遵循如下规则：

- 如果在 Pod 配置中没有设置 `command` 或者 `args`，那么将使用 Docker 镜像自带的命令及其参数。
- 如果在 Pod 配置中只设置了 `command` 但是没有设置 `args`，那么容器启动时只会执行该命令，Docker 镜像中自带的命令及其参数会被忽略。
- 如果在 Pod 配置中只设置了 `args`，那么 Docker 镜像中自带的命令会使用该新参数作为其执行时的参数。
- 如果在 Pod 配置中同时设置了 `command` 与 `args`，那么 Docker 镜像中自带的命令及其参数会被忽略。容器启动时只会执行配置中设置的命令，并使用配置中设置的参数作为命令的参数。

## 例子

### `Pod` 启动例子：

使用 `command` 和 `args` 示例：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo
  labels:
    purpose: demo
spec:
  containers:
  - name: demo-container
    image: debian
    command: ["printenv"]
    args: ["HOSTNAME", "KUBERNETES_PORT"]
  restartPolicy: OnFailure
```

使用`环境变量`来设置参数：

```yaml
env:
- name: MESSAGE
  value: "hello world"
command: ["/bin/echo"]
args: ["$(MESSAGE)"]
```

上面例子使用 `env` 来声明环境变量，但 k8s 中也可以使用 `ConfigMaps` 与 `Secrets` 来做为变量传入。

通过 `shell` 命令来执行：

```yaml
command: ["/bin/bash"]
args: ["-c", "while true; do echo "Hello World"; sleep 10;done"]
```

### Docker 镜像启动例子

`Cmd` 单独使用：

```yaml
FROM ubuntu:trusty
CMD ["echo", "Hello World"] 
```

`Entrypoint` 单独使用：

```yaml
FROM ubuntu:trusty
ENV name John
ENTRYPOINT ["echo", "Hello, $name"]
```

`Entrypoint` 和 `Cmd` 组合使用：

```yaml
FROM ubuntu:trusty
ENTRYPOINT ["/bin/ping", "-c", "10"]
CMD ["localhost"]
```

## 参考链接

- https://kubernetes.io/zh/docs/tasks/inject-data-application/define-command-argument-container/