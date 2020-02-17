## PostgreSQL 简介[1]

`PostgreSQL` 可以说是目前功能最强大、特性最丰富和结构最复杂的开源数据库管理系统，其中有些特性甚至连商业数据库都不具备。这个起源于加州大学伯克利分校的数据库，现已成为一项国际开发项目，并且拥有广泛的用户群，尤其是在海外，目前国内使用者也越来越多。

`PostgreSQL` 基本上算是见证了整个数据库理论和技术的发展历程，由 UCB 计算机教授 Michael Stonebraker 于 1986 年创建。在此之前，Stonebraker 教授主导了关系数据库 Ingres 研究项目，88 年，提出了 Postgres 的第一个原型设计。

`MySQL` 号称是使用最广泛的开源数据库，而 `PG` 则被称为功能最强大的开源数据库。

## 创建新的用户
- 创建一个新的用户
    ```sql
    CREATE USER <username> WITH ENCRYPTED PASSWORD '<your_own_password>';
    ```

## 用户授权

- 授予 `CONNECT` 访问权限
    ```sql
    GRANT CONNECT ON DATABASE database_name TO username;
    ```

- 然后授予模式使用
    ```sql
    GRANT USAGE ON SCHEMA schema_name TO username;
    ```

- 为特定表授予 `SELECT` 权限
    ```sql
    GRANT SELECT ON table_name TO username;
    ```

- 将 `SELECT` 授予多个表
    ```sql
    # 执行格式
    GRANT SELECT ON ALL TABLES IN SCHEMA schema_name TO username;

    # 例子
    grant select on all tables in schema public to user1;
    ```

- 如果您希望将来自动授予对新表的访问权限，则必须更改默认值
    ```sql
    ALTER DEFAULT PRIVILEGES IN SCHEMA schema_name GRANT SELECT ON TABLES TO username;
    ```

## 创建数据库

- 创建以 `utf-8` 字符的数据库，并且以 `template0` 为模版创建
    ```sql
    CREATE DATABASE dbname WITH  OWNER = postgres TEMPLATE = template0 ENCODING = 'UTF8';
    ```

- 给指定用户授指定数据库所有权限
    ```sql
    GRANT ALL PRIVILEGES ON DATABASE dbname to username;
    ```

- 在执行登陆操作后提示 `FATAL： role 'root' is not permitted to log in.`
    ```sql
    alter user "root" login;
    ```

## 数据库备份与恢复
- 备份所有数据库
    ```sql
    pg_dumpall > db.out
    ```

- 恢复所有数据库
    ```sql
    # 执行这个命令的时候连接到哪个数据库无关紧要，因为pg_dumpall 创建的脚本将会包含恰当的创建和连接数据库的命令
    psql -f db.out postgres
    ```

- 备份单个数据库
    ```sql
    pg_dump -h localhost -U postgres(用户名) 数据库名(缺省时同用户名)  > /data/dum.sql
    ```

- 恢复单个数据库
    ```sql
    psql -U postgres(用户名)  数据库名(缺省时同用户名) < /data/dum.sql
    ```

- 备份单个数据库并压缩
    ```sql
    pg_dump -h localhost -U postgres(用户名) 数据库名(缺省时同用户名) | gzip > /data/dum.sql.gz
    ```

- 恢复单个压缩数据库备份
    ```sql
    gunzip < /data/dum.sql.gz | psql -h localhost -U postgres(用户名) 数据库名(缺省时同用户名)
    ```

- 备份单表操作
    ```sql
    pg_dump -U postgres -h localhost -p 5432 -t staff -f staff.sql yjl（表示数据库名称）

    -U 表示用户
    -h 表示主机
    -p 表示端口号
    -t 表示表名
    -f 表示备份后的sql文件的名字
    -d 表示要恢复数据库名称
    ```

- 恢复数据单表操作
    ```sql
    psql -U postgres -h localhost -p 5432 -d product -f staff.sql
    ```

## 查询当前链接

