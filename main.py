from our_argparse import args
from multiagents.multiagents import MultiAgents
from multiagents.tools.metrics import database_server_conf, db
from multiagents.tools.metrics import get_workload_statistics, get_slow_queries, WORKLOAD_FILE_NAME
from multiagents.utils.server import obtain_slow_queries
import json
import os
import asyncio
import time

async def main(args):
    multi_agents = MultiAgents.from_task(args.agent_conf_name, args)
    report, records = await multi_agents.run(args)

    cur_time = time.time()
    with open(f"./alert_results/examples/{str(cur_time)}.jsonl", "w") as f:
        json.dump(records, f, indent=4)

    return report, records

if __name__ == "__main__":

    # read from the anomalies with alerts. for each anomaly, 
    with open("./anomalies/public_testing_set/testing_cases.json", "r") as f:
        anomaly_jsons = json.load(f)

    content = next(iter(anomaly_jsons.values()))

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
    args.diag_id = str(0)
    
    asyncio.run(main(args))