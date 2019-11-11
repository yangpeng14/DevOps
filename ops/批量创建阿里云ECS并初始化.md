## 程序简介
一个能`批量创建阿里云ECS`并能够`自动初始化ECS`

## 程序功能
- 通过阿里云提供的`SDK aliyun-python-sdk-ecs`调用`阿里云API`批量创建`ECS`
- 能对创建成功后的`ECS检查是否启动`
- 能自动`登陆ECS并初始化`(初始化ECS程序这里不提供)
- 目前只支持创建阿里云VPC网络

## 程序环境要求
- Python 3.5+
- Python aliyun-python-sdk-ecs sdk 版本大于 4.4.3
- 安装 paramiko 模块 （是一个基于SSH用于连接远程服务器并执行相关操作（SSHClient和SFTPClinet,即一个是远程连接，一个是上传下载服务），使用该模块可以对远程服务器进行命令或文件操作，值得一说的是，fabric和ansible内部的远程管理就是使用的paramiko来现实）

## 程序主要参数解释
参数 | 解释
---|--
access_id、access_secret | 阿里云AK凭证，必填
dry_run | 是否只预检此次请求，默认false
region_id | ECS实例所属的地域ID
instance_type | ECS实例的资源规格，默认ecs.n4.xlarge
instance_charge_type | 默认按量付费
image_id | 镜像ID，默认Centos7.4_x64
security_group_id | 指定新创建实例所属于的安全组ID，必填
zone_id  | 实例所属的可用区编号，默认为cn-beijing-a
vswitch_id | 虚拟交换机ID。如果您创建的是VPC类型ECS实例，需要指定虚拟交换机ID
instance_name | 实例名称
password | 默认密码 Test123$%#
amount | 创建ECS实例的数量。取值范围：1~100，默认为1
internet_max_bandwidth_out | 公网出口带宽最大值，单位为Mbit/s。取值范围：0~100，默认值0
system_disk_size | 系统盘大小，默认为40G
system_disk_category | 系统盘的磁盘种类，默认为cloud_efficiency（高效云盘）
data_disks | 数据盘，默认100G
tags | 实例标签，类型是str，默认值business-types: test，可选

## 程序运行样例
- 批量创建`2个ECS实例`、密码设置为`Test123$%#`、实例名称为`test-1 test-2`、两个数据盘大小分别为`高效云盘100G 高效云盘200G`、实例标签`business-types: test`、按量计费、`ecs.n4.xlarge`规格、镜像为`Centos7.4_x64`、公网带宽为`0 Mbit/s`

    `aliyun_batch_create_ecs.py --access_id="***" --access_secret="***" --amount 2 --security_group_id="安全组ID" --vswitch_id="交换机ID" --instance_name="test-[1,2]" --password="Test123$%#" --data_disks="[{'Size': 100, 'Category': 'cloud_efficiency', 'Encrypted': 'false', 'DeleteWithInstance': True}, {'Size': 200, 'Category': 'cloud_efficiency', 'Encrypted': 'false', 'DeleteWithInstance': True}]" --tags="[{'Key': 'business-types', 'Value': 'test'}]"`

## 下面是 deploaliyun_batch_create_ecs.py 部分代码，获取程序全部代码，请关注我的 `YP小站` 公众号并回复 `阿里云批量创建ECS`
```python
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
```

## 参考链接
- `创建RAM用户会生成AK信息` https://help.aliyun.com/document_detail/121941.html?spm=a2c4g.11186623.6.554.5806582fZklIzZ
- `阿里云批量创建ECS SDK` https://help.aliyun.com/document_detail/93105.html?spm=a2c4g.11186623.6.1321.41c6d660oMk5ZN
- `阿里云 RunInstances 批量创建ECS参数解释` https://help.aliyun.com/document_detail/63440.html?spm=a2c4g.11186623.6.1114.1daa431dNQL6v2
- `阿里云 DescribeInstanceStatus 检查ECS是否启动` https://help.aliyun.com/document_detail/25505.html?spm=a2c4g.11186623.2.16.127a6da7Bgz4eb&aly_as=G9Cy1Uf#DescribeInstanceStatus