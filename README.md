# 个人自动化运维指南 

> 如果中间内容对你有所帮助，可以帮我在 [yangpeng14/DevOps](https://github.com/yangpeng14/DevOps)上点个 star

> 你的赞赏是我的动力

![你的赞赏是我的动力](https://www.yp14.cn/img/zs.png)

如果你是新人，目前阿里云搞双十一活动买云主机有优惠，可以点击[链接](https://www.aliyun.com/1111/2019/group-buying-share?ptCode=A4F5921E30342172AF5EDAD7E4306306647C88CF896EF535&userCode=uwhxi2r0&share_source=wechat&from=timeline&isappinstalled=0)购买

+ [邀请你一起购买 86元人民币/年 云主机](https://www.aliyun.com/1111/2019/group-buying-share?ptCode=A4F5921E30342172AF5EDAD7E4306306647C88CF896EF535&userCode=uwhxi2r0&share_source=wechat&from=timeline&isappinstalled=0)

## 目录

### 一、Let's Encrypt 证书自动颁发脚本
1. [基于 acme.sh脚本 DNS别名功能 分批申请证书](https://github.com/yangpeng14/DevOps/blob/master/letsencrypt/letsencrypt-dns-alias.md)


### 二、一些Python工具
1. [Python工具](https://github.com/yangpeng14/DevOps/tree/master/python3)


### 三、Docker知识
1. [Docker容器日志清理方案](https://github.com/yangpeng14/DevOps/blob/master/docker/docker-%E5%AE%B9%E5%99%A8%E6%97%A5%E5%BF%97%E6%B8%85%E7%90%86%E6%96%B9%E6%A1%88.md)

### 四、Kubernetes知识
1. [Metrics Serve 0.3.2安装](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/metrics-Server-v0-3-2%E7%89%88%E6%9C%AC%E5%AE%89%E8%A3%85.md)
2. [Prometheus Operator手动安装](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/prometheus-operator%E6%89%8B%E5%8A%A8%E9%83%A8%E7%BD%B2.md)
3. [Etcd v3版本备份与恢复](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/etcd-v3%E5%A4%87%E4%BB%BD%E4%B8%8E%E6%81%A2%E5%A4%8D.md)
4. [Etcd 使用命令](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/etcd%E4%BD%BF%E7%94%A8%E5%91%BD%E4%BB%A4.md)
5. [Kubernetes v1.12.0 HA搭建](https://www.yp14.cn/2018/09/30/Kubernetes-v1-12-0-HA%E6%90%AD%E5%BB%BA/)
6. [AlertManager 钉钉报警](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/AlertManager-%E9%92%89%E9%92%89%E6%8A%A5%E8%AD%A6.md)
7. [Prometheus 如何自动发现 Kubernetes Metrics 接口](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/prometheus-%E5%A6%82%E4%BD%95%E8%87%AA%E5%8A%A8%E5%8F%91%E7%8E%B0kubernetes-metrics%E6%8E%A5%E5%8F%A3.md)
8. [Kubelet 证书自动续期](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/kubelet-%E8%AF%81%E4%B9%A6%E8%87%AA%E5%8A%A8%E7%BB%AD%E6%9C%9F.md)
9. [Helm v3 新的功能](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/helm-v3-%E6%96%B0%E7%9A%84%E5%8A%9F%E8%83%BD.md)
10. [K8s Ingress Nginx 支持 Socket.io](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/k8s-ingress-nginx%E6%94%AF%E6%8C%81socket.io.md)
11. [k8s 蓝绿部署之 Service Label](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/k8s%E8%93%9D%E7%BB%BF%E9%83%A8%E7%BD%B2%E4%B9%8B-service-label.md)

### 五、Istio知识
1. [Istio Helm 安装](https://github.com/yangpeng14/DevOps/blob/master/istio/istio-Helm-%E5%AE%89%E8%A3%85.md)

### 六、运维知识
1. [Sentry历史数据清理](https://github.com/yangpeng14/DevOps/blob/master/ops/sentry%E5%8E%86%E5%8F%B2%E6%95%B0%E6%8D%AE%E6%B8%85%E7%90%86.md)
2. [Sentry9.1.2部署](https://github.com/yangpeng14/DevOps/blob/master/ops/sentry9.1.2%E9%83%A8%E7%BD%B2.md)
3. [Gitlab Docker Compose 启动配置](https://github.com/yangpeng14/DevOps/blob/master/ops/Gitlab-Docker-Compose-%E5%90%AF%E5%8A%A8%E9%85%8D%E7%BD%AE.md)
4. [ES6版本自定义索引模板](https://github.com/yangpeng14/DevOps/blob/master/ops/es6%E8%87%AA%E5%AE%9A%E4%B9%89%E7%B4%A2%E5%BC%95%E6%A8%A1%E6%9D%BF.md)
5. [Elasticsearch查询](https://github.com/yangpeng14/DevOps/blob/master/ops/Elasticsearch%E6%9F%A5%E8%AF%A2.md)
6. [Gitlab CI 搭建持续集成环境](https://github.com/yangpeng14/DevOps/blob/master/ops/gitlab-ci-%E6%90%AD%E5%BB%BA%E6%8C%81%E7%BB%AD%E9%9B%86%E6%88%90%E7%8E%AF%E5%A2%83.md)
7. [Gitlab CI + Helm + Kubernetes 构建CI/CD](https://github.com/yangpeng14/DevOps/blob/master/ops/gitlab-ci-helm-k8s.md)
8. [批量创建阿里云ECS并初始化](https://github.com/yangpeng14/DevOps/blob/master/ops/%E6%89%B9%E9%87%8F%E5%88%9B%E5%BB%BA%E9%98%BF%E9%87%8C%E4%BA%91ECS%E5%B9%B6%E5%88%9D%E5%A7%8B%E5%8C%96.md)
9. [Harbor v1.7.0自动镜像回收](https://github.com/yangpeng14/DevOps/blob/master/ops/harbor-v1.7.0-%E8%87%AA%E5%8A%A8%E9%95%9C%E5%83%8F%E5%9B%9E%E6%94%B6.md)

## 公众号
欢迎关注公众号**YP小站**，我会定期分享本人家乡美食以及自动化运维相关文章，欢迎大家关注交流，如果有机会也可以去我家乡湖南游玩

![YP小站](https://www.yp14.cn/img/yp_wx.png)