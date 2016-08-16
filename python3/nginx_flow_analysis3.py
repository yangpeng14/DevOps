#!/usr/bin/python3
#-*-coding=utf-8-*-

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
            for line in f.readlines():
                try:
                    list_line = line.split()
                    timeArray = time.strptime(list_line[3].strip('['), "%d/%b/%Y:%H:%M:%S")
                    timeStamp_start = int(time.mktime(timeArray))
                    list_line1 = [timeStamp_start, list_line[9]]
                    #生成字典
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

class Main():
    #主调函数
    def main(self):
        parser = argparse.ArgumentParser(
            description="Nginx flow analysis, Supported file types ascii text.")
        parser.add_argument('-f', '--file',
                            dest='file',
                            nargs='?',
                            help="log file input.")
        parser.add_argument('-m', '--minute',
                            dest='minute',
                            default=5,
                            nargs='?',
                            type=int,
                            help="Nginx separation time,Default 5 min.")
        args = parser.parse_args()

        Input_sorted_log = input_logfile_sort()
        display_format1 = displayFormat()
        times = args.minute * 60
        for type in os.popen("""file {}""".format(args.file)):
            file_type = type.strip().split()[1]
        if file_type.lower() == 'ascii':
            logascii_analysis = log_partition()
            logascii_analysis.log_pr(Input_sorted_log.logascii_sortetd(args.file), times)
            print('\033[1;32;40m')
            display_format1.execut_time()
            print('\033[0m')
        else:
            print('\033[1;32;40m')
            print("Supported file types ascii text.")
            print("Example: python3 {} -f nginxlogfile -m time".format(sys.argv[0]))
            print('\033[0m')

if __name__ == '__main__':
    main_obj = Main()
    main_obj.main()