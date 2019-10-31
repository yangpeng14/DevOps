#### 一、包含查询match和对时间进行范围查询range的DSL

```
需要从message中找出包含 http-apr-8080-exec，并且限定时间范围在中午12点到13点之间的结果，找了好久终于编出了如下语句，做一个记录。

GET /_search
{
  "_source": ["message"],
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "message": "http-apr-8080-exec"
          }
        }
      ],
      "filter": {
        "range": {
          "@timestamp": {
            "gte": "2018-06-15T12:00:00.000+0800",
            "lt":  "2018-06-15T13:00:00.000+0800"
          }
        }
      }
    }
  },
  "sort": [ { "@timestamp": { "order": "desc" } } ],
  "size": 5000
}

参考链接：https://www.elastic.co/guide/en/elasticsearch/reference/current/query-filter-context.html
```

#### 二、elasticdump 导出数据
```
elasticdump \
  --input=http://172.16.0.195:9200/logstash-2019.01.06 \
  --output=sls-2019-01-06-query-1.json \
  --limit=10000 \
  --searchBody '{
  "query": {
    "bool": {
      "must": [
        {
          "match": { "kubernetes.pod_name": "sls-backend-production" },
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

#### 三、Bool Query

```
POST _search
{
  "query": {
    "bool" : {
      "must" : {
        "term" : { "user" : "kimchy" }
      },
      "filter": {
        "term" : { "tag" : "tech" }
      },
      "must_not" : {
        "range" : {
          "age" : { "gte" : 10, "lte" : 20 }
        }
      },
      "should" : [
        { "term" : { "tag" : "wow" } },
        { "term" : { "tag" : "elasticsearch" } }
      ],
      "minimum_should_match" : 1,
      "boost" : 1.0
    }
  }
}

参考链接：https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html
```

#### 四、查询索引模板命令
```
# 查询es中所有索引模板名称
curl localhost:9200/_template  | jq keys

# 查询一个索引模板详细信息
curl localhost:9200/_template/logstash  | jq
```
