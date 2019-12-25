## GoAccess 是什么？

`GoAccess` 是一个开源的`实时Web日志分析器`和`交互式查看器`，可在*nix系统上的终端或通过浏览器运行。它为系统管理员提供了实时而有价值的HTTP统计信息。

## GoAccess 输出展示

- 终端输出

    ![](/img/goaccess-nginx.png)

- HTML Dashboard

    ![HTML Dashboard](/img/goaccess-dashboard.png)

## 为什么选择GoAccess？
`GoAccess` 被设计为一种基于终端的快速日志分析器。它的核心思想是无需使用浏览器就可以快速实时地实时分析和查看Web服务器统计信息（如果您想通过SSH快速分析访问日志，或者只是喜欢在终端中工作，那将是一个很好的选择）。

终端输出是默认输出，但它具有生成完整的，独立的实时 `HTML` 报告以及 `JSON` 和 `CSV` 报告的功能。

## GoAccess 功能

`GoAccess` 解析指定的Web日志文件，并将数据输出到X终端。功能包括：

- 完全实时

    终端每200毫秒更新一次，HTML每秒更新一次。

- 需要最少的配置

    直接接日志文件并运行，选择日志格式，然后让GoAccess解析访问日志并向您显示统计信息。

- 跟踪应用程序响应时间

    跟踪服务请求所花费的时间。如果您要跟踪正在降低网站速度的页面，则非常有用。

- 几乎所有Web日志格式

    GoAccess 允许使用任何自定义日志格式字符串。预定义的选项包括 Apache，Nginx，Amazon S3，Elastic Load Balancing，CloudFront等。

- 增量日志处理

    需要数据持久性吗？GoAccess 能够通过磁盘 `B + Tree` 数据库增量处理日志。

- 仅一个依赖

    GoAccess是用C语言编写的。要运行它，你只需要将 `ncurses` 作为依赖项

- 访问次数

    按小时或日期来统计请求数，访问者，带宽等。

- 多个虚拟主机的指标

    有多个虚拟主机？它具有一个面板，该面板显示哪个虚拟主机正在消耗大多数Web服务器资源。

- 颜色方案可定制的

    Tailor GoAccess 可以适合您自己的颜色口味/方案。通过终端，或者简单地在HTML输出上应用样式表。

- 对大型数据集的支持

    GoAccess 为大型数据集提供了一个磁盘B + Tree存储。

- Docker支持

    能够从上游构建 GoAccess 的Docker映像。

## 默认支持的Web日志格式

GoAccess允许任何自定义日志格式字符串。使用 `-log-format` 参数指定日志格式，预定义的选项包括但不限于：

- COMBINED     | 联合日志格式（Apache、Nginx等）
- VCOMBINED    | 支持虚拟主机的联合日志格式
- COMMON       | 通用日志格式
- VCOMMON      | 支持虚拟主机的通用日志格式
- W3C          | W3C 扩展日志格式
- SQUID        | Native Squid 日志格式
- CLOUDFRONT   | 亚马逊 CloudFront Web 分布式系统
- CLOUDSTORAGE | 谷歌云存储
- AWSELB       | 亚马逊弹性负载均衡
- AWSS3        | 亚马逊简单存储服务 (S3)

## 存储

GoAccess 支持三种类型的存储方式。请根据你的需要和系统环境进行选择。

- 默认哈希表
    > 内存哈希表可以提供较好的性能，缺点是数据集的大小受限于物理内存的大小。GoAccess 默认使用内存哈希表。如果你的内存可以装下你的数据集，那么这种模式的表现非常棒。此模式具有非常好的内存利用率和性能表现。

- Tokyo Cabinet 磁盘 B+ 树

    > 使用这种模式来处理巨大的数据集，大到不可能在内存中完成任务。当数据提交到磁盘以后，B+树数据库比任何一种哈希数据库都要慢。但是，使用 SSD 可以极大的提高性能。往后您可能需要快速载入保存的数据，那么这种方式就可以被使用。

- Tokyo Cabinet 内存哈希表
    > 作为默认哈希表的替换方案。因为使用通用类型在内存表现以及速度方面都很平均。

## 安装

- 源码安装

    ```bash
    $ wget https://tar.goaccess.io/goaccess-1.3.tar.gz
    $ tar -xzvf goaccess-1.3.tar.gz
    $ cd goaccess-1.3/
    $ ./configure --enable-utf8 --enable-geoip=legacy
    $ make
    $ make install
    ```

- Debian / Ubuntu

    ```bash
    $ echo "deb https://deb.goaccess.io/ $(lsb_release -cs) main" | sudo tee -a /etc/apt/sources.list.d/    goaccess.list
    $ wget -O - https://deb.goaccess.io/gnugpg.key | sudo apt-key add -
    $ sudo apt-get update
    $ sudo apt-get install goaccess
    ```

    注意事项：

    - 要获得磁盘上的支持（Trusty + 或 Wheezy +），请运行：`sudo apt-get install goaccess-tcb`
    - `.deb` 官方仓库中的软件包也可以通过HTTPS获得。您可能需要安装 `apt-transport-https`


- CentOS / RedHat

    ```bash
    $ yum install goaccess -y
    ```

- OS X / Homebrew

    ```bash
    $ brew install goaccess
    ```

## 用法/示例

- 要输出到终端并生成交互式报告

    ```bash
    $ goaccess access.log
    ```

- 生成 HTML 报告

    ```bash
    $ goaccess --log-format=COMBINED access.log -a > report.html
    ```

