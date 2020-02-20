## 症状表现

服务器CPU资源使用一直处于100%的状态，通过 `top` 命令查看，发现可疑进程 `kdevtmpfsi`。通过 google搜索，发现这是挖矿病毒。

![](/img/kdevtmpfsi-top.png)

## 排序方法

`首先`：查看 `kdevtmpfsi` 进程，使用 `ps -ef | grep kdevtmpfsi` 命令查看，见下图。

![](/img/kdevtmpfsi-1.png)

> PS： 通过 `ps -ef` 命令查出 `kdevtmpfsi` 进程号，直接 kill -9 进程号并删除 /tmp/kdevtmpfsi 执行文件。但没有过1分钟进程又运行了，这时就能想到，`kdevtmpfsi` 有守护程序或者有计划任务。通过 `crontab -l` 查看是否有可疑的计划任务。

`第二步`：根据上面结果知道 `kdevtmpfsi` 进程号是 `10393`，使用 `systemctl status 10393` 发现 `kdevtmpfsi` 有守护进程，见下图。

![](/img/kdevtmpfsi-2.png)

`第三步`：kill 掉 kdevtmpfsi 守护进程 `kill -9 30903 30904`，再 `killall -9 kdevtmpfsi` 挖矿病毒，最后删除 kdevtmpfsi 执行程序 `rm -f /tmp/kdevtmpfsi`。

## 事后检查

- 通过 `find / -name "*kdevtmpfsi*"` 命令搜索是否还有 kdevtmpfsi 文件
- 查看 Linux ssh 登陆审计日志。`Centos` 与 `RedHat` 审计日志路径为 `/var/log/secure`，`Ubuntu` 与 `Debian` 审计日志路径为 `/var/log/auth.log`。
- 检查 crontab 计划任务是否有可疑任务

## 后期防护

- 启用`ssh公钥登陆`，禁用密码登陆。
- `云主机`：完善安全策略，入口流量，一般只开放 80 443 端口就行，出口流量默认可以不限制，如果有需要根据需求来限制。`物理机`：可以通过`硬件防火墙`或者`机器上iptables` 来开放出入口流量规则。
- 本机不是直接需要对外提供服务，可以拒绝外网卡入口所有流量，通过 `jumper` 机器内网登陆业务机器。
- 公司有能力可以搭建安全扫描服务，定期检查机器上漏洞并修复。

`小结`：以上例举几点措施，不全。这里只是抛砖引玉的效果，更多的措施需要结合自己业务实际情况，否则就空中楼阁。