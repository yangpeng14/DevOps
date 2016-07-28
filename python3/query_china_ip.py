#!/usr/bin/python3
# -*-coding=utf-8-*-

import re
import requests
import math


def fetch_ip_data():
    print('\033[1;32;40m')
    print("Fetching data from apnic.net, it might take a few minutes, please wait...")
    print('\033[0m')
    rs = requests.get('http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest', timeout=60)
    page = rs.text
    cnregex = re.compile(r'apnic\|cn\|ipv4\|[0-9\.]+\|[0-9]+\|[0-9]+\|a.*',re.IGNORECASE)  # re.I(re.IGNORECASE): 忽略大小写
    cndata = cnregex.findall(page)

    # results = []
    with open('/tmp/cn_iplist.txt', 'w') as f:
        for item in cndata:  # out item = 'apnic|CN|ipv4|223.254.0.0|65536|20100723|allocated'
            unit_items = item.split('|')
            starting_ip = unit_items[3]  # out 223.254.0.0
            num_ip = int(unit_items[4])  # out 65536

            imask = 0xffffffff ^ (num_ip - 1)  # out 4294901760
            # convert to string
            imask = hex(imask)[2:]  # out ffff0000 #hex 把10进制数转换为16进制数
            mask = [0] * 4  # out [0, 0, 0, 0]
            mask[0] = imask[0:2]
            mask[1] = imask[2:4]
            mask[2] = imask[4:6]
            mask[3] = imask[6:8]  # out mask = ['ff', 'ff', '00', '00']

            # convert str to int
            mask = [int(i, 16) for i in mask]  # 把16进制转换为10进制 out [255, 255, 0, 0]
            mask = "%d.%d.%d.%d" % tuple(mask)  # out 255.255.0.0

            # mask in *nix format
            mask2 = 32 - int(math.log(num_ip, 2))  # out 16 返回num_ip的以2为底的对数

            # results.append((starting_ip, mask, mask2))  # out [('223.254.0.0', '255.255.0.0', 16), ('223.255.252.0', '255.255.254.0', 23)]
            results = '{} {} {}\n'.format(starting_ip, mask, mask2)
            f.write(results)
    print('\033[1;32;40m')
    print('The results are output to /tmp/cn_iplist.txt')
    print('\033[0m')
    return '--------Done----------'

if __name__ == '__main__':
    fetch_ip_data()