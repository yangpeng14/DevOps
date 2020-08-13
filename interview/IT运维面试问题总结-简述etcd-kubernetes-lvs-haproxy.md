## 集群相关

### 简述ETCD及其特点？

etcd 是 CoreOS 团队发起的开源项目，是一个管理配置信息和服务发现（service discovery）的项目，它的目标是构建一个高可用的分布式键值（key-value）数据库，基于 Go 语言实现。

特点：

- 简单：支持 REST 风格的 HTTP+JSON API
- 安全：支持 HTTPS 方式的访问
- 快速：支持并发 1k/s 的写操作
- 可靠：支持分布式结构，基于 Raft 的一致性算法，Raft 是一套通过选举主节点来实现分布式系统一致性的算法。

### 简述ETCD适应的场景？

etcd基于其优秀的特点，可广泛的应用于以下场景：

- `服务发现`(Service Discovery)：服务发现主要解决在同一个分布式集群中的进程或服务，要如何才能找到对方并建立连接。本质上来说，服务发现就是想要了解集群中是否有进程在监听udp或tcp端口，并且通过名字就可以查找和连接。
- `消息发布与订阅`：在分布式系统中，最适用的一种组件间通信方式就是消息发布与订阅。即构建一个配置共享中心，数据提供者在这个配置中心发布消息，而消息使用者则订阅他们关心的主题，一旦主题有消息发布，就会实时通知订阅者。通过这种方式可以做到分布式系统配置的集中式管理与动态更新。 应用中用到的一些配置信息放到etcd上进行集中管理。
- `负载均衡`：在分布式系统中，为了保证服务的高可用以及数据的一致性，通常都会把数据和服务部署多份，以此达到对等服务，即使其中的某一个服务失效了，也不影响使用。etcd本身分布式架构存储的信息访问支持负载均衡。etcd集群化以后，每个etcd的核心节点都可以处理用户的请求。所以，把数据量小但是访问频繁的消息数据直接存储到etcd中也可以实现负载均衡的效果。
- `分布式通知与协调`：与消息发布和订阅类似，都用到了etcd中的Watcher机制，通过注册与异步通知机制，实现分布式环境下不同系统之间的通知与协调，从而对数据变更做到实时处理。
- `分布式锁`：因为etcd使用Raft算法保持了数据的强一致性，某次操作存储到集群中的值必然是全局一致的，所以很容易实现分布式锁。锁服务有两种使用方式，一是保持独占，二是控制时序。
- `集群监控与Leader竞选`：通过etcd来进行监控实现起来非常简单并且实时性强。

### 简述HAProxy及其特性？

HAProxy是可提供高可用性、负载均衡以及基于TCP和HTTP应用的代理，是免费、快速并且可靠的一种解决方案。HAProxy非常适用于并发大（并发达1w以上）web站点，这些站点通常又需要会话保持或七层处理。HAProxy的运行模式使得它可以很简单安全的整合至当前的架构中，同时可以保护web服务器不被暴露到网络上。

HAProxy的主要特性有：

- 可靠性和稳定性非常好，可以与硬件级的F5负载均衡设备相媲美；
- 最高可以同时维护40000-50000个并发连接，单位时间内处理的最大请求数为20000个，最大处理能力可达10Git/s；
- 支持多达8种负载均衡算法，同时也支持会话保持；
- 支持虚机主机功能，从而实现web负载均衡更加灵活；
- 支持连接拒绝、全透明代理等独特的功能；
- 拥有强大的ACL支持，用于访问控制；
- 其独特的弹性二叉树数据结构，使数据结构的复杂性上升到了0(1)，即数据的查寻速度不会随着数据条目的增加而速度有所下降；
- 支持客户端的keepalive功能，减少客户端与haproxy的多次三次握手导致资源浪费，让多个请求在一个tcp连接中完成；
- 支持TCP加速，零复制功能，类似于mmap机制；
- 支持响应池（response buffering）；
- 支持RDP协议；
- 基于源的粘性，类似nginx的ip_hash功能，把来自同一客户端的请求在一定时间内始终调度到上游的同一服务器；
- 更好统计数据接口，其web接口显示后端集群中各个服务器的接收、发送、拒绝、错误等数据的统计信息；
- 详细的健康状态检测，web接口中有关于对上游服务器的健康检测状态，并提供了一定的管理功能；
- 基于流量的健康评估机制；
- 基于http认证；
- 基于命令行的管理接口；
- 日志分析器，可对日志进行分析。

### 简述HAProxy常见的负载均衡策略？

HAProxy负载均衡策略非常多，常见的有如下8种：

- roundrobin：表示简单的轮询。
- static-rr：表示根据权重。
- leastconn：表示最少连接者先处理。
- source：表示根据请求的源IP，类似Nginx的IP_hash机制。
- ri：表示根据请求的URI。
- rl_param：表示根据HTTP请求头来锁定每一次HTTP请求。
- rdp-cookie(name)：表示根据据cookie(name)来锁定并哈希每一次TCP请求。

### 简述负载均衡四层和七层的区别？

`四层负载均衡器`也称为4层交换机，主要通过分析IP层及TCP/UDP层的流量实现基于IP加端口的负载均衡，如常见的LVS、F5等；

`七层负载均衡器`也称为7层交换机，位于OSI的最高层，即应用层，此负载均衡器支持多种协议，如HTTP、FTP、SMTP等。7层负载均衡器可根据报文内容，配合一定的负载均衡算法来选择后端服务器，即“内容交换器”。如常见的HAProxy、Nginx。

### 简述LVS、Nginx、HAproxy的什么异同？

- 相同：
    三者都是软件负载均衡产品。

- 区别：
    - LVS基于Linux操作系统实现软负载均衡，而HAProxy和Nginx是基于第三方应用实现的软负载均衡；
    - LVS是可实现4层的IP负载均衡技术，无法实现基于目录、URL的转发。而HAProxy和Nginx都可以实现4层和7层技术，HAProxy可提供TCP和HTTP应用的负载均衡综合解决方案；
    - LVS因为工作在ISO模型的第四层，其状态监测功能单一，而HAProxy在状监测方面功能更丰富、强大，可支持端口、URL、脚本等多种状态检测方式；
    - HAProxy功能强大，但整体性能低于4层模式的LVS负载均衡。
    - Nginx主要用于Web服务器或缓存服务器。

### 简述Heartbeat？

Heartbeat是Linux-HA项目中的一个组件，它提供了心跳检测和资源接管、集群中服务的监测、失效切换等功能。heartbeat最核心的功能包括两个部分，心跳监测和资源接管。心跳监测可以通过网络链路和串口进行，而且支持冗余链路，它们之间相互发送报文来告诉对方自己当前的状态，如果在指定的时间内未收到对方发送的报文，那么就认为对方失效，这时需启动资源接管模块来接管运行在对方主机上的资源或者服务。

### 简述Keepalived及其工作原理？

Keepalived 是一个基于VRRP协议来实现的LVS服务高可用方案，可以解决静态路由出现的单点故障问题。

在一个LVS服务集群中通常有主服务器（MASTER）和备份服务器（BACKUP）两种角色的服务器，但是对外表现为一个虚拟IP，主服务器会发送VRRP通告信息给备份服务器，当备份服务器收不到VRRP消息的时候，即主服务器异常的时候，备份服务器就会接管虚拟IP，继续提供服务，从而保证了高可用性。

### 简述Keepalived体系主要模块及其作用？

keepalived体系架构中主要有三个模块，分别是core、check和vrrp。

- `core模块`为keepalived的核心，负责主进程的启动、维护及全局配置文件的加载和解析。
- `vrrp模块`是来实现VRRP协议的。
- `check`负责健康检查，常见的方式有端口检查及URL检查。

### 简述Keepalived如何通过健康检查来保证高可用？

Keepalived工作在TCP/IP模型的第三、四和五层，即网络层、传输层和应用层。 

- `网络层`，Keepalived采用ICMP协议向服务器集群中的每个节点发送一个ICMP的数据包，如果某个节点没有返回响应数据包，则认为此节点发生了故障，Keepalived将报告次节点失效，并从服务器集群中剔除故障节点。
- `传输层`，Keepalived利用TCP的端口连接和扫描技术来判断集群节点是否正常。如常见的web服务默认端口80，ssh默认端口22等。Keepalived一旦在传输层探测到相应端口没用响应数据返回，则认为此端口发生异常，从而将此端口对应的节点从服务器集群中剔除。
- `应用层`，可以运行FTP、telnet、smtp、dns等各种不同类型的高层协议，Keepalived的运行方式也更加全面化和复杂化，用户可以通过自定义Keepalived的工作方式，来设定监测各种程序或服务是否正常，若监测结果与设定的正常结果不一致，将此服务对应的节点从服务器集群中剔除。 

