## 前言

阿里云监控为云上用户提供常用云产品的监控数据和用户自定义上报的监控数据。在可视化展示层面，除了在云监控控制台查看监控图表外，您还可以将云监控的数据添加到Grafana中展示。

## 阿里云SLB监控展示

![](/img/slb-monitoring.png)


## Grafana 部署 aliyun-cms-grafana 插件

1、本文略过 Grafana 部署

2、安装 aliyun-cms-grafana 插件

假如 Grafana 插件安装目录为 `/var/lib/grafana/plugins/`

执行以下命令安装插件

```bash
$ cd /var/lib/grafana/plugins/
$ git clone https://github.com/aliyun/aliyun-cms-grafana.git
```

3、重启 Grafana 服务

```bash
# CentOS6 rpm 安装可以使用下面方式重启
$ service grafana-server restart

# CentOS7 rpm 安装可以使用下面方式重启
$ systemctl restart grafana-server

# k8s 部署 Grafana 可以直接删除 Grafana Pod，k8s会自动在创建一个新的 Pod
```
> 注意：此插件版本目前不支持对监控数据设置报警。

## Grafana 中配置 aliyun-cms-grafana 数据源

1、登录 Grafana

2、单击左上方的 `Configuration`，在弹出的列表中选 `Data Sources`

![](/img/grafna-1.png)

3、进入 `Data Sources` 页面，单击右上方的 `Add data source`，添加新的数据源

![](/img/grafana-2.png)

4、填写云监控数据源的配置项

配置项 | 配置内容
---|---
Name | 请您根据所需自定义一个新数据源的名称
type | Type请选择CMS Grafana Service
URL  | URL样例：http://metrics.cn-shanghai.aliyuncs.com，metrics是Project名称，cn-shanghai.aliyuncs.com是Project所在地域Endpoint，在配置数据源时，需要替换成自己的Project和Region地址。
Access | 使用默认值即可
Auth | 使用默认值即可
cloudmonitor service details | 分别填写具备读取权限的AccessKey信息。建议使用子账号的AccessKey

> 不同域选择请参考[云监控接入地址](https://help.aliyun.com/document_detail/28616.html?spm=a2c4g.11186623.2.10.74283646MuJPVZ#section-xf3-lbv-zdb)

配置示例如下图：

![](/img/grafana-3.png)

最后点击 `Save & Test` 测试是否连接成功。

## 监控阿里云 SLB

Grafana Dashboard 需要自己编写，作者这里已编写一个 `SLB模板` 监控，获取 `SLB模板` 请在微信公众号 `YP小站` 后台回复 `SLB` 获取下载链接。

## 总结

`aliyun-cms-grafana` 插件可以通过 Grafana 展示阿里云监控 ECS、SLB、RDS等监控，本文只例举展示 SLB 监控。更多使用方法请参考 https://help.aliyun.com/document_detail/109434.html?spm=5176.10695662.1996646101.searchclickresult.4c5b44e3RrXV6v&aly_as=iKwLOy4Lw 链接。

> aliyun-cms-grafana 项目地址 https://github.com/aliyun/aliyun-cms-grafana

## 参考链接

- https://help.aliyun.com/document_detail/109434.html?spm=5176.10695662.1996646101.searchclickresult.4c5b44e3RrXV6v&aly_as=iKwLOy4Lw
- https://github.com/aliyun/aliyun-cms-grafana