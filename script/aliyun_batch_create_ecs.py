#!/usr/bin/env python3
# coding=utf-8

# Aliyun ECS Python SDK 版本大于 4.4.3 即可 pip3 install aliyun-python-sdk-ecs

import json
import time
import traceback
import argparse
import socket
import select
import ast

from paramiko import SSHClient, AutoAddPolicy, ssh_exception
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
from aliyunsdkecs.request.v20140526.RunInstancesRequest import RunInstancesRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest

RUNNING_STATUS = 'Running'
CHECK_INTERVAL = 3
CHECK_TIMEOUT = 180


class AliyunRunInstancesExample(object):

    def __init__(self):
        params_dict = self.parse_args()
        self.access_id = params_dict["access_id"]
        self.access_secret = params_dict["access_secret"]

        # 是否只预检此次请求。true：发送检查请求，不会创建实例，也不会产生费用；false：发送正常请求，通过检查后直接创建实例，并直接产生费用
        self.dry_run = params_dict["dry_run"]
        # 实例所属的地域ID
        self.region_id = params_dict["region_id"]
        # 实例的资源规格
        self.instance_type = params_dict["instance_type"]
        # 实例的计费方式
        self.instance_charge_type = params_dict["instance_charge_type"]
        # 镜像ID
        self.image_id = params_dict["image_id"]
        # 指定新创建实例所属于的安全组ID
        self.security_group_id = params_dict["security_group_id"]
        # 购买资源的时长
        self.period = params_dict["period"]
        # 购买资源的时长单位
        self.period_unit = params_dict["period_unit"]
        # 实例所属的可用区编号
        self.zone_id = params_dict["zone_id"]
        # 网络计费类型
        self.internet_charge_type = params_dict["internet_charge_type"]
        # 虚拟交换机ID
        self.vswitch_id = params_dict["vswitch_id"]
        # 实例名称
        self.instance_name = params_dict["instance_name"]
        # 实例的密码
        self.password = params_dict["password"]
        # 指定创建ECS实例的数量
        self.amount = params_dict["amount"]
        # 公网出带宽最大值
        self.internet_max_bandwidth_out = params_dict["internet_max_bandwidth_out"]
        # 是否为实例名称和主机名添加有序后缀
        self.unique_suffix = params_dict["unique_suffix"]
        # 是否为I/O优化实例
        self.io_optimized = params_dict["io_optimized"]
        # 是否开启安全加固
        self.security_enhancement_strategy = params_dict["security_enhancement_strategy"]
        # 自动释放时间
        self.auto_release_time = params_dict["auto_release_time"]
        # 系统盘大小
        self.system_disk_size = params_dict["system_disk_size"]
        # 系统盘的磁盘种类
        self.system_disk_category = params_dict["system_disk_category"]
        # data_disks 和 tags 参数由str类型转换为list类型
        # 数据盘
        self.data_disks = ast.literal_eval(params_dict["data_disks"])
        # 实例、安全组、磁盘和主网卡的标签
        self.tags = ast.literal_eval(params_dict["tags"])

        self.client = AcsClient(self.access_id, self.access_secret, self.region_id)

    def parse_args(self):
        parser = argparse.ArgumentParser(description='Aliyun ECS创建参数选项')
        parser.add_argument("--access_id", "-access_id", type=str, required=True, help="Aliyun ak id")
        parser.add_argument("--access_secret", "-access_secret",
                            type=str, required=True, help="Aliyun ak secret")
        parser.add_argument("--dry_run", "-dry_run", type=bool, choices=[True, False], default=False,
                            help="是否只预检此次请求，默认false。true：发送检查请求，不会创建实例，也不会产生费用；false：发送正常请求，通过检查后直接创建实例，并直接产生费用")
        parser.add_argument("--region_id", "-region_id",
                            type=str, default="cn-beijing", help="实例所属的地域ID，默认cn-beijing")
        parser.add_argument("--instance_type", "-instance_type",
                            type=str, default="ecs.n4.xlarge", help="实例的资源规格，默认ecs.n4.xlarge")
        parser.add_argument("--instance_charge_type",
                            "-instance_charge_type", type=str, default="PostPaid", help="实例的计费方式，默认按量付费")
        parser.add_argument("--image_id", "-image_id", type=str,
                            default="centos_7_04_64_20G_alibase_201701015.vhd", help="镜像ID，默认Centos7.4_x64")
        parser.add_argument("--security_group_id", "-security_group_id",
                            type=str, required=True, help="指定新创建实例所属于的安全组ID，必须设置")
        parser.add_argument("--period", "-period", type=int,
                            default=1, help="购买资源的时长,当参数InstanceChargeType取值为PrePaid(包年包月)时才生效且为必选值, 默认为1")
        parser.add_argument("--period_unit", "-period_unit",
                            type=str, default="Hourly", help="购买资源的时长单位, 默认为Hourly")
        parser.add_argument("--zone_id", "-zone_id",
                            type=str, default="cn-beijing-a", help="实例所属的可用区编号，默认为cn-beijing-a")
        parser.add_argument("--internet_charge_type",
                            "-internet_charge_type", type=str, default="PayByTraffic", help="网络计费类型，默认为PayByTraffic(按使用流量计费)")
        parser.add_argument("--vswitch_id", "-vswitch_id",
                            type=str, help="虚拟交换机ID。如果您创建的是VPC类型ECS实例，需要指定虚拟交换机ID")
        parser.add_argument("--instance_name", "-instance_name", type=str,
                            default="test-[1,2]", help="实例名称, 创建多台ECS实例时，您可以使用UniqueSuffix为这些实例设置不同的实例名称。您也可以使用name_prefix[begin_number,bits]name_suffix的命名格式设置有序的实例名称，例如，设置InstanceName取值为test-[1,4]-alibabacloud，则第一台ECS实例的实例名称为test-0001-alibabacloud")
        parser.add_argument("--password", "-password", type=str,
                            default="Test123$%#", help="实例的密码，长度为8至30个字符，必须同时包含大小写英文字母、数字和特殊符号中的三类字符，默认密码请查看程序 --password参数")
        parser.add_argument("--amount", "-amount", type=int,
                            default=1, help="指定创建ECS实例的数量。取值范围：1~100，默认为1")
        parser.add_argument("--internet_max_bandwidth_out", "-internet_max_bandwidth_out",
                            type=int, default=0, help="公网出口带宽最大值，单位为Mbit/s。取值范围：0~100，默认值0")
        parser.add_argument("--unique_suffix", "-unique_suffix",
                            type=bool, choices=[True, False], default=True, help="是否为HostName和InstanceName添加有序后缀，有序后缀从001开始递增，最大不能超过999。例如，LocalHost001，LocalHost002和MyInstance001，MyInstance002。默认值：true")
        parser.add_argument("--io_optimized", "-io_optimized",
                            type=str, default="optimized", help="是否为I/O优化实例，默认为optimized：I/O优化")
        parser.add_argument("--security_enhancement_strategy",
                            "-security_enhancement_strategy", type=str, default="Active", help="是否开启安全加固，默认值为 Active：启用安全加固，只对公共镜像生效")
        parser.add_argument("--auto_release_time", "-auto_release_time", type=str,
                            help="自动释放时间。按照ISO8601标准表示，使用UTC +0时间。格式为：yyyy-MM-ddTHH:mm:ssZ，最短释放时间为当前时间半小时之后，最长释放时间不能超过当前时间三年")
        parser.add_argument("--system_disk_size", "-system_disk_size", type=int, default=40, help="系统盘大小，默认为40G")
        parser.add_argument("--system_disk_category", "-system_disk_category", type=str,
                            default="cloud_efficiency", help="系统盘的磁盘种类，默认为cloud_efficiency（高效云盘）")
        parser.add_argument("--data_disks", "-data_disks", type=str,
                            default="[{'Size': 100, 'Category': 'cloud_efficiency', 'Encrypted': 'false', 'DeleteWithInstance': True}]", help="数据盘，默认100G，类型是str")
        parser.add_argument("--tags", "-tags", type=str,
                            default="[{'Key': 'business-types', 'Value': 'test'}]", help="实例标签，类型是str，默认值business-types: test")
        args_options = parser.parse_args()
        params_dict = vars(args_options)
        return params_dict

    def run(self):
        try:
            ids = self.run_instances()
            return self._check_instances_status(ids)
        except ClientException as e:
            print('Fail. Something with your connection with Aliyun go incorrect.'
                  ' Code: {code}, Message: {msg}'
                  .format(code=e.error_code, msg=e.message))
        except ServerException as e:
            print('Fail. Business error.'
                  ' Code: {code}, Message: {msg}'
                  .format(code=e.error_code, msg=e.message))
        except Exception:
            print('Unhandled error')
            print(traceback.format_exc())

    def run_instances(self):
        """
        调用创建实例的API，得到实例ID后继续查询实例状态
        :return:instance_ids 需要检查的实例ID
        """
        request = RunInstancesRequest()

        # true：发送检查请求，不会创建实例。检查项包括是否填写了必需参数、请求格式、业务限制和ECS库存。如果检查不通过，则返回对应错误。如果检查通过，则返回错误码DryRunOperation
        # false（默认）：发送正常请求，通过检查后直接创建实例。
        request.set_DryRun(self.dry_run)

        request.set_InstanceType(self.instance_type)
        request.set_InstanceChargeType(self.instance_charge_type)
        request.set_ImageId(self.image_id)
        request.set_SecurityGroupId(self.security_group_id)
        request.set_Period(self.period)
        request.set_PeriodUnit(self.period_unit)
        request.set_ZoneId(self.zone_id)
        request.set_InternetChargeType(self.internet_charge_type)
        request.set_VSwitchId(self.vswitch_id)
        request.set_InstanceName(self.instance_name)
        request.set_Password(self.password)
        request.set_Amount(self.amount)
        request.set_InternetMaxBandwidthOut(self.internet_max_bandwidth_out)
        request.set_UniqueSuffix(self.unique_suffix)
        request.set_IoOptimized(self.io_optimized)
        request.set_SecurityEnhancementStrategy(
            self.security_enhancement_strategy)
        if self.auto_release_time:
            request.set_AutoReleaseTime(self.auto_release_time)
        request.set_SystemDiskSize(self.system_disk_size)
        request.set_SystemDiskCategory(self.system_disk_category)
        request.set_DataDisks(self.data_disks)
        request.set_Tags(self.tags)

        body = self.client.do_action_with_exception(request)
        data = json.loads(body)
        instance_ids = data['InstanceIdSets']['InstanceIdSet']
        print('Success. Instance creation succeed. InstanceIds: {}'.format(', '.join(instance_ids)))

        # instance_ids 输出为一个list
        return instance_ids

    def _check_instances_status(self, instance_ids):
        """
        每3秒中检查一次实例的状态，超时时间设为3分钟.
        :param instance_ids 需要检查的实例ID
        :return:
        """
        start = time.time()
        host_info_list = []
        while True:
            request = DescribeInstancesRequest()
            request.set_InstanceIds(json.dumps(instance_ids))
            body = self.client.do_action_with_exception(request)
            data = json.loads(body)
            for instance in data['Instances']['Instance']:
                if RUNNING_STATUS in instance['Status']:
                    instance_ids.remove(instance['InstanceId'])
                    print('Instance boot successfully: {}'.format(
                        instance['InstanceId']))
                    host_info_list.append({"host": instance['VpcAttributes']['PrivateIpAddress']['IpAddress'][0],
                        "password": self.password, "hostname": instance['InstanceName']})

            if not instance_ids:
                print('Instances all boot successfully')
                break

            if time.time() - start > CHECK_TIMEOUT:
                print('Instances boot failed within {timeout}s: {ids}'
                      .format(timeout=CHECK_TIMEOUT, ids=', '.join(instance_ids)))
                break

            time.sleep(CHECK_INTERVAL)
        # 输出主机连接信息
        return host_info_list


