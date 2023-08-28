import requests
import json

from utils.core import read_yaml


def prometheus(url, params):
    conf = read_yaml('PROMETHEUS', 'config/tool_config.yaml')
    res = requests.get(url=conf.get('api_url') + url, params=params)
    print(json.dumps(res.json()))

if __name__ == '__main__':
    #prometheus('api/v1/query_range', {'query': '100 - (avg(irate(node_cpu_seconds_total{instance=~"123.56.63.105:9100",mode="idle"}[1m])) * 100)', 'start': '1684412385', 'end': '1684412485', 'step': '3'})
    prometheus('api/v1/query_range', {'query': 'node_load5', 'start': '1684412385', 'end': '1684412485', 'step': '3'})