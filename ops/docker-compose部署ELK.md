## ELK 是什么？[1]
`ELK` 是三个开源项目的首字母缩写，这三个项目分别是：`Elasticsearch`、`Logstash` 和 `Kibana`。

- `Elasticsearch` 是一个分布式的开源搜索和分析引擎，适用于所有类型的数据，包括文本、数字、地理空间、结构化和非结构化数据。
- `Logstash` 是服务器端数据处理管道，能够同时从多个来源采集数据，转换数据，然后将数据发送到诸如 `Elasticsearch` 等“存储库”中。
- `Kibana` 则可以让用户在 `Elasticsearch` 中使用图形和图表对数据进行可视化。

## Elasticsearch 的用途是什么？[2]
`Elasticsearch` 在速度和可扩展性方面都表现出色，而且还能够索引多种类型的内容，这意味着其可用于多种用例：

- 应用程序搜索
- 网站搜索
- 企业搜索
- 日志处理和分析
- 基础设施指标和容器监测
- 应用程序性能监测
- 地理空间数据分析和可视化
- 安全分析
- 业务分析

## Elasticsearch 的工作原理是什么？
原始数据会从多个来源（包括日志、系统指标和网络应用程序）输入到 Elasticsearch 中。数据采集指在 Elasticsearch 中进行索引之前解析、标准化并充实这些原始数据的过程。这些数据在 Elasticsearch 中索引完成之后，用户便可针对他们的数据运行复杂的查询，并使用聚合来检索自身数据的复杂汇总。在 Kibana 中，用户可以基于自己的数据创建强大的可视化，分享仪表板，并对 Elastic Stack 进行管理。

## Elasticsearch 索引是什么？
`Elasticsearch` 索引指相互关联的文档集合。`Elasticsearch` 会以 `JSON` 文档的形式存储数据。每个文档都会在一组键（字段或属性的名称）和它们对应的值（字符串、数字、布尔值、日期、数值组、地理位置或其他类型的数据）之间建立联系。

`Elasticsearch` 使用的是一种名为倒排索引的数据结构，这一结构的设计可以允许十分快速地进行全文本搜索。倒排索引会列出在所有文档中出现的每个特有词汇，并且可以找到包含每个词汇的全部文档。

在索引过程中，`Elasticsearch` 会存储文档并构建倒排索引，这样用户便可以近实时地对文档数据进行搜索。索引过程是在索引 API 中启动的，通过此 API 您既可向特定索引中添加 JSON 文档，也可更改特定索引中的 JSON 文档。

## Logstash 的用途是什么？
`Logstash` 是 Elastic Stack 的核心产品之一，可用来对数据进行聚合和处理，并将数据发送到 Elasticsearch。Logstash 是一个开源的服务器端数据处理管道，允许您在将数据索引到 Elasticsearch 之前同时从多个来源采集数据，并对数据进行充实和转换。

## Kibana 的用途是什么？
`Kibana` 是一款适用于 Elasticsearch 的数据可视化和管理工具，可以提供实时的直方图、线形图、饼状图和地图。Kibana 同时还包括诸如 Canvas 和 Elastic Maps 等高级应用程序；Canvas 允许用户基于自身数据创建定制的动态信息图表，而 Elastic Maps 则可用来对地理空间数据进行可视化。

## 为何使用 Elasticsearch？
`Elasticsearch 很快`。 由于 Elasticsearch 是在 `Lucene` 基础上构建而成的，所以在全文本搜索方面表现十分出色。Elasticsearch 同时还是一个近实时的搜索平台，这意味着从文档索引操作到文档变为可搜索状态之间的延时很短，一般只有一秒。因此，Elasticsearch 非常适用于对时间有严苛要求的用例，例如安全分析和基础设施监测。

`Elasticsearch 具有分布式的本质特征`。 Elasticsearch 中存储的文档分布在不同的容器中，这些容器称为分片，可以进行复制以提供数据冗余副本，以防发生硬件故障。Elasticsearch 的分布式特性使得它可以扩展至数百台（甚至数千台）服务器，并处理 PB 量级的数据。

`Elasticsearch 包含一系列广泛的功能`。 除了速度、可扩展性和弹性等优势以外，Elasticsearch 还有大量强大的内置功能（例如数据汇总和索引生命周期管理），可以方便用户更加高效地存储和搜索数据。

`Elastic Stack 简化了数据采集、可视化和报告过程`。 通过与 Beats 和 Logstash 进行集成，用户能够在向 Elasticsearch 中索引数据之前轻松地处理数据。同时，Kibana 不仅可针对 Elasticsearch 数据提供实时可视化，同时还提供 UI 以便用户快速访问应用程序性能监测 (APM)、日志和基础设施指标等数据。

## 环境
- CentOS7.4 系统
- Docker version 18.06.1-ce
- docker-compose version 1.22.0
- 部署单节点 ELK

## 调整系统配置 [3]
- 内核 `vm.max_map_count` 至少设置为 `262144` 

    ```bash
    # 设置内核参数
    $ echo "vm.max_map_count=262144" >> /etc/sysctl.conf

    # 生效设置
    $ sysctl -p

    # 重启 docker，让内核参数对docker服务生效
    $ systemctl restart docker
    ```

