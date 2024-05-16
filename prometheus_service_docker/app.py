import json
import os
import threading
import logging

import uvicorn
from fastapi import FastAPI, Request
from datetime import datetime

from prometheus_abnormal_metric import obtain_exceptions_in_times
from get_slow_queries import obtain_slow_queries


app = FastAPI()


@app.get('/test')
async def test():
    return {
        "code": 0,
        "msg": "success",
        "data": "prometheus service is running"
    }


@app.post('/alert')
async def alert(request: Request):
    """
    return add alert
    :return:
    """
    args = await request.json()
    # 将obj写入文件中
    with open("alert_history.txt", "a") as f:
        f.write(json.dumps(args) + "\n")

    try:
        if args["status"] == "resolved":
            # 开启异步线程，拼装诊断文件
            thread = threading.Thread(target=gen_diagnostic_file, args=(args,))
            thread.start()
    except Exception as e:
        logging.error(e)

    return {
        "code": 0,
        "msg": "success",
        "data": ""
    }


def gen_diagnostic_file(args):
    alerts = args.get("alerts", [])

    # 获取alert的startsAt属性，并将其转换为UTC时间格式
    alert_time = alerts[0].get("startsAt")
    alert_time = alert_time[:-4] + 'Z'
    alert_time = datetime.strptime(alert_time, "%Y-%m-%dT%H:%M:%S.%fZ")

    # 获取开始时间和结束时间，开始时间减去5分钟，结束时间加上60秒
    start_seconds = alert_time.timestamp() - 60 * 5
    end_seconds = alert_time.timestamp() + 60

    # 调用obtain_exceptions_in_times函数获取在指定时间范围内的异常，并返回结果
    exceptions = obtain_exceptions_in_times(start_seconds, end_seconds)
    # 调用obtain_slow_queries函数获取在指定时间范围内的慢查询，并返回结果
    slow_queries = obtain_slow_queries(start_seconds, end_seconds)

    diagnostic_file_data = {
        "start_time": start_seconds,
        "end_time": end_seconds,
        "start_timestamp": datetime.fromtimestamp(start_seconds).strftime("%Y-%m-%d %H:%M:%S"),
        "end_timestamp": datetime.fromtimestamp(end_seconds).strftime("%Y-%m-%d %H:%M:%S"),
        "alerts": [alerts],
        "workload": [],  # 获取异常时间段内所有的请求，可根据实际情况增加窗口时间
        "slow_queries": slow_queries,
        "exceptions": exceptions
    }

    # 将获取到的数据写入到一个新的文件中，文件名为当前的时间戳
    # 检查文件夹是否存在，不存在则创建
    path = './gen_diagnostic_files'
    if not os.path.exists(path):
        os.makedirs(path)

    filename = 'alert_time_' + datetime.fromtimestamp(start_seconds).strftime("%Y-%m-%d-%H-%M-%S") + '.json'
    with open(os.path.join(path, filename), 'w') as f:
        json.dump(diagnostic_file_data, f)


if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=8023
    )
