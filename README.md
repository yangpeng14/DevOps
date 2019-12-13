# 个人自动化运维指南 

> 如果中间内容对你有所帮助，可以帮我在 [yangpeng14/DevOps](https://github.com/yangpeng14/DevOps)上点个 star

> 你的赞赏是我的动力

![你的赞赏是我的动力](/img/zs.png)

如果你是新人，目前阿里云搞双十一活动买云主机有优惠，可以点击[链接](https://www.aliyun.com/1111/2019/group-buying-share?ptCode=A4F5921E30342172AF5EDAD7E4306306647C88CF896EF535&userCode=uwhxi2r0&share_source=wechat&from=timeline&isappinstalled=0)购买

+ [邀请你一起购买 86元人民币/年 云主机](https://www.aliyun.com/1111/2019/group-buying-share?ptCode=A4F5921E30342172AF5EDAD7E4306306647C88CF896EF535&userCode=uwhxi2r0&share_source=wechat&from=timeline&isappinstalled=0)

## 目录

### 一、Let's Encrypt 证书自动颁发脚本
1. [基于 acme.sh脚本 DNS别名功能 分批申请证书](https://github.com/yangpeng14/DevOps/blob/master/letsencrypt/letsencrypt-dns-alias.md)


### 二、工具
1. [Python工具](https://github.com/yangpeng14/DevOps/tree/master/python3)
2. [提高阅读代码效率神器 Sourcetrail](https://github.com/yangpeng14/DevOps/blob/master/tools/%E6%8F%90%E9%AB%98%E9%98%85%E8%AF%BB%E4%BB%A3%E7%A0%81%E6%95%88%E7%8E%87%E7%A5%9E%E5%99%A8-Sourcetrail.md)
3. [Linux IO分析小神器](https://github.com/yangpeng14/DevOps/blob/master/tools/Linux-IO%E5%88%86%E6%9E%90%E5%B0%8F%E7%A5%9E%E5%99%A8.md)
4. [春运开始了-该抢火车票了](https://github.com/yangpeng14/DevOps/blob/master/tools/%E6%98%A5%E8%BF%90%E5%BC%80%E5%A7%8B%E4%BA%86-%E8%AF%A5%E6%8A%A2%E7%81%AB%E8%BD%A6%E7%A5%A8%E4%BA%86.md)

### 三、Docker知识
1. [Docker容器日志清理方案](https://github.com/yangpeng14/DevOps/blob/master/docker/docker-%E5%AE%B9%E5%99%A8%E6%97%A5%E5%BF%97%E6%B8%85%E7%90%86%E6%96%B9%E6%A1%88.md)
2. [一次构建多平台docker镜像](https://github.com/yangpeng14/DevOps/blob/master/docker/%E4%B8%80%E6%AC%A1%E6%9E%84%E5%BB%BA%E5%A4%9A%E5%B9%B3%E5%8F%B0docker%E9%95%9C%E5%83%8F.md)
3. [RedHat 开源企业镜像项目 Quay](https://github.com/yangpeng14/DevOps/blob/master/docker/RedHat%E5%BC%80%E6%BA%90%E4%BC%81%E4%B8%9A%E9%95%9C%E5%83%8F%E9%A1%B9%E7%9B%AEQuay.md)
4. [Docker 必修课程 Dockerfile](https://github.com/yangpeng14/DevOps/blob/master/docker/Docker%E5%BF%85%E4%BF%AE%E8%AF%BE%E7%A8%8BDockerfile.md)
5. [Docker 镜像分析之 dive](https://github.com/yangpeng14/DevOps/blob/master/docker/docker%E9%95%9C%E5%83%8F%E5%88%86%E6%9E%90%E4%B9%8Bdive.md)
6. [Docker 最简单管理方法之 Portainer](https://github.com/yangpeng14/DevOps/blob/master/docker/Docker%E6%9C%80%E7%AE%80%E5%8D%95%E7%AE%A1%E7%90%86%E6%96%B9%E6%B3%95%E4%B9%8BPortainer.md)
7. [比 docker stats 命令好用工具 ctop](https://github.com/yangpeng14/DevOps/blob/master/docker/%E6%AF%94docker-stats%E5%91%BD%E4%BB%A4%E5%A5%BD%E7%94%A8%E5%B7%A5%E5%85%B7ctop.md)

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
10. [K8S Ingress Nginx 支持 Socket.io](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/k8s-ingress-nginx%E6%94%AF%E6%8C%81socket.io.md)
11. [K8S 蓝绿部署之 Service Label](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/k8s%E8%93%9D%E7%BB%BF%E9%83%A8%E7%BD%B2%E4%B9%8B-service-label.md)
12. [K8S 之 kubeadm 安装](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/k8s%E4%B9%8Bkubeadm%E5%AE%89%E8%A3%85.md)
13. [K8S Dashboard V2.0.0 Beta6 部署](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/k8s-dashboard-v2.0.0-beta6%E9%83%A8%E7%BD%B2.md)
14. [K8S 之 Headless 浅谈](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/k8s%E4%B9%8BHeadless%E6%B5%85%E8%B0%88.md)
15. [K8S node NotReady 后如何保证服务可用](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/k8s-node-NotReady%E5%90%8E%E5%A6%82%E4%BD%95%E4%BF%9D%E8%AF%81%E6%9C%8D%E5%8A%A1%E5%8F%AF%E7%94%A8.md)
16. [浅谈 K8S QoS(服务质量等级)](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/%E6%B5%85%E8%B0%88k8s-QoS(%E6%9C%8D%E5%8A%A1%E8%B4%A8%E9%87%8F%E7%AD%89%E7%BA%A7).md)
17. [Kubernetes 北极星指标](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/kubernetes%E5%8C%97%E6%9E%81%E6%98%9F%E6%8C%87%E6%A0%87.md)
18. [升级到 Kubernetes v1.16 须知API问题总结](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/%E5%8D%87%E7%BA%A7%E5%88%B0Kubernetes-v1.16%E9%A1%BB%E7%9F%A5API%E9%97%AE%E9%A2%98%E6%80%BB%E7%BB%93.md)
19. [Kubernetes 必须掌握技能之 RBAC](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/kubernetes%E5%BF%85%E9%A1%BB%E6%8E%8C%E6%8F%A1%E6%8A%80%E8%83%BD%E4%B9%8BRBAC.md)
20. [Kubernetes 终端管理神器](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/kubernetes%E7%BB%88%E7%AB%AF%E7%AE%A1%E7%90%86%E7%A5%9E%E5%99%A8.md)
21. [Kubernetes v1.17.0 正式发布](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/kubernetes-v1.17.0%E6%AD%A3%E5%BC%8F%E5%8F%91%E5%B8%83.md)
22. [3分钟部署生产级k8s集群](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/3%E5%88%86%E9%92%9F%E9%83%A8%E7%BD%B2%E7%94%9F%E4%BA%A7%E7%BA%A7k8s%E9%9B%86%E7%BE%A4.md)
23. [K8S 滚动更新如何优雅停止 Pod](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/k8s%E6%BB%9A%E5%8A%A8%E6%9B%B4%E6%96%B0%E5%A6%82%E4%BD%95%E4%BC%98%E9%9B%85%E5%81%9C%E6%AD%A2pod.md)

### 五、Istio知识
1. [Istio Helm 安装](https://github.com/yangpeng14/DevOps/blob/master/istio/istio-Helm-%E5%AE%89%E8%A3%85.md)
2. [K8S 金丝雀部署之 Istio](https://github.com/yangpeng14/DevOps/blob/master/kubernetes/k8s%E9%87%91%E4%B8%9D%E9%9B%80%E9%83%A8%E7%BD%B2%E4%B9%8B-Istio.md)
3. [小米开源 Istio Dashboard Naftis 服务](https://github.com/yangpeng14/DevOps/blob/master/istio/%E5%B0%8F%E7%B1%B3%E5%BC%80%E6%BA%90Istio-dashboard-Naftis%E6%9C%8D%E5%8A%A1.md)
4. [Istio 自动注入 sidecar 不成功解决方案](https://github.com/yangpeng14/DevOps/blob/master/istio/Istio%E8%87%AA%E5%8A%A8%E6%B3%A8%E5%85%A5sidecar%E4%B8%8D%E6%88%90%E5%8A%9F%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88.md)

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
10. [网页主体格式转换神器](https://github.com/yangpeng14/DevOps/blob/master/ops/zignis-plugin-read.md)
11. [Nginx 流量统计分析](https://github.com/yangpeng14/DevOps/blob/master/ops/nginx-%E6%B5%81%E9%87%8F%E7%BB%9F%E8%AE%A1%E5%88%86%E6%9E%90.md)
12. [Elasticsearch RESTful API 常用操作](https://github.com/yangpeng14/DevOps/blob/master/ops/elasticsearch-RESTful-API-%E5%B8%B8%E7%94%A8%E6%93%8D%E4%BD%9C.md)
13. [Nginx 基于客户端IP分析](https://github.com/yangpeng14/DevOps/blob/master/ops/nginx-%E5%9F%BA%E4%BA%8E%E5%AE%A2%E6%88%B7%E7%AB%AFIP%E5%88%86%E6%9E%90.md)
14. [Nginx必须知道哪些事](https://github.com/yangpeng14/DevOps/blob/master/ops/Nginx%E5%BF%85%E9%A1%BB%E7%9F%A5%E9%81%93%E5%93%AA%E4%BA%9B%E4%BA%8B.md)
15. [Nginx 服务指标监测](https://github.com/yangpeng14/DevOps/blob/master/ops/Nginx%E6%9C%8D%E5%8A%A1%E6%8C%87%E6%A0%87%E7%9B%91%E6%B5%8B.md)

### 七、Podman知识
1. [Podman 会取代 Docker 吗?](https://github.com/yangpeng14/DevOps/blob/master/podman/podman%E4%BC%9A%E5%8F%96%E4%BB%A3docker%E5%90%97.md)

## 公众号
欢迎大家关注微信公众号**YP小站**，我会定期分享本人家乡美食、自动化运维、DevOps、Kubernetes、Service Mesh和Cloud Native相关文章，欢迎大家关注交流，如果有机会也可以去我家乡湖南游玩。

![YP小站](/img/yp_wx.png)