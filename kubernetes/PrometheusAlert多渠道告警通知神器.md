## Prometheus Alert 简介

`Prometheus Alert` 是开源的运维告警中心消息转发系统，支持主流的监控系统 `Prometheus`，日志系统 `Graylog` 和数据可视化系统 `Grafana` 发出的预警消息。通知渠道支持钉钉、微信、华为云短信、腾讯云短信、腾讯云电话、阿里云短信、阿里云电话等。

![](/img/PrometheusAlert.png)

## PrometheusAlert 特性

- 支持多种消息来源，目前主要有prometheus、graylog2、graylog3、grafana
- 支持多种类型的发送目标，支持钉钉、微信、腾讯短信、腾讯语音、华为短信
- 针对Prometheus增加了告警级别，并且支持按照不同级别发送消息到不同目标对象
- 简化Prometheus分组配置，支持按照具体消息发送到单个或多个接收方
- 增加手机号码配置项，和号码自动轮询配置，可固定发送给单一个人告警信息，也可以通过自动轮询的方式发送到多个人员且支持按照不同日期发送到不同人员
- 增加 Dashboard，暂时支持测试配置是否正确

## 部署方法

`PrometheusAlert` 可以部署在本地和云平台上，支持windows、linux、公有云、私有云、混合云、容器和kubernetes。你可以根据实际场景或需求，选择相应的方式来部署 `PrometheusAlert`：

- 容器部署

```bash
$ git clone https://github.com/feiyu563/PrometheusAlert.git
$ mkdir /etc/prometheusalert-center/
$ cp PrometheusAlert/conf/app.conf /etc/prometheusalert-center/
$ docker run -d -p 8080:8080 -v /etc/prometheusalert-center:/app/conf --name prometheusalert-center feiyu563/prometheus-alert:latest
```

- Linux 系统部署

```bash
$ git clone https://github.com/feiyu563/PrometheusAlert.git
$ cd PrometheusAlert/example/linux/

# 后台运行请执行 nohup ./PrometheusAlert &
$ ./PrometheusAlert
```

- Windows 系统部署

```bash
$ git clone https://github.com/feiyu563/PrometheusAlert.git
$ cd PrometheusAlert/example/windows/

双击运行 PrometheusAlert.exe 即可
```

- kubernetes 部署

```bash
$ kubectl app -n monitoring -f https://raw.githubusercontent.com/feiyu563/PrometheusAlert/master/example/kubernetes/PrometheusAlert-Deployment.yaml
```

- Helm 部署

```bash
$ git clone https://github.com/feiyu563/PrometheusAlert.git
$ cd PrometheusAlert/example/helm/prometheusalert

# 如需修改配置文件,请更新 config 中的 app.conf
$ helm install -n monitoring .
```

> 启动后可使用浏览器打开测试地址: http://127.0.0.1:8080

## 配置说明

`PrometheusAlert` 暂时提供以下几类接口,分别对应各自接入端

- prometheus 接口

    - /prometheus/alert

- grafana 接口

接口路由 | 解释
---|---
/grafana/phone | 腾讯云电话接口(v3.0版本将废弃)
/grafana/dingding | 钉钉接口
/grafana/weixin | 微信接口
/grafana/txdx | 腾讯云短信接口
/grafana/txdh | 腾讯云电话接口
/grafana/hwdx | 华为云短信接口
/grafana/alydx | 阿里云短信接口
/grafana/alydh | 阿里云电话接口

- graylog2 接口

接口路由 | 解释
---|---
/graylog2/phone | 腾讯云电话接口(v3.0版本将废弃)
/graylog2/dingding | 钉钉接口
/graylog2/weixin | 微信接口
/graylog2/txdx | 腾讯云短信接口
/graylog2/txdh | 腾讯云电话接口
/graylog2/hwdx | 华为云短信接口
/graylog2/alydx | 阿里云短信接口
/graylog2/alydh | 阿里云电话接口

- graylog3 接口

接口路由 | 解释
---|---
/graylog3/phone | 腾讯云电话接口(v3.0版本将废弃)
/graylog3/dingding | 钉钉接口
/graylog3/weixin | 微信接口
/graylog3/txdx | 腾讯云短信接口
/graylog3/txdh | 腾讯云电话接口
/graylog3/hwdx | 华为云短信接口
/graylog3/alydx | 阿里云短信接口
/graylog3/alydh | 阿里云电话接口

- 语音短信回调接口

    - /tengxun/status

## 接入配置

### Prometheus 接入配置

在 Prometheus Alertmanager 中启用 Webhook，可参考如下模板：

```yaml
global:
  resolve_timeout: 5m
route:
  group_by: ['instance']
  group_wait: 10m
  group_interval: 10s
  repeat_interval: 10m
  receiver: 'web.hook.prometheusalert'
receivers:
- name: 'web.hook.prometheusalert'
  webhook_configs:
  - url: 'http://[prometheusalert_url]:8080/prometheus/alert'
```

Prometheus Server 的告警rules配置，可参考如下模板：