class SshConnect(object):
    def __init__(self, host, password, hostname, username="root", port=int(22), timeout=int(10)):
        self.host = host
        self.password = password
        self.username = username
        self.hostname = hostname
        self.port = int(port)
        self.timeout = int(timeout)
        # shell初始化脚本或者命令
        self.cmd = "echo Hello World && hostname %s && hostname" % hostname

    def log_tail(self, transport):
        channel = transport.open_session()
        channel.get_pty()
        # 将命令传入管道中
        channel.exec_command(self.cmd)
        while True:
            # 判断退出的准备状态
            if channel.exit_status_ready():
                break
            try:
                # 通过socket进行读取日志
                rl, wl, el = select.select([channel], [], [])
                if len(rl) > 0:
                    recv = channel.recv(1024)
                    # 此处将获取的数据解码转换成utf8
                    print(recv.decode('utf8', 'ignore').strip("\n"))
            # 键盘终端异常
            except KeyboardInterrupt:
                print("Caught control-C")
                channel.send("\x03")  # 发送 ctrl+c
                channel.close()

    def connect(self):
        # 远程连接新创建ECS，并运行shell命令或者脚本
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            ssh.connect(self.host, username=self.username, password=self.password,
                        port=self.port, timeout=self.timeout, allow_agent=True)
            # 开启channel 管道
            transport = ssh.get_transport()
            self.log_tail(transport)
            ssh.close()
            print('\033[1;32;40m' + '*' * 50)
            print("{} machine initialization successful".format(self.host))
            print('*' * 50 + '\033[0m')
        except ssh_exception.NoValidConnectionsError:
            print(
                "ssh_exception.NoValidConnectionsError错误。%s 实例还没有完全启动好，等待1分钟再次尝试" % self.host)
            time.sleep(60)
            ssh.connect(self.host, username=self.username, password=self.password,
                        port=self.port, timeout=self.timeout, allow_agent=True)
            # 开启channel 管道
            transport = ssh.get_transport()
            self.log_tail(transport)
            ssh.close()
            print('\033[1;32;40m' + '*' * 50)
            print("{} machine initialization successful".format(self.host))
            print('*' * 50 + '\033[0m')
        except socket.timeout:
            print("socket.timeout错误。%s 实例还没有完全启动好，等待1分钟再次尝试" % self.host)
            time.sleep(60)
            ssh.connect(self.host, username=self.username, password=self.password,
                        port=self.port, timeout=self.timeout, allow_agent=True)
            # 开启channel 管道
            transport = ssh.get_transport()
            self.log_tail(transport)
            ssh.close()
            print('\033[1;32;40m' + '*' * 50)
            print("{} machine initialization successful".format(self.host))
            print('*' * 50 + '\033[0m')
        except:
            print('\033[1;31;40m' + '*' * 50)
            print("{} machine initialization failed".format(self.host))
            print('*' * 50 + '\033[0m')
            ssh.close()


if __name__ == '__main__':
    for host_info in AliyunRunInstancesExample().run():
        ssh = SshConnect(host_info['host'], host_info['password'], host_info['hostname'])
        ssh.connect()
