## Quay 简介
`Quay` 是一个`registry`，`存储`，`构建`和`部署容器`的镜像仓库。它分析您`镜像中的安全漏洞`，可帮助您减轻潜在的`安全风险问题`。此外，它提供`地理复制`和`BitTorrent分发`，以提高`分布式开发站点之间的性能`，并提高`灾难恢复的弹性`和`冗余性`。

## Quay 现状
- `Quay` 可以配合红帽`OpenShift`企业版使用，提供一个企业级镜像仓库功能。

- 一个好消息，`上月中旬`红帽推出了 `Quay` 项目的开源项目，该项目是代表 `Red Hat Quay` 和 `Quay.io` 的代码的`上游项目`。根据 `Red Hat` 的开源承诺，`Project Quay` 是新开源的，代表了自 2013 年以来 CoreOS（现在是 Red Hat）围绕 Quay 容器注册表进行的多年工作的高潮。

## 使用 Red Hat Quay，您可以

- 提高镜像安全性。`Red Hat Quay` 提供可靠强大的`访问控制`。

- `轻松构建`和`部署新容器`。`Red Hat Quay`通过与 `GitHub`，`Bitbucket`等集成实现容器构建的`自动化`。机器人帐户允许自动部署软件。
![](https://www.yp14.cn/img/Quay-commit.png)

- 扫描容器以提供安全性。`Red Hat Quay`会`扫描`您的`容器中的漏洞`，从而使您可以`了解已知问题`以及`如何解决它们`。
![](https://www.yp14.cn/img/quay_main.jpg)

## 基于 RedHat 企业数据中心的 Quay 提供如下功能：

- `时间机器`：`Red Hat Quay`提供了存储库中`所有标签`的`两周可配置历史记录`，并能够通过`图像回滚`将标签还原到以前的状态。

- `地域复制`：连续的`地理分布`可提高性能，确保您的内容始终在最需要的地方可用。

- `安全漏洞检测集成`：`Red Hat Quay` `漏洞检测器`（例如Clair）集成在一起，并扫描您的容器镜像识别已知漏洞。

- `垃圾回收`：自动连续的镜像垃圾回收有效地将资源用于活动对象，并降低成本，而无需计划内`停机`或`只读模式`。

- `存储`：支持多个存储后端来存储您的容器。

- `自动化的容器构建`：`Red Hat Quay`允许您使用构建触发器来简化您的`持续集成`/ `持续交付`（CI / CD）流程。

- `审核日志记录`：`Red Hat Quay``跟踪控制`和`数据平面事件`日志记录，以及`应用程序编程接口（API`）和`用户界面（UI）操作`。

- `高可用性`：可以运行`Red Hat Quay`的`多个实例`以实现`冗余`，提高高可用性，可以防止单点故障。

- `企业授权和认证`：使用`Red Hat Quay`，您可以集成现有的`身份基础结构`，包括轻型目录访问协议（LDAP），开放式授权（OAuth）和 开放式ID连接（OIDC）和 Keystone，并使用细粒度的权限系统映射到您的组织并授予整个团队访问权限以管理特定的存储库。

- `指标`：内置的`Prometheus`指标导出可在`每个实例上`启用`临时`和`批处理作业`指标，以便于`监视`和`警报`。

- `持续集成`：当开发人员提交代码时，`Red Hat Quay`允许您`自动构建`和`推送镜像`。您可以`构建容器`以响应来自GitHub（托管和企业），Bitbucket，GitLab（托管和企业）等的`git push`。

- `机器人帐户`：这些帐户创建凭据以自动部署软件。

- `洪流分布`：`Red Hat Quay`支持使用`BitTorrent`提取容器镜像。其结果是减少了`下载`和`部署时间`，并通过让多台计算机提供`二进制数据`来提高了`稳定性`。

- `支持多种架构清单`：客户可以在`多种体系结构`上`运行容器`，例如 IBM Power LE和 z System，基于ARM的IoT设备 或 基于Windows的工作负载。
![](https://www.yp14.cn/img/quay-features1.png)

## Quay 开源项目地址
- https://github.com/quay/quay

## Quay 开源项目提供如下功能
- Docker Registry Protocol v2

- Docker清单架构v2.1，v2.2

- 通过按需转码的 `AppC 镜像发现`

- 通过按需转码进行镜像压缩

- LDAP，Keystone，OIDC，Google和GitHub提供的身份验证

- ACL，团队管理和审核日志

- 本地文件系统S3，GCS，Swift和Ceph提供的地理复制存储

- 与GitHub，Bitbucket，GitLab和git集成的持续集成

- 通过`Clair`进行`安全漏洞分析`

- 兼容`Swagger`的`HTTP API`

## 总结
`Quay` 是一个类型于开源 `Harbor` 镜像管理服务，目前提供的功能比`Harbor`强大，现在`Quay`已经开源，大家可以去尝试体验下。

`云上体验`：

- `quay.io` https://quay.io/plans/
- `RedHat` https://www.openshift.com/products/quay

## 参考链接
- https://www.redhat.com/zh/resources/quay-datasheet
- https://github.com/quay/quay
- https://www.ithome.com.tw/review/129692
- https://mp.weixin.qq.com/s/Ul61I9vdCe2dv6-cJhYjNA