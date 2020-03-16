## 什么是 KubeVirt ？

`Kubevirt` 是Redhat开源的以容器方式运行虚拟机的项目，以k8s add-on方式，利用k8s CRD为增加资源类型VirtualMachineInstance（VMI）， 使用容器的image registry去创建虚拟机并提供VM生命周期管理。 CRD的方式是的kubevirt对虚拟机的管理不局限于pod管理接口，但是也无法使用pod的RS DS Deployment等管理能力，也意味着 kubevirt如果想要利用pod管理能力，要自主去实现，目前kubevirt实现了类似RS的功能。 kubevirt目前支持的runtime是docker和runv。

## 为什么使用 KubeVirt ？

KubeVirt 技术可满足已采用或想要采用Kubernetes开发团队的需求，但他们拥有现有的基于虚拟机的工作负载，无法轻松地对其进行容器化。更具体地说，该技术提供了一个统一的开发平台，开发人员可以在该平台上构建，修改和部署驻留在公共共享环境中的应用程序容器和虚拟机中的应用程序。

好处是广泛而重大的。依赖现有基于虚拟机的工作负载团队有权快速将应用程序容器化。通过将虚拟化工作负载直接放置在开发工作流中，团队可以随时间分解它们，同时仍然可以按需使用剩余的虚拟化组件。

## KubeVirt 能做什么 ？

- 利用 KubeVirt 和 Kubernetes 来管理虚拟机
- 一个平台上将现有的虚拟化与容器化打通并管理
- 支持虚拟机应用与容器化应用实现内部交互访问

## KubeVirt 架构

从kubevirt架构看如何创建虚拟机，Kubevirt架构如图所示，由4部分组件组成。从架构图看出kubevirt创建虚拟机的核心就是 创建了一个特殊的pod `virt-launcher` 其中的子进程包括`libvirt`和`qemu`。做过openstack nova项目的朋友应该比较 习惯于一台宿主机中运行一个`libvirtd`后台进程，`kubevirt`中采用每个pod中一个`libvirt`进程是去中心化的模式避免因为 `libvirtd` 服务异常导致所有的虚拟机无法管理。

![](/img/architecture.png)

## 虚拟机创建流程
- client 发送创建VMI命令达到k8s API server.
- K8S API 创建VMI
- virt-controller监听到VMI创建时，根据VMI spec生成pod spec文件，创建pods
- k8s调度创建pods
- virt-controller监听到pods创建后，根据pods的调度node，更新VMI 的nodeName
- virt-handler监听到VMI nodeName与自身节点匹配后，与pod内的virt-launcher通信，virt-laucher创建虚拟机，并负责虚拟机生命周期管理

## 项目地址与快速使用

- 项目地址 https://github.com/kubevirt/kubevirt
- 快速使用 https://kubevirt.io//quickstart_minikube/

## 参考链接

- https://kubevirt.io/
- https://remimin.github.io/2018/09/14/kubevirt/