from multiagents.tools.metric_monitor.anomaly_detection import detect_anomalies
from prometheus_service.prometheus_abnormal_metric import prometheus_metrics
from multiagents.tools.metrics import *
from multiagents.utils.markdown_format import generate_prometheus_chart_content
from server.knowledge_base.kb_doc_api import search_docs


def metric_analysis_results(agent_name, alert_metric, diag_id, enable_prometheus, start_time, end_time):

    if "cpu" in agent_name or "workload" in agent_name or "index" in agent_name or "query" in agent_name:
        metric_prefix = "cpu"
    elif "write" in agent_name or "io" in agent_name:
        metric_prefix = "io"
    elif "mem" in agent_name or "write" in agent_name:
        metric_prefix = "memory"
    else:
        metric_prefix = "cpu"
    
    metrics_list = prometheus_metrics[f"{metric_prefix}_metrics"]    
    alert_metric_list = []
    alert_metric_list.append(alert_metric)
    if enable_prometheus == True:
        detailed_alert_metric = obtain_values_of_metrics(-1, 
            alert_metric_list, int(start_time), int(end_time))
        
        detailed_metrics = obtain_values_of_metrics(-1, 
            metrics_list, int(start_time), int(end_time))
    else:
        detailed_alert_metric = obtain_values_of_metrics(diag_id, 
            alert_metric_list, -1, 1)

        detailed_metrics = obtain_values_of_metrics(diag_id, 
            metrics_list, -1, 1)

    # identify the abnormal metrics
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

    if detailed_alert_metric != {} and detailed_alert_metric != None:
        for detailed_values in detailed_alert_metric.values():
            # draw the metric chart
            chart_metric_values = [[i, str(value)] for i, value in enumerate(detailed_values)]
            chart_content = generate_prometheus_chart_content(alert_metric, chart_metric_values, x_label_format="%H:%M", size=(400, 225))
            with open(f"./alert_results/{current_diag_time}/{alert_metric}.html", "w") as f:
                f.write(chart_content)
                        
            alert_metric_str = """The statistics of alert metric {} are:\n [chart] ./alert_results/{}/{}.html\n\n""".format(alert_metric, current_diag_time, alert_metric)
    else:
        alert_metric_str = ""

    metric_str = "The abnormal metrics are:\n"
    for i,metric_name in enumerate(top5_abnormal_metrics):

        if metric_name in detailed_metrics:
            metric_values = detailed_metrics[metric_name]

            # draw the metric chart
            chart_metric_values = [[i, str(value)] for i, value in enumerate(metric_values)]
            chart_content = generate_prometheus_chart_content(metric_name, chart_metric_values, x_label_format="%H:%M", size=(400, 225))
            with open(f"./alert_results/{current_diag_time}/{metric_name}.html", "w") as f:
                f.write(chart_content)
                    
            metric_str = metric_str + f"{i+1}. {metric_name} contains abnormal patterns: {top5_abnormal_metrics[metric_name]} \n [chart] ./alert_results/{current_diag_time}/{metric_name}.html \n"
    if top5_abnormal_metrics == {}:
        metric_str = ""
    else:
        metric_str = metric_str + "\n"

    docs_query = [metric_name for metric_name in top5_abnormal_metrics]
    matched_docs = search_docs(str(docs_query), knowledge_base_name=str(agent_name.split(" ")[0]), top_k=2, score_threshold=0.3)

    docs_str = ""
    if matched_docs != []:
        matched_docs_str = ""
        for i, matched_doc in enumerate(matched_docs):
            matched_docs_str = matched_docs_str + f"{i+1}. {matched_doc.metadata['content']} \n"

        docs_str = """The matched knowledge for analyzing above abnormal metrics is:\n{}\n\n""".format(matched_docs_str)

    return alert_metric_str + metric_str + docs_str, abnormal_metric_detailed_values

    # if metric_prefix == "cpu":
    #     docs_str = cpu_knowledge_matcher.match(top5_abnormal_metrics)
    # elif metric_prefix == "io":
    #     docs_str = io_knowledge_matcher.match(top5_abnormal_metrics)
    # elif metric_prefix == "memory":
    #     docs_str = memory_knowledge_matcher.match(top5_abnormal_metrics)
    # elif metric_prefix == "workload":
    #     docs_str = workload_knowledge_matcher.match(top5_abnormal_metrics)
    # elif metric_prefix == "index":
    #     docs_str = index_knowledge_matcher.match(top5_abnormal_metrics)
    # elif metric_prefix == "query":
    #     docs_str = query_knowledge_matcher.match(top5_abnormal_metrics)
    # elif metric_prefix == "write":
    #     docs_str = write_knowledge_matcher.match(top5_abnormal_metrics)
    # elif metric_prefix == "configuration":
    #     docs_str = configuration_knowledge_matcher.match(top5_abnormal_metrics)
    # else:
    #     docs_str = ""


def workload_analysis_results(agent_name, diag_id):

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

    # cache_kb = KBServiceFactory.get_service("cache", SupportedVSType.CHROMADB)
    # docs = cache_kb.search_docs(top5_abnormal_metrics, top_k=5)

    if workload_state != "":
        workload_str = """The workload queries are:\n{}\n\n""".format(workload_state)

        matched_docs = search_docs("workload", knowledge_base_name=str(agent_name.split(" ")[0]), top_k=2, score_threshold=0.3)

        if matched_docs != []:
            docs_str = """The matched knowledge for analyzing above workload queries is:\n{}\n\n""".format(str(matched_docs))
            
            workload_str = workload_str + docs_str
    else:
        workload_str = ""

    return workload_str


def slow_query_analysis_results(agent_name, diag_id):

    # get the slow queries from the anomaly file
    slow_queries = get_slow_queries(diag_id)
    if not isinstance(slow_queries, list):
        slow_queries = []

    if slow_queries != []:
        # concate the sqls in the dict slow_queries into a string
        
        # concat_slow_queries = "\n".join([f'\t {i+1}. the slow query comes from {sql["dbname"]} database, takes {sql["execution_time"]} seconds, and its statement is "{sql["sql"]}"' for i, sql in enumerate(slow_queries)])

        concat_slow_queries = "\n".join([f'{i+1}. The slow query statement is "{sql}"' for i, sql in enumerate(slow_queries)])

        slow_queries_str = """The slow queries that should be optimized are:\n{}\n\n""".format(concat_slow_queries)


        matched_docs = search_docs("slow query", knowledge_base_name=str(agent_name.split(" ")[0]), top_k=2, score_threshold=0.3)

        if matched_docs != []:
            docs_str = """The matched knowledge for analyzing above slow queries is:
        {}\n\n""".format(str(matched_docs))

            slow_queries_str = slow_queries_str + docs_str
        else:
            slow_queries_str = ""
    else:
        slow_queries_str = ""

    return slow_queries_str