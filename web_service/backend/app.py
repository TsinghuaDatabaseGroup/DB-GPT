import json
import os
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"],)


@app.get('/test')
async def test():
    return {
        "code": 0,
        "msg": "success",
        "data": "server is running"
    }

@app.options('/histories')
async def histories_options():
    return {"Allow": "POST"}


@app.post('/histories')
async def histories(request: Request):

    args = await request.json()
    start = args.get("start", None)
    end = args.get("end", None)
    model = args.get("model", None)
    # 未获取到参数或参数不存在
    if not args or not model:
        return {
            "code": 40002,
            "msg": "参数无效",
            "data": {}
        }


    folder_path = f"../../alert_results/{model}"
    file_list = os.listdir(folder_path)
    file_list = sorted(file_list, reverse=True)
    json_list = []
    # 遍历文件列表
    for file_name in file_list:
        # 确保文件是以.json扩展名结尾
        if file_name.endswith(".json") or file_name.endswith(".jsonl"):
            # 拼接文件路径
            file_path = os.path.join(folder_path, file_name)
            timestamp = int(os.path.splitext(file_name)[0])
            # 将时间戳转换为datetime对象
            if start and timestamp < int(start):
                continue
            if end and timestamp > int(end):
                continue
            # 打开文件并读取JSON数据
            with open(file_path, "r") as file:
                json_data = json.load(file)
                resp_data = {}
                resp_data["title"] = json_data.get("title", "")
                resp_data["time"] = datetime.fromtimestamp(int(json_data.get("time", ""))).strftime("%Y-%m-%d %H:%M:%S")
                resp_data["alerts"] = json_data.get("alerts", "")
                resp_data["file_name"] = file_name
            # 将JSON数据添加到列表中
            json_list.append(resp_data)
    return {
        "code": 0,
        "msg": "success",
        "data": json_list
    }

@app.options('/history-detail')
async def history_detail_options():
    return {"Allow": "POST"}


@app.post('/history-detail')
async def history_detail(request: Request):
    """
    return add alert
    :return:
    """
    args = await request.json()
    file_name = args.get("file", None)
    model = args.get("model", None)

    # 未获取到参数或参数不存在
    if not args or not file_name or not model:
        return {
            "code": 40002,
            "msg": "参数无效",
            "data": {}
        }
    # 拼接文件路径
    file_path = f"../../alert_results/{model}/{file_name}"
    if file_path.endswith(".json") or file_path.endswith(".jsonl"):
        # 打开文件并读取JSON数据
        with open(file_path, "r") as file:
            json_data = json.load(file)
            json_data["time"] = datetime.fromtimestamp(int(json_data.get("time", ""))).strftime("%Y-%m-%d %H:%M:%S")
            return {
                "code": 0,
                "msg": "success",
                "data": json_data
            }
    else:
        return {
            "code": 40002,
            "msg": "无对应的文件",
            "data": {}
        }


if __name__ == "__main__":
    uvicorn.run(
        app = app,
        host = "0.0.0.0",
        port = 8024
    )
