import json
import os
import requests

from bmtools.tools.db_diag.utils.db_parser import get_conf
from bmtools.tools.db_diag.utils.database import DBArgs, Database

from utils.core import read_yaml

if __name__ == '__main__':

    # load db settings
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    script_dir = os.path.dirname(script_dir)
    script_dir = os.path.dirname(script_dir)
    script_dir = os.path.dirname(script_dir)
    postgresql_conf = read_yaml('POSTGRESQL', 'config/tool_config.yaml')
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign dbargs
    dbargs.dbname = "tpch"

    # send request to database
    db = Database(dbargs, timeout=-1)

    query = "select l_discount,count (distinct l_orderkey), sum(distinct l_tax) from lineitem, part where l_discount > 100 group by l_discount;"

    ###### api start ######

    executor_url = "http://8.131.229.55:5114/rewrite/single_rule"

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

    ###### api end ######

    print(text_output)