## realip 功能介绍

`用途`：`realip` 当本机 `Nginx` 处于反向代理后端时可以获取到用户的`真实IP地址`。

`使用`：`realip` 功能需要 `Nginx` 添加 `ngx_http_realip_module` 模块，默认情况下是不被编译，如果需要添加，请在编译时添加 `--with-http_realip_module` 选项开启它。

## realip 作用域

`set_real_ip_from`、`real_ip_header` 和 `real_ip_recursive` 都可以用于 `http`、 `server`、`location` 区域配置。

## realip 部署参数解释

- `set_real_ip_from`：设置反向代理服务器，即信任服务器IP
- `real_ip_header X-Forwarded-For`：用户真实IP存在`X-Forwarded-For`请求头中
- `real_ip_recursive`：
    - `off`：会将`real_ip_header`指定的HTTP头中的最后一个IP作为真实IP
    - `on`：会将`real_ip_header`指定的HTTP头中的最后一个不是信任服务器的IP当成真实IP


## http 头中的 X-Forwarded-For、X-Real-IP、Remote Address 解释

`X-Forwarded-For` 位于HTTP请求头，是HTTP的扩展 `header`，用于表示HTTP请求端`真实IP`。

格式如下：

```
X-Forwarded-For: client, proxy1, proxy2
```

Nginx 代理一般配置为:

```
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

解释：

- `X-Forwarded-For`：Nginx追加上去的，但前面部分来源于nginx收到的请求头，这部分内容不是`很可信`。符合IP格式的才可以使用，否则容易引发`XSS`或者`SQL注入漏洞`。
- `Remote Address`：HTTP协议没有IP的概念，`Remote Address`来自于TCP连接，表示与服务端建立TCP连接的设备IP，因此，Remote Address无法伪造。
- `X-Real-IP`：HTTP代理用于表示与它产生TCP连接的设备IP，可能是其他代理，也可能是真正的请求端。

## realip 功能举例说明

下面是一个简单的架构图：

![](/img/nginx-realip-2.png)

### 假设一：

如果 Nginx 没有使用 `realip模块`，

## 参考链接

- https://cloud.tencent.com/developer/article/1521273
- https://www.cnblogs.com/amyzhu/p/9610056.html