Keepalived通过完整的健康检查机制，保证集群中的所有节点均有效从而实现高可用。

### 简述LVS的概念及其作用？

LVS是linux virtual server的简写linux虚拟服务器，是一个虚拟的服务器集群系统，可以在unix/linux平台下实现负载均衡集群功能。

LVS的主要作用是：通过LVS提供的负载均衡技术实现一个高性能、高可用的服务器群集。因此LVS主要可以实现：

- 把单台计算机无法承受的大规模的并发访问或数据流量分担到多台节点设备上分别处理，减少用户等待响应的时间，提升用户体验。
- 单个重负载的运算分担到多台节点设备上做并行处理，每个节点设备处理结束后，将结果汇总，返回给用户，系统处理能力得到大幅度提高。
- 7*24小时的服务保证，任意一个或多个设备节点设备宕机，不能影响到业务。在负载均衡集群中，所有计算机节点都应该提供相同的服务，集群负载均衡获取所有对该服务的如站请求。

### 简述LVS的工作模式及其工作过程？

LVS 有三种负载均衡的模式，分别是VS/NAT（nat 模式）、VS/DR（路由模式）、VS/TUN（隧道模式）。

- NAT模式（VS-NAT）

    - `原理`：首先负载均衡器接收到客户的请求数据包时，根据调度算法决定将请求发送给哪个后端的真实服务器（RS）。然后负载均衡器就把客户端发送的请求数据包的目标IP地址及端口改成后端真实服务器的IP地址（RIP）。真实服务器响应完请求后，查看默认路由，把响应后的数据包发送给负载均衡器，负载均衡器在接收到响应包后，把包的源地址改成虚拟地址（VIP）然后发送回给客户端。
    - `优点`：集群中的服务器可以使用任何支持TCP/IP的操作系统，只要负载均衡器有一个合法的IP地址。
    - `缺点`：扩展性有限，当服务器节点增长过多时，由于所有的请求和应答都需要经过负载均衡器，因此负载均衡器将成为整个系统的瓶颈。
- IP隧道模式（VS-TUN）
    - `原理`：首先负载均衡器接收到客户的请求数据包时，根据调度算法决定将请求发送给哪个后端的真实服务器（RS）。然后负载均衡器就把客户端发送的请求报文封装一层IP隧道（T-IP）转发到真实服务器（RS）。真实服务器响应完请求后，查看默认路由，把响应后的数据包直接发送给客户端，不需要经过负载均衡器。
    - `优点`：负载均衡器只负责将请求包分发给后端节点服务器，而RS将应答包直接发给用户。所以，减少了负载均衡器的大量数据流动，负载均衡器不再是系统的瓶颈，也能处理很巨大的请求量。
    - `缺点`：隧道模式的RS节点需要合法IP，这种方式需要所有的服务器支持“IP Tunneling”。
- 直接路由模式（VS-DR）
    - `原理`：首先负载均衡器接收到客户的请求数据包时，根据调度算法决定将请求发送给哪个后端的真实服务器（RS）。然后负载均衡器就把客户端发送的请求数据包的目标MAC地址改成后端真实服务器的MAC地址（R-MAC）。真实服务器响应完请求后，查看默认路由，把响应后的数据包直接发送给客户端，不需要经过负载均衡器。
    - `优点`：负载均衡器只负责将请求包分发给后端节点服务器，而RS将应答包直接发给用户。所以，减少了负载均衡器的大量数据流动，负载均衡器不再是系统的瓶颈，也能处理很巨大的请求量。
    - `缺点`：需要负载均衡器与真实服务器RS都有一块网卡连接到同一物理网段上，必须在同一个局域网环境。

### 简述LVS调度器常见算法（均衡策略）？

LVS调度器用的调度方法基本分为两类：

- 固定调度算法：rr，wrr，dh，sh
    - rr：轮询算法，将请求依次分配给不同的rs节点，即RS节点中均摊分配。适合于RS所有节点处理性能接近的情况。
    - wrr：加权轮训调度，依据不同RS的权值分配任务。权值较高的RS将优先获得任务，并且分配到的连接数将比权值低的RS更多。相同权值的RS得到相同数目的连接数。
    - dh：目的地址哈希调度（destination hashing）以目的地址为关键字查找一个静态hash表来获得所需RS。
    - sh：源地址哈希调度（source hashing）以源地址为关键字查找一个静态hash表来获得需要的RS。
- 动态调度算法：wlc，lc，lblc，lblcr
    - wlc：加权最小连接数调度，假设各台RS的权值依次为Wi，当前tcp连接数依次为Ti，依次去Ti/Wi为最小的RS作为下一个分配的RS。
    - lc：最小连接数调度（least-connection），IPVS表存储了所有活动的连接。LB会比较将连接请求发送到当前连接最少的RS。
    - lblc：基于地址的最小连接数调度（locality-based least-connection）：将来自同一个目的地址的请求分配给同一台RS，此时这台服务器是尚未满负荷的。否则就将这个请求分配给连接数最小的RS，并以它作为下一次分配的首先考虑。

### 简述LVS、Nginx、HAProxy各自优缺点？

- Nginx的优点：
    - 工作在网络的7层之上，可以针对http应用做一些分流的策略，比如针对域名、目录结构。Nginx正则规则比HAProxy更为强大和灵活。
    - Nginx对网络稳定性的依赖非常小，理论上能ping通就就能进行负载功能，LVS对网络稳定性依赖比较大，稳定要求相对更高。
    - Nginx安装和配置、测试比较简单、方便，有清晰的日志用于排查和管理，LVS的配置、测试就要花比较长的时间了。
    - 可以承担高负载压力且稳定，一般能支撑几万次的并发量，负载度比LVS相对小些。
    - Nginx可以通过端口检测到服务器内部的故障，比如根据服务器处理网页返回的状态码、超时等等。
    - Nginx不仅仅是一款优秀的负载均衡器/反向代理软件，它同时也是功能强大的Web应用服务器。
    - Nginx作为Web反向加速缓存越来越成熟了，速度比传统的Squid服务器更快，很多场景下都将其作为反向代理加速器。
    - Nginx作为静态网页和图片服务器，这方面的性能非常优秀，同时第三方模块也很多。
- Nginx的缺点：
    - Nginx仅能支持http、https和Email协议，这样就在适用范围上面小些。
    - 对后端服务器的健康检查，只支持通过端口来检测，不支持通过url来检测。
    - 不支持Session的直接保持，需要通过ip_hash来解决。
- LVS的优点：
    - 抗负载能力强、是工作在网络4层之上仅作分发之用，没有流量的产生。因此负载均衡软件里的性能最强的，对内存和cpu资源消耗比较低。
    - LVS工作稳定，因为其本身抗负载能力很强，自身有完整的双机热备方案。
    - 无流量，LVS只分发请求，而流量并不从它本身出去，这点保证了均衡器IO的性能不会收到大流量的影响。
    - 应用范围较广，因为LVS工作在4层，所以它几乎可对所有应用做负载均衡，包括http、数据库等。
- LVS的缺点是：
    - 软件本身不支持正则表达式处理，不能做动静分离。相对来说，Nginx/HAProxy+Keepalived则具有明显的优势。
    - 如果是网站应用比较庞大的话，LVS/DR+Keepalived实施起来就比较复杂了。相对来说，Nginx/HAProxy+Keepalived就简单多了。
- HAProxy的优点：
    - HAProxy也是支持虚拟主机的。
    - HAProxy的优点能够补充Nginx的一些缺点，比如支持Session的保持，Cookie的引导，同时支持通过获取指定的url来检测后端服务器的状态。
    - HAProxy跟LVS类似，本身就只是一款负载均衡软件，单纯从效率上来讲HAProxy会比Nginx有更出色的负载均衡速度，在并发处理上也是优于Nginx的。
    - HAProxy支持TCP协议的负载均衡转发。

### 简述代理服务器的概念及其作用？

代理服务器是一个位于客户端和原始（资源）服务器之间的服务器，为了从原始服务器取得内容，客户端向代理服务器发送一个请求并指定目标原始服务器，然后代理服务器向原始服务器转交请求并将获得的内容返回给客户端。

其主要作用有：

- 资源获取：代替客户端实现从原始服务器的资源获取；
- 加速访问：代理服务器可能离原始服务器更近，从而起到一定的加速作用；
- 缓存作用：代理服务器保存从原始服务器所获取的资源，从而实现客户端快速的获取；
- 隐藏真实地址：代理服务器代替客户端去获取原始服务器资源，从而隐藏客户端真实信息。

