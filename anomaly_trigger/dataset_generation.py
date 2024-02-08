import subprocess
import time
import random
import datetime
import createdatabase
import dropdatabase

def run_cmd(cmd_list):
    try:
        for cmd in cmd_list:
            #current_datetime = datetime.datetime.now()
            #timestamp = current_datetime.timestamp()
            #inttimestamp=int(timestamp)
            #log_file.write(f"{cmd} started at {inttimestamp}\n")
            #log_file.flush()
            # 运行脚本
            subprocess.run(cmd, shell=True)
            # 记录结束时间
            #current_datetime = datetime.datetime.now()
            #end_time = datetime.datetime.strftime(current_datetime,"%Y-%m-%d %H:%M:%S")
            #timestamp = current_datetime.timestamp()
            #inttimestamp=int(timestamp)
            #log_file.write(f"{cmd} ended at {inttimestamp}\n")
            #log_file.flush()
            # 休息60秒钟
            time.sleep(60)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# 定义要运行的脚本文件
script = "anomaly_trigger/main.py"

    # 循环500次
for i in range(500):
        # 生成随机参数
    Thread_1 = random.randint(50, 200)
    Thread_2 = random.randint(50, 200)
    Thread_3 = random.randint(50, 200)
    Thread_4 = random.randint(50, 200)
    Thread_5 = random.randint(50, 200)
    ncolumns1=random.randint(5, 20)
    ncolumns2=random.randint(20, 40)
    ncolumns3=random.randint(50, 100)
    ncolumns4=random.randint(5, 20)
    ncolumns5=random.randint(50, 100)
    ncolumns6=random.randint(50, 100)
    nrows1=random.randint(50, 100)
    nrows2=random.randint(50, 100)
    nrows3=random.randint(200, 400)
    nrows4=random.randint(2000000, 4000000)
    nrows5=random.randint(20000, 40000)
    nrows6=random.randint(200, 400)
    colsize1=random.randint(20, 80)
    colsize2=random.randint(50, 100)
    colsize3=random.randint(50, 100)
    colsize4=random.randint(50, 100)
    colsize5=random.randint(50, 100)
    colsize6=random.randint(50, 100)
        
        # 构建命令
    #Highly concurrent commits   
    cmd0 = f"python {script} --anomaly INSERT_LARGE_DATA --threads {Thread_1} --ncolumn {ncolumns1} --colsize {colsize1} --nrow {nrows1} "
    #Highly concurrent inserts
    cmd1 = f"python {script} --anomaly INSERT_LARGE_DATA --threads {Thread_2} --ncolumn {ncolumns2} --colsize {colsize2} --nrow {nrows2}"
    #Lock waits
    cmd2 = f"python {script} --anomaly LOCK_CONTENTION --threads {Thread_3} --ncolumn {ncolumns3} --colsize {colsize3} --nrow {nrows3}"
    #Vacuum
    cmd3 = f"python {script} --anomaly VACUUM --threads {Thread_4} --ncolumn {ncolumns4} --colsize {colsize4} --nrow {nrows4}"
    #Missing indexes
    cmd4 = f"python {script} --anomaly MISSING_INDEXES --threads {Thread_5} --ncolumn {ncolumns5} --colsize {colsize5} --nrow {nrows5}"
    #Too many indexes
    cmd5 = f"python {script} --anomaly REDUNDANT_INDEX   --threads 5 --ncolumn {ncolumns6} --colsize {colsize6} --nrow {nrows6}"
    #INSERT_LARGE_DATA, IO_CONTENTION
    cmd6 = f"python anomaly_trigger/main.py --anomaly INSERT_LARGE_DATA,IO_CONTENTION"
    #cmd7=f"bash stop_benchmark_tpcc.sh"
    #POOR_JOIN_PERFORMANCE, CPU_CONTENTION
    cmd8 = f"python anomaly_trigger/main.py --anomaly POOR_JOIN_PERFORMANCE,CPU_CONTENTION"
    #FETCH_LARGE_DATA , CORRELATED_SUBQUERY
    cmd9 = f"python anomaly_trigger/main.py --anomaly FETCH_LARGE_DATA,CORRELATED_SUBQUERY"
    #cmd10=f"bash missing_indexes_and_vacuum.sh"
    #Heavy workloads  #I/O saturation
    cmd_list=cmd_list = [cmd0,cmd1,cmd2,cmd3,cmd4,cmd5,cmd6,cmd8,cmd9]
    #dropdatabase.dropdatabase()
    #createdatabase.createdatabase()
    run_cmd(cmd_list)
    #dropdatabase.dropdatabase()
    #run_cmd67(cmd6,cmd7)
# 关闭日志文件
#log_file.close()


