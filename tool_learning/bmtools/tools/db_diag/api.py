import json
import os
import requests
import numpy as np
import openai
import paramiko

import sys
sys.path.append(".")

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
from nltk.tokenize import word_tokenize
import nltk

from ..tool import Tool
from bmtools.tools.db_diag.utils.db_parser import get_conf
from bmtools.tools.db_diag.utils.database import DBArgs, Database
# from bmtools.models.customllm import CustomLLM
from bmtools.knowledge.knowledge_extraction import KnowledgeExtraction
from bmtools.tools.db_diag.anomaly_detection import detect_anomalies
from bmtools.tools.db_diag.anomaly_detection import prometheus

from termcolor import colored
import pdb

import configparser
from .optimization_tools.index_selection.selection_utils import selec_com
from .optimization_tools.index_selection.selection_utils.workload import Workload
from .optimization_tools.index_selection.selection_algorithms.extend_algorithm import ExtendAlgorithm
from .optimization_tools.index_selection.selection_utils.postgres_dbms import PostgresDatabaseConnector

import warnings

def obtain_values_of_metrics(start_time, end_time, metrics):

    if end_time - start_time > 11000*3:     # maximum resolution of 11,000 points per timeseries
        #raise Exception("The time range is too large, please reduce the time range")
        warnings.warn("The time range ({}, {}) is too large, please reduce the time range".format(start_time, end_time))

    required_values = {}

    print(" ====> metrics: ", metrics)
    for metric in metrics:
        metric_values = prometheus('api/v1/query_range', {'query': metric, 'start': start_time, 'end': end_time, 'step': '3'})
        if metric_values["data"]["result"] != []:
            metric_values = metric_values["data"]["result"][0]["values"]
        else:
            raise Exception("No metric values found for the given time range")

        # compute the average value of the metric
        max_value = np.max(np.array([float(value) for _, value in metric_values]))

        required_values[metric] = max_value

    return required_values

def find_abnormal_metrics(start_time, end_time, monitoring_metrics, resource):

    resource_keys = ["memory", "cpu", "disk", "network"]

    abnormal_metrics = []
    for metric_name in monitoring_metrics:

        interval_time = 5
        metric_values = prometheus('api/v1/query_range', {'query': metric_name, 'start': start_time-interval_time*60, 'end': end_time+interval_time*60, 'step': '3'})

        if metric_values["data"]["result"] != []:
            metric_values = metric_values["data"]["result"][0]["values"]
        else:
            continue

        if detect_anomalies(np.array([float(value) for _, value in metric_values])):
            
            success = True
            for key in resource_keys:
                if key in metric_name and key != resource:
                    success = False
                    break
            if success:
                abnormal_metrics.append(metric_name)

    return abnormal_metrics


INDEX_SELECTION_ALGORITHMS = {
    "extend": ExtendAlgorithm,
}

def get_index_result(algo, work_list, connector, columns,
                        sel_params="parameters", process=False, overhead=False):
    
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)

    exp_conf_file = script_dir + f"/optimization_tools/index_selection/selection_data/algo_conf/{algo}_config.json"
    with open(exp_conf_file, "r") as rf:
        exp_config = json.load(rf)

    data = list()
    config = selec_com.find_parameter_list(exp_config["algorithms"][0],
                                            params=sel_params)[0]
    
    workload = Workload(selec_com.read_row_query(work_list, exp_config,
                                                    columns, type=""))
    connector.drop_hypo_indexes()

    algorithm = INDEX_SELECTION_ALGORITHMS[algo](
        connector, config["parameters"], process)

    indexes = algorithm.calculate_best_indexes(
        workload, overhead=overhead)

    indexes = indexes[0]

    if indexes == []:
        return [], -1, -1
    

    indexes = [str(ind) for ind in indexes]
    cols = [ind.split(",") for ind in indexes]
    cols = [list(map(lambda x: x.split(".")[-1], col)) for col in cols]
    indexes = [
        f"{ind.split('.')[0]}#{','.join(col)}" for ind, col in zip(indexes, cols)]

    no_cost, ind_cost = list(), list()
    total_no_cost, total_ind_cost = 0, 0
    for sql in work_list:
        no_cost_ = connector.get_ind_cost(sql, "")
        total_no_cost += no_cost_
        no_cost.append(no_cost_)

        ind_cost_ = connector.get_ind_cost(sql, indexes)
        total_ind_cost += ind_cost_
        ind_cost.append(ind_cost_)

    # pdb.set_trace()

    return indexes, total_no_cost, total_ind_cost


