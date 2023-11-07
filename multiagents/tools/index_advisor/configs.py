import os
import json

from .index_selection.selection_algorithms.extend_algorithm import ExtendAlgorithm
from .index_selection.selection_algorithms.db2advis_algorithm import DB2AdvisAlgorithm
from .index_selection.selection_utils.workload import Workload
from .index_selection.selection_utils import selec_com
import time
import pdb


INDEX_SELECTION_ALGORITHMS = {
    "extend": ExtendAlgorithm,
    "db2advis": DB2AdvisAlgorithm
}

def get_index_result(algo, work_list, connector, columns,
                     sel_params="parameters", process=False, overhead=False):

    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)

    exp_conf_file = script_dir + \
        f"/index_selection/selection_data/algo_conf/{algo}_config.json"
    with open(exp_conf_file, "r") as rf:
        exp_config = json.load(rf)

    config = selec_com.find_parameter_list(exp_config["algorithms"][0],
                                           params=sel_params)[0]
    
    workload = Workload(selec_com.read_row_query(work_list, exp_config,
                                                 columns, type=""))
    
    connector.enable_simulation()
    time.sleep(.1)
    connector.drop_hypo_indexes()

    algorithm = INDEX_SELECTION_ALGORITHMS[algo](
        connector, config["parameters"], process)

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
    for sql in work_list:
        if '$' not in sql['sql']:
            no_cost_ = connector.get_ind_cost(sql['sql'], "")
            total_no_cost += round(no_cost_*sql['frequency'], 2)
            no_cost.append(no_cost_)

            ind_cost_ = connector.get_ind_cost(sql['sql'], indexes)
            total_ind_cost += round(ind_cost_*sql['frequency'], 2)
            ind_cost.append(ind_cost_)

    return indexes, total_no_cost, total_ind_cost