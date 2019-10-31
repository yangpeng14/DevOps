#!/usr/bin/env python3
# coding=utf-8

import argparse
import sys
import os
import time
import re


class Main(object):
    def __init__(self):
        params_dict = self.parse_args()
        self.command = params_dict["command"]
        self.domain_list = params_dict["domain"].split(",")
        self.challenge_alias = params_dict["challenge_alias"]
        self.dns = params_dict["dns"]
        self.key_name = params_dict["key_name"]
        self.secret_name = params_dict["secret_name"]
        self.key = params_dict["key"]
        self.secret = params_dict["secret"]

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description='颁发Let’s Encrypt证书，程序只支持DNS别名颁发证书 例子: letsencrypt-dns-alias.py --command="--issue" --challenge-alias="alias domain" --dns="dns_ali" --key-name="Ali_Key" --secret-name="Ali_Secret" --key="***" --secret="***" --domain="*.a.com,*.b.com"'
        )
        parser.add_argument(
            "--command",
            "-command",
            type=str,
            required=True,
            default="--issue",
            help="输入 acme.sh 脚本参数，除--domain、-d、--domain-alias、--challenge-alias、--dns、--log-level、--log 外，其它参数都可以输入。默认为 --issue"
        )
        parser.add_argument("--domain",
                            "-domain",
                            type=str,
                            required=True,
                            help="颁发证书域名，例如：*.a.com,*.b.com")
        parser.add_argument(
            "--challenge-alias",
            "-challenge-alias",
            type=str,
            required=True,
            help="The challenge domain alias for DNS alias mode: https://github.com/Neilpang/acme.sh/wiki/DNS-alias-mode"
        )
        parser.add_argument("--dns",
                            "-dns",
                            type=str,
                            required=True,
                            default="dns_ali",
                            help="[dns_cf|dns_dp|dns_cx|dns_ali]等 默认阿里云api")
        parser.add_argument("--key-name",
                            "-key-name",
                            type=str,
                            default="Ali_Key",
                            help="DNS厂商 Api Key 名称，默认为 Ali_Key")
        parser.add_argument("--secret-name",
                            "-secret-name",
                            type=str,
                            default="Ali_Secret",
                            help="DNS厂商 Api Secret 名称，默认为 Ali_Secret")
        parser.add_argument("--key",
                            "-key",
                            type=str,
                            default="",
                            help="DNS厂商 Api Key，默认为空")
        parser.add_argument("--secret",
                            "-secret",
                            type=str,
                            default="",
                            help="DNS厂商 Api Secret，默认为空")
        args_options = parser.parse_args()
        params_dict = vars(args_options)
        return params_dict

    def check_command(self):
        excludingParameter = "--domain -d --domain-alias --challenge-alias --dns --log-level --log"
        for opt in self.command.split():
            if opt in excludingParameter:
                print("\033[31;31m")
                print("-command 选项不能传入这些参数 %s" % excludingParameter)
                print("\033[0m \n")
                sys.exit(1)

    def check_error(self):
        with open("/root/.acme.sh/acme.sh.log", "r") as f:
            for line in f.readlines():
                # 忽略大小写匹配
                if re.findall("error", line.strip(), flags=re.IGNORECASE):
                    return True

    def issue(self):
        # 检查 -command 参数
        self.check_command()
        os.environ['command'] = str(self.command)
        os.environ['challenge_alias'] = str(self.challenge_alias)
        os.environ['dns'] = str(self.dns)
        verify_domain = []
        if self.key_name and self.secret_name and self.key and self.secret:
            os.environ['key_name'] = str(self.key_name)
            os.environ['secret_name'] = str(self.secret_name)
            os.environ['key'] = str(self.key)
            os.environ['secret'] = str(self.secret)
            # 每次取5个新域名去申请颁发证书，如果过多导致申请证书失败。叠加，验证通过的域名直接会跳过。
            for domainSplitList in range(0, len(self.domain_list), 5):
                number_retries = 1
                verify_domain.extend(self.domain_list[domainSplitList:domainSplitList + 5])
                verify_domain_str = ",".join(verify_domain)
                os.environ['verify_domain_str'] = str(verify_domain_str)
                while True:
                    if number_retries <= 3:
                        # 清空acme.sh脚本输出日志
                        os.system('echo > /root/.acme.sh/acme.sh.log')
                        # 传入DNS厂商 API key 并调用 acme.sh 申请证书
                        os.system('export $key_name=$key && export $secret_name=$secret && /root/.acme.sh/acme.sh $command --challenge-alias $challenge_alias --dns $dns --log-level 2 --log --domain $verify_domain_str')
                        if self.check_error():
                            print("\033[31;31m")
                            print("{} 申请证书失败 {}次，等待20秒再次重试。".format(verify_domain, number_retries))
                            print("\033[0m \n")
                            number_retries += 1
                            time.sleep(20)
                        else:
                            print("\033[32;32m")
                            print("{} 申请证书成功。".format(verify_domain))
                            print("\033[0m \n")
                            break
                    else:
                        print("\033[31;31m")
                        print("重试申请次数超过2次")
                        print("\033[0m \n")
                        sys.exit(1)
        else:
            for domainSplitList in range(0, len(self.domain_list), 5):
                number_retries = 1
                verify_domain.extend(self.domain_list[domainSplitList:domainSplitList + 5])
                verify_domain_str = ",".join(verify_domain)
                os.environ['verify_domain_str'] = str(verify_domain_str)
                while True:
                    if number_retries <= 3:
                        # 清空acme.sh脚本输出日志
                        os.system('echo > /root/.acme.sh/acme.sh.log')
                        # 配置文件中已记录DNS厂商 API key，调用 acme.sh 申请证书
                        os.system('/root/.acme.sh/acme.sh $command --challenge-alias $challenge_alias --dns $dns --log-level 2 --log --domain $verify_domain_str')
                        if self.check_error():
                            print("\033[31;31m")
                            print("{} 申请证书失败 {}次，等待20秒再次重试。".format(verify_domain, number_retries))
                            print("\033[0m \n")
                            number_retries += 1
                            time.sleep(20)
                        else:
                            print("\033[32;32m")
                            print("{} 申请证书成功。".format(verify_domain))
                            print("\033[0m \n")
                            break
                    else:
                        print("\033[31;31m")
                        print("重试申请次数超过2次")
                        print("\033[0m \n")
                        sys.exit(1)


if __name__ == "__main__":
    Issue = Main()
    Issue.issue()
