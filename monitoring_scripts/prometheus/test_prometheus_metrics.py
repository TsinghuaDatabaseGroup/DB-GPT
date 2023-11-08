import requests
import json
import sys

sys.path.append('./')

def prometheus(url, params):
    # conf = read_yaml('PROMETHEUS', 'config/tool_config.yaml')
    res = requests.get(url="http://8.131.229.55:9090/" + url, params=params)
    print(json.dumps(res.json()))

if __name__ == '__main__':
    prometheus('api/v1/query_range', {'query': 'node_disk_io_time_seconds_total{instance=~"123.56.63.105:9100"}', 'start': '1693994400', 'end': '1693994550', 'step': '3'})

    #prometheus('api/v1/query_range', {'query': '100 - (avg(irate(node_cpu_seconds_total{instance=~"123.56.63.105:9100",mode="idle"}[1m])) * 100)', 'start': '1684412385', 'end': '1684412485', 'step': '3'})

    # node_sockstat_TCP_alloc{instance=~"123.56.63.105:9100"}

    # irate(node_netstat_Tcp_PassiveOpens{instance=~"123.56.63.105:9100"}[1m])

    # irate(node_network_receive_bytes_total{instance=~"123.56.63.105:9100",device=~'$nic'}[5m])*8

    # irate(pg_stat_bgwriter_buffers_backend_fsync{instance="123.56.63.105:9100"}[5m])
    # '(avg(irate(node_cpu_seconds_total{{instance=~\\"172.27.58.65:9100\\",mode=\\"user\\"}}[1m]))) * 100'
    # 1693994400.0 1693994550