import psycopg2
import sql
import random
import os
import datetime

#create a table
def create_table(table_name,colsize, ncolumns):

    column_definitions = ', '.join(f'name{i} varchar({colsize})' for i in range(ncolumns))
    creat_sql = f'CREATE TABLE {table_name} (id int, {column_definitions}, time timestamp);'
    sql.execute_sql(creat_sql)

#delete the table
def delete_table(table_name):

    delete_sql=f'DROP TABLE if exists {table_name}'
    sql.execute_sql(delete_sql)
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

    #insert the data
    #insert_definitions = ', '.join(f'repeat(round(random()*999)::text,{(colsize//3)})' for i in range(ncolumns))
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {colsize}))' for i in range(ncolumns))
    insert_data=f'insert into {table_name} select generate_series(1,{nrows}),{insert_definitions}, now();'
    sql.concurrent_execute_sql(threads,duration,insert_data,commit_interval=1)

    #delete the table
    delete_table(table_name)
    
    #print the end time
    print_time()

'''missing_index'''
def missing_index(threads,duration,ncolumns,nrows,colsize,table_name='table1'):
    #create a new table
    print_time()
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)

    # insert some data to be selected 
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {colsize}))' for i in range(ncolumns))
    insert_data=f'insert into {table_name} select generate_series(1,{nrows}),{insert_definitions}, now();'
    sql.execute_sql(insert_data)  

    #select without the index
    missing_index='select * from '+table_name+' where id='
    sql.concurrent_execute_sql(threads,duration,missing_index,nrows)

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

    # insert some data to be updated 
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {colsize}))' for i in range(ncolumns))
    insert_data=f'insert into {table_name} select generate_series(1,{nrows}),{insert_definitions}, now();' 
    sql.execute_sql(insert_data) 

    #lock_contention
    col_name = random.randint(0, ncolumns-1)
    row_name = random.randint(1, nrows-1)
    lock_contention = f'update {table_name} set name{col_name}=(SELECT substr(md5(random()::text), 1, {colsize})) where id ={row_name}'
    sql.concurrent_execute_sql(threads,duration,lock_contention,nrows)

    #delete the table
    delete_table(table_name)
    print_time()


'''vacuum'''
def vacuum(threads,duration,ncolumns,nrows,colsize,table_name='table1'):
    #create a new table
    print_time()
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)

    # insert some data to be deleted
    insert_definitions = ', '.join(f'(SELECT substr(md5(random()::text), 1, {colsize}))' for i in range(ncolumns))
    insert_data=f'insert into {table_name} select generate_series(1,{nrows}),{insert_definitions}, now();' 
    sql.execute_sql(insert_data) 

    # delete 80% of the rows
    delete_nrows=int(nrows*0.8)
    vacuum=f'delete from {table_name} where id < {delete_nrows};'
    sql.execute_sql(vacuum)

    # do the select , then the vacuum occurs
    select='select * from '+table_name+' where id='
    sql.concurrent_execute_sql(threads,duration,select,nrows)

    #delete the table
    delete_table(table_name)
    print_time()

'''redundent_index'''
def redundent_index(threads,duration,ncolumns,nrows,colsize,nindex,table_name='table1'):
    #create a new table
    print_time()
    delete_table(table_name)
    create_table(table_name,colsize, ncolumns)

    #initialization of the indexes
    nindex=int((nindex*ncolumns)/10)
    sql.build_index(table_name,nindex)
    id_index='CREATE INDEX index_'+table_name+'_id ON '+table_name+'(id);'
    sql.execute_sql(id_index)

    #lock_contention
    col_name = random.randint(0, ncolumns-1)
    row_name = random.randint(1, nrows-1)
    lock_contention = f'update {table_name} set name{col_name}=(SELECT substr(md5(random()::text), 1, {colsize})) where id ={row_name}'
    sql.concurrent_execute_sql(threads,duration,lock_contention,nrows)

    #drop the index
    sql.drop_index(table_name)

    #delete the table
    delete_table(table_name)
    print_time()




'''io_contention'''
def io_contention():
    print_time()
    command = (
    "su - root -c 'cd /sysbench-tpcc-master; "
    "./tpcc.lua --db-driver=pgsql --tables=2 --scale=3 --threads=50 --events=0 "
    "--pgsql-host=172.27.58.65 --pgsql-user=dbmind --pgsql-password=DBMINDdbmind2020 "
    "--pgsql-port=5432 --pgsql-db=tpcc --time=90 --rand-type=uniform --report-interval=10 run'"
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






    










