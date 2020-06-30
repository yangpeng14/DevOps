## Arthas 简介

`Arthas` 是Alibaba开源的Java诊断工具，深受开发者喜爱。

`Arthas` 支持 `JDK 6+`，支持 `Linux`、`Mac`、`Windows`，采用命令行交互模式，同时提供丰富的 Tab 自动补全功能，进一步方便进行问题的定位和诊断。

## Arthas 能帮你解决的问题

- 1、这个类从哪个 jar 包加载的？为什么会报各种类相关的 Exception？
- 2、我改的代码为什么没有执行到？难道是我没 commit？分支搞错了？
- 3、遇到问题无法在线上 debug，难道只能通过加日志再重新发布吗？
- 4、线上遇到某个用户的数据处理有问题，但线上同样无法 debug，线下无法重现！
- 5、是否有一个全局视角来查看系统的运行状况？
- 6、有什么办法可以监控到JVM的实时运行状态？
- 7、怎么快速定位应用的热点，生成火焰图？

## Arthas 安装

### 使用 as.sh

Arthas 支持在 Linux/Unix/Mac 等平台上一键安装，请复制以下内容，并粘贴到命令行中，敲 `回车` 执行即可：

```bash
$ curl -L https://alibaba.github.io/arthas/install.sh | sh
```

上述命令会下载启动脚本文件 `as.sh` 到`当前目录`，你可以放在任何地方或将其加入到 `$PATH` 中。

直接在shell下面执行 `./as.sh` ，就会进入交互界面。

也可以执行 `./as.sh -h` 来获取更多参数信息。

### 手动安装

通过 rpm/deb 来安装

在releases页面下载rpm/deb包： https://github.com/alibaba/arthas/releases

```bash
# 安装deb
$ sudo dpkg -i arthas*.deb

# 安装rpm
$ sudo rpm -i arthas*.rpm

# deb/rpm安装的用法，在安装后，可以直接执行
$ as.sh
```

## 启动 Arthas

在命令行下面执行（使用和目标进程一致的用户启动，否则可能attach失败）：

```bash
$ curl -O https://alibaba.github.io/arthas/arthas-boot.jar
$ java -jar arthas-boot.jar
```

- 执行该程序的用户需要和目标进程具有相同的权限。比如以admin用户来执行：`sudo su admin && java -jar arthas-boot.jar` 或 `sudo -u admin -EH java -jar arthas-boot.jar`。
- 如果attach不上目标进程，可以查看 `~/logs/arthas/` 目录下的日志。
- 如果下载速度比较慢，可以使用aliyun的镜像：`java -jar arthas-boot.jar --repo-mirror aliyun --use-http`
- `java -jar arthas-boot.jar -h` 打印更多参数信息。

选择应用java进程：

```bash
$ $ java -jar arthas-boot.jar

* [1]: 35542
  [2]: 71560 arthas-demo.jar
```

Demo进程是第2个，则输入2，再输入 `回车/enter`。Arthas会attach到目标进程上，并输出日志：

```bash
[INFO] Try to attach process 71560
[INFO] Attach process 71560 success.
[INFO] arthas-client connect 127.0.0.1 3658
  ,---.  ,------. ,--------.,--.  ,--.  ,---.   ,---.
 /  O  \ |  .--. ''--.  .--'|  '--'  | /  O  \ '   .-'
|  .-.  ||  '--'.'   |  |   |  .--.  ||  .-.  |`.  `-.
|  | |  ||  |\  \    |  |   |  |  |  ||  | |  |.-'    |
`--' `--'`--' '--'   `--'   `--'  `--'`--' `--'`-----'
 
wiki: https://alibaba.github.io/arthas
version: 3.0.5.20181127201536
pid: 71560
time: 2018-11-28 19:16:24
 
$
```

### Dashboard

```bash
# 在上面基础环境中执行 dashboard 命令
$ dashboard
```

![](/img/arthas-dashboard.png)

## 在线演示

- `基础教程`：https://alibaba.github.io/arthas/arthas-tutorials?language=cn&id=arthas-basics
- `进阶教程`：https://alibaba.github.io/arthas/arthas-tutorials?language=cn&id=arthas-advanced

## 基于 Docker 诊断 Java 进程

### 诊断 Docker 里的 Java 进程

```bash
$ docker exec -it  ${containerId} /bin/bash -c "wget https://alibaba.github.io/arthas/arthas-boot.jar && java -jar arthas-boot.jar"
```

### 诊断 k8s 里容器里的 Java 进程

```bash
$ kubectl exec -it ${pod} --container ${containerId} -- /bin/bash -c "wget https://alibaba.github.io/arthas/arthas-boot.jar && java -jar arthas-boot.jar"
```

### 把 Arthas 打包到基础镜像里

```bash
FROM openjdk:8-jdk-alpine

# copy arthas
COPY --from=hengyunabc/arthas:latest /opt/arthas /opt/arthas
```

如果想`指定版本`，可以查看具体的tags：https://hub.docker.com/r/hengyunabc/arthas/tags

## 总结

`Arthas` 是一个强大的 Java 诊断工具，可以分析 Java 代码bug带来的资源消耗等问题。

Arthas 详细使用方法，公众号后台回复 `Arthas` 获取Arthas详细参数思维导图。

## 参考链接

- `Arthas` 快速入门 https://alibaba.github.io/arthas/quick-start.html
- https://github.com/alibaba/arthas/blob/master/README_CN.md