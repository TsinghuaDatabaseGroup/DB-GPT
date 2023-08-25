import logging

from flask import Blueprint
from api.utils.response import ResMsg
from api.utils.util import route

bp = Blueprint("config", __name__, url_prefix='/config')

logger = logging.getLogger(__name__)


@route(bp, '/instances', methods=["POST"])
def instances():
    """
    return start gradio
    :return:
    """
    res = ResMsg()
    res.update(data={
        "node": "172.27.58.65:9100",
        "postgresql": "172.27.58.65:9187",
    })
    return res.data
