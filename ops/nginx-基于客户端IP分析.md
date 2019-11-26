## 程序功能
- 通过分析`nginx日志`，基于`客户端IP`统计出`流量`、`请求数`和`HTTP 状态码`

## 输出结果
![](https://www.yp14.cn/img/nginx-fruit.png)

## 环境
- python3+
- 需要安装`python prettytable`
- 目前只支持`nginx 日志`

## 程序要求
`Nginx日志格式要求：`

- 第一个字段为 `$remote_addr`
- 第六个字段为 `$status`
- 第7个字段为 `$body_bytes_sent` 或者 `$bytes_sent`

`字段解释：`

- `$remote_addr`：客户端的访问ip
- `body_bytes_sent`：发送给客户端的字节数,不包括响应头的大小
- `bytes_sent`：发送给客户端的字节数
- `$status`：http状态码

`下面是例子：`

```
log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                  '$status $body_bytes_sent $request_time "$http_referer" '
                  '$host DIRECT/$upstream_addr $upstream_http_content_type '
                  '"$http_user_agent" "$http_x_forwarded_for"';
```

## 运行方法

```bash
# 基于客户端ip请求数排序，打印全部输出
$ ./nginx_analysis_log3.py /var/log/nginx/access.log

# 基于客户端ip请求数排序，只打印前5行
$ ./nginx_analysis_log3.py /var/log/nginx/access.log 5
```

## 程序不足的地方

- `nginx日志过大`，导致程序中`字典过大`，就会占用服务器`大量内存`。

## 程序代码

下面是 nginx_analysis_log3.py 部分代码，获取程序全部代码，请关注我的 `YP小站` 微信公众号并回复 `nginx客户端IP分析`

```python
#!/usr/bin/python3
# -*-coding=utf-8-*-

# ------------------------------------------------------
# Name:         nginx 日志分析脚本
# Purpose:      此脚本只用来分析nginx的访问日志
# Employ:       python3 nginx_analysis_log3.py NginxLogFilePath or python3 nginx_analysis_log3.py NginxLogFilePath number
# ------------------------------------------------------

import time
import sys
from prettytable import PrettyTable

class displayFormat():
    def format_size(self, size):
        # 格式化流量单位
        KB = 1024  # KB -> B  B是字节
        MB = 1048576  # MB -> B
        GB = 1073741824  # GB -> B
        TB = 1099511627776  # TB -> B
        if size >= TB:
            size = str("%.2f" % (float(size / TB)) ) + 'T'
        elif size < KB:
            size = str(size) + 'B'
        elif size >= GB and size < TB:
            size = str("%.2f" % (float(size / GB))) + 'G'
        elif size >= MB and size < GB:
            size = str("%.2f" % (float(size / MB))) + 'M'
        else:
            size = str("%.2f" % (float(size / KB))) + 'K'
        return size

    def error_print(self):
        # 输出错误信息
        print
        print('Usage : ' + sys.argv[0] + ' NginxLogFilePath [Number]')
        print
        sys.exit(1)

    def execut_time(self):
        # 输出脚本执行的时间
        print
        print("Script Execution Time: %.3f second" % time.clock())
        print

class hostInfo():
    host_info = ['200', '301', '302', '304', '307', '400', '401', '403', '404', '499', '500', '502', '503', '504', '206', '204', '202', '201', '101', '429', '415', '410', '408', 'times', 'size']
    def __init__(self, host):
        self.host = host = {}.fromkeys(self.host_info, 0)
        # out {'500': 0, '502': 0, '302': 0, '304': 0, '301': 0, 'times': 0, '200': 0, '404': 0, '401': 0, '403': 0, 'size': 0, '503': 0, '409': 0}

    def increment(self, status_times_size, is_size):
       # 该方法是用来给host_info中的各个值加1
        if status_times_size == 'times':
            self.host['times'] += 1
        elif is_size:
            self.host['size'] = self.host['size'] + status_times_size
        else:
            self.host[status_times_size] += 1
        # print(self.host) # out
        # ip: 1.1.1.1
        # {'200': 0, '302': 0, '304': 0, 'times': 1, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 0}
        # {'200': 1, '302': 0, '304': 0, 'times': 1, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 0}
        # {'200': 1, '302': 0, '304': 0, 'times': 1, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 27882}
        # ip: 2.2.2.2
        # {'200': 0, '302': 0, '304': 0, 'times': 1, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 0}
        # {'200': 1, '302': 0, '304': 0, 'times': 1, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 0}
        # {'200': 1, '302': 0, '304': 0, 'times': 1, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 27882}

    def get_value(self, value):
        # 该方法是取到各个主机信息中对应的值
        return self.host[value]


class analysis_log():
    # 内存优化
    __slots__ = ['report_dict', 'total_size_sent', 'total_request_times', 'total_200', 'total_301', \
        'total_302', 'total_304', 'total_307', 'total_400', 'total_401', 'total_403', 'total_404', 'total_499', \
        'total_500', 'total_502', 'total_503', 'total_504', 'total_206', 'total_204', 'total_202', 'total_201', 'total_101', 'total_429', 'total_415', 'total_410', 'total_408']

    def __init__(self):
        # 初始化一个空字典
        self.report_dict = {}
        self.total_size_sent, self.total_request_times, self.total_200, self.total_301, \
        self.total_302, self.total_304, self.total_307, self.total_400, self.total_401, self.total_403, \
        self.total_404, self.total_499, self.total_500, self.total_502, self.total_503, \
        self.total_504, self.total_206, self.total_204, self.total_202, self.total_201, \
        self.total_101, self.total_429, self.total_415, self.total_410, \
        self.total_408 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    def split_eachline_todict(self, line):
        # 分割文件中的每一行，并返回一个字典
        split_line = line.split()
        split_dict = {'remote_host': split_line[0], 'status': split_line[8], 'bytes_sent': split_line[9]}
        return split_dict

    def generate_log_report(self, logfile):
        # 读取文件，分析split_eachline_todict方法生成的字典
        with open(logfile, 'r') as infile:
            for line in infile.readlines():
                try:
                    line_dict = self.split_eachline_todict(line)
                    host = line_dict['remote_host']
                    status = line_dict['status']
                except ValueError:
                    continue
                except IndexError:
                    continue

                if host not in self.report_dict:
                    host_info_obj = hostInfo(host)
                    # out {'500': 0, '502': 0, '302': 0, '304': 0, '301': 0, 'times': 0, '200': 0, '404': 0, '401': 0, '403': 0, 'size': 0, '503': 0, '409': 0}
                    self.report_dict[host] = host_info_obj  #以host_info_obj方法做为value值
                    # out {'1.1.1.1': {'500': 0, '502': 0, '302': 0, '304': 0, '301': 0, 'times': 0, '200': 0, '404': 0, '401': 0, '403': 0, 'size': 0, '503': 0, '409': 0}}
                else:
                    host_info_obj = self.report_dict[host]
                    # out <__main__.hostInfo object at 0x7fc0aa7ff510> 各值加1后的host_info_obj方法
                    # out {'500': 0, '502': 0, '302': 0, '304': 0, '301': 0, 'times': 1, '200': 1, '404': 0, '401': 0, '403': 0, 'size': 1024, '503': 0, '409': 0}
                host_info_obj.increment('times', False)  # 出现的请求次数加1
                if status in host_info_obj.host_info:
                    host_info_obj.increment(status, False)  # 出现的状态码次数加1
                try:
                    bytes_sent = int(line_dict['bytes_sent'])
                except ValueError:
                    bytes_sent = 0
                host_info_obj.increment(bytes_sent, True)  # 发送字节相加
        return self.report_dict
        # out {'1.1.1.1': <__main__.hostInfo object at 0x7ffd3d1cd550>, '2.2.2.2': <__main__.hostInfo object at 0x7ffd3d1cd510>}

    def return_sorted_list(self, true_dict):
        # 输出方法ost_info_obj
        # 计算各个状态次数、流量总量，请求的总次数，并且计算各个状态的总量 并生成一个正真的字典，方便排序
        for host_key in true_dict:
            host_value = true_dict[host_key]
            times = host_value.get_value('times')
            self.total_request_times = self.total_request_times + times
            size = host_value.get_value('size')
            self.total_size_sent = self.total_size_sent + size

            o200 = host_value.get_value('200')
            o301 = host_value.get_value('301')
            o302 = host_value.get_value('302')
            o304 = host_value.get_value('304')
            o307 = host_value.get_value('307')
            o400 = host_value.get_value('400')
            o401 = host_value.get_value('401')
            o403 = host_value.get_value('403')
            o404 = host_value.get_value('404')
            o499 = host_value.get_value('499')
            o500 = host_value.get_value('500')
            o502 = host_value.get_value('502')
            o503 = host_value.get_value('503')
            o504 = host_value.get_value('504')
            o206 = host_value.get_value('206')
            o204 = host_value.get_value('204')
            o202 = host_value.get_value('202')
            o201 = host_value.get_value('201')
            o101 = host_value.get_value('101')
            o429 = host_value.get_value('429')
            o415 = host_value.get_value('415')
            o410 = host_value.get_value('410')
            o408 = host_value.get_value('408')

            # 字典中如果出现重复的key值，那会以最后传入的key值为准
            true_dict[host_key] = {'200': o200, '301': o301, '302': o302, '304': o304, '307': o307, '400': o400, '401': o401, '403': o403, \
                                   '404': o404, '499': o499, '500': o500, '502': o502, '503': o503, '504': o504, \
                                   '206': o206, '204': o204, '202': o202, '201': o201, '101': o101, '429': o429, \
                                   '415': o415, '410': o410, '408': o408, \
                                   'total_request_times': times, 'total_size_sent': size}

            self.total_200 = self.total_200 + o200
            self.total_301 = self.total_301 + o301
            self.total_302 = self.total_302 + o302
            self.total_304 = self.total_304 + o304
            self.total_307 = self.total_307 + o307
            self.total_400 = self.total_400 + o400
            self.total_401 = self.total_401 + o401
            self.total_403 = self.total_403 + o403
            self.total_404 = self.total_404 + o404
            self.total_499 = self.total_499 + o499
            self.total_500 = self.total_500 + o500
            self.total_502 = self.total_502 + o502
            self.total_503 = self.total_503 + o503
            self.total_504 = self.total_504 + o504
            self.total_206 = self.total_206 + o206
            self.total_204 = self.total_204 + o204
            self.total_202 = self.total_202 + o202
            self.total_201 = self.total_201 + o201
            self.total_101 = self.total_101 + o101
            self.total_429 = self.total_429 + o429
            self.total_415 = self.total_415 + o415
            self.total_410 = self.total_410 + o410
            self.total_408 = self.total_408 + o408

        sorted_list = sorted(true_dict.items(), key=lambda k: (k[1]['total_request_times'], k[1]['total_size_sent']), reverse=True)
        return sorted_list
```