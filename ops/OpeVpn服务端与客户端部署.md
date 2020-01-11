## OpenVpn 简介[1]

`OpenVPN` 是一个用于创建虚拟专用网络加密通道的软件包，最早由`James Yonan`编写。OpenVPN允许创建的VPN使用公开密钥、电子证书、或者用户名／密码来进行身份验证。

它大量使用了OpenSSL加密库中的SSLv3/TLSv1协议函数库。

当前 `OpenVPN` 能在 `Solaris`、`Linux`、`OpenBSD`、`FreeBSD`、`NetBSD`、`Mac OS X`与`Microsoft Windows`以及`Android`和`iOS`上运行，并包含了许多安全性的功能。它并不是一个基于Web的VPN软件，也不与IPsec及其他VPN软件包兼容。

## 功能与端口[1]

- OpenVPN所有的通信都基于一个单一的IP端口，默认且推荐使用UDP协议通讯，同时也支持TCP。IANA（Internet Assigned Numbers Authority）指定给OpenVPN的官方端口为1194。OpenVPN 2.0以后版本每个进程可以同时管理数个并发的隧道。
- OpenVPN使用通用网络协议（TCP与UDP）的特点使它成为IPsec等协议的理想替代，尤其是在ISP（Internet service provider）过滤某些特定VPN协议的情况下。
- OpenVPN连接能通过大多数的代理服务器，并且能够在NAT的环境中很好地工作。
- 服务端具有向客户端“推送”某些网络配置信息的功能，这些信息包括：IP地址、路由设置等。
- OpenVPN提供了两种虚拟网络接口：通用Tun/Tap驱动，通过它们，可以创建三层IP隧道，或者虚拟二层以太网，后者可以传送任何类型的二层以太网络数据。
- 传送的数据可通过LZO算法压缩。

## OpenVpn 部署[2]

> `注意`：证书口令 `example`

### 初始化包含配置文件和证书的容器。容器将提示输入密码以保护新生成的证书颁发机构使用的私钥

```bash
# 创建宿主机 openvpn 数据存储目录
$ mkdir -p /var/www/openvpn/data
$ chmod 777 /var/www/openvpn/data


# 初始化 OpenVpn 存储目录，将保存配置文件和证书的容器。容器将提示您输入密码，以保护新生成的证书颁发机构使用的私钥
# 证书口令 example

$ docker run -v /var/www/openvpn/data:/etc/openvpn --log-driver=none --rm kylemanna/openvpn ovpn_genconfig -u udp://vpn.example.com

$ docker run -v /var/www/openvpn/data:/etc/openvpn --log-driver=none --rm -it kylemanna/openvpn ovpn_initpki
```

### 启动 OpenVPN 服务器进程

```bash
$ docker run -d --restart=always --name openvpn \
--hostname openvpn \
-p 1194:1194/udp \
--cap-add=NET_ADMIN \
-v /var/www/openvpn/data:/etc/openvpn \
kylemanna/openvpn:latest
```

### 生成没有密码的客户端证书

```bash
$ docker run -v /var/www/openvpn/data:/etc/openvpn --log-driver=none --rm -it kylemanna/openvpn easyrsa build-client-full CLIENTNAME nopass
```

### 检索具有嵌入证书的客户端配置(导出生成的客户端证书)

```bash
$ docker run -v /var/www/openvpn/data:/etc/openvpn --log-driver=none --rm kylemanna/openvpn ovpn_getclient CLIENTNAME > CLIENTNAME.ovpn
```

## OpenVpn 客户端部署与配置

> 适用于 `Ubuntu`、`Debian`

### 部署客户端

```bash
# 安装openssl和lzo，lzo用于压缩通讯数据加快传输速度
$ sudo apt-get install openssl libssl-dev
$ sudo apt-get install lzop

# 安装openvpn和easy-rsa
$ sudo apt-get install openvpn
$ sudo apt-get install easy-rsa
```

### 配置客户端.ovpn 文件（上一步，OpenVpn 导出的客户端证书）

> 下面列出修改几个关键的参数


检查你的发行版本是否包含 `/etc/openvpn/update-resolv-conf` 脚本
如果存在编辑你传输的OpenVPN客户端配置文件添加下面三个参数：

```
script-security 2
up /etc/openvpn/update-resolv-conf
down /etc/openvpn/update-resolv-conf
```

如果你使用的是 `CentOS`，把 `group` 从 `nogroup` 修改为 `nobody` 以匹配发行版本的可用组

```
group nobody
```


```bash
# 修改客户端 .ovpn 配置
$ vim CLIENTNAME.ovpn

# 默认全局走 openvpn，这里注释
# redirect-gateway def1

# 声明使用淘宝 DNS
dhcp-option DNS 223.5.5.5
dhcp-option DNS 223.6.6.6

# 声明 172.16.10.0/24 172.16.20.0/24 两个网段走 VPN
route-nopull
route 172.16.10.0 255.255.255.0 vpn_gateway
route 172.16.20.0 255.255.255.0 vpn_gateway

script-security 2
up /etc/openvpn/update-resolv-conf
down /etc/openvpn/update-resolv-conf
```

### 启动命令

```bash
$ nohup /usr/sbin/openvpn --config /etc/openvpn/CLIENTNAME.ovpn --log-append /tmp/openvpn.log &
```

> `MacOS` 客户端下载地址

下载 [tunnelblick](https://tunnelblick.net/downloads.html)客户端工具，导入证书即可使用。

## 参考链接

- [1]https://zh.wikipedia.org/wiki/OpenVPN
- [2]https://github.com/kylemanna/docker-openvpn