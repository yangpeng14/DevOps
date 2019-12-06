## 程序功能
分析Linux服务器 IO 进程，分别按 `读` 和 `写` 的进程排序，`默认显示前5行`。功能类似 Linux Shell `pidstat`命令。

## 程序输出结果

r-pid |  r-process  | read(bytes) | w-pid |     w-process     | write(btyes)
---|---|---|---|---|---
 6316  | (AliYunDun) |    57344    |  338  | (systemd-journal) |    536576 
 10105 |  (php5-fpm) |      0      |  879  |       (etcd)      |    233472 
 10111 |   (nginx)   |      0      |  266  |   (jbd2/vda1-8)   |    122880 
 933   |   (crond)   |      0      |  609  |     (rsyslogd)    |    81920  
 2     |  (kthreadd) |      0      |  2422 |     (php5-fpm)    |    61440  
 10114 |   (nginx)   |      0      |  2438 |     (php5-fpm)    |    61440  

 ## 程序环境
 - Python3+
 - 安装 Python prettytable 插件

 ## 运行示例
 ```bash
 # 如果不接参数，默认是等待5秒，打印前6个进程，脚本运行一次
$ io_difference_analysis3.py 4 5 3
 ```
- 第一个数位每次收集读写数据的间隔秒数
- 第二个数是打印出读写最多的n个进程
- 第三个为运行脚本的次数

## 程序部分代码
下面是程序部分代码，获取完整代码请关注微信公众号 `YP小站` ,并回复 `获取IO分析代码`

```python
#!/usr/bin/python3
#-*- coding:utf-8 -*-

import os
import re
import sys
import time
from prettytable import PrettyTable

####
sys_proc_path = '/proc/'
re_find_process_number = '^\d+$'

####
# 通过/proc/$pid/io获取读写信息
####

def collect_info():
    _tmp = {}
    re_find_process_dir = re.compile(re_find_process_number)
    for i in os.listdir(sys_proc_path):
        if re_find_process_dir.search(i):
            proc_num = re_find_process_dir.search(i).group()
            # 获得进程名
            try:
                with open("%s%s/stat" % (sys_proc_path, proc_num), "r") as process_name1:
                    process_name = process_name1.read().split(" ")[1]
                    # 读取io信息
                    with open("%s%s/io" % (sys_proc_path, proc_num), "r") as rw_io:
                        for _info in rw_io.readlines():
                            cut_info = _info.strip().split(':')
                            if cut_info[0].strip() == "read_bytes":
                                read_io = int(cut_info[1].strip())
                            if cut_info[0].strip() == "write_bytes":
                                write_io = int(cut_info[1].strip())
                                _tmp[proc_num] = {"name": process_name, "read_bytes": read_io, "write_bytes": write_io}
            except:pass
    return _tmp #返回结果 {10: {'write_bytes': '200', 'read_bytes': '100', 'name': '(httpd)'}, '1782': {'write_bytes': 8192, 'read_bytes': 76390400, 'name': '(gnome-session)'}}

def main(_sleep_time, _list_num):
    _sort_read_dict = {}
    _sort_write_dict = {}
    # 获取系统读写数据
    process_info_list_frist = collect_info()
    time.sleep(_sleep_time)
    process_info_list_second = collect_info()
    # 将读数据和写数据进行分组，写入两个字典中
    for loop in process_info_list_second.keys():
        second_read_v = process_info_list_second[loop]["read_bytes"]  # out 100
        second_write_v = process_info_list_second[loop]["write_bytes"]  # out 200
        try:
            frist_read_v = process_info_list_frist[loop]["read_bytes"]
        except:
            frist_read_v = 0
        try:
            frist_write_v = process_info_list_frist[loop]["write_bytes"]
        except:
            frist_write_v = 0
        # 计算第二次获得数据域第一次获得数据的差
        _sort_read_dict[loop] = second_read_v - frist_read_v  # 赋值{10:读差值, 20:读差值}
        _sort_write_dict[loop] = second_write_v - frist_write_v  # 赋值{10:写差值, 20:写差值}
    # 将读写数据进行排序
    sort_read_dict = sorted(_sort_read_dict.items(), key=lambda x: x[1], reverse=True)  # out [(20, 读差值), (10, 读差值)]
    sort_write_dict = sorted(_sort_write_dict.items(), key=lambda y: y[1], reverse=True)  # out [(20, 写差值), (10, 写差值)]
    # 打印统计结果
    system_time = time.strftime('%F %T')
    print(system_time)
    X = PrettyTable(["r-pid", "r-process", "read(bytes)", "w-pid", "w-process", "write(btyes)"]) #列表名不能有重复
    X.align["r-pid"] = "l"# Left align r-pid
    X.padding_width = 1# One space between column edges and contents (default)
```