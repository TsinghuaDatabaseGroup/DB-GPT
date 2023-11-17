import re
with open('missingindex2.txt', 'r') as file:
    # 逐行读取文件并将每一行作为字符串添加到列表中
    lines = [line.strip() for line in file]
# 输入的字符串
for line in lines:
    input_string = f"{line}"
    anomaly_match = re.search(r'--anomaly\s+([^\s]+)', input_string)
    anomaly = str(anomaly_match.group(1)) if anomaly_match else None
    threads_match = re.search(r'--threads (\d+)', input_string)
    ncolumn_match = re.search(r'--ncolumn (\d+)', input_string)
    colsize_match = re.search(r'--colsize (\d+)', input_string)
    nrow_match = re.search(r'--nrow (\d+)', input_string)
    duration_match=re.search(r'--duration (\d+)', input_string)
        # 提取的数字存入变量
    threads = int(threads_match.group(1)) if threads_match else None
    ncolumn = int(ncolumn_match.group(1)) if ncolumn_match else None
    colsize = int(colsize_match.group(1)) if colsize_match else None
    nrow = int(nrow_match.group(1)) if nrow_match else None
    duration=int(duration_match.group(1)) if duration_match else None
    if anomaly == 'INSERT_LARGE_DATA':
        # 打印提取的数字
        code=f'''import psycopg2
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
    column_definitions = ', '.join(f'name{{i}} varchar({{colsize}})' for i in range(ncolumns))
    creat_sql = f'CREATE TABLE {{table_name}} (id int, {{column_definitions}}, time timestamp);'
    db.execute_sqls(creat_sql)

#delete the table
def delete_table(table_name):
    db=Database(init())
    delete_sql=f'DROP TABLE if exists {{table_name}}'
    db.execute_sqls(delete_sql)

#print the current time
def print_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(formatted_time)


def insert_large_data(threads,duration,ncolumns,nrows,colsize,table_name='table1'):

    print_time()
    #Delete undeleted tables
    delete_table(table_name)
    #create a new table
    create_table(table_name,colsize, ncolumns)
    db=Database(init())
    #insert the data
    #insert_definitions = ', '.join(f'repeat(round(random()*999)::text,{{(colsize//3)}})' for i in range(ncolumns))
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {{colsize}}))' for i in range(ncolumns))
    insert_data=f'insert into {{table_name}} select generate_series(1,{{nrows}}),{{insert_definitions}}, now();'
    db.concurrent_execute_sql(threads,duration,insert_data,commit_interval=1)

    #delete the table
    delete_table(table_name)
    
    #print the end time
    print_time()
if __name__ == "__main__":
    # Number of threads to use for concurrent inserts
    num_threads = {threads}
    
    # Duration for which to run the inserts (in seconds)
    insert_duration = {duration}
    
    # Number of columns in the table
    num_columns = {ncolumn}
    
    # Number of rows to insert
    num_rows = {nrow}
    
    # Size of each column (in characters)
    column_size = {colsize}
    
    # Table name
    table_name = 'table1'
    
    # Call the insert_large_data function
    insert_large_data(num_threads, insert_duration, num_columns, num_rows, column_size, table_name)\n\n\n\n'''
    if anomaly == 'MISSING_INDEXES':
        code=f'''import psycopg2
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
    column_definitions = ', '.join(f'name{{i}} varchar({{colsize}})' for i in range(ncolumns))
    creat_sql = f'CREATE TABLE {{table_name}} (id int, {{column_definitions}}, time timestamp);'
    db.execute_sqls(creat_sql)

#delete the table
def delete_table(table_name):
    db=Database(init())
    delete_sql=f'DROP TABLE if exists {{table_name}}'
    db.execute_sqls(delete_sql)

#print the current time
def print_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(formatted_time)


def missing_index(threads,duration,ncolumns,nrows,colsize,table_name='table1'):
    #create a new table
    print_time()
    db=Database(init())
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)

    # insert some data to be selected 
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {{colsize}}))' for i in range(ncolumns))
    insert_data=f'insert into {{table_name}} select generate_series(1,{{nrows}}),{{insert_definitions}}, now();'
    db.execute_sqls(insert_data)  

    #select without the index
    missing_index='select * from '+table_name+' where id='
    db.concurrent_execute_sql(threads,duration,missing_index,nrows)

    #delete the table
    delete_table(table_name)
    #print the end time
    print_time()

if __name__ == "__main__":
    # Number of threads to use for concurrent inserts
    num_threads = {threads}
    
    # Duration for which to run the inserts (in seconds)
    insert_duration = {duration}
    
    # Number of columns in the table
    num_columns = {ncolumn}
    
    # Number of rows to insert
    num_rows = {nrow}
    
    # Size of each column (in characters)
    column_size = {colsize}
    
    # Table name
    table_name = 'table1'
    
    # Call the insert_large_data function
    missing_index(num_threads, insert_duration, num_columns, num_rows, column_size, table_name)\n\n\n\n'''

    if anomaly == 'VACUUM':
        code=f'''import psycopg2
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
    column_definitions = ', '.join(f'name{{i}} varchar({{colsize}})' for i in range(ncolumns))
    creat_sql = f'CREATE TABLE {{table_name}} (id int, {{column_definitions}}, time timestamp);'
    db.execute_sqls(creat_sql)

#delete the table
def delete_table(table_name):
    db=Database(init())
    delete_sql=f'DROP TABLE if exists {{table_name}}'
    db.execute_sqls(delete_sql)

#print the current time
def print_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(formatted_time)


def vacuum(threads,duration,ncolumns,nrows,colsize,table_name='table1'):
    db=Database(init())
    #create a new table
    print_time()
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)

    # insert some data to be deleted
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {{colsize}}))' for i in range(ncolumns))
    insert_data=f'insert into {{table_name}} select generate_series(1,{{nrows}}),{{insert_definitions}}, now();' 
    db.execute_sqls(insert_data) 

    # delete 80% of the rows
    delete_nrows=int(nrows*0.8)
    vacuum=f'delete from {{table_name}} where id < {{delete_nrows}};'
    db.execute_sqls(vacuum)

    # do the select , then the vacuum occurs
    select='select * from '+table_name+' where id='
    db.concurrent_execute_sql(threads,duration,select,nrows)

    #delete the table
    delete_table(table_name)
    print_time()


if __name__ == "__main__":
    # Number of threads to use for concurrent inserts
    num_threads = {threads}
    
    # Duration for which to run the inserts (in seconds)
    insert_duration = {duration}
    
    # Number of columns in the table
    num_columns = {ncolumn}
    
    # Number of rows to insert
    num_rows = {nrow}
    
    # Size of each column (in characters)
    column_size = {colsize}
    
    # Table name
    table_name = 'table1'
    
    # Call the insert_large_data function
    vacuum(num_threads, insert_duration, num_columns, num_rows, column_size, table_name)\n\n\n\n'''

    if anomaly == 'LOCK_CONTENTION':
        code=f'''import psycopg2
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
    column_definitions = ', '.join(f'name{{i}} varchar({{colsize}})' for i in range(ncolumns))
    creat_sql = f'CREATE TABLE {{table_name}} (id int, {{column_definitions}}, time timestamp);'
    db.execute_sqls(creat_sql)

#delete the table
def delete_table(table_name):
    db=Database(init())
    delete_sql=f'DROP TABLE if exists {{table_name}}'
    db.execute_sqls(delete_sql)

#print the current time
def print_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(formatted_time)


def lock_contention(threads,duration,ncolumns,nrows,colsize,table_name='table1'):
    #create a new table
    print_time()
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)
    db=Database(init())
    # insert some data to be updated 
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {{colsize}}))' for i in range(ncolumns))
    insert_data=f'insert into {{table_name}} select generate_series(1,{{nrows}}),{{insert_definitions}}, now();' 
    db.execute_sqls(insert_data) 
    pool = Pool(threads)
    for _ in range(threads):
        pool.apply_async(
            lock, (table_name, ncolumns, colsize, duration, nrows))
    pool.close()
    pool.join()
    #delete the table
    delete_table(table_name)
    print_time()

def lock(table_name, ncolumns, colsize, duration, nrows):
    args=init()
    start = time.time()
    #lock_contention
    while time.time()-start < duration:
        conn = psycopg2.connect(database=args.dbname, user=args.user, password=args.password,
                                        host=args.host, port=args.port)
        cur = conn.cursor()
        while time.time()-start < duration:
            col_name = random.randint(0, ncolumns-1)
            row_name = random.randint(1, nrows-1)
            lock_contention = f'update {{table_name}} set name{{col_name}}=(SELECT substr(md5(random()::text), 1, {{colsize}})) where id ={{row_name}}'
            #db.concurrent_execute_sql(threads,duration,lock_contention,nrows)
            cur.execute(lock_contention)
            conn.commit()
        conn.commit()
        conn.close()

if __name__ == "__main__":
    # Number of threads to use for concurrent inserts
    num_threads = {threads}
    
    # Duration for which to run the inserts (in seconds)
    insert_duration = {duration}
    
    # Number of columns in the table
    num_columns = {ncolumn}
    
    # Number of rows to insert
    num_rows = {nrow}
    
    # Size of each column (in characters)
    column_size = {colsize}
    
    # Table name
    table_name = 'table1'
    
    # Call the insert_large_data function
    lock_contention(num_threads, insert_duration, num_columns, num_rows, column_size, table_name)\n\n\n\n'''

    if anomaly == 'REDUNDANT_INDEX':
        code=f'''import psycopg2
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
    
    def build_index(self, table_name, idx_num):
        self.conn = self.resetConn(timeout=-1)
        cursor = self.conn.cursor()
        
        for i in range(0, idx_num):
            the_sql = 'CREATE INDEX index_' + table_name + '_' + str(i) + ' ON ' + table_name + '(name' + str(i) + ');'
            print(the_sql)
            cursor.execute(the_sql)

        
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
    column_definitions = ', '.join(f'name{{i}} varchar({{colsize}})' for i in range(ncolumns))
    creat_sql = f'CREATE TABLE {{table_name}} (id int, {{column_definitions}}, time timestamp);'
    db.execute_sqls(creat_sql)

#delete the table
def delete_table(table_name):
    db=Database(init())
    delete_sql=f'DROP TABLE if exists {{table_name}}'
    db.execute_sqls(delete_sql)

#print the current time
def print_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(formatted_time)

def redundent_index(threads,duration,ncolumns,nrows,colsize,nindex,table_name='table1'):
    #create a new table
    print_time()
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)
    db=Database(init())
    # insert some data to be updated 
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {{colsize}}))' for i in range(ncolumns))
    insert_data=f'insert into {{table_name}} select generate_series(1,{{nrows}}),{{insert_definitions}}, now();' 
    db.execute_sqls(insert_data) 

    #initialization of the indexes
    nindex=int((nindex*ncolumns)/10)
    db.build_index(table_name,nindex)
    id_index='CREATE INDEX index_'+table_name+'_id ON '+table_name+'(id);'
    db.execute_sqls(id_index)

    #lock_contention
    pool = Pool(threads)
    for _ in range(threads):
        pool.apply_async(
            lock, (table_name, ncolumns, colsize, duration, nrows))
    pool.close()
    pool.join()

    #drop the index
    db.drop_index(table_name)

    #delete the table
    delete_table(table_name)
    print_time()


def lock(table_name, ncolumns, colsize, duration, nrows):
    args=init()
    start = time.time()
    #lock_contention
    while time.time()-start < duration:
        conn = psycopg2.connect(database=args.dbname, user=args.user, password=args.password,
                                        host=args.host, port=args.port)
        cur = conn.cursor()
        while time.time()-start < duration:
            col_name = random.randint(0, ncolumns-1)
            row_name = random.randint(1, nrows-1)
            lock_contention = f'update {{table_name}} set name{{col_name}}=(SELECT substr(md5(random()::text), 1, {{colsize}})) where id ={{row_name}}'
            #db.concurrent_execute_sql(threads,duration,lock_contention,nrows)
            cur.execute(lock_contention)
            conn.commit()
        conn.commit()
        conn.close()

if __name__ == "__main__":
    # Number of threads to use for concurrent inserts
    num_threads = {threads}
    
    # Duration for which to run the inserts (in seconds)
    insert_duration = {duration}
    
    # Number of columns in the table
    num_columns = {ncolumn}
    
    # Number of rows to insert
    num_rows = {nrow}
    
    # Size of each column (in characters)
    column_size = {colsize}
    
    # Table name
    table_name = 'table1'
    
    nindex=6
    
    # Call the insert_large_data function
    redundent_index(num_threads, insert_duration, num_columns, num_rows, column_size, nindex,table_name)\n\n\n\n'''
        
    if anomaly == 'INSERT_LARGE_DATA,IO_CONTENTION':
        code=f'''import os
import datetime

#print the current time
def print_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(formatted_time)

if __name__ == "__main__":
    print_time()
    command = (
    "su - root -c 'cd /sysbench-tpcc-master; "
    "./tpcc.lua --db-driver=pgsql --tables=2 --scale=3 --threads=50 --events=0 "
    "--pgsql-host=xxxx --pgsql-user=xxxx --pgsql-password=xxxx "
    "--pgsql-port=5432 --pgsql-db=tpcc --time=90 --rand-type=uniform --report-interval=10 run'"
    )

    os.system(command)
    print_time()\n\n\n\n'''
    if anomaly == 'FETCH_LARGE_DATA,CORRELATED_SUBQUERY':
        # 打印提取的数字
        code=f'''import os
import re
import time

import psycopg2


REPEATCOUNT = 1
TIMELOGPATH = str(int(time.time())) + "_tpch_trigger_time_log.txt"
TIMELOG = open(TIMELOGPATH, 'w+')


class Database():

    def __init__(self):
        self.conn = None
        self.conn = psycopg2.connect(database='tpch',
                                     user='xxxx',
                                     password='xxxx',
                                     host='xxxx',
                                     port=5432)

    def execute_sql(self, sql):
        fail = 1
        cur = self.conn.cursor()
        i = 0
        cnt = 3
        while fail == 1 and i < cnt:
            try:
                fail = 0
                cur.execute(sql)
            except BaseException as error:
                fail = 1
                print(error)
            res = []
            if fail == 0:
                res = cur.fetchall()
            i = i + 1
        if fail == 1:
            # print("SQL Execution Fatal!!", sql)
            return 0, ''
        elif fail == 0:
            return 1, res


def all_sql_files():
    res_path = "{{}}/tpch-queries/".format(
        os.path.dirname(os.path.abspath(__file__)))
    # all_file_list = list(filter(file_filter, os.listdir(res_path)))
    # all_file_list = sorted(all_file_list, key=custom_sort)
    all_file_list = [
        '4.explain.sql']

    print(all_file_list)
    files_list = []
    for file in all_file_list:
        files_list.append(res_path + file)
    return files_list


def custom_sort(item):
    # 提取数字和字母部分
    match = re.match(r'(\d+)(\D+)', item)
    # 将数字部分转换为整数以进行比较
    num_part = int(match.group(1))
    # 返回元组以按数字和字母排序
    return (num_part, match.group(2))


def file_filter(f):
    if f[-4:] == '.sql' and 'schema' not in f and 'fkindexes' not in f:
        return True
    else:
        return False


def get_sql_from_file(file_name):
    file = open(file_name)
    lines = file.readlines().copy()
    sql = ''
    for line in lines:
        sql += line
    sql = sql.replace('\n', ' ').replace('   ', ' ').replace('  ', ' ')
    file.close()
    return sql


def test_hint_from_file(sql_file):
    db = Database()
    sql = get_sql_from_file(sql_file)
    success, result_cont = db.execute_sql(sql)
    print(success, result_cont)


def test_all():
    sql_files = all_sql_files()

    for sql_file in list(sql_files):
        if sql_file:
            test_hint_from_file(sql_file)


def test_one():
    res_path = "{{}}/tpch-queries/".format(
        os.path.dirname(os.path.abspath(__file__)))
    test_hint_from_file(res_path + '1.explain.sql')


if __name__ == '__main__':
    for i in range(0, REPEATCOUNT):
        TIMELOG.write(str(int(time.time()))+";")
        test_all()
        TIMELOG.write(str(int(time.time()))+"\n")
        TIMELOG.flush()

    TIMELOG.close()\n\n\n\n'''
    if anomaly == 'POOR_JOIN_PERFORMANCE,CPU_CONTENTION':
        # 打印提取的数字
        code=f'''import os
import re
import time

import psycopg2


REPEATCOUNT = 1
TIMELOGPATH = str(int(time.time())) + "_job_trigger_time_log.txt"
TIMELOG = open(TIMELOGPATH, 'w+')


class Database():

    def __init__(self):
        self.conn = None
        self.conn = psycopg2.connect(database='imdbload',
                                     user='xxxx',
                                     password='xxxx',
                                     host='xxxx',
                                     port=5432)

    def execute_sql(self, sql):
        fail = 1
        cur = self.conn.cursor()
        i = 0
        cnt = 3
        while fail == 1 and i < cnt:
            try:
                fail = 0
                cur.execute(sql)
            except BaseException as error:
                fail = 1
                print(error)
            res = []
            if fail == 0:
                res = cur.fetchall()
            i = i + 1
        if fail == 1:
            # print("SQL Execution Fatal!!", sql)
            return 0, ''
        elif fail == 0:
            return 1, res


def all_sql_files():
    res_path = "{{}}/join-order-benchmark-master/".format(
        os.path.dirname(os.path.abspath(__file__)))
    # all_file_list = list(filter(file_filter, os.listdir(res_path)))
    # all_file_list = sorted(all_file_list, key=custom_sort)
    all_file_list = [
        '1a.sql', '1b.sql', '1c.sql', '1d.sql',
        '2a.sql', '2b.sql', '2c.sql', '2d.sql',
        '3a.sql', '3b.sql', '3c.sql',
        '4a.sql', '4b.sql', '4c.sql',
        '5a.sql', '5b.sql', '5c.sql',
        '6a.sql', '6b.sql', '6c.sql', '6d.sql', '6e.sql', '6f.sql',
        '7a.sql', '7b.sql', '7c.sql',
        '8a.sql', '8b.sql', '8c.sql', '8d.sql',
        '9a.sql', '9b.sql', '9c.sql', '9d.sql',
        '10a.sql', '10b.sql', '10c.sql',
        '11a.sql', '11b.sql', '11c.sql', '11d.sql',
        '12a.sql', '12b.sql', '12c.sql',
        '13a.sql', '13b.sql', '13c.sql', '13d.sql',
        '14a.sql', '14b.sql', '14c.sql',
        '15a.sql', '15b.sql', '15c.sql', '15d.sql',
        '16a.sql', '16b.sql', '16c.sql', '16d.sql',
        '17a.sql', '17b.sql', '17c.sql', '17d.sql', '17e.sql', '17f.sql',
        '18a.sql', '18b.sql', '18c.sql',
        '19a.sql', '19b.sql', '19c.sql', '19d.sql',
        '20a.sql', '20b.sql', '20c.sql',
        '21a.sql', '21b.sql', '21c.sql',
        '22a.sql', '22b.sql', '22c.sql', '22d.sql',
        '23a.sql', '23b.sql', '23c.sql',
        '24a.sql', '24b.sql',
        '25a.sql', '25b.sql', '25c.sql',
        '26a.sql', '26b.sql', '26c.sql',
        '27a.sql', '27b.sql', '27c.sql',
        '28a.sql', '28b.sql', '28c.sql',
        '29a.sql', '29b.sql', '29c.sql',
        '30a.sql', '30b.sql', '30c.sql',
        '31a.sql', '31b.sql', '31c.sql',
        '32a.sql', '32b.sql',
        '33a.sql', '33b.sql', '33c.sql']

    print(all_file_list)
    files_list = []
    for file in all_file_list:
        files_list.append(res_path + file)
    return files_list


def custom_sort(item):
    # 提取数字和字母部分
    match = re.match(r'(\d+)(\D+)', item)
    # 将数字部分转换为整数以进行比较
    num_part = int(match.group(1))
    # 返回元组以按数字和字母排序
    return (num_part, match.group(2))


def file_filter(f):
    if f[-4:] == '.sql' and 'schema' not in f and 'fkindexes' not in f:
        return True
    else:
        return False


def get_sql_from_file(file_name):
    file = open(file_name)
    lines = file.readlines().copy()
    sql = ''
    for line in lines:
        sql += line
    sql = sql.replace('\n', ' ').replace('   ', ' ').replace('  ', ' ')
    file.close()
    return sql


def test_hint_from_file(sql_file):
    db = Database()
    sql = get_sql_from_file(sql_file)
    success, result_cont = db.execute_sql(sql)
    print(success, result_cont)


def test_all():
    sql_files = all_sql_files()

    for sql_file in list(sql_files)[:-10]:
        if sql_file:
            test_hint_from_file(sql_file)


def test_one():
    res_path = "{{}}/join-order-benchmark-master/".format(
        os.path.dirname(os.path.abspath(__file__)))
    test_hint_from_file(res_path + '1a.sql')


if __name__ == '__main__':
    for i in range(0, REPEATCOUNT):
        TIMELOG.write(str(int(time.time()))+";")
        test_all()
        TIMELOG.write(str(int(time.time()))+"\n")
        TIMELOG.flush()

    TIMELOG.close()

)\n\n\n\n'''
    with open('m_i_code.txt', 'a') as file:
        file.write(code)