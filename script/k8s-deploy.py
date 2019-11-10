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

def main():
    build_arg_list = []
    file_name_list = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hb:f:", ["help", "build-arg=", "file="])
        # check opts param
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit(1)
            elif opt in ("-b", "--build-arg"):
                build_arg_list.append(arg)
            elif opt in ("-f", "--file"):
                file_name_list.append(arg)
            else:
                pass

        if build_arg_list:
            build_arg = '--build-arg ' + ' --build-arg '.join(build_arg_list)
            os.environ['build_arg'] = str(build_arg)

        if file_name_list:
            try:
                with open(file_name_list[0], "r", encoding='utf-8') as f:
                    results = f.read()
                    results_dict = yaml.load(results, Loader=yaml.FullLoader)
                    if results_dict["replicaCount"] > 30 or results_dict["replicaCount"] <= 0:
                        print("\033[31;31m" "replicaCount要求范围: 大于0小于30个Pod，请重新调整replicaCount参数!" "\033[0m \n")
                        sys.exit(1)
                    helm_values_file = '-f ' + ' -f '.join(file_name_list)
            # 没有传入replicaCount参数，就走Helm默认replicaCount配置参数
            except KeyError:
                helm_values_file = '-f ' + ' -f '.join(file_name_list)
            except FileNotFoundError:
                print("\033[31;31m" "-f 或者 --file 指定的文件不存在!" "\033[0m \n")
                sys.exit(1)

        # check args param
        if len(args) == 4:
            os.environ['project'] = str(args[0])
            os.environ['server_name'] = str(args[1])
            os.environ['docker_images_version'] = str(args[2])
            os.environ['dockerfile_name'] = str(args[3])
            if os.system('docker build -t harbor.example.com/$project/$server_name:$docker_images_version . \
            -f $dockerfile_name $build_arg && \
            docker login -u admin -p ****** harbor.example.com && \
            docker push harbor.example.com/$project/$server_name:$docker_images_version') != 0:
                print("\033[31;31m" "Docker Build 失败!" "\033[0m \n")
                sys.exit(1)

            # 调用方法部署k8s
            if file_name_list:
                check_item_exists(args[0], args[1], args[2], helm_values_file)
            else:
                check_item_exists(args[0], args[1], args[2])

        elif len(args) == 5:
            # 判断第五个参数是不是 --no-cache
            if args[4] == "--no-cache":
                os.environ['project'] = str(args[0])
                os.environ['server_name'] = str(args[1])
                os.environ['docker_images_version'] = str(args[2])
                os.environ['dockerfile_name'] = str(args[3])
                if os.system('docker build --no-cache -t harbor.example.com/$project/$server_name:$docker_images_version . \
                -f $dockerfile_name $build_arg && \
                docker login -u admin -p ****** harbor.example.com && \
                docker push \
                harbor.example.com/$project/$server_name:$docker_images_version') != 0:
                    print("\033[31;31m" "Docker Build 失败!" "\033[0m \n")
                    sys.exit(1)

                # 调用方法部署k8s
                if file_name_list:
                    check_item_exists(args[0], args[1], args[2], helm_values_file)
                else:
                    check_item_exists(args[0], args[1], args[2])
            else:
                print("\033[31;31m" "第五个参数不是 --no-cache !" "\033[0m \n")
                sys.exit(1)
        else:
            usage()
            sys.exit(1)

    except getopt.GetoptError:
        print("\033[31;31m" "输入参数错误!" "\033[0m \n")
        usage()
        sys.exit(1)

if __name__ == '__main__':
    main()
