import logging
from flask import Blueprint, request
from api.utils.response import ResMsg
from api.utils.util import route


bp = Blueprint("alert", __name__, url_prefix='/alert')

logger = logging.getLogger(__name__)


@route(bp, '/alert', methods=["POST"])
def alert():
    """
    return add alert
    :return:
    """
    res = ResMsg()
    obj = request.get_json(force=True)
    # 将obj写入文件中
    with open("alert.txt", "a") as f:
        f.write(str(obj) + "\n")
    res.update(data=[])
    return res.data

