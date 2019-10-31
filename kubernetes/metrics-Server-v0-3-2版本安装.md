#### 一、参考链接
1. 官方github https://github.com/kubernetes-incubator/metrics-server
2. http://www.cnblogs.com/wjoyxt/p/10003159.html
3. http://orchome.com/1203

#### 二、修改配置
##### 1. 创建 metrics-server 使用的证书
```
# 注意: "CN": "system:metrics-server" 一定是这个，因为后面授权时用到这个名称，否则会报禁止匿名访问

cat > metrics-server-csr.json <<EOF
{
  "CN": "system:metrics-server",
  "hosts": [],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "BeiJing",
      "L": "BeiJing",
      "O": "k8s",
      "OU": "system"
    }
  ]
}
EOF
```

##### 2. 生成 metrics-server 证书和私钥

```
cfssl gencert -ca=/opt/kubernetes/ssl/ca.pem   -ca-key=/opt/kubernetes/ssl/ca-key.pem    -config=/opt/kubernetes/ssl/ca-config.json -profile=kubernetes metrics-server-csr.json | cfssljson -bare metrics-server
```

##### 3. 修改 kubernetes 控制平面组件的配置以支持 metrics-server

```
# kube-apiserver 配置文件中添加如下参数

--requestheader-client-ca-file=/opt/kubernetes/ssl/ca.pem \
--requestheader-extra-headers-prefix=X-Remote-Extra- \
--requestheader-group-headers=X-Remote-Group \
--requestheader-username-headers=X-Remote-User \
--proxy-client-cert-file=/opt/kubernetes/ssl/metrics-server.pem \
--proxy-client-key-file=/opt/kubernetes/ssl/metrics-server-key.pem \
--runtime-config=api/all=true \

# 注意
# --requestheader-XXX、--proxy-client-XXX 是 kube-apiserver 的 aggregator layer 相关的配置参数，metrics-server & HPA 需要使用；
# --requestheader-client-ca-file：用于签名 --proxy-client-cert-file 和 # --proxy-client-key-file 指定的证书；在启用了 metric aggregator 时使用；
# 如果 kube-apiserver 机器没有运行 kube-proxy，则还需要添加 --enable-aggregator-routing=true 参数
# requestheader-client-ca-file 指定的 CA 证书，必须具有 client auth and server auth
```

##### 4. 添加 kube-controller-manager配置

```
# 添加如下配置参数：
--horizontal-pod-autoscaler-use-rest-clients=true

# 用于配置 HPA 控制器使用 REST 客户端获取 metrics 数据
```

##### 5. 重启 kube-apiserver kube-controller-manager 服务
```
systemctl restart kube-apiserver
systemctl restart kube-controller-manager
```

#### 三、安装 metrics-server

##### 1. 下载项目并修改deployment文件
```
# git clone https://github.com/kubernetes-incubator/metrics-server
# cd metrics-server/deploy/1.8+
# vim metrics-server-deployment.yaml
# 修改如下参数

      - name: metrics-server
        image: yangpeng2468/metrics-server-amd64:v0.3.2
        imagePullPolicy: IfNotPresent
        command:
        - /metrics-server
        - --kubelet-insecure-tls
        - --kubelet-preferred-address-types=InternalIP
        
注释：
1、metrics默认使用hostname来通信的，而且coredns中已经添加了宿主机的/etc/resolv.conf，所以只需要添加一个内部的dns服务器或者在pod的deployment的yaml手动添加主机解析记录,再或者改变参数为InternalIP，直接用ip来连接
2、kubelet-insecure-tls: 跳过验证kubelet的ca证书，暂时开启。（不推荐用于生产环境）
```

##### 2. 部署

```
# cd metrics-server/deploy/1.8+
# kubectl apply -f .
# kubectl get pods -n kube-system | grep metrics
```

##### 3. 验证

```
# kubectl top nodes

NAME    CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%   
es-60   377m         18%    5915Mi          76%       
es-61   267m         13%    5479Mi          70% 

注意： 内存单位 Mi=1024*1024字节  M=1000*1000字节
        CPU单位 1核=1000m 即250m=1/4核
        
# kubectl top pod --all-namespaces
```
