import psycopg2
import pymysql
import json
import logging
import os
from enum import IntEnum
import time
import random
from multiprocessing.pool import *

DB_CONFIG = {
    "dbname":"sysbench",  # 连接到默认的 "postgres" 数据库
    "user":"test",  # 替换为你的数据库用户名
    "password":"Test123_456",  # 替换为你的数据库密码
    "host":"localhost",  # 替换为你的数据库主机地址
    "port": 5432,
    # "dbtype": "postgresql"
    }

SERVER_CONFIG = {
    "host": "localhost",
    "port": 22,
    "user": 'root',
    "password": 'xxxx'
}


def extract_node_types(json_tree):
    node_types = []
    
    def traverse_tree(node):
        if isinstance(node, dict):
            if 'Node Type' in node:
                node_types.append(node['Node Type'])
            for key, value in node.items():
                traverse_tree(value)
        elif isinstance(node, list):
            for item in node:
                traverse_tree(item)
    
    traverse_tree(json_tree)
    return node_types

class DataType(IntEnum):
    VALUE = 0
    TIME = 1
    CHAR = 2

AGGREGATE_CONSTRAINTS = {
    DataType.VALUE.value: ['count', 'max', 'min', 'avg', 'sum'],
    DataType.VALUE.CHAR: ['count', 'max', 'min'],
    DataType.VALUE.TIME: ['count', 'max', 'min']
}

def check_index_exist(cursor, index_name):
        try:
            cursor.execute(f"SELECT indexname FROM pg_indexes WHERE indexname = '{index_name}';")
            result = cursor.fetchone()
            return result is not None
        except psycopg2.Error as e:
            print(f"Error checking index: {e}")
            return False

def transfer_field_type(column_type, server):
    data_type = list()
    if server == 'mysql':
        data_type = [['int', 'tinyint', 'smallint', 'mediumint', 'bigint', 'float', 'double', 'decimal'],
                     ['date', 'time', 'year', 'datetime', 'timestamp']]
        column_type = column_type.lower().split('(')[0]
    elif server == 'postgresql':
        data_type = [['integer', 'numeric'],
                     ['date']]

    if column_type in data_type[0]:
        return DataType.VALUE.value
    elif column_type in data_type[1]:
        return DataType.TIME.value
    else:
        return DataType.CHAR.value


class DBArgs(object):

    def __init__(self, dbtype, config, dbname=None,application_name=None):
        self.dbtype = dbtype
        if self.dbtype == 'mysql':
            self.host = config['host']
            self.port = config['port']
            self.user = config['user']
            self.password = config['password']
            self.dbname = dbname if dbname else config['dbname']
            self.driver = 'com.mysql.jdbc.Driver'
            self.jdbc = 'jdbc:mysql://'
        else:
            self.host = config['host']
            self.port = config['port']
            self.user = config['user']
            self.password = config['password']
            self.dbname = dbname if dbname else config['dbname']
            self.driver = 'org.postgresql.Driver'
            self.jdbc = 'jdbc:postgresql://'
            self.application_name = application_name


