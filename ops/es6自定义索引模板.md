#### 一、查询索引模板命令
```
# 查询es中所有索引模板名称
curl localhost:9200/_template  | jq keys

# 查询一个索引模板详细信息
curl localhost:9200/_template/logstash  | jq
```


#### 二、添加自定义nginx索引模板，因为索引名不使用logstash，所以需要自定义

```
# 参考链接
# https://github.com/logstash-plugins/logstash-output-elasticsearch/blob/7.x/lib/logstash/outputs/elasticsearch/elasticsearch-template-es6x.json
# https://www.jianshu.com/p/1f67e4436c37

curl -XPUT "http://localhost:9200/_template/nginx_template" -H 'Content-Type: application/json' -d'
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