### 简述高可用集群可通过哪两个维度衡量高可用性，各自含义是什么？

- RTO（Recovery Time Objective）：RTO指服务恢复的时间，最佳的情况是 0，即服务立即恢复；最坏是无穷大，即服务永远无法恢复；
- RPO（Recovery Point Objective）：RPO 指指当灾难发生时允许丢失的数据量，0 意味着使用同步的数据，大于 0 意味着有数据丢失，如“RPO=1 d”指恢复时使用一天前的数据，那么一天之内的数据就丢失了。因此，恢复的最佳情况是 RTO = RPO = 0，几乎无法实现。

### 简述什么是CAP理论？

CAP理论指出了在分布式系统中需要满足的三个条件，主要包括：

- Consistency（一致性）：所有节点在同一时间具有相同的数据；
- Availability（可用性）：保证每个请求不管成功或者失败都有响应；
- Partition tolerance（分区容错性）：系统中任意信息的丢失或失败不影响系统的继续运行。

CAP 理论的核心是：一个分布式系统不可能同时很好的满足一致性，可用性和分区容错性这三个需求，最多只能同时较好的满足两个。 

### 简述什么是ACID理论？

- 原子性(Atomicity)：整体不可分割性，要么全做要不全不做；
- 一致性(Consistency)：事务执行前、后数据库状态均一致；
- 隔离性(Isolation)：在事务未提交前，它操作的数据，对其它用户不可见；
- 持久性 (Durable)：一旦事务成功，将进行永久的变更，记录与redo日志。 

### 简述什么是Kubernetes？

Kubernetes是一个全新的基于容器技术的分布式系统支撑平台。是Google开源的容器集群管理系统（谷歌内部:Borg）。在Docker技术的基础上，为容器化的应用提供部署运行、资源调度、服务发现和动态伸缩等一系列完整功能，提高了大规模容器集群管理的便捷性。并且具有完备的集群管理能力，多层次的安全防护和准入机制、多租户应用支撑能力、透明的服务注册和发现机制、內建智能负载均衡器、强大的故障发现和自我修复能力、服务滚动升级和在线扩容能力、可扩展的资源自动调度机制以及多粒度的资源配额管理能力。 

### 简述Kubernetes和Docker的关系？

Docker 提供容器的生命周期管理和，Docker 镜像构建运行时容器。它的主要优点是将将软件/应用程序运行所需的设置和依赖项打包到一个容器中，从而实现了可移植性等优点。

Kubernetes 用于关联和编排在多个主机上运行的容器。

### 简述Kubernetes中什么是Minikube、Kubectl、Kubelet？

`Minikube` 是一种可以在本地轻松运行一个单节点 Kubernetes 群集的工具。

`Kubectl` 是一个命令行工具，可以使用该工具控制Kubernetes集群管理器，如检查群集资源，创建、删除和更新组件，查看应用程序。

`Kubelet` 是一个代理服务，它在每个节点上运行，并使从服务器与主服务器通信。

### 简述Kubernetes常见的部署方式？

常见的Kubernetes部署方式有：

- kubeadm：也是推荐的一种部署方式；
- 二进制：
- minikube：在本地轻松运行一个单节点 Kubernetes 群集的工具。

### 简述Kubernetes如何实现集群管理？

在集群管理方面，Kubernetes将集群中的机器划分为一个Master节点和一群工作节点Node。其中，在Master节点运行着集群管理相关的一组进程kube-apiserver、kube-controller-manager和kube-scheduler，这些进程实现了整个集群的资源管理、Pod调度、弹性伸缩、安全控制、系统监控和纠错等管理能力，并且都是全自动完成的。 

### 简述Kubernetes的优势、适应场景及其特点？

Kubernetes作为一个完备的分布式系统支撑平台，其主要优势：

- 容器编排
- 轻量级
- 开源
- 弹性伸缩
- 负载均衡

Kubernetes常见场景：

- 快速部署应用
- 快速扩展应用
- 无缝对接新的应用功能
- 节省资源，优化硬件资源的使用

Kubernetes相关特点：

- 可移植: 支持公有云、私有云、混合云、多重云（multi-cloud）。
- 可扩展: 模块化,、插件化、可挂载、可组合。
- 自动化: 自动部署、自动重启、自动复制、自动伸缩/扩展。

### 简述Kubernetes的缺点或当前的不足之处？

Kubernetes当前存在的缺点（不足）如下：

- 安装过程和配置相对困难复杂。
- 管理服务相对繁琐。
- 运行和编译需要很多时间。
- 它比其他替代品更昂贵。
- 对于简单的应用程序来说，可能不需要涉及Kubernetes即可满足。

### 简述Kubernetes相关基础概念？

- `master`：k8s集群的管理节点，负责管理集群，提供集群的资源数据访问入口。拥有Etcd存储服务（可选），运行Api Server进程，Controller Manager服务进程及Scheduler服务进程。
- `node`（worker）：Node（worker）是Kubernetes集群架构中运行Pod的服务节点，是Kubernetes集群操作的单元，用来承载被分配Pod的运行，是Pod运行的宿主机。运行docker eninge服务，守护进程kunelet及负载均衡器kube-proxy。
- `pod`：运行于Node节点上，若干相关容器的组合。Pod内包含的容器运行在同一宿主机上，使用相同的网络命名空间、IP地址和端口，能够通过localhost进行通信。Pod是Kurbernetes进行创建、调度和管理的最小单位，它提供了比容器更高层次的抽象，使得部署和管理更加灵活。一个Pod可以包含一个容器或者多个相关容器。
- `label`：Kubernetes中的Label实质是一系列的Key/Value键值对，其中key与value可自定义。Label可以附加到各种资源对象上，如Node、Pod、Service、RC等。一个资源对象可以定义任意数量的Label，同一个Label也可以被添加到任意数量的资源对象上去。Kubernetes通过Label Selector（标签选择器）查询和筛选资源对象。
- `Replication Controller`：Replication Controller用来管理Pod的副本，保证集群中存在指定数量的Pod副本。集群中副本的数量大于指定数量，则会停止指定数量之外的多余容器数量。反之，则会启动少于指定数量个数的容器，保证数量不变。Replication Controller是实现弹性伸缩、动态扩容和滚动升级的核心。
- `Deployment`：Deployment在内部使用了RS来实现目的，Deployment相当于RC的一次升级，其最大的特色为可以随时获知当前Pod的部署进度。
- `HPA`（Horizontal Pod Autoscaler）：Pod的横向自动扩容，也是Kubernetes的一种资源，通过追踪分析RC控制的所有Pod目标的负载变化情况，来确定是否需要针对性的调整Pod副本数量。
- `Service`：Service定义了Pod的逻辑集合和访问该集合的策略，是真实服务的抽象。Service提供了一个统一的服务访问入口以及服务代理和发现机制，关联多个相同Label的Pod，用户不需要了解后台Pod是如何运行。
- `Volume`：Volume是Pod中能够被多个容器访问的共享目录，Kubernetes中的Volume是定义在Pod上，可以被一个或多个Pod中的容器挂载到某个目录下。
- `Namespace`：Namespace用于实现多租户的资源隔离，可将集群内部的资源对象分配到不同的Namespace中，形成逻辑上的不同项目、小组或用户组，便于不同的Namespace在共享使用整个集群的资源的同时还能被分别管理。

### 简述Kubernetes集群相关组件？

Kubernetes Master控制组件，调度管理整个系统（集群），包含如下组件:

- `Kubernetes API Server`：作为Kubernetes系统的入口，其封装了核心对象的增删改查操作，以RESTful API接口方式提供给外部客户和内部组件调用，集群内各个功能模块之间数据交互和通信的中心枢纽。
- `Kubernetes Scheduler`：为新建立的Pod进行节点(node)选择(即分配机器)，负责集群的资源调度。
- `Kubernetes Controller`：负责执行各种控制器，目前已经提供了很多控制器来保证Kubernetes的正常运行。
- `Replication Controller`：管理维护Replication Controller，关联Replication Controller和Pod，保证Replication Controller定义的副本数量与实际运行Pod数量一致。
- `Node Controller`：管理维护Node，定期检查Node的健康状态，标识出(失效|未失效)的Node节点。
- `Namespace Controller`：管理维护Namespace，定期清理无效的Namespace，包括Namesapce下的API对象，比如Pod、Service等。
- `Service Controller`：管理维护Service，提供负载以及服务代理。
- `EndPoints Controller`：管理维护Endpoints，关联Service和Pod，创建Endpoints为Service的后端，当Pod发生变化时，实时更新Endpoints。
- `Service Account Controller`：管理维护Service Account，为每个Namespace创建默认的Service Account，同时为Service Account创建Service Account Secret。
- `Persistent Volume Controller`：管理维护Persistent Volume和Persistent Volume Claim，为新的Persistent Volume Claim分配Persistent Volume进行绑定，为释放的Persistent Volume执行清理回收。
- `Daemon Set Controller`：管理维护Daemon Set，负责创建Daemon Pod，保证指定的Node上正常的运行Daemon Pod。
- `Deployment Controller`：管理维护Deployment，关联Deployment和Replication Controller，保证运行指定数量的Pod。当Deployment更新时，控制实现Replication Controller和Pod的更新。
- `Job Controller`：管理维护Job，为Jod创建一次性任务Pod，保证完成Job指定完成的任务数目
- `Pod Autoscaler Controller`：实现Pod的自动伸缩，定时获取监控数据，进行策略匹配，当满足条件时执行Pod的伸缩动作。