def build_db_diag_tool(config) -> Tool:
    tool = Tool(
        "Database Diagnosis",
        "Diagnose the bottlenecks of a database based on relevant metrics",
        name_for_model="db_diag",
        description_for_model="Plugin for diagnosing the bottlenecks of a database based on relevant metrics",
        logo_url="https://commons.wikimedia.org/wiki/File:Postgresql_elephant.svg",
        contact_email="hello@contact.com",
        legal_info_url="hello@legal.com"
    )

    #URL_CURRENT_WEATHER= "http://api.weatherapi.com/v1/current.json"
    #URL_FORECAST_WEATHER = "http://api.weatherapi.com/v1/forecast.json"

    URL_PROMETHEUS = 'http://8.131.229.55:9090/'
    prometheus_metrics = {#"cpu_usage": "avg(rate(process_cpu_seconds_total{instance=\"172.27.58.65:9187\"}[5m]) * 1000)", 
                          "cpu_usage" : '(avg(irate(node_cpu_seconds_total{instance=~"172.27.58.65:9100",mode="user"}[1m]))) * 100',
                          "cpu_metrics": ["node_scrape_collector_duration_seconds{instance=\"172.27.58.65:9100\"}", "node_procs_running{instance=\"172.27.58.65:9100\"}", "node_procs_blocked{instance=\"172.27.58.65:9100\"}", "node_entropy_available_bits{instance=\"172.27.58.65:9100\"}", "node_load1{instance=\"172.27.58.65:9100\"}", "node_load5{instance=\"172.27.58.65:9100\"}", "node_load15{instance=\"172.27.58.65:9100\"}"], 
                          "memory_usage": "node_memory_MemTotal_bytes{instance=~\"172.27.58.65:9100\"} - (node_memory_Cached_bytes{instance=~\"172.27.58.65:9100\"} + node_memory_Buffers_bytes{instance=~\"172.27.58.65:9100\"} + node_memory_MemFree_bytes{instance=~\"172.27.58.65:9100\"})",
                          "memory_metrics": ["irate(node_disk_write_time_seconds_total{instance=~\"172.27.58.65:9100\"}[1m])", "node_memory_Inactive_anon_bytes{instance=\"172.27.58.65:9100\"}", "node_memory_MemFree_bytes{instance=\"172.27.58.65:9100\"}", "node_memory_Dirty_bytes{instance=\"172.27.58.65:9100\"}", "pg_stat_activity_count{datname=~\"(imdbload|postgres|sysbench|template0|template1|tpcc|tpch)\", instance=~\"172.27.58.65:9187\", state=\"active\"} !=0"],
                          "network_metrics": ["node_sockstat_TCP_tw{instance=\"172.27.58.65:9100\"}", "node_sockstat_TCP_orphan{instance=\"172.27.58.65:9100\"}"]}
    # "node_sockstat_TCP_tw{instance=\"172.27.58.65:9100\"}", 

    executor_url = "http://8.131.229.55:5114/rewrite/single_rule"

    # load knowlege extractor
    knowledge_matcher = KnowledgeExtraction("/bmtools/tools/db_diag/root_causes_dbmind.jsonl")

    # load db settings
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    script_dir = os.path.dirname(script_dir)
    config = get_conf(script_dir + '/my_config.ini', 'postgresql')
    dbargs = DBArgs("postgresql", config=config)  # todo assign database name
    db = Database(dbargs, timeout=-1)

    server_config = get_conf(script_dir + '/my_config.ini', 'benchserver')

    monitoring_metrics = []
    with open(str(os.getcwd()) + "/bmtools/tools/db_diag/database_monitoring_metrics", 'r') as f:
        monitoring_metrics = f.read()
    monitoring_metrics = eval(monitoring_metrics)

    @tool.get("/obtain_start_and_end_time_of_anomaly")
    def obtain_start_and_end_time_of_anomaly():

        # 读取tool_learning/bmtools/diag_time.txt文件，获取最后一行异常时间段
        with open(str(os.getcwd()) + "/bmtools/diag_time.txt", 'r') as f:
            last_line = f.readlines()[-1].replace("\n", "")
            print("-----------last_line: ", last_line)
            diag_start_time = last_line.split('-')[0]
            diag_end_time = last_line.split('-')[1]
        print("diag_start_time: ", diag_start_time)
        print("diag_end_time: ", diag_end_time)
        if not diag_start_time or not diag_end_time:
            raise Exception("No start and end time of anomaly!")
        return {"start_time": diag_start_time, "end_time": diag_end_time}

        '''
        If the anomaly period is recorded on the server side, you can use the following code to obtain the start and end time of the anomaly.q
        '''

        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        start_time = 0
        end_time = 0

        try:
            # Connect to the remote server
            ssh.connect(server_config["server_address"], username=server_config["username"], password=server_config["password"])

            # Create an SFTP client
            sftp = ssh.open_sftp()

            # Change to the remote directory
            sftp.chdir(server_config["remote_directory"])

            # Get a list of files in the directory
            files = sftp.listdir()

            required_file_name = ""
            required_tp = -1
            # Read the contents of each file
            for filename in files:
                remote_filepath = server_config["remote_directory"] + '/' + filename

                if "trigger_time_log" not in filename:
                    continue
                
                tp = filename.split("_")[0]
                
                if tp.isdigit():
                    tp = int(tp)
                    if required_tp < tp:
                        required_tp = tp
                        required_file_name = filename
                        
            file_content = sftp.open(server_config["remote_directory"] + '/' + required_file_name).read()
            file_content = file_content.decode()
            tps = file_content.split("\n")[0]
            start_time = tps.split(";")[0]
            end_time = tps.split(";")[1]

        finally:
            # Close the SFTP session and SSH connection
            sftp.close()
            ssh.close()

        return {"start_time": start_time, "end_time": end_time}

    @tool.get("/whether_is_abnormal_metric")
    def whether_is_abnormal_metric(start_time:int, end_time:int, metric_name : str="cpu_usage"):

        interval_time = 5
        metric_values = prometheus('api/v1/query_range', {'query': prometheus_metrics[metric_name], 'start': start_time, 'end': end_time, 'step': '3'})
        # prometheus('api/v1/query_range', {'query': '100 - (avg(irate(node_cpu_seconds_total{instance=~"172.27.58.65:9100",mode="idle"}[1m])) * 100)', 'start': '1684412385', 'end': '1684413285', 'step': '3'})
        # print(" === metric_values", metric_values)

        # pdb.set_trace()

        if metric_values["data"]["result"] != []:
            metric_values = metric_values["data"]["result"][0]["values"]
        else:
            raise Exception("No metric values found for the given time range")

        is_abnormal = detect_anomalies(np.array([float(value) for _, value in metric_values]))

        if is_abnormal:
            return "The metric is abnormal"
        else:
            return "The metric is normal"


    @tool.get("/cpu_diagnosis_agent")
    def cpu_diagnosis_agent(start_time : int, end_time : int):

        # live_tuples\n- dead_tuples\n- table_size

        cpu_metrics = prometheus_metrics["cpu_metrics"]
        cpu_metrics = cpu_metrics # + find_abnormal_metrics(start_time, end_time, monitoring_metrics, 'cpu')

        print("==== cpu_metrics", cpu_metrics)


        detailed_cpu_metrics = obtain_values_of_metrics(start_time, end_time, cpu_metrics)

        openai.api_key = os.environ["OPENAI_API_KEY"]

        db = Database(dbargs, timeout=-1)
        slow_queries = db.obtain_historical_slow_queries()

        slow_query_state = ""
        for i,query in enumerate(slow_queries):
            slow_query_state += str(i+1) + '. ' + str(query) + "\n"

        print(slow_query_state)

        docs_str = knowledge_matcher.match(detailed_cpu_metrics)

        prompt = """The CPU metric is abnormal. Then obtain the CPU relevant metric values from Prometheus: {}. The slow queries are:
        {}

Next output the analysis of potential causes of the high CPU usage based on the CPU relevant metric values,

Note: include the important slow queries in the output, but not all queries.
{}""".format(detailed_cpu_metrics, slow_query_state, docs_str)

        print(prompt)

        # pdb.set_trace()
        
        # response = openai.Completion.create(
        # model="text-davinci-003",
        # prompt=prompt,
        # temperature=0,
        # max_tokens=1000,
        # top_p=1.0,
        # frequency_penalty=0.0,
        # presence_penalty=0.0,
        # stop=["#", ";"]
        # )
        # output_text = response.choices[0].text.strip()

        # Set up the OpenAI GPT-3 model
        # model_engine = "gpt-3.5-turbo"

        # prompt_response = openai.ChatCompletion.create(
        #     engine="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "assistant", "content": "The table schema is as follows: " + str(schema)},
        #         {"role": "user", "content": str(prompt)}
        #         ]
        # )
        # output_text = prompt_response['choices'][0]['message']['content']

        prompt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": str(prompt)}
            ]
        )

        output_analysis = prompt_response['choices'][0]['message']['content']

        # llm = CustomLLM()
        # output_analysis = llm(prompt)

        return {"diagnose": output_analysis, "knowledge": docs_str}

    @tool.get("/memory_diagnosis_agent")
    def memory_diagnosis_agent(start_time : int, end_time : int):

        memory_metrics = prometheus_metrics["memory_metrics"]

        memory_metrics = prometheus_metrics["memory_metrics"]
        memory_metrics = memory_metrics # + find_abnormal_metrics(start_time, end_time, monitoring_metrics, 'memory')

        detailed_memory_metrics = obtain_values_of_metrics(start_time, end_time, memory_metrics)

        # print with color red
        # print(colored("==== detailed_memory_metrics", "red"), detailed_memory_metrics)

        openai.api_key = os.environ["OPENAI_API_KEY"]

        db = Database(dbargs, timeout=-1)
        slow_queries = db.obtain_historical_slow_queries()

        slow_query_state = ""
        for i,query in enumerate(slow_queries):
            slow_query_state += str(i+1) + '. ' + str(query) + "\n"

        print(slow_query_state)
        
        # TODO: need a similarity match function to match the top-K examples
        # 1. get the categories of incoming metrics. Such as "The abnormal metrics include A, B, C, D"
        # 2. embedding the metrics
        # note: 这个metrics的embedding有可能预计算吗？如果metrics的种类（组合数）有限的话
        # 3. match the top-K examples(embedding)
        # note: 不用embedding如何有效的筛选出来与当前metrics最相关的example呢？可以枚举吗？比如如果我知道某一个example涉及到哪些metrics？
        #       该如何判断某一个metrics跟一段文本是相关的呢？能否用一个模型来判断一段文本涉及到哪些metrics呢？重新训练的话感觉需要很多样本才行
        #       能不能用关键词数量？

        docs_str = knowledge_matcher.match(detailed_memory_metrics)

        prompt = """The memory metric is abnormal. Then obtain the memory metric values from Prometheus: {}. The slow queries are:
        {}
        
Output the analysis of potential causes of the high memory usage based on the memory metric values and slow queries, e.g., 

{}

Note: include the important slow queries in the output.
""".format(detailed_memory_metrics, slow_query_state, docs_str)

        print(prompt)

        # response = openai.Completion.create(
        # model="text-davinci-003",
        # prompt=prompt,
        # temperature=0,
        # max_tokens=1000,
        # top_p=1.0,
        # frequency_penalty=0.0,
        # presence_penalty=0.0,
        # stop=["#", ";"]
        # )
        # output_text = response.choices[0].text.strip()

        # Set up the OpenAI GPT-3 model
        # model_engine = "gpt-3.5-turbo"

        # prompt_response = openai.ChatCompletion.create(
        #     engine="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "assistant", "content": "The table schema is as follows: " + str(schema)},
        #         {"role": "user", "content": str(prompt)}
        #         ]
        # )
        # output_text = prompt_response['choices'][0]['message']['content']

        prompt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": str(prompt)}
            ]
        )

        output_analysis = prompt_response['choices'][0]['message']['content']

        # llm = CustomLLM()
        # output_analysis = llm(prompt)

        return {"diagnose": output_analysis, "knowledge": docs_str}


    @tool.get("/optimize_index_selection")
    def optimize_index_selection(start_time : int, end_time : int):
        """optimize_index_selection(start_time : int, end_time : int) returns the recommended index by running the algorithm 'Extend'. 
           This method uses a recursive algorithm that considers only a limited subset of index candidates.
           The method exploits structures and properties that are typical for real-world workloads and the performance of indexes.
           It identifies beneficial indexes and does not construct similar indexes.
           The recursion only realizes index selections/extensions with significant additional performance per size ratio.

           The following is an example:
           Thoughts: I will use the \\\'optimize_index_selection\\\' command to recommend the index for the given workload.
           Reasoning: I need to recommend the effective index for the given workload. I will use the \\\'optimize_index_selection\\\' command to get the index from 'Extend' and return the result.
           Plan: - Use the \\\'optimize_index_selection\\\' command to get the index. 
           Command: {"name": "optimize_index_selection", 
                     "args": {"workload": "SELECT A.col1 from A join B where A.col2 = B.col2 and B.col3 > 2 group by A.col1"}}
           Result: Command optimize_index_selection returned: "A#col2; B#col2,col3"
        """
        algo = "extend"
        dbname = "imdbload"
        sel_params = "parameters"
        process, overhead = True, True
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        script_dir = os.path.dirname(script_dir)
        config = get_conf(script_dir + '/my_config.ini', 'postgresql')
        schema_file = script_dir + f"/optimization_tools/index_selection/selection_data/data_info/schema_job.json"
        workload_file = script_dir + f"/optimization_tools/index_selection/selection_data/data_info/job_templates.sql"

        tables, columns = selec_com.get_columns_from_schema(schema_file)

        # load db settings
        db_config = {}
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        script_dir = os.path.dirname(script_dir)

        config = get_conf(script_dir + '/my_config.ini', 'postgresql')
        db_config["postgresql"] = config
        db_config["postgresql"]["dbname"] = dbname
        connector = PostgresDatabaseConnector(db_config, autocommit=True)

        workload = []
        with open(workload_file, "r") as rf:
            for line in rf.readlines():
                workload.append(line.strip())

        indexes, total_no_cost, total_ind_cost = get_index_result(algo, workload, connector,
                                                              columns, sel_params=sel_params,
                                                              process=process, overhead=overhead)

        if indexes == []:
            return "No beneficial single-column indexes can be found!"

        return f"The recommended indexes are: {indexes}, which reduces cost from {total_no_cost} to {total_ind_cost}."


    # tranformation rules (45)
    # ['AGGREGATE_ANY_PULL_UP_CONSTANTS', 'AGGREGATE_EXPAND_DISTINCT_AGGREGATES', 'AGGREGATE_EXPAND_DISTINCT_AGGREGATES_TO_JOIN', 'AGGREGATE_JOIN_REMOVE', 'AGGREGATE_JOIN_TRANSPOSE_EXTENDED', 'AGGREGATE_UNION_TRANSPOSE', 'AGGREGATE_UNION_AGGREGATE', 'AGGREGATE_VALUES', 'AGGREGATE_PROJECT_MERGE', 'FILTER_INTO_JOIN', 'FILTER_MERGE', 'FILTER_AGGREGATE_TRANSPOSE', 'FILTER_PROJECT_TRANSPOSE', 'FILTER_TABLE_FUNCTION_TRANSPOSE', 'FILTER_SCAN', 'FILTER_CORRELATE', 'FILTER_SET_OP_TRANSPOSE', 'FILTER_REDUCE_EXPRESSIONS', 'JOIN_CONDITION_PUSH', 'JOIN_EXTRACT_FILTER', 'JOIN_PROJECT_BOTH_TRANSPOSE', 'JOIN_PROJECT_LEFT_TRANSPOSE', 'JOIN_PROJECT_RIGHT_TRANSPOSE', 'JOIN_REDUCE_EXPRESSIONS', 'JOIN_LEFT_UNION_TRANSPOSE', 'JOIN_RIGHT_UNION_TRANSPOSE', 'SEMI_JOIN_REMOVE', 'PROJECT_CALC_MERGE', 'PROJECT_CORRELATE_TRANSPOSE', 'PROJECT_REDUCE_EXPRESSIONS', 'PROJECT_SUB_QUERY_TO_CORRELATE', 'PROJECT_MERGE', 'PROJECT_REMOVE', 'PROJECT_TO_CALC', 'CALC_MERGE', 'CALC_REMOVE', 'SORT_UNION_TRANSPOSE', 'SORT_REMOVE', 'SORT_REMOVE_CONSTANT_KEYS', 'SORT_JOIN_TRANSPOSE', 'SORT_PROJECT_TRANSPOSE', 'UNION_MERGE', 'UNION_REMOVE', 'UNION_PULL_UP_CONSTANTS', 'UNION_TO_DISTINCT']

    @tool.get("/AGGREGATE_ANY_PULL_UP_CONSTANTS_rule")
    def AGGREGATE_ANY_PULL_UP_CONSTANTS_rule(query : str):

        param = {
            "sql": query,
            "rule": "AGGREGATE_ANY_PULL_UP_CONSTANTS"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/AGGREGATE_EXPAND_DISTINCT_AGGREGATES_rule")
    def AGGREGATE_EXPAND_DISTINCT_AGGREGATES_rule(query : str):

        param = {
            "sql": query,
            "rule": "AGGREGATE_EXPAND_DISTINCT_AGGREGATES"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/AGGREGATE_EXPAND_DISTINCT_AGGREGATES_TO_JOIN_rule")
    def AGGREGATE_EXPAND_DISTINCT_AGGREGATES_TO_JOIN_rule(query : str):

        param = {
            "sql": query,
            "rule": "AGGREGATE_EXPAND_DISTINCT_AGGREGATES_TO_JOIN"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/AGGREGATE_JOIN_REMOVE_rule")
    def AGGREGATE_JOIN_REMOVE_rule(query : str):

        param = {
            "sql": query,
            "rule": "AGGREGATE_JOIN_REMOVE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/AGGREGATE_JOIN_TRANSPOSE_EXTENDED_rule")
    def AGGREGATE_JOIN_TRANSPOSE_EXTENDED_rule(query : str):

        param = {
            "sql": query,
            "rule": "AGGREGATE_JOIN_TRANSPOSE_EXTENDED"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/AGGREGATE_UNION_TRANSPOSE_rule")
    def AGGREGATE_UNION_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "AGGREGATE_UNION_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/AGGREGATE_UNION_AGGREGATE_rule")
    def AGGREGATE_UNION_AGGREGATE_rule(query : str):

        param = {
            "sql": query,
            "rule": "AGGREGATE_UNION_AGGREGATE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/AGGREGATE_VALUES_rule")
    def AGGREGATE_VALUES_rule(query : str):

        param = {
            "sql": query,
            "rule": "AGGREGATE_VALUES"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/AGGREGATE_PROJECT_MERGE_rule")
    def AGGREGATE_PROJECT_MERGE_rule(query : str):

        param = {
            "sql": query,
            "rule": "AGGREGATE_PROJECT_MERGE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/FILTER_INTO_JOIN_rule")
    def FILTER_INTO_JOIN_rule(query : str):

        param = {
            "sql": query,
            "rule": "FILTER_INTO_JOIN"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/FILTER_MERGE_rule")
    def FILTER_MERGE_rule(query : str):

        param = {
            "sql": query,
            "rule": "FILTER_MERGE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/FILTER_AGGREGATE_TRANSPOSE_rule")
    def FILTER_AGGREGATE_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "FILTER_AGGREGATE_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/FILTER_PROJECT_TRANSPOSE_rule")
    def FILTER_PROJECT_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "FILTER_PROJECT_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/FILTER_TABLE_FUNCTION_TRANSPOSE_rule")
    def FILTER_TABLE_FUNCTION_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "FILTER_TABLE_FUNCTION_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/FILTER_SCAN_rule")
    def FILTER_SCAN_rule(query : str):

        param = {
            "sql": query,
            "rule": "FILTER_SCAN"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/FILTER_CORRELATE_rule")
    def FILTER_CORRELATE_rule(query : str):

        param = {
            "sql": query,
            "rule": "FILTER_CORRELATE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/FILTER_SET_OP_TRANSPOSE_rule")
    def FILTER_SET_OP_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "FILTER_SET_OP_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/FILTER_REDUCE_EXPRESSIONS_rule")
    def FILTER_REDUCE_EXPRESSIONS_rule(query : str):

        param = {
            "sql": query,
            "rule": "FILTER_REDUCE_EXPRESSIONS"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/JOIN_CONDITION_PUSH_rule")
    def JOIN_CONDITION_PUSH_rule(query : str):

        param = {
            "sql": query,
            "rule": "JOIN_CONDITION_PUSH"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/JOIN_EXTRACT_FILTER_rule")
    def JOIN_EXTRACT_FILTER_rule(query : str):

        param = {
            "sql": query,
            "rule": "JOIN_EXTRACT_FILTER"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/JOIN_PROJECT_BOTH_TRANSPOSE_rule")
    def JOIN_PROJECT_BOTH_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "JOIN_PROJECT_BOTH_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/JOIN_PROJECT_LEFT_TRANSPOSE_rule")
    def JOIN_PROJECT_LEFT_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "JOIN_PROJECT_LEFT_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/JOIN_PROJECT_RIGHT_TRANSPOSE_rule")
    def JOIN_PROJECT_RIGHT_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "JOIN_PROJECT_RIGHT_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/JOIN_REDUCE_EXPRESSIONS_rule")
    def JOIN_REDUCE_EXPRESSIONS_rule(query : str):

        param = {
            "sql": query,
            "rule": "JOIN_REDUCE_EXPRESSIONS"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/JOIN_LEFT_UNION_TRANSPOSE_rule")
    def JOIN_LEFT_UNION_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "JOIN_LEFT_UNION_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/JOIN_RIGHT_UNION_TRANSPOSE_rule")
    def JOIN_RIGHT_UNION_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "JOIN_RIGHT_UNION_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/SEMI_JOIN_REMOVE_rule")
    def SEMI_JOIN_REMOVE_rule(query : str):

        param = {
            "sql": query,
            "rule": "SEMI_JOIN_REMOVE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/PROJECT_CALC_MERGE_rule")
    def PROJECT_CALC_MERGE_rule(query : str):

        param = {
            "sql": query,
            "rule": "PROJECT_CALC_MERGE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/PROJECT_CORRELATE_TRANSPOSE_rule")
    def PROJECT_CORRELATE_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "PROJECT_CORRELATE_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/PROJECT_REDUCE_EXPRESSIONS_rule")
    def PROJECT_REDUCE_EXPRESSIONS_rule(query : str):

        param = {
            "sql": query,
            "rule": "PROJECT_REDUCE_EXPRESSIONS"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/PROJECT_SUB_QUERY_TO_CORRELATE_rule")
    def PROJECT_SUB_QUERY_TO_CORRELATE_rule(query : str):

        param = {
            "sql": query,
            "rule": "PROJECT_SUB_QUERY_TO_CORRELATE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/PROJECT_MERGE_rule")
    def PROJECT_MERGE_rule(query : str):

        param = {
            "sql": query,
            "rule": "PROJECT_MERGE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/PROJECT_REMOVE_rule")
    def PROJECT_REMOVE_rule(query : str):

        param = {
            "sql": query,
            "rule": "PROJECT_REMOVE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/PROJECT_TO_CALC_rule")
    def PROJECT_TO_CALC_rule(query : str):

        param = {
            "sql": query,
            "rule": "PROJECT_TO_CALC"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/CALC_MERGE_rule")
    def CALC_MERGE_rule(query : str):

        param = {
            "sql": query,
            "rule": "CALC_MERGE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/CALC_REMOVE_rule")
    def CALC_REMOVE_rule(query : str):

        param = {
            "sql": query,
            "rule": "CALC_REMOVE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/SORT_UNION_TRANSPOSE_rule")
    def SORT_UNION_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "SORT_UNION_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/SORT_REMOVE_rule")
    def SORT_REMOVE_rule(query : str):

        param = {
            "sql": query,
            "rule": "SORT_REMOVE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/SORT_REMOVE_CONSTANT_KEYS_rule")
    def SORT_REMOVE_CONSTANT_KEYS_rule(query : str):

        param = {
            "sql": query,
            "rule": "SORT_REMOVE_CONSTANT_KEYS"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/SORT_JOIN_TRANSPOSE_rule")
    def SORT_JOIN_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "SORT_JOIN_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/SORT_PROJECT_TRANSPOSE_rule")
    def SORT_PROJECT_TRANSPOSE_rule(query : str):

        param = {
            "sql": query,
            "rule": "SORT_PROJECT_TRANSPOSE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/UNION_MERGE_rule")
    def UNION_MERGE_rule(query : str):

        param = {
            "sql": query,
            "rule": "UNION_MERGE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/UNION_REMOVE_rule")
    def UNION_REMOVE_rule(query : str):

        param = {
            "sql": query,
            "rule": "UNION_REMOVE"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/UNION_PULL_UP_CONSTANTS_rule")
    def UNION_PULL_UP_CONSTANTS_rule(query : str):

        param = {
            "sql": query,
            "rule": "UNION_PULL_UP_CONSTANTS"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output



    @tool.get("/UNION_TO_DISTINCT_rule")
    def UNION_TO_DISTINCT_rule(query : str):

        param = {
            "sql": query,
            "rule": "UNION_TO_DISTINCT"
        }
        print("Rule param:", param)

        headers = {'Content-Type': 'application/json'}
        res_completion = requests.post(executor_url, data=json.dumps(param), headers=headers)

        #print("============ res_completion", res_completion.text)

        data = json.loads(res_completion.text.strip())
        data = data.get('data')
        new_query = data.get('rewritten_sql')

        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            text_output = f"Failed to optimize the query. The new query is still {query}"
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"

        return text_output

    # query hints (15)
    # ["bitmapscan",
    # "gathermerge",
    # "hashagg",
    # "hashjoin",
    # "indexonlyscan",
    # "indexscan",
    # "material",
    # "mergejoin",
    # "nestloop",
    # "parallel_append",
    # "parallel_hash",
    # "partition_pruning",
    # "seqscan",
    # "sort",
    # "tidscan",]

    @tool.get("/enable_or_disable_bitmapscan_operator")
    def enable_or_disable_bitmapscan_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_bitmapscan to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_bitmapscan knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the bitmapscan operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators}, after disabling the bitmapscan operator."
            

        return text_output



    @tool.get("/enable_or_disable_gathermerge_operator")
    def enable_or_disable_gathermerge_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_gathermerge to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_gathermerge knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the gathermerge operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the gathermerge operator."

        return text_output



    @tool.get("/enable_or_disable_hashagg_operator")
    def enable_or_disable_hashagg_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_hashagg to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_hashagg knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the hashagg operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the hashagg operator."

        return text_output



    @tool.get("/enable_or_disable_hashjoin_operator")
    def enable_or_disable_hashjoin_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_hashjoin to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_hashjoin knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the hashjoin operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the hashjoin operator."

        return text_output



    @tool.get("/enable_or_disable_indexonlyscan_operator")
    def enable_or_disable_indexonlyscan_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_indexonlyscan to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_indexonlyscan knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the indexonlyscan operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the indexonlyscan operator."

        return text_output



    @tool.get("/enable_or_disable_indexscan_operator")
    def enable_or_disable_indexscan_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_indexscan to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_indexscan knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the indexscan operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the indexscan operator."

        return text_output



    @tool.get("/enable_or_disable_material_operator")
    def enable_or_disable_material_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_material to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_material knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the material operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the material operator."

        return text_output



    @tool.get("/enable_or_disable_mergejoin_operator")
    def enable_or_disable_mergejoin_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_mergejoin to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_mergejoin knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the mergejoin operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the mergejoin operator."

        return text_output



    @tool.get("/enable_or_disable_nestloop_operator")
    def enable_or_disable_nestloop_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_nestloop to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_nestloop knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the nestloop operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the nestloop operator."

        return text_output



    @tool.get("/enable_or_disable_parallel_append_operator")
    def enable_or_disable_parallel_append_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_parallel_append to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_parallel_append knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the parallel_append operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the parallel_append operator."

        return text_output



    @tool.get("/enable_or_disable_parallel_hash_operator")
    def enable_or_disable_parallel_hash_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_parallel_hash to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_parallel_hash knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the parallel_hash operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the parallel_hash operator."

        return text_output



    @tool.get("/enable_or_disable_partition_pruning_operator")
    def enable_or_disable_partition_pruning_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_partition_pruning to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_partition_pruning knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the partition_pruning operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the partition_pruning operator."

        return text_output



    @tool.get("/enable_or_disable_seqscan_operator")
    def enable_or_disable_seqscan_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_seqscan to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_seqscan knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the seqscan operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the seqscan operator."

        return text_output



    @tool.get("/enable_or_disable_sort_operator")
    def enable_or_disable_sort_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_sort to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_sort knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the sort operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the sort operator."

        return text_output


    @tool.get("/enable_or_disable_tidscan_operator")
    def enable_or_disable_tidscan_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_tidscan to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_tidscan knob.")
        else:
            if action == "ON":
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the tidscan operator."
            else:
                total_cost, operators = db.query_plan_statistics(new_query_plan)
                text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the tidscan operator."

        return text_output

    return tool