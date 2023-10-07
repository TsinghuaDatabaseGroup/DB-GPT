import json
import logging
import os

from flask import Blueprint, request

from api.utils.code import ResponseCode
from api.utils.response import ResMsg
from api.utils.util import route


bp = Blueprint("alert", __name__, url_prefix='/alert')

logger = logging.getLogger(__name__)


@route(bp, '/histories', methods=["POST"])
def history():
    """
    return add alert
    :return:
    """
    res = ResMsg()

    # obj = request.get_json(force=True)
    # print("=====alert=obj=======", obj)
    folder_path = "./alert_results/examples"
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
                resp_data["file_name"] = file_name
            # 将JSON数据添加到列表中
            json_list.append(resp_data)
    res.update(data=json_list)
    return res.data



@route(bp, '/history-detail', methods=["POST"])
def history_detail():
    """
    return add alert
    :return:
    """
    res = ResMsg()

    obj = request.get_json(force=True)
    file_name = obj.get("file")

    # 未获取到参数或参数不存在
    if not obj or not file_name:
        res.update(code=ResponseCode.InvalidParameter)
        return res.data
    json_data = {}
    # 拼接文件路径
    file_path = "./alert_results/examples/" + file_name
    if file_path.endswith(".json"):
        # 打开文件并读取JSON数据
        with open(file_path, "r") as file:
            json_data = json.load(file)
    else:
        res.update(code=ResponseCode.InvalidParameter)
        return res.data

    res.update(data=json_data)
    return res.data