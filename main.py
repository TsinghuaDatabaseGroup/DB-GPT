from our_argparse import args
from multiagents.multiagents import MultiAgents
from multiagents.tools.metrics import database_server_conf, db
from multiagents.tools.metrics import current_diag_time, update_current_time, get_workload_statistics, get_slow_queries, WORKLOAD_FILE_NAME, BATCH_ANOMALY_FILE_NAME
from utils.server import obtain_slow_queries
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

    multi_agents, model_type = MultiAgents.from_task(args.agent_conf_name, args)

    create_dir_if_not_exists(f"./alert_results/{model_type}")
    
    report, records = await multi_agents.run(args)

    cur_time = int(time.time())


    with open(f"./alert_results/{model_type}/{str(cur_time)}.jsonl", "w") as f:
        json.dump(records, f, indent=4)

    if os.path.exists(f"./alert_results/{str(current_diag_time)}"):
        os.system(f"rm -rf ./alert_results/{str(current_diag_time)}")

    return report, records


if __name__ == "__main__":
    
    # read from the anomalies with alerts. for each anomaly, 
    # "anomalies/public_testing_set/batch_testing_set.json"
    with open(BATCH_ANOMALY_FILE_NAME, "r") as f:
        anomaly_jsons = json.load(f)

    # diag_id, content = next(iter(anomaly_jsons.items()))
    # diag_id = "10"
    
    for i,diag_id in enumerate(anomaly_jsons):

        content = anomaly_jsons[diag_id]
        
        args.start_at_seconds = content["start_time"]
        args.end_at_seconds = content["end_time"]

        slow_queries = []
        workload_statistics = []
        workload_sqls = ""
        if args.enable_slow_query_log == True:
            # [slow queries] read from query logs
            # /var/lib/pgsql/12/data/pg_log/postgresql-Mon.log
            # slow_queries = obtain_slow_queries(database_server_conf)
            slow_queries = content["slow_queries"]
        if args.enable_workload_statistics_view == True:
            workload_statistics = db.obtain_historical_queries_statistics(topn = 50)
        if args.enable_workload_sqls == True:
            workload_sqls = content["workload"]

        with open(WORKLOAD_FILE_NAME, 'w') as f:
            json.dump({'slow_queries': slow_queries, 'workload_statistics': workload_statistics, 'workload_sqls': workload_sqls}, f)

        if "alerts" in content and content["alerts"] != []:
            args.alerts = content["alerts"] # possibly multiple alerts for a single anomaly
        else:
            args.alerts = []
        
        if "labels" in content and content["labels"] != []:
            args.labels = content["labels"]
        else:
            args.labels = []
        args.start_at_seconds = content["start_time"]
        args.end_at_seconds = content["end_time"]        
        args.diag_id = str(diag_id)
        
        # count the time to run main function
        start_time = time.time()
        asyncio.run(main(args))
        end_time = time.time()
        print("============diag during time==========: ", end_time - start_time)
