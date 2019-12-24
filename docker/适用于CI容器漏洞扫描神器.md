## Trivy 简介

`Trivy` 是一个用于容器简单而全面的漏洞扫描程序。软件漏洞是软件或操作系统中存在的故障，缺陷或弱点。 `Trivy` 检测OS软件包（Alpine，RHEL，CentOS等）的漏洞和应用程序依赖项（捆绑程序，Composer，npm，yarn等）。 Trivy易于使用。只需安装二进制文件即可开始扫描。扫描所需要做的就是指定容器 Image 名称。

也可以用于CI，在推送到容器仓库之前，可以轻松扫描本地容器镜像。

## Trivy 特性

- 全面检测漏洞
    - 支持操作系统 (Alpine, Red Hat Universal Base Image, Red Hat Enterprise Linux, CentOS, Oracle Linux, Debian, Ubuntu, Amazon Linux, openSUSE Leap, SUSE Enterprise Linux and Distroless)
    - 应用依赖 (Bundler, Composer, Pipenv, npm, yarn and Cargo)

- 简单
    - 只要指定 image 名称
    - 详情请看 [Quick Start](https://github.com/aquasecurity/trivy#quick-start) 和 [Examples](https://github.com/aquasecurity/trivy#examples)

- 易于安装
    - apt-get install，yum install，brew install（请参阅[安装](https://github.com/aquasecurity/trivy#installation)）
    - 没有依赖包

- 准确度高
    - 特别是 `Alpine Linux` 和 `RHEL/CentOS`
    - 其他操作系统也很高

- 开发安全
    - 适用于CI，例如 Travis CI，CircleCI，Jenkins等。
    - 请参阅 [CI示例](https://github.com/aquasecurity/trivy#continuous-integration-ci)


## 结果输出

![](/img/trivy-usage1.png)

![](/img/trivy-usage2.png)

## 安装

- RHEL/CentOS

    ```bash
    $ sudo vim /etc/yum.repos.d/trivy.repo

    [trivy]
    name=Trivy repository
    baseurl=https://aquasecurity.github.io/trivy-repo/rpm/releases/$releasever/$basearch/
    gpgcheck=0
    enabled=1

    $ sudo yum -y update
    $ sudo yum -y install trivy
    ```

    或者 

    ```bash
    $ rpm -ivh https://github.com/aquasecurity/trivy/releases/download/v0.1.6/trivy_0.1.6_Linux-64bit.rpm
    ```

- Debian/Ubuntu

    ```bash
    $ sudo apt-get install wget apt-transport-https gnupg lsb-release
    $ wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
    $ echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | sudo tee -a /etc/apt/sources.list.d/trivy.list
    $ sudo apt-get update
    $ sudo apt-get install trivy
    ```

    或者

    ```bash
    $ sudo apt-get install rpm
    $ wget https://github.com/aquasecurity/trivy/releases/download/v0.1.6/trivy_0.1.6_Linux-64bit.deb
    $ sudo dpkg -i trivy_0.1.6_Linux-64bit.deb
    ```

- macOS

    ```bash
    $ brew install aquasecurity/trivy/trivy
    ```

## 例子

- 扫描镜像

    ```bash
    $ trivy python:3.6.4
    ```

    结果输出：
    ![](/img/trivy-3.png)

- 扫描镜像文件

    ```bash
    $ docker save ruby:2.3.0-alpine3.9 -o ruby-2.3.0.tar
    $ trivy --input ruby-2.3.0.tar
    ```
- 将结果另存为JSON

    ```bash
    $ trivy -f json -o results.json python:3.6.4
    ```

    结果输出：
    ![](/img/trivy-json.png)

- 按严重程度过滤漏洞

    ```bash
    $ trivy --severity HIGH,CRITICAL ruby:2.3.0
    ```

- 按类型过滤漏洞

    ```bash
    $ trivy --vuln-type os ruby:2.3.0
    ```

## 持续集成（CI）

- GitLab CI 例子

    ```bash
    $ cat .gitlab-ci.yml

    stages:
      - test

    trivy:
      stage: test
      image: docker:19.03.1
      services:
        - name: docker:dind
          entrypoint: ["env", "-u", "DOCKER_HOST"]
          command: ["dockerd-entrypoint.sh"]
      variables:
        DOCKER_HOST: tcp://docker:2375/
        DOCKER_DRIVER: overlay2
        # See https://github.com/docker-library/docker/pull/166
        DOCKER_TLS_CERTDIR: ""
      before_script:
        - apk add --no-cache curl
        - export VERSION=$(curl --silent "https://api.github.com/repos/aquasecurity/trivy/releases/ latest" | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')
        - echo $VERSION
        - wget https://github.com/aquasecurity/trivy/releases/download/v${VERSION}/trivy_${VERSION} _Linux-64bit.tar.gz
        - tar zxvf trivy_${VERSION}_Linux-64bit.tar.gz
      allow_failure: true
      script:
        - docker build -t trivy-ci-test:$CI_COMMIT_SHA .
        - ./trivy --exit-code 0 --cache-dir $CI_PROJECT_DIR/.trivycache/ --no-progress --severity HIGH  trivy-ci-test:$CI_COMMIT_SHA
        - ./trivy --exit-code 1 --severity CRITICAL  --no-progress trivy-ci-test:$CI_COMMIT_SHA
      cache:
        paths:
          - $CI_PROJECT_DIR/.trivycache/
    ```

## 总结

`Trivy` 非常适合用于持续集成，这是把握容器安全第一道关卡。

## 参考链接

> https://github.com/aquasecurity/trivy