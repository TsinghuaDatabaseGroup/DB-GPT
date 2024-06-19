import logging
from multiagents.tools.metric_monitor.anomaly_detection import detect_anomalies
from multiagents.tools.metrics import *
from multiagents.tools.metric_monitor.anomaly_analysis import (
    metric_analysis_results,
    slow_query_analysis_results,
    workload_analysis_results
)
from multiagents.utils.markdown_format import generate_prometheus_chart_content
from prometheus_service_docker.prometheus_abnormal_metric import prometheus_metrics
from server.knowledge_base.kb_doc_api import search_docs, fetch_expert_kb_names
from multiagents.initialization import LANGUAGE

FUNCTION_DEFINITION = {
    "whether_is_abnormal_metric": {
        "name": "whether_is_abnormal_metric",
        "description": "检测是否存在异常指标。" if LANGUAGE == "zh"
        else "detect if there is an abnormal metric.",
        "parameters": {'type': 'object', 'properties': {}}
    },
    "match_diagnose_knowledge": {
        "name": "match_diagnose_knowledge",
        "description": "在诊断知识库中搜索相关的故障诊断知识。" if LANGUAGE == "zh"
        else "search the relevant diagnosis knowledge from diagnosis knowledge base.",
        "parameters": {'type': 'object', 'properties': {}}
    }
}

# can be removed
def whether_is_abnormal_metric(
        start_time: int,
        end_time: int,
        metric_name: str = "cpu_usage",
        diag_id: str = "",
        enable_prometheus: bool = True):
    if metric_name not in prometheus_metrics:
        # print(f"{metric_name} is unknown")
        return f"The metric {metric_name} is unknown \n {metric_name}"

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

    chart_content = generate_prometheus_chart_content(metric_name, chart_metric_values, x_label_format="%H:%M",
                                                      size=(400, 225))

    with open(f"./alert_results/{current_diag_time}/{metric_name}.html", "w") as f:
        f.write(chart_content)

    if is_abnormal:
        # print(f"{metric_name} is abnormal")
        result_str = f"指标{metric_name}是异常的。\n" if LANGUAGE == "zh" else f"The metric {metric_name} is abnormal \n "
        return result_str + f"[chart] ./alert_results/{current_diag_time}/{metric_name}.html"
    else:
        # print(f"{metric_name} is normal")
        return f"无法判断指标{metric_name}是否异常。\n" if LANGUAGE == "zh" \
            else f"Cannot decide whether the metric {metric_name} is abnormal.\n"  # + f"[chart] ./alert_results/{current_diag_time}/{metric_name}.html"


def match_diagnose_knowledge(
        start_time: int,
        end_time: int,
        metric_name: str = "CpuExpert",
        alert_metric: str = "",
        diag_id: str = "",
        enable_prometheus: bool = True):
    agent_name = metric_name.lower()

    candidate_agent_name = str(agent_name.split(" ")[0])
    expert_names = fetch_expert_kb_names()
    kb_name = ""
    for expert_name in expert_names:
        if candidate_agent_name in expert_name.lower():
            kb_name = expert_name
            break
    if kb_name == "":
        logging.error(f"The expert name {candidate_agent_name} is not found in knowledge base!")

    # alerts and metrics
    alert_and_metric_str, abnormal_metric_detailed_values, metrc_knowledge_list = metric_analysis_results(agent_name, kb_name, alert_metric, diag_id, enable_prometheus, start_time, end_time)

    if "network" in agent_name:
        if LANGUAGE == "zh":
            return f"从Prometheus中查找到的与{agent_name}相关的指标是：\n {alert_and_metric_str}"
        else:
            return f"The {agent_name} relevant metric values from Prometheus are:\n {alert_and_metric_str}"

    # slow queries
    slow_queries_str, slow_query_knowledge_list = slow_query_analysis_results(agent_name, kb_name, diag_id)

    # workload
    workload_str, workload_knowledge_list = workload_analysis_results(agent_name, kb_name, diag_id)

    knowledge_str = alert_and_metric_str + workload_str + slow_queries_str
    knowledge_list = metrc_knowledge_list + workload_knowledge_list + slow_query_knowledge_list

    # print(" == knowledge_str == ", knowledge_str)

    return knowledge_str, abnormal_metric_detailed_values, knowledge_list