- 默认情况下，Elasticsearch 使用 uid:gid（1000:1000）作为容器内的运行用户，如果把数据挂载到宿主机目录中，需要修改权限。

- 设置 nofile 和 nproc 的 ulimit 值为 65535
    ```bash
    $ vim /etc/security/limits.conf

    root soft nofile 65535
    root hard nofile 65535
    * soft nofile 65535
    * hard nofile 65535
    ```

- 为了性能和节点稳定性，需要禁用 Swap。docker 中使用 `-e "bootstrap.memory_lock=true" --ulimit memlock=-1:-1`。

- 使用 `ES_JAVA_OPTS` 环境变量来设置堆大小。例如，docker 中配置 `16GB` 的使用方法 `-e ES_JAVA_OPTS="-Xms16g -Xmx16g"`。

- 如果您使用 `devicemapper` 存储驱动程序，请确保未使用默认 `loop-lvm` 模式。配置 `docker-engine` 改为使用 `direct-lvm`。

- 默认的 `json` 文件日志记录驱动程序不适用于生产环境。

- 生产环境磁盘推荐使用 `SSD`

## 部署 Elasticsearch
```bash
# 创建存储目录
$ mkdir -p /data/ELKStack && cd /data/ELKStack
$ mkdir -p /data/ELKStack/elasticsearch-data /data/ELKStack/elasticsearch/package

# 修改权限 
$ chown -R 1000:1000 /data/ELKStack/elasticsearch-data /data/ELKStack/elasticsearch

# 编辑 docker-compose 配置
$ vim ./elasticsearch/docker-compose.yml
```
```yaml
version: '2'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:6.3.1
    container_name: elasticsearch
    environment:
      - cluster.name=docker-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms12000m -Xmx12000m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65536
        hard: 65536
    mem_limit: 16000m
    cap_add:
      - IPC_LOCK
    restart: always
    # 设置 docker host 网络模式
    network_mode: "host"
    #network_mode: "bridge"
    #ports:
    #  - "9200:9200"
    #  - "9300:9300"
    volumes:
       - /data/ELKStack/elasticsearch-data:/usr/share/elasticsearch/data
       - /data/ELKStack/elasticsearch/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml
       - /data/ELKStack/elasticsearch/package:/tmp/package
    user: elasticsearch
    # 支持 sql 查询
    command: bash -c "elasticsearch-plugin install file:///tmp/package/elasticsearch-sql-6.3.1.1.zip; elasticsearch"
```

```bash
# 编辑 elasticsearch.yml 配置
$ vim /data/ELKStack/elasticsearch/elasticsearch.yml
```
```yaml
cluster.name: "docker-cluster"
network.host: 0.0.0.0

discovery.zen.minimum_master_nodes: 1
http.port: 9200
transport.tcp.port: 9300
# 如果是多节点es，通过ping来健康检查
# discovery.zen.ping.unicast.hosts: ["172.16.1.3:9300", "172.16.1.4:9300"]
discovery.zen.fd.ping_timeout: 120s
discovery.zen.fd.ping_retries: 3
discovery.zen.fd.ping_interval: 30s
cluster.info.update.interval: 1m
xpack.security.enabled: false
indices.fielddata.cache.size:  20%
indices.breaker.total.limit: 60%
indices.recovery.max_bytes_per_sec: 100mb
indices.memory.index_buffer_size: 20%
script.painless.regex.enabled: true
```

```bash
# 启动 es
$ cd /data/ELKStack/elasticsearch
$ docker-compose up -d
```

## 部署 Kibana
```bash
# 创建目录并配置权限
$ mkdir -p /data/ELKStack/kibana-data /data/ELKStack/kibana
$ chown -R 1000:1000 /data/ELKStack/kibana-data /data/ELKStack/kibana

# 编辑 docker-compose.yml 配置
# vim /data/ELKStack/kibana/docker-compose.yml
```
```yaml
version: '2'
services:
  kibana:
    image: docker.elastic.co/kibana/kibana:6.3.1
    container_name: kibana
    restart: always
    network_mode: "bridge"
    mem_limit: 2000m
    environment:
      SERVER_NAME: kibana.example.com
    ports:
      - "5601:5601"
    external_links:
      - elasticsearch:elasticsearch
    volumes:
       - /data/ELKStack/kibana/kibana.yml:/usr/share/kibana/config/kibana.yml
       - /data/ELKStack/kibana-data:/usr/share/kibana/data
```

```bash
# 编辑 kibana.yml
$ vim /data/ELKStack/kibana/kibana.yml
```

```yaml
# Default Kibana configuration from kibana-docker.
server.name: kibana
server.host: "0"
elasticsearch.url: http://elasticsearch:9200
xpack.security.enabled: false
```

```bash
# 启动 kibana
$ cd /data/ELKStack/kibana
$ docker-compose up -d
```


