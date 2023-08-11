import requests
import json

def prometheus(url, params):
    res = requests.get(url='http://8.131.229.55:9090/' + url, params=params)
    print(json.dumps(res.json()))

if __name__ == '__main__':
    #prometheus('api/v1/query_range', {'query': '100 - (avg(irate(node_cpu_seconds_total{instance=~"123.56.63.105:9100",mode="idle"}[1m])) * 100)', 'start': '1684412385', 'end': '1684412485', 'step': '3'})
    prometheus('api/v1/query_range', {'query': 'node_load5', 'start': '1684412385', 'end': '1684412485', 'step': '3'})