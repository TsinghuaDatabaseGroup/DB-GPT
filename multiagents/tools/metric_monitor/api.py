import numpy as np
import ast

from multiagents.tools.metric_monitor.anomaly_detection import prometheus
from multiagents.tools.metric_monitor.anomaly_detection import detect_anomalies
from multiagents.tools.metrics import prometheus_metrics, postgresql_conf, obtain_values_of_metrics, processed_values
from multiagents.tools.metrics import current_diag_time, diag_start_time, diag_end_time
from multiagents.tools.metrics import get_workload_statistics, get_slow_queries, get_workload_sqls
from multiagents.tools.metrics import knowledge_matcher
from utils.markdown_format import generate_prometheus_chart_content
from multiagents.tools.index_advisor.api import optimize_index_selection


def obtain_start_and_end_time_of_anomaly(input: str = 'json dict string'):
    return {"start_time": diag_start_time, "end_time": diag_end_time}


def whether_is_abnormal_metric(
        start_time: int,
        end_time: int,
        metric_name: str = "cpu_usage"):

    if metric_name not in prometheus_metrics:
        # print(f"{metric_name} is unknown")
        return f"The metric {metric_name} is unknown \n {metric_name}"

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

    # draw the metric chart
    chart_metric_values = [[i, str(value)] for i, value in metric_values]

    chart_content = generate_prometheus_chart_content(metric_name, chart_metric_values, x_label_format="%H:%M", size=(400, 225))
    with open(f"./alert_results/{current_diag_time}/{metric_name}.html", "w") as f:
        f.write(chart_content)

    is_abnormal = detect_anomalies(
        np.array([float(value) for _, value in metric_values]))

    if is_abnormal:
        # print(f"{metric_name} is abnormal")
        return f"The metric {metric_name} is abnormal \n " + f"[chart] ./alert_results/{current_diag_time}/{metric_name}.html"
    else:
        # print(f"{metric_name} is normal")
        return f"The metric {metric_name} is normal \n " + f"[chart] ./alert_results/{current_diag_time}/{metric_name}.html"
    

