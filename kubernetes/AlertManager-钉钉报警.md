## AlertManager Dingtalk 简介
用于接收`AlertManager`服务通知并通过钉钉机器人报警

## prometheus-operator 安装请参考往期文章
- `https://github.com/yangpeng14/DevOps/blob/master/kubernetes/prometheus-operator%E6%89%8B%E5%8A%A8%E9%83%A8%E7%BD%B2.md`

## AlertManager 钉钉报警服务示例
![](https://www.yp14.cn/img/warn.png)

## 项目地址
`https://github.com/yangpeng14/alertmanager-dingtalk-hook`

## 主要代码
```python
import os
import json
import requests
import arrow

from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def send():
    if request.method == 'POST':
        post_data = request.get_data()
        send_alert(bytes2json(post_data))
        return 'success'
    else:
        return 'weclome to use prometheus alertmanager dingtalk webhook server!'


def bytes2json(data_bytes):
    data = data_bytes.decode('utf8').replace("'", '"')
    return json.loads(data)


def send_alert(data):
    token = os.getenv('ROBOT_TOKEN')
    if not token:
        print('you must set ROBOT_TOKEN env')
        return
    url = 'https://oapi.dingtalk.com/robot/send?access_token=%s' % token
    for output in data['alerts'][:]:
        try:
            pod_name = output['labels']['pod']
        except KeyError:
            try:
                pod_name = output['labels']['pod_name']
            except KeyError:
                pod_name = 'null'
                
        try:
            namespace = output['labels']['namespace']
        except KeyError:
            namespace = 'null'

        try:
            message = output['annotations']['message']
        except KeyError:
            try:
                message = output['annotations']['description']
            except KeyError:
                message = 'null'

        send_data = {
            "msgtype": "markdown",
            "markdown": {
                "title": "prometheus_alert",
                "text": "## 告警程序: prometheus_alert \n" +
                        "**告警级别**: %s \n\n" % output['labels']['severity'] +
                        "**告警类型**: %s \n\n" % output['labels']['alertname'] +
                        "**故障pod**: %s \n\n" % pod_name +
                        "**故障namespace**: %s \n\n" % namespace +
                        "**告警详情**: %s \n\n" % message +
                        "**告警状态**: %s \n\n" % output['status'] +
                        "**触发时间**: %s \n\n" % arrow.get(output['startsAt']).to('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss ZZ') +
                        "**触发结束时间**: %s \n" % arrow.get(output['endsAt']).to('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss ZZ')
            }
        }
        req = requests.post(url, json=send_data)
        result = req.json()
        if result['errcode'] != 0:
            print('notify dingtalk error: %s' % result['errcode'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 使用 Docker 运行
`docker run -p 5000:5000 --name -e ROBOT_TOKEN=<钉钉机器人TOKEN> dingtalk-hook -d yangpeng2468/alertmanager-dingtalk-hook:v1`

