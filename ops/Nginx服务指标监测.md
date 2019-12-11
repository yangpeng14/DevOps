## ngxtop 简介

`ngxtop` 解析您的 nginx 访问日志，并输出 top nginx服务器有用的（类似）指标。因此，您可以实时了解服务器的状况。

## ngxtop 默认输出

```bash
$ ngxtop
```
![](/img/ngtop-1.png)

## 查看客户端 TOP IP
```bash
$ ngxtop top remote_addr

running for 20 seconds, 3215 records processed: 159.62 req/sec

top remote_addr
| remote_addr     |   count |
|-----------------+---------|
| 118.173.177.161 |      20 |
| 110.78.145.3    |      16 |
| 171.7.153.7     |      16 |
| 180.183.67.155  |      16 |
| 183.89.65.9     |      16 |
| 202.28.182.5    |      16 |
| 1.47.170.12     |      15 |
| 119.46.184.2    |      15 |
| 125.26.135.219  |      15 |
| 125.26.213.203  |      15 |
```

## 列出 4xx 和 5xx 以及 HTTP referer
```bash
$ ngxtop -i 'status >= 400' print request status http_referer

running for 2 seconds, 28 records processed: 13.95 req/sec

request, status, http_referer:
| request   |   status | http_referer   |
|-----------+----------+----------------|
| -         |      400 | -              |
```

## 安装
```bash
$ pip install ngxtop
```

## 项目地址
- https://github.com/lebinh/ngxtop

## 参考链接
- https://github.com/lebinh/ngxtop