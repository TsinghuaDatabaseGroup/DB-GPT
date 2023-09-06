from multiagents.utils.core import read_yaml, read_prometheus_metrics_yaml
import warnings
from multiagents.tools.metric_monitor.anomaly_detection import prometheus
import numpy as np
import pdb

promethest_conf = read_yaml('PROMETHEUS', 'config/tool_config.yaml')
benchserver_conf = read_yaml('BENCHSERVER', 'config/tool_config.yaml')
postgresql_conf = read_yaml('POSTGRESQL', 'config/tool_config.yaml')

node_exporter_instance = promethest_conf.get('node_exporter_instance')
postgresql_exporter_instance = promethest_conf.get('postgresql_exporter_instance')

prometheus_metrics = read_prometheus_metrics_yaml(config_path='config/prometheus_metrics.yaml', node_exporter_instance=node_exporter_instance, postgresql_exporter_instance=postgresql_exporter_instance)

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
        if metric_values["data"]["result"] != []:
            metric_values = metric_values["data"]["result"][0]["values"]
        else:
            raise Exception("No metric values found for the given time range")

        # compute the average value of the metric
        max_value = np.max(np.array([float(value)
                           for _, value in metric_values]))

        required_values[metric] = max_value

    return required_values

