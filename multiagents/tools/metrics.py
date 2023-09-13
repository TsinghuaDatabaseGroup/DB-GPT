from multiagents.utils.core import read_yaml, read_prometheus_metrics_yaml
import warnings
from multiagents.tools.metric_monitor.anomaly_detection import prometheus
import numpy as np
import pdb
from termcolor import colored


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

            # compute the average value of the metric
            # max_value = np.max(np.array([float(value)
            #                 for _, value in metric_values]))
            values = [float(value)
                            for _, value in metric_values]

            required_values[metric.split('{')[0]] = values
        else:
            #raise Exception("No metric values found for the given time range")
            print(colored(f"No metric values found for {start_time}-{end_time} of {metric}", "red"))

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
