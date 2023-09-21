import psycopg2
import sys
sys.path.append('/root/DB-GPT/')
from utils.database import DBArgs,Database
import random
import os
import datetime
import yaml
import time
from multiprocessing.pool import *

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

#print the current time
def print_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(formatted_time)


'''insert_large_data'''
def insert_large_data(threads,duration,ncolumns,nrows,colsize,table_name='table1'):

    print_time()
    #Delete undeleted tables
    delete_table(table_name)
    #create a new table
    create_table(table_name,colsize, ncolumns)
    db=Database(init())
    #insert the data
    #insert_definitions = ', '.join(f'repeat(round(random()*999)::text,{(colsize//3)})' for i in range(ncolumns))
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {colsize}))' for i in range(ncolumns))
    insert_data=f'insert into {table_name} select generate_series(1,{nrows}),{insert_definitions}, now();'
    db.concurrent_execute_sql(threads,duration,insert_data,commit_interval=1)

    #delete the table
    delete_table(table_name)
    
    #print the end time
    print_time()

'''missing_index'''
def missing_index(threads,duration,ncolumns,nrows,colsize,table_name='table1'):
    #create a new table
    print_time()
    db=Database(init())
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)

    # insert some data to be selected 
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {colsize}))' for i in range(ncolumns))
    insert_data=f'insert into {table_name} select generate_series(1,{nrows}),{insert_definitions}, now();'
    db.execute_sqls(insert_data)  

    #select without the index
    missing_index='select * from '+table_name+' where id='
    db.concurrent_execute_sql(threads,duration,missing_index,nrows)

    #delete the table
    delete_table(table_name)
    #print the end time
    print_time()


'''lock_contention'''
def lock_contention(threads,duration,ncolumns,nrows,colsize,table_name='table1'):
    #create a new table
    print_time()
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)
    db=Database(init())
    # insert some data to be updated 
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {colsize}))' for i in range(ncolumns))
    insert_data=f'insert into {table_name} select generate_series(1,{nrows}),{insert_definitions}, now();' 
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


'''vacuum'''
def vacuum(threads,duration,ncolumns,nrows,colsize,table_name='table1'):
    db=Database(init())
    #create a new table
    print_time()
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)

    # insert some data to be deleted
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {colsize}))' for i in range(ncolumns))
    insert_data=f'insert into {table_name} select generate_series(1,{nrows}),{insert_definitions}, now();' 
    db.execute_sqls(insert_data) 

    # delete 80% of the rows
    delete_nrows=int(nrows*0.8)
    vacuum=f'delete from {table_name} where id < {delete_nrows};'
    db.execute_sqls(vacuum)

    # do the select , then the vacuum occurs
    select='select * from '+table_name+' where id='
    db.concurrent_execute_sql(threads,duration,select,nrows)

    #delete the table
    delete_table(table_name)
    print_time()

'''redundent_index'''
def redundent_index(threads,duration,ncolumns,nrows,colsize,nindex,table_name='table1'):
    #create a new table
    print_time()
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




'''io_contention'''
def io_contention():
    print_time()
    command = (
    "su - root -c 'cd /sysbench-tpcc-master; "
    "./tpcc.lua --db-driver=pgsql --tables=2 --scale=3 --threads=50 --events=0 "
    "--pgsql-host=xxxx --pgsql-user=xxxx --pgsql-password=xxxx "
    "--pgsql-port=xxxx --pgsql-db=tpcc --time=90 --rand-type=uniform --report-interval=10 run'"
    )

    os.system(command)
    print_time()

'''fetch_large_data'''
def fetch_large_data():
    print_time()
    try:
        
        os.system("python benchmark_tpch.py")
        print_time()
    except Exception as e:
        print(f"exception: {e}")



'''cpu_contention'''
def cpu_contention():
    try:
        print_time()
        os.system("python benchmark_job.py")
        print_time()
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
        while time.time()-start < duration:
            col_name = random.randint(0, ncolumns-1)
            row_name = random.randint(1, nrows-1)
            lock_contention = f'update {table_name} set name{col_name}=(SELECT substr(md5(random()::text), 1, {colsize})) where id ={row_name}'
            #db.concurrent_execute_sql(threads,duration,lock_contention,nrows)
            cur.execute(lock_contention)
            conn.commit()
        conn.commit()
        conn.close()
