#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
删除单个七牛目录下文件或者单个文件
使用方法  python3 qiniu_delete3_single.py 需要删除七牛目录路径下文件或者单个文件
"""

import subprocess
import sys
from qiniu import Auth
from qiniu import BucketManager

access_key = ''
secret_key = ''

#初始化Auth状态
q = Auth(access_key, secret_key)

#初始化BucketManager
bucket = BucketManager(q)

#你要删除的空间名
bucket_name = ''

# 列出所要删除的文件
out_file = '/tmp/qiniu_list'

def list_filename(path):
    subprocess.Popen('qshell account {} {}'.format(access_key, secret_key), shell=True)
    subprocess.Popen('qshell listbucket {} {} {}'.format(bucket_name, path, out_file), shell=True).wait()

def del_file():
    try:
        with open(out_file, 'r') as f:
            for i in f.readlines():
                if len(i) == 0:
                    print("There is no file under the path!")
                    break
                else:
                    file_name = i.strip().split()[0].strip()
                    ret, info = bucket.delete(bucket_name, file_name)
                    print(info)
    except:pass

if __name__ == '__main__':
    try:
        list_filename(sys.argv[1])
    except:
        print("""$"Usage: $1 Need to delete the path, Output /tmp/qiniu_list""")
        sys.exit(1)
    del_file()
    subprocess.Popen('rm -f {}'.format(out_file), shell=True)
