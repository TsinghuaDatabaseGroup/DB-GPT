from multiagents.our_argparse import args
from multiagents.multiagents import MultiAgents
from multiagents.tools.metrics import db, current_diag_time
from multiagents.tools.metrics import WORKLOAD_FILE_NAME
import json
import os
import asyncio
import time
from pathlib import Path

def create_dir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        path = Path(dir_path)
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Failed to create directory {dir_path}: {e}")


async def main(args):
    global current_diag_time

    create_dir_if_not_exists(f"./alert_results/{str(current_diag_time)}")
    print('<flow>{"title": "初始化专家角色", "content": "", "isCompleted": 0, "isRuning": 1}</flow>')
    
    # initialize llm agents
    multi_agents, model_type = MultiAgents.from_task(args.agent_conf_name, args)

    create_dir_if_not_exists(f"./alert_results/{model_type}")

    report, records = await multi_agents.run(args)

    current_diag_time = time.localtime()

    cur_time = int(time.mktime(current_diag_time))

    current_diag_time = time.strftime("%Y-%m-%d-%H:%M:%S", current_diag_time)

    records["report_generate_time"] = current_diag_time

    with open(f"./alert_results/{model_type}/{str(cur_time)}.jsonl", "w", encoding='utf8') as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

    if os.path.exists(f"./alert_results/{str(current_diag_time)}"):
        os.system(f"rm -rf ./alert_results/{str(current_diag_time)}")

    return report, records


if __name__ == "__main__":

    # read from the anomalies with alerts. for each anomaly,
    with open(args.anomaly_file, "r") as f:
        anomaly_json = json.load(f)

    args.start_at_seconds = anomaly_json["start_time"]
    args.end_at_seconds = anomaly_json["end_time"]

    slow_queries = []
    workload_statistics = []
    workload_sqls = ""

    if args.enable_slow_query_log == True:
        # [slow queries] read from query logs
        # /var/lib/pgsql/12/data/pg_log/postgresql-Mon.log
        slow_queries = anomaly_json["slow_queries"]
    if args.enable_workload_statistics_view == True:
        workload_statistics = db.obtain_historical_queries_statistics(topn=50)
    if args.enable_workload_sqls == True:
        workload_sqls = anomaly_json["workload"]

    with open(WORKLOAD_FILE_NAME, 'w') as f:
        json.dump({'slow_queries': slow_queries, 'workload_statistics': workload_statistics,
                   'workload_sqls': workload_sqls}, f)

    if "alerts" in anomaly_json and anomaly_json["alerts"] != []:
        args.alerts = anomaly_json["alerts"]  # possibly multiple alerts for a single anomaly
    else:
        args.alerts = []

    if "labels" in anomaly_json and anomaly_json["labels"] != []:
        args.labels = anomaly_json["labels"]
    else:
        args.labels = []
    args.start_at_seconds = anomaly_json["start_time"]
    args.end_at_seconds = anomaly_json["end_time"]
    args.diag_id = "0"
    # count the time to run main function
    start_time = time.time()
    asyncio.run(main(args))
    end_time = time.time()
    print(f"****Diagnose Finished!****\n****During Time : {end_time - start_time}****")
