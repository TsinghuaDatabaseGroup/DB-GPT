import os

from configs import POSTGRESQL_CONFIG
from multiagents.utils.database import DBArgs, Database
import jpype as jp
import jpype.imports

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
                # print("Start the java jvm virtual environment successfully")
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
                res = SingleRewrite.singleRule(rule, query, POSTGRESQL_CONFIG.get('host'), str(POSTGRESQL_CONFIG.get('port')), POSTGRESQL_CONFIG.get('user'), POSTGRESQL_CONFIG.get('password'), POSTGRESQL_CONFIG.get('dbname'), "postgresql")
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

    dbargs = DBArgs("postgresql", config=POSTGRESQL_CONFIG)  # todo assign database name
    db = Database(dbargs, timeout=-1)
    new_query = data.get('rewritten_sql')
    new_query_plan = db.pgsql_query_plan(new_query)
    if new_query_plan is None:
        text_output = f"Failed to optimize the query. The new query is still {query}"
    else:
        total_cost, operators = db.query_plan_statistics(new_query_plan)
        text_output = f"New query is {new_query}\nNew query plan statistics: total cost is {total_cost}, and the operators are {operators}"
    return text_output