## 部署 Logstash
```bash
# 创建目录并配置权限
$ mkdir -p /data/ELKStack/logstash/conf /data/ELKStack/logstash/plugins
$ chown -R 1000:1000 /data/ELKStack/logstash

# 编辑 docker-compose.yml 配置
# vim /data/ELKStack/logstash/docker-compose.yml
```
```yaml
version: '2'
services:
  logstash:
    image: docker.elastic.co/logstash/logstash:6.3.1
    container_name: logstash
    restart: always
    network_mode: "bridge"
    mem_limit: 1300m
    ports:
      - 5044:5044
    volumes:
      - /data/ELKStack/logstash/conf:/config-dir
      - /data/ELKStack/logstash/plugins:/tmp/plugins
      - /data/ELKStack/logstash/logstash.yml:/usr/share/logstash/config/logstash.yml
      - /etc/localtime:/etc/localtime
    external_links:
      - elasticsearch:elasticsearch
    user: logstash
    command: bash -c "logstash -f /config-dir --config.reload.automatic"
```

```bash
# 编辑 logstash.yml
$ vim /data/ELKStack/logstash/logstash.yml
```
```yaml
http.host: "0.0.0.0"
```

```bash
# 配置 logstash conf
$ cd /data/ELKStack/logstash/conf

$ # vim 01-input.conf

input {
  beats {
    port => 5044
  }

}

$ vim 02-output.conf

output {
  if [type] =~ "nginx" {
    #stdout { codec => rubydebug }
    elasticsearch {
      hosts => ["elasticsearch:9200"]
      index => "%{type}-%{+YYYY.MM.dd}"
      #user => user
      #password => password
    }
  }
  else {
    #stdout { codec => rubydebug }
    elasticsearch {
      hosts => ["elasticsearch:9200"]
      index => "logstash-%{+YYYY.MM.dd}"
      #user => user
      #password => password
    }
  }
}

$ vim 03-filter-log.conf

filter {

   geoip {
       source => "[json][ip]"
       target =>"geoip"
       database =>"/tmp/plugins/GeoLite2-City.mmdb"
       add_field => ["[geoip][coordinates]", "%{[geoip][longitude]}" ] # 添加字段coordinates，值为经度
       add_field => ["[geoip][coordinates]", "%{[geoip][latitude]}" ] # 添加字段coordinates，值为纬度
   }

   mutate {
      convert => { "[json][code]" => "string" }
      convert => { "[geoip][coordinates]" => "float" }
   }
}
```

```bash
# 启动 logstash
$ cd /data/ELKStack/logstash
$ docker-compose up -d
```

## elasticsearch 索引定时清理

- elasticsearch-curator 安装
    ```bash
    # 安装 curator 源
    $ rpm --import https://packages.elastic.co/GPG-KEY-elasticsearch

    # 编辑 curator yum 源配置
    $ vim /etc/yum.repos.d/curator.repo

    [curator-5]
    name=CentOS/RHEL 7 repository for Elasticsearch Curator 5.x packages
    baseurl=https://packages.elastic.co/curator/5/centos/7
    gpgcheck=1
    gpgkey=https://packages.elastic.co/GPG-KEY-elasticsearch
    enabled=1

    # 安装 curator
    $ yum install elasticsearch-curator -y
    ```

- 配置 config.yml
    ```bash
    $ mkdir -p /data/ELKStack/curator
    $ vim /data/ELKStack/curator/config.yml
    ```
    ```yaml
    lient:
     hosts:
       - 172.16.1.3
     port: 9200
     url_prefix:
     use_ssl: False
     certificate:
     client_cert:
     client_key:
     ssl_no_validate: False
     http_auth:
     timeout: 150
     master_only: False

    logging:
     loglevel: INFO
     logfile:
     logformat: default
     blacklist: ['elasticsearch', 'urllib3']
    ```

- 配置 action.yml 清理规则
    ```bash
    $ vim /data/ELKStack/curator/action.yml
    ```
    ```yaml
    actions:
      1:
        action: delete_indices
        description: >-
          Delete indices older than 60 days. Ignore the error if the    filter does not result in an actionable list of indices    (ignore_empty_list) and exit cleanly.
        options:
          ignore_empty_list: True
          disable_action: False
        filters:
        - filtertype: pattern
          kind: regex
          # 保留 kibana|json|monitoring|metadata 不被清理
          value: '^((?!(kibana|json|monitoring|metadata)).)*$'
        - filtertype: age
          source: creation_date
          direction: older
          #timestring: '%Yi-%m-%d'
          unit: days
          unit_count: 60
    ```

- 设置计划任务
    ```bash
    $ crontab -e

    0 0 * * * /usr/bin/curator --config /data/ELKStack/curator/config.yml /data/ELKStack/curator/action.yml 1>> /tmp/curator.log 2>&1
    ```

# 参考链接
- [1]https://www.elastic.co/cn/what-is/elk-stack
- [2]https://www.elastic.co/cn/what-is/elasticsearch
- [3]https://www.elastic.co/guide/en/elasticsearch/reference/6.3/docker.html