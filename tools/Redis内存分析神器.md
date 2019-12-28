## RDR 简介

`RDR` 是解析 `redis rdbfile` 工具。与`redis-rdb-tools`相比，RDR 是由golang 实现的，速度更快（5GB rdbfile 在我的PC上大约需要2分钟）。


## 例子

```bash
$ ./rdr show -p 8080 *.rdb
```

![](/img/rdr.png)

```bash
$ ./rdr keys example.rdb

portfolio:stock_follower_count:ZH314136
portfolio:stock_follower_count:ZH654106
portfolio:stock_follower:ZH617824
portfolio:stock_follower_count:ZH001019
portfolio:stock_follower_count:ZH346349
portfolio:stock_follower_count:ZH951803
portfolio:stock_follower:ZH924804
portfolio:stock_follower_count:INS104806
```

## 优势

- 分析 Redis 内存中那个 Key 值占用的内存最多
- 分析出 Redis 内存中那一类开头的 Key 占用最多，有利于内存优化
- Redis Key 值以 Dashboard 展示，这样更直观

## 安装

- Linux amd64

    ```bash
    $ wget https://github.com/xueqiu/rdr/releases/download/v0.0.1/rdr-linux -O /usr/local/bin/rdr
    $ chmod +x /usr/local/bin/rdr
    ```

- MacOS

    ```bash
    $ curl https://github.com/xueqiu/rdr/releases/download/v0.0.1/rdr-darwin -o /usr/local/bin/rdr
    $ chmod +x /usr/local/bin/rdr
    ```

- Windows

    ```bash
    # 浏览器下载下面链接，在点击运行
    https://github.com/xueqiu/rdr/releases/download/v0.0.1/rdr-windows.exe
    ```


## RDR 参数解释

- show 网页显示 rdbfile 的统计信息
- keys 从 rdbfile 获取所有 key
- help 帮助
- --version 显示版本信息

`分析多个 Redis rdb`

```bash
$ rdr keys FILE1 [FILE2] [FILE3]...
```

## 项目地址

- https://github.com/xueqiu/rdr