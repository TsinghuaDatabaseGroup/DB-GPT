import argparse

def main_parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--anomaly_file', type=str, default="", required=True, help='the file name of batch anomaly flie name')
    parser.add_argument('--config_file', type=str, default="config.yaml", required=False, help='the config file')
    parser.add_argument('--latest_alert_file', type=str, default="", required=False, help='the file name of latest alert information')
    parser.add_argument('--agent_conf_name', type=str, default="agent_conf", required=False, help='the file name of llm agent settings')
    parser.add_argument('--max_hired_experts', type=int, default=2, required=False, help='the maximum number of hired experts')
    parser.add_argument('--max_api_num', type=int, default=5, required=False, help='the maximum number of tool apis for single llm at initialization stage')
    # parser.add_argument('--max_abnormal_metric_num', type=int, default=5, required=False, help='the maximum number of abnormal metrics (after detectiion) passed to single llm')
    parser.add_argument('--enable_slow_query_log', type=bool, default=True, required=False, help='True for enabling the collection of slow queries from database logs')
    parser.add_argument('--enable_workload_statistics_view', type=bool, default=True, required=False, help='True for enabling the collection of query template information from database view')
    parser.add_argument('--enable_workload_sqls', type=bool, default=True, required=False, help='True for fetching the sql queries during the anomaly')
    parser.add_argument('--enable_prometheus', type=bool, default=False, required=False, help='True for fetching monitoring metrics from prometheus; False for fetching monitoring metrics from anomaly files')
    # parser.add_argument('--process_num', type=int, default=10, required=False, help='Parallel level for batching diagnosis')
    parser.add_argument('--start_at_seconds', type=int, default=1696841344, required=False, help='the starting time of an anomaly')
    parser.add_argument('--end_at_seconds', type=int, default=1696841415, required=False, help='the end time of an anomaly')
    parser.add_argument('--training_data_position', type=str, default="./logs/diag_training_data_with_exact_sqls.jsonl", required=False, help='the file path of recorded training data')
    args = parser.parse_args()

    return args

args = main_parse_args()
