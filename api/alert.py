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
    print("=====alert=obj=======", obj)

    res.update(data=[])
    return res.data

