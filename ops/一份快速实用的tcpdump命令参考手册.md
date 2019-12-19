## tcpdump 简介

对于 `tcpdump` 的使用，大部分管理员会分成两类。有一类管理员，他们熟知 `tcpdump` 和其中的所有标记；另一类管理员，他们仅了解基本的使用方法，剩下事情都要借助参考手册才能完成。出现这种情况的原因在于， `tcpdump` 是一个相当高级的命令，使用的时候需要对网络的工作机制有相当深入的了解。

在今天的文章中，我想提供一个快速但相当实用的 `tcpdump` 参考。我会谈到基本的和一些高级的使用方法。我敢肯定我会忽略一些相当酷的命令，欢迎你补充在评论部分。

在我们深入了解以前，最重要的是了解 `tcpdump` 是用来做什么的。 `tcpdump` 命令用来保存和记录网络流量。你可以用它来观察网络上发生了什么，并可用来解决各种各样的问题，包括和网络通信无关的问题。除了网络问题，我经常用 tcpdump 解决应用程序的问题。如果你发现两个应用程序之间无法很好工作，可以用 `tcpdump` 观察出了什么问题。 `tcpdump` 可以用来抓取和读取数据包，特别是当通信没有被加密的时候。

## 基础知识

了解 `tcpdump` ，首先要知道 `tcpdump` 中使用的标记（flag）。在这个章节中，我会涵盖到很多基本的标记，这些标记在很多场合下会被用到。

### 不转换主机名、端口号等

```bash
# tcpdump -n
```

通常情况下， tcpdump 会尝试查找和转换主机名和端口号。

```bash
# tcpdump

tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on eth0, link-type EN10MB (Ethernet), capture size 65535 bytes
16:15:05.051896 IP blog.ssh > 10.0.3.1.32855: Flags [P.], seq 2546456553:2546456749, ack 1824683693, win 355, options [nop,nop,TS val 620879437 ecr 620879348], length 196
```

你可以通过 `-n` 标记关闭这个功能。我个人总是使用这个标记，因为我喜欢使用 IP 地址而不是主机名，主机名和端口号的转换经常会带来困扰。但是，知道利用 tcpdump 转换或者不转换的功能还是相当有用的，特别是有些时候，知道源流量（source traffic）来自哪个服务器是相当重要的。

```bash
# tcpdump -n

tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on eth0, link-type EN10MB (Ethernet), capture size 65535 bytes
16:23:47.934665 IP 10.0.3.246.22 > 10.0.3.1.32855: Flags [P.], seq 2546457621:2546457817, ack 1824684201, win 355, options [nop,nop,TS val 621010158 ecr 621010055], length 196
```

### 增加详细信息

```bash
# tcpdump -v
```

增加一个简单 `-v` 标记，输出会包含更多信息，例如一个 IP 包的生存时间(ttl, time to live)、长度和其他的选项。

```bash
# tcpdump

tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on eth0, link-type EN10MB (Ethernet), capture size 65535 bytes
16:15:05.051896 IP blog.ssh > 10.0.3.1.32855: Flags [P.], seq 2546456553:2546456749, ack 1824683693, win 355, options [nop,nop,TS val 620879437 ecr 620879348], length 196
```

`tcpdump` 的详细信息有三个等级，你可以通过在命令行增加 v 标记的个数来获取更多的信息。通常我在使用 `tcpmdump` 的时候，总是使用最高等级的详细信息，因为我希望看到所有信息，以免后面会用到。

```bash
# tcpdump -vvv -c 1

tcpdump: listening on eth0, link-type EN10MB (Ethernet), capture size 65535 bytes
16:36:13.873456 IP (tos 0x10, ttl 64, id 121, offset 0, flags [DF], proto TCP (6), length 184)
    blog.ssh > 10.0.3.1.32855: Flags [P.], cksum 0x1ba1 (incorrect -> 0x0dfd), seq 2546458841:2546458973, ack 1824684869, win 355, options [nop,nop,TS val 621196643 ecr 621196379], length 132
```

### 指定网络接口

```bash
# tcpdump -i eth0
```

通常情况下，如果不指定网络接口， `tcpdump` 在运行时会选择编号最低的网络接口，一般情况下是 `eth0`，不过因系统不同可能会有所差异。

```bash
# tcpdump

tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on eth0, link-type EN10MB (Ethernet), capture size 65535 bytes
16:15:05.051896 IP blog.ssh > 10.0.3.1.32855: Flags [P.], seq 2546456553:2546456749, ack 1824683693, win 355, options [nop,nop,TS val 620879437 ecr 620879348], length 196
```

你可以用 `-i` 标记来指定网络接口。在大多数 Linux 系统上，`any` 这一特定的网络接口名用来让 tcpdump 监听所有的接口。我发现这在排查服务器（拥有多个网络接口）的问题特别有用，尤其是牵扯到路由的时候。

```bash
# tcpdump -i any

tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
16:45:59.312046 IP blog.ssh > 10.0.3.1.32855: Flags [P.], seq 2547763641:2547763837, ack 1824693949, win 355, options [nop,nop,TS val 621343002 ecr 621342962], length 196
```

