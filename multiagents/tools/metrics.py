from multiagents.utils.core import read_yaml
import warnings
from multiagents.tools.metric_monitor.anomaly_detection import prometheus
import numpy as np

promethest_conf = read_yaml('PROMETHEUS', 'config/tool_config.yaml')
benchserver_conf = read_yaml('BENCHSERVER', 'config/tool_config.yaml')
postgresql_conf = read_yaml('POSTGRESQL', 'config/tool_config.yaml')

node_exporter_instance = promethest_conf.get('node_exporter_instance')
postgresql_exporter_instance = promethest_conf.get('postgresql_exporter_instance')

prometheus_metrics = {
    "cpu_usage": f"(avg(irate(node_cpu_seconds_total{{instance=~\"{node_exporter_instance}\",mode=\"user\"}}[1m]))) * 100",
    "cpu_metrics": [
        f"node_scrape_collector_duration_seconds{{instance=\"{node_exporter_instance}\"}}",
        f"node_procs_running{{instance=\"{node_exporter_instance}\"}}",
        f"node_procs_blocked{{instance=\"{node_exporter_instance}\"}}",
        f"node_entropy_available_bits{{instance=\"{node_exporter_instance}\"}}",
        f"node_load1{{instance=\"{node_exporter_instance}\"}}",
        f"node_load5{{instance=\"{node_exporter_instance}\"}}",
        f"node_load15{{instance=\"{node_exporter_instance}\"}}"],
    "memory_usage": f"node_memory_MemTotal_bytes{{instance=~\"{node_exporter_instance}\"}} - (node_memory_Cached_bytes{{instance=~\"{node_exporter_instance}\"}} + node_memory_Buffers_bytes{{instance=~\"{node_exporter_instance}\"}} + node_memory_MemFree_bytes{{instance=~\"{node_exporter_instance}\"}})",
    "memory_metrics": [
        f"irate(node_disk_write_time_seconds_total{{instance=~\"{node_exporter_instance}\"}}[1m])",
        f"node_memory_Inactive_anon_bytes{{instance=\"{node_exporter_instance}\"}}",
        f"node_memory_MemFree_bytes{{instance=\"{node_exporter_instance}\"}}",
        f"node_memory_Dirty_bytes{{instance=\"{node_exporter_instance}\"}}",
        f"pg_stat_activity_count{{instance=~\"{postgresql_exporter_instance}\", state=\"active\"}} !=0"],
    "network_metrics": [
        f"node_sockstat_TCP_tw{{instance=\"{node_exporter_instance}\"}}",
        f"node_sockstat_TCP_orphan{{instance=\"{node_exporter_instance}\"}}"]
        }

def obtain_values_of_metrics(start_time, end_time, metrics):

    if end_time - start_time > 11000 * 3:
        warnings.warn(
            "The time range ({}, {}) is too large, please reduce the time range".format(
                start_time, end_time))

    required_values = {}

    print(" ====> metrics: ", metrics)
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

