## ELK 7.10 搭建

ELK 7.10 搭建请参考 [容器部署ELK7.10-适用于生产](https://www.yp14.cn/2021/01/07/%E5%AE%B9%E5%99%A8%E9%83%A8%E7%BD%B2ELK7-10-%E9%80%82%E7%94%A8%E4%BA%8E%E7%94%9F%E4%BA%A7/)

## Grafana展示Nginx图表

![](../img/grafana-nginx-access-1.png)

## Nginx 日志字段配置

> 注意：请确保 nginx 使用该字段，Nginx `Key名称`如果有修改，`Logstash` 和 `Grafana模板` 需要根据自己Nginx字段来修改

```json
log_format aka_logs
    '{"@timestamp":"$time_iso8601",'
    '"host":"$hostname",'
    '"server_ip":"$server_addr",'
    '"client_ip":"$remote_addr",'
    '"xff":"$http_x_forwarded_for",'
    '"domain":"$host",'
    '"url":"$uri",'
    '"referer":"$http_referer",'
    '"args":"$args",'
    '"upstreamtime":"$upstream_response_time",'
    '"responsetime":"$request_time",'
    '"request_method":"$request_method",'
    '"status":"$status",'
    '"size":"$body_bytes_sent",'
    '"request_body":"$request_body",'
    '"request_length":"$request_length",'
    '"protocol":"$server_protocol",'
    '"upstreamhost":"$upstream_addr",'
    '"file_dir":"$request_filename",'
    '"http_user_agent":"$http_user_agent"'
  '}';
```

## Filebeat 配置

> Filebeat Version 7.10

```bash
#=========================== Filebeat inputs =============================
filebeat.inputs:                   # inputs为复数，表名type可以有多个
- type: log                        # 输入类型
  access:
  enabled: true                    # 启用这个type配置
  # 日志是json开启这个
  json.keys_under_root: true       # 默认这个值是FALSE的，也就是我们的json日志解析后会被放在json键上。设为TRUE，所有的keys就会被放到根节点
  json.overwrite_keys: true        # 是否要覆盖原有的key，这是关键配置，将keys_under_root设为TRUE后，再将overwrite_keys也设为TRUE，就能把filebeat默认的key值给覆盖
  max_bytes: 20480                 # 单条日志的大小限制,建议限制(默认为10M,queue.mem.events * max_bytes 将是占有内存的一部分)
  paths:
    - /var/log/nginx/access.log    # 监控nginx 的access日志

  fields:                          # 额外的字段
    source: nginx-access           # 自定义source字段，用于es建议索引（字段名小写，我记得大写好像不行）

# 自定义es的索引需要把ilm设置为false
setup.ilm.enabled: false

#-------------------------- Kafka output ------------------------------
output.kafka:            # 输出到kafka
  enabled: true          # 该output配置是否启用
  hosts: ["host1:9092", "host2:9092", "host3:9092"]  # kafka节点列表
  topic: "elk-%{[fields.source]}"   # kafka会创建该topic，然后logstash(可以过滤修改)会传给es作为索引名称
  partition.hash:
    reachable_only: true # 是否只发往可达分区
  compression: gzip      # 压缩
  max_message_bytes: 1000000  # Event最大字节数。默认1000000。应小于等于kafka broker message.max.bytes值
  required_acks: 1  # kafka ack等级
  worker: 1  # kafka output的最大并发数
  bulk_max_size: 2048    # 单次发往kafka的最大事件数
logging.to_files: true   # 输出所有日志到file，默认true， 达到日志文件大小限制时，日志文件会自动限制替换，详细配置：https://www.cnblogs.com/qinwengang/p/10982424.html
close_older: 30m         # 如果一个文件在某个时间段内没有发生过更新，则关闭监控的文件handle。默认1h
force_close_files: false # 这个选项关闭一个文件,当文件名称的变化。只在window建议为true

# 没有新日志采集后多长时间关闭文件句柄，默认5分钟，设置成1分钟，加快文件句柄关闭
close_inactive: 1m

# 传输了3h后荏没有传输完成的话就强行关闭文件句柄，这个配置项是解决以上案例问题的key point
close_timeout: 3h

# 这个配置项也应该配置上，默认值是0表示不清理，不清理的意思是采集过的文件描述在registry文件里永不清理，在运行一段时间后，registry会变大，可能会带来问题
clean_inactive: 72h

# 设置了clean_inactive后就需要设置ignore_older，且要保证ignore_older < clean_inactive
ignore_older: 70h

# 限制 CPU和内存资源
max_procs: 1 # 限制一个CPU核心,避免过多抢占业务资源
queue.mem.events: 256 # 存储于内存队列的事件数，排队发送 (默认4096)
queue.mem.flush.min_events: 128 # 小于 queue.mem.events ,增加此值可提高吞吐量 (默认值2048)
```

## Logstash 配置

> Logstash Version 7.10

```bash
$ vim 01-input.conf

input {                                        # 输入组件
    kafka {                                    # 从kafka消费数据
        bootstrap_servers => ["host1:9092,host2:9092,host3:9092"]
        #topics => "%{[@metadata][topic]}"     # 使用kafka传过来的topic
        topics_pattern => "elk-.*"             # 使用正则匹配topic
        codec => "json"                        # 数据格式
        consumer_threads => 3                  # 消费线程数量
        decorate_events => true                # 可向事件添加Kafka元数据，比如主题、消息大小的选项，这将向logstash事件中添加一个名为kafka的字段
        auto_offset_reset => "latest"          # 自动重置偏移量到最新的偏移量
        group_id => "logstash-groups1"         # 消费组ID，多个有相同group_id的logstash实例为一个消费组
        client_id => "logstash1"               # 客户端ID
        fetch_max_wait_ms => "1000"            # 指当没有足够的数据立即满足fetch_min_bytes时，服务器在回答fetch请求之前将阻塞的最长时间        
  }
}

$ vim 02-output.conf

output {                                       # 输出组件
    elasticsearch {
        # Logstash输出到es
        hosts => ["host1:9200", "host2:9200", "host3:9200"]
        index => "%{[fields][source]}-%{+YYYY-MM-dd}"      # 直接在日志中匹配，索引会去掉elk
        user => "elastic"
        password => "xxxxxx"
    }
    #stdout {
    #    codec => rubydebug
    #}
}

$ vim 03-filter.conf

filter {
   # 因为Nginx前端有负载均衡，$remote_addr 字段不是用户真实ip地址
   # 本例获取 $http_x_forwarded_for 字段，$http_x_forwarded_for 字段第一个ip地址就是用户真实ip地址
   # 再nginx字段基础上添加 real_remote_addr 字段，用于存储用户真实ip地址
   if ([fields][source] =~ "nginx-access") {
     if "," in [xff] {
        mutate {
          split => ["xff", ","]
          add_field => { "real_remote_addr" => "%{[xff][0]}" }
        }
     } else if ([xff] == "-") {
        mutate {
          add_field => { "real_remote_addr" => "-" }
        }
     } else {
        mutate {
          add_field => { "real_remote_addr" => "%{xff}" }
        }
     }

     geoip {
       target => "geoip"
       source => "real_remote_addr"
       database => "/usr/share/logstash/data/GeoLite2-City/GeoLite2-City.mmdb"
       add_field => [ "[geoip][coordinates]", "%{[geoip][longitude]}" ]
       add_field => [ "[geoip][coordinates]", "%{[geoip][latitude]}" ]
       # 去掉显示 geoip 显示的多余信息
       remove_field => ["[geoip][latitude]", "[geoip][longitude]", "[geoip][country_code]", "[geoip][country_code2]", "[geoip][country_code3]", "[geoip][timezone]", "[geoip][continent_code]", "[geoip][region_code]"]
     }

     mutate {
       convert => {
         "[size]" => "integer"
         "[status]" => "integer"
         "[responsetime]" => "float"
         "[upstreamtime]" => "float"
         "[geoip][coordinates]" => "float"
       }
     }

     # 根据http_user_agent来自动处理区分用户客户端系统与版本
     useragent {
       source => "http_user_agent"
       target => "ua"
       # 过滤useragent没用的字段
       remove_field => [ "[ua][minor]","[ua][major]","[ua][build]","[ua][patch]","[ua][os_minor]","[ua][os_major]" ]
     }
   }
}
```

## Grafana Nginx 图表

获取 `Grafana Nginx 图表` 链接下载，公众号后台回复 `g-nginx-1` 下载。

> 注意：如果 `Logstash` 配置按照本文来配，需要 Grafana 图表中 `client_ip` 字段替换为 `real_remote_addr` 字段。

## 参考链接

- https://grafana.com/grafana/dashboards/11190