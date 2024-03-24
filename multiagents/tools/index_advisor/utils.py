import sys
sys.path.insert(0, '/home/wuy/DB-GPT')
from configs import POSTGRESQL_CONFIG
# from multiagents.tools.index_advisor.index_selection.selection_utils.postgres_dbms import PostgresDatabaseConnector
# from multiagents.tools.index_advisor.index_selection.selection_utils import selec_com
# from multiagents.tools.index_advisor.configs import get_index_result
from multiagents.tools.metrics import advisor
from multiagents.tools.metrics import get_workload_statistics
import ast
from multiagents.initialization import LANGUAGE

import re
import json
import sys
import os
import time
# sys.path.insert(0,'./')
from index_eab.eab_utils.workload import Workload, Table, Column, Query
# from index_eab.eab_utils.common_utils import get_columns_from_schema, read_row_query
from index_eab.eab_utils.postgres_dbms import PostgresDatabaseConnector

from index_eab.index_advisor.extend_algorithm import ExtendAlgorithm
from index_eab.index_advisor.drop_algorithm import DropAlgorithm

# from multiagents.tools.index_advisor.configs import get_index_result



FUNCTION_DEFINITION = {
    "optimize_index_selection": {
        "name": "optimize_index_selection",
        "description":
            "使用索引选择算法返回推荐的索引。" if LANGUAGE == "zh"
            else "returns the recommended index by running the index selection algorithm.",
        "parameters": {'type': 'object', 'properties': {}}
    }
}


INDEX_SELECTION_ALGORITHMS = {
    "extend": ExtendAlgorithm,
    "drop": DropAlgorithm

}


def replace_placeholders(sql_string, substring, sampled_values):


    pattern = r"\$\d+\b"
    return re.sub(pattern, str(sampled_values[0]) if len(sampled_values)>1 else '2', sql_string)

def read_row_query(sql_list, columns, column_sampled_values, _type="template"):
    workload = list()
    for query_id, query_text in enumerate(sql_list):
        # if type == "template" and exp_conf["queries"] \
        #         and query_id + 1 not in exp_conf["queries"]:
        #     continue
       
        if 'insert' in query_text['sql'].lower():
            continue
        # if 'update' in query_text['sql'].lower():
        #     continue
        if 'delete' in query_text['sql'].lower():
            continue

        query = Query(query_id, query_text=query_text['sql'], frequency=query_text['frequency'])
        for column in columns:
            # column_tmp = [col for col in columns if column.name == col.name]
            if column.name in query.text.lower() and \
                    f"{column.table.name}" in query.text.lower():
                # column.name
                # print(f"before replace, {query.text.lower()}")
                query.text = replace_placeholders(query.text.lower(), column.name, column_sampled_values[column])
                # print(f"after replace, {query.text}\n")
                query.columns.append(column)

        workload.append(query)
    return workload

def get_ind_cost(connector, query, indexes, mode="hypo"):
    connector.create_indexes(indexes, mode)

    stmt = f"explain (format json) {query}"
    query_plan = connector.exec_fetch(stmt)[0][0]["Plan"]
    # drop view
    # self._cleanup_query(query)
    total_cost = query_plan["Total Cost"]

    if mode == "hypo":
        connector.drop_hypo_indexes()
    else:
        connector.drop_indexes()

    return total_cost

def get_index_result(algo, work_list, connector, columns, column_sampled_values,
                     sel_params="parameters", process=False, overhead=False):

    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)

    # exp_conf_file = script_dir + \
    #     f"/index_selection/selection_data/algo_conf/{algo}_config.json"
    # with open(exp_conf_file, "r") as rf:
    #     exp_config = json.load(rf)

    # config = selec_com.find_parameter_list(exp_config["algorithms"][0],
    #                                        params=sel_params)[0]
    parameters = {"budget_MB": 1500, "max_index_width": 2, "max_indexes": 5, "constraint": "storage"}
    algo='extend'
    queries=read_row_query(work_list, columns, column_sampled_values, _type="")
    workload = Workload(queries)
    # connector.enable_simulation()
    # time.sleep(.1)
    try:
        connector.drop_hypo_indexes()
    except Exception as e:
        print(e)

    algorithm = INDEX_SELECTION_ALGORITHMS[algo](
        connector, parameters, process=process)

    indexes = algorithm.calculate_best_indexes(workload, overhead=overhead)

    if indexes == [] or indexes == None or indexes == "":
        return [], -1, -1

    if isinstance(indexes[0], list) and len(indexes) >= 1:
        indexes = indexes[0]

    # if indexes are of string type
    if not isinstance(indexes, list):
        indexes = [str(indexes)]
    else:
        indexes = [str(ind) for ind in indexes]

    cols = [ind.split(",") for ind in indexes]
    cols = [list(map(lambda x: x.split(".")[-1], col)) for col in cols]
    indexes = [
        f"{ind.split('.')[0]}#{','.join(col)}" for ind,
        col in zip(
            indexes,
            cols)]

    no_cost, ind_cost = list(), list()
    total_no_cost, total_ind_cost = 0, 0
    for sql in queries:
        no_cost_ = get_ind_cost(connector, sql.text, [])
        # print(f"no_cost_ {no_cost_}")
        total_no_cost += round(no_cost_*sql.frequency, 2)
        no_cost.append(no_cost_)

        ind_cost_ = get_ind_cost(connector, sql.text, indexes)
        # print(f"ind_cost_ {ind_cost_}")
        total_ind_cost += round(ind_cost_*sql.frequency, 2)
        ind_cost.append(ind_cost_)

    return indexes, total_no_cost, total_ind_cost

def get_sampled_values(db_connector, column, table, sample_size=1):

        sql = f"select {column} from {table} limit ({sample_size})"

        rows = db_connector.exec_fetch(sql, one=False)

        sampled_values = []
        for row in rows:
            # if row is of string type, add quotes
            if isinstance(row[0], str):
                sampled_values.append(f"\'{row[0]}\'")
        # print(f" in get_sample_values, {table}.{column}: {sampled_values}")
        return sampled_values
    
def get_columns_from_db(db_connector):

    tables, columns = list(), list()
    column_sampled_values={}
    for table in db_connector.get_tables():
        # print(f"-------------- table {table}")
        table_object = Table(table)
        tables.append(table_object)
        # print(f"@@@@@@ cols: {db_connector.get_cols(table)}")
        for col in db_connector.get_cols(table):
 
            sampled_values = get_sampled_values(db_connector, col, table)
            # column_object = Column(col, sampled_values)
            
            column_object = Column(col)
            column_object.table=table_object
            # print(f"############## col {col}, {column_object}")
            column_sampled_values[column_object]=sampled_values
            table_object.add_column(column_object)
            columns.append(column_object)

    return tables, columns, column_sampled_values
