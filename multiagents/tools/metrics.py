from multiagents.utils.yaml_utils import read_yaml, read_prometheus_metrics_yaml
from multiagents.utils.server import obtain_slow_queries, obtain_anomaly_time
import warnings
from multiagents.tools.metric_monitor.anomaly_detection import prometheus
import numpy as np
from termcolor import colored
from multiagents.utils.database import DBArgs, Database
from multiagents.knowledge.knowledge_extraction import KnowledgeExtraction
import time
import json
import os

current_diag_time = time.localtime()
current_diag_time = time.strftime("%Y-%m-%d-%H:%M:%S", current_diag_time)
if not os.path.exists(f"./alert_results/{str(current_diag_time)}"):
    try:
        os.makedirs(f"./alert_results/{str(current_diag_time)}")
    except:
        pass

diag_start_time, diag_end_time = obtain_anomaly_time()

promethest_conf = read_yaml('PROMETHEUS', 'config/tool_config.yaml')
benchserver_conf = read_yaml('BENCHSERVER', 'config/tool_config.yaml')
postgresql_conf = read_yaml('POSTGRESQL', 'config/tool_config.yaml')
database_server_conf = read_yaml('DATABASESERVER', 'config/tool_config.yaml')

node_exporter_instance = promethest_conf.get('node_exporter_instance')
postgresql_exporter_instance = promethest_conf.get('postgresql_exporter_instance')

prometheus_metrics = read_prometheus_metrics_yaml(config_path='config/prometheus_metrics.yaml', node_exporter_instance=node_exporter_instance, postgresql_exporter_instance=postgresql_exporter_instance)

# configuration of the index advisor
advisor = "db2advis"  # option: extend, db2advis (fast)


# [workload statistics] read from pg_stat_statements 
dbargs = DBArgs("postgresql", config=postgresql_conf)
db = Database(dbargs, timeout=-1)


WORKLOAD_FILE_NAME = "workload_info.json"
ANOMALY_FILE_NAME = "anomalies/testing_set/testing_set_with_workload_last_10.json"
# with open(WORKLOAD_FILE_NAME, 'w') as f:
#     json.dump({'workload_statistics': '[]', 'slow_queries': '[]'}, f)

def get_workload_statistics():
    with open(WORKLOAD_FILE_NAME, 'r') as f:
        info = json.load(f)
        return info["workload_statistics"]

# def set_workload_statistics(stats):
#     if os.path.exists(WORKLOAD_FILE_NAME):
#         with open(WORKLOAD_FILE_NAME, 'r') as rf:
#             info = json.load(rf)
#         info["workload_statistics"] = stats
#         with open(WORKLOAD_FILE_NAME, 'w') as f:
#             json.dump(info, f)
#     else:
#         with open(WORKLOAD_FILE_NAME, 'w') as f:
#             json.dump({'workload_statistics': stats, 'slow_queries': '[]'}, f)

def get_slow_queries(diag_id):
    with open(ANOMALY_FILE_NAME, 'r') as f:
        info = json.load(f)
    return info[diag_id]["slow_queries"]

# def set_slow_queries(stats):
#     if os.path.exists(WORKLOAD_FILE_NAME):
#         with open(WORKLOAD_FILE_NAME, 'r') as rf:
#             info = json.load(rf)
#         info["workload_statistics"] = stats
#         with open(WORKLOAD_FILE_NAME, 'w') as f:
#             json.dump(info, f)
#     else:
#         with open(WORKLOAD_FILE_NAME, 'w') as f:
#             json.dump({'workload_statistics': '[]', 'slow_queries': stats}, f)

def get_workload_sqls(diag_id):
    with open(ANOMALY_FILE_NAME, 'r') as f:
        info = json.load(f)
    return info[diag_id]["workload"]

# [diagnosis knowledge]
knowledge_matcher = KnowledgeExtraction(
    "/multiagents/knowledge/root_causes_dbmind.jsonl")


def obtain_values_of_metrics(start_time, end_time, metrics):

    if end_time - start_time > 11000 * 3:
        warnings.warn(
            "The time range ({}, {}) is too large, please reduce the time range".format(
                start_time, end_time))

    required_values = {}

    for metric in metrics:
        metric_values = prometheus('api/v1/query_range',
                                   {'query': metric,
                                    'start': start_time,
                                    'end': end_time,
                                    'step': '3'})
        if "data" in metric_values and metric_values["data"]["result"] != []:
            metric_values = metric_values["data"]["result"][0]["values"]

            # compute the average value of the metric
            # max_value = np.max(np.array([float(value)
            #                 for _, value in metric_values]))
            values = [float(value)
                            for _, value in metric_values]

            required_values[metric.split('{')[0]] = values
        else:
            #raise Exception("No metric values found for the given time range")
            # print(colored(f"No metric values found for {start_time}-{end_time} of {metric}", "red"))
            pass

    return required_values

def processed_values(data):
    if data == []:
        raise Exception("No metric values found for the given time range")
    
    # compute processed values for the metric
    # max (reserve two decimal places)
    max_value = round(np.max(np.array(data)), 2)
    # min
    min_value = round(np.min(np.array(data)), 2)
    # mean
    mean_value = round(np.mean(np.array(data)), 2)
    # deviation
    deviation_value = round(np.std(np.array(data)), 2)
    # evenly sampled 10 values (reserve two decimal places)
    evenly_sampled_values = [round(data[i], 2) for i in range(0, len(data), len(data) // 10)]

    # describe the above five values in a string
    return f"the max value is {max_value}, the min value is {min_value}, the mean value is {mean_value}, the deviation value is {deviation_value}, and the evenly_sampled_values are {evenly_sampled_values}."
