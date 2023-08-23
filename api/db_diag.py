import logging

from flask import Blueprint, request

from agentverse import AgentVerse
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
    # obj = request.get_json(force=True)
    # dataset_name = obj.get("dataset")
    # # 未获取到参数或参数不存在
    # if not obj or not dataset_name:
    #     res.update(code=ResponseCode.InvalidParameter)
    #     return res.data
    # agentverse.run()
    res.update(data=str(agentverse.next()))
    return res.data


@route(bp, '/next_step', methods=["POST"])
def next_step():
    """
    return start gradio
    :return:
    """
    res = ResMsg()

    # obj = request.get_json(force=True)
    # dataset_name = obj.get("dataset")
    # # 未获取到参数或参数不存在
    # if not obj or not dataset_name:
    #     res.update(code=ResponseCode.InvalidParameter)
    #     return res.data

    res.update(data=str(agentverse.next()))
    return res.data

@route(bp, '/submit', methods=["POST"])
def submit():
    """
    return start gradio
    :return:
    """
    res = ResMsg()

    # obj = request.get_json(force=True)
    # dataset_name = obj.get("dataset")
    # # 未获取到参数或参数不存在
    # if not obj or not dataset_name:
    #     res.update(code=ResponseCode.InvalidParameter)
    #     return res.data


    res.update(data=agentverse.submit())
    return res.data


@route(bp, '/reset', methods=["POST"])
def reset():
    """
    return start gradio
    :return:
    """
    res = ResMsg()

    # obj = request.get_json(force=True)
    # dataset_name = obj.get("dataset")
    # # 未获取到参数或参数不存在
    # if not obj or not dataset_name:
    #     res.update(code=ResponseCode.InvalidParameter)
    #     return res.data

    agentverse.reset()
    res.update(data={})
    return res.data

#
# @route(bp, '/distribution', methods=["POST"])
# def distribution():
#     """
#     return the data and workload statistics of the dataset
#     :return:
#     """
#     res = ResMsg()
#     obj = request.get_json(force=True)
#     dataset_name = obj.get("dataset")
#     # 未获取到参数或参数不存在
#     if not obj or not dataset_name:
#         res.update(code=ResponseCode.InvalidParameter)
#         return res.data
#
#     # 生成参数
#     args = PartitionConfig()
#     args.database = dataset_name
#     # 生成路径
#     success, msg = args.generate_paths()
#     # 生成路径失败
#     if not success:
#         res.update(code=ResponseCode.InvalidParameter, msg=msg)
#         return res.data
#
#     # obtain the table info
#     tbls = table_statistics(args)
#     # {'lineitem': ['l_quantity', 'l_shipdate'], 'orders': ['o_orderkey', 'o_custkey'], 'customer': ['c_custkey']}
#
#     # obtain the column info (in column graph)
#     graph = Column2Graph(args)
#
#     # todo：graph.vertex_matrix graph.edge_matrix 取值，需要转变成 json 识别的格式
#     # json format
#
#     # 数据集获取
#     vertex_json = graph.vertex_json
#     edge_json = graph.edge_json
#     nodes = []
#     links = []
#     categories = []
#     for i, key in enumerate(vertex_json.keys()):
#         nodes.append({
#             "name": key,
#             "symbolSize": min(max(graph.vertex_json[key] * 1000, 16), 40),
#             "id": key,
#             "value": graph.vertex_json[key],
#             "category": i
#         })
#         categories.append(i)
#
#     for i, key in enumerate(edge_json.keys()):
#         edge_json_value = edge_json[key]
#         edge_json_value.setdefault('lineStyle', {})
#         edge_json_value.get('lineStyle').setdefault('width', min(max(edge_json_value.get('value') / 100, 1), 20))
#         links.append(edge_json_value)
#     data = {
#         "distributions": tbls,
#         "column2Graph": {
#             "nodes": nodes,
#             "categories": categories,
#             "links": links
#         }
#     }
#     res.update(data=data)
#     return res.data
