import json
from prometheus_service.prometheus_abnormal_metric import fetch_prometheus_metrics
from datetime import datetime
import paramiko
from datetime import datetime
import re
from configs import SERVER_CONFIG, POSTGRESQL_CONFIG
from multiagents.utils.database import DBArgs, Database

def obtain_slow_queries(server_config, diag_start_time, diag_end_time):

    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the remote server
        ssh.connect(server_config["server_address"], username=server_config["username"], password=server_config["password"])

        # Create an SFTP client
        sftp = ssh.open_sftp()

        # Change to the remote directory
        sftp.chdir(server_config["remote_directory"])

        # Get a list of files in the directory
        files = sftp.listdir()

        # Read the contents of each file
        slow_sqls = []
        for filename in files:
            remote_filepath = server_config["remote_directory"] + '/' + filename
            # read content from the remote file
            remote_file = sftp.open(remote_filepath, 'r')
            try:
                for line in remote_file:
                    
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
                        except ValueError as e:
                            #print(f"ValueError: {e}")
                            pass

            except UnicodeDecodeError as e:
                #print(f"UnicodeDecodeError: {e}")
                pass

    finally:
        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()

    return slow_sqls



if __name__ == "__main__":

    dbargs = DBArgs("postgresql", config=POSTGRESQL_CONFIG)
    db = Database(dbargs, timeout=-1)
    new_dataset = {}
    with open("./prometheus_and_db_docker/alert_history.txt") as f:

        lines = f.readlines()
        for line in lines:
            alert_data = json.loads(line)
            if alert_data['status'] != "resolved":
                continue
            
            start_alert_time = alert_data["alerts"][0]["startsAt"]
            end_alert_time = alert_data["alerts"][0]["endsAt"]

            try:
                dt_object = datetime.strptime(start_alert_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            except:
                dt_object = datetime.strptime(start_alert_time, "%Y-%m-%dT%H:%M:%SZ")
            
            start_seconds = dt_object.timestamp()
            start_timestamp = dt_object.strftime("%Y-%m-%d %H:%M:%S")

            try:
                dt_object = datetime.strptime(end_alert_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            except:
                dt_object = datetime.strptime(end_alert_time, "%Y-%m-%dT%H:%M:%SZ")
            end_seconds = dt_object.timestamp()
            end_timestamp = dt_object.strftime("%Y-%m-%d %H:%M:%S")

            workload_statistics = db.obtain_historical_queries_statistics(topn=50)
            workload_calls = {}
            for workload in workload_statistics:
                workload_calls[workload["sql"]] = workload["calls"]

            slow_queries = obtain_slow_queries(SERVER_CONFIG, start_seconds, end_seconds)
            
            metrics = fetch_prometheus_metrics(alert_data)

            new_dict = {
                "start_time": start_seconds,
                "end_time": start_timestamp,
                "start_timestamp": end_seconds,
                "end_timestamp": end_timestamp,
                "alerts": [alert_data],
                "workload": workload_calls, # not accurate
                "slow_queries": slow_queries,
                "exceptions": metrics
            }

            # record the new_dict into a new json file under diagnostic_files directory
            with open(f"./diagnostic_files/new_testing_case_{str(int(start_seconds))}.json", "w") as f:
                json.dump(new_dict, f)