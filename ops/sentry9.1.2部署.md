# 一、Sentry 介绍
Sentry 是一个开源的实时错误报告工具，支持 web 前后端、移动应用以及游戏，支持 Python、OC、Java、Go、Node.js、Django、RoR [等主流编程语言和框架](https://getsentry.com/platforms/) ，还提供了 GitHub、Slack、Trello 等常见开发工具的[集成](https://getsentry.com/integrations/)。

# 二、Sentry 基本概念
## Sentry 是什么
通常我们所说的 Sentry 是指 Sentry 的后端服务，由 Django 编写。8.0 版本使用了 React.js 构建前端 UI。使用 Sentry 前还需要在自己的应用中配置 Sentry 的 SDK —— 通常在各语言的包管理工具中叫做 Raven。

当然，Sentry 还可以是其公司所提供的 Sentry SaaS 服务。

## DSN（Data Source Name）
Sentry 服务支持多用户、多团队、多应用管理，每个应用都对应一个 PROJECT_ID，以及用于身份认证的 PUBLIC_KEY 和 SECRET_KEY。由此组成一个这样的 DSN：

`'{PROTOCOL}://{PUBLIC_KEY}:{SECRET_KEY}@{HOST}/{PATH}{PROJECT_ID}'`

PROTOCOL 通常会是 http 或者 https，HOST 为 Sentry 服务的主机名和端口，PATH 通常为空。

# 三、Docker部署Sentry服务
## 官方提供Docker部署配置
[官方Docker部署仓库](https://github.com/getsentry/onpremise)

## 环境要求
1. Docker 17.05.0+
2. Docker-Compose 1.17.0+
3. 服务器配置只少需要3G内存

## 修改配置文件
1. 拉取官方配置 `git pull https://github.com/getsentry/onpremise`
2. 修改 `config.yml` 邮箱设置和system.url-prefix
```bash
mail.backend: 'smtp'  # Use dummy if you want to disable email entirely
mail.host: 'localhost'
mail.port: 25
mail.username: ''
mail.password: ''
mail.use-tls: false
mail.from: 'root@localhost'
mail.subject-prefix: '[Sentry] '

system.url-prefix: 'https://sentry.example.com'
```

3. 修改`docker-compose.yml` 配置，本人直接挂载宿主机目录上，没有使用docker volumes
```bash
#volumes:
#    sentry-data:
#      external: true
#    sentry-postgres:
#      external: true
```

4. 修改`sentry.conf.py`配置
```bash
# 在配置文件中 # General # 下面添加
SENTRY_DEFAULT_TIME_ZONE = 'Asia/Shanghai'

# 修改 workers 参数根据机器cpu核心来设置，添加 buffer-size 参数
SENTRY_WEB_OPTIONS = {
    'http': '%s:%s' % (SENTRY_WEB_HOST, SENTRY_WEB_PORT),
    'protocol': 'uwsgi',
    # This is need to prevent https://git.io/fj7Lw
    'uwsgi-socket': None,
    'http-keepalive': True,
    'memory-report': False,
    'workers': 3,  # the number of web workers
    'buffer-size': 32768,
}
```

5. 设置 `SENTRY_SECRET_KEY` 
```bash
$ cp .env.example .env
$ docker-compose run web config generate-secret-key # 获取 sentry key 值
$ cp .env.example .env # copy
$ vim .env # 把刚才生成的sentry key 配置到 SENTRY_SECRET_KEY='**************'
```

## 添加钉钉通知支持
1. `vim requirements.txt`
```bash
# Add plugins here
sentry-dingding~=0.0.2  # 钉钉通知插件
django-smtp-ssl~=1.0  # 发邮件支持SSL协议
redis-py-cluster==1.3.4
```

# 四、构建
## Docker build
`注意：`部署Sentry，以后如果添加新的插件支持或者修改参数都得重新build

`docker-compose build --pull` # Build the services again after updating, and make sure we're up to date on patch version

`docker-compose run --rm web upgrade` # Run new migrations

`docker-compose up -d` # Recreate the services

启动后`docker-compose ps`看到的结果
```bash
       Name                     Command               State           Ports
------------------------------------------------------------------------------------
sentry_cron_1        /entrypoint.sh run cron          Up      9000/tcp
sentry_memcached_1   docker-entrypoint.sh memcached   Up      11211/tcp
sentry_postgres_1    docker-entrypoint.sh postgres    Up      5432/tcp
sentry_redis_1       docker-entrypoint.sh redis ...   Up      6379/tcp
sentry_smtp_1        docker-entrypoint.sh exim  ...   Up      25/tcp
sentry_web_1         /entrypoint.sh run web           Up      0.0.0.0:9000->9000/tcp
sentry_worker_1      /entrypoint.sh run worker        Up      9000/tcp
```

## 构建后镜像名描述
名称 | 描述
---|---
sentry_cron	| 定时任务，使用的是celery-beat
sentry_memcached | memcached
sentry_postgres | pgsql数据库
sentry_redis | 运行celery需要的服务
sentry_smtp | 邮件服务
sentry_web | 使用django+drf写的一套Sentry Web界面
sentry_worker | celery的worker服务，用来跑异步任务的

# 五、配置外部反向代理
## 配置Nginx Sentry虚拟主机配置
```bash
upstream sentry {
  server sentry-host:9000;
}

server {
    listen   80;
    server_name sentry.example.com;

    location / {
      if ($request_method = GET) {
        rewrite  ^ https://$host$request_uri? permanent;
      }
      return 405;
    }
  }

  server {
    listen   443 ssl;
    server_name sentry.example.com;

    proxy_set_header   Host                 $http_host;
    proxy_set_header   X-Forwarded-Proto    $scheme;
    proxy_set_header   X-Forwarded-For      $remote_addr;
    proxy_redirect     off;

    # keepalive + raven.js is a disaster
    keepalive_timeout 0;

    # use very aggressive timeouts
    proxy_read_timeout 5s;
    proxy_send_timeout 5s;
    send_timeout 5s;
    resolver_timeout 5s;
    client_body_timeout 5s;

    # buffer larger messages
    client_max_body_size 50m;
    client_body_buffer_size 100k;

    location / {
      proxy_pass        http://sentry;

      add_header Strict-Transport-Security "max-age=31536000";
    }
}
```

# 六、Sentry历史数据清理
## Sentry数据软清理 （清理完不会释放磁盘，如果很长时间没有运行，清理时间会很长）
1. 保留60天数据。cleanup的使用delete命令删除postgresql数据，但postgrdsql对于delete, update等操作，只是将对应行标志为DEAD，并没有真正释放磁盘空间
```bash
$ docker exec -it sentry_worker_1 bash
$ sentry cleanup  --days 60
```

2. postgres数据清理 （清理完后会释放磁盘空间）

```bash
$ docker exec -it sentry_postgres_1 bash
$ vacuumdb -U postgres -d postgres -v -f --analyze
```

3. 定时清理脚本
```bash
#!/usr/bin/env bash
 
docker exec -i sentry_worker_1 sentry cleanup --days 60 && docker exec -i -u postgres sentry_postgres_1 vacuumdb -U postgres -d postgres -v -f --analyze
```