### 写入文件

```bash
# tcpdump -w /path/to/file
```

`tcpdump` 运行结果会输出在屏幕上。

```bash
# tcpdump

tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on eth0, link-type EN10MB (Ethernet), capture size 65535 bytes
16:15:05.051896 IP blog.ssh > 10.0.3.1.32855: Flags [P.], seq 2546456553:2546456749, ack 1824683693, win 355, options [nop,nop,TS val 620879437 ecr 620879348], length 196
```

但很多时候，你希望把 `tcpdump` 的输出结果保存在文件中，最简单的方法就是利用 `-w` 标记。如果你后续还会检查这些网络数据，这样做就特别有用。将这些数据存成一个文件的好处，就是你可以多次读取这个保存下来的文件，并且可以在这个网络流量的快照上使用其它标记或者过滤器（我们后面会讨论到）。

```bash
#  tcpdump  -w /var/tmp/tcpdata.pcap

 tcpdump : listening on eth0, link-type EN10MB (Ethernet), capture size 65535 bytes
1 packet captured
2 packets received by filter
0 packets dropped by kernel
```

通常这些数据被缓存而不会被写入文件，直到你用 `CTRL+C` 结束 `tcpdump` 命令的时候。

### 读取文件

```bash
#  tcpdump  -r /path/to/file
```

一旦你将输出存成文件，就必然需要读取这个文件。要做到这点，你只需要在 -r 标记后指定这个文件的存放路径。

```bash
# tcpdump -r /var/tmp/tcpdata.pcap 

reading from file /var/tmp/tcpdata.pcap, link-type EN10MB (Ethernet)
16:56:01.610473 IP blog.ssh > 10.0.3.1.32855: Flags [P.], seq 2547766673:2547766805, ack 1824696181, win 355, options [nop,nop,TS val 621493577 ecr 621493478], length 132
```

