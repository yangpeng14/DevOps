## Nginx简介
Nginx（发音同engine x）是一个异步框架的 Web 服务器，也可以用`作反向代理`，`负载平衡器` 和 `HTTP 缓存`。该软件由 Igor Sysoev 创建，并于2004年首次公开发布。同名公司成立于2011年，以提供支持。Nginx 是一款免费的开源软件，根据类 BSD 许可证的条款发布。一大部分Web服务器使用 Nginx ，通常作为负载均衡器。[[1]]

## Nginx的特点
- 更快:
    - 单次请求会得到更快的响应
    - 在高并发环境下,Nginx比其他web服务器有更快的响应

- 高扩展性:
    - nginx是基于模块化设计,由多个耦合度极低的模块组成,因此具有很高的扩展性。许多高流量的网站都倾向于开发符合自己业务特性的定制模块。

- 高可靠性:
    - nginx的可靠性来自于其核心框架代码的优秀设计，模块设计的简单性；另外，官方提供的常用模块都非常稳定，每个worker进程相对独立，master进程在一个worker进程出错时可以快速拉起新的worker子进程提供服务。

- 低内存消耗:
    - 一般情况下，10000个非活跃的HTTP `Keep-Alive` 连接在Nginx中仅消耗2.5MB的内存，这是nginx支持高并发连接的基础。
    - 单机支持10万以上的并发连接：`理论上，Nginx 支持的并发连接上限取决于内存，10万远未封顶。`

- 热部署:
    - master 进程与 worker 进程的分离设计，使得 Nginx 能够提供热部署功能，即在 7x24 小时不间断服务的前提下，升级 Nginx 的可执行文件。当然，它也支持不停止服务就更新配置项，更换日志文件等功能。

- 最自由的 BSD 许可协议:
    - 这是 Nginx 可以快速发展的强大动力。BSD 许可协议不只是允许用户免费使用 Nginx ，它还允许用户在自己的项目中直接使用或修改 Nginx 源码，然后发布。[[2]]

## 内置变量参数详解
- $args    # 请求中的参数值
- $query_string # 同 $args
- $arg_NAME  # GET请求中NAME的值
- $is_args   # 如果请求中有参数，值为"?"，否则为空字符串
- $uri # 请求中的当前URI(不带请求参数，参数位于$args)- ，可以不同于浏览器传递的$request_uri的值，它可以通过内部重定向，或者使用index指令进行修改，$uri不包含主机名，如"/foo/bar.html"。
- $document_uri  # 同 $uri
- $document_root  # 当前请求的文档根目录或别名
- $host  # 优先级：HTTP请求行的主机名>"HOST"请求头字段>- 符合请求的服务器名.请求中的主机头字段，如果请求中的主机头不可用，则为服务器处理请求的服务器名称
- $hostname # 主机名
- $https    # 如果开启了SSL安全模式，值为"on"，否则为空字符串。
- $binary_remote_addr # 客户端地址的二进制形式，固定长度为4个字节
- $body_bytes_sent # 传输给客户端的字节数，响应头不计算在内；这个变量和Apache的mod_log_config模块中的"%B"参数保持兼容
- $bytes_sent # 传输给客户端的字节数
- $connection  # TCP连接的序列号
- $connection_requests  # TCP连接当前的请求数量
- $content_length          # "Content-Length" 请求头字段
- $content_type            # "Content-Type" 请求头字段
- $cookie_name  # cookie名称
- $limit_rate   # 用于设置响应的速度限制
- $msec # 当前的Unix时间戳
- $nginx_version  # nginx版本
- $pid  # 工作进程的PID
- $pipe # 如果请求来自管道通信，值为"p"，否则为"."
- $proxy_protocol_addr # 获取代理访问服务器的客户端地址，如果是直接访问，该值为空字符串
- $realpath_root # 当前请求的文档根目录或别名的真实路径，会将所有符号连接转换为真实路径
- $remote_addr  # 客户端地址
- $remote_port  # 客户端端口
- $remote_user  # 用于HTTP基础认证- 服务的用户名
- $request # 代表客户端的请求地址
- $request_body  # 客户端的请求主体：此变量可在l- - ocation中使用，将请求主体通过proxy_pass，fastcgi_pass，uwsgi_pass和scgi_pass传递给下一级的代理服务器
- $request_body_file # 将客户端请求主体保存在临时文件中。文件处理结束后，此文件需删除。如果需要之一开启此功能，需要设置client_body_in_fi- le_only。如果将次文件传 递给后端的代理服务器，需要禁用request body，即设置proxy_pass_request_body off，fastcgi_pass_request_body - off，uwsgi_pass_request_body off，or scgi_pass_request_body off
- $request_completion # 如果请求成功，值为"OK"，如果请求未完成或者请求不是一个范围请求的最后一部分，则为空
- $request_filename  # 当前连接请求的文件路径，由root或alias指令与URI请求生成
- $request_length   # 请求的长度 (包括请求的地址，http请求头和请求主体)
- $request_method   # HTTP请求方法，通常为"GET"或"POST"- 
- $request_time     # 处理客户端请求使用的时间,单位为秒，精度毫秒； - 从读入客户端的第一个字节开始，直到把最后一个字符发送给客户端后进行日志写入为止。- 
- $request_uri    # 这个变量等于包含一些客户端请求参数的原始URI，它无法修改，请查看$uri更改或重写URI，不包含主机名，例如："/cnphp/- test.php?arg=freemouse"
- $scheme  # 请求使用的Web协议，"http" 或 "https"
- $server_addr  # 服务器端地址，需要注意的是：为了避免访问linux系统内核，应将ip地址提前设置在配置文件中
- $server_name      # 服务器名
- $server_port      # 服务器端口
- $server_protocol  # 服务器的HTTP版本，通常为 "HTTP/1.0" 或 "HTTP/1.1"
- $status # HTTP响应代码
- $time_iso8601  # 服务器时间的ISO 8610格式
- $time_local   # 服务器时间（LOG Format 格式）
- $cookie_NAME # 客户端请求Header头中的cookie变量，前缀"$cookie_"加上cookie名称的变量，该变量的值即为cookie名称的值
- $http_NAME # 匹配任意请求头字段；变量名中的后半部分NAME可以替换成任意请求头字段，如在配置文件中需要获取http请求头："Accept-L- anguage"，$http_accept_language即可
- $http_cookie # cookie 信息
- $http_host  # 请求地址，即浏览器中你输入的地址（IP或域名）
- $http_referer # url跳转来源,用来记录从那个页面链接访问过来的
- $http_user_agent # 用户终端浏览器等信息
- $http_x_forwarded_for
- $sent_http_NAME # 可以设置任意http响应头字段；变量名中的后半部分NAME可以替换成任意响应头字段，如需要设置响应头 Content-length，$s- ent_http_content_length即可
- $sent_http_cache_control # 发送http缓存控制
- $sent_http_connection # 发送http连接
- $sent_http_content_type # 发送http类型
- $sent_http_keep_alive # 发送http连接保持
- $sent_http_last_modified # 发送http最后修改
- $sent_http_location # 发送http位置
- $sent_http_transfer_encoding- # 发送http传输编码 [[3]]

