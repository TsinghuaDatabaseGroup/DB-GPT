import paramiko
from datetime import datetime
import re

SERVER_CONFIG = {
    "server_address": "",
    "username": "",
    "password": "",
    "remote_directory": ""
}


def validate_server_config(config):
    required_keys = ["server_address", "username", "password", "remote_directory"]

    missing_keys = [key for key in required_keys if key not in config or not config[key]]

    if missing_keys:
        print(f"Missing or empty required config keys: {', '.join(missing_keys)}")
        return False

    return True


def parse_log_line(line):
    """从日志行中提取相关数据。"""
    if "[]LOG:" in line or "[postgres]" in line:
        return None

    parts = line.split('statement: ')
    if len(parts) < 2:
        return None

    sql = parts[1].strip().lower()
    timestamp_str, _ = parts[0].split(' ', 3)[:2]

    try:
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        return None

    return timestamp, sql


def extract_execution_details(words):
    """从日志消息部分提取执行细节。"""
    for i, word in enumerate(words):
        if word == "duration:":
            execution_seconds = round(float(words[i + 1]) / 1000, 2)
            dbname = re.findall(r'\[([^]]+)\]', words[4])[0]
            return execution_seconds, dbname
    return None, None


def obtain_slow_queries(diag_start_time, diag_end_time):
    slow_sqls = []

    if not validate_server_config(SERVER_CONFIG):
        return []

    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_CONFIG['server_address'], username=SERVER_CONFIG['username'],
                    password=SERVER_CONFIG['password'])

        with ssh.open_sftp() as sftp:
            sftp.chdir(SERVER_CONFIG['remote_directory'])
            files = sftp.listdir()

            for filename in files:
                with sftp.open(f"{SERVER_CONFIG['remote_directory']}/{filename}", 'r') as remote_file:
                    for line in remote_file:
                        try:
                            parsed_data = parse_log_line(line)
                            if parsed_data:
                                timestamp, sql = parsed_data
                                sql_start_time = (timestamp - datetime(1970, 1, 1)).total_seconds()

                                if diag_start_time <= sql_start_time <= diag_end_time:
                                    execution_seconds, dbname = extract_execution_details(line.split(' '))
                                    if execution_seconds and "select" in sql:
                                        sql = sql.replace("\n", "").replace("\t", "")
                                        slow_sqls.append({
                                            "sql": sql,
                                            "dbname": dbname,
                                            "execution_time": f"{execution_seconds}s"
                                        })
                        except UnicodeDecodeError:
                            pass

    return slow_sqls