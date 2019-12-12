## 环境
- Kubernetes v1.15.6 源码安装
- Istio v1.2.5 Helm 安装

## Istio v1.2.5 Helm 安装
- https://mp.weixin.qq.com/s/PPTnoyVD2bzeZ6vHRUphzQ

## 问题

安装完后，做官方 `bookinfo` 实验 `kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml` 出现 `sidecar` 自动注入不成功。

## 解决方法

- 第一种可能：

    安装 Istio 时，配置了 enableNamespacesByDefault: false
    ```yaml
    sidecarInjectorWebhook:
      enabled: true
      # 变量为true，就会为所有命名空间开启自动注入功能。如果赋值为false，则只有标签为istio-injection的命名空间才会开启自动注入功能
      enableNamespacesByDefault: false
      rewriteAppHTTPProbe: false
    ```

    `解决方法：`
    ```bash
    # 设置标签
    $ kubectl label namespace default istio-injection=enabled

    # 查看
    $ kubectl get namespace -L istio-injection

    NAME                   STATUS   AGE    ISTIO-INJECTION
    default                Active   374d   enabled
    ```

- 第二种可能：

    安装 Istio 时，设置 autoInject: disabled
    ```yaml
    proxy:
      includeIPRanges: 192.168.16.0/20,192.168.32.0/20
      # 是否开启自动注入功能，取值enabled则该pods只要没有被注解为sidecar.istio.io/inject: "false",就会自动注入。  如果取值为disabled，则需要为pod设置注解sidecar.istio.io/inject: "true"才会进行注入
      autoInject: disabled
    ```

    `解决方法：`
    - 第一个方法：设置 `autoInject: enabled`
    - 第二个方法：在 `Pod` 或者 `Deployment` 声明 `sidecar.istio.io/inject: "true"`

- 第三种可能：

    `kube-apiserver --enable-admission-plugins` 没有配置 `MutatingAdmissionWebhook,ValidatingAdmissionWebhook`

    `解决方法：`
    ```bash
    $ vim kube-apiserver

    --enable-admission-plugins=NamespaceLifecycle,LimitRanger,ServiceAccount,DefaultStorageClass,DefaultTolerationSeconds,MutatingAdmissionWebhook,ValidatingAdmissionWebhook,ResourceQuota,NodeRestriction \
    ```

- 第四种可能：

    如果自动注入时，报如下错误信息：

    `Error creating: Internal error occurred: failed calling webhook "sidecar-injector.istio.io": Post https://istio-sidecar-injector.istio-system.svc:443/inject?timeout=30s: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)`

    `原因：`

    `Master` 节点没安装 `flanneld、docker、kube-proxy`，会导致 `Master` 节点访问不了集群内部的 `Service`(istio-sidecar-injector)，导致自动注入失败。

    `解决方法：`

    `Master` 安装 `flanneld、docker、kube-proxy`，并且针对 Master 节点上的 node 设置 `SchedulingDisabled`

- 第五种可能：

    没有配置 `Aggregation` (一定要安装 `metrics-server` ，收集监控数据。提供 `HPA` 伸缩数据)

    `解决方法：`
    - 第一个方法：在 Master 节点安装 `kube-proxy` 服务（推荐直接把 `master` 节点安装一个 `node`，并设置成不可调度）
    - 第二个方法：`kube-apiserver` 配置中启用 `--enable-aggregator-routing=true` (允许在不修改 Kubernetes 核心代码的同时扩展 Kubernetes API)


## 参考链接
- https://kubernetes.io/docs/tasks/access-kubernetes-api/configure-aggregation-layer/
- https://www.okcode.net/article/62009