### 简述Kubernetes RC的机制？

Replication Controller用来管理Pod的副本，保证集群中存在指定数量的Pod副本。当定义了RC并提交至Kubernetes集群中之后，Master节点上的Controller Manager组件获悉，并同时巡检系统中当前存活的目标Pod，并确保目标Pod实例的数量刚好等于此RC的期望值，若存在过多的Pod副本在运行，系统会停止一些Pod，反之则自动创建一些Pod。

### 简述Kubernetes Replica Set 和 Replication Controller 之间有什么区别？

Replica Set 和 Replication Controller 类似，都是确保在任何给定时间运行指定数量的 Pod 副本。不同之处在于RS 使用基于集合的选择器，而 Replication Controller 使用基于权限的选择器。

### 简述kube-proxy作用？

kube-proxy 运行在所有节点上，它监听 apiserver 中 service 和 endpoint 的变化情况，创建路由规则以提供服务 IP 和负载均衡功能。简单理解此进程是Service的透明代理兼负载均衡器，其核心功能是将到某个Service的访问请求转发到后端的多个Pod实例上。

### 简述kube-proxy iptables原理？

Kubernetes从1.2版本开始，将iptables作为kube-proxy的默认模式。iptables模式下的kube-proxy不再起到Proxy的作用，其核心功能：通过API Server的Watch接口实时跟踪Service与Endpoint的变更信息，并更新对应的iptables规则，Client的请求流量则通过iptables的NAT机制“直接路由”到目标Pod。

### 简述kube-proxy ipvs原理？

IPVS在Kubernetes1.11中升级为GA稳定版。IPVS则专门用于高性能负载均衡，并使用更高效的数据结构（Hash表），允许几乎无限的规模扩张，因此被kube-proxy采纳为最新模式。

在IPVS模式下，使用iptables的扩展ipset，而不是直接调用iptables来生成规则链。iptables规则链是一个线性的数据结构，ipset则引入了带索引的数据结构，因此当规则很多时，也可以很高效地查找和匹配。

可以将ipset简单理解为一个IP（段）的集合，这个集合的内容可以是IP地址、IP网段、端口等，iptables可以直接添加规则对这个“可变的集合”进行操作，这样做的好处在于可以大大减少iptables规则的数量，从而减少性能损耗。

### 简述kube-proxy ipvs和iptables的异同？

iptables与IPVS都是基于Netfilter实现的，但因为定位不同，二者有着本质的差别：iptables是为防火墙而设计的；IPVS则专门用于高性能负载均衡，并使用更高效的数据结构（Hash表），允许几乎无限的规模扩张。

与iptables相比，IPVS拥有以下明显优势：

- 1、为大型集群提供了更好的可扩展性和性能；
- 2、支持比iptables更复杂的复制均衡算法（最小负载、最少连接、加权等）；
- 3、支持服务器健康检查和连接重试等功能；
- 4、可以动态修改ipset的集合，即使iptables的规则正在使用这个集合。

### 简述Kubernetes中什么是静态Pod？

静态pod是由kubelet进行管理的仅存在于特定Node的Pod上，他们不能通过API Server进行管理，无法与ReplicationController、Deployment或者DaemonSet进行关联，并且kubelet无法对他们进行健康检查。静态Pod总是由kubelet进行创建，并且总是在kubelet所在的Node上运行。

### 简述Kubernetes中Pod可能位于的状态？

- `Pending`：API Server已经创建该Pod，且Pod内还有一个或多个容器的镜像没有创建，包括正在下载镜像的过程。
- `Running`：Pod内所有容器均已创建，且至少有一个容器处于运行状态、正在启动状态或正在重启状态。
- `Succeeded`：Pod内所有容器均成功执行退出，且不会重启。
- `Failed`：Pod内所有容器均已退出，但至少有一个容器退出为失败状态。
- `Unknown`：由于某种原因无法获取该Pod状态，可能由于网络通信不畅导致。

### 简述Kubernetes创建一个Pod的主要流程？

Kubernetes中创建一个Pod涉及多个组件之间联动，主要流程如下：

- 1、客户端提交Pod的配置信息（可以是yaml文件定义的信息）到kube-apiserver。
- 2、Apiserver收到指令后，通知给controller-manager创建一个资源对象。
- 3、Controller-manager通过api-server将pod的配置信息存储到ETCD数据中心中。
- 4、Kube-scheduler检测到pod信息会开始调度预选，会先过滤掉不符合Pod资源配置要求的节点，然后开始调度调优，主要是挑选出更适合运行pod的节点，然后将pod的资源配置单发送到node节点上的kubelet组件上。
- 5、Kubelet根据scheduler发来的资源配置单运行pod，运行成功后，将pod的运行信息返回给scheduler，scheduler将返回的pod运行状况的信息存储到etcd数据中心。

### 简述Kubernetes中Pod的重启策略？

Pod重启策略（RestartPolicy）应用于Pod内的所有容器，并且仅在Pod所处的Node上由kubelet进行判断和重启操作。当某个容器异常退出或者健康检查失败时，kubelet将根据RestartPolicy的设置来进行相应操作。

Pod的重启策略包括Always、OnFailure和Never，默认值为Always。

- `Always`：当容器失效时，由kubelet自动重启该容器；
- `OnFailure`：当容器终止运行且退出码不为0时，由kubelet自动重启该容器；
- `Never`：不论容器运行状态如何，kubelet都不会重启该容器。

同时Pod的重启策略与控制方式关联，当前可用于管理Pod的控制器包括ReplicationController、Job、DaemonSet及直接管理kubelet管理（静态Pod）。

不同控制器的重启策略限制如下：

- RC和DaemonSet：必须设置为Always，需要保证该容器持续运行；
- Job：OnFailure或Never，确保容器执行完成后不再重启；
- kubelet：在Pod失效时重启，不论将RestartPolicy设置为何值，也不会对Pod进行健康检查。

### 简述Kubernetes中Pod的健康检查方式？

对Pod的健康检查可以通过两类探针来检查：LivenessProbe和ReadinessProbe。

- `LivenessProbe探针`：用于判断容器是否存活（running状态），如果LivenessProbe探针探测到容器不健康，则kubelet将杀掉该容器，并根据容器的重启策略做相应处理。若一个容器不包含LivenessProbe探针，kubelet认为该容器的LivenessProbe探针返回值用于是“Success”。
- `ReadineeProbe探针`：用于判断容器是否启动完成（ready状态）。如果ReadinessProbe探针探测到失败，则Pod的状态将被修改。Endpoint Controller将从Service的Endpoint中删除包含该容器所在Pod的Eenpoint。
- `startupProbe探针`：启动检查机制，应用一些启动缓慢的业务，避免业务长时间启动而被上面两类探针kill掉。

### 简述Kubernetes Pod的LivenessProbe探针的常见方式？

kubelet定期执行LivenessProbe探针来诊断容器的健康状态，通常有以下三种方式：

- `ExecAction`：在容器内执行一个命令，若返回码为0，则表明容器健康。
- `TCPSocketAction`：通过容器的IP地址和端口号执行TCP检查，若能建立TCP连接，则表明容器健康。
- `HTTPGetAction`：通过容器的IP地址、端口号及路径调用HTTP Get方法，若响应的状态码大于等于200且小于400，则表明容器健康。

### 简述Kubernetes Pod的常见调度方式？

Kubernetes中，Pod通常是容器的载体，主要有如下常见调度方式：

