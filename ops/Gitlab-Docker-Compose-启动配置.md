#### 一、配置 gitlab 

1. gitlab-ce 开启https
```
# 参考: https://docs.gitlab.com/omnibus/settings/nginx.html#manually-configuring-https

external_url 'https://gitlab.example.com'
nginx['enable'] = true
nginx['redirect_http_to_https'] = true    # http重定向到https
nginx['redirect_http_to_https_port'] = 80
```

2. 申请Let's Encrypt证书并手动添加证书
```
# /mnt/gitlab-docker/config 是挂载宿主机目录

$ mkdir -p /mnt/gitlab-docker/config/ssl
$ chmod 700 /mnt/gitlab-docker/config/ssl
$ cp gitlab.example.com.key gitlab.example.com.crt /mnt/gitlab-docker/config/ssl
```

3. gitlab-ce docker-compose 完整配置
```
version: '2'
services:
  gitlab:
    image: 'gitlab/gitlab-ce:12.4.1-ce.0'
    restart: always
    container_name: gitlab
    hostname: 'gitlab'
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'https://code.example.com'
        nginx['enable'] = true
        nginx['redirect_http_to_https'] = true
        nginx['redirect_http_to_https_port'] = 80
        # 开启 pages 功能
        pages_external_url 'http://pages.example.com'
        gitlab_pages['inplace_chroot'] = true
        gitlab_rails['lfs_enabled'] = true
        # 设置时区为北京时间
        gitlab_rails['time_zone'] = 'PRC'
        gitlab_rails['gitlab_email_enabled'] = true
        gitlab_rails['gitlab_email_from'] = 'code@example.com'
        gitlab_rails['gitlab_email_display_name'] = 'code'
        gitlab_rails['gitlab_email_reply_to'] = 'code@example.com'
        gitlab_rails['smtp_enable'] = true
        gitlab_rails['smtp_address'] = 'smtp.exmail.qq.com'
        gitlab_rails['smtp_port'] = 465
        gitlab_rails['smtp_user_name'] = 'code@example.com'
        gitlab_rails['smtp_password'] = '******'
        gitlab_rails['smtp_domain'] = 'exmail.qq.com'
        gitlab_rails['smtp_authentication'] = 'login'
        gitlab_rails['smtp_enable_starttls_auto'] = true
        gitlab_rails['smtp_tls'] = true
        unicorn['worker_processes'] = 2
        unicorn['worker_timeout'] = 60
        sidekiq['concurrency'] = 4
        # 解决 GitLab 响应 Forbidden
        gitlab_rails['rack_attack_git_basic_auth'] = {'enabled' => true, 'ip_whitelist' => ["0.0.0.0"], 'maxretry' => 300, 'findtime' => 5, 'bantime' => 60}
    # 内存和CPU限制，worker_processes 配置声明使用2核CPU
    mem_limit: 5500m
    cpu_shares: 200 #2核
    ports:
      - '443:443'
      - '80:80'
      - '22:22'
    volumes:
      # 挂载宿主机目录可以根据实际情况挂载
      - '/mnt/gitlab-docker/config:/etc/gitlab'
      - '/mnt/gitlab-docker/logs:/var/log/gitlab'
      - '/mnt/gitlab-docker/data:/var/opt/gitlab'
      - '/etc/localtime:/etc/localtime'
```

#### 二、测试gitlab邮件服务

```
$ docker exec -it gitlab bash
$ gitlab-rails console

irb(main):003:0> Notify.test_email('code@example.com', 'Message Subject', 'Message Body').deliver_now
```