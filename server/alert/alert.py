import logging
from datetime import datetime
import json
import os
from fastapi import Body, Request
from server.utils import BaseResponse
from configs import DIAGNOSTIC_RESULTS_PATH, DIAGNOSE_LLM_MODEL_LIST


def histories(start: str = Body(default=None, description="诊断文件开始时间"),
              end: str = Body(default=None, description="诊断文件结束时间"),
              model: str = Body("GPT4-0613", description="诊断模型")):
    folder_path = os.path.join(DIAGNOSTIC_RESULTS_PATH, model)
    # 获取文件列表
    if not os.path.exists(folder_path):
        return BaseResponse(code=404, msg="该模型没有对应的诊断文件夹")
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
                try:
                    json_data = json.load(file)
                    json_data["time"] = datetime.fromtimestamp(int(json_data.get("time", ""))).strftime("%Y-%m-%d %H:%M:%S")
                    json_data["file_name"] = file_name
                    # 将JSON数据添加到列表中
                    json_list.append(json_data)
                except Exception as e:
                    logging.error(f"读取Json文件{file_path}失败: {e}")
                    continue
    return BaseResponse(code=200, msg="Success", data=json_list)


def history_detail(file: str = Body(..., description="诊断文件名称"),
                   model: str = Body("GPT4-0613", description="诊断模型")):
    file_path = f"{DIAGNOSTIC_RESULTS_PATH}/{model}/{file}"
    if not os.path.exists(file_path):
        return BaseResponse(code=404, msg="无对应的诊断文件")
    if file_path.endswith(".json") or file_path.endswith(".jsonl"):
        # 打开文件并读取JSON数据
        with open(file_path, "r") as file:
            json_data = json.load(file)
            json_data["time"] = datetime.fromtimestamp(int(json_data.get("time", ""))).strftime("%Y-%m-%d %H:%M:%S")
            return BaseResponse(code=200, msg="Success", data=json_data)
    else:
        return BaseResponse(code=400, msg="无对应的文件")


def diagnose_llm_model_list():
    return BaseResponse(code=200, msg="Success", data=DIAGNOSE_LLM_MODEL_LIST)

