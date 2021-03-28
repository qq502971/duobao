# coding:utf-8
import requests
import json
import time
import mysql.connector
import threading
from threading import Thread


fin = False
config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'duobao',
    'password': 'wasd123',
    'database': 'duobao'
}
con = mysql.connector.connect(**config)
# 创建游标，用于执行mysql语句，并且查询结果会一并保存游标之中。
cursor = con.cursor()
sq = 'select * from task where status = 0 or status = 3'
cursor.execute(sq)
taskList = cursor.fetchall()
cursor.close()
print("tasklist_______", taskList)
# 已读取状态，改为1
# con.cursor().execute('update task set status = 1 where status = 0 or status = 3')

# 循环 把数据库任务提交给接口
def search():
    for one in taskList:
        name = one[3]
        url = one[2]
        print(one)
        # 添加任务地址
        url = 'http://query.shuzhikj.com/api/platform/add_task?name=' + str(name) + '&url=' + str(url) + '&type=1&urlmode=1'
        # 请求头带上apikey参数以及对应的值
        headers = {
            'apikey': 'mJDNNXnsu946MLB'
        }

        # 请求获取
        http_data = requests.get(url=url, headers=headers)
        http_text = http_data.text

        # 将json格式数据转换为字典
        json_data = json.loads(http_text)
        print('任务》》', '关键词：', one[3], http_text)

        def_a(one=one, json_data=json_data, headers=headers)

def def_a(one, json_data,headers):
    # 以下是查询
    while True:
        # 设置延迟时间
        time.sleep(5)

        # shuzhi = '"http://query.shuzhikj.com/api/platform/get_taskrank?id=" + json_data['data']'


        # 查询接口
        http_data = requests.get("http://query.shuzhikj.com/api/platform/get_taskrank?id=" + json_data['data'],headers=headers)
        http_json = json.loads(http_data.text)

        # if判断 code是否=0
        if http_json['code'] == 0:
            print('任务》》', '关键词：', one[3], http_data.text)
        else:
            cursor = con.cursor()
            print("[查询成功]任务排名为:", http_json['data'], "原始数据为:", http_data.text)

            con.cursor().execute('update task set status = 2,rank = ' + str(http_json['data']) + ' where id=' + str(one[0]))
            con.commit()
            print('one为：', one[1], 'data为：', http_json['data'])

            # 把排名更新到服务器
            updata_rank = "https://t.idccap.com/api/v1/QuickRanking/updata_rank"
            payload = {
                'id': one[1],
                'rank': http_json['data']
            }
            http_data = requests.post(url=updata_rank, data=payload)
            http_text = http_data.text
            print('传输成功:', http_text)
            cursor.close()
            break
search()
threading.Thread(target=search, args=('n',)).start()
threading.Thread(target=search, args=('n',)).start()