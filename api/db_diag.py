import logging

from flask import Blueprint, request

from agentverse import AgentVerse
from api.utils.code import ResponseCode
from api.utils.response import ResMsg
from api.utils.util import route

bp = Blueprint("db_diag", __name__, url_prefix='/db_diag')

logger = logging.getLogger(__name__)

agentverse = AgentVerse.from_task('db_diag')

@route(bp, '/run', methods=["POST"])
def run():
    """
    return start gradio
    :return:
    """
    res = ResMsg()
    obj = request.get_json(force=True)
    start_at = obj.get("start_at")
    end_at = obj.get("end_at")
    # 未获取到参数或参数不存在
    if not obj or not start_at or not start_at:
        res.update(code=ResponseCode.InvalidParameter)
        return res.data
    # 将start_at和end_at写入文件
    with open("bmtools/diag_time.txt", "a") as f:
        f.write(str(start_at) + "-" + str(end_at) + "\n")
    agentverse.reset()
    results = agentverse.next()
    result = {}
    # 判断是否是数组，如果是数组，且长度大于1，取第一个值
    if isinstance(results, list) and len(results) > 0:
        result = results[0]
        result = {"content": result.content, "sender": result.sender}
    res.update(data=result)
    return res.data


@route(bp, '/next_step', methods=["POST"])
def next_step():
    """
    return start gradio
    :return:
    """
    res = ResMsg()
    results = agentverse.next()
    result = {}
    # 判断是否是数组，如果是数组，且长度大于1，取第一个值
    if isinstance(results, list) and len(results) > 0:
        result = results[0]
        result = {"content": result.content, "sender": result.sender}
    res.update(data=result)
    return res.data

@route(bp, '/submit', methods=["POST"])
def submit():
    """
    return start gradio
    :return:
    """
    res = ResMsg()
    obj = request.get_json(force=True)
    message = obj.get("message")
    results = agentverse.submit(message)
    result = None
    # 判断是否是数组，如果是数组，且长度大于1，取第一个值
    if isinstance(results, list) and len(results) > 0:
        result = results[0]
        result = {"content": result.content, "sender": result.sender}
    res.update(data=result)
    return res.data


@route(bp, '/reset', methods=["POST"])
def reset():
    """
    return start gradio
    :return:
    """
    res = ResMsg()
    agentverse.reset()
    res.update(data={})
    return res.data