- 查询当前连接数
    ```sql
    # 统计当前所有连接数
    select count(1) from pg_stat_activity;

    # 查询当前连接数详细信息
    select * from pg_stat_activity;
    ```

- 查询最大连接数
    ```sql
    show max_connections;

    # 最大连接数也可以在pg配置文件中配置：
    # 在 postgresql.conf 中设置：
    max_connections = 500
    ```

## 统计数据库占用磁盘大小

- 统计各数据库占用磁盘大小
```sql
 SELECT d.datname AS Name,  pg_catalog.pg_get_userbyid(d.datdba) AS Owner,
    CASE WHEN pg_catalog.has_database_privilege(d.datname, 'CONNECT')
        THEN pg_catalog.pg_size_pretty(pg_catalog.pg_database_size(d.datname))
        ELSE 'No Access'
    END AS SIZE
FROM pg_catalog.pg_database d
    ORDER BY
    CASE WHEN pg_catalog.has_database_privilege(d.datname, 'CONNECT')
        THEN pg_catalog.pg_database_size(d.datname)
        ELSE NULL
    END DESC -- nulls first
    LIMIT 20
```

- 统计数据库中各表占用磁盘大小
```sql
# 只显示表名和占用磁盘大小
SELECT
    table_schema || '.' || table_name AS table_full_name,
    pg_size_pretty(pg_total_relation_size('"' || table_schema || '"."' || table_name || '"')) AS size
FROM information_schema.tables
ORDER BY
    pg_total_relation_size('"' || table_schema || '"."' || table_name || '"') DESC


# 详细显示各个参数
SELECT *, pg_size_pretty(total_bytes) AS total
    , pg_size_pretty(index_bytes) AS INDEX
    , pg_size_pretty(toast_bytes) AS toast
    , pg_size_pretty(table_bytes) AS TABLE
  FROM (
  SELECT *, total_bytes-index_bytes-COALESCE(toast_bytes,0) AS table_bytes FROM (
      SELECT c.oid,nspname AS table_schema, relname AS TABLE_NAME
              , c.reltuples AS row_estimate
              , pg_total_relation_size(c.oid) AS total_bytes
              , pg_indexes_size(c.oid) AS index_bytes
              , pg_total_relation_size(reltoastrelid) AS toast_bytes
          FROM pg_class c
          LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
          WHERE relkind = 'r'
  ) a
) a ORDER BY total_bytes desc;
```

## 查看 PostgreSQL 正在执行的 SQL

```sql
SELECT 
    procpid, 
    start, 
    now() - start AS lap, 
    current_query 
FROM 
    (SELECT 
        backendid, 
        pg_stat_get_backend_pid(S.backendid) AS procpid, 
        pg_stat_get_backend_activity_start(S.backendid) AS start, 
       pg_stat_get_backend_activity(S.backendid) AS current_query 
    FROM 
        (SELECT pg_stat_get_backend_idset() AS backendid) AS S 
    ) AS S 
WHERE 
   current_query <> '<IDLE>' 
ORDER BY 
   lap DESC;

# 参数解释

procpid：进程id
start：进程开始时间
lap：经过时间
current_query：执行中的sql

# 通过命令：
=# select pg_cancel_backend(线程id);

来kill掉指定的SQL语句。（这个函数只能 kill  Select 查询，而updae,delete DML不生效）

# 使用
=# select pg_terminate_backend(pid int)
可以kill 各种DML(SELECT,UPDATE,DELETE,DROP)操作

虽然可以使用 kill -9 来强制删除用户进程，但是不建议这么去做。
因为：对于执行 update 的语句来说，kill掉进程，可能会导致 Postgres 进入到 recovery mode
而在 recovery mode 下，会锁表，不允许链接数据库。
```

## 参考链接

- [1]https://jin-yang.github.io/post/postgresql-introduce.html
- https://wiki.postgresql.org/wiki/Disk_Usage
- http://www.postgres.cn/docs/9.4/app-pg-dumpall.html