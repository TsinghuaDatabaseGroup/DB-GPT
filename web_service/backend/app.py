import json
import os

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
async def histories():
    folder_path = "../../alert_results/examples"
    file_list = os.listdir(folder_path)
    json_list = []
    # 遍历文件列表
    for file_name in file_list:
        # 确保文件是以.json扩展名结尾
        if file_name.endswith(".json"):
            # 拼接文件路径
            file_path = os.path.join(folder_path, file_name)
            # 打开文件并读取JSON数据
            with open(file_path, "r") as file:
                json_data = json.load(file)
                resp_data = {}
                resp_data["title"] = json_data.get("title", "")
                resp_data["time"] = json_data.get("time", "")
                resp_data["status"] = json_data.get("status", "")
                resp_data["severity"] = json_data.get("severity", "")
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

    # 未获取到参数或参数不存在
    if not args or not file_name:
        return {
            "code": 40002,
            "msg": "参数无效",
            "data": {}
        }
    # 拼接文件路径
    file_path = "../../alert_results/examples/" + file_name
    if file_path.endswith(".json"):
        # 打开文件并读取JSON数据
        with open(file_path, "r") as file:
            json_data = json.load(file)
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
