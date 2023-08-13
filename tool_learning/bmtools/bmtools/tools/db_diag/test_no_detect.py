
from bmtools.agent.singletool import load_single_tools, STQuestionAnswerer
import datetime
import pdb

tool_name, tool_url = 'db_diag',  "http://127.0.0.1:8079/tools/db_diag/"
# pdb.set_trace()
tool_name, tool_config = load_single_tools(tool_name, tool_url)
print(tool_name, tool_config)
stqa =  STQuestionAnswerer()

# langchain

agent = stqa.load_tools(tool_name, tool_config, prompt_type="react-with-tool-description") # langchain: react-with-tool-description autogpt: autogpt

# database on 123.56.63.105

# fetch_large_data /  correlated_subquery
start_timestamp_str = "2023-08-09 17:00:30"
end_timestamp_str = "2023-08-09 17:02:00"

# INSERT\_LARGE\_DATA IO\_CONTENTION CPU\_CONTENTION
start_timestamp_str = "2023-08-09 14:52:30"
end_timestamp_str = "2023-08-09 14:56:30"

# POOR\_JOIN\_PERFORMANCE WORKLOAD\_CONTENTION
start_timestamp_str = "2023-08-08 11:04:00"
end_timestamp_str = "2023-08-08 11:06:30"


dt = datetime.datetime.strptime(start_timestamp_str, "%Y-%m-%d %H:%M:%S")
timestamp = dt.timestamp()
start_time = timestamp

dt = datetime.datetime.strptime(end_timestamp_str, "%Y-%m-%d %H:%M:%S")
timestamp = dt.timestamp()
end_time = timestamp

print(" ===== time period: ", start_time, end_time)

text = "The database performance is bad during {} to {}. Please help me to diagnose the causes and give some optimization suggestions.".format(start_time, end_time)

#text = "Here is a database performance problem. Please help me to diagnose the causes and give some optimization suggestions."

agent(""" {}

First, you need to diagnose the causes of the anomaly from the following two aspects:

    - call the whether_is_abnormal_metric API and examine whether CPU usage is high (or abnormal). Next, if the CPU usage is high (or abnormal), cpu_diagnosis_agent and obtain the diagnosis results.

    - call the whether_is_abnormal_metric API and examine whether memory usage is high (or abnormal). Next, if the memory usage is high (or abnormal), memory_diagnosis_agent and obtain the diagnosis results.

Second, you need to give potential optimization solutions for each root causes.

Finally, list the above diagnosed causes and their matched solutions in easy-to-understand format using bullet points.

================================
A Demonstration example:

Thought: I need to check whether the CPU usage is high or abnormal during the given time period.

Action: whether_is_abnormal_metric

Action Input: {{"start_time": xxxx, "end_time": xxxx, "metric_name": "cpu_usage"}}

Note. 1) Do not use any image in the output; 
2) Give some optimization suggestions based on the diagnosis results.
""".format(text))

'''
1) Action can only be one of the following API names: whether_is_abnormal_metric, obtain_values_of_metrics, cpu_diagnosis_agent, memory_diagnosis_agent. Any other content in Action is unacceptable;
'''

'''
{"diagnose":"Based on the CPU relevant metric values you provided, 
 
 let's analyze the potential causes of the high CPU usage:\n\n
 
 1. node_scrape_collector_duration_seconds: The value of 0.00016402 indicates the duration it takes to scrape metrics from the node exporter. This metric alone does not directly indicate high CPU usage but can be used to monitor the performance of the scraping process.\n\n
 
 2. node_procs_running: The value of 12.0 represents the number of processes currently running on the node. If this value is consistently high, it could indicate that there are too many processes running, potentially causing high CPU usage.\n\n
 
 3. node_procs_blocked: The value of 4.0 represents the number of processes currently blocked on the node. If this value is consistently high, it could indicate that there are processes waiting for resources, which can lead to high CPU usage.\n\n
 
 4. node_entropy_available_bits: The value of 3754.0 represents the available entropy bits on the node. This metric is not directly related to CPU usage but can be an indicator of system randomness. Low entropy can sometimes cause high CPU usage due to increased demand for random numbers.\n\n5. node_load1, node_load5, node_load15: These metrics represent the average system load over the last 1, 5, and 15 minutes, respectively. The values of 5.96, 3.36, and 1.49 indicate that the system load is relatively high. High system load can be a potential cause of high CPU usage if the CPU is constantly busy handling multiple tasks.\n\n
 
 Based on these metrics, it is difficult to pinpoint the exact cause of the high CPU usage. However, the high number of running processes, blocked processes, and high system load could be contributing factors. It is recommended to further investigate the specific processes or applications that are consuming the most CPU resources to identify the root cause of the issue.",
 
 "knowledge":"missing_index: This function checks for the presence of a required index using a workload-index-recommend interface. If the recommended index information is available, it indicates that a required index is missing and provides a suggestion for the recommended index. If the information is not available, it is not a root cause for the issue.\n\n"}
'''
