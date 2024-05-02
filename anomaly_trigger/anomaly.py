import psycopg2
import sys
from utils.database import DB_CONFIG, SERVER_CONFIG
from utils.database import DBArgs,Database
import random
import os
import datetime
import yaml
import time
import paramiko
from multiprocessing.pool import *
import promethues

def init():
    # add the config
    # config_path = "/root/DB-GPT/config/tool_config.yaml"
    # with open(config_path, 'r') as config_file:
    #     config = yaml.safe_load(config_file)
    db_args = DBArgs("postgresql", DB_CONFIG, application_name="anomaly")
    return db_args


def restart_init():
    # add the config
    db_args = DBArgs("postgresql", DB_CONFIG, application_name="restart")
    return db_args

def restart():
    db=Database(restart_init())
    sql="SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.application_name = 'anomaly';"
    db.execute_sqls(sql)

def restart_postgresql():

    # 创建SSH客户端实例
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 连接到远程服务器
        ssh.connect(hostname=SERVER_CONFIG['host'], port=SERVER_CONFIG['port'], username=SERVER_CONFIG['user'], password=SERVER_CONFIG['password'])

        # 执行PostgreSQL重启命令
        # 注意：根据您服务器的配置，这些命令可能需要调整
        stdin, stdout, stderr = ssh.exec_command("sudo systemctl restart postgresql-12.service")
        exit_status = stdout.channel.recv_exit_status()  # 阻塞直到命令执行完成

        if exit_status == 0:
            print("PostgreSQL服务已重启")
        else:
            print("重启命令执行失败，错误信息：", stderr.read().decode())
    except Exception as e:
        print(f"SSH连接或命令执行出错：{e}")
    finally:
        # 关闭SSH连接
        ssh.close()

# create a table
def create_table(table_name,colsize, ncolumns):
    db=Database(init())
    column_definitions = ', '.join(f'name{i} varchar({colsize})' for i in range(ncolumns))
    creat_sql = f'CREATE TABLE {table_name} (id int, {column_definitions}, time timestamp);'
    db.execute_sqls(creat_sql)

# delete the table
def delete_table(table_name):
    db=Database(init())
    delete_sql=f'DROP TABLE if exists {table_name}'
    db.execute_sqls(delete_sql)

# print the current time
def print_start_time(cmd):
    log_file = open("dataset.txt", "a")
    current_time = datetime.datetime.now()
    timestamp = current_time.timestamp()
    inttimestamp=int(timestamp)
    log_file.write(f"{cmd} started at {inttimestamp}\n")
    log_file.flush()
    print(inttimestamp)

def print_end_time(cmd):
    log_file = open("dataset.txt", "a")
    current_time = datetime.datetime.now()
    timestamp = current_time.timestamp()
    inttimestamp=int(timestamp)
    log_file.write(f"{cmd} ended at {inttimestamp}\n")
    log_file.flush()
    print(inttimestamp)

def write_amomaly_sql_to_file(text):
    try:
        with open('badsql.txt', 'a') as file:
            file.write(f"{text}\n")
        print("文本已成功写入到badsql.txt文件中。")
    except Exception as e:
        print(f"写入文件时出现错误: {e}")

def write_amomaly_sql_to_file_a_line(text):
    try:
        with open('badsql.txt', 'a') as file:
            file.write(f"{text}\t\t")
        print("文本已成功写入到badsql.txt文件中。")
    except Exception as e:
        print(f"写入文件时出现错误: {e}")

def write_space():
    try:
        with open('badsql.txt', 'a') as file:
            file.write(f"\n")
    except Exception as e:
        print(f"写入文件时出现错误: {e}")

'''insert_large_data'''
def insert_large_data(threads,duration,ncolumns,nrows,colsize,table_name='table1'):
    cmd=f"python anomaly_trigger/main.py --anomaly INSERT_LARGE_DATA --threads {threads} --ncolumn {ncolumns} --nrow {nrows} --colsize {colsize}"
    #Delete undeleted tables
    delete_table(table_name)
    #create a new table
    create_table(table_name,colsize, ncolumns)
    db=Database(init())
    #insert the data
    #insert_definitions = ', '.join(f'repeat(round(random()*999)::text,{(colsize//3)})' for i in range(ncolumns))
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {colsize}))' for i in range(ncolumns))
    insert_data=f'insert into {table_name} select generate_series(1,{nrows}),{insert_definitions}, now();'
    write_amomaly_sql_to_file(insert_data)
    time.sleep(10)
    print_start_time(cmd)
    db.concurrent_execute_sql(threads,duration,insert_data,commit_interval=1)
    print_end_time(cmd)
    time.sleep(10)
    #restaet the pg database
    restart()
    time.sleep(10)
    cpu,mem=promethues.restart_decision()
    if((cpu>50)|(mem>50)):
        restart_postgresql()
    
    #delete the table
    delete_table(table_name)