## Nginx 日志例子
```bash
log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent $request_time "$http_referer" '
                      '$host DIRECT/$upstream_addr $upstream_http_content_type '
                      '"$http_user_agent" "$http_x_forwarded_for" '
                      '"$Cookie_MEIQIA_EXTRA_TRACK_ID" "$Cookie_cpsInfo" "$Cookie_sid_account" "$Cookie_sid_user" "$Cookie_ss_user" "$Cookie_xxd_uid" "$Cookie_xxd_user" "$uid_got" "$uid_set"';
```

## log_format 部分参数解释
- $proxy_protocol_addr # 远程地址（如果启用了代理协议）
- $remote_addr # 客户端的源IP地址
- $remote_user # 用于HTTP基础认证服务的用户名 
- $time_local # 访问时间和时区 
- $request    # 请求的URI和HTTP协议
- $http_host # 请求地址，即浏览器中你输入的地址（IP或域名）
- $request # 请求的URI和HTTP协议
- $http_host  # 请求地址，即浏览器中你输入的地址（IP或域名）
- $status                 # HTTP请求状态
- $upstream_status        # upstream状态
- $body_bytes_sent        # 发送给客户端文件内容大小
- $http_referer           # url跳转来源
- $http_user_agent        # 用户终端浏览器等信息
- $ssl_protocol           # SSL协议版本 
- $ssl_cipher             # 交换数据中的算法 
- $upstream_addr          # 后台upstream的地址，即真正提供服务的主机地址
- $request_time           # 整个请求的总时间 
- $upstream_response_time # 请求过程中，upstream响应时间  [[4]]

## 参考链接
[1]:https://zh.wikipedia.org/wiki/Nginx
[2]:https://www.jianshu.com/p/99d50fcc5cd6
[3]:https://mooon.top/2019/03/25/blog/nginx%E5%86%85%E7%BD%AE%E5%8F%98%E9%87%8F%E4%BB%A5%E5%8F%8A%E6%97%A5%E5%BF%97%E6%A0%BC%E5%BC%8F%E5%8F%98%E9%87%8F%E5%8F%82%E6%95%B0%E8%AF%A6%E8%A7%A3/
[4]:https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/log-format/

- https://zh.wikipedia.org/wiki/Nginx
- https://www.jianshu.com/p/99d50fcc5cd6
- https://mooon.top/2019/03/25/blog/nginx%E5%86%85%E7%BD%AE%E5%8F%98%E9%87%8F%E4%BB%A5%E5%8F%8A%E6%97%A5%E5%BF%97%E6%A0%BC%E5%BC%8F%E5%8F%98%E9%87%8F%E5%8F%82%E6%95%B0%E8%AF%A6%E8%A7%A3/
- https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/log-format/