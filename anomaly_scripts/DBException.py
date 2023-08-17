import subprocess
import time

"""
# 安装sysbench
curl -s https://packagecloud.io/install/repositories/akopytov/sysbench/script.rpm.sh | sudo bash

yum install sysbench

"""

TIMELOGPATH = str(int(time.time())) + "_trigger_time_log.txt"
TIMELOG = open(TIMELOGPATH, 'w+')

class DBException:

    def trigger_sysbench_exception(self):
        """触发异常"""
        self.run_shell_cmd([
            'sysbench --db-driver=pgsql --threads=90 --tables=2 --pgsql-host=xxxx --pgsql-user=xxxx --pgsql-password=xxxx --pgsql-port=5432 --pgsql-db=sysbench --time=60 --rand-type=uniform --table_size=10000000 oltp_read_only run'
        ])

    def run_shell_cmd(self, target_sql_list):
        cmd = ""
        for target_sql in target_sql_list:
            cmd += target_sql + '; '

        TIMELOG.write(str(int(time.time()))+";")
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)
        (stdout, stderr) = proc.communicate()
        stdout, stderr = stdout.decode('utf-8'), stderr.decode()
        if 'FATAL:' in stderr or 'failed to connect' in stderr:
            print(
                "An error occurred while connecting to the database.\n" +
                "Details: " +
                stderr)
        print(stdout)
        TIMELOG.write(str(int(time.time()))+"\n")
        TIMELOG.flush()
        return stdout


if __name__ == '__main__':
    db_exception = DBException()

    # 开启异常负载
    for i in range(5):
        db_exception.trigger_sysbench_exception()

    TIMELOG.close()
