import datetime
import decimal
import uuid

import yaml
from flask.json import JSONEncoder as BaseJSONEncoder
import pdb

class JSONEncoder(BaseJSONEncoder):

    def default(self, o):
        """
        如有其他的需求可直接在下面添加
        :param o:
        :return:
        """
        if isinstance(o, datetime.datetime):
            # 格式化时间
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, datetime.date):
            # 格式化日期
            return o.strftime('%Y-%m-%d')
        if isinstance(o, decimal.Decimal):
            # 格式化高精度数字
            return str(o)
        if isinstance(o, uuid.UUID):
            # 格式化uuid
            return str(o)
        if isinstance(o, bytes):
            # 格式化字节数据
            return o.decode("utf-8")
        return super(JSONEncoder, self).default(o)


def read_yaml(config_name, config_path):
    """
    config_name:需要读取的配置内容
    config_path:配置文件路径
    """
    if config_path:
        with open(config_path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f.read())
            if config_name and config_name in conf.keys():
                return conf[config_name]
            else:
                return conf
    else:
        raise ValueError('请输入正确配置文件路径')


def read_prometheus_metrics_yaml(config_path, node_exporter_instance, postgresql_exporter_instance):
    """
    config_path: 配置文件路径
    """
    if not config_path:
        raise ValueError('请输入正确的配置文件路径')

    result_dict = {}
    with open(config_path, 'r', encoding='utf-8') as f:
        prometheus_metrics = yaml.safe_load(f.read())

        for key in prometheus_metrics:
            items = prometheus_metrics[key]

            if isinstance(items, list):
                query_list = []
                for item in items:
                    instance_from = item.get('instance_from')
                    instance = node_exporter_instance if instance_from == 'node' else (
                        postgresql_exporter_instance if instance_from == 'postgresql' else None
                    )
                    if not instance:
                        raise ValueError('请输入正确的instance_from')
                    query_list.append(item['query'].replace('$instance', instance))
                result_dict[key] = query_list

            elif isinstance(items, dict):
                instance_from = items.get('instance_from')
                instance = node_exporter_instance if instance_from == 'node' else (
                    postgresql_exporter_instance if instance_from == 'postgresql' else None
                )
                if not instance:
                    raise ValueError('请输入正确的instance_from')
                result_dict[key] = items['query'].replace('$instance', instance)

    return result_dict