class Database():
    def __init__(self, args, timeout=-1):
        self.args = args
        self.conn = self.resetConn(timeout)
        # self.schema = self.compute_table_schema()

    def resetConn(self, timeout=-1):
        if self.args.dbtype == 'mysql':
                conn = pymysql.connect(
                host=self.args.host,
                user=self.args.user,
                passwd=self.args.password,
                database=self.args.dbname,
                port=int(self.args.port),
                charset='utf8',
                connect_timeout=timeout,
                read_timeout=timeout,
                write_timeout=timeout)
        elif self.args.dbtype == 'postgresql':
            if timeout > 0:
                conn = psycopg2.connect(database=self.args.dbname,
                                            user=self.args.user,
                                            password=self.args.password,
                                            host=self.args.host,
                                            port=self.args.port,
                                            options='-c statement_timeout={}s'.format(timeout),
                                            application_name=self.args.application_name)
            else:
                
                conn = psycopg2.connect(database=self.args.dbname,
                                            user=self.args.user,
                                            password=self.args.password,
                                            host=self.args.host,
                                            port=self.args.port,
                                            application_name=self.args.application_name)

        return conn
    '''
    def exec_fetch(self, statement, one=True):
        cur = self.conn.cursor()
        cur.execute(statement)
        if one:
            return cur.fetchone()
        return cur.fetchall()    
    '''

    def execute_sql(self, sql):
        fail = 1
        self.conn = self.resetConn(timeout=-1)
        cur = self.conn.cursor()
        i = 0
        cnt = 5 # retry times
        while fail == 1 and i < cnt:
            try:
                fail = 0
                # print("========== start execution", i)
                cur.execute(sql)
            except BaseException:
                fail = 1
                time.sleep(1)
            res = []
            if fail == 0:
                res = cur.fetchall()
            i = i + 1
        logging.debug('database {}, return flag {}, execute sql {}\n'.format(self.args.dbname, 1 - fail, sql))

        cur.close()
        self.conn.close()

        # print("========== finish time:", time.time())

        if fail == 1:
            # raise RuntimeError("Database query failed")
            # print("SQL Execution Fatal!!")

            return 0, ''
        elif fail == 0:
            # print("SQL Execution Succeed!!")

            return 1, res

    def pgsql_results(self, sql):
        try:
            #success, res = self.execute_sql('explain (FORMAT JSON, analyze) ' + sql)
            success, res = self.execute_sql(sql)
            #print("pgsql_results", success, res)
            if success == 1:
                return res
            else:
                return "<fail>"
        except Exception as error:
            logging.error('pgsql_results Exception', error)
            return "<fail>"

    def pgsql_query_plan(self, sql):
        try:
            #success, res = self.execute_sql('explain (FORMAT JSON, analyze) ' + sql)

            # sql starts with "set"
            if sql.startswith("set"): # hint query
                sqls = sql.split(";")
                sql = sqls[0] + ';' + ' explain (FORMAT JSON) ' + sqls[1]
            else:
                sql = 'explain (FORMAT JSON) ' + sql
            
            success, res = self.execute_sql(sql)
            if success == 1:
                plan = res[0][0][0]['Plan']
                return plan
            else:
                logging.error('pgsql_query_plan Fails!')
                return None
        except Exception as error:
            logging.error('pgsql_query_plan Exception', error)
            return None

    def query_plan_statistics(self, plan):
        operators = extract_node_types(plan)

        return plan['Total Cost'], operators


    def pgsql_cost_estimation(self, sql):
        try:
            #success, res = self.execute_sql('explain (FORMAT JSON, analyze) ' + sql)
            success, res = self.execute_sql('explain (FORMAT JSON) ' + sql)
            if success == 1:
                cost = res[0][0][0]['Plan']['Total Cost']
                return cost
            else:
                logging.error('pgsql_cost_estimation Fails!')
                return 0
        except Exception as error:
            logging.error('pgsql_cost_estimation Exception', error)
            return 0

    def pgsql_actual_time(self, sql):
        try:
            #success, res = self.execute_sql('explain (FORMAT JSON, analyze) ' + sql)
            success, res = self.execute_sql('explain (FORMAT JSON, analyze) ' + sql)
            if success == 1:
                cost = res[0][0][0]['Plan']['Actual Total Time']
                return cost
            else:
                return -1
        except Exception as error:
            logging.error('pgsql_actual_time Exception', error)
            return -1

    def mysql_cost_estimation(self, sql):
        try:
            success, res = self.execute_sql('explain format=json ' + sql)
            if success == 1:
                total_cost = self.get_mysql_total_cost(0, json.loads(res[0][0]))
                return float(total_cost)
            else:
                return -1
        except Exception as error:
            logging.error('mysql_cost_estimation Exception', error)
            return -1

    def get_mysql_total_cost(self, total_cost, res):
        if isinstance(res, dict):
            if 'query_cost' in res.keys():
                total_cost += float(res['query_cost'])
            else:
                for key in res:
                    total_cost += self.get_mysql_total_cost(0, res[key])
        elif isinstance(res, list):
            for i in res:
                total_cost += self.get_mysql_total_cost(0, i)

        return total_cost

    def get_tables(self):
        if self.args.dbtype == 'mysql':
            return self.mysql_get_tables()
        else:
            return self.pgsql_get_tables()

    # query cost estimated by the optimizer
    def cost_estimation(self, sql):
        if self.args.dbtype == 'mysql':
            return self.mysql_cost_estimation(sql)
        else:
            return self.pgsql_cost_estimation(sql)

    def compute_table_schema(self):
        """
        schema: {table_name: [field_name]}
        :param cursor:
        :return:
        """

        if self.args.dbtype == 'postgresql':
            # cur_path = os.path.abspath('.')
            # tpath = cur_path + '/sampled_data/'+dbname+'/schema'
            sql = 'SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\';'
            success, res = self.execute_sql(sql)
            #print("======== tables", res)
            if success == 1:                
                tables = res
                schema = {}
                for table_info in tables:
                    table_name = table_info[0]
                    sql = 'SELECT column_name, data_type FROM information_schema.columns WHERE table_name = \'' + table_name + '\';'
                    success, res = self.execute_sql(sql)
                    #print("======== table columns", res)
                    columns = res
                    schema[table_name] = []
                    for col in columns:

                        ''' compute the distinct value ratio of the column
                        
                        if transfer_field_type(col[1], self.args.dbtype) == DataType.VALUE.value:
                            sql = 'SELECT count({}) FROM {};'.format(col[0], table_name)
                            success, res = self.execute_sql(sql)
                            print("======== column rows", res)
                            num = res
                            if num[0][0] != 0:
                                schema[table_name].append(col[0])
                        '''

                        #schema[table_name].append("column {} is of {} type".format(col[0], col[1]))
                        schema[table_name].append("{}".format(col[0]))
                '''
                with open(tpath, 'w') as f:
                    f.write(str(schema))
                '''
                #print(schema)
                return schema

            else:
                logging.error('pgsql_cost_estimation Fails!')
                return 0

    def simulate_index(self, index):
        #table_name = index.table()
        statement = (
            "SELECT * FROM hypopg_create_index(E'{}');".format(index)
        )
        result = self.execute_sql(statement)

        return result

    def obtain_historical_queries_statistics(self, topn = 50):
        try:
            #success, res = self.execute_sql('explain (FORMAT JSON, analyze) ' + sql)
            #command = "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 2;"
            
            command = f"SELECT s.query, s.calls, s.total_time, d.datname FROM pg_stat_statements s JOIN pg_database d ON s.dbid = d.oid ORDER BY s.total_time DESC LIMIT {topn};"
            success, res = self.execute_sql(command)
            if success == 1:
                slow_queries = []
                for sql_stat in res:
                    if not "postgres" in sql_stat[3]:
                        sql_template = sql_stat[0].replace("\n", "").replace("\t", "").strip()
                        # print("===== logged slow query: ", sql_template,sql_stat[1],sql_stat[2],sql_stat[3])
                        sql_template = sql_template.lower()
                        if "explain" in sql_template or "analyze" in sql_template:
                            continue

                        slow_queries.append({"sql": sql_template, "calls": sql_stat[1], "total_time": sql_stat[2], "dbname": sql_stat[3]})
                        
                return slow_queries
            else:
                logging.error('obtain_historical_queries_statistics Fails!')
                return 0
        except Exception as error:
            logging.error('obtain_historical_queries_statistics Exception', error)
            return 0        

    def drop_simulated_index(self, oid):
        statement = f"select * from hypopg_drop_index({oid})"
        result = self.execute_sql(statement)

        assert result[0] is True, f"Could not drop simulated index with oid = {oid}."

    def execute_sqls(self,sql):
        self.conn =self.resetConn(timeout=-1)
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        cur.close()
        self.conn.close()

    def execute_sql_duration(self, duration, sql, max_id=0, commit_interval=500):
        self.conn = self.resetConn(timeout=-1)
        cursor = self.conn.cursor()
        start = time.time()
        cnt = 0
        if duration > 0:
            while (time.time() - start) < duration:
                if max_id > 0:
                    id = random.randint(1, max_id - 1)
                    cursor.execute(sql + str(id) + ';')
                else:
                    cursor.execute(sql)
                cnt += 1
                if cnt % commit_interval == 0:
                    self.conn.commit()
        else:
            print("error, the duration should be larger than 0")
        self.conn.commit()
        cursor.close()
        self.conn.close()
        return cnt

    def concurrent_execute_sql(self, threads, duration, sql, max_id=0, commit_interval=500):
        pool = ThreadPool(threads)
        results = [pool.apply_async(self.execute_sql_duration, (duration, sql, max_id, commit_interval)) for _ in range(threads)]
        pool.close()
        pool.join()
        return results
    

        
    def build_index(self, table_name, idx_num):
        self.conn = self.resetConn(timeout=-1)
        cursor = self.conn.cursor()
    
        for i in range(0, idx_num):
            the_sql = 'CREATE INDEX index_' + table_name + '_' + str(i) + ' ON ' + table_name + '(name' + str(i) + ');'
            print(the_sql)
            cursor.execute(the_sql)

        # 检查索引是否创建成功
            #if check_index_exist(cursor, 'index_' + table_name + '_' + str(i)):
                #print(f'Index index_{table_name}_{i} created successfully.')
            #else:
                #print(f'Failed to create index index_{table_name}_{i}.')
    
        self.conn.commit()
        self.conn.close()
        return


    
    def drop_index(self,table_name):
        self.conn = self.resetConn(timeout=-1)
        cursor = self.conn.cursor()
        cursor.execute("select indexname from pg_indexes where tablename='"+table_name+"';")
        idxs = cursor.fetchall()
        for idx in idxs:
            the_sql = 'DROP INDEX ' + idx[0] + ';'
            cursor.execute(the_sql)
            print(the_sql)
        self.conn.commit()
        self.conn.close()
        return
