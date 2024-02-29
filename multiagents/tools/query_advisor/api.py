from configs import POSTGRESQL_CONFIG
from multiagents.utils.database import DBArgs, Database
from multiagents.tools.query_advisor.rewrite_class import rule_is_valid

REWRITE_RULES = [
    "AGGREGATE_ANY_PULL_UP_CONSTANTS",
    "AGGREGATE_EXPAND_DISTINCT_AGGREGATES",
    "AGGREGATE_EXPAND_DISTINCT_AGGREGATES_TO_JOIN",
    "AGGREGATE_JOIN_REMOVE",
    "AGGREGATE_JOIN_TRANSPOSE_EXTENDED",
    "AGGREGATE_UNION_TRANSPOSE",
    "AGGREGATE_UNION_AGGREGATE",
    "AGGREGATE_VALUES",
    "AGGREGATE_PROJECT_MERGE",
    "FILTER_INTO_JOIN",
    "FILTER_MERGE",
    "FILTER_AGGREGATE_TRANSPOSE",
    "FILTER_PROJECT_TRANSPOSE",
    "FILTER_TABLE_FUNCTION_TRANSPOSE",
    "FILTER_SCAN",
    "FILTER_CORRELATE",
    "FILTER_SET_OP_TRANSPOSE",
    "FILTER_REDUCE_EXPRESSIONS",
    "JOIN_CONDITION_PUSH",
    "JOIN_EXTRACT_FILTER",
    "JOIN_PROJECT_BOTH_TRANSPOSE",
    "JOIN_PROJECT_LEFT_TRANSPOSE",
    "JOIN_PROJECT_RIGHT_TRANSPOSE",
    "JOIN_REDUCE_EXPRESSIONS",
    "JOIN_LEFT_UNION_TRANSPOSE",
    "JOIN_RIGHT_UNION_TRANSPOSE",
    "SEMI_JOIN_REMOVE",
    "PROJECT_CALC_MERGE",
    "PROJECT_CORRELATE_TRANSPOSE",
    "PROJECT_REDUCE_EXPRESSIONS",
    "PROJECT_SUB_QUERY_TO_CORRELATE",
    "PROJECT_MERGE",
    "PROJECT_REMOVE",
    "PROJECT_TO_CALC",
    "CALC_MERGE",
    "CALC_REMOVE",
    "SORT_UNION_TRANSPOSE",
    "SORT_REMOVE",
    "SORT_REMOVE_CONSTANT_KEYS",
    "SORT_JOIN_TRANSPOSE",
    "SORT_PROJECT_TRANSPOSE",
    "UNION_MERGE",
    "UNION_REMOVE",
    "UNION_PULL_UP_CONSTANTS",
    "UNION_TO_DISTINCT",
]
KNOB_OPERATORS = [
    "bitmapscan",
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
    "tidscan"
]

FUNCTION_DEFINITION = {
    "sql_rewrite_based_on_rule": {
        "name": "sql_rewrite_based_on_rule",
        "description": "给定sql和改写规则，判断改写是否有效。有效则返回改写后的sql，否则返回原sql。",
        "parameters": {
            "type": "object",
            "properties": {
                "rule": {
                    "type": "string",
                    "enum": REWRITE_RULES,
                    "description": "改写规则，根据上下文信息推理出它。",
                },
                "query": {
                    "type": "string",
                    "description": "需要改写的sql",
                },
            },
            "required": ["rule", "query"],
        },
    },
    "explain_query_after_changing_knob": {
        "name": "explain_query_after_changing_knob",
        "description": "启用或禁用某个算子，返回解释的查询计划。",
        "parameters": {
            "type": "object",
            "properties": {
                "operator": {
                    "type": "string",
                    "enum": KNOB_OPERATORS,
                    "description": "算子名称",
                },
                "action": {
                    "type": "string",
                    "enum": ["on", "off"],
                    "description": "启用或禁用",
                },
                "query": {
                    "type": "string",
                    "description": "给定的sql",
                }
            },
            "required": ["operator", "action", "query"]
        },
    }
}


def sql_rewrite_based_on_rule(rule, query):
    return rule_is_valid(rule, query)


def explain_query_after_changing_knob(operator, action, query):
    dbargs = DBArgs("postgresql", config=POSTGRESQL_CONFIG)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_{operator} to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        text_output = f"Failed to explain the query after changing the {operator} knob."
    else:
        if "on" in action.lower():
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the {operator} operator."
        else:
            total_cost, operators = db.query_plan_statistics(new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators}, after disabling the {operator} operator."

    return text_output
