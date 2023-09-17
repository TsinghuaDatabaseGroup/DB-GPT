import numpy as np
from multiagents.knowledge.knowledge_extraction import KnowledgeExtraction
from multiagents.utils.database import DBArgs, Database
from multiagents.tools.metric_monitor.anomaly_detection import prometheus
from multiagents.tools.metric_monitor.anomaly_detection import detect_anomalies
from multiagents.tools.metrics import prometheus_metrics, postgresql_conf, obtain_values_of_metrics, processed_values
import pdb

def obtain_start_and_end_time_of_anomaly(input: str = 'json dict string'):

    # 读取根目录./diag_time.txt文件，获取最后一行异常时间段
    with open("./diag_time.txt", 'r') as f:
        last_line = f.readlines()[-1].replace("\n", "")
        print("-----------last_line: ", last_line)
        diag_start_time = last_line.split('-')[0]
        diag_end_time = last_line.split('-')[1]
    print("diag_start_time: ", diag_start_time)
    print("diag_end_time: ", diag_end_time)

    if not diag_start_time or not diag_end_time:
        raise Exception("No start and end time of anomaly!")
    
    return {"start_time": diag_start_time, "end_time": diag_end_time}

def whether_is_abnormal_metric(
        start_time: int,
        end_time: int,
        metric_name: str = "cpu_usage"):

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

    if is_abnormal:
        print(f"{metric_name} is abnormal")
        return "The metric is abnormal"
    else:
        print(f"{metric_name} is normal")
        return "The metric is normal"
    

def match_diagnose_knowledge(
        start_time: int,
        end_time: int,
        metric_name: str = "cpu"):

    dbargs = DBArgs("postgresql", config=postgresql_conf) # todo switch databases
    db = Database(dbargs, timeout=-1)
    knowledge_matcher = KnowledgeExtraction(
        "/multiagents/knowledge/root_causes_dbmind.jsonl")

    if "cpu" in metric_name:
        metric_prefix = "cpu"
    elif "io" in metric_name:
        metric_prefix = "io"
    elif "mem" in metric_name:
        metric_prefix = "memory"
    else:
        metric_prefix = "network"

    metrics_list = prometheus_metrics[f"{metric_prefix}_metrics"]

    detailed_metrics = obtain_values_of_metrics(
        start_time, end_time, metrics_list)
    
    # identify the abnormal metrics
    detailed_abnormal_metrics = {}

    for metric_name, metric_values in detailed_metrics.items():
        if detect_anomalies(np.array(metric_values)):
            detailed_abnormal_metrics[metric_name] = processed_values(metric_values)

    if metric_prefix == "network":
        
        return """The {} relevant metric values from Prometheus are: 
        {}""".format(metric_prefix,
            detailed_abnormal_metrics)
    
    slow_queries = db.obtain_historical_slow_queries()

    slow_query_state = ""
    for i, query in enumerate(slow_queries):
        # slow_query_state += str(i + 1) + '. ' + str(query) + "\n"
        query["total_time"] = "{:.2f}".format(query["total_time"])
        query["sql"] = query["sql"].replace("\n", " ")
        query["sql"] = query["sql"].replace("\t", " ")

        slow_query_state += '\t' + str(i + 1) + '. ' + f'the query comes from {query["dbname"]} database, is used for {query["calls"]} times, takes {query["total_time"]} seconds, and its statement is "{query["sql"]}"' + "\n"
    
    docs_str = knowledge_matcher.match(detailed_abnormal_metrics)

    knowledge_str=  \
"""The {} metric values are: 
    {} 
    
The slow queries are:
{}

The matched knowledge is:
    {}""".format(metric_prefix,
        detailed_abnormal_metrics,
        slow_query_state,
        docs_str)


    return knowledge_str