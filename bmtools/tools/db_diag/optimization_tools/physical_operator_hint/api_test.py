import os
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

    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign
    dbargs.dbname = "tpch"

    # send request to database
    db = Database(dbargs, timeout=-1)

    query = "select l_discount,count (distinct l_orderkey), sum(distinct l_tax) from lineitem, part where l_discount > 100 group by l_discount;"

    action = "off"

    ###### api start ######

    # add hint to the query
    new_query = f"set enable_sort to {action}; " + query
    
    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan == None:
        # raise error
        raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_gathermerge knob.")
    else:
        query_plan = db.pgsql_query_plan(query)
        cost = query_plan['Total Cost']
        new_cost = new_query_plan['Total Cost']

        if cost <= new_cost:
            text_output = "Fail to speed up the query by changing the knob."
        else:
            if action == "ON" or action == "on" or action == "On":
                text_output = f"The query cost can be reduced from {cost} to {new_cost} after enabling the gathermerge operator."
            else:
                text_output = f"The query cost can be reduced from {cost} to {new_cost} after disabling the gathermerge operator."

    ###### api end ######

    print(text_output)