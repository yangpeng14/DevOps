> - 作者：haohao
> - 链接：https://qhh.me/2019/09/07/%E5%9F%BA%E4%BA%8E-Kubernetes-%E7%9A%84-7-%E5%A4%A7-DevOps-%E5%85%B3%E9%94%AE%E5%AE%9E%E8%B7%B5/

## 前言

本文主要介绍 DevOps 的 7 大关键实践在 Kubernetes 平台下如何落地，结合我们目前基于 Kubernetes 平台的 DevOps 实践谈谈是如何贯彻相关理念的，这里不会对其具体实现细节进行深入讲解，只做一个大致的概括的描述，分享下已有的实践，具体实践细节有时间了会单独整理一篇文章分享。

## DevOps 简介

DevOps 集文化理念、实践和工具于一身，可以提高企业高速交付应用程序和服务的能力，与使用传统软件开发和基础设施管理流程相比，能够帮助企业更快地发展和改进产品。

![](/img/devops-1.png)

### Goals

The goals of DevOps span the entire delivery pipeline. They include:

- Improved deployment frequency;
- Faster time to market;
- Lower failure rate of new releases;
- Shortened lead time between fixes;
- Faster mean time to recovery (in the event of a new release crashing or otherwise disabling the current system).

## DevOps 的 7 大关键实践在Kubernetes 平台下的落地

下面为基于 Kubernetes 的 CI/CD 流水线整体实践，使用 Kubernetes + Docker + Jenkins + Helm 等云原生工具链来构建 CI/CD 管道，基于 Google Cloud Platform 云平台构建：

![](/img/k8s-devops-ci-cd.png)


### 1. Configuration Management

关于配置文件的管理我们统一使用 Kubernetes 提供的 configmap 和 secret 资源对象来实现，对于一般的应用配置使用 configmap 管理，对于敏感数据使用 secret 存储。

### 2. Release Management

关于发布管理，使用 Helm 工具统一以 Chart 的方式打包并发布应用，维护每个微服务的历史版本，可以按需回滚。应用的镜像版本统一存储到一个 Docker 私服。

### 3. Continuous Integration

关于持续集成整合了一套完全开源的工具链：Gitlab + Maven + Jenkins + TestNg + SonarQuebe + Allure。Jenkins 运行在 Kubernetes 集群中，所有的工具链都以容器的方式运行，按需定义并使用，无需单独安装维护。

![](/img/k8s-ci-jenkins-pipeline.png)

### 4. Continuous Deployment

关于持续部署方面做的不是很好，没有形成完整的 Pipeline，整个自动化 Pipeline 进行到预发布环境，对于生产环境发布，研发人员自助式点击另一个单独的部署 Pipeline Job 进行部署，选择镜像版本进行发布。

![](/img/k8s-cd-jenkins-pipeline.png)

### 5. Infrastructure as Code

基础架构即代码的指的是所有软件基础设施的管理维护都以代码的方式管理起来，对于基础设施资源的创建、销毁、变更，不再是人工通过界面化点触式管理，所有这些更改都基于代码的提交变更和一套自动化框架。比如知名的 Terraform 就是一个业界比较流行的 IaC 框架，专门用于代码化管理云基础设施。在 Infrastructure as Code 方面，其实 Kubernetes 完全契合这一点，所有的基础架构及应用服务都可以被抽象成 API 资源对象，我们只需要按需定义 yaml 资源文件即可快速生成相应的资源。比如我们需要一个 Redis 中间件，那么只需要编写一个声明式 yaml 文件，定义需要的配置、版本等信息即可以容器的方式在 k8s 集群中运行起来。最终只需要在 git 代码仓库维护这些 yaml 文件即可。

![](/img/k8s-iac.png)

### 6. Test Automation

关于测试自动化，目前主要有三种类型的测试：单元测试、后端接口测试、UI 自动化测试。所有的这些测试都集成在 Jenkins pipeline 中。后端接口测试和 UI 测试除了在自动化 Pipeline 中运行，还会每天定时跑测试，最终的测试报告统一收集到 Reportportal 报表平台。

![](/img/rp_dashboard.png)

### 7. Application Performance Monitoring

关于应用监控采用云原生架构下的最佳实践： Prometheus 监控栈

![](/img/prometheus-arch.png)

关于日志采集基于 EFK 技术栈

![](/img/k8s-efk-arch.png)

## 相关文档

- https://www.wikiwand.com/en/DevOps#/Definitions_and_history