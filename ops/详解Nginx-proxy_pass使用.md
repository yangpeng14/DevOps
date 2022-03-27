## 前言

日常不管是研发还是运维，都多少会使用`Nginx`服务，很多情况Nginx用于反向代理，那就离不开使用`proxy_pass`，有些同学会对 `proxy_pass` 转发代理时 `后面url加 /`、`后面url没有 /`、`后面url添加其它路由`等场景，不能很明白其中的意思，下面来聊聊这些分别代表什么意思。

## 详解

客户端请求 URL `https://172.16.1.1/hello/world.html`

### 第一种场景 后面url加 /

```bash
location /hello/ {
    proxy_pass http://127.0.0.1/;
}
```

`结果`：代理到URL：http://127.0.0.1/world.html


### 第二种场景 后面url没有 /

```bash
location /hello/ {
    proxy_pass http://127.0.0.1;
}
```

`结果`：代理到URL：http://127.0.0.1/hello/world.html

### 第三种场景 后面url添加其它路由，并且最后添加 /

```bash
location /hello/ {
    proxy_pass http://127.0.0.1/test/;
}
```

`结果`：代理到URL：http://127.0.0.1/test/world.html

### 第四种场景 后面url添加其它路由，但最后没有添加 /

```bash
location /hello/ {
    proxy_pass http://127.0.0.1/test;
}
```

`结果`：代理到URL：http://127.0.0.1/testworld.html