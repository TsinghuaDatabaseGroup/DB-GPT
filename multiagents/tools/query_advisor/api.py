import os

from multiagents.utils.database import DBArgs, Database
import jpype as jp
import jpype.imports
from multiagents.tools.metrics import postgresql_conf

# tranformation rules (45)
# ['AGGREGATE_ANY_PULL_UP_CONSTANTS', 'AGGREGATE_EXPAND_DISTINCT_AGGREGATES', 'AGGREGATE_EXPAND_DISTINCT_AGGREGATES_TO_JOIN', 'AGGREGATE_JOIN_REMOVE', 'AGGREGATE_JOIN_TRANSPOSE_EXTENDED', 'AGGREGATE_UNION_TRANSPOSE', 'AGGREGATE_UNION_AGGREGATE', 'AGGREGATE_VALUES', 'AGGREGATE_PROJECT_MERGE', 'FILTER_INTO_JOIN', 'FILTER_MERGE', 'FILTER_AGGREGATE_TRANSPOSE', 'FILTER_PROJECT_TRANSPOSE', 'FILTER_TABLE_FUNCTION_TRANSPOSE', 'FILTER_SCAN', 'FILTER_CORRELATE', 'FILTER_SET_OP_TRANSPOSE', 'FILTER_REDUCE_EXPRESSIONS', 'JOIN_CONDITION_PUSH', 'JOIN_EXTRACT_FILTER', 'JOIN_PROJECT_BOTH_TRANSPOSE', 'JOIN_PROJECT_LEFT_TRANSPOSE', 'JOIN_PROJECT_RIGHT_TRANSPOSE', 'JOIN_REDUCE_EXPRESSIONS', 'JOIN_LEFT_UNION_TRANSPOSE', 'JOIN_RIGHT_UNION_TRANSPOSE', 'SEMI_JOIN_REMOVE', 'PROJECT_CALC_MERGE', 'PROJECT_CORRELATE_TRANSPOSE', 'PROJECT_REDUCE_EXPRESSIONS', 'PROJECT_SUB_QUERY_TO_CORRELATE', 'PROJECT_MERGE', 'PROJECT_REMOVE', 'PROJECT_TO_CALC', 'CALC_MERGE', 'CALC_REMOVE', 'SORT_UNION_TRANSPOSE', 'SORT_REMOVE', 'SORT_REMOVE_CONSTANT_KEYS', 'SORT_JOIN_TRANSPOSE', 'SORT_PROJECT_TRANSPOSE', 'UNION_MERGE', 'UNION_REMOVE', 'UNION_PULL_UP_CONSTANTS', 'UNION_TO_DISTINCT']

class java_rewrite(object):
    def __init__(self):
        self.start_jvm()
        pass

    def start_jvm(self):
        try:
            # 如果已经启动jvm的虚拟环境则跳过；否则进入else，启动java的虚拟环境
            if jpype.isJVMStarted():
                return True
            else:
                base_dir = os.path.abspath(os.curdir)
                local_lib_dir = os.path.join(base_dir+'/multiagents/tools/query_advisor/query_rewrite/', 'java_jar')
                _ = os.popen(
                    'mvn dependency:build-classpath -Dmdep.outputFile=classpath.txt').read()
                classpath = open(
                    os.path.join(
                        base_dir,
                        'classpath.txt'),
                    'r').readline().split(':')
                classpath.extend([os.path.join(local_lib_dir, jar)
                                  for jar in os.listdir(local_lib_dir)])
                jp.startJVM(jp.getDefaultJVMPath(), classpath=classpath)
                print("系统启动java的jvm虚拟环境成功")
                return True
        except Exception as e:
            print("系统启动java的jvm虚拟环境出现错误,错误原因:" + str(e))
            return False


    def stop_jvm(self):
        try:
            if jpype.isJVMStarted():
                jpype.shutdownJVM()
                print("关闭java的jvm虚拟环境成功")
        except Exception as e:
            print("关闭java的jvm虚拟环境出错,错误原因:" + str(e))
            return False

    def single_rule_rewrite(self, query, rule):
        try:
            if self.start_jvm():
                # 如果遇到签名问题，执行``` zip -d java_parser.jar 'META-INF/.SF' 'META-INF/.RSA' 'META-INF/*SF' ```
                SingleRewrite = jp.JClass("SingleRewrite")
                # String rule, String sql, String host, String port, String user, String passwd, String dbType/mysql/postgresql
                res = SingleRewrite.singleRule(rule, query, postgresql_conf.get('host'), str(postgresql_conf.get('port')), postgresql_conf.get('user'), postgresql_conf.get('password'), postgresql_conf.get('dbname'), "postgresql")
                return res
        except Exception as e:
            print("JAVA调用singleRule方法出错,错误原因:" + str(e))
            return {
                "status": False,
                "message": str(e)
            }

JavaRewrite = java_rewrite()

