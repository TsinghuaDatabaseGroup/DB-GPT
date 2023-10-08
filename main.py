import argparse
from multiagents.multiagents import MultiAgents
from multiagents.tools.metrics import database_server_conf, db
from multiagents.tools.metrics import get_workload_statistics, set_workload_statistics, get_slow_queries, set_slow_queries
from multiagents.utils.server import obtain_slow_queries

parser = argparse.ArgumentParser()
parser.add_argument('--latest_alert_file', type=str, default="latest_alert_info", required=False, help='the file name of latest alert information')
parser.add_argument('--agent_conf_name', type=str, default="agent_conf", required=False, help='the file name of llm agent settings')
parser.add_argument('--max_hired_experts', type=int, default=2, required=False, help='the maximum number of hired experts')
parser.add_argument('--max_api_num', type=int, default=20, required=False, help='the maximum number of tool apis passed to single llm')
# parser.add_argument('--max_abnormal_metric_num', type=int, default=5, required=False, help='the maximum number of abnormal metrics (after detectiion) passed to single llm')
parser.add_argument('--enable_slow_query_log', type=bool, default=False, required=False, help='True for enabling the collection of slow queries from database logs')
parser.add_argument('--enable_workload_statistics_view', type=bool, default=True, required=False, help='True for enabling the collection of query template information from database view')
args = parser.parse_args()

if args.enable_slow_query_log == True:
    # [slow queries] read from query logs
    # /var/lib/pgsql/12/data/pg_log/postgresql-Mon.log
    slow_queries = obtain_slow_queries(database_server_conf)
    set_slow_queries(str(slow_queries))

if args.enable_workload_statistics_view == True:
    workload_statistics = db.obtain_historical_queries_statistics()
    set_workload_statistics(str(workload_statistics))


multi_agents = MultiAgents.from_task(args.agent_conf_name, args)
multi_agents.run(args)