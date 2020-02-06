## Elasticsearch 简介

`Elasticsearch` 是一个分布式的开源搜索和分析引擎，适用于所有类型的数据，包括文本、数字、地理空间、结构化和非结构化数据。

Elasticsearch 虽然可以通过 `RESTful API` 操作，但是使用还是比较麻烦，下文介绍几个常用的可视化管理工具。

`PS`: 下面是Elasticsearch 部署 与 RESTful API 常用操作

- [Docker-compose 部署 ELK](https://www.yp14.cn/2019/12/16/Docker-compose-%E9%83%A8%E7%BD%B2-ELK/)
- [Elasticsearch RESTful API 常用操作](https://www.yp14.cn/2019/11/25/Elasticsearch-RESTful-API-%E5%B8%B8%E7%94%A8%E6%93%8D%E4%BD%9C/)


## ElasticHD

`ElasticHD` 支持 `ES监控`、`实时搜索`、`Index template快捷替换修改`、`索引列表信息查看`， `SQL converts to DSL`工具等。是一款非常伴的 Dashboard。

`项目地址`：https://github.com/360EntSecGroup-Skylar/ElasticHD

`Docker 安装`：

```bash
$ docker run -p 9200:9200 -d --name elasticsearch elasticsearch
$ docker run -p 9800:9800 -d --link elasticsearch:demo containerize/elastichd

Open http://localhost:9800 in Browser
Connect with http://demo:9200
```

`ElasticHD Dashboard 展示`：

![](/img/Elastic-HD-Dashboard-1.png)

![](/img/Elastic-HD-Dashboard-7.png)


## elasticsearch-head

`elasticsearch-head` 是用于监控 Elasticsearch 状态的客户端插件，包括数据可视化、执行增删改查操作等。

`项目地址`：https://github.com/mobz/elasticsearch-head

`Docker 安装`：

- Elasticsearch 5.x 安装: docker run -p 9100:9100 mobz/elasticsearch-head:5
- Elasticsearch 2.x 安装: docker run -p 9100:9100 mobz/elasticsearch-head:2
- Elasticsearch 1.x 安装: docker run -p 9100:9100 mobz/elasticsearch-head:1
- alpine 镜像 mobz/elasticsearch-head:5-alpine

安装完成后，使用浏览器打开 `http://localhost:9100/`

`Google Chrome 浏览器插件安装`：直接在谷歌浏览器插件中心搜索 `ElasticSearch Head`，搜索到安装好就可以直接使用，简单方便。

`elasticsearch-head Dashboard 展示`：

![](/img/elasticsearch-head.png)

## Dejavu

`Dejavu` 也是一个 Elasticsearch的 Web UI 工具，其 UI界面更符合当下主流的前端页面风格，因此使用起来很方便。

`项目地址`：https://github.com/appbaseio/dejavu/

`Docker 安装`：

```bash
$ docker run -p 1358:1358 -d appbaseio/dejavu

open http://localhost:1358/
```

`Dejavu Dashboard 展示`：

- 数据预览页面非常直观，索引/类型/文档 显示得一清二楚

    ![](/img/Dejavu-1.png)


- 视觉过滤器
    ![](/img/Dejavu-2.gif)
    整理数据，直观地查找信息，隐藏不相关的数据并使一切有意义。对于所有本机数据类型，我们都有。全局搜索栏允许您在数据集中执行文本搜索。

    此外，任何过滤的视图都可以导出为JSON或CSV文件。

- 现代UI元素
    ![](/img/Dejavu-3.gif)

    索引中包含成千上万的文档并不少见。Dejavu支持分页视图，该视图还允许您更改页面大小。

    Dejavu还支持浏览来自多个索引和类型的数据，可以单独或通过批量查询来更新数据。还支持删除。

- 导入 JSON 或 CSV 数据

   ![](/img/Dejavu-4.gif)
    导入器视图允许通过指导数据映射配置将CSV或JSON数据直接导入到Elasticsearch中。

## 总结

上面例举三个 Elasticsearch 可视化工具，没有具体细说，这篇文章只作为抛砖引玉，具体使用读者可以慢慢研究。

## 参考链接

- https://github.com/360EntSecGroup-Skylar/ElasticHD
- https://github.com/mobz/elasticsearch-head
- https://github.com/appbaseio/dejavu