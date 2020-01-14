## 前提

> 本文使用 Ingress Nginx Version 0.24.1

本文所讲的配置规则，都配置在 `annotations`（局部配置） 中，`Ingress Nginx Deployment` 必须配置 `--annotations-prefix` 参数，默认以 `nginx.ingress.kubernetes.io` 开头。 

Ingress Nginx Deployment 示例：

```yaml
containers:
  - name: nginx-ingress-controller
    image: quay.io/kubernetes-ingress-controller/nginx-ingress-controller:0.24.1
    args:
      - /nginx-ingress-controller
      - --configmap=$(POD_NAMESPACE)/nginx-configuration
      - --tcp-services-configmap=$(POD_NAMESPACE)/tcp-services
      - --udp-services-configmap=$(POD_NAMESPACE)/udp-services
      - --publish-service=$(POD_NAMESPACE)/ingress-nginx
      - --annotations-prefix=nginx.ingress.kubernetes.io
      - --ingress-class=nginx # 指定ingress-class 属性
```

`--ingress-class`：声明ingress入口名称，如果要绑定这个ingress，需要在 `annotation` 中定义 `kubernetes.io/ingress.class: "nginx"`

## 开启 TLS

> 创建ssl证书 secret

```bash
$ kubectl create secret tls www-example-com --key tls.key --cert tls.crt -n default
```

> `nginx.ingress.kubernetes.io/ssl-redirect` 默认为 `true`，启用 `TLS` 时，http请求会 `308` 重定向到https

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: demo-ingress
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx" # 绑定ingress-class
    nginx.ingress.kubernetes.io/ssl-redirect: "false" # 关闭SSL跳转
spec:
  rules:
  - host: www.example.com
    http:
      paths:
      - path: /
        backend:
          serviceName: demo-svc
          servicePort: 8080
  tls:
  - secretName: www-example-com
    hosts:
    - www.example.com
```

## 配置白名单IP范围

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: demo-ingress
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx" # 绑定ingress-class
    nginx.ingress.kubernetes.io/whitelist-source-range: 10.0.0.0/24,172.10.0.1
spec:
  rules:
  - host: www.example.com
    http:
      paths:
      - path: /
        backend:
          serviceName: demo-svc
          servicePort: 8080
```

## 支持socket.io配置

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: demo-ingress
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx" # 绑定ingress-class
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "3600"
    nginx.ingress.kubernetes.io/upstream-hash-by: "$http_x_forwarded_for" # 以客户端IP哈希
spec:
  rules:
  - host: www.example.com
    http:
      paths:
      - path: /
        backend:
          serviceName: demo-svc
          servicePort: 8080
```

## rewrite 配置

> 下面 rewrite 规则意思是 访问 www.example.com/hello/(.*) 跳转到 www.example.com/(.*)

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: demo-ingress
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx" # 绑定ingress-class
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/rewrite-target: "/$1"
spec:
  rules:
  - host: www.example.com
    http:
      paths:
      - path: /hello/(.*)$
        backend:
          serviceName: demo-svc
          servicePort: 8080
```

或者

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: demo-ingress
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx" # 绑定ingress-class
    nginx.ingress.kubernetes.io/configuration-snippet: |
      rewrite ^/hello/(.*)$ /$1 redirect;
spec:
  rules:
  - host: www.example.com
    http:
      paths:
      - path: /hello/(.*)$
        backend:
          serviceName: demo-svc
          servicePort: 8080
```

## 限速

> 设置 www.example.com/login 登陆页为每秒100个连接数，10.0.0.0/24,172.10.0.1 IP段不在限速范围

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: demo-ingress
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx" # 绑定ingress-class
    nginx.ingress.kubernetes.io/limit-rps: '100'
    nginx.ingress.kubernetes.io/limit-whitelist: 10.0.0.0/24,172.10.0.1
spec:
  rules:
  - host: www.example.com
    http:
      paths:
      - path: /login
        backend:
          serviceName: demo-svc
          servicePort: 8080
```

## 参考链接
- https://github.com/kubernetes/ingress-nginx/blob/nginx-0.24.1/docs/user-guide/nginx-configuration/annotations.md