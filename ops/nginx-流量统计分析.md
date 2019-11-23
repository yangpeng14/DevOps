## 程序简介
- 通过分析`nginx日志`，统计出`nginx流量`（统计nginx日志中 $body_bytes_sent 字段），能自定义`时间间隔`，默认时间间隔为`5分钟`，单位为`分钟`。

## 输出结果
开始时间 | 结束时间 | 分割线 | 统计流量
--|--|--|--
2019-11-23 03:26:00 | 2019-11-23 04:26:00 | <=========> | 2.04M
2019-11-23 04:27:43 | 2019-11-23 05:27:43 | <=========> | 895.05K
2019-11-23 05:28:25 | 2019-11-23 06:28:25 | <=========> | 1.88M
2019-11-23 06:33:08 | 2019-11-23 07:33:08 | <=========> | 1.29M
2019-11-23 07:37:28 | 2019-11-23 08:37:28 | <=========> | 1.16M

## 环境
- python3+
- 需要安装`python argparse`
- 目前只支持`nginx 日志`

## 程序要求
- nginx日志格式要求，第四个字段为 `[$time_local]` 和 第7个字段为 `$body_bytes_sent` 或者 `$bytes_sent`
```
log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                  '$status $body_bytes_sent $request_time "$http_referer" '
                  '$host DIRECT/$upstream_addr $upstream_http_content_type '
                  '"$http_user_agent" "$http_x_forwarded_for"';
```
- `body_bytes_sent`：发送给客户端的字节数,不包括响应头的大小
- `bytes_sent`：发送给客户端的字节数
- 注意：nginx日志中间不能有空行，否则程序读取不到空行后面的日志

## 例子
```bash
# 分析 nginx access.log 日志，以 1小时 切割，统计每小时产生的流量
$ ./nginx_large_file_flow_analysis3.py -f /var/log/nginx/access.log -m 60
```

## 程序代码
下面是 nginx_large_file_flow_analysis3.py 部分代码，获取程序全部代码，请关注我的 `YP小站` 微信公众号并回复 `nginx流量统计`

```python
#!/usr/bin/python3
#-*-coding=utf-8-*-

#-----------------------------------------------------------------------------
# 注意：日志中间不能有空行，否则程序读取不到空行后面的日志
#-----------------------------------------------------------------------------

import time
import os
import sys
import argparse

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

    def execut_time(self):
        # 输出脚本执行的时间
        print('\n')
        print("Script Execution Time: %.3f second" % time.clock())

class input_logfile_sort():
    # 内存优化
    __slots__ = ['read_logascii_dict', 'key']

    def __init__(self):
        self.read_logascii_dict = {}
        self.key = 1

    def logascii_sortetd(self, logfile):
        with open(logfile, 'r') as f:
            while 1:
                    list_line = f.readline().split()
                    try:
                        if not list_line:
                            break
                        timeArray = time.strptime(list_line[3].strip('['), "%d/%b/%Y:%H:%M:%S")
                        timeStamp_start = int(time.mktime(timeArray))
                        list_line1 = [timeStamp_start, list_line[9]]
                        # 生成字典
                        self.read_logascii_dict[self.key] = list_line1
                        self.key += 1
                    except ValueError:
                        continue
                    except IndexError:
                        continue
        sorted_list_ascii = sorted(self.read_logascii_dict.items(), key=lambda k: (k[1][0]))
        return sorted_list_ascii
        # out [(4, [1420686592, '1024321222']), (3, [1449544192, '10243211111'])]

class log_partition():
    display_format = displayFormat()
    def __init__(self):
        self.size1 = 0
        self.j = 0

    def time_format(self, time_stamps_start, time_stamps_end):
        time_start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_stamps_start))
        time_end = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_stamps_end))
        print(time_start + ' -- ' + time_end + ' ' * 6 + '<=========>' + ' ' * 6 + self.display_format.format_size(self.size1))

    def log_pr(self, stored_log, times):
        time_stamps_start = stored_log[0][1][0]
        time_stamps_end = time_stamps_start + times
        lines = len(stored_log)
        for line in stored_log:
            self.j += 1
            if int(line[1][0]) <= time_stamps_end:
                try:
                    self.size1 = self.size1 + int(line[1][1])
                    if self.j == lines:
                        self.time_format(time_stamps_start, time_stamps_end)
                except ValueError:
                    continue
            else:
                try:
                    self.time_format(time_stamps_start, time_stamps_end)
                    self.size1 = 0
                    self.size1 = self.size1 + int(line[1][1])
                    time_stamps_start = int(line[1][0])
                    time_stamps_end = time_stamps_start + times
                    if self.j == lines:
                        self.time_format(time_stamps_start, time_stamps_end)
                except ValueError:
                    continue
```