- Deployment或RC：该调度策略主要功能就是自动部署一个容器应用的多份副本，以及持续监控副本的数量，在集群内始终维持用户指定的副本数量。
- NodeSelector：定向调度，当需要手动指定将Pod调度到特定Node上，可以通过Node的标签（Label）和Pod的nodeSelector属性相匹配。
- NodeAffinity亲和性调度：亲和性调度机制极大的扩展了Pod的调度能力，目前有两种节点亲和力表达：
- requiredDuringSchedulingIgnoredDuringExecution：硬规则，必须满足指定的规则，调度器才可以调度Pod至Node上（类似nodeSelector，语法不同）。
- preferredDuringSchedulingIgnoredDuringExecution：软规则，优先调度至满足的Node的节点，但不强求，多个优先级规则还可以设置权重值。
- Taints和Tolerations（污点和容忍）：
- Taint：使Node拒绝特定Pod运行；
- Toleration：为Pod的属性，表示Pod能容忍（运行）标注了Taint的Node。

### 简述Kubernetes初始化容器（init container）？

`init container`的运行方式与应用容器不同，它们必须先于应用容器执行完成，当设置了多个init container时，将按顺序逐个运行，并且只有前一个init container运行成功后才能运行后一个init container。当所有init container都成功运行后，Kubernetes才会初始化Pod的各种信息，并开始创建和运行应用容器。

### 简述Kubernetes deployment升级过程？

- 初始创建Deployment时，系统创建了一个ReplicaSet，并按用户的需求创建了对应数量的Pod副本。
- 当更新Deployment时，系统创建了一个新的ReplicaSet，并将其副本数量扩展到1，然后将旧ReplicaSet缩减为2。
- 之后，系统继续按照相同的更新策略对新旧两个ReplicaSet进行逐个调整。
- 最后，新的ReplicaSet运行了对应个新版本Pod副本，旧的ReplicaSet副本数量则缩减为0。

### 简述Kubernetes deployment升级策略？

在Deployment的定义中，可以通过spec.strategy指定Pod更新的策略，目前支持两种策略：Recreate（重建）和RollingUpdate（滚动更新），默认值为RollingUpdate。

- `Recreate`：设置spec.strategy.type=Recreate，表示Deployment在更新Pod时，会先杀掉所有正在运行的Pod，然后创建新的Pod。
- `RollingUpdate`：设置spec.strategy.type=RollingUpdate，表示Deployment会以滚动更新的方式来逐个更新Pod。同时，可以通过设置spec.strategy.rollingUpdate下的两个参数（maxUnavailable和maxSurge）来控制滚动更新的过程。

### 简述Kubernetes DaemonSet类型的资源特性？

DaemonSet资源对象会在每个Kubernetes集群中的节点上运行，并且每个节点只能运行一个pod，这是它和deployment资源对象的最大也是唯一的区别。因此，在定义yaml文件中，不支持定义replicas。

它的一般使用场景如下：

- 在去做每个节点的日志收集工作。
- 监控每个节点的的运行状态。

### 简述Kubernetes自动扩容机制？

Kubernetes使用Horizontal Pod Autoscaler（HPA）的控制器实现基于CPU使用率进行自动Pod扩缩容的功能。HPA控制器周期性地监测目标Pod的资源性能指标，并与HPA资源对象中的扩缩容条件进行对比，在满足条件时对Pod副本数量进行调整。

- HPA原理

Kubernetes中的某个Metrics Server（Heapster或自定义Metrics Server）持续采集所有Pod副本的指标数据。HPA控制器通过Metrics Server的API（Heapster的API或聚合API）获取这些数据，基于用户定义的扩缩容规则进行计算，得到目标Pod副本数量。

当目标Pod副本数量与当前副本数量不同时，HPA控制器就向Pod的副本控制器（Deployment、RC或ReplicaSet）发起scale操作，调整Pod的副本数量，完成扩缩容操作。

### 简述Kubernetes Service类型？

通过创建Service，可以为一组具有相同功能的容器应用提供一个统一的入口地址，并且将请求负载分发到后端的各个容器应用上。 其主要类型有：
- `ClusterIP`：虚拟的服务IP地址，该地址用于Kubernetes集群内部的Pod访问，在Node上kube-proxy通过设置的iptables规则进行转发；
- `NodePort`：使用宿主机的端口，使能够访问各Node的外部客户端通过Node的IP地址和端口号就能访问服务；
- `LoadBalancer`：使用外接负载均衡器完成到服务的负载分发，需要在spec.status.loadBalancer字段指定外部负载均衡器的IP地址，通常用于公有云。

### 简述Kubernetes Service分发后端的策略？

Service负载分发的策略有：RoundRobin和SessionAffinity

- RoundRobin：默认为轮询模式，即轮询将请求转发到后端的各个Pod上。
- SessionAffinity：基于客户端IP地址进行会话保持的模式，即第1次将某个客户端发起的请求转发到后端的某个Pod上，之后从相同的客户端发起的请求都将被转发到后端相同的Pod上。

### 简述Kubernetes Headless Service？

在某些应用场景中，若需要人为指定负载均衡器，不使用Service提供的默认负载均衡的功能，或者应用程序希望知道属于同组服务的其他实例。Kubernetes提供了Headless Service来实现这种功能，即不为Service设置ClusterIP（入口IP地址），仅通过Label Selector将后端的Pod列表返回给调用的客户端。

### 简述Kubernetes外部如何访问集群内的服务？

对于Kubernetes，集群外的客户端默认情况，无法通过Pod的IP地址或者Service的虚拟IP地址:虚拟端口号进行访问。通常可以通过以下方式进行访问Kubernetes集群内的服务：
- 映射Pod到物理机：将Pod端口号映射到宿主机，即在Pod中采用hostPort方式，以使客户端应用能够通过物理机访问容器应用。
- 映射Service到物理机：将Service端口号映射到宿主机，即在Service中采用nodePort方式，以使客户端应用能够通过物理机访问容器应用。
- 映射Sercie到LoadBalancer：通过设置LoadBalancer映射到云服务商提供的LoadBalancer地址。这种用法仅用于在公有云服务提供商的云平台上设置Service的场景。

### 简述Kubernetes ingress？

Kubernetes的Ingress资源对象，用于将不同URL的访问请求转发到后端不同的Service，以实现HTTP层的业务路由机制。

Kubernetes使用了Ingress策略和Ingress Controller，两者结合并实现了一个完整的Ingress负载均衡器。使用Ingress进行负载分发时，Ingress Controller基于Ingress规则将客户端请求直接转发到Service对应的后端Endpoint（Pod）上，从而跳过kube-proxy的转发功能，kube-proxy不再起作用，全过程为：ingress controller + ingress 规则 ----> services。

同时当Ingress Controller提供的是对外服务，则实际上实现的是边缘路由器的功能。

### 简述Kubernetes镜像的下载策略？

K8s的镜像下载策略有三种：Always、Never、IFNotPresent。

- `Always`：镜像标签为latest时，总是从指定的仓库中获取镜像。
- `Never`：禁止从仓库中下载镜像，也就是说只能使用本地镜像。
- `IfNotPresent`：仅当本地没有对应镜像时，才从目标仓库中下载。
默认的镜像下载策略是：当镜像标签是latest时，默认策略是Always；当镜像标签是自定义时（也就是标签不是latest），那么默认策略是IfNotPresent。

### 简述Kubernetes的负载均衡器？

负载均衡器是暴露服务的最常见和标准方式之一。

根据工作环境使用两种类型的负载均衡器，即内部负载均衡器或外部负载均衡器。内部负载均衡器自动平衡负载并使用所需配置分配容器，而外部负载均衡器将流量从外部负载引导至后端容器。

### 简述Kubernetes各模块如何与API Server通信？

Kubernetes API Server作为集群的核心，负责集群各功能模块之间的通信。集群内的各个功能模块通过API Server将信息存入etcd，当需要获取和操作这些数据时，则通过API Server提供的REST接口（用GET、LIST或WATCH方法）来实现，从而实现各模块之间的信息交互。

如kubelet进程与API Server的交互：每个Node上的kubelet每隔一个时间周期，就会调用一次API Server的REST接口报告自身状态，API Server在接收到这些信息后，会将节点状态信息更新到etcd中。

如kube-controller-manager进程与API Server的交互：kube-controller-manager中的Node Controller模块通过API Server提供的Watch接口实时监控Node的信息，并做相应处理。

如kube-scheduler进程与API Server的交互：Scheduler通过API Server的Watch接口监听到新建Pod副本的信息后，会检索所有符合该Pod要求的Node列表，开始执行Pod调度逻辑，在调度成功后将Pod绑定到目标节点上。

### 简述Kubernetes Scheduler作用及实现原理？