'''missing_index'''
def missing_index(threads,duration,ncolumns,nrows,colsize,table_name='table1'):
    cmd=f"python anomaly_trigger/main.py --anomaly MISSING_INDEXES --threads {threads} --ncolumn {ncolumns} --nrow {nrows} --colsize {colsize}"
    #create a new table
    
    db=Database(init())
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)

    # insert some data to be selected 
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {colsize}))' for i in range(ncolumns))
    insert_data=f'insert into {table_name} select generate_series(1,{nrows}),{insert_definitions}, now();'
    db.execute_sqls(insert_data)  

    #select without the index
    missing_index='select * from '+table_name+' where id='
    write_amomaly_sql_to_file(missing_index)
    time.sleep(10)
    print_start_time(cmd)
    db.concurrent_execute_sql(threads,duration,missing_index,nrows)
    print_end_time(cmd)
    time.sleep(10)
    restart()
    time.sleep(10)
    #restaet the pg database
    cpu,mem=promethues.restart_decision()
    if((cpu>50)|(mem>50)):
        restart_postgresql()
    
    #delete the table
    delete_table(table_name)
    #print the end time


'''lock_contention'''
def lock_contention(threads,duration,ncolumns,nrows,colsize,table_name='table1'):
    cmd=f"python anomaly_trigger/main.py --anomaly LOCK_CONTENTION --threads {threads} --ncolumn {ncolumns} --nrow {nrows} --colsize {colsize}"
    #create a new table
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)
    db=Database(init())
    # insert some data to be updated 
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {colsize}))' for i in range(ncolumns))
    insert_data=f'insert into {table_name} select generate_series(1,{nrows}),{insert_definitions}, now();' 
    db.execute_sqls(insert_data) 
    pool = Pool(threads)
    time.sleep(10)
    print_start_time(cmd)
    for _ in range(threads):
        pool.apply_async(
            lock, (table_name, ncolumns, colsize, duration, nrows))
    pool.close()
    pool.join()
    print_end_time(cmd)
    write_space()
    time.sleep(10)
    restart()
    time.sleep(10)
    #restaet the pg database
    cpu,mem=promethues.restart_decision()
    if((cpu>50)|(mem>50)):
        restart_postgresql()
    
    #delete the table
    delete_table(table_name)


'''vacuum'''
def vacuum(threads,duration,ncolumns,nrows,colsize,table_name='table1'):
    cmd=f"python anomaly_trigger/main.py --anomaly VACUUM --threads {threads} --ncolumn {ncolumns} --nrow {nrows} --colsize {colsize}"
    db=Database(init())
    #create a new table
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)

    # insert some data to be deleted
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {colsize}))' for i in range(ncolumns))
    insert_data=f'insert into {table_name} select generate_series(1,{nrows}),{insert_definitions}, now();' 
    db.execute_sqls(insert_data) 
    time.sleep(10)
    print_start_time(cmd)
    # delete 80% of the rows
    delete_nrows=int(nrows*0.8)
    vacuum=f'delete from {table_name} where id < {delete_nrows};'
    write_amomaly_sql_to_file(vacuum)
    db.execute_sqls(vacuum)
    print_end_time(cmd)
    time.sleep(10)
    # do the select , then the vacuum occurs
    select='select * from '+table_name+' where id='
    db.concurrent_execute_sql(threads,duration,select,nrows)
    time.sleep(10)
    restart()
    time.sleep(10)
    #restaet the pg database
    cpu,mem=promethues.restart_decision()
    if((cpu>50)|(mem>50)):
        restart_postgresql()
    
    #delete the table
    delete_table(table_name)

'''redundent_index'''
def redundent_index(threads,duration,ncolumns,nrows,colsize,nindex,table_name='table1'):
    cmd=f"python anomaly_trigger/main.py --anomaly REDUNDANT_INDEX --threads {threads} --ncolumn {ncolumns} --nrow {nrows} --colsize {colsize}"
    #create a new table
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)
    db=Database(init())
    # insert some data to be updated 
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {colsize}))' for i in range(ncolumns))
    insert_data=f'insert into {table_name} select generate_series(1,{nrows}),{insert_definitions}, now();' 
    db.execute_sqls(insert_data) 

    #initialization of the indexes
    nindex=int((nindex*ncolumns)/10)
    db.build_index(table_name,nindex)
    id_index='CREATE INDEX index_'+table_name+'_id ON '+table_name+'(id);'
    db.execute_sqls(id_index)
    time.sleep(10)
    #lock_contention
    print_start_time(cmd)
    pool = Pool(threads)
    for _ in range(threads):
        pool.apply_async(
            lock, (table_name, ncolumns, colsize, duration, nrows))
    pool.close()
    pool.join()
    print_end_time(cmd)
    time.sleep(10)
    #drop the index
    db.drop_index(table_name)
    restart()
    time.sleep(10)
    #restaet the pg database
    cpu,mem=promethues.restart_decision()
    if((cpu>50)|(mem>50)):
        restart_postgresql()
    
    #delete the table
    delete_table(table_name)


