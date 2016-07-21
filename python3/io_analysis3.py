#!/usr/bin/python3
#-*- coding:utf-8 -*-

"""
python io_analysis3.py 4 5 3 ，第一个数位每次收集读写数据的间隔秒数，第二个数是打印出读写最多的n个进程，第三个为运行脚本的次数
如果不接参数，默认是等待5秒，打印前6个进程，脚本运行一次
"""

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

def main(_list_num):
    _sort_read_dict = {}
    _sort_write_dict = {}
    # 获取系统读写数据
    process_info_list_frist = collect_info()
    # 将读数据和写数据进行分组，写入两个字典中
    for loop in process_info_list_frist.keys():
        frist_read_v = process_info_list_frist[loop]["read_bytes"]  # out 100
        frist_write_v = process_info_list_frist[loop]["write_bytes"]  # out 200
        # 生成字典
        _sort_read_dict[loop] = frist_read_v  # 赋值{10:读值, 20:读值}
        _sort_write_dict[loop] = frist_write_v  # 赋值{10:写值, 20:写值}
    # 将读写数据进行排序
    sort_read_dict = sorted(_sort_read_dict.items(), key=lambda x: x[1], reverse=True)  # out [(20, 读值), (10, 读值)]
    sort_write_dict = sorted(_sort_write_dict.items(), key=lambda y: y[1], reverse=True)  # out [(20, 写值), (10, 写值)]
    # 打印统计结果
    system_time = time.strftime('%F %T')
    print(system_time)
    X = PrettyTable(["r-pid", "r-process", "read(bytes)", "w-pid", "w-process", "write(btyes)"]) #列表名不能有重复
    X.align["r-pid"] = "l"# Left align r-pid
    X.padding_width = 1# One space between column edges and contents (default)
    for _num in range(_list_num):
        res  = []
        read_pid = sort_read_dict[_num][0]
        write_pid = sort_write_dict[_num][0]
        res.append("%s" % read_pid)
        res.append(process_info_list_frist[read_pid]["name"])
        res.append("%s" % sort_read_dict[_num][1])
        res.append(write_pid)
        res.append(process_info_list_frist[write_pid]["name"])
        res.append("%s" % sort_write_dict[_num][1])
        X.add_row(res)
    print(X)
    print("\n" * 1)

if __name__ == '__main__':
    try:
        _sleep_time = sys.argv[1]
    except:
        _sleep_time = 5
    try:
        _num = sys.argv[2]
    except:
        _num = 6
    try:
        loop = sys.argv[3]
    except:
        loop = 1
    if int(loop) == 1:
        for i in range(int(loop)):
            main(int(_num))
    else:
        for i in range(int(loop)):
            loop1 = int(loop) - 1
            if i == int(loop1):
                main(int(_num))
            else:
                main(int(_num))
                time.sleep(int(_sleep_time))