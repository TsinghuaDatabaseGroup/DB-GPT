import numpy as np
import ast

from multiagents.tools.metric_monitor.anomaly_detection import prometheus
from multiagents.tools.metric_monitor.anomaly_detection import detect_anomalies
from multiagents.tools.metrics import *
from multiagents.tools.metric_monitor.anomaly_analysis import metric_analysis_results, slow_query_analysis_results, workload_analysis_results
from multiagents.utils.markdown_format import generate_prometheus_chart_content
from multiagents.tools.index_advisor.api import optimize_index_selection
from server.knowledge_base.kb_doc_api import search_docs
from server.knowledge_base.kb_service.base import KBServiceFactory, SupportedVSType
from prometheus_service.prometheus_abnormal_metric import prometheus_metrics


def whether_is_abnormal_metric(
        start_time: int,
        end_time: int,
        metric_name: str = "cpu_usage",
        diag_id: str = "",
        enable_prometheus: bool = True):

    if metric_name not in prometheus_metrics:
        # print(f"{metric_name} is unknown")
        return f"The metric {metric_name} is unknown \n {metric_name}"

    if enable_prometheus == True:
        # read metric values from prometheus
        metric_values = prometheus('api/v1/query_range',
                                    {'query': prometheus_metrics[metric_name],
                                    'start': start_time,
                                    'end': end_time,
                                    'step': '3'})

        if "data" not in metric_values:
            raise Exception("The metric name could be wrong!")
        if "result" in metric_values["data"] and metric_values["data"]["result"] != []:
            metric_values = metric_values["data"]["result"][0]["values"]
        else:
            raise Exception("No metric values found for the given time range")

        is_abnormal = detect_anomalies(
            np.array([float(value) for _, value in metric_values]))
    else:
        # read metric values from the anomaly file
        metric_values = obtain_values_of_metrics(diag_id, [prometheus_metrics[metric_name]], -1, -1)
        
        if len(metric_values) > 0:
            metric_values = next(iter(metric_values.values()))
            is_abnormal = detect_anomalies(
                np.array(metric_values))
        else:
            is_abnormal = False


    # draw the metric chart
    chart_metric_values = [[i, str(value)] for i, value in metric_values]

    chart_content = generate_prometheus_chart_content(metric_name, chart_metric_values, x_label_format="%H:%M", size=(400, 225))

    with open(f"./alert_results/{current_diag_time}/{metric_name}.html", "w") as f:
        f.write(chart_content)

    if is_abnormal:
        # print(f"{metric_name} is abnormal")
        return f"The metric {metric_name} is abnormal \n " + f"[chart] ./alert_results/{current_diag_time}/{metric_name}.html"
    else:
        # print(f"{metric_name} is normal")
        return f"Cannot decide whether the metric {metric_name} is abnormal.\n" # + f"[chart] ./alert_results/{current_diag_time}/{metric_name}.html"
    

def match_diagnose_knowledge(
        start_time: int,
        end_time: int,
        metric_name: str = "cpu expert",
        alert_metric: str = "",
        diag_id: str = "",
        enable_prometheus: bool = True):

    agent_name = metric_name.lower()

    # alerts and metrics
    alert_and_metric_str, abnormal_metric_detailed_values = metric_analysis_results(agent_name, alert_metric, diag_id, enable_prometheus, start_time, end_time)
    
    if "network" in agent_name:
        return """The {} relevant metric values from Prometheus are:\n 
        {}""".format(agent_name,
            alert_and_metric_str)

    # slow queries
    slow_queries_str = slow_query_analysis_results(agent_name, diag_id)

    # workload
    workload_str = workload_analysis_results(agent_name, diag_id)
    
    
    knowledge_str = alert_and_metric_str + workload_str + slow_queries_str

    print(" == knowledge_str == ", knowledge_str)

    return knowledge_str, abnormal_metric_detailed_values