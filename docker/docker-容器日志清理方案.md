#### 一、docker 容器日志清理方案

```
# 设置一个容器服务的日志大小上限
# 在启动容器的时候增加一个参数设置该容器的日志大小，及日志驱动

--log-driver json-file  #日志驱动
--log-opt max-size=[0-9+][k|m|g] #文件的大小
--log-opt max-file=[0-9+] #文件数量
```

```
# 全局设置
编辑文件/etc/docker/daemon.json, 增加以下日志的配置

"log-driver":"json-file",
"log-opts": {"max-size":"500m", "max-file":"3"}

max-size=500m，意味着一个容器日志大小上限是500M，
max-file=3，意味着一个容器有三个日志，分别是id+.json、id+1.json、id+2.json。
```

```
# 然后重启docker守护进程

systemctl daemon-reload
systemctl restart docker

# 注意：设置的日志大小，只对新建的容器有效。
```