'''io_contention'''
def io_contention():
    cmd=f"python anomaly_trigger/main.py --anomaly INSERT_LARGE_DATA,IO_CONTENTION"
    print_start_time(cmd)
    command = (
    "su - root -c 'cd /sysbench-tpcc-master; "
    "./tpcc.lua --db-driver=pgsql --tables=2 --scale=3 --threads=50 --events=0 "
    "--pgsql-host=xxx --pgsql-user=xxx --pgsql-password=xxx "
    "--pgsql-port=xxxx --pgsql-db=tpcc --time=90 --rand-type=uniform --report-interval=10 run'"
    )
    write_amomaly_sql_to_file("sysbench-tpcc to INSERT_LARGE_DATA, IO_CONTENTION")
    os.system(command)
    print_end_time(cmd)
    time.sleep(10)
    restart()
    time.sleep(10)
    #restaet the pg database
    cpu,mem=promethues.restart_decision()
    if((cpu>50)|(mem>50)):
        restart_postgresql()


'''fetch_large_data'''
def fetch_large_data():
    cmd=f"python anomaly_trigger/main.py --anomaly FETCH_LARGE_DATA,CORRELATED_SUBQUERY"
    
    try:
        print_start_time(cmd)
        os.system("python anomaly_trigger/benchmark_tpch.py")
        print_end_time(cmd)
        write_amomaly_sql_to_file('''select o_orderpriority, count(*) as order_count from orders where o_orderdate >= date '1996-03-01' and o_orderdate < date '1996-03-01' + interval '3' month and exists ( select * from lineitem where l_orderkey = o_orderkey and l_commitdate < l_receiptdate ) group by o_orderpriority order by o_orderpriority LIMIT 1;''')
        time.sleep(10)
        restart()
        time.sleep(10)
    #restaet the pg database
        cpu,mem=promethues.restart_decision()
        if((cpu>50)|(mem>50)):
            restart_postgresql()
    
    except Exception as e:
        print(f"exception: {e}")


'''cpu_contention'''
def cpu_contention():
    cmd=f"python anomaly_trigger/main.py --anomaly POOR_JOIN_PERFORMANCE,CPU_CONTENTION"
    try:
        print_start_time(cmd)
        os.system("python anomaly_trigger/benchmark_job.py")
        print_end_time(cmd)
        write_amomaly_sql_to_file('''SELECT MIN(mc.note) AS production_note, MIN(t.title) AS movie_title,MIN(t.production_year) AS movie_year FROM company_type AS ct,info_type AS it,movie_companies AS mc,movie_info_idx AS mi_idx,title AS WHERE ct.kind = 'production companies'AND it.info = 'top 250 rank'AND mc.note NOT LIKE '%(as Metro-Goldwyn-Mayer Pictures)%' AND (mc.note LIKE '%(co-production)%'OR mc.note LIKE '%(presents)%') AND ct.id = mc.company_type_idAND t.id = mc.movie_id AND t.id = mi_idx.movie_id AND mc.movie_id = mi_idx.movie_id AND it.id = mi_idx.info_type_id;''')
        time.sleep(10)
        restart()
        time.sleep(10)
        #restaet the pg database
        cpu,mem=promethues.restart_decision()
        if((cpu>50)|(mem>50)):
            restart_postgresql()
        
    except Exception as e:
        print(f"exception: {e}")


def lock(table_name, ncolumns, colsize, duration, nrows):
    args=init()
    start = time.time()
    #lock_contention
    while time.time()-start < duration:
        conn = psycopg2.connect(database=args.dbname, user=args.user, password=args.password,
                                        host=args.host, port=args.port)
        cur = conn.cursor()
        #write_amomaly_sql_to_file(lock_contention)
        while time.time()-start < duration:
            col_name = random.randint(0, ncolumns-1)
            row_name = random.randint(1, nrows-1)
            lock_contention = f'update {table_name} set name{col_name}=(SELECT substr(md5(random()::text), 1, {colsize})) where id ={row_name}'
            cur.execute(lock_contention)
            conn.commit()
        conn.commit()
        conn.close()
    write_amomaly_sql_to_file_a_line(lock_contention)