# 判断改写后语句是否有效
def rule_is_valid(rule, query):
    res = JavaRewrite.single_rule_rewrite(query, rule)
    data = res.get('data')

    if res is None or not res.get('status'):
        return f"Failed to optimize the query. error msg is {res.get('message')}"

    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    new_query = data.get('rewritten_sql')
    new_query_plan = db.pgsql_query_plan(new_query)
    if new_query_plan is None:
        text_output = f"Failed to optimize the query. The new query is still {query}"
    else:
        total_cost, operators = db.query_plan_statistics(new_query_plan)
        text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"
    return text_output


def AGGREGATE_ANY_PULL_UP_CONSTANTS_rule(query):
    return rule_is_valid("AGGREGATE_ANY_PULL_UP_CONSTANTS", query)


def AGGREGATE_EXPAND_DISTINCT_AGGREGATES_rule(query):
    return rule_is_valid("AGGREGATE_EXPAND_DISTINCT_AGGREGATES", query)


def AGGREGATE_EXPAND_DISTINCT_AGGREGATES_TO_JOIN_rule(query):
    return rule_is_valid("AGGREGATE_EXPAND_DISTINCT_AGGREGATES_TO_JOIN", query)


def AGGREGATE_JOIN_REMOVE_rule(query):
    return rule_is_valid("AGGREGATE_JOIN_REMOVE", query)


def AGGREGATE_JOIN_TRANSPOSE_EXTENDED_rule(query):
    return rule_is_valid("AGGREGATE_JOIN_TRANSPOSE_EXTENDED", query)


def AGGREGATE_UNION_TRANSPOSE_rule(query):
    return rule_is_valid("AGGREGATE_UNION_TRANSPOSE", query)


def AGGREGATE_UNION_AGGREGATE_rule(query):
    return rule_is_valid("AGGREGATE_UNION_AGGREGATE", query)


def AGGREGATE_VALUES_rule(query):
    return rule_is_valid("AGGREGATE_VALUES", query)


def AGGREGATE_PROJECT_MERGE_rule(query):
    return rule_is_valid("AGGREGATE_PROJECT_MERGE", query)


def FILTER_INTO_JOIN_rule(query):
    return rule_is_valid("FILTER_INTO_JOIN", query)


def FILTER_MERGE_rule(query):
    return rule_is_valid("FILTER_MERGE", query)


def FILTER_AGGREGATE_TRANSPOSE_rule(query):
    return rule_is_valid("FILTER_AGGREGATE_TRANSPOSE", query)


def FILTER_PROJECT_TRANSPOSE_rule(query):
    return rule_is_valid("FILTER_PROJECT_TRANSPOSE", query)


def FILTER_TABLE_FUNCTION_TRANSPOSE_rule(query):
    return rule_is_valid("FILTER_TABLE_FUNCTION_TRANSPOSE", query)


def FILTER_SCAN_rule(query):
    return rule_is_valid("FILTER_SCAN", query)


def FILTER_CORRELATE_rule(query):
    return rule_is_valid("FILTER_CORRELATE", query)


def FILTER_SET_OP_TRANSPOSE_rule(query):
    return rule_is_valid("FILTER_SET_OP_TRANSPOSE", query)


def FILTER_REDUCE_EXPRESSIONS_rule(query):
    return rule_is_valid("FILTER_REDUCE_EXPRESSIONS", query)


def JOIN_CONDITION_PUSH_rule(query):
    return rule_is_valid("JOIN_CONDITION_PUSH", query)


def JOIN_EXTRACT_FILTER_rule(query):
    return rule_is_valid("JOIN_EXTRACT_FILTER", query)


def JOIN_PROJECT_BOTH_TRANSPOSE_rule(query):
    return rule_is_valid("JOIN_PROJECT_BOTH_TRANSPOSE", query)


def JOIN_PROJECT_LEFT_TRANSPOSE_rule(query):
    return rule_is_valid("JOIN_PROJECT_LEFT_TRANSPOSE", query)


def JOIN_PROJECT_RIGHT_TRANSPOSE_rule(query):
    return rule_is_valid("JOIN_PROJECT_RIGHT_TRANSPOSE", query)


def JOIN_REDUCE_EXPRESSIONS_rule(query):
    return rule_is_valid("JOIN_REDUCE_EXPRESSIONS", query)


def JOIN_LEFT_UNION_TRANSPOSE_rule(query):
    return rule_is_valid("JOIN_LEFT_UNION_TRANSPOSE", query)


def JOIN_RIGHT_UNION_TRANSPOSE_rule(query):
    return rule_is_valid("JOIN_RIGHT_UNION_TRANSPOSE", query)


def SEMI_JOIN_REMOVE_rule(query):
    return rule_is_valid("SEMI_JOIN_REMOVE", query)


def PROJECT_CALC_MERGE_rule(query):
    return rule_is_valid("PROJECT_CALC_MERGE", query)


def PROJECT_CORRELATE_TRANSPOSE_rule(query):
    return rule_is_valid("PROJECT_CORRELATE_TRANSPOSE", query)


def PROJECT_REDUCE_EXPRESSIONS_rule(query):
    return rule_is_valid("PROJECT_REDUCE_EXPRESSIONS", query)


