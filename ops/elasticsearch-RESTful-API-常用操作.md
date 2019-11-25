## 什么是 ElasticSearch
`ElasticSearch` 是一个基于`Lucene`的搜索服务器。它提供了一个分布式多用户能力的`全文搜索引擎`，基于`RESTful web`接口。Elasticsearch是用`Java语言`开发的，并作为`Apache许可条款`下的开放源码发布，是一种流行的`企业级搜索引擎`。

## HTTP RESTful API 常用操作

- 查询和过滤上下文
```json
$ curl -X GET "localhost:9200/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { 
    "bool": { 
      "must": [
        { "match": { "title":   "Search"        }}, 
        { "match": { "content": "Elasticsearch" }}  
      ],
      "filter": [ 
        { "term":  { "status": "published" }}, 
        { "range": { "publish_date": { "gte": "2019-01-01" }}} 
      ]
    }
  }
}
'
```
- 查询 ES 中所有`索引模板名称`
```bash
$ curl localhost:9200/_template  | jq keys
```

- 查询一个索引模板详细信息
```bash
$ curl localhost:9200/_template/logstash  | jq
```

- 查询 ES 集群健康状态
```bash
$  curl -s -XGET 'http://localhost:9200/_cluster/health?pretty'
```

- 查询 ES 集群设置
```bash
curl -s -XGET 'http://localhost:9200/_cluster/settings' | jq
```

- 下架 ES 集群中一个节点
```bash
$ curl -X PUT "http://localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "transient" : {
    "cluster.routing.allocation.exclude._name" : "node-3"
  }
}'

# 除了_name 之外, 还可以用_ip、_host进行匹配
```

- 设置 discovery.zen.minimum_master_nodes
```bash
# 法定个数就是 ( master 候选节点个数 / 2) + 1 ，默认为 1
$ curl -X PUT "http://localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
    "persistent" : {
        "discovery.zen.minimum_master_nodes" : 2
    }
}'
```

- 增加一个`default_template`模板，设置副本为`0` (`默认副本为1`)，不推介这样做，集群没有备份数据
```bash
$ curl -XPUT "localhost:9200/_template/default_template" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["*"],
  "settings": {
    "index": {
      "number_of_replicas": 0
    }
  }
}'
```

- 把现有的 ES 集群中 `index` 副本去掉，不推介这样做，集群没有备份数据
```bash
$ curl -X PUT "localhost:9200/_all/_settings" -H 'Content-Type: application/json' -d'
{
    "index" : {
        "number_of_replicas" : 0
    }
}'
```

- 添加`自定义nginx`索引模板
```json
$ curl -XPUT "http://localhost:9200/_template/nginx_template" -H 'Content-Type: application/json' -d'
{
  "template" : "*nginx*",
  "version" : 60001,
  "settings" : {
    "index.refresh_interval" : "5s"
  },
  "mappings" : {
    "_default_" : {
      "dynamic_templates" : [ {
        "message_field" : {
          "path_match" : "message",
          "match_mapping_type" : "string",
          "mapping" : {
            "type" : "text",
            "norms" : false
          }
        }
      }, {
        "string_fields" : {
          "match" : "*",
          "match_mapping_type" : "string",
          "mapping" : {
            "type" : "text", "norms" : false,
            "fields" : {
              "keyword" : { "type": "keyword", "ignore_above": 256 }
            }
          }
        }
      } ],
      "properties" : {
        "@timestamp": { "type": "date"},
        "@version": { "type": "keyword"},
        "geoip"  : {
          "dynamic": true,
          "properties" : {
            "ip": { "type": "ip" },
            "location" : { "type" : "geo_point" },
            "latitude" : { "type" : "half_float" },
            "longitude" : { "type" : "half_float" }
          }
        }
      }
    }
  }
}
'
```

## elasticdump 导出数据

- 导出`kubernetes pod name`名为`test` 并且 `log` 字段中匹配`access`数据
```json
$ elasticdump \
  --input=http://localhost:9200/logstash-2019.01.06 \
  --output=/tmp/test-2019-01-06-query.json \
  --limit=10000 \
  --searchBody '{
  "query": {
    "bool": {
      "must": [
        {
          "match": { "kubernetes.pod_name": "test" },
          "match": { "log": "*access*" }}
      ],
      "filter": {
        "range": {
          "@timestamp": {
            "gte": "2019-01-06T00:00:00.000+00:00",
            "lt":  "2019-01-06T10:00:00.000+00:00"
          }
        }
      }
    }
  }
}'
```