Kubernetes Scheduler是负责Pod调度的重要功能模块，Kubernetes Scheduler在整个系统中承担了“承上启下”的重要功能，“承上”是指它负责接收Controller Manager创建的新Pod，为其调度至目标Node；“启下”是指调度完成后，目标Node上的kubelet服务进程接管后继工作，负责Pod接下来生命周期。

Kubernetes Scheduler的作用是将待调度的Pod（API新创建的Pod、Controller Manager为补足副本而创建的Pod等）按照特定的调度算法和调度策略绑定（Binding）到集群中某个合适的Node上，并将绑定信息写入etcd中。

在整个调度过程中涉及三个对象，分别是待调度Pod列表、可用Node列表，以及调度算法和策略。

Kubernetes Scheduler通过调度算法调度为待调度Pod列表中的每个Pod从Node列表中选择一个最适合的Node来实现Pod的调度。随后，目标节点上的kubelet通过API Server监听到Kubernetes Scheduler产生的Pod绑定事件，然后获取对应的Pod清单，下载Image镜像并启动容器。

### 简述Kubernetes Scheduler使用哪两种算法将Pod绑定到worker节点？

Kubernetes Scheduler根据如下两种调度算法将 Pod 绑定到最合适的工作节点：
- `预选`（Predicates）：输入是所有节点，输出是满足预选条件的节点。kube-scheduler根据预选策略过滤掉不满足策略的Nodes。如果某节点的资源不足或者不满足预选策略的条件则无法通过预选。如“Node的label必须与Pod的Selector一致”。
- `优选`（Priorities）：输入是预选阶段筛选出的节点，优选会根据优先策略为通过预选的Nodes进行打分排名，选择得分最高的Node。例如，资源越富裕、负载越小的Node可能具有越高的排名。

### 简述Kubernetes kubelet的作用？

在Kubernetes集群中，在每个Node（又称Worker）上都会启动一个kubelet服务进程。该进程用于处理Master下发到本节点的任务，管理Pod及Pod中的容器。每个kubelet进程都会在API Server上注册节点自身的信息，定期向Master汇报节点资源的使用情况，并通过cAdvisor监控容器和节点资源。

### 简述Kubernetes kubelet监控Worker节点资源是使用什么组件来实现的？

kubelet使用cAdvisor对worker节点资源进行监控。在 Kubernetes 系统中，cAdvisor 已被默认集成到 kubelet 组件内，当 kubelet 服务启动时，它会自动启动 cAdvisor 服务，然后 cAdvisor 会实时采集所在节点的性能指标及在节点上运行的容器的性能指标。

### 简述Kubernetes如何保证集群的安全性？

Kubernetes通过一系列机制来实现集群的安全控制，主要有如下不同的维度：

- 基础设施方面：保证容器与其所在宿主机的隔离；
- 权限方面：
    - 最小权限原则：合理限制所有组件的权限，确保组件只执行它被授权的行为，通过限制单个组件的能力来限制它的权限范围。
    - 用户权限：划分普通用户和管理员的角色。
- 集群方面：
    - API Server的认证授权：Kubernetes集群中所有资源的访问和变更都是通过Kubernetes API Server来实现的，因此需要建议采用更安全的HTTPS或Token来识别和认证客户端身份（Authentication），以及随后访问权限的授权（Authorization）环节。
    - API Server的授权管理：通过授权策略来决定一个API调用是否合法。对合法用户进行授权并且随后在用户访问时进行鉴权，建议采用更安全的RBAC方式来提升集群安全授权。
    - 敏感数据引入Secret机制：对于集群敏感数据建议使用Secret方式进行保护。
    - AdmissionControl（准入机制）：对kubernetes api的请求过程中，顺序为：先经过认证 & 授权，然后执行准入操作，最后对目标对象进行操作。

### 简述Kubernetes准入机制？

在对集群进行请求时，每个准入控制代码都按照一定顺序执行。如果有一个准入控制拒绝了此次请求，那么整个请求的结果将会立即返回，并提示用户相应的error信息。

`准入控制`（AdmissionControl）准入控制本质上为一段准入代码，在对kubernetes api的请求过程中，顺序为：先经过认证 & 授权，然后执行准入操作，最后对目标对象进行操作。常用组件（控制代码）如下：
- `AlwaysAdmit`：允许所有请求
- `AlwaysDeny`：禁止所有请求，多用于测试环境。
- `ServiceAccount`：它将serviceAccounts实现了自动化，它会辅助serviceAccount做一些事情，比如如果pod没有serviceAccount属性，它会自动添加一个default，并确保pod的serviceAccount始终存在。
- `LimitRanger`：观察所有的请求，确保没有违反已经定义好的约束条件，这些条件定义在namespace中LimitRange对象中。
- `NamespaceExists`：观察所有的请求，如果请求尝试创建一个不存在的namespace，则这个请求被拒绝。

### 简述Kubernetes RBAC及其特点（优势）？

RBAC是基于角色的访问控制，是一种基于个人用户的角色来管理对计算机或网络资源的访问的方法。

相对于其他授权模式，RBAC具有如下优势：

- 对集群中的资源和非资源权限均有完整的覆盖。
- 整个RBAC完全由几个API对象完成， 同其他API对象一样， 可以用kubectl或API进行操作。
- 可以在运行时进行调整，无须重新启动API Server。

### 简述Kubernetes Secret作用？

Secret对象，主要作用是保管私密数据，比如密码、OAuth Tokens、SSH Keys等信息。将这些私密信息放在Secret对象中比直接放在Pod或Docker Image中更安全，也更便于使用和分发。

### 简述Kubernetes Secret有哪些使用方式？

创建完secret之后，可通过如下三种方式使用：
- 在创建Pod时，通过为Pod指定Service Account来自动使用该Secret。
- 通过挂载该Secret到Pod来使用它。
- 在Docker镜像下载时使用，通过指定Pod的spc.ImagePullSecrets来引用它。

### 简述Kubernetes PodSecurityPolicy机制？

Kubernetes PodSecurityPolicy是为了更精细地控制Pod对资源的使用方式以及提升安全策略。在开启PodSecurityPolicy准入控制器后，Kubernetes默认不允许创建任何Pod，需要创建PodSecurityPolicy策略和相应的RBAC授权策略（Authorizing Policies），Pod才能创建成功。

### 简述Kubernetes PodSecurityPolicy机制能实现哪些安全策略？

在PodSecurityPolicy对象中可以设置不同字段来控制Pod运行时的各种安全策略，常见的有：
- 特权模式：privileged是否允许Pod以特权模式运行。
- 宿主机资源：控制Pod对宿主机资源的控制，如hostPID：是否允许Pod共享宿主机的进程空间。
- 用户和组：设置运行容器的用户ID（范围）或组（范围）。
- 提升权限：AllowPrivilegeEscalation：设置容器内的子进程是否可以提升权限，通常在设置非root用户（MustRunAsNonRoot）时进行设置。
- SELinux：进行SELinux的相关配置。

### 简述Kubernetes网络模型？

Kubernetes网络模型中每个Pod都拥有一个独立的IP地址，并假定所有Pod都在一个可以直接连通的、扁平的网络空间中。所以不管它们是否运行在同一个Node（宿主机）中，都要求它们可以直接通过对方的IP进行访问。设计这个原则的原因是，用户不需要额外考虑如何建立Pod之间的连接，也不需要考虑如何将容器端口映射到主机端口等问题。

同时为每个Pod都设置一个IP地址的模型使得同一个Pod内的不同容器会共享同一个网络命名空间，也就是同一个Linux网络协议栈。这就意味着同一个Pod内的容器可以通过localhost来连接对方的端口。

在Kubernetes的集群里，IP是以Pod为单位进行分配的。一个Pod内部的所有容器共享一个网络堆栈（相当于一个网络命名空间，它们的IP地址、网络设备、配置等都是共享的）。

### 简述Kubernetes CNI模型？

CNI提供了一种应用容器的插件化网络解决方案，定义对容器网络进行操作和配置的规范，通过插件的形式对CNI接口进行实现。CNI仅关注在创建容器时分配网络资源，和在销毁容器时删除网络资源。在CNI模型中只涉及两个概念：容器和网络。

- `容器`（Container）：是拥有独立Linux网络命名空间的环境，例如使用Docker或rkt创建的容器。容器需要拥有自己的Linux网络命名空间，这是加入网络的必要条件。
- `网络`（Network）：表示可以互连的一组实体，这些实体拥有各自独立、唯一的IP地址，可以是容器、物理机或者其他网络设备（比如路由器）等。

对容器网络的设置和操作都通过插件（Plugin）进行具体实现，CNI插件包括两种类型：CNI Plugin和IPAM（IP Address  Management）Plugin。CNI Plugin负责为容器配置网络资源，IPAM Plugin负责对容器的IP地址进行分配和管理。IPAM Plugin作为CNI Plugin的一部分，与CNI Plugin协同工作。

