## Harbor 简介
Harbor是一个用于存储和分发Docker镜像的企业级Registry服务器，通过添加一些企业必需的功能特性，例如安全、标识和管理等，扩展了开源Docker Distribution。作为一个企业级私有Registry服务器，Harbor提供了更好的性能和安全。提升用户使用Registry构建和运行环境传输镜像的效率。Harbor支持安装在多个Registry节点的镜像资源复制，镜像全部保存在私有Registry中， 确保数据和知识产权在公司内部网络中管控。另外，Harbor也提供了高级的安全特性，诸如用户管理，访问控制和活动审计等

## Harbor 回收镜像难点
- Harbor 镜像回收分两步，`第一步`清理镜像的tag，这是删除镜像关联关系并没有真正释放磁盘。`第二步 垃圾回收`，释放磁盘空间。
- Harbor 从1.7.0 开始提供不停服务运行`垃圾回收功能`，运行垃圾回收时，Harbor`数据库`处于`只读`状态。
- Harbor 磁盘回收难点在于清理`镜像关联的tag`，虽然控制台提供删除功能，但镜像很多时我们不可能一个个去点击删除，这样很浪费时间，下面就是今天要讲的调取`Harbor Api`接口清理镜像关联的tag。

## 运行本程序要求
- Harbor 结构要求`product_line/project/tag`。例：`B线/hello:20190912123205-c808c4`
- K8s 要求 namespace 下面是 project ，并且和Harbor结构是一一对应。原因是因为`程序`需要连接k8s查询需要`保留目前使用的镜像版本`。
- 目前程序`只测试过 Harbor v1.7.0`，测试是没有问题的
- `Python3.5+`
- `官方 Python SDK`已经不维护了，本程序是在官方 python sdk 基础上修改
- 程序分两块，分别是`harborclient_modify_v1_7_0` 和 `清理程序`

## harborclient_modify_v1_7_0 代码
```python
#!/usr/bin/env python3
# -*- coding=utf8 -*-

import json
import logging
import requests

logging.basicConfig(level=logging.INFO)


class HarborClient(object):
    def __init__(self, host, user, password, protocol="http"):
        self.host = host
        self.user = user
        self.password = password
        self.protocol = protocol

        self.session_id = self.login()

    # def __del__(self):
    #     self.logout()

    def login(self):
        login_data = requests.post('%s://%s/c/login' %
                                   (self.protocol, self.host),
                                   data={'principal': self.user,
                                         'password': self.password})

        if login_data.status_code == 200:
            session_id = login_data.cookies.get('sid')

            logging.debug("Successfully login, session id: {}".format(
                session_id))
            return session_id
        else:
            logging.error("Fail to login, please try again")
            return None

    def logout(self):
        requests.get('%s://%s/c/logout' % (self.protocol, self.host),
                     cookies={'sid': self.session_id})
        logging.debug("Successfully logout")

    # GET /projects
    def get_projects(self, project_name=None, is_public=None):
        # TODO: support parameter
        result = None
        path = '%s://%s/api/projects' % (self.protocol, self.host)
        response = requests.get(path,
                                cookies={'sid': self.session_id})
        if response.status_code == 200:
            result = response.json()
            logging.debug("Successfully get projects result: {}".format(
                result))
        else:
            logging.error("Fail to get projects result")
        return result

    # GET /repositories
    def get_repositories(self, project_id, query_string=None):
        # TODO: support parameter
        result = None
        path = '%s://%s/api/repositories?project_id=%s' % (
            self.protocol, self.host, project_id)
        response = requests.get(path,
                                cookies={'sid': self.session_id})
        if response.status_code == 200:
            result = response.json()
            logging.debug(
                "Successfully get repositories with id: {}, result: {}".format(
                    project_id, result))
        else:
            logging.error("Fail to get repositories result with id: {}".format(
                project_id))
        return result

    # DELETE /repositories
    def delete_repository(self, repo_name, tag=None):
        # TODO: support to check tag
        # TODO: return 200 but the repo is not deleted, need more test
        result = False
        path = '%s://%s/api/repositories/%s' % (self.protocol,
                                                          self.host, repo_name)
        response = requests.delete(path,
                                   cookies={'sid': self.session_id})
        if response.status_code == 200:
            result = True
            print("Delete {} successful!".format(repo_name))
            logging.debug("Successfully delete repository: {}".format(
                repo_name))
        else:
            logging.error("Fail to delete repository: {}".format(repo_name))
        return result

    # Get /repositories/{repo_name}/tags
    def get_repository_tags(self, repo_name):
        result = None
        path = '%s://%s/api/repositories/%s/tags' % (
            self.protocol, self.host, repo_name)
        response = requests.get(path,
                                cookies={'sid': self.session_id}, timeout=60)
        if response.status_code == 200:
            result = response.json()
            logging.debug(
                "Successfully get tag with repo name: {}, result: {}".format(
                    repo_name, result))
        else:
            logging.error("Fail to get tags with repo name: {}".format(
                repo_name))
        return result

    # Del /repositories/{repo_name}/tags/{tag}
    def del_repository_tag(self, repo_name, tag):
        result = False
        path = '%s://%s/api/repositories/%s/tags/%s' % (
            self.protocol, self.host, repo_name, tag)
        response = requests.delete(path,
                                   cookies={'sid': self.session_id})
        if response.status_code == 200:
            result = True
            print("Delete {} {} successful!".format(repo_name, tag))
            logging.debug(
                "Successfully delete repository repo_name: {}, tag: {}".format(
                    repo_name, tag))
        else:
            logging.error("Fail to delete repository repo_name: {}, tag: {}".format(
                repo_name, tag))
        return result

```

