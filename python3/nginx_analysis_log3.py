#!/usr/bin/python3
#-*-coding=utf-8-*-

# ------------------------------------------------------
# Name:         nginx 日志分析脚本
# Purpose:      此脚本只用来分析nginx的访问日志
# Employ:       python3 nginx_analysis_log3.py or python3 nginx_analysis_log3.py number
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
    host_info = ['200', '301', '302', '304', '400', '401', '403', '404', '499', '500', '502', '503', '504', 'times', 'size']
    def __init__(self, host):
        self.host = host = {}.fromkeys(self.host_info, 0)
        #out {'500': 0, '502': 0, '302': 0, '304': 0, '301': 0, 'times': 0, '200': 0, '404': 0, '401': 0, '403': 0, 'size': 0, '503': 0, '409': 0}

    def increment(self, status_times_size, is_size):
       # 该方法是用来给host_info中的各个值加1
        if status_times_size == 'times':
            self.host['times'] += 1
        elif is_size:
            self.host['size'] = self.host['size'] + status_times_size
        else:
            self.host[status_times_size] += 1
        #print(self.host) # out
        # ip: 1.1.1.1
        # {'200': 0, '302': 0, '304': 0, 'times': 1, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 0}
        # {'200': 1, '302': 0, '304': 0, 'times': 1, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 0}
        # {'200': 1, '302': 0, '304': 0, 'times': 1, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 27882}
        # ip: 1.1.1.1
        # {'200': 1, '302': 0, '304': 0, 'times': 2, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 27882}
        # {'200': 2, '302': 0, '304': 0, 'times': 2, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 27882}
        # {'200': 2, '302': 0, '304': 0, 'times': 2, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 30884}
        # ip: 2.2.2.2
        # {'200': 0, '302': 0, '304': 0, 'times': 1, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 0}
        # {'200': 1, '302': 0, '304': 0, 'times': 1, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 0}
        # {'200': 1, '302': 0, '304': 0, 'times': 1, '404': 0, '403': 0, '503': 0, '500': 0, 'size': 27882}

    def get_value(self, value):
        # 该方法是取到各个主机信息中对应的值
        return self.host[value]

class analysis_log():
    def __init__(self):
        #初始化一个空字典
        self.report_dict = {}
        self.total_size_sent, self.total_request_times, self.total_200, self.total_301, \
        self.total_302, self.total_304, self.total_400, self.total_401, self.total_403, \
        self.total_404, self.total_499, self.total_500, self.total_502, self.total_503, \
        self.total_504 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    def split_eachline_todict(self, line):
        #分割文件中的每一行，并返回一个字典
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
                    #out <__main__.hostInfo object at 0x7fc0aa7ff510>
                    # out {'500': 0, '502': 0, '302': 0, '304': 0, '301': 0, 'times': 0, '200': 0, '404': 0, '401': 0, '403': 0, 'size': 0, '503': 0, '409': 0}
                    self.report_dict[host] = host_info_obj  #以host_info_obj方法做为value值
                    #out {'1.1.1.1': <__main__.hostInfo object at 0x7fc0aa7ff510>}
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
        #out {'1.1.1.1': <__main__.hostInfo object at 0x7ffd3d1cd550>, '2.2.2.2': <__main__.hostInfo object at 0x7ffd3d1cd510>}

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
            o400 = host_value.get_value('400')
            o401 = host_value.get_value('401')
            o403 = host_value.get_value('403')
            o404 = host_value.get_value('404')
            o499 = host_value.get_value('499')
            o500 = host_value.get_value('500')
            o502 = host_value.get_value('502')
            o503 = host_value.get_value('503')
            o504 = host_value.get_value('504')

            #字典中如果出现重复的key值，那会以最后传入的key值为准
            true_dict[host_key] = {'200': o200, '301': o301, '302': o302, '304': o304, '400': o400, '401': o401, '403': o403, \
                                   '404': o404, '499': o499, '500': o500, '502': o502, '503': o503, '504': o504, \
                                   'total_request_times': times, 'total_size_sent': size}

            self.total_200 = self.total_200 + o200
            self.total_301 = self.total_301 + o301
            self.total_302 = self.total_302 + o302
            self.total_304 = self.total_304 + o304
            self.total_400 = self.total_400 + o400
            self.total_401 = self.total_401 + o401
            self.total_403 = self.total_403 + o403
            self.total_404 = self.total_404 + o404
            self.total_499 = self.total_499 + o499
            self.total_500 = self.total_500 + o500
            self.total_502 = self.total_502 + o502
            self.total_503 = self.total_503 + o503
            self.total_504 = self.total_504 + o504

        sorted_list = sorted(true_dict.items(), key= lambda k: (k[1]['total_request_times'], k[1]['total_size_sent']), reverse=True)
        return sorted_list

