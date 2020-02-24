## Kaniko 简介

`Kaniko` 是 Google 造的轮子之一，用于在 Kubernetes 上无需`特权模式`构建 `docker image`。

`Kaniko` 不依赖`Docker daemon`守护程序，而是完全在`userspace`中执行`Dockerfile`中的每个命令。这使您可以在`没有特权模式`或没有运行`Docker daemon`的环境（例如：Kubernetes集群）中构建容器镜像。

## Kaniko 工作原理

传统的 Docker build 是 Docker daemon 根据 Dockerfile，使用特权用户（root）在宿主机依次执行，并生成镜像的每一层。

而 `Kaniko` 工作原理和此类似，`Kaniko` 执行器获取并展开基础镜像（在Dockerfile中FROM一行定义），按顺序执行每条命令，每条命令执行完毕后为文件系统做快照。快照是在用户空间创建，并与内存中存在的上一个状态进行对比，任何改变都会作为对基础镜像的修改，并以新层级对文件系统进行增加扩充，并将任何修改都写入镜像的元数据中。当Dockerfile中每条命令都执行完毕后，执行器将新生成的镜像推送到镜像仓库中。

`Kaniko` 解压文件系统，执行命令，在执行器镜像的用户空间中对文件系统做快照，这都是为什么Kaniko不需要特权访问的原因，以上操作中没有引入任何 Docker daemon 进程或者 CLI 操作。

![](/img/Kaniko-1.png)

## 在 Kubernetes 中使用

`前提条件`：

- 需要一个运行的 kubernetes 集群
- 需要创建一个 `Kubernetes secret`，其中包含推送到镜像仓库所需的身份验证信息

解决目标 `registry` 认证问题，官方文档中的样例是通过添加一个 `kaniko-secret.json` 并把内容赋值给 `GOOGLE_APPLICATION_CREDENTIALS` 这个环境变量，如果是自建 `registry` 可以直接使用 `docker config`。

```bash
$ echo "{\"auths\":{\"registry.example.com\":{\"username\":\"username\",\"password\":\"password\"}}}" > config.json

$ kubectl create configmap docker-config --from-file=config.json

configmap/docker-config created
```

使用 Pod 构建

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: kaniko
spec:
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:latest
    args: ["--dockerfile=<path to Dockerfile within the build context>",
            "--context=s3://<bucket name>/<path to .tar.gz>",
            "--destination=<aws_account_id.dkr.ecr.region.amazonaws.com/my-repository:my-tag>"]
    volumeMounts:
      - name: docker-config
        mountPath: /kaniko/.docker/
      # when not using instance role
      - name: aws-secret
        mountPath: /root/.aws/
  restartPolicy: Never
  volumes:
    - name: docker-config
      configMap:
        name: docker-config
    # when not using instance role
    - name: aws-secret
      secret:
        secretName: aws-secret
```

## Kaniko 一些构建参数

构建参数 | 解释
---|---
--build-arg | 构建时传递ARG值，可以多次传递
--cache | 设置缓存，`true` 开启缓存
--cache-repo | 指定用来缓存的远程仓库
--cache-dir | 定义缓存的目录
--skip-tls-verify | 仓库地址是http时使用，不推荐生产使用
--cleanup | 设置此标志可在构建结束时清理文件系统
--registry-mirror | 设置镜像仓库，默认`index.docker.io`


## 参考链接

- https://github.com/GoogleContainerTools/kaniko
- https://blog.csdn.net/M2l0ZgSsVc7r69eFdTj/article/details/80014492
- https://blog.ihypo.net/15487483292659.html