一个小提醒，如果你熟悉 [wireshark](https://www.wireshark.org/) 这类网络诊断工具，也可以利用它们来读取 `tcpdump` 保存的文件。

### 指定抓包大小

```bash
#  tcpdump  -s 100
```

较新版本的 `tcpdump` 通常可以截获 65535 字节，但某些情况下你不需要截获默认大小的数据包。运行 `tcpdump` 时，你可以通过 `-s` 标记来指定快照长度。

### 指定抓包数量

```bash
#  tcpdump  -c 10
```

`tcpdump` 会一直运行，直至你用 `CTRL+C` 让它退出。

```bash
#  tcpdump  host google.com

 tcpdump : verbose output suppressed, use -v or -vv for full protocol decode
listening on eth0, link-type EN10MB (Ethernet), capture size 65535 bytes
^C
0 packets captured
4 packets received by filter
0 packets dropped by kernel
```

你也可以通过 `-c` 标记后面加上抓包的数量，让 `tcpdump` 在抓到一定数量的数据包后停止操作。当你不希望看到 `tcpdump` 的输出大量出现在屏幕上，以至于你无法阅读的时候，就会希望使用这个标记。当然，通常更好的方法是借助过滤器来截获特定的流量。

### 基础知识汇总

```bash
#  tcpdump  -nvvv -i any -c 100 -s 100
```

你可以将以上这些基础的标记组合起来使用，来让 `tcpdump` 提供你所需要的信息。

```bash
# tcpdump -w /var/tmp/tcpdata.pcap -i any -c 10 -vvv

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
10 packets captured
10 packets received by filter
0 packets dropped by kernel

# tcpdump -r /var/tmp/tcpdata.pcap -nvvv -c 5

reading from file /var/tmp/tcpdata.pcap, link-type LINUX_SLL (Linux cooked)
17:35:14.465902 IP (tos 0x10, ttl 64, id 5436, offset 0, flags [DF], proto TCP (6), length 104)
    10.0.3.246.22 > 10.0.3.1.32855: Flags [P.], cksum 0x1b51 (incorrect -> 0x72bc), seq 2547781277:2547781329, ack 1824703573, win 355, options [nop,nop,TS val 622081791 ecr 622081775], length 52
17:35:14.466007 IP (tos 0x10, ttl 64, id 52193, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.1.32855 > 10.0.3.246.22: Flags [.], cksum 0x1b1d (incorrect -> 0x4950), seq 1, ack 52, win 541, options [nop,nop,TS val 622081791 ecr 622081791], length 0
17:35:14.470239 IP (tos 0x10, ttl 64, id 5437, offset 0, flags [DF], proto TCP (6), length 168)
    10.0.3.246.22 > 10.0.3.1.32855: Flags [P.], cksum 0x1b91 (incorrect -> 0x98c3), seq 52:168, ack 1, win 355, options [nop,nop,TS val 622081792 ecr 622081791], length 116
17:35:14.470370 IP (tos 0x10, ttl 64, id 52194, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.1.32855 > 10.0.3.246.22: Flags [.], cksum 0x1b1d (incorrect -> 0x48da), seq 1, ack 168, win 541, options [nop,nop,TS val 622081792 ecr 622081792], length 0
17:35:15.464575 IP (tos 0x10, ttl 64, id 5438, offset 0, flags [DF], proto TCP (6), length 104)
    10.0.3.246.22 > 10.0.3.1.32855: Flags [P.], cksum 0x1b51 (incorrect -> 0xc3ba), seq 168:220, ack 1, win 355, options [nop,nop,TS val 622082040 ecr 622081792], length 52
```

## 过滤器

介绍完基础的标记后，我们该介绍过滤器了。 `tcpdump` 可以通过各式各样的表达式，来过滤所截取或者输出的数据。我在这篇文章里会给出一些简单的例子，以便让你们了解语法规则。你们可以查询 `tcpdump` 帮助中的 [pcap-filter](http://www.tcpdump.org/manpages/pcap-filter.7.html) 章节，了解更为详细的信息。

### 查找特定主机的流量

```bash
#  tcpdump  -nvvv -i any -c 3 host 10.0.3.1
```

运行上述命令， `tcpdump` 会像前面一样把结果输出到屏幕上，不过只会显示源 IP 或者目的 IP 地址是 `10.0.3.1` 的数据包。通过增加主机 `10.0.3.1` 参数，我们可以让 `tcpdump` 过滤掉源和目的地址不是 `10.0.3.1` 的数据包。

```bash
# tcpdump -nvvv -i any -c 3 host 10.0.3.1

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
17:54:15.067496 IP (tos 0x10, ttl 64, id 5502, offset 0, flags [DF], proto TCP (6), length 184)
    10.0.3.246.22 > 10.0.3.1.32855: Flags [P.], cksum 0x1ba1 (incorrect -> 0x9f75), seq 2547785621:2547785753, ack 1824705637, win 355, options [nop,nop,TS val 622366941 ecr 622366923], length 132
17:54:15.067613 IP (tos 0x10, ttl 64, id 52315, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.1.32855 > 10.0.3.246.22: Flags [.], cksum 0x1b1d (incorrect -> 0x7c34), seq 1, ack 132, win 540, options [nop,nop,TS val 622366941 ecr 622366941], length 0
17:54:15.075230 IP (tos 0x10, ttl 64, id 5503, offset 0, flags [DF], proto TCP (6), length 648)
    10.0.3.246.22 > 10.0.3.1.32855: Flags [P.], cksum 0x1d71 (incorrect -> 0x3443), seq 132:728, ack 1, win 355, options [nop,nop,TS val 622366943 ecr 622366941], length 596
```

### 只显示源地址为特定主机的流量

```bash
#  tcpdump  -nvvv -i any -c 3 src host 10.0.3.1
```

前面的例子显示了源和目的地址是 `10.0.3.1` 的流量，而上面的命令只显示数据包源地址是 `10.0.3.1` 的流量。这是通过在 `host` 前面增加 `src` 参数来实现的。这个额外的过滤器告诉 `tcpdump` 查找特定的源地址。 反过来通过 `dst` 过滤器，可以指定目的地址。

```bash
# tcpdump -nvvv -i any -c 3 src host 10.0.3.1

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
17:57:12.194902 IP (tos 0x10, ttl 64, id 52357, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.1.32855 > 10.0.3.246.22: Flags [.], cksum 0x1b1d (incorrect -> 0x1707), seq 1824706545, ack 2547787717, win 540, options [nop,nop,TS val 622411223 ecr 622411223], length 0
17:57:12.196288 IP (tos 0x10, ttl 64, id 52358, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.1.32855 > 10.0.3.246.22: Flags [.], cksum 0x1b1d (incorrect -> 0x15c5), seq 0, ack 325, win 538, options [nop,nop,TS val 622411223 ecr 622411223], length 0
17:57:12.197677 IP (tos 0x10, ttl 64, id 52359, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.1.32855 > 10.0.3.246.22: Flags [.], cksum 0x1b1d (incorrect -> 0x1491), seq 0, ack 633, win 536, options [nop,nop,TS val 622411224 ecr 622411224], length 0

# tcpdump -nvvv -i any -c 3 dst host 10.0.3.1

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
17:59:37.266838 IP (tos 0x10, ttl 64, id 5552, offset 0, flags [DF], proto TCP (6), length 184)
    10.0.3.246.22 > 10.0.3.1.32855: Flags [P.], cksum 0x1ba1 (incorrect -> 0x586d), seq 2547789725:2547789857, ack 1824707577, win 355, options [nop,nop,TS val 622447491 ecr 622447471], length 132
17:59:37.267850 IP (tos 0x10, ttl 64, id 5553, offset 0, flags [DF], proto TCP (6), length 392)
    10.0.3.246.22 > 10.0.3.1.32855: Flags [P.], cksum 0x1c71 (incorrect -> 0x462e), seq 132:472, ack 1, win 355, options [nop,nop,TS val 622447491 ecr 622447491], length 340
17:59:37.268606 IP (tos 0x10, ttl 64, id 5554, offset 0, flags [DF], proto TCP (6), length 360)
    10.0.3.246.22 > 10.0.3.1.32855: Flags [P.], cksum 0x1c51 (incorrect -> 0xf469), seq 472:780, ack 1, win 355, options [nop,nop,TS val 622447491 ecr 622447491], length 308
```

### 过滤源和目的端口

```bash
#  tcpdump  -nvvv -i any -c 3 port 22 and port 60738
```

通过类似 `and` 操作符，你可以在 `tcpdump` 上使用更为复杂的过滤器描述。这个就类似 `if` 语句，你就这么想吧。这个例子中，我们使用 `and` 操作符告诉 `tcpdump` 只输出端口号是 `22` 和 `60738` 的数据包。这点在分析网络问题的时候很有用，因为可以通过这个方法来关注某一个特定会话（session）的数据包。

```bash
# tcpdump -nvvv -i any -c 3 port 22 and port 60738

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
18:05:54.069403 IP (tos 0x10, ttl 64, id 64401, offset 0, flags [DF], proto TCP (6), length 104)
    10.0.3.1.60738 > 10.0.3.246.22: Flags [P.], cksum 0x1b51 (incorrect -> 0x5b3c), seq 917414532:917414584, ack 1550997318, win 353, options [nop,nop,TS val 622541691 ecr 622538903], length 52
18:05:54.072963 IP (tos 0x10, ttl 64, id 13601, offset 0, flags [DF], proto TCP (6), length 184)
    10.0.3.246.22 > 10.0.3.1.60738: Flags [P.], cksum 0x1ba1 (incorrect -> 0xb0b1), seq 1:133, ack 52, win 355, options [nop,nop,TS val 622541692 ecr 622541691], length 132
18:05:54.073080 IP (tos 0x10, ttl 64, id 64402, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.1.60738 > 10.0.3.246.22: Flags [.], cksum 0x1b1d (incorrect -> 0x1e3b), seq 52, ack 133, win 353, options [nop,nop,TS val 622541692 ecr 622541692], length 0
```

你可以用两种方式来表示 `and` `操作符，and` 或者 `&&` 都可以。我个人倾向于两个都使用，特别要记住在使用 `&&` 的时候，要用单引号或者双引号包住表达式。在 BASH 中，你可以使用 `&&` 运行一个命令，该命令成功后再执行后面的命令。通常，最好将表达式用引号包起来，这样会避免不预期的结果，特别当过滤器中有一些特殊字符的时候。

```bash
# tcpdump -nvvv -i any -c 3 'port 22 && port 60738'

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
18:06:16.062818 IP (tos 0x10, ttl 64, id 64405, offset 0, flags [DF], proto TCP (6), length 88)
    10.0.3.1.60738 > 10.0.3.246.22: Flags [P.], cksum 0x1b41 (incorrect -> 0x776c), seq 917414636:917414672, ack 1550997518, win 353, options [nop,nop,TS val 622547190 ecr 622541776], length 36
18:06:16.065567 IP (tos 0x10, ttl 64, id 13603, offset 0, flags [DF], proto TCP (6), length 120)
    10.0.3.246.22 > 10.0.3.1.60738: Flags [P.], cksum 0x1b61 (incorrect -> 0xaf2d), seq 1:69, ack 36, win 355, options [nop,nop,TS val 622547191 ecr 622547190], length 68
18:06:16.065696 IP (tos 0x10, ttl 64, id 64406, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.1.60738 > 10.0.3.246.22: Flags [.], cksum 0x1b1d (incorrect -> 0xf264), seq 36, ack 69, win 353, options [nop,nop,TS val 622547191 ecr 622547191], length 0
```

### 查找两个端口号的流量

```bash
#  tcpdump  -nvvv -i any -c 20 'port 80 or port 443'
```

你可以用 `or` 或者 `||` 操作符来过滤结果。在这个例子中，我们使用 `or` 操作符去截获发送和接收端口为 `80` 或 `443` 的数据流。这在 Web 服务器上特别有用，因为服务器通常有两个开放的端口，端口号 `80` 表示 `http` `连接，443` 表示 `https`。

```bash
# tcpdump -nvvv -i any -c 20 'port 80 or port 443'

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
18:24:28.817940 IP (tos 0x0, ttl 64, id 39930, offset 0, flags [DF], proto TCP (6), length 60)
    10.0.3.1.50524 > 10.0.3.246.443: Flags [S], cksum 0x1b25 (incorrect -> 0x8611), seq 3836995553, win 29200, options [mss 1460,sackOK,TS val 622820379 ecr 0,nop,wscale 7], length 0
18:24:28.818052 IP (tos 0x0, ttl 64, id 0, offset 0, flags [DF], proto TCP (6), length 40)
    10.0.3.246.443 > 10.0.3.1.50524: Flags [R.], cksum 0x012c (correct), seq 0, ack 3836995554, win 0, length 0
18:24:32.721330 IP (tos 0x0, ttl 64, id 48510, offset 0, flags [DF], proto TCP (6), length 475)
    10.0.3.1.60374 > 10.0.3.246.80: Flags [P.], cksum 0x1cc4 (incorrect -> 0x3a4e), seq 580573019:580573442, ack 1982754038, win 237, options [nop,nop,TS val 622821354 ecr 622815632], length 423
18:24:32.721465 IP (tos 0x0, ttl 64, id 1266, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.246.80 > 10.0.3.1.60374: Flags [.], cksum 0x1b1d (incorrect -> 0x45d7), seq 1, ack 423, win 243, options [nop,nop,TS val 622821355 ecr 622821354], length 0
18:24:32.722098 IP (tos 0x0, ttl 64, id 1267, offset 0, flags [DF], proto TCP (6), length 241)
    10.0.3.246.80 > 10.0.3.1.60374: Flags [P.], cksum 0x1bda (incorrect -> 0x855c), seq 1:190, ack 423, win 243, options [nop,nop,TS val 622821355 ecr 622821354], length 189
18:24:32.722232 IP (tos 0x0, ttl 64, id 48511, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.1.60374 > 10.0.3.246.80: Flags [.], cksum 0x1b1d (incorrect -> 0x4517), seq 423, ack 190, win 245, options [nop,nop,TS val 622821355 ecr 622821355], length 0
```

### 查找两个特定端口和来自特定主机的数据流

```bash
#  tcpdump  -nvvv -i any -c 20 '(port 80 or port 443) and host 10.0.3.169'
```

前面的例子用来排查多端口的协议问题，是非常有效的。如果 Web 服务器的数据流量相当大， `tcpdump` 的输出可能有点混乱。我们可以通过增加 `host` 参数进一步限定输出。在这种情况下，我们通过把 `or` 表达式放在括号中来保持 `or` 描述。

```bash
# tcpdump -nvvv -i any -c 20 '(port 80 or port 443) and host 10.0.3.169'

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
18:38:05.551194 IP (tos 0x0, ttl 64, id 63169, offset 0, flags [DF], proto TCP (6), length 60)
    10.0.3.169.33786 > 10.0.3.246.443: Flags [S], cksum 0x1bcd (incorrect -> 0x0d96), seq 4173164403, win 29200, options [mss 1460,sackOK,TS val 623024562 ecr 0,nop,wscale 7], length 0
18:38:05.551310 IP (tos 0x0, ttl 64, id 0, offset 0, flags [DF], proto TCP (6), length 40)
    10.0.3.246.443 > 10.0.3.169.33786: Flags [R.], cksum 0xa64a (correct), seq 0, ack 4173164404, win 0, length 0
18:38:05.717130 IP (tos 0x0, ttl 64, id 51574, offset 0, flags [DF], proto TCP (6), length 60)
    10.0.3.169.35629 > 10.0.3.246.80: Flags [S], cksum 0x1bcd (incorrect -> 0xdf7c), seq 1068257453, win 29200, options [mss 1460,sackOK,TS val 623024603 ecr 0,nop,wscale 7], length 0
18:38:05.717255 IP (tos 0x0, ttl 64, id 0, offset 0, flags [DF], proto TCP (6), length 60)
    10.0.3.246.80 > 10.0.3.169.35629: Flags [S.], cksum 0x1bcd (incorrect -> 0xed80), seq 2992472447, ack 1068257454, win 28960, options [mss 1460,sackOK,TS val 623024603 ecr 623024603,nop,wscale 7], length 0
18:38:05.717474 IP (tos 0x0, ttl 64, id 51575, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.169.35629 > 10.0.3.246.80: Flags [.], cksum 0x1bc5 (incorrect -> 0x8c87), seq 1, ack 1, win 229, options [nop,nop,TS val 623024604 ecr 623024603], length 0
```

在一个过滤器中，你可以多次使用括号。在下面的例子中，下面命令可以限定截获满足如下条件的数据包：发送或接收端口号为 `80` 或 `443`，主机来源于 `10.0.3.169` 或者 `10.0.3.1`，且目的地址是 `10.0.3.246`。

```bash
# tcpdump -nvvv -i any -c 20 '((port 80 or port 443) and (host 10.0.3.169 or host 10.0.3.1)) and dst host 10.0.3.246'

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
18:53:30.349306 IP (tos 0x0, ttl 64, id 52641, offset 0, flags [DF], proto TCP (6), length 60)
    10.0.3.1.35407 > 10.0.3.246.80: Flags [S], cksum 0x1b25 (incorrect -> 0x4890), seq 3026316656, win 29200, options [mss 1460,sackOK,TS val 623255761 ecr 0,nop,wscale 7], length 0
18:53:30.349558 IP (tos 0x0, ttl 64, id 52642, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.1.35407 > 10.0.3.246.80: Flags [.], cksum 0x1b1d (incorrect -> 0x3454), seq 3026316657, ack 3657995297, win 229, options [nop,nop,TS val 623255762 ecr 623255762], length 0
18:53:30.354056 IP (tos 0x0, ttl 64, id 52643, offset 0, flags [DF], proto TCP (6), length 475)
    10.0.3.1.35407 > 10.0.3.246.80: Flags [P.], cksum 0x1cc4 (incorrect -> 0x10c2), seq 0:423, ack 1, win 229, options [nop,nop,TS val 623255763 ecr 623255762], length 423
18:53:30.354682 IP (tos 0x0, ttl 64, id 52644, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.1.35407 > 10.0.3.246.80: Flags [.], cksum 0x1b1d (incorrect -> 0x31e6), seq 423, ack 190, win 237, options [nop,nop,TS val 623255763 ecr 623255763], length 0
```

## 理解输出结果

打开 `tcpdump` 的所有选项去截获网络流量是相当困难的，但一旦你拿到这些数据你就要对它进行解读。在这个章节，我们将涉及如何判断源/目的 `IP` 地址，源/目的端口号，以及 `TCP` 协议类型的数据包。当然这些是相当基础的，你从 `tcpdump` 里面获取的信息也远不止这些。不过这篇文章主要是粗略的介绍，我们会关注在这些基础知识上。我建议你们可以通过[帮助页](http://www.tcpdump.org/manpages/)获取更为详细的信息。


### 判断源和目的地址

判断源和目的地址和端口号相当简单。

从上面的输出，我们可以看到源 `IP` 地址是 `10.0.3.246`，源端口号是 `56894`， 目的 IP 地址是 `192.168.0.92`，端口号是 `22`。一旦你理解 `tcpdump` 格式后，这些信息很容易判断。如果你还没有猜到格式，你可以按照 `src-ip.src-port > dest-ip.dest-port: Flags[S]` 格式来分析。源地址位于 `>` 前面，后面则是目的地址。你可以把 `>` 想象成一个指向目的地址的箭头符号。

### 判断数据包类型

```bash
10.0.3.246.56894 > 192.168.0.92.22: Flags [S], cksum 0xcf28 (incorrect -> 0x0388), seq 682725222, win 29200, options [mss 1460,sackOK,TS val 619989005 ecr 0,nop,wscale 7], length 0
```

从上面的例子，我们可以判断这个数据包是一个 `SYN` 数据包。我们是通过 `tcpdump` 输出中的 `[S]` 标记字段得出这个结论，不同类型的数据包有不同类型的标记。不需要深入了解 `TCP` 协议中的数据包类型，你就可以通过下面的速查表来加以判断。

- [S] – SYN (开始连接)
- [.] – 没有标记
- [P] – PSH (数据推送)
- [F] – FIN (结束连接)
- [R] – RST (重启连接)

在这个版本的 `tcpdump` 输出中，`[S.]` 标记代表这个数据包是 `SYN-ACK` 数据包。

### 不好的例子

```bash
15:15:43.323412 IP (tos 0x0, ttl 64, id 51051, offset 0, flags [DF], proto TCP (6), length 60)
    10.0.3.246.56894 > 192.168.0.92.22: Flags [S], cksum 0xcf28 (incorrect -> 0x0388), seq 682725222, win 29200, options [mss 1460,sackOK,TS val 619989005 ecr 0,nop,wscale 7], length 0
15:15:44.321444 IP (tos 0x0, ttl 64, id 51052, offset 0, flags [DF], proto TCP (6), length 60)
    10.0.3.246.56894 > 192.168.0.92.22: Flags [S], cksum 0xcf28 (incorrect -> 0x028e), seq 682725222, win 29200, options [mss 1460,sackOK,TS val 619989255 ecr 0,nop,wscale 7], length 0
15:15:46.321610 IP (tos 0x0, ttl 64, id 51053, offset 0, flags [DF], proto TCP (6), length 60)
    10.0.3.246.56894 > 192.168.0.92.22: Flags [S], cksum 0xcf28 (incorrect -> 0x009a), seq 682725222, win 29200, options [mss 1460,sackOK,TS val 619989755 ecr 0,nop,wscale 7], length 0
```

上面显示了一个不好的通信例子，在这个例子中“不好”，代表通信没有建立起来。我们可以看到 `10.0.3.246` 发出一个 `SYN` 数据包给 主机 `192.168.0.92`，但是主机并没有应答。

### 好的例子

```bash
15:18:25.716453 IP (tos 0x10, ttl 64, id 53344, offset 0, flags [DF], proto TCP (6), length 60)
    10.0.3.246.34908 > 192.168.0.110.22: Flags [S], cksum 0xcf3a (incorrect -> 0xc838), seq 1943877315, win 29200, options [mss 1460,sackOK,TS val 620029603 ecr 0,nop,wscale 7], length 0
15:18:25.716777 IP (tos 0x0, ttl 63, id 0, offset 0, flags [DF], proto TCP (6), length 60)
    192.168.0.110.22 > 10.0.3.246.34908: Flags [S.], cksum 0x594a (correct), seq 4001145915, ack 1943877316, win 5792, options [mss 1460,sackOK,TS val 18495104 ecr 620029603,nop,wscale 2], length 0
15:18:25.716899 IP (tos 0x10, ttl 64, id 53345, offset 0, flags [DF], proto TCP (6), length 52)
    10.0.3.246.34908 > 192.168.0.110.22: Flags [.], cksum 0xcf32 (incorrect -> 0x9dcc), ack 1, win 229, options [nop,nop,TS val 620029603 ecr 18495104], length 0
```

好的例子应该向上面这样，我们看到典型的 TCP 3次握手。第一数据包是 `SYN` 包，从主机 `10.0.3.246` 发送给 主机`192.168.0.110`，第二个包是 `SYN-ACK` 包，主机`192.168.0.110` 回应 `SYN` 包。最后一个包是一个 `ACK` 或者 `SYN – ACK – ACK` 包，是主机 `10.0.3.246` 回应收到了 `SYN – ACK` 包。从上面看到一个 `TCP/IP` 连接成功建立。

## 数据包检查

### 用十六进制和 ASCII 码打印数据包

```bash
#  tcpdump  -nvvv -i any -c 1 -XX 'port 80 and host 10.0.3.1'
```

排查应用程序网络问题的通常做法，就是用 `tcpdump` 的 `-XX` 标记打印出 16 进制和 ASCII 码格式的数据包。这是一个相当有用的命令，它可以让你看到源地址，目的地址，数据包类型以及数据包本身。但我不是这个命令输出的粉丝，我认为它太难读了。

```bash
# tcpdump -nvvv -i any -c 1 -XX 'port 80 and host 10.0.3.1'

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
19:51:15.697640 IP (tos 0x0, ttl 64, id 54313, offset 0, flags [DF], proto TCP (6), length 483)
    10.0.3.1.45732 > 10.0.3.246.80: Flags [P.], cksum 0x1ccc (incorrect -> 0x2ce8), seq 3920159713:3920160144, ack 969855140, win 245, options [nop,nop,TS val 624122099 ecr 624117334], length 431
        0x0000:  0000 0001 0006 fe0a e2d1 8785 0000 0800  ................
        0x0010:  4500 01e3 d429 4000 4006 49f5 0a00 0301  E....)@.@.I.....
        0x0020:  0a00 03f6 b2a4 0050 e9a8 e3e1 39ce d0a4  .......P....9...
        0x0030:  8018 00f5 1ccc 0000 0101 080a 2533 58f3  ............%3X.
        0x0040:  2533 4656 4745 5420 2f73 6f6d 6570 6167  %3FVGET./somepag
        0x0050:  6520 4854 5450 2f31 2e31 0d0a 486f 7374  e.HTTP/1.1..Host
        0x0060:  3a20 3130 2e30 2e33 2e32 3436 0d0a 436f  :.10.0.3.246..Co
        0x0070:  6e6e 6563 7469 6f6e 3a20 6b65 6570 2d61  nnection:.keep-a
        0x0080:  6c69 7665 0d0a 4361 6368 652d 436f 6e74  live..Cache-Cont
        0x0090:  726f 6c3a 206d 6178 2d61 6765 3d30 0d0a  rol:.max-age=0..
        0x00a0:  4163 6365 7074 3a20 7465 7874 2f68 746d  Accept:.text/htm
        0x00b0:  6c2c 6170 706c 6963 6174 696f 6e2f 7868  l,application/xh
        0x00c0:  746d 6c2b 786d 6c2c 6170 706c 6963 6174  tml+xml,applicat
        0x00d0:  696f 6e2f 786d 6c3b 713d 302e 392c 696d  ion/xml;q=0.9,im
        0x00e0:  6167 652f 7765 6270 2c2a 2f2a 3b71 3d30  age/webp,*/*;q=0
        0x00f0:  2e38 0d0a 5573 6572 2d41 6765 6e74 3a20  .8..User-Agent:.
        0x0100:  4d6f 7a69 6c6c 612f 352e 3020 284d 6163  Mozilla/5.0.(Mac
        0x0110:  696e 746f 7368 3b20 496e 7465 6c20 4d61  intosh;.Intel.Ma
        0x0120:  6320 4f53 2058 2031 305f 395f 3529 2041  c.OS.X.10_9_5).A
        0x0130:  7070 6c65 5765 624b 6974 2f35 3337 2e33  ppleWebKit/537.3
        0x0140:  3620 284b 4854 4d4c 2c20 6c69 6b65 2047  6.(KHTML,.like.G
        0x0150:  6563 6b6f 2920 4368 726f 6d65 2f33 382e  ecko).Chrome/38.
        0x0160:  302e 3231 3235 2e31 3031 2053 6166 6172  0.2125.101.Safar
        0x0170:  692f 3533 372e 3336 0d0a 4163 6365 7074  i/537.36..Accept
        0x0180:  2d45 6e63 6f64 696e 673a 2067 7a69 702c  -Encoding:.gzip,
        0x0190:  6465 666c 6174 652c 7364 6368 0d0a 4163  deflate,sdch..Ac
        0x01a0:  6365 7074 2d4c 616e 6775 6167 653a 2065  cept-Language:.e
        0x01b0:  6e2d 5553 2c65 6e3b 713d 302e 380d 0a49  n-US,en;q=0.8..I
        0x01c0:  662d 4d6f 6469 6669 6564 2d53 696e 6365  f-Modified-Since
        0x01d0:  3a20 5375 6e2c 2031 3220 4f63 7420 3230  :.Sun,.12.Oct.20
        0x01e0:  3134 2031 393a 3430 3a32 3020 474d 540d  14.19:40:20.GMT.
        0x01f0:  0a0d 0a                                  ...
```

### 只打印 ASCII 码格式的数据包

```bash
#  tcpdump  -nvvv -i any -c 1 -A 'port 80 and host 10.0.3.1'
```

我倾向于只打印 ASCII 格式数据，这可以帮助我快速定位数据包中发送了什么，哪些是正确的，哪些是错误的。你可以通过 `-A `标记来实现这一点。

```bash
# tcpdump -nvvv -i any -c 1 -A 'port 80 and host 10.0.3.1'

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
19:59:52.011337 IP (tos 0x0, ttl 64, id 53757, offset 0, flags [DF], proto TCP (6), length 406)
    10.0.3.1.46172 > 10.0.3.246.80: Flags [P.], cksum 0x1c7f (incorrect -> 0xead1), seq 1552520173:1552520527, ack 428165415, win 237, options [nop,nop,TS val 624251177 ecr 624247749], length 354
E.....@.@.Ln
...
....\.P\.....I'...........
%5Q)%5C.GET /newpage HTTP/1.1
 
Host: 10.0.3.246
Connection: keep-alive
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36
Accept-Encoding: gzip,deflate,sdch
Accept-Language: en-US,en;q=0.8
```

从上面的输出，你可以看到我们成功获取了一个 http 的 `GET` 请求包。如果网络通信没有被加密，用人类可阅读的格式打出包中数据，对于解决应用程序的问题是很有帮助。如果你排查一个网络通信被加密的问题，打印包中数据就不是很有用。不过如果你有证书的话，你还是可以使用 `ssldump` 或者 `wireshark`。

## 非 TCP 数据流

虽然这篇文章主要采用 TCP 传输来讲解 `tcpdump` ，但是 `tcpdump` 绝对不是只能抓 TCP 数据包。它还可以用来获取其他类型的数据包，例如 ICMP、 UDP 和 ARP 包。下面是一些简单的例子，说明 `tcpdump` 可以截获非 TCP 数据包。

### ICMP 数据包

```bash
# tcpdump -nvvv -i any -c 2 icmp

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
20:11:24.627824 IP (tos 0x0, ttl 64, id 0, offset 0, flags [DF], proto ICMP (1), length 84)
    10.0.3.169 > 10.0.3.246: ICMP echo request, id 15683, seq 1, length 64
20:11:24.627926 IP (tos 0x0, ttl 64, id 31312, offset 0, flags [none], proto ICMP (1), length 84)
    10.0.3.246 > 10.0.3.169: ICMP echo reply, id 15683, seq 1, length 64
```

### UDP 数据包

```bash
# tcpdump -nvvv -i any -c 2 udp

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked), capture size 65535 bytes
20:12:41.726355 IP (tos 0xc0, ttl 64, id 0, offset 0, flags [DF], proto UDP (17), length 76)
    10.0.3.246.123 > 198.55.111.50.123: [bad udp cksum 0x43a9 -> 0x7043!] NTPv4, length 48
        Client, Leap indicator: clock unsynchronized (192), Stratum 2 (secondary reference), poll 6 (64s), precision -22
        Root Delay: 0.085678, Root dispersion: 57.141830, Reference-ID: 199.102.46.75
          Reference Timestamp:  3622133515.811991035 (2014/10/12 20:11:55)
          Originator Timestamp: 3622133553.828614115 (2014/10/12 20:12:33)
          Receive Timestamp:    3622133496.748308420 (2014/10/12 20:11:36)
          Transmit Timestamp:   3622133561.726278364 (2014/10/12 20:12:41)
            Originator - Receive Timestamp:  -57.080305658
            Originator - Transmit Timestamp: +7.897664248
20:12:41.748948 IP (tos 0x0, ttl 54, id 9285, offset 0, flags [none], proto UDP (17), length 76)
    198.55.111.50.123 > 10.0.3.246.123: [udp sum ok] NTPv4, length 48
        Server, Leap indicator:  (0), Stratum 3 (secondary reference), poll 6 (64s), precision -20
        Root Delay: 0.054077, Root dispersion: 0.058944, Reference-ID: 216.229.0.50
          Reference Timestamp:  3622132887.136984840 (2014/10/12 20:01:27)
          Originator Timestamp: 3622133561.726278364 (2014/10/12 20:12:41)
          Receive Timestamp:    3622133618.830113530 (2014/10/12 20:13:38)
          Transmit Timestamp:   3622133618.830129086 (2014/10/12 20:13:38)
            Originator - Receive Timestamp:  +57.103835195
            Originator - Transmit Timestamp: +57.103850722
```

如果你觉得有好例子进一步说明 `tcpdump` 命令，可以加下面群交流。

## 文章来源

> bencane.com