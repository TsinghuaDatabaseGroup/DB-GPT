import paramiko
from datetime import datetime
import re

def obtain_anomaly_time():
    # read from ./diag_time.txt，and obtain the last line as the newest anomaly
    with open("./diag_time.txt", 'r') as f:
        last_line = f.readlines()[-1].replace("\n", "")
        diag_start_time = last_line.split('-')[0]
        diag_end_time = last_line.split('-')[1]
    # print("diag_start_time: ", diag_start_time)
    # print("diag_end_time: ", diag_end_time)

    if not diag_start_time or not diag_end_time:
        raise Exception("No start and end time of anomaly!")
    
    return round(float(diag_start_time), 2), round(float(diag_end_time), 2)


# def obtain_slow_queries(server_config, start_time, end_time):
def obtain_slow_queries(server_config):
    # # TODO 暂时不读取文件内容
    # return []

    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    diag_start_time, diag_end_time = obtain_anomaly_time()

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