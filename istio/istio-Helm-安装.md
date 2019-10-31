### 一、参考官方文档
```
https://istio.io/docs/setup/kubernetes/#downloading-the-release # 安装前准备
https://istio.io/docs/setup/kubernetes/install/helm/  # 参考官方文档 helm 安装
```

### 二、Istio安装前准备

##### 1. Go to the Istio release page to download the installation file corresponding to your OS. On a macOS or Linux system, you can run the following command to download and extract the latest release automatically:
```
$ curl -L https://git.io/getLatestIstio | ISTIO_VERSION=1.2.5 sh -
```

##### 2. Move to the Istio package directory. For example, if the package is istio-1.2.5:
```
$ cd istio-1.2.5

The installation directory contains:

Installation YAML files for Kubernetes in install/kubernetes
Sample applications in samples/
The istioctl client binary in the bin/ directory. istioctl is used when manually injecting Envoy as a sidecar proxy.
```
##### 3. Add the istioctl client to your PATH environment variable, on a macOS or Linux system:
```
$ export PATH=$PWD/bin:$PATH
```

### 三、Helm 安装Istio 1.2.5版本
##### 1. Helm tiller 安装这里不在细说，google一下很多配置方法

##### 2. 安装CRDs
```
$ helm install install/kubernetes/helm/istio-init --name istio-init --namespace istio-system
```

##### 3. Istio Helm Values.yaml配置参数，下面参数只是参考，可以自行调整。本人k8s集群中已安装nginx ingress，所以配置中开启ingress配置，不需要可以不配置
```
Istio 参数选择解释可参考 https://istio.io/docs/reference/config/installation-options/#mixer-options
```

```
global:
  defaultResources:
    requests:
      cpu: 30m
      memory: 50Mi
    limits:
      cpu: 400m
      memory: 600Mi
  proxy:
    includeIPRanges: 192.168.16.0/20,192.168.32.0/20
    # 是否开启自动注入功能，取值enabled则该pods只要没有被注解为sidecar.istio.io/inject: "false",就会自动注入。如果取值为disabled，则需要为pod设置注解sidecar.istio.io/inject: "true"才会进行注入
    autoInject: disabled
    resources:
      requests:
        cpu: 30m
        memory: 50Mi
      limits:
        cpu: 400m
        memory: 500Mi
  mtls:
    enabled: false

sidecarInjectorWebhook:
  enabled: true
  # 变量为true，就会为所有命名空间开启自动注入功能。如果赋值为false，则只有标签为istio-injection的命名空间才会开启自动注入功能
  enableNamespacesByDefault: false
  rewriteAppHTTPProbe: false

mixer:
  nodeSelector:
    label: test
  policy:
    enabled: false
  telemetry:
    enabled: true
    resources:
      requests:
        cpu: 100m
        memory: 300Mi
      limits:
        cpu: 1000m
        memory: 1024Mi

pilot:
  enabled: true
  nodeSelector:
    label: test
  resources:
    requests:
      cpu: 100m
      memory: 300Mi
    limits:
      cpu: 1000m
      memory: 1024Mi

gateways:
  enabled: true
  istio-ingressgateway:
    enabled: true
    type: NodePort
    nodeSelector:
      label: test
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 1000m
        memory: 1024Mi
  istio-egressgateway:
    enabled: false
    type: NodePort
    nodeSelector:
      label: test
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 1000m
        memory: 256Mi

tracing:
  enabled: true
  provider: jaeger
  jaeger:
    resources:
      limits:
        cpu: 300m
        memory: 900Mi
      requests:
        cpu: 30m
        memory: 100Mi
  zipkin:
    resources:
      limits:
        cpu: 300m
        memory: 900Mi
      requests:
        cpu: 30m
        memory: 100Mi
  nodeSelector:
    label: test
  contextPath: /
  ingress:
    enabled: true
    hosts:
      - tracing1.example.com

kiali:
  enabled: true
  resources:
    limits:
      cpu: 300m
      memory: 900Mi
    requests:
      cpu: 30m
      memory: 50Mi
  hub: kiali
  nodeSelector:
    label: test
  contextPath: /
  ingress:
    enabled: true
    hosts:
      - kiali1.example.com
  dashboard:
    grafanaURL: http://grafana1.example.com:8088
    jaegerURL: http://tracing1.example.com:8088

grafana:
  enabled: true
  persist: true
  storageClassName: grafana-data
  accessMode: ReadWriteMany
  resources:
    requests:
      cpu: 30m
      memory: 50Mi
    limits:
      cpu: 300m
      memory: 500Mi
  security:
    enabled: true
    secretName: grafana
    usernameKey: username
    passphraseKey: passphrase
  nodeSelector:
    label: test
  contextPath: /
  ingress:
    enabled: true
    hosts:
      - grafana1.example.com

# 默认开启
prometheus:
  resources:
    requests:
      cpu: 30m
      memory: 50Mi
    limits:
      cpu: 500m
      memory: 1024Mi
  retention: 3d
  nodeSelector:
    label: test
  contextPath: /
  ingress:
    enabled: true
    hosts:
      - prometheus1.example.com

istio_cni:
  enabled: false
```

##### 4. Helm 安装 Istio
```
$ helm install ./install/kubernetes/helm/istio --name istio --namespace istio-system -f Values.yaml
```

##### 5. Istio 检查
```
$ helm status istio
```
