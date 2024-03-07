from configs import POSTGRESQL_CONFIG
from multiagents.tools.index_advisor.index_selection.selection_utils.postgres_dbms import PostgresDatabaseConnector
from multiagents.tools.index_advisor.index_selection.selection_utils import selec_com
from multiagents.tools.index_advisor.configs import get_index_result
from multiagents.tools.metrics import advisor
from multiagents.tools.metrics import get_workload_statistics
import ast
from multiagents.initialization import LANGUAGE

FUNCTION_DEFINITION = {
    "optimize_index_selection": {
        "name": "optimize_index_selection",
        "description":
            "使用索引选择算法返回推荐的索引。" if LANGUAGE == "zh"
            else "returns the recommended index by running the index selection algorithm.",
        "parameters": {'type': 'object', 'properties': {}}
    }
}


def optimize_index_selection(**kwargs):
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

    # 1. Split the workloads by database names
    databases = {}
    workload_statistics = get_workload_statistics()
    if isinstance(workload_statistics, str):
        workload_statistics = ast.literal_eval(workload_statistics)

    for query_template in workload_statistics:
        database_name = query_template["dbname"]

        if database_name not in databases:
            databases[database_name] = []

        databases[database_name].append({"sql": query_template["sql"], "frequency": query_template["calls"]})

    index_advice = "推荐的索引是：\n" if LANGUAGE == "zh" else f"Recommended indexes: \n"

    for dbname in databases:

        # 2. load db settings
        db_config = {"postgresql": POSTGRESQL_CONFIG}
        db_config["postgresql"]["dbname"] = dbname
        connector = PostgresDatabaseConnector(db_config, autocommit=True)

        tables, columns = selec_com.get_columns_from_db(connector)  # todo sample data for each column

        # 3. read the workload queries
        workload = databases[dbname]  # list of dict

        # script_path = os.path.abspath(__file__)
        # script_dir = os.path.dirname(script_path)
        # # read from the logged queries recorded by the match_diagnose_knowledge function
        # workload_file = script_dir + \
        #                 f"/index_selection/selection_data/data_info/job_templates.sql"
        # workload = list()
        # with open(workload_file, "r") as rf:
        #     for line in rf.readlines():
        #         workload.append(line.strip())

        indexes, total_no_cost, total_ind_cost = get_index_result(advisor, workload, connector, columns)

        if len(indexes) != 0:
            index_advice += (
                f"对数据库{dbname}，推荐的索引是：{indexes}，cost从原来的{total_no_cost}减少到{total_ind_cost}。\n" if LANGUAGE == "zh"
                else f"\t For {dbname}, the recommended indexes are: {indexes}, which reduces cost from {total_no_cost} to {total_ind_cost}.\n"
            )

    return index_advice
