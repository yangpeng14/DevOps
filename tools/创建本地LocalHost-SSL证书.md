## 背景

程序开发时，避免不了使用https加密通信，可以通过 `openssl` 工具来生成 `ssl` 证书，对于不懂的开发来说，`openssl` 工具是太难使用。有没有一个好用又简单的工具，可以试一试这个用Go语言写的命令行工具：`mkcert`，非常简单易用。

## mkcert 简介

`mkcert` 是一个使用go语言编写的生成本地自签证书的小工具，具有跨平台，使用简单，支持多域名，自动信任CA等一系列方便的特性，可供本地开发时快速创建 `https` 环境使用。

## 制作证书

`mkcert` 是制作本地信任的开发证书简单工具。它不需要任何配置。

- 创建本地CA，将CA加入本地可信CA，如下图

    ```bash
    $ mkcert -install

    Created a new local CA at "/Users/filippo/  Library/Application Support/mkcert" 💥
    The local CA is now installed in the system     trust store! ⚡️
    The local CA is now installed in the Firefox    trust store (requires browser restart)! 🦊
    ```
    ![](/img/mkcert-ca.png)

- 生成多域名证书

    ```bash
    $ mkcert example.com "*.example.com"    example.test localhost 127.0.0.1 ::1

    Using the local CA at "/Users/filippo/  Library/Application Support/mkcert" ✨

    Created a new certificate valid for the     following names 📜
     - "example.com"
     - "*.example.com"
     - "example.test"
     - "localhost"
     - "127.0.0.1"
     - "::1"

    # 证书文件输出在当前目录下
    The certificate is at "./example.com+5.pem"     and the key at "./example.com+5-key.pem" ✅
    ```

## 安装

- MacOS

    ```bash
    $ brew install mkcert
    $ brew install nss # Firefox 浏览器支持
    ```

- Linux

    首先安装 `certutil`
    ```bash
    $ sudo apt install libnss3-tools

    或者

    $ sudo yum install nss-tools

    或者

    $ sudo pacman -S nss

    或者

    $ sudo zypper install mozilla-nss-tools
    ```

    然后可以使用 [Linuxbrew](https://docs.brew.sh/Homebrew-on-Linux) 进行安装
    ```bash
    $ brew install mkcert
    ```

    或从源代码构建（需要Go 1.13+）
    ```bash
    $ git clone https://github.com/FiloSottile/mkcert
    $ cd mkcert
    $ go build -ldflags "-X main.Version=$(git describe --tags)"
    ```

- Windows

    ```bash
    $ choco install mkcert
    ```

## MacOS 引用证书

- 安装 nginx

    ```bash
    $ brew install nginx
    ```

- 配置 Nginx，再虚拟主机配置中添加下面内容

    ```
    ssl_certificate /usr/local/etc/nginx/ssl/example.com+5.pem;
    ssl_certificate_key /usr/local/etc/nginx/ssl/example.com+5-key.pem;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA';
    ```

- 重载 Nginx

    ```bash
    $ nginx -t && nginx -s reload
    ```

- 浏览器访问 https://localhost:8443

    ![](/img/localhost-ssl.png)

## 项目地址

- https://github.com/FiloSottile/mkcert