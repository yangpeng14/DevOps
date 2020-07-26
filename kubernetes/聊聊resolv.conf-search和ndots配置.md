## 背景

Kubernetes 集群中，域名解析离不开 `DNS` 服务，在 Kubernetes v1.10 以前集群使用 `kube-dns` dns服务，后来在 Kubernetes v1.10+ 使用 `Coredns` 做为集群dns服务。

使用 Kubernetes 集群时，会发现 Pod `/etc/resolv.conf` 配置。具体如下：

```
nameserver 10.10.0.2
search production.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

小伙伴们会好奇，`search` 或者 `ndots` 这是干嘛呀！想知道是干嘛的，接着看下文。

## 名词解释

- `search`：搜索主机名查找列表。搜索列表目前仅限于6个域名，共计256个字符。

- `ndots`：通俗一点说，如果你的域名请求参数中，`点的个数`比配置的`ndots`小，则会按照配置的`search`内容，依次添加相应的后缀直到获取到域名解析后的地址。如果通过添加了search之后还是找不到域名，则会按照一开始请求的域名进行解析。

## 抓包分析DNS请求

Kubernetes Pod 内抓包，请参考 [K8S Pod 内抓包快速定位网络问题](https://www.yp14.cn/2020/06/01/K8S-Pod-%E5%86%85%E6%8A%93%E5%8C%85%E5%BF%AB%E9%80%9F%E5%AE%9A%E4%BD%8D%E7%BD%91%E7%BB%9C%E9%97%AE%E9%A2%98/)

### 解析集群内部域名

下面例子解析同一个 `namespace` 中 service 名称为 `blog` 域名。

```bash
# 进入 piwik 容器网络
$ e_net piwik-654dc7b97b-g44kn production

 Entering pod netns for production/piwik-654dc7b97b-g44kn

 Execute the command: nsenter -n -t 16519

# 使用 tcpdump 抓 dns 53 端口包
$ tcpdump -nt -i eth0 port 53 

# 再打开另一个窗口，进入 piwik 容器
$ kubectl exec -it piwik-654dc7b97b-g44kn -n production  sh

# 解析 blog 域名
$ nslookup blog

Server:		10.10.0.2
Address:	10.10.0.2#53

Name:	blog.production.svc.cluster.local
Address: 10.10.72.218
```

下面是抓 `blog` 域名 DNS 包结果：

![](/img/coredns-img-1.png)

从上面看，解析 `blog` 域名时，点的个数比配置中 `ndots` 值小，会按照配置 `search` 参数填补域名后缀。在第一次填补后缀 `production.svc.cluster.local` 就解析出 `A记录`，这时就会终止dns查询返回A记录结果。

### 解析集群外部域名

下面例子解析集群外部域名 `www.jd.com` 京东网站。

```bash
# 进入 piwik 容器
$ kubectl exec -it piwik-654dc7b97b-g44kn -n production  sh

# dns 解析京东域名
$ nslookup www.jd.com

Server:		10.10.0.2
Address:	10.10.0.2#53

Non-authoritative answer:
www.jd.com	canonical name = www.jd.com.gslb.qianxun.com.
www.jd.com.gslb.qianxun.com	canonical name = www.jdcdn.com.
www.jdcdn.com	canonical name = img2x-v6-sched.jcloudedge.com.
Name:	img2x-v6-sched.jcloudedge.com
Address: 222.186.184.3
```

下面是抓 `www.jd.com `域名 DNS 包结果：

![](/img/coredns-img-2.png)

从上图抓包来看，京东域名点的个数比配置中 `ndots` 值小，会按照配置 `search` 参数填补域名后缀。依次填补 `production.svc.cluster.local.`、`svc.cluster.local.`、`cluster.local.`都没有查询出结果，后面直接解析 `www.jd.com` 域名，查询出A记录并返回结果。

### 解析域名点数大于或者等于ndots配置

解析域名`点数`大于或者等于`ndots`配置，又会发生什么事情了？

下面来看看结果：

```bash
# 点数等于 ndots 配置
$ nslookup a.b.c.e.yp14.cn

Server:		10.10.0.2
Address:	10.10.0.2#53

Non-authoritative answer:
Name:	a.b.c.e.yp14.cn
Address: 39.106.191.105
```

点数等于 ndots 配置结果

![](/img/coredns-img-3.png)


```bash
# 点数大于 ndots 配置
$ nslookup a.b.c.e.f.yp14.cn

Server:		10.10.0.2
Address:	10.10.0.2#53

Non-authoritative answer:
Name:	a.b.c.e.f.yp14.cn
Address: 39.106.191.105
```

点数等于 ndots 大于配置结果

![](/img/coredns-img-4.png)

从上面我们可以得出结论，不管是点数大于或者等于 `ndots` 配置，都不会填补 `search` 声明的配置。

## 优化建议

通过上面案例可以发现`ndots`的值和请求息息相关，在使用中为了避免过多的DNS查询请求，可以适当优化相应的值或者请求域名。

- 条件允许的情况下，尽量将请求体中的点都带上，并且要大于或者等于配置中的ndots的值。
- 由于自动填补域名后缀是按照配置中的参数依次添加，所以在`同一个namespace`下，可以直接解析`Service名`即可。如 nslookup blog，会自动补全 `production.svc.cluster.local` 后缀，且是第一个配置的，因此查询也只有一条。提高DNS解析速度。