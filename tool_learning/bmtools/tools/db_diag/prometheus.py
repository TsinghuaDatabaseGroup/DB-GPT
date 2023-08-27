import requests
import json
import datetime
import numpy as np

from utils.core import read_yaml

conf = read_yaml('PROMETHEUS', 'config/tool_config.yaml')

def prometheus(url, params):

    output = requests.get(conf.get('api_url') + url, params=params)
    output = output.json()
    print(output)
    #output = json.dumps(res.json())
    output = output["data"]["result"][0]["values"]
    output = np.array([float(value) for _, value in output])
    print(output)
    #print(type(output))

if __name__ == '__main__':

    start_timestamp_str = "2023-08-09 14:52:30"
    dt = datetime.datetime.strptime(start_timestamp_str, "%Y-%m-%d %H:%M:%S")
    timestamp = dt.timestamp()
    start_time = timestamp

    end_timestamp_str = "2023-08-09 14:56:30"
    dt = datetime.datetime.strptime(end_timestamp_str, "%Y-%m-%d %H:%M:%S")
    timestamp = dt.timestamp()
    end_time = timestamp

    prometheus('api/v1/query_range', {'query': "irate(node_disk_write_time_seconds_total{instance=~\"{}\"}[1m])".format(conf.get('postgresql_exporter_instance')), 'start': start_time, 'end': end_time, 'step': '3'})