class Main():
    def main(self):
        #主调函数
        display_format = displayFormat()
        arg_length = len(sys.argv)
        if arg_length == 1:
            display_format.error_print()
        elif arg_length == 2 or arg_length == 3:
            infile_name = sys.argv[1]
            try:
                if arg_length == 3:
                    lines = int(sys.argv[2])
                else:
                    lines = 0
            except IOError as e:
                print
                print(e)
                display_format.error_print()
            except ValueError:
                print
                print("Please Enter A Volid Number !!")
                display_format.error_print()
        else:
            display_format.error_print()
        fileAnalysis_obj = analysis_log()
        not_true_dict = fileAnalysis_obj.generate_log_report(infile_name)
        # out {'1.1.1.1': <__main__.hostInfo object at 0x7ffd3d1cd550>, '2.2.2.2': <__main__.hostInfo object at 0x7ffd3d1cd510>}
        log_report = fileAnalysis_obj.return_sorted_list(not_true_dict)
        total_ip = len(log_report)
        if lines:
            log_report = log_report[0:lines]

        print('\n')
        total_size_sent = display_format.format_size(fileAnalysis_obj.total_size_sent)
        total_request_times = fileAnalysis_obj.total_request_times
        print('Total IP: %s   Total Send Size: %s   Total Request Times: %d' % (total_ip, total_size_sent, total_request_times))
        print('\n')

        X = PrettyTable(['IP', 'Send Size', 'Request Times', 'Request Times%', '200', '301', '302', '304', '400', '401', '403', \
                         '404', '499', '500', '502', '503', '504'])
        X.align["IP"] = "l"  # Left align IP
        X.padding_width = 1  # One space between column edges and contents (default)
        for host in log_report:
            list1 = []
            times = host[1]['total_request_times']
            times_percent = (float(times) / float(total_request_times)) * 100
            list1.append("%s" % host[0])
            list1.append("%s" % (display_format.format_size(host[1]['total_size_sent'])))
            list1.append("%s" % times)
            list1.append("%.2f" % float(times_percent))
            list2 = [host[1]['200'], host[1]['301'], host[1]['302'], host[1]['304'], host[1]['400'], host[1]['401'], host[1]['403'], \
                     host[1]['404'], host[1]['499'], host[1]['500'], host[1]['502'], host[1]['503'], host[1]['504']]
            list1.extend(list2)
            X.add_row(list1)
        print(X)

        print('\n')
        Total_X = PrettyTable(['TIP', 'TSend Size', 'TRequest Times', 'TRequest Times%', 'T200', 'T301', \
                         'T302', 'T304', 'T400', 'T401', 'T403', 'T404', 'T499', 'T500', 'T502', 'T503', 'T504'])
        Total_X.align["T IP"] = "l"  # Left align IP
        Total_X.padding_width = 1  # One space between column edges and contents (default)
        Total_list = []
        Total_list.append(total_ip)
        Total_list.append(total_size_sent)
        Total_list.append(total_request_times)
        Total_list.append('100%')
        Total_list1 = [fileAnalysis_obj.total_200, fileAnalysis_obj.total_301, fileAnalysis_obj.total_302, fileAnalysis_obj.total_304, \
                       fileAnalysis_obj.total_400, fileAnalysis_obj.total_401, fileAnalysis_obj.total_403, fileAnalysis_obj.total_404, \
                       fileAnalysis_obj.total_499, fileAnalysis_obj.total_500, fileAnalysis_obj.total_502, fileAnalysis_obj.total_503, \
                       fileAnalysis_obj.total_504]
        Total_list.extend(Total_list1)
        Total_X.add_row(Total_list)
        print(Total_X)

        print('\n')
        display_format.execut_time()
        print('\n')

if __name__ == '__main__':
    main_obj = Main()
    main_obj.main()