def match_diagnose_knowledge(
        start_time: int,
        end_time: int,
        metric_name: str = "cpu",
        alert_metric: str = "",
        diag_id: str = ""):

    slow_queries = get_slow_queries(diag_id)

    if not isinstance(slow_queries, list):
        slow_queries = []

    # if slow_queries != [] and slow_queries != "[]" and slow_queries != "":
    #     try:

    #         slow_queries = ast.literal_eval(slow_queries)
    #     except:
    #         print("fail to parse slow queries:", slow_queries)
    #         slow_queries = []
    # else:
    #     slow_queries = []

    if "cpu" in metric_name.lower():
        metric_prefix = "cpu"
    elif "io" in metric_name.lower():
        metric_prefix = "io"
    elif "mem" in metric_name.lower():
        metric_prefix = "memory"
    else:
        metric_prefix = "network"

    metrics_list = prometheus_metrics[f"{metric_prefix}_metrics"]
    
    alert_metric_list = []
    alert_metric_list.append(alert_metric)
    detailed_alert_metric = obtain_values_of_metrics(
        int(start_time), int(end_time), alert_metric_list)

    detailed_metrics = obtain_values_of_metrics(
        int(start_time), int(end_time), metrics_list)
    
    # identify the abnormal metrics
    # detailed_abnormal_metrics = {}
    top5_abnormal_metrics = {}
    top5_abnormal_metrics_map = {}
    
    for metric_name, metric_values in detailed_metrics.items():
        anomaly_value, is_abnormal = detect_anomalies(np.array(metric_values))
        if is_abnormal:
            # maintain the top 5 abnormal metrics
            if len(top5_abnormal_metrics) < 5:
                top5_abnormal_metrics[metric_name] = processed_values(metric_values)
                top5_abnormal_metrics_map[metric_name] = anomaly_value
                # sort top5_abnormal_metrics_map by keys in descending order
            else:
                # identify the min value of top5_abnormal_metrics_map together with the key
                min_abnormal_value = min(top5_abnormal_metrics_map.values())
                # identify the key of min_abnormal_value
                min_abnormal_value_key = list(top5_abnormal_metrics_map.keys())[list(top5_abnormal_metrics_map.values()).index(min_abnormal_value)]

                if anomaly_value > min_abnormal_value:

                    top5_abnormal_metrics[metric_name] = processed_values(metric_values) # convert time-series data into feature values

                    top5_abnormal_metrics.pop(min_abnormal_value_key)
                    top5_abnormal_metrics_map.pop(min_abnormal_value_key)
    
    abnormal_metric_detailed_values = []
    for metric_name in top5_abnormal_metrics:
        new_metric_name = metric_name.replace("irate(", "")
        metric_chart_data = {"values": detailed_metrics[metric_name], "title": f"{new_metric_name} (for {metric_prefix} expert)", "type": "line"}

        abnormal_metric_detailed_values.append(metric_chart_data)

    metric_str = ""

    for i,metric_name in enumerate(top5_abnormal_metrics):

        if metric_name in detailed_metrics:
            metric_values = detailed_metrics[metric_name]

            # draw the metric chart
            chart_metric_values = [[i, str(value)] for i, value in enumerate(metric_values)]
            chart_content = generate_prometheus_chart_content(metric_name, chart_metric_values, x_label_format="%H:%M", size=(400, 225))
            with open(f"./alert_results/{current_diag_time}/{metric_name}.html", "w") as f:
                f.write(chart_content)

            metric_str = metric_str + f"{i+1}. {metric_name} contains abnormal patterns: {top5_abnormal_metrics[metric_name]} \n [chart] ./alert_results/{current_diag_time}/{metric_name}.html \n"

    if metric_prefix == "network":
        
        return """The {} relevant metric values from Prometheus are:\n 
        {}""".format(metric_prefix,
            metric_str)

    workload_state = get_workload_sqls(diag_id)

    # if workload_statistics != "[]" and workload_statistics != "":
    #     workload_statistics = ast.literal_eval(workload_statistics)
    # else:
    #     workload_statistics = []

    # workload_state = ""

    # for i, query in enumerate(workload_statistics):
    #     # workload_state += str(i + 1) + '. ' + str(query) + "\n"
    #     if isinstance(query["total_time"], str):
    #         query["total_time"] = float(query["total_time"])

    #     query["total_time"] = "{:.2f}".format(query["total_time"])
    #     query["sql"] = query["sql"].replace("\n", " ")
    #     query["sql"] = query["sql"].replace("\t", " ")

    #     workload_state += '\t' + str(i + 1) + '. ' + f'the query template comes from {query["dbname"]} database, is used for {query["calls"]} times, takes {query["total_time"]} seconds, and its statement is "{query["sql"]}"' + "\n"
    
    # matching_metrics = {**detailed_abnormal_metrics}
    
    docs_str = knowledge_matcher.match(top5_abnormal_metrics)

    if detailed_alert_metric != {} and detailed_alert_metric != None:
        for detailed_values in detailed_alert_metric.values():
            # draw the metric chart
            chart_metric_values = [[i, str(value)] for i, value in enumerate(detailed_values)]
            chart_content = generate_prometheus_chart_content(alert_metric, chart_metric_values, x_label_format="%H:%M", size=(400, 225))
            with open(f"./alert_results/{current_diag_time}/{alert_metric}.html", "w") as f:
                f.write(chart_content)
                        
            alert_metric_str = """The statistics of alert metric {} are:\n [chart] ./alert_results/{}/{}.html \n""".format(alert_metric, current_diag_time, alert_metric)
    else:
        alert_metric_str = ""

    if workload_state != "":
        workload_str = """The workload queries are:
        {}
        
        """.format(workload_state)
    else:
        workload_str = ""

    if slow_queries != []:
        # concate the sqls in the dict slow_queries into a string
        
        #concat_slow_queries = "\n".join([f'\t {i+1}. the slow query comes from {sql["dbname"]} database, takes {sql["execution_time"]} seconds, and its statement is "{sql["sql"]}"' for i, sql in enumerate(slow_queries)])

        concat_slow_queries = "\n".join([f'\t {i+1}. The slow query statement is "{sql}"' for i, sql in enumerate(slow_queries)])

        slow_queries_str = """The slow queries that should be optimized are:
    {}
        
""".format(concat_slow_queries)
    else:
        slow_queries_str = ""

    if docs_str:
        docs_str = """The matched knowledge is:
    {}
""".format(docs_str)

    knowledge_str= alert_metric_str + metric_str + workload_str + slow_queries_str + docs_str
    # knowledge_str= alert_metric_str + metric_str + workload_str + slow_queries_str # no_knowledge

    return knowledge_str, abnormal_metric_detailed_values