### 简述Kubernetes网络策略？

为实现细粒度的容器间网络访问隔离策略，Kubernetes引入Network Policy。

Network Policy的主要功能是对Pod间的网络通信进行限制和准入控制，设置允许访问或禁止访问的客户端Pod列表。Network Policy定义网络策略，配合策略控制器（Policy Controller）进行策略的实现。

### 简述Kubernetes网络策略原理？

Network Policy的工作原理主要为：policy controller需要实现一个API Listener，监听用户设置的Network Policy定义，并将网络访问规则通过各Node的Agent进行实际设置（Agent则需要通过CNI网络插件实现）。

### 简述Kubernetes中flannel的作用？

Flannel可以用于Kubernetes底层网络的实现，主要作用有：

- 它能协助Kubernetes，给每一个Node上的Docker容器都分配互相不冲突的IP地址。
- 它能在这些IP地址之间建立一个覆盖网络（Overlay Network），通过这个覆盖网络，将数据包原封不动地传递到目标容器内。

### 简述Kubernetes Calico网络组件实现原理？

Calico是一个基于BGP的纯三层的网络方案，与OpenStack、Kubernetes、AWS、GCE等云平台都能够良好地集成。

Calico在每个计算节点都利用Linux Kernel实现了一个高效的vRouter来负责数据转发。每个vRouter都通过BGP协议把在本节点上运行的容器的路由信息向整个Calico网络广播，并自动设置到达其他节点的路由转发规则。

Calico保证所有容器之间的数据流量都是通过IP路由的方式完成互联互通的。Calico节点组网时可以直接利用数据中心的网络结构（L2或者L3），不需要额外的NAT、隧道或者Overlay Network，没有额外的封包解包，能够节约CPU运算，提高网络效率。

### 简述Kubernetes共享存储的作用？

Kubernetes对于有状态的容器应用或者对数据需要持久化的应用，因此需要更加可靠的存储来保存应用产生的重要数据，以便容器应用在重建之后仍然可以使用之前的数据。因此需要使用共享存储。

### 简述Kubernetes数据持久化的方式有哪些？

Kubernetes通过数据持久化来持久化保存重要数据，常见的方式有：
- EmptyDir（空目录）：没有指定要挂载宿主机上的某个目录，直接由Pod内保部映射到宿主机上。类似于docker中的manager volume。

- 场景：
    - 只需要临时将数据保存在磁盘上，比如在合并/排序算法中；
    - 作为两个容器的共享存储。
- 特性：
    - 同个pod里面的不同容器，共享同一个持久化目录，当pod节点删除时，volume的数据也会被删除。
    - emptyDir的数据持久化的生命周期和使用的pod一致，一般是作为临时存储使用。
- Hostpath：将宿主机上已存在的目录或文件挂载到容器内部。类似于docker中的bind mount挂载方式。
    - 特性：增加了pod与节点之间的耦合。

PersistentVolume（简称PV）：如基于NFS服务的PV，也可以基于GFS的PV。它的作用是统一数据持久化目录，方便管理。

### 简述Kubernetes PV和PVC？

PV是对底层网络共享存储的抽象，将共享存储定义为一种“资源”。

PVC则是用户对存储资源的一个“申请”。

### 简述Kubernetes PV生命周期内的阶段？

某个PV在生命周期中可能处于以下4个阶段（Phaes）之一。
- Available：可用状态，还未与某个PVC绑定。
- Bound：已与某个PVC绑定。
- Released：绑定的PVC已经删除，资源已释放，但没有被集群回收。
- Failed：自动资源回收失败。

### 简述Kubernetes所支持的存储供应模式？

Kubernetes支持两种资源的存储供应模式：静态模式（Static）和动态模式（Dynamic）。
- `静态模式`：集群管理员手工创建许多PV，在定义PV时需要将后端存储的特性进行设置。
- `动态模式`：集群管理员无须手工创建PV，而是通过StorageClass的设置对后端存储进行描述，标记为某种类型。此时要求PVC对存储的类型进行声明，系统将自动完成PV的创建及与PVC的绑定。

### 简述Kubernetes CSI模型？

Kubernetes CSI是Kubernetes推出与容器对接的存储接口标准，存储提供方只需要基于标准接口进行存储插件的实现，就能使用Kubernetes的原生存储机制为容器提供存储服务。CSI使得存储提供方的代码能和Kubernetes代码彻底解耦，部署也与Kubernetes核心组件分离，显然，存储插件的开发由提供方自行维护，就能为Kubernetes用户提供更多的存储功能，也更加安全可靠。

CSI包括CSI Controller和CSI Node：

- CSI Controller的主要功能是提供存储服务视角对存储资源和存储卷进行管理和操作。
- CSI Node的主要功能是对主机（Node）上的Volume进行管理和操作。

### 简述Kubernetes Worker节点加入集群的过程？

通常需要对Worker节点进行扩容，从而将应用系统进行水平扩展。主要过程如下：

- 1、在该Node上安装Docker、kubelet和kube-proxy服务；
- 2、然后配置kubelet和kubeproxy的启动参数，将Master URL指定为当前Kubernetes集群Master的地址，最后启动这些服务；
- 3、通过kubelet默认的自动注册机制，新的Worker将会自动加入现有的Kubernetes集群中；
- 4、Kubernetes Master在接受了新Worker的注册之后，会自动将其纳入当前集群的调度范围。

### 简述Kubernetes Pod如何实现对节点的资源控制？

Kubernetes集群里的节点提供的资源主要是计算资源，计算资源是可计量的能被申请、分配和使用的基础资源。当前Kubernetes集群中的计算资源主要包括CPU、GPU及Memory。CPU与Memory是被Pod使用的，因此在配置Pod时可以通过参数CPU Request及Memory Request为其中的每个容器指定所需使用的CPU与Memory量，Kubernetes会根据Request的值去查找有足够资源的Node来调度此Pod。

通常，一个程序所使用的CPU与Memory是一个动态的量，确切地说，是一个范围，跟它的负载密切相关：负载增加时，CPU和Memory的使用量也会增加。

### 简述Kubernetes Requests和Limits如何影响Pod的调度？

当一个Pod创建成功时，Kubernetes调度器（Scheduler）会为该Pod选择一个节点来执行。对于每种计算资源（CPU和Memory）而言，每个节点都有一个能用于运行Pod的最大容量值。调度器在调度时，首先要确保调度后该节点上所有Pod的CPU和内存的Requests总和，不超过该节点能提供给Pod使用的CPU和Memory的最大容量值。

### 简述Kubernetes Metric Service？

在Kubernetes从1.10版本后采用Metrics Server作为默认的性能数据采集和监控，主要用于提供核心指标（Core Metrics），包括Node、Pod的CPU和内存使用指标。

对其他自定义指标（Custom Metrics）的监控则由Prometheus等组件来完成。

### 简述Kubernetes中，如何使用EFK实现日志的统一管理？

在Kubernetes集群环境中，通常一个完整的应用或服务涉及组件过多，建议对日志系统进行集中化管理，通常采用EFK实现。

EFK是 Elasticsearch、Fluentd 和 Kibana 的组合，其各组件功能如下：

- Elasticsearch：是一个搜索引擎，负责存储日志并提供查询接口；
- Fluentd：负责从 Kubernetes 搜集日志，每个node节点上面的fluentd监控并收集该节点上面的系统日志，并将处理过后的日志信息发送给Elasticsearch；
- Kibana：提供了一个 Web GUI，用户可以浏览和搜索存储在 Elasticsearch 中的日志。

通过在每台node上部署一个以DaemonSet方式运行的fluentd来收集每台node上的日志。Fluentd将docker日志目录/var/lib/docker/containers和/var/log目录挂载到Pod中，然后Pod会在node节点的/var/log/pods目录中创建新的目录，可以区别不同的容器日志输出，该目录下有一个日志文件链接到/var/lib/docker/contianers目录下的容器日志输出。

### 简述Kubernetes如何进行优雅的节点关机维护？

由于Kubernetes节点运行大量Pod，因此在进行关机维护之前，建议先使用kubectl drain将该节点的Pod进行驱逐，然后进行关机维护。

### 简述Kubernetes集群联邦？

Kubernetes集群联邦可以将多个Kubernetes集群作为一个集群进行管理。因此，可以在一个数据中心/云中创建多个Kubernetes集群，并使用集群联邦在一个地方控制/管理所有集群。

### 简述Helm及其优势？