def PROJECT_SUB_QUERY_TO_CORRELATE_rule(query):
    return rule_is_valid("PROJECT_SUB_QUERY_TO_CORRELATE", query)


def PROJECT_MERGE_rule(query):
    return rule_is_valid("PROJECT_MERGE", query)


def PROJECT_REMOVE_rule(query):
    return rule_is_valid("PROJECT_REMOVE", query)


def PROJECT_TO_CALC_rule(query):
    return rule_is_valid("PROJECT_TO_CALC", query)


def CALC_MERGE_rule(query):
    return rule_is_valid("CALC_MERGE", query)


def CALC_REMOVE_rule(query):
    return rule_is_valid("CALC_REMOVE", query)


def SORT_UNION_TRANSPOSE_rule(query):
    return rule_is_valid("SORT_UNION_TRANSPOSE", query)


def SORT_REMOVE_rule(query):
    return rule_is_valid("SORT_REMOVE", query)


def SORT_REMOVE_CONSTANT_KEYS_rule(query):
    return rule_is_valid("SORT_REMOVE_CONSTANT_KEYS", query)


def SORT_JOIN_TRANSPOSE_rule(query):
    return rule_is_valid("SORT_JOIN_TRANSPOSE", query)


def SORT_PROJECT_TRANSPOSE_rule(query):
    return rule_is_valid("SORT_PROJECT_TRANSPOSE", query)


def UNION_MERGE_rule(query):
    return rule_is_valid("UNION_MERGE", query)


def UNION_REMOVE_rule(query):
    return rule_is_valid("UNION_REMOVE", query)


def UNION_PULL_UP_CONSTANTS_rule(query):
    return rule_is_valid("UNION_PULL_UP_CONSTANTS", query)


def UNION_TO_DISTINCT_rule(query):
    return rule_is_valid("UNION_TO_DISTINCT", query)


# query hints (15)
# ["bitmapscan",
# "gathermerge",
# "hashagg",
# "hashjoin",
# "indexonlyscan",
# "indexscan",
# "material",
# "mergejoin",
# "nestloop",
# "parallel_append",
# "parallel_hash",
# "partition_pruning",
# "seqscan",
# "sort",
# "tidscan",]

def enable_or_disable_bitmapscan_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_bitmapscan to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_bitmapscan knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the bitmapscan operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators}, after disabling the bitmapscan operator."

    return text_output


def enable_or_disable_gathermerge_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_gathermerge to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_gathermerge knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the gathermerge operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the gathermerge operator."

    return text_output


def enable_or_disable_hashagg_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_hashagg to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_hashagg knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the hashagg operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the hashagg operator."

    return text_output


def enable_or_disable_hashjoin_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_hashjoin to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_hashjoin knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the hashjoin operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the hashjoin operator."

    return text_output


def enable_or_disable_indexonlyscan_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_indexonlyscan to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_indexonlyscan knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the indexonlyscan operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the indexonlyscan operator."

    return text_output


def enable_or_disable_indexscan_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_indexscan to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_indexscan knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the indexscan operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the indexscan operator."

    return text_output


def enable_or_disable_material_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_material to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_material knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the material operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the material operator."

    return text_output


def enable_or_disable_mergejoin_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_mergejoin to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_mergejoin knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the mergejoin operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the mergejoin operator."

    return text_output


def enable_or_disable_nestloop_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_nestloop to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_nestloop knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the nestloop operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the nestloop operator."

    return text_output


def enable_or_disable_parallel_append_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_parallel_append to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_parallel_append knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the parallel_append operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the parallel_append operator."

    return text_output


def enable_or_disable_parallel_hash_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_parallel_hash to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_parallel_hash knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the parallel_hash operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the parallel_hash operator."

    return text_output


def enable_or_disable_partition_pruning_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_partition_pruning to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_partition_pruning knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the partition_pruning operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the partition_pruning operator."

    return text_output


def enable_or_disable_seqscan_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_seqscan to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_seqscan knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the seqscan operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the seqscan operator."

    return text_output


def enable_or_disable_sort_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_sort to \"{action}\"; " + query.replace("\n", "")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_sort knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the sort operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the sort operator."

    return text_output


def enable_or_disable_tidscan_operator(action: str, query: str):
    dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    # add hint to the query
    new_query = f"set enable_tidscan to \"{action}\"; " + query.replace("\n", " ")

    # execute the new query
    new_query_plan = db.pgsql_query_plan(new_query)

    if new_query_plan is None:
        # raise error
        raise Exception(
            status_code=400,
            detail=f"Failed to explain the query after changing the enable_tidscan knob.")
    else:
        if action == "ON":
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after enabling the tidscan operator."
        else:
            total_cost, operators = db.query_plan_statistics(
                new_query_plan)
            text_output = f"The new query plan statistics: total cost is {total_cost} and the operators are {operators},  after disabling the tidscan operator."

    return text_output
