## 前言

随着各大浏览器对 `http` 请求标识为 `不安全`（见下图），现如今强烈推荐网站使用 `https` 请求。对于运维同学来说，`SSL` 证书`有效期`如何监控，不可能去记住每个域名证书到期日期，今天作者分享`两个脚本`并配合`zabbix` 来监控 SSL 证书到期日期。这样就不会因为 SSL 证书到期导致网站瘫痪。

![](../img/http-ssl-1.png)

## 脚本

### 注释

> - 两个脚本都可以使用，任选一个就行。
> - 优化 `openssl s_client` 命令监测域名时会出现卡死（卡死原因：一般是网站挂掉导致没有响应），导致 `zabbix agent` 异常问题。
> - 本文不提供 zabbix 配置，具体谷歌搜索一下。

### 脚本一

```bash
#! /usr/bin/env bash

host=$1
port=${2:-"443"}

end_date=`timeout 6 openssl s_client -host $host -port $port -showcerts  </dev/null 2>/dev/null |
        sed -n '/BEGIN CERTIFICATE/,/END CERT/p' |
        openssl x509 -text 2> /dev/null |
        sed -n 's/ *Not After : *//p'`

if [ -n "$end_date" ];then
   # 把时间转换为时间戳
   end_date_seconds=`date '+%s' --date "$end_date"`
   # 获取当前时间
   now_seconds=`date '+%s'`
   echo "($end_date_seconds-$now_seconds)/24/3600" | bc
fi
```

### 脚本二

```bash
#! /usr/bin/env bash

host=$1
port=${2:-"443"}

end_date=`echo | timeout 6 openssl s_client -servername ${host} -connect ${host}:${port} 2>/dev/null |
	openssl x509 -noout -dates | grep notAfter | awk -F "=" '{print $NF}'`

if [ -n "$end_date" ];then
   # 把时间转换为时间戳
   end_date_seconds=`date '+%s' --date "$end_date"`
   # 获取当前时间
   now_seconds=`date '+%s'`
   echo "($end_date_seconds-$now_seconds)/24/3600" | bc
fi
```