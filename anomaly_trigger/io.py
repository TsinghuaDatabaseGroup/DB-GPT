import os
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
    print_time()