## 清理程序
```python
#!/usr/bin/env python3
# -*- coding=utf8 -*-

import sys
import harborclient_modify_v1_7_0
import pykube
import time

class GetK8sApi(object):
    # 判断harbor传入的项目是否存在k8s中
    def get_deployment(self, namespace, deployment_name):
        result = None
        try:
            api = pykube.HTTPClient(pykube.KubeConfig.from_file("k8s config"))
            deploy_out = pykube.Deployment.objects(api).filter(namespace=namespace).get(name=deployment_name)
            result = deploy_out.obj["spec"]["template"]["spec"]["containers"][0]["image"].split(":")[1]
            return result
        except pykube.exceptions.ObjectDoesNotExist:
            return result

class GetHarborApi(object):
    def __init__(self, host, user, password, protocol="http"):
        self.host = host
        self.user = user
        self.password = password
        self.protocol = protocol
        self.client = harborclient_modify_v1_7_0.HarborClient(self.host, self.user, self.password, self.protocol)

    # Del repo_name tag
    def del_repo_name_tag(self, repo_name, tag):
        for repo_name_tag in self.client.get_repository_tags(repo_name):
            if repo_name_tag['name'] != tag:
                self.client.del_repository_tag(repo_name, repo_name_tag['name'])

    # Del repo_name
    def del_repo_name(self, repo_name):
        self.client.delete_repository(repo_name)

    # 软删除harbor不用的项目及镜像
    def main(self):
        get_k8s_api = GetK8sApi()
        for projects in self.client.get_projects():
            # 公共基础镜像不用清理
            if projects['name'] != "public" and projects['name'] != "library" and len(
                    self.client.get_repositories(projects['project_id'])):
                for project_repo_name in self.client.get_repositories(projects['project_id']):
                    k8s_image_tag = get_k8s_api.get_deployment(project_repo_name['name'].split("/")[0], project_repo_name['name'].split("/")[1])
                    if k8s_image_tag is None:
                        self.del_repo_name(project_repo_name['name'])
                        time.sleep(3)
                    else:
                        self.del_repo_name_tag(project_repo_name['name'], k8s_image_tag)
                        time.sleep(3)
            # harbor中项目名和k8s中deploymnet名称不一致，暂时不处理，下面比如 test 项目
            elif projects['name'] == "test":
                pass

if __name__ == '__main__':
    sys.path.append("../")
    host = "domain"
    user = "user"
    password = "******"
    protocol = "https"
    cline_get = GetHarborApi(host, user, password, protocol)
    cline_get.main()
```