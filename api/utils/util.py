from functools import wraps
from flask import jsonify
from api.utils.response import ResMsg
import os
import numpy as np


def route(bp, *args, **kwargs):
    """
    路由设置,统一返回格式
    :param bp: 蓝图
    :param args:
    :param kwargs:
    :return:
    """
    kwargs.setdefault('strict_slashes', False)

    def decorator(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            rv = f(*args, **kwargs)
            # 响应函数返回整数和浮点型
            if isinstance(rv, (int, float)):
                res = ResMsg()
                res.update(data=rv)
                return jsonify(res.data)
            # 响应函数返回元组
            elif isinstance(rv, tuple):
                # 判断是否为多个参数
                if len(rv) >= 3:
                    return jsonify(rv[0]), rv[1], rv[2]
                else:
                    return jsonify(rv[0]), rv[1]
            # 响应函数返回字典
            elif isinstance(rv, dict):
                return jsonify(rv)
            # 响应函数返回字节
            elif isinstance(rv, bytes):
                rv = rv.decode('utf-8')
                return jsonify(rv)
            else:
                return jsonify(rv)

        return wrapper

    return decorator

def view_route(f):
    """
    路由设置,统一返回格式
    :param f:
    :return:
    """

    def decorator(*args, **kwargs):
        rv = f(*args, **kwargs)
        if isinstance(rv, (int, float)):
            res = ResMsg()
            res.update(data=rv)
            return jsonify(res.data)
        elif isinstance(rv, tuple):
            if len(rv) >= 3:
                return jsonify(rv[0]), rv[1], rv[2]
            else:
                return jsonify(rv[0]), rv[1]
        elif isinstance(rv, dict):
            return jsonify(rv)
        elif isinstance(rv, bytes):
            rv = rv.decode('utf-8')
            return jsonify(rv)
        else:
            return jsonify(rv)

    return decorator


def get_dataset_names():
    current_file = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_file)
    parent_path = os.path.dirname(directory_path)
    dataset_path = os.path.join(parent_path, "services/partition/datasets")

    directory_names = []
    for dir_name in os.listdir(dataset_path):
        if os.path.isdir(os.path.join(dataset_path, dir_name)):
            directory_names.append({"name": dir_name, "value": dir_name})
    return directory_names


def generate_coordinates(num_points, graph_width, graph_height):
    # 计算每个点的横坐标和纵坐标上的间隔
    x_interval = graph_width // num_points
    y_interval = graph_height // num_points

    # 生成相应数量的点
    points = np.zeros((num_points, 2))

    # 根据间隔计算每个点在图中的坐标
    for i in range(num_points):
        points[i][0] = (i * x_interval) + (x_interval // 2)
        points[i][1] = (i * y_interval) + (y_interval // 2)

    return points.tolist()