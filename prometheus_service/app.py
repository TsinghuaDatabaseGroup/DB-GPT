import json
import threading
import logging
import uvicorn
from fastapi import FastAPI, Request

from prometheus_abnormal_metric import fetch_prometheus_metrics

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
            # 开启异步线程，获取异常时间内的prometheus指标，并保存到新文件中，文件名为时间戳
            thread = threading.Thread(target=fetch_prometheus_metrics, args=(args, ))
            thread.start()
    except Exception as e:
        logging.error(e)

    return {
        "code": 0,
        "msg": "success",
        "data": ""
    }

if __name__ == "__main__":
    uvicorn.run(
        app = app,
        host = "0.0.0.0",
        port = 8023
    )
