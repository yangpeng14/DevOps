## realip 功能介绍

`用途`：当本机 `Nginx` 处于反向代理后端时可以获取到用户的`真实IP地址`。

`使用`：`realip` 功能需要 `Nginx` 添加 `ngx_http_realip_module` 模块，默认情况下是不被编译，如果需要添加，请在编译时添加 `--with-http_realip_module` 选项开启它。

## realip 作用域

`set_real_ip_from`、`real_ip_header` 和 `real_ip_recursive` 都可以用于 `http`、 `server`、`location` 区域配置。

## realip 部分参数解释

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

1、如果 Nginx 没有使用 `realip模块`，第二台 Nginx中 `X-Forwarded-For` 请求是 1.1.1.1，但 `remote_addr` 地址是 2.2.2.2，这时应用服务可以通过 `X-Forwarded-For` 字段获取用户真实IP。不过这里有点风险，如果中间多几层反向代理服务，就无法获取唯一一个用户真实IP。

2、如果 Nginx 使用`realip模块`，并如下设置；Nginx 会取 `X-Forwarded-For` 最后一个IP也就是 2.2.2.2 作为真实IP。最后应用服务拿到的地址也是 2.2.2.2，但事实这不是用户IP。

```
set_real_ip_from 2.2.2.2;
set_real_ip_from 2.2.2.3; 
real_ip_header X-Forwarded-For; 
real_ip_recursive off;
```

3、如果 Nginx 使用`realip模块`，并如下设置；由于 2.2.2.2 是信任服务器IP，Nginx 会继续往前查找，发现 1.1.1.1 不是信任服务器IP，就认为是真实IP。但事实 1.1.1.1 也就是用户IP。最后应用服务也拿到唯一的用户真实IP。

```
set_real_ip_from 2.2.2.2;
set_real_ip_from 2.2.2.3; 
real_ip_header X-Forwarded-For; 
real_ip_recursive on;
```

## 参考链接

- https://cloud.tencent.com/developer/article/1521273
- https://www.cnblogs.com/amyzhu/p/9610056.html
