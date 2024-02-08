import subprocess
import createdatabase
import dropdatabase
import psycopg2
import sys
sys.path.append('/root/DB-GPT/')
import time
import datetime
import random
import yaml
from multiprocessing.pool import *


class DBArgs(object):

    def __init__(self, dbtype, config, dbname=None):
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

class Database():
    def __init__(self, args, timeout=-1):
        self.args = args
        self.conn = self.resetConn(timeout)


        # self.schema = self.compute_table_schema()

    def resetConn(self, timeout=-1):
        conn = psycopg2.connect(database=self.args.dbname,
                                            user=self.args.user,
                                            password=self.args.password,
                                            host=self.args.host,
                                            port=self.args.port)
        return conn

    
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
    
def init():
    #add the config
    config_path = "/root/DB-GPT/config/tool_config.yaml"
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file) 
    db_args =DBArgs('pgsql', config)
    return db_args


#create a table
def create_table(table_name,colsize, ncolumns):
    db=Database(init())
    column_definitions = ', '.join(f'name{i} varchar({colsize})' for i in range(ncolumns))
    creat_sql = f'CREATE TABLE {table_name} (id int, {column_definitions}, time timestamp);'
    db.execute_sqls(creat_sql)

#delete the table
def delete_table(table_name):
    db=Database(init())
    delete_sql=f'DROP TABLE if exists {table_name}'
    db.execute_sqls(delete_sql)

def run_command(command):
    """运行给定的命令"""
    process = subprocess.Popen(command, shell=True)
    return process

def main():
    # 定义要运行的命令
    command1 = "python anomaly_trigger/miss_multi.py"
    command2 = "python anomaly_trigger/insert_multi.py"
    dropdatabase.dropdatabase("tmp")
    createdatabase.createdatabase("tmp")
    # 同时启动两个进程
    table_name="table1"
    delete_table(table_name)
    create_table(table_name,1000, 1000)
    process1 = run_command(command1)
    process2 = run_command(command2)

    # 等待进程完成
    process1.wait()
    process2.wait()
    print("Both processes have finished.")
    dropdatabase.dropdatabase("tmp")
if __name__ == "__main__":
    main()
