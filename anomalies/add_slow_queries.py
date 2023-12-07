import json
from datetime import datetime
import re
import os


def obtain_slow_queries(diag_start_time, diag_end_time):
    # # TODO 暂时不读取文件内容
    # return []

    try:
        server_dir = "/var/lib/pgsql/12/data/pg_log"
        # Get a list of files in the directory
        files = os.listdir(server_dir)

        # Read the contents of each file
        slow_sqls = []
        for filename in files:
            if '.log' not in filename:
                continue
            filepath = server_dir + '/' + filename
            
            with open(filepath, 'r') as file:
                try:
                    out_date = False
                    for line in file:
                        
                        if out_date == True:
                            break

                        # if the line contains the required time range
                        if "[]LOG:" not in line and "[postgres]" not in line:
                            words = line.split('statement: ')

                            if len(words) < 2:
                                continue

                            sql = words[-1].strip().lower()

                            words = words[0].split(' ')

                            if len(words) < 2:
                                continue

                            sql_start_time = words[0] + ' ' + words[1]
                            
                            # convert the string type timestamp into value in seconds
                            try:
                                timestamp = datetime.strptime(sql_start_time, '%Y-%m-%d %H:%M:%S.%f')
                                sql_start_time = (timestamp - datetime(1970, 1, 1)).total_seconds()

                                if (diag_start_time <= sql_start_time and sql_start_time <= diag_end_time):
                                    for i, word in enumerate(words):
                                        if word == "duration:":
                                            # reserve two digits
                                            execution_seconds = round(float(words[i + 1])/1000, 2)
                                            if "select" in sql:
                                                sql = sql.strip().replace("\n", "").replace("\t", "")
                                                dbname = re.findall(r'\[([^]]+)\]', words[4])[0]
                                                slow_sqls.append({"sql": sql, "dbname": dbname, "execution_time": str(execution_seconds)+'s'})
                                            break
                                elif sql_start_time > diag_end_time:
                                    out_date = True
                                    break
                            except ValueError as e:
                                #print(f"ValueError: {e}")
                                pass

                except UnicodeDecodeError as e:
                    #print(f"UnicodeDecodeError: {e}")
                    pass

    finally:
        pass
    
    return slow_sqls

# /var/lib/pgsql/12/data/pg_log
with open("testing_set_without_scripts.json", 'r') as f:
    anomaly_blocks = json.load(f)

for anomaly_id in anomaly_blocks:
    # get the start  time and end time
    anomaly_block = anomaly_blocks[anomaly_id]
    diag_start_time = int(anomaly_block["start_time"])
    diag_end_time = int(anomaly_block["end_time"])
    if "slow_queries" not in anomaly_block:
        anomaly_blocks[anomaly_id]['slow_queries'] = []

    slow_queries = obtain_slow_queries(diag_start_time, diag_end_time)
    if slow_queries != []:
        
        anomaly_blocks[anomaly_id]['slow_queries'].append(slow_queries)

with open("testing_set_without_scripts.json", 'w') as f:
    f.write(json.dumps(anomaly_blocks, indent=4))
