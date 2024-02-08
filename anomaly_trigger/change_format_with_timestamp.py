import re
import random

input_file_name = "xxx"
output_file_name = "xxx"


try:
    # 打开输入文件以读取内容
    with open(input_file_name, 'r') as input_file:
        # 读取输入文件的所有行
        lines = input_file.readlines()
    print("已读取")
except FileNotFoundError:
    print(f"文件 {input_file_name} 不存在。")
except Exception as e:
    print(f"发生错误: {str(e)}")
for line in lines:
    # 输入的字符串
    input_string = line
    anomaly_match = re.search(r'--fault\s+([^\s]+)', input_string)
    anomaly = str(anomaly_match.group(1)) if anomaly_match else None
    bash_match = re.search(r'bash\s+([^\s]+)', input_string)
    bash = str(bash_match.group(1)) if bash_match else None
    pattern1 = r'started at (\d+)'
    timestamp_match1 = re.search(pattern1,input_string)
    timestamp1=str(timestamp_match1.group(0)) if timestamp_match1 else ""
    pattern2 = r'ended at (\d+)'
    timestamp_match2 = re.search(pattern2,input_string)
    timestamp2=str(timestamp_match2.group(0)) if timestamp_match2 else ""
    if anomaly=="cpu":
        # 使用正则表达式提取数字
        threads_match = re.search(r'--client_5 (\d+)', input_string)
        ncolumn_match = re.search(r'--ncolumns (\d+)', input_string)
        colsize_match = re.search(r'--colsize (\d+)', input_string)
        nrow_match = re.search(r'--nrows (\d+)', input_string)

        # 提取的数字存入变量
        threads = int(threads_match.group(1)) if threads_match else None
        ncolumn = int(ncolumn_match.group(1)) if ncolumn_match else None
        colsize = int(colsize_match.group(1)) if colsize_match else None
        nrow = int(nrow_match.group(1)) if nrow_match else None
        # 打开输出文件以写入内容
        with open(output_file_name, 'a') as output_file:
            script=f'python anomaly_trigger/main.py --anomaly INSERT_LARGE_DATA   --threads {threads} --ncolumn {ncolumn} --colsize {colsize} --nrow {nrow} {timestamp1}{timestamp2}\n'
            output_file.write(script)
    if anomaly=="wait":
        # 使用正则表达式提取数字
        threads_match = re.search(r'--client_1 (\d+)', input_string)
        ncolumn_match = re.search(r'--ncolumns (\d+)', input_string)
        colsize_match = re.search(r'--colsize (\d+)', input_string)
        nrow_match = re.search(r'--nrows (\d+)', input_string)

        # 提取的数字存入变量
        threads = int(threads_match.group(1)) if threads_match else None
        ncolumn = int(ncolumn_match.group(1)) if ncolumn_match else None
        colsize = int(colsize_match.group(1)) if colsize_match else None
        nrow = int(nrow_match.group(1)) if nrow_match else None
        # 打开输出文件以写入内容
        with open(output_file_name, 'a') as output_file:
            script=f'python anomaly_trigger/main.py --anomaly LOCK_CONTENTION   --threads {threads} --ncolumn {ncolumn} --colsize {colsize} --nrow {nrow} {timestamp1}{timestamp2}\n'
            output_file.write(script)
    if anomaly=="vacuum":
        # 使用正则表达式提取数字
        threads_match = re.search(r'--client_4 (\d+)', input_string)
        ncolumn_match = re.search(r'--ncolumns (\d+)', input_string)
        colsize_match = re.search(r'--colsize (\d+)', input_string)
        nrow_match = re.search(r'--nrows (\d+)', input_string)

        # 提取的数字存入变量
        threads = int(threads_match.group(1)) if threads_match else None
        ncolumn = int(ncolumn_match.group(1)) if ncolumn_match else None
        colsize = int(colsize_match.group(1)) if colsize_match else None
        nrow = int(nrow_match.group(1)) if nrow_match else None
        # 打开输出文件以写入内容
        with open(output_file_name, 'a') as output_file:
            script=f'python anomaly_trigger/main.py --anomaly VACUUM   --threads {threads} --ncolumn {ncolumn} --colsize {colsize} --nrow {nrow} {timestamp1}{timestamp2}\n'
            output_file.write(script)
    
    if anomaly=="io":
        # 使用正则表达式提取数字
        threads_match = re.search(r'--client_2 (\d+)', input_string)
        ncolumn_match = re.search(r'--ncolumns (\d+)', input_string)
        colsize_match = re.search(r'--colsize (\d+)', input_string)
        nrow_match = re.search(r'--nrows (\d+)', input_string)

        # 提取的数字存入变量
        threads = int(threads_match.group(1)) if threads_match else None
        ncolumn = int(ncolumn_match.group(1)) if ncolumn_match else None
        colsize = int(colsize_match.group(1)) if colsize_match else None
        nrow = int(nrow_match.group(1)) if nrow_match else None
        # 打开输出文件以写入内容
        with open(output_file_name, 'a') as output_file:
            script=f'python anomaly_trigger/main.py --anomaly MISSING_INDEXES    --threads {threads} --ncolumn {ncolumn} --colsize {colsize} --nrow {nrow} {timestamp1}{timestamp2}\n'
            output_file.write(script)
    if bash =="too_many_indexes.sh":
        threads =random.randint(5,10)
        ncolumn = random.randint(50,100)
        colsize = random.randint(50,100)
        nrow = random.randint(400000,1000000)
        # 打开输出文件以写入内容
        with open(output_file_name, 'a') as output_file:
            script=f'python anomaly_trigger/main.py --anomaly REDUNDANT_INDEX   --threads {threads} --ncolumn {ncolumn} --colsize {colsize} --nrow {nrow} {timestamp1}{timestamp2}\n'
            output_file.write(script)
    if bash =="run_benchmark_job.sh":
        # 打开输出文件以写入内容
        with open(output_file_name, 'a') as output_file:
            script=f"python anomaly_trigger/main.py --anomaly POOR_JOIN_PERFORMANCE,CPU_CONTENTION {timestamp1}{timestamp2}\n"
            output_file.write(script)
    if bash =="run_benchmark_tpch.sh":
        # 打开输出文件以写入内容
        with open(output_file_name, 'a') as output_file:
            script=f"python anomaly_trigger/main.py --anomaly FETCH_LARGE_DATA,CORRELATED_SUBQUERY {timestamp1}{timestamp2}\n"
            output_file.write(script)
    if bash =="run_benchmark_tpcc.sh":
        # 打开输出文件以写入内容
        with open(output_file_name, 'a') as output_file:
            script=f"python anomaly_trigger/main.py --anomaly INSERT_LARGE_DATA,IO_CONTENTION {timestamp1}{timestamp2}\n"
            output_file.write(script)