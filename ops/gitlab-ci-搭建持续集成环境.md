# CI/CD
## 什么是持续集成？
在软件工程里，持续集成（Continuous Integration, CI）是指这样的一种实践：在一天里多次将所有开发人员的代码合并到一个共享的主干里，每次合并都会触发持续集成服务器进行自动构建，这个过程包括了编译、单元测试、集成测试、质量分析等步骤，结果只有两个：成功或者失败。如果得到失败的结果，说明有人提交了不合格的代码，这就能及时发现问题。

## 持续集成的优点
1. 持续自动化测试（持续集成可通过时间间隔触发，或其他方式触发）
2. 跟踪工程健康状况
3. 强制性单元测试用例，验收测试用例等
4. 静态代码检测，生成测试报告

## 什么是持续交付？
持续交付（Continuous delivery）指的是，频繁地将软件的新版本，交付给质量团队或者用户，以供评审。如果评审通过，代码就进入生产阶段。

## 什么是持续部署？
持续部署（Continuous deployment，缩写为CD），是一种软件工程方法，意指在软件开发流程中，以自动化方式，频繁而且持续性的，将软件部署到生产环境（production environment）中，使软件产品能够快速的发展。持续布署可以被整合到持续整合与持续交付的流程之中。

## 图文详解 CI/CD 流程
![](https://www.yp14.cn/img/ci-cd.jpeg)

# GitLab CI

## GitLab CI 简介
GitLab CI 是 GitLab 默认集成的 CI 功能，GitLab CI 通过在项目内 .gitlab-ci.yaml 配置文件读取 CI 任务并进行相应处理；GitLab CI 通过其称为 GitLab Runner 的 Agent 端进行 build 操作；Runner 本身可以使用多种方式安装，比如使用 Docker 镜像启动等；Runner 在进行 build 操作时也可以选择多种 build 环境提供者；比如直接在 Runner 所在宿主机 build、通过新创建虚拟机(vmware、virtualbox)进行 build等；同时 Runner 支持 Docker 作为 build 提供者，即每次 build 新启动容器进行 build。

## GitLab CI/CD 如何工作
使用GitLab CI/CD，您需要的是托管在Git存储库中的应用程序代码库，并且在根路径.gitlab-ci.yml文件中指定构建、测试和部署脚本。在此文件中，您可以定义要运行的脚本，定义包含和缓存依赖项，选择要按顺序运行的命令和要并行运行的命令，定义要在哪里部署应用程序，以及指定是否将要自动运行脚本或手动触发任何脚本。

## 图文详解 GitLab CI 流程
![](https://www.yp14.cn/img/gitlab-ci.jpg)

## CentOS7 部署 GitLab CI
1. 添加GitLab Runner社区版Package

    `curl -s https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm.sh | sudo bash`

2. 安装GitLab Runner社区版

    `sudo yum install gitlab-runner -y`

3. 默认配置文件位置

    `/etc/gitlab-runner/config.toml`

## GitLab CI 注册
`项目主页 -> Sttings -> CI/CD -> Runners Expand`

需要按照步骤输入：

- `gitlab-runner register`
- 输入gitlab的服务URL，这个使用的是https://gitlab.com/
- 输入gitlab-ci的Toekn
- 关于集成服务中对于这个runner的描述
- 给这个gitlab-runner输入一个标记，这个tag非常重要，在后续的使用过程中需要使用这个tag来指定gitlab-runner
- 是否运行在没有tag的build上面。在配置gitlab-ci的时候，会有很多job，每个job可以通过tags属性来选择runner。这里为true表示如果job没有配置tags，也执行
- 是否锁定runner到当前项目
- 选择执行器，gitlab-runner实现了很多执行器，可用在不同场景中运行构建，详情可见`https://docs.gitlab.com/runner/executors/README.html`，这里选用`Shell`模式

## 编写 .gitlab-ci.yaml 文件
```bash
stages:
  - build
  - test
  - deploy

job 0:
  stage: .pre
  script: make something useful before build stage

job 1:
  stage: build
  only: 
    - master
  tags:
    - tag-test
  script: make build dependencies

job 2:
  stage: build
  only: 
    - master
  tags:
    - tag-test
  script: make build artifacts

job 3:
  stage: test
  only: 
    - master
  tags:
    - tag-test
  script: make test

job 4:
  stage: deploy
  only: 
    - master
  tags:
    - tag-test
  script:
    - echo "Deploy ..."
    - make deploy
  when: manual

job 5:
  stage: .post
  script: make something useful at the end of pipeline
```

## .gitlab-ci.yaml 文件参数解释
值 | 描述
---|---
stages | 定义管道中的阶段
build、test、deploy | 作业分为不同的阶段、并且相同的作业stage可以并行执行
job 0 | 用户自定义任务名称 
.pre | 始终是管道的第一阶段
.post | 始终是管道的最后阶段
only | 定义将为其运行作业的分支和标签的名称
except | 定义将不运行作业的分支和标签的名称
tags | 当管道的Git引用是标签时
script | 执行shell命令或者脚本
when | 用于实现在发生故障或发生故障时运行的作业

`when 可以设置为以下值之一：`

值 | 描述
---|---
on_success | 仅当先前阶段中的所有作业都成功（或因为已标记，被视为成功allow_failure）时才执行作业 。这是默认值
on_failure | 仅当至少一个先前阶段的作业失败时才执行作业
always | 执行作业，而不管先前阶段的作业状态如何
manual | 手动执行作业（在GitLab 8.10中已添加）

## 参考文献
https://docs.gitlab.com/ce/ci/yaml/README.html

https://wiki.mbalib.com/wiki/%E6%8C%81%E7%BB%AD%E9%9B%86%E6%88%90

https://zh.wikipedia.org/wiki/%E6%8C%81%E7%BA%8C%E6%95%B4%E5%90%88

https://zh.wikipedia.org/wiki/%E6%8C%81%E7%BA%8C%E9%83%A8%E7%BD%B2

## 关注我
![公众号](https://www.yp14.cn/img/gzh.jpeg)