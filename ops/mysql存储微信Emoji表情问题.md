## 问题

`Tomcat` 中报 `Java` 如下错误：

```
java.sql.SQLException: Incorrect string value: '\xF0\x9F\x8D\x87 \xE7...' for column 'name' at row 1
        at com.mysql.jdbc.SQLError.createSQLException(SQLError.java:1078)
        at com.mysql.jdbc.MysqlIO.checkErrorPacket(MysqlIO.java:4187)
        at com.mysql.jdbc.MysqlIO.checkErrorPacket(MysqlIO.java:4119)
        at com.mysql.jdbc.MysqlIO.sendCommand(MysqlIO.java:2570)
        at com.mysql.jdbc.MysqlIO.sqlQueryDirect(MysqlIO.java:2731)
        at com.mysql.jdbc.ConnectionImpl.execSQL(ConnectionImpl.java:2815)
        at com.mysql.jdbc.PreparedStatement.executeInternal(PreparedStatement.java:2155)
        at com.mysql.jdbc.PreparedStatement.execute(PreparedStatement.java:1379)
        at com.alibaba.druid.filter.FilterChainImpl.preparedStatement_execute
```

上面错误意思是 `mysql` 数据库中 `name` 字段插入`不正确的字符串值`。`name` 字段是记录`微信呢称`，设计之出没有考虑到微信呢称中使用 `Emoji` 表情，导致写入数据失败。

## 问题根本原因

`Mysql` 版本是 `5.7.22`，当时使用下面命令创建数据库，使用 `utf8` 编码。但 `utf8` 不支持 `Emoji` 表情。 

```sql
create database if not exists my_db default charset utf8 collate utf8_general_ci;
```

## utf8 为什么不支持 Emoji

utf8不支持emoji，是因为`emoji`是用`4个字节`存储的字符，而`mysql`的utf8只能存储`1-3个字节`的字符。


## 解决思路

- （1）Mysql 服务器 client、mysql、mysqld 中需要显式指定字符集为 utf8mb4
- （2）在(1)的服务器上创建的db，需要为 `utf8mb4` 字符集，`COLLATE` 为 `utf8mb4_unicode_ci` 或 `utf8mb4_general_ci`
- （3）在(2)的db中创建 `table` 和存放`emoji字段`的字符集为 `utf8mb4`，`collate` 为 `utf8mb4_unicode_ci` 或 `utf8mb4_general_ci`。
- （4）`MySQL驱动`最低不能低于 `5.1.13`，5.1.34 可用。

`utf8_unicode_ci` 与 `utf8_general_ci` 比较：

- utf8_unicode_ci 和 utf8_general_ci 对中、英文来说没有实质的差别。
- utf8_general_ci 校对速度快，但准确度稍差。
- utf8_unicode_ci 准确度高，但校对速度稍慢。

`小结`：如果你的应用有德语、法语或者俄语，请一定使用 `utf8_unicode_ci`。一般用 `utf8_general_ci` 就足够。

## utf8mb4 mysql最低版本支持

`注意`：`utf8mb4` 最低 `mysql` 版本支持为 `5.5.3+`，若不是，请升级到较新版本。

MySQL 在 `5.5.3` 之后增加了 `utf8mb4` 字符编码，mb4即 most bytes 4。简单说 utf8mb4 是 utf8 的超集并完全兼容utf8，能够用四个字节存储更多的字符。

但抛开数据库，标准的 UTF-8 字符集编码是可以用 1~4 个字节去编码21位字符，这几乎包含了是世界上所有能看见的语言了。
然而在MySQL里实现的utf8最长使用3个字节，也就是只支持到了 Unicode 中的 基本多文本平面 （U+0000至U+FFFF），包含了控制符、拉丁文，中、日、韩等绝大多数国际字符，但并不是所有，最常见的就算现在手机端常用的表情字符 emoji和一些不常用的汉字，这些需要四个字节才能编码出来。

## 具体解决方法操作

### 修改 /etc/mysql/my.cnf （配置一般情况都存放这里），添加如下内容

```
[client]
default-character-set = utf8mb4

[mysql]
default-character-set = utf8mb4

[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
init_connect='SET NAMES utf8mb4'
```

### 重启数据库，检查变量

```
mysql> SHOW VARIABLES WHERE Variable_name LIKE 'character_set_%' OR Variable_name LIKE 'collation%';

Variable_name	Value
character_set_client	utf8mb4
character_set_connection utf8mb4
character_set_database	utf8mb4
character_set_filesystem binary
character_set_results	utf8mb4
character_set_server	utf8mb4
character_set_system	utf8
collation_connection	utf8mb4_unicode_ci
collation_database	utf8mb4_unicode_ci
collation_server	utf8mb4_unicode_ci
```

### 必须保证下面几个变量是 `utf8mb4`

系统变量 | 描述
---|---
character_set_client | 客户端来源数据使用的字符集
character_set_connection | 连接层字符集
character_set_database | 当前选中数据库的默认字符集
character_set_results | 查询结果字符集
character_set_server | 默认的内部操作字符集

### 将数据库 和 已经建好的表也转换成 utf8mb4

```sql
ALTER DATABASE database_name CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci; # 更改数据库编码 
ALTER TABLE table_name CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; # 更改表编码
ALTER TABLE table_name CHANGE column_name VARCHAR(191) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;  # 更改列的编码
```

`查询字符集编码`

```sql
show create database fangdai_CMS; # 查询数据库编码
show create table t_member; # 查询表编码
show full columns from t_member; # 查询所有表字段编码
```

### 数据库连接配置

添加 `characterEncoding=utf8` 会被自动识别为 utf8mb4 ；`autoReconnect=true` 参数必做添加。

## 参考链接

- https://yq.aliyun.com/articles/269558#
- https://blog.csdn.net/u010129985/article/details/83756180