import warnings
import sys
import json
import os
import requests
import numpy as np
import openai
import paramiko
import pdb

from multiagents.tools.index_advisor.index_selection.selection_utils.postgres_dbms import PostgresDatabaseConnector
from multiagents.tools.index_advisor.index_selection.selection_utils.workload import Workload
from multiagents.tools.index_advisor.index_selection.selection_utils import selec_com
from multiagents.tools.index_advisor.configs import INDEX_SELECTION_ALGORITHMS, get_index_result

from multiagents.utils.database import DBArgs, Database
from multiagents.utils.core import read_yaml

from multiagents.tools.metrics import prometheus_metrics, benchserver_conf, postgresql_conf

def optimize_index_selection(start_time: int, end_time: int):
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
    schema_file = script_dir + \
        f"/index_selection/selection_data/data_info/schema_job.json"
    workload_file = script_dir + \
        f"/index_selection/selection_data/data_info/job_templates.sql"

    script_dir = os.path.dirname(script_dir)
    tables, columns = selec_com.get_columns_from_schema(schema_file)

    # load db settings
    db_config = {}
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    script_dir = os.path.dirname(script_dir)

    db_config["postgresql"] = postgresql_conf
    db_config["postgresql"]["dbname"] = dbname
    connector = PostgresDatabaseConnector(db_config, autocommit=True)

    workload = []
    with open(workload_file, "r") as rf:
        for line in rf.readlines():
            workload.append(line.strip())

    indexes, total_no_cost, total_ind_cost = get_index_result(
        algo, workload, connector, columns, sel_params=sel_params, process=process, overhead=overhead)

    if indexes == []:
        return "No beneficial single-column indexes can be found!"

    return f"The recommended indexes are: {indexes}, which reduces cost from {total_no_cost} to {total_ind_cost}."