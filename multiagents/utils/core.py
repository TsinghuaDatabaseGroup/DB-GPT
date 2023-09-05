import datetime
import decimal
import uuid

import yaml
from flask.json import JSONEncoder as BaseJSONEncoder

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
    print(config_name.upper())
    if config_name and config_path:
        with open(config_path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f.read())
        if config_name.upper() in conf.keys():
            return conf[config_name.upper()]
        else:
            raise KeyError('未找到对应的配置信息')
    else:
        raise ValueError('请输入正确的配置名称或配置文件路径')