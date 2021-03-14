## Nginx 配置可视化UI展示

![Login](../img/nginx-login.png)

![Home](../img/nginx-home.png)

![Upstream](../img/nginx-upstream.png)

![listen](../img/nginx-lisner.png)

![Location](../img/nginx-location.png)

![Conf](../img/nginx-conf.png)

## 功能

- Nginx 可视化管理
- Nginx 配置管理
- Nginx 性能监控

## 部署

### 快速部署

```bash
docker run --detach \
--publish 80:80 --publish 8889:8889 \
--name nginx_ui \
--restart always \
crazyleojay/nginx_ui:latest
```

### 数据持久化部署

`配置文件路径`：/usr/local/nginx/conf/nginx.conf

```bash
docker run --detach \
--publish 80:80 --publish 8889:8889 \
--name nginx_ui \
--restart always \
--volume /home/nginx.conf:/usr/local/nginx/conf/nginx.conf \
crazyleojay/nginx_ui:latest
```

> 项目地址：https://github.com/onlyGuo/nginx-gui

## 小结

该项目适用于`测试环境`或者`本地开发环境`不适合`生产环境`，提供给不懂Nginx配置人员使用，通过Web界面能简单的配置。

## 参考链接

- https://github.com/onlyGuo/nginx-gui