- 生成 JSON 报告

    ```bash
    $ goaccess --log-format=COMBINED access.log -a -d -o json > report.json
    ```

- 生成 CSV 文件

    ```bash
    $ goaccess --log-format=COMBINED access.log --no-csv-summary -o csv > report.csv
    ```

- GoAccess 还为实时过滤和解析提供了极大的灵活性。例如，要从goaccess启动以来通过监视日志来快速诊断问题：

    ```bash
    $ tail -f access.log | goaccess -
    ```

- 更妙的是，进行筛选，同时保持打开的管道保持实时分析，我们可以利用的 `tail -f` 和匹配模式的工具，如`grep`，`awk`，`sed`，等：

    ```bash
    $ tail -f access.log | grep -i --line-buffered 'firefox' | goaccess --log-format=COMBINED -
    ```

- 或从文件的开头进行解析，同时保持管道处于打开状态并应用过滤器

    ```bash
    $ tail -f -n +0 access.log | grep -i --line-buffered 'firefox' | goaccess -o report.html    --real-time-html -
    ```

- 监示多个日志文件

    ```bash
    $ goaccess access.log access.log.1
    ```

- 实时 HTML 输出

    生成实时HTML报告的过程与创建静态报告的过程非常相似。只--real-time-html需要使其实时即可。
    ```bash
    $ goaccess --log-format=COMBINED access.log -o /usr/share/nginx/html/your_site/report.html --real-time-html
    ```

## 自定义 日志/日期 格式

有两种方法自定义配置日志格式。最简单的方式是运行 GoAccess 时使用 `-c` 显示一个配置窗口。但是这种方式不是永久有效的，因此你需要在配置文件中设定格式。

配置文件位于：`%sysconfdir%/goaccess.conf` 或者 `~/.goaccessrc`

`注意`：`%sysconfdir%` 可能是 `/etc/`, `/usr/etc/` 或者 `/usr/local/etc/`

`time-format` 参数 time-format 后跟随一个空格符，指定日志的时间格式，包含普通字符与特殊格式说明符的任意组合。他们都由百分号 (%)开始。参考 `man strftime`。 %T 或者 %H:%M:%S

`注意`：如果给定的时间戳以微秒计算，则必须在 time-format 中使用参数 `%f`。

`date-format` 参数 date-format 后跟随一个空格符，指定日志的日期格式，包含普通字符与特殊格式说明符的任意组合。他们都由百分号 (%)开始。参考 `man strftime`。

`注意`：如果给定的时间戳以微秒计算，则必须在 date-format 中使用参数 `%f` 。

`log-format` 参数 log-format 后跟随一个空格符或者制表分隔符(`\t`)，用于指定日志字符串格式。

`特殊格式说明符`：

- `%x` 匹配 time-format 和 date-format 变量的日期和时间字段。用于使用时间戳来代替日期和时间两个独立变量的场景。
- `%t` 匹配 time-format 变量的时间字段。
- `%d` 匹配 date-format 变量的日期字段。
- `%v` 根据 canonical 名称设定的服务器名称(服务区或者虚拟主机)。
- `%e` 请求文档时由 HTTP 验证决定的用户 ID。
- `%h` 主机(客户端IP地址，IPv4 或者 IPv6)。
- `%r` 客户端请求的行数。这些请求使用分隔符(单引号，双引号)引用的部分可以被解析。否则，需要使用由特殊格式说明符(例如：`%m`, - `%U`, `%q` 和 `%H`)组合格式去解析独立的字段。
    - `注意`: 既可以使用 `%r` 获取完整的请求，也可以使用 `%m`, `%U`, `%q` and `%H` 去组合你的请求，但是不能同时使用。
- `%m` 请求的方法。
- `%U` 请求的 URL。
    - `注意`: 如果查询字符串在 `%U` 中，则无需使用 `%q`。但是，如果 URL 路径中没有包含任何查询字符串，则你可以使用 `%q` 查询字符串将附加在请求后面。
- `%q` 查询字符串。 
- `%H` 请求协议。
- `%s` 服务器回传客户端的状态码。
- `%b` 回传客户端的对象的大小。
- `%R` HTTP 请求的 "Referer" 值。
- `%u` HTTP 请求的 "UserAgent" 值。
- `%D` 处理请求的时间消耗，使用微秒计算。
- `%T` 处理请求的时间消耗，使用带秒和毫秒计算。
- `%L` 处理请求的时间消耗，使用十进制数表示的毫秒计算。
- `%^` 忽略此字段。
- `%~` 继续解析日志字符串直到找到一个非空字符(!isspace)。
- `~h` 在 X-Forwarded-For (XFF) 字段中的主机(客户端 IP 地址，IPv4 或者 IPv6)。


## 注意事项

每一个活动面板上最多有 366 个对象，如果是实时 HTML 报告则为 50 个对象。对象上限可以通过最大对象数自定义，但是只有 CSV 和 JSON 格式的输出允许超过默认值，即 366 对象每面板。

在使用磁盘B+树(使用参数 `--keep-db-files` 和 `--load-from-disk`)加载了同一个日志两次，则 GoAccess 会将每个请求也计算两次。问题#334 详细说明了此问题。

一次访问就是一次请求(访问日志中的每一行)，例如，10 次请求 = 10 次访问。具有相同 IP，日期，和 UserAgent 的 HTTP 请求将被认为是一个独立访问。

## 参考链接

- https://goaccess.cc/?mod=man
- https://github.com/allinurl/goaccess