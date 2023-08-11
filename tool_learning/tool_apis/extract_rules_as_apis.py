

template = """

    @tool.get("/AGGREGATE_EXPAND_DISTINCT_AGGREGATES_rule")
    def AGGREGATE_EXPAND_DISTINCT_AGGREGATES_rule(query):

        param = {
            "sql": query,
            "rule": "AGGREGATE_EXPAND_DISTINCT_AGGREGATES"
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
            text_output = f"The new query is {new_query}. The plan of the new query is {new_query_plan}"

        return text_output

"""

template2 = """


    @tool.get("/enable_or_disable_bitmapscan_operator")
    def enable_or_disable_bitmapscan_operator(action : str, query : str):

        # add hint to the query
        new_query = f"set enable_bitmapscan to {action}; " + query

        # execute the new query
        new_query_plan = db.pgsql_query_plan(new_query)

        if new_query_plan == None:
            # raise error
            raise Exception(status_code=400, detail=f"Failed to explain the query after changing the enable_bitmapscan knob.")
        else:
            if action == "ON":
                text_output = f"The new query plan is {new_query_plan} after enabling the bitmapscan operator."
            else:
                text_output = f"The new query plan is {new_query_plan} after disabling the bitmapscan operator."

        return text_output
"""

our_rules = ['AGGREGATE_ANY_PULL_UP_CONSTANTS', 'AGGREGATE_EXPAND_DISTINCT_AGGREGATES', 'AGGREGATE_EXPAND_DISTINCT_AGGREGATES_TO_JOIN', 'AGGREGATE_JOIN_REMOVE', 'AGGREGATE_JOIN_TRANSPOSE_EXTENDED', 'AGGREGATE_UNION_TRANSPOSE', 'AGGREGATE_UNION_AGGREGATE', 'AGGREGATE_VALUES', 'AGGREGATE_PROJECT_MERGE', 'FILTER_INTO_JOIN', 'FILTER_MERGE', 'FILTER_AGGREGATE_TRANSPOSE', 'FILTER_PROJECT_TRANSPOSE', 'FILTER_TABLE_FUNCTION_TRANSPOSE', 'FILTER_SCAN', 'FILTER_CORRELATE', 'FILTER_SET_OP_TRANSPOSE', 'FILTER_REDUCE_EXPRESSIONS', 'JOIN_CONDITION_PUSH', 'JOIN_EXTRACT_FILTER', 'JOIN_PROJECT_BOTH_TRANSPOSE', 'JOIN_PROJECT_LEFT_TRANSPOSE', 'JOIN_PROJECT_RIGHT_TRANSPOSE', 'JOIN_REDUCE_EXPRESSIONS', 'JOIN_LEFT_UNION_TRANSPOSE', 'JOIN_RIGHT_UNION_TRANSPOSE', 'SEMI_JOIN_REMOVE', 'PROJECT_CALC_MERGE', 'PROJECT_CORRELATE_TRANSPOSE', 'PROJECT_REDUCE_EXPRESSIONS', 'PROJECT_SUB_QUERY_TO_CORRELATE', 'PROJECT_MERGE', 'PROJECT_REMOVE', 'PROJECT_TO_CALC', 'CALC_MERGE', 'CALC_REMOVE', 'SORT_UNION_TRANSPOSE', 'SORT_REMOVE', 'SORT_REMOVE_CONSTANT_KEYS', 'SORT_JOIN_TRANSPOSE', 'SORT_PROJECT_TRANSPOSE', 'UNION_MERGE', 'UNION_REMOVE', 'UNION_PULL_UP_CONSTANTS', 'UNION_TO_DISTINCT']


knobs = ["bitmapscan",
"gathermerge",
"hashagg",
"hashjoin",
"indexonlyscan",
"indexscan",
"material",
"mergejoin",
"nestloop",
"parallel_append",
"parallel_hash",
"partition_pruning",
"seqscan",
"sort",
"tidscan",]

with open("user_selected_knobs_as_apis.txt", "w") as f2:

    for rule in knobs:
        rule = rule.strip()
        #f2.write(template.replace("AGGREGATE_EXPAND_DISTINCT_AGGREGATES", rule))
        f2.write(template2.replace("bitmapscan", rule))