```yaml
groups:
 1. name: node_alert
  rules:
 2. alert: 主机CPU告警
    expr: node_load1 > 1
    labels:
      name: prometheusalertcenter
      level: 3   #告警级别,告警级别定义 0 信息,1 警告,2 一般严重,3 严重,4 灾难
    annotations:
      description: "{{ $labels.instance }} CPU load占用过高"  #告警信息
      mobile: 15888888881,15888888882,15888888883  #告警发送目标手机号(需要设置电话和短信告警级别)
      ddurl: "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx,https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" #支持添加多个钉钉机器人告警,用,号分割即可,如果留空或者未填写,则默认发送到配置文件中填写的钉钉器人地址
      wxurl: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxx-xxxxxx-xxxxxx-xxxxxx,https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx-xxxx-xxxxxxx-xxxxx" #支持添加多个企业微信机器人告警,用,号分割即可,如果留空或者未填写,则默认发送到配置文件中填写的企业微信机器人地址
```

最终告警效果：

![](/img/prometheus-11.png)


其它接入，请参考 https://github.com/feiyu563/PrometheusAlert/blob/master/README.MD

## 配置文件解析

```
#---------------------↓全局配置-----------------------
appname = PrometheusAlert
#监听端口
httpport = 8080
runmode = dev
#开启JSON请求
copyrequestbody = true
#告警消息标题
title=NX-TEST
#链接到告警平台地址
GraylogAlerturl=http://graylog.org
#logo图标地址
logourl=https://raw.githubusercontent.com/feiyu563/PrometheusAlert/master/doc/alert-center.png
#短信告警级别(等于3就进行短信告警) 告警级别定义 0 信息,1 警告,2 一般严重,3 严重,4 灾难
messagelevel=3
#电话告警级别(等于4就进行语音告警) 告警级别定义 0 信息,1 警告,2 一般严重,3 严重,4 灾难
phonecalllevel=4
#默认拨打号码
defaultphone=15395105573
#故障恢复是否启用电话通知0为关闭,1为开启
phonecallresolved=1
#自动告警抑制(自动告警抑制是默认同一个告警源的告警信息只发送告警级别最高的第一条告警信息,其他消息默认屏蔽,这么做的目的是为了减少相同告警来源的消息数量,防止告警炸弹,0为关闭,1为开启)
silent=1

#---------------------↓webhook-----------------------
#是否开启钉钉告警通道,可同时开始多个通道0为关闭,1为开启
open-dingding=1
#默认钉钉机器人地址
ddurl=https://oapi.dingtalk.com/robot/send?access_token=xxxxx

#是否开启微信告警通道,可同时开始多个通道0为关闭,1为开启
open-weixin=1
#默认企业微信机器人地址
wxurl=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx

#---------------------↓腾讯云接口-----------------------
#是否开启腾讯云短信告警通道,可同时开始多个通道0为关闭,1为开启
open-txdx=0
#腾讯云短信接口key
TXY_DX_appkey=xxxxx
#腾讯云短信模版ID 腾讯云短信模版配置可参考 prometheus告警:{1}
TXY_DX_tpl_id=xxxxx
#腾讯云短信sdk app id
TXY_DX_sdkappid=xxxxx
#腾讯云短信签名 根据自己审核通过的签名来填写
TXY_DX_sign=腾讯云

#是否开启腾讯云电话告警通道,可同时开始多个通道0为关闭,1为开启
TXY_DH_open-txdh=0
#腾讯云电话接口key
TXY_DH_phonecallappkey=xxxxx
#腾讯云电话模版ID
TXY_DH_phonecalltpl_id=xxxxx
#腾讯云电话sdk app id
TXY_DH_phonecallsdkappid=xxxxx

#---------------------↓华为云接口-----------------------
#是否开启华为云短信告警通道,可同时开始多个通道0为关闭,1为开启
open-hwdx=0
#华为云短信接口key
HWY_DX_APP_Key=xxxxxxxxxxxxxxxxxxxxxx
#华为云短信接口Secret
HWY_DX_APP_Secret=xxxxxxxxxxxxxxxxxxxxxx
#华为云APP接入地址(端口接口地址)
HWY_DX_APP_Url=https://rtcsms.cn-north-1.myhuaweicloud.com:10743
#华为云短信模板ID
HWY_DX_Templateid=xxxxxxxxxxxxxxxxxxxxxx
#华为云签名名称，必须是已审核通过的，与模板类型一致的签名名称,按照自己的实际签名填写
HWY_DX_Signature=华为云
#华为云签名通道号
HWY_DX_Sender=xxxxxxxxxx

#---------------------↓阿里云接口-----------------------
#是否开启阿里云短信告警通道,可同时开始多个通道0为关闭,1为开启
open-alydx=0
#阿里云短信主账号AccessKey的ID
ALY_DX_AccessKeyId=xxxxxxxxxxxxxxxxxxxxxx
#阿里云短信接口密钥
ALY_DX_AccessSecret=xxxxxxxxxxxxxxxxxxxxxx
#阿里云短信签名名称
ALY_DX_SignName=阿里云
#阿里云短信模板ID
ALY_DX_Template=xxxxxxxxxxxxxxxxxxxxxx

#是否开启阿里云电话告警通道,可同时开始多个通道0为关闭,1为开启
open-alydx=0
#阿里云电话主账号AccessKey的ID
ALY_DH_AccessKeyId=xxxxxxxxxxxxxxxxxxxxxx
#阿里云电话接口密钥
ALY_DH_AccessSecret=xxxxxxxxxxxxxxxxxxxxxx
#阿里云电话被叫显号，必须是已购买的号码
ALY_DX_CalledShowNumber=xxxxxxxxx
#阿里云电话文本转语音（TTS）模板ID
ALY_DH_TtsCode=xxxxxxxx
```

## 项目地址

- https://github.com/feiyu563/PrometheusAlert