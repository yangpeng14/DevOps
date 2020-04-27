## 前言

1、`Ingress Nginx` 默认访问日志都输出到 `/var/log/nginx/access.log` 文件中，但是对于生产环境来说，不可能把所有日志都输到一个日志文件中，一般情况都是根据域名分别输出到各个文件中。

2、`Ingress Nginx` 修改默认日志输出字段，可以输出为`json`格式 和 普通日志格式。

## 根据域名设置访问日志输出

```bash
$ vim test-example-com.yaml
```

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: demo-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/enable-access-log: "true"
    nginx.ingress.kubernetes.io/configuration-snippet: |
       access_log /var/log/nginx/test.example.com.access.log upstreaminfo if=$loggable;
       error_log  /var/log/nginx/test.example.com.error.log;
spec:
  rules:
  - host: test.example.com
    http:
      paths:
      - backend:
          serviceName: demo
          servicePort: 8080
```

```yaml
# 部署
$ kubectl apply -f test-example-com.yaml
```

## 设置输出为`json`格式 和 普通日志格式

修改 `mandatory.yaml` 部署文件 nginx-configuration ConfigMap 配置中 `log-format-upstream` 字段，具体修改如下：

1、普通访问日志格式

```yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: nginx-configuration
  namespace: ingress-nginx
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
data:
  client-header-buffer-size: "512k"
  large-client-header-buffers: "4 512k"
  client-body-buffer-size: "128k"
  proxy-buffer-size: "256k"
  client-body-buffer-size: "128k"
  proxy-body-size: "50m"
  server-name-hash-bucket-size: "128"
  map-hash-bucket-size: "128"
  ssl-ciphers: "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA"
  ssl-protocols: "TLSv1 TLSv1.1 TLSv1.2"
  log-format-upstream: '[$the_real_ip] - $remote_user [$time_local] "$request" $status $body_bytes_sent $request_time "$http_referer" $host DIRECT/$upstream_addr $upstream_http_content_type "$http_user_agent" "$http_x_forwarded_for" $request_length [$proxy_upstream_name] $upstream_response_length $upstream_response_time $upstream_status $req_id'
```

2、json 访问日志格式

```yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: nginx-configuration
  namespace: ingress-nginx
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
data:
  client-header-buffer-size: "512k"
  large-client-header-buffers: "4 512k"
  client-body-buffer-size: "128k"
  proxy-buffer-size: "256k"
  client-body-buffer-size: "128k"
  proxy-body-size: "50m"
  server-name-hash-bucket-size: "128"
  map-hash-bucket-size: "128"
  ssl-ciphers: "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA"
  ssl-protocols: "TLSv1 TLSv1.1 TLSv1.2"
  log-format-upstream: '{"time": "$time_iso8601", "remote_addr": "$proxy_protocol_addr", "x-forward-for": "$proxy_add_x_forwarded_for", "request_id": "$req_id", "remote_user": "$remote_user", "bytes_sent": $bytes_sent, "request_time": $request_time, "status":$status, "vhost": "$host", "request_proto": "$server_protocol", "path": "$uri", "request_query": "$args", "request_length": $request_length, "duration": $request_time,"method": "$request_method", "http_referrer": "$http_referer", "http_user_agent": "$http_user_agent"}'
```

```bash
# 部署
$ kubectl apply -f mandatory.yaml
```

## 参考链接
- https://github.com/kubernetes/ingress-nginx/blob/master/docs/user-guide/nginx-configuration/configmap.md
- https://github.com/kubernetes/ingress-nginx/blob/master/docs/user-guide/nginx-configuration/annotations.md