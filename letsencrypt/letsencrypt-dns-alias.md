### 一、写本外壳背景
1. [acme.sh](https://github.com/Neilpang/acme.sh) 使用 [DNS alias mode 功能](https://github.com/Neilpang/acme.sh/wiki/DNS-alias-mode) 申请 Let's Encrypt 证书，如果申请DNS域大约超过8个以上就会遇到 `Incorrect TXT record`错误。本人大致看了`acme.sh`脚本`alias mode`功能暂时没有发现脚本中间有bug，后本人没有办法就在`acme.sh`脚本外面套一层外壳，具体使用方法见下面内容。

### 二、使用本外壳前准备环境
1. [acme.sh 脚本安装](https://github.com/Neilpang/acme.sh/wiki/How-to-install)
2. [设置DNS CNAME 记录](https://github.com/Neilpang/acme.sh/wiki/DNS-alias-mode)
3. 安装`Python3`环境
4. [下载 letsencrypt-dns-alias.py](https://github.com/yangpeng14/DevOps/blob/master/letsencrypt/letsencrypt-dns-alias.py)

### 三、本外壳使用注意
1. 只支持`DNS alias mode 功能`。
2. 只支持`--challenge-alias`参数，不支持`--domain-alias`参数。
3. 不能往外壳传入`--domain -d --domain-alias --challenge-alias --dns --log-level --log`参数。
4. 每次向`Let's Encrypt`申请5个域名，依次累加，申请通过的域名在一断时间内不需要再次验证。
5. 开启记录日志模式，日志级别为 `2`。
6. 申请证书失败时，支持重试2次，每次等待20秒。

### 四、使用方法
1. 第一次使用下面命令

```
$ letsencrypt-dns-alias.py --command="--issue" --challenge-alias="alias domain" --dns="dns_ali" --key-name="Ali_Key" --secret-name="Ali_Secret" --key="***" --secret="***" --domain="*.a.com,*.b.com"
```

2. 如果`acme.sh`脚本已记录DNS厂商AK值，可以使用下面命令。

```
$ letsencrypt-dns-alias.py --command="--issue" --challenge-alias="alias domain" --dns="dns_ali" --domain="*.a.com,*.b.com"
```

3. 上面命令中`--key-name="Ali_Key" --secret-name="Ali_Secret"` 是DNS厂商api名称，具体api支持见[How to use DNS API](https://github.com/Neilpang/acme.sh/wiki/dnsapi)。