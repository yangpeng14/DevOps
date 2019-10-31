#### 一、Sentry数据软清理 （清理完不会释放磁盘，如果很长时间没有运行，清理时间会很长）

```
# 登陆 sentry_worker_1 容器
$ docker exec -it sentry_worker_1 bash
 
# 保留60天数据。cleanup的使用delete命令删除postgresql数据，但postgrdsql对于delete, update等操作，只是将对应行标志为DEAD，并没有真正释放磁盘空间
$ sentry cleanup  --days 60
```

#### 二、postgres数据清理 （清理完后会释放磁盘空间）
```
# 登陆 sentry_postgres_1 容器
$ docker exec -it sentry_postgres_1 bash
 
# 运行清理
$ vacuumdb -U postgres -d postgres -v -f --analyze
```

#### 三、定时清理脚本
```
#!/usr/bin/env bash
 
docker exec -i sentry_worker_1 sentry cleanup --days 60 && docker exec -i -u postgres sentry_postgres_1 vacuumdb -U postgres -d postgres -v -f --analyze
```
