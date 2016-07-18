#!/usr/bin/python3
#-*- coding:utf-8 -*-

#使用方法: python3 qip3.py www.jd.com www.baidu.com or python3 qip3.py 8.8.8.8 114.114.114.114

import requests
import socket
import sys
import re
from lxml import etree

def Analysis(domain):
    while True:
        try:
            results = socket.getaddrinfo(domain, None)
            ipaddrs = (x[4][0] for x in results)
            ipaddrs1 = list(set(list(ipaddrs)))
            return ipaddrs1
        except Exception:
            print(domain, '域名解析不出IP或IP不合法，请重新输入!')
            sys.exit()

def Ip_query(ipaddr):
    rs = requests.get("http://ip138.com/ips138.asp?ip={}&action=2".format(ipaddr), timeout=3)
    page = etree.HTML(rs.content)
    xpath = "//ul[@class='ul1']/li/text()"
    hanzi_list = page.xpath(xpath)
    print('Analysis IP: ', ipaddr)
    for hanzi in hanzi_list:
        print(hanzi)
    return '-------------------------Done----------------------'


if __name__ == '__main__':
    for parameter in range(1, len(sys.argv)):
            if re.match(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', sys.argv[parameter]):
                print(Ip_query(sys.argv[parameter]))
            else:
                for domain1 in Analysis(sys.argv[parameter]):
                    print('Domain name resolution: ', sys.argv[parameter])
                    print(Ip_query(domain1))
