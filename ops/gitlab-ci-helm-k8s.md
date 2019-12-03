## Gitlab 和 Kubernetes CI/CD流程图
![](/img/gitlab-k8s.png)

## Gitlab 和 Gitlab CI搭建参考往期文章
- https://github.com/yangpeng14/DevOps/blob/master/ops/Gitlab-Docker-Compose-%E5%90%AF%E5%8A%A8%E9%85%8D%E7%BD%AE.md
- https://github.com/yangpeng14/DevOps/blob/master/ops/gitlab-ci-%E6%90%AD%E5%BB%BA%E6%8C%81%E7%BB%AD%E9%9B%86%E6%88%90%E7%8E%AF%E5%A2%83.md

## Helm安装(gitlab runner机器上安装)
- 安装目前最新helm 2.16.0版本
```
$ wget https://get.helm.sh/helm-v2.16.0-linux-amd64.tar.gz
$ tar -zvf helm-v2.16.0-linux-amd64.tar.gz
$ cd linux-amd64/
$ cp helm /usr/local/bin
```

- 验证Helm
```
helm version
Client: &version.Version{SemVer:"v2.16.0", GitTreeState:"clean"}
Server: &version.Version{SemVer:"v2.16.0", itTreeState:"clean"}
```

- 初始化Helm
```
$ helm init --client-only
$ helm plugin install https://github.com/chartmuseum/helm-push
```

- 更新repo为阿里源
```
$ helm repo remove stable
$ helm repo add ali https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts
```

## Gitlab CI 文件配置样例
```bash
stages:
  - test
  - deploy

# test job
job 1:
  stage: test
  only: 
    - master
  tags:
    - tag-test
  script: echo "单元测试"

# deploy 阶段把 docker build 和 k8s部署 放在一个阶段
job 2:
  stage: deploy
  only: 
    - master
  tags:
    - tag-test
  script:
    - echo "Deploy ..."
    # deploy 自己写的python部署脚本
    # helm.yaml helm values配置文件
    # product-line 产品线
    # project-name 项目名称，如果多分支可以使用 project-name-$CI_COMMIT_REF_NAME
    # $(date "+%Y%m%d%H%M%S")-${CI_COMMIT_SHA:0:6} docker tag
    # Dockerfile 构建项目dockerfile
    - deploy -f helm.yaml product-line project-name $(date "+%Y%m%d%H%M%S")-${CI_COMMIT_SHA:0:6} Dockerfile 
  when: manual
```

## deploy 部署脚本
- 下面是 deploy 部分代码，获取脚本全部代码，请关注我的 `YP小站` 公众号并回复 `获取deploy代码`

```python
#!/usr/bin/env python3

import sys
import os
import getopt
import yaml
import pykube

def usage():
    print("Usage: %s [ -b | --build-arg | -f | --file ] product-line project-name docker_images_version dockerfile_name --no-cache" % sys.argv[0], "\n", "or",
    "Usage: %s [ -b | --build-arg | -f | --file ] product-line project-name docker_images_version dockerfile_name" % sys.argv[0], "\n\n",
    "-b, --build-arg 声明Dockerfile中环境变量，参数可以指定多次，示例 A=b, ", "\n",
    "-f, --file 指定Helm values.yaml文件，参数只能指定一次，指定多个也只会取第一个值")

def check_item_exists(project, server_name, docker_images_version, *args):
    api = pykube.HTTPClient(pykube.KubeConfig.from_file("k8s config"))
    deploy = pykube.Deployment.objects(api).filter(namespace=project)
    os.environ['project'] = str(project)
    os.environ['server_name'] = str(server_name)
    os.environ['docker_images_version'] = str(docker_images_version)
    os.environ['s_name'] = str(server_name)
    if args:
        os.environ['helm_values_file'] = str(args[0])

    if os.system('helm status $server_name 1> /dev/null 2>&1') == 0:
        os.system("echo '\033[1;32;40m' 'Helm滚动发布、超时为5分钟、失败在本次基础上自动回滚上一个版本。' '\033[0m \n'")
        os.system('helm upgrade --timeout 300 --atomic --install $server_name --namespace $project \
        --set serverName=$server_name --set image.project=$project \
        --set serverFeatureNameReplace=$server_name \
        --set image.tag=$docker_images_version "Helm warehouse address" $helm_values_file')
        return
    else:
        # 兼容过去没有使用Helm部署
        for deployment in deploy:
            if server_name == str(deployment):
                # deployment进行滚动升级
                os.system('kubectl set image deployment/$server_name \
                 $server_name=harbor.example.com/$project/$server_name:$docker_images_version \
                 --namespace=$project')
                return

    # 部署新项目
    # 使用helm模板部署服务
    os.system('helm install --name $server_name --namespace $project \
    --set serverName=$server_name --set image.project=$project \
    --set serverFeatureNameReplace=$server_name \
    --set image.tag=$docker_images_version "Helm warehouse address" $helm_values_file')
    return
```

## 参考文献
https://blog.csdn.net/ygqygq2/article/details/85097857
