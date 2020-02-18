## 前言

本文是对[Rate Limiting with NGINX and NGINX Plus](https://link.jianshu.com/?t=https%3A%2F%2Fwww.nginx.com%2Fblog%2Frate-limiting-nginx%2F)的主要内容（去掉了关于NGINX Plus相关内容）的翻译。

`限流`（rate limiting）是`NGINX`众多特性中最有用的，也是经常容易被误解和错误配置的，特性之一。该特性可以限制某个用户在一个给定时间段内能够产生的`HTTP`请求数。请求可以简单到就是一个对于主页的`GET`请求或者一个登陆表格的`POST`请求。

`限流` 也可以用于安全目的上，比如减慢暴力密码破解攻击。通过限制进来的请求速率，并且（结合日志）标记出目标`URLs`来帮助防范`DDoS`攻击。一般地说，限流是用在保护上游应用服务器不被在同一时刻的大量用户请求湮没。

下面介绍`NGINX`限流的基本用法。

## NGINX限流是如何工作的

`NGINX` 限流使用`漏桶算法`（leaky bucket algorithm），该算法广泛应用于通信和基于包交换计算机网络中，用来处理当带宽被限制时的突发情况。和一个从上面进水，从下面漏水的桶的原理很相似；如果进水的速率大于漏水的速率，这个桶就会发生溢出。
![](/img/6688932-0a729ba489cc3e8e.png)

在请求处理过程中，水代表从客户端来的请求，而桶代表了一个队列，请求在该队列中依据先进先出`（FIFO）`算法等待被处理。漏的水代表请求离开缓冲区并被服务器处理，溢出代表了请求被丢弃并且永不被服务。


## 配置基本的限流功能

有两个主要的指令可以用来配置限流：`limit_req_zone`和`limit_req`，例子：

```
limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;

server {
    location /login/ {
        limit_req zone=mylimit;


        proxy_pass http://my_upstream;
    }
} 
```

当[limit\_req](https://link.jianshu.com/?t=http%3A%2F%2Fnginx.org%2Fen%2Fdocs%2Fhttp%2Fngx_http_limit_req_module.html%23limit_req) 在它出现的环境中启用了限流（在上面的例子中，作用在所有对于`/login/`的请求上），则[limit\_req\_zone](https://link.jianshu.com/?t=http%3A%2F%2Fnginx.org%2Fen%2Fdocs%2Fhttp%2Fngx_http_limit_req_module.html%23limit_req_zone)指令定义了限流的参数。

[limit\_req\_zone](https://link.jianshu.com/?t=http%3A%2F%2Fnginx.org%2Fen%2Fdocs%2Fhttp%2Fngx_http_limit_req_module.html%23limit_req_zone)指令一般定义在http块内部，使得该指令可以在多个环境中使用。该指令有下面三个参数：

* `Key` — 在限流应用之前定义了请求的特征。在上面例子中，它是`$binary_remote_addr`（NGINX变量），该变量代表了某个客户端IP地址的二进制形式。这意味着我们可以将每个特定的IP地址的请求速率限制为第三个参数所定义的值。（使用这个变量的原因是因为它比用string代表客户端IP地址的`$remote_addr`变量消耗更少的空间。）
    
* `Zone` — 定义了存储每个IP地址状态和它访问受限请求URL的频率的共享内存区域。将这些信息保存在共享内存中，意味着这些信息能够在NGINX工作进程之间共享。定义有两个部分：由`zone=`关键字标识的区域名称，以及冒号后面的区域大小。约16000个IP地址的状态信息消耗1M内存大小，因此我们的区域（`zone`）大概可以存储约160000个地址。当NGINX需要添加新的记录时，如果此时存储耗尽了，最老的记录会被移除。如果释放的存储空间还是无法容纳新的记录，NGINX返回`503 (Service Temporarily Unavailable)`状态码。此外，为了防止内存被耗尽，每次NGINX创建一个新的记录的同时移除多达两条前60秒内没有被使用的记录。
    
* `Rate` — 设置最大的请求速率。在上面的例子中，速率不能超过10个请求每秒。NGINX事实上可以在毫秒级别追踪请求，因此这个限制对应了1个请求每100毫秒。因为我们不允许突刺（bursts，短时间内的突发流量，详细见下一部分。），这意味着如果某个请求到达的时间离前一个被允许的请求小于100毫秒，它会被拒绝。
    

`limit_req_zone`指令设置限流和共享内存区域的参数，但是该指令实际上并不限制请求速率。为了限制起作用，需要将该限制应用到某个特定的`location`或`server`块（_block_），通过包含一个`limit_req`指令的方式。在上面的例子中，我们将请求限制在`/login/`上。

所以现在对于`/login/`，每个特定的IP地址被限制为10个请求每秒— 或者更准确地说，不能在与前一个请求间隔100毫秒时间内发送请求。

## 处理流量突刺（Bursts）

如果在100毫秒内得到2个请求会怎么样？对于第2个请求，NGINX返回503状态码给客户端。这可能不是我们想要的，因为事实上，应用是趋向于突发性的。相反，我们想要缓存任何过多的请求并且及时地服务它们。下面是我们使用`limit_req`的`burst`参数来更新配置：

```
location /login/ {
      limit_req zone=mylimit burst=20;

      proxy_pass http://my_upstream;
}
```

`burst`参数定义了一个客户端能够产生超出区域（_zone_）规定的速率的请求数量（在我们示例`mylimit`区域中，速率限制是10个请求每秒，或1个请求每100毫秒）。一个请求在前一个请求后的100毫秒间隔内达到，该请求会被放入一个队列，并且该队列大小被设置为20.

这意味着如果从某个特定IP地址来的21个请求同时地达到，NGINX立即转发第一个请求到上游的服务器组，并且将剩余的20个请求放入队列中。然后，NGINX每100毫秒转发一个队列中的请求，并且只有当某个新进来的请求使得队列中的请求数目超过了20，则返回`503`给客户端。

## 无延迟排队

带有`burst`的配置产生平滑的网络流量，但是不实用，因为该配置会使得你的网站表现的很慢。在上面的例子中，队列中第20个数据包等待2秒才能被转发，这时该数据包的响应可能对于客户端已经没有了意义。为了处理这种情况，除了`burst`参数外，添加`nodelay`参数。

```
location /login/ {
      limit_req zone=mylimit burst=20 nodelay;

      proxy_pass http://my_upstream
}
```

带有`nodelay`参数，NGINX仍然会按照`burst`参数在队列中分配插槽（_slot_）以及利用已配置的限流，但是不是通过间隔地转发队列中的请求。相反，当某个请求来的太快，只要队列中有可用的空间（_slot_），NGINX会立即转发它。该插槽（_slot_）被标记为“已使用”，并且不会被释放给另一个请求，一直到经过适当的时间（在上面的例子中，是100毫秒）。

像之前一样假设有20个插槽的队列是空的，并且来自于给定的IP地址的21个请求同时地到达。NGINX立即转发这21个请求以及将队列中的20个插槽标记为“已使用”，然后每隔100毫秒释放一个插槽。（相反，如果有25个请求，NGINX会立即转发25个中的21个请求，标记20个插槽为“已使用”，并且用`503`状态拒绝4个请求。）

现在假设在转发第一个请求集合之后的101毫秒，有另外的20个请求同时地到达。队列中只有1个插槽被释放，因此NGINX转发1个请求，并且用`503`状态拒绝其它的19个请求。相反，如果在这20个新请求到达之前过去了501毫秒，则有5个插槽被释放，因此NGINX立即转发5个请求，并且拒绝其它15个请求。

效果等同于10个请求每秒的限流。如果你想利用请求之间的无限制性间隔的限流，`nodelay`选项则是非常有用的。

`注意`：**对于大多数的部署，我们推荐在`_limit_req`指令中包含`burst`和`nodelay`参数。

## 高级设置的例子

通过结合基本的限流和其它的`NGINX`特性，你可以实现更多的细微的流量限制。

### 白名单

下面的例子展示了如何将限流作用在任何一个不在“白名单”中的请求上。

```
geo $limit {
        default 1;
        10.0.0.0/8 0;
        192.168.0.0/24 0;
}

map $limit $limit_key {
        0 "";
        1 $binary_remote_addr;
}

limit_req_zone $limit_key zone=req_zone:10m rate=5r/s;

server {
        location / {
                limit_req zone=req_zone burst=10 nodelay;
                
                # ...
        }
}
```

这个例子同时使用了[geo](https://link.jianshu.com/?t=http%3A%2F%2Fnginx.org%2Fen%2Fdocs%2Fhttp%2Fngx_http_geo_module.html%3F%26_ga%3D2.242299339.855057190.1515977474-966707169.1512552597%23geo)和[map](https://link.jianshu.com/?t=http%3A%2F%2Fnginx.org%2Fen%2Fdocs%2Fhttp%2Fngx_http_map_module.html%3F%26_ga%3D2.45561965.855057190.1515977474-966707169.1512552597%23map)指令。对于IP地址在白名单中的，`geo`块分配`0`值给`$limit`；其它所有不在白名单中的IP地址，分配`1`值。然后我们使用一个map去将这些值映射到某个key中，例如：

* 如果`$limit`是`0`，`$limit_key`被设置为空字符串
* 如果`$limit`是`1`，`$limit_key`被设置为客户端的IP地址的二进制格式

这个两个结合起来，对于白名单中的IP地址，`$limit_key`被设置为空字符串；否则，被设置为客户端的IP地址。当`limit_req_zone`指令的第一个参数是一个空字符串，限制不起作用，因此白名单的IP地址（在`10.0.0.0/8`和`192.168.0.0/24`子网中）没有被限制。其它所有的IP地址都被限制为5个请求每秒。

`limit_req`指令将限制作用在`/`定位中，并且允许在没有转发延迟的情况下，转发多达10个数据包。

### 在一个定位中包含多个`limit_req`指令

可以在单个定位（_location_）中包含多个`limit_req`指令。匹配给定的请求限制都会被使用，这意味着采用最严格的限制。例如，如果多于一个的指令使用了延迟，最终使用最长的延迟。类似地，如果某个指令使得请求被拒绝，即使其它的指令允许请求通过，最终还是被拒绝。

我们可以在白名单中的IP地址上应用某个限流来扩展之前的例子：

```
http {
      # ...

      limit_req_zone $limit_key zone=req_zone:10m rate=5r/s;
      limit_req_zone $binary_remote_addr zone=req_zone_wl:10m rate=15r/s;

      server {
            # ...
            location / {
                  limit_req zone=req_zone burst=10 nodelay;
                  limit_req zone=req_zone_wl burst=20 nodelay;
                  # ...            
            }
      }
}
```

在白名单上的IP地址不匹配第一个限流（`req_zone`），但是能匹配第二个（`req_zone_wl`），因此这些IP地址被限制为15个请求每秒。不在白名单上的IP地址两个限流都能匹配上，因此最严格的那个限流起作用：5个请求每秒。

## 配置相关的特性

### 日志（Logging）

默认，NGNIX记录由于限流导致的延迟或丢弃的请求的日志，如下面的例子：

```
2015/06/13 04:20:00 [error] 120315#0: *32086 limiting requests, excess: 1.000 by zone "mylimit", client: 192.168.1.2, server: nginx.com, request: "GET / HTTP/1.0", host: "nginx.com"
```

该日志记录包含的字段：

* `limiting requests` — 日志条目记录了某个限流的标志
* `excess` — 超过这个请求代表的配置的速率的每毫秒请求数目
* `zone` — 定义了启用了限流的区域
* `client` — 产生请求的客户端IP地址
* `server` — 服务器的IP地址或主机名
* `request` — 客户端产生的实际的HTTP请求
* `host` — HTTP头部主机名的值

默认，NGINX日志在`error`级别拒绝请求，如上面例子中的`[error]`所示。（它在低一个级别上记录延迟的请求，因此默认是`info`。）用`limit_req_log_level`指令来改变日志级别。下面我们设置在`warn`级别上记录被拒绝的请求的日志：

```
location /login/ {
      limit_req zone=mylimit burst=20 nodelay;
      limit_req_log_level warn;

      proxy_pass http://my_upstream;
}
```

### 发送给客户端的错误码

默认，当某个客户端超过它的限流，NGINX用`503（Service Temporarily Unavailable）`状态码来响应。使用`limit_req_status`指令设置一个不同的状态码（在下面的例子是`444`）：

```
location /login/ {
      limit_req zone=mylimit burst=20 nodelay;
      limit_req_status 444;
}
```

### 拒绝对特定位置的所有请求

如果你想拒绝对于某个特定URL的所有请求，而不是仅仅的限制它们，可以为这个URL配置一个[location](https://link.jianshu.com/?t=http%3A%2F%2Fnginx.org%2Fen%2Fdocs%2Fhttp%2Fngx_http_core_module.html%3F%26_ga%3D2.11539581.855057190.1515977474-966707169.1512552597%23location)块，并且在其中包含[deny](https://link.jianshu.com/?t=http%3A%2F%2Fnginx.org%2Fen%2Fdocs%2Fhttp%2Fngx_http_access_module.html%3F%26_ga%3D2.45117677.855057190.1515977474-966707169.1512552597%23deny) `all`指令：

```
location /foo.php {
      deny all;
}
```

## 原文出处

> 作者：zlup

> 原文链接：https://www.jianshu.com/p/2cf3d9609af3