`Helm` 是 Kubernetes 的软件包管理工具。类似 Ubuntu 中使用的apt、Centos中使用的yum 或者Python中的 pip 一样。

Helm能够将一组K8S资源打包统一管理, 是查找、共享和使用为Kubernetes构建的软件的最佳方式。

Helm中通常每个包称为一个Chart，一个Chart是一个目录（一般情况下会将目录进行打包压缩，形成name-version.tgz格式的单一文件，方便传输和存储）。

- Helm优势

在 Kubernetes中部署一个可以使用的应用，需要涉及到很多的 Kubernetes 资源的共同协作。使用helm则具有如下优势：

- 统一管理、配置和更新这些分散的 k8s 的应用资源文件；
- 分发和复用一套应用模板；
- 将应用的一系列资源当做一个软件包管理。
- 对于应用发布者而言，可以通过 Helm 打包应用、管理应用依赖关系、管理应用版本并发布应用到软件仓库。
- 对于使用者而言，使用 Helm 后不用需要编写复杂的应用部署文件，可以以简单的方式在 Kubernetes 上查找、安装、升级、回滚、卸载应用程序。

### 简述OpenShift及其特性？

OpenShift是一个容器应用程序平台，用于在安全的、可伸缩的资源上部署新应用程序，而配置和管理开销最小。

OpenShift构建于Red Hat Enterprise Linux、Docker和Kubernetes之上，为企业级应用程序提供了一个安全且可伸缩的多租户操作系统，同时还提供了集成的应用程序运行时和库。

其主要特性：
- 自助服务平台：OpenShift允许开发人员使用Source-to-Image(S2I)从模板或自己的源代码管理存储库创建应用程序。系统管理员可以为用户和项目定义资源配额和限制，以控制系统资源的使用。
- 多语言支持：OpenShift支持Java、Node.js、PHP、Perl以及直接来自Red Hat的Ruby。OpenShift还支持中间件产品，如Apache httpd、Apache Tomcat、JBoss EAP、ActiveMQ和Fuse。
- 自动化：OpenShift提供应用程序生命周期管理功能，当上游源或容器映像发生更改时，可以自动重新构建和重新部署容器。根据调度和策略扩展或故障转移应用程序。
- 用户界面：OpenShift提供用于部署和监视应用程序的web UI，以及用于远程管理应用程序和资源的CLi。
- 协作：OpenShift允许在组织内或与更大的社区共享项目。
- 可伸缩性和高可用性：OpenShift提供了容器多租户和一个分布式应用程序平台，其中包括弹性，高可用性，以便应用程序能够在物理机器宕机等事件中存活下来。OpenShift提供了对容器健康状况的自动发现和自动重新部署。
- 容器可移植性：在OpenShift中，应用程序和服务使用标准容器映像进行打包，组合应用程序使用Kubernetes进行管理。这些映像可以部署到基于这些基础技术的其他平台上。
- 开源：没有厂商锁定。
- 安全性：OpenShift使用SELinux提供多层安全性、基于角色的访问控制以及与外部身份验证系统(如LDAP和OAuth)集成的能力。
- 动态存储管理：OpenShift使用Kubernetes持久卷和持久卷声明的方式为容器数据提供静态和动态存储管理
- 基于云(或不基于云)：可以在裸机服务器、活来自多个供应商的hypervisor和大多数IaaS云提供商上部署OpenShift容器平台。
- 企业级：Red Hat支持OpenShift、选定的容器映像和应用程序运行时。可信的第三方容器映像、运行时和应用程序由Red Hat认证。可以在OpenShift提供的高可用性的强化安全环境中运行内部或第三方应用程序。
- 日志聚合和metrics：可以在中心节点收集、聚合和分析部署在OpenShift上的应用程序的日志信息。OpenShift能够实时收集关于应用程序的度量和运行时信息，并帮助不断优化性能。
- 其他特性：OpenShift支持微服务体系结构，OpenShift的本地特性足以支持DevOps流程，很容易与标准和定制的持续集成/持续部署工具集成。

### 简述OpenShift projects及其作用？

OpenShift管理projects和users。一个projects对Kubernetes资源进行分组，以便用户可以使用访问权限。还可以为projects分配配额，从而限制了已定义的pod、volumes、services和其他资源。

project允许一组用户独立于其他组组织和管理其内容，必须允许用户访问项目。如果允许创建项目，用户将自动访问自己的项目。

### 简述OpenShift高可用的实现？

OpenShift平台集群的高可用性(HA)有两个不同的方面：

OpenShift基础设施本身的HA(即主机)；

以及在OpenShift集群中运行的应用程序的HA。

默认情况下，OpenShift为master节点提供了完全支持的本机HA机制。
对于应用程序或“pods”，如果pod因任何原因丢失，Kubernetes将调度另一个副本，将其连接到服务层和持久存储。如果整个节点丢失，Kubernetes会为它所有的pod安排替换节点，最终所有的应用程序都会重新可用。pod中的应用程序负责它们自己的状态，因此它们需要自己维护应用程序状态(如HTTP会话复制或数据库复制)。

### 简述OpenShift的SDN网络实现？

默认情况下，Docker网络使用仅使用主机虚机网桥bridge，主机内的所有容器都连接至该网桥。连接到此桥的所有容器都可以彼此通信，但不能与不同主机上的容器通信。

为了支持跨集群的容器之间的通信，OpenShift容器平台使用了软件定义的网络(SDN)方法。软件定义的网络是一种网络模型，它通过几个网络层的抽象来管理网络服务。SDN将处理流量的软件(称为控制平面)和路由流量的底层机制(称为数据平面)解耦。SDN支持控制平面和数据平面之间的通信。

在OpenShift中，可以为pod网络配置三个SDN插件:

- 1、ovs-subnet：默认插件，子网提供了一个flat pod网络，其中每个pod可以与其他pod和service通信。
- 2、ovs-multitenant：该为pod和服务提供了额外的隔离层。当使用此插件时，每个project接收一个惟一的虚拟网络ID (VNID)，该ID标识来自属于该project的pod的流量。通过使用VNID，来自不同project的pod不能与其他project的pod和service通信。
- 3、ovs-network policy：此插件允许管理员使用NetworkPolicy对象定义自己的隔离策略。

cluster network由OpenShift SDN建立和维护，它使用Open vSwitch创建overlay网络，master节点不能通过集群网络访问容器，除非master同时也为node节点。

### 简述OpenShift角色及其作用？

OpenShift的角色具有不同级别的访问和策略，包括集群和本地策略。user和group可以同时与多个role关联。

### 简述OpenShift支持哪些身份验证？

OpenShift容器平台支持的其他认证类型包括:
- Basic Authentication (Remote)：一种通用的后端集成机制，允许用户使用针对远程标识提供者验证的凭据登录到OpenShift容器平台。用户将他们的用户名和密码发送到OpenShift容器平台，OpenShift平台通过到服务器的请求验证这些凭据，并将凭据作为基本的Auth头传递。这要求用户在登录过程中向OpenShift容器平台输入他们的凭据。
- Request Header Authentication：用户使用请求头值(如X-RemoteUser)登录到OpenShift容器平台。它通常与身份验证代理结合使用，身份验证代理对用户进行身份验证，然后通过请求头值为OpenShift容器平台提供用户标识。
- Keystone Authentication：Keystone是一个OpenStack项目，提供标识、令牌、目录和策略服务。OpenShift容器平台与Keystone集成，通过配置OpenStack Keystone v3服务器将用户存储在内部数据库中，从而支持共享身份验证。这种配置允许用户使用Keystone凭证登录OpenShift容器平台。
- LDAP Authentication：用户使用他们的LDAP凭证登录到OpenShift容器平台。在身份验证期间，LDAP目录将搜索与提供的用户名匹配的条目。如果找到匹配项，则尝试使用条目的专有名称(DN)和提供的密码进行简单绑定。
- GitHub Authentication：GitHub使用OAuth，它允许与OpenShift容器平台集成使用OAuth身份验证来促进令牌交换流。这允许用户使用他们的GitHub凭证登录到OpenShift容器平台。为了防止使用GitHub用户id的未授权用户登录到OpenShift容器平台集群，可以将访问权限限制在特定的GitHub组织中。

### 简述什么是中间件？

`中间件`是一种独立的系统软件或服务程序，分布式应用软件借助这种软件在不同的技术之间共享资源。通常位于客户机/服务器的操作系统中间，是连接两个独立应用程序或独立系统的软件。

通过中间件实现两个不同系统之间的信息交换。

> - 作者：木二
> - 链接：https://www.yuque.com/docs/share/d3dd1e8e-6828-4da7-9e30-6a4f45c6fa8e