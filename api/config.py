import logging

from flask import Blueprint
from api.utils.response import ResMsg
from api.utils.util import route
from utils.core import read_yaml

bp = Blueprint("config", __name__, url_prefix='/config')

logger = logging.getLogger(__name__)


@route(bp, '/instances', methods=["POST"])
def instances():
    """
    return start gradio
    :return:
    """
    res = ResMsg()
    conf = read_yaml('PROMETHEUS', 'config/tool_config.yaml')
    res.update(data={
        "node": conf.get('node_exporter_instance'),
        "postgresql": conf.get('postgresql_exporter_instance'),
    })
    return res.data
