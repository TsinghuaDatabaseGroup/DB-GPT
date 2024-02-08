import os
import re
import time

import psycopg2


REPEATCOUNT = 1
TIMELOGPATH = str(int(time.time())) + "_job_trigger_time_log.txt"
TIMELOG = open(TIMELOGPATH, 'w+')


class Database():

    def __init__(self):
        self.conn = None
        self.conn = psycopg2.connect(database='imdbload',
                                     user='xxxx',
                                     password='xxxx',
                                     host='xxxx',
                                     port=5432)

    def execute_sql(self, sql):
        fail = 1
        cur = self.conn.cursor()
        i = 0
        cnt = 3
        while fail == 1 and i < cnt:
            try:
                fail = 0
                cur.execute(sql)
            except BaseException as error:
                fail = 1
                print(error)
            res = []
            if fail == 0:
                res = cur.fetchall()
            i = i + 1
        if fail == 1:
            # print("SQL Execution Fatal!!", sql)
            return 0, ''
        elif fail == 0:
            return 1, res


def all_sql_files():
    res_path = "{}/join-order-benchmark-master/".format(
        os.path.dirname(os.path.abspath(__file__)))
    # all_file_list = list(filter(file_filter, os.listdir(res_path)))
    # all_file_list = sorted(all_file_list, key=custom_sort)
    all_file_list = [
        '1a.sql', '1b.sql', '1c.sql', '1d.sql',
        '2a.sql', '2b.sql', '2c.sql', '2d.sql',
        '3a.sql', '3b.sql', '3c.sql',
        '4a.sql', '4b.sql', '4c.sql',
        '5a.sql', '5b.sql', '5c.sql',
        '6a.sql', '6b.sql', '6c.sql', '6d.sql', '6e.sql', '6f.sql',
        '7a.sql', '7b.sql', '7c.sql',
        '8a.sql', '8b.sql', '8c.sql', '8d.sql',
        '9a.sql', '9b.sql', '9c.sql', '9d.sql',
        '10a.sql', '10b.sql', '10c.sql',
        '11a.sql', '11b.sql', '11c.sql', '11d.sql',
        '12a.sql', '12b.sql', '12c.sql',
        '13a.sql', '13b.sql', '13c.sql', '13d.sql',
        '14a.sql', '14b.sql', '14c.sql',
        '15a.sql', '15b.sql', '15c.sql', '15d.sql',
        '16a.sql', '16b.sql', '16c.sql', '16d.sql',
        '17a.sql', '17b.sql', '17c.sql', '17d.sql', '17e.sql', '17f.sql',
        '18a.sql', '18b.sql', '18c.sql',
        '19a.sql', '19b.sql', '19c.sql', '19d.sql',
        '20a.sql', '20b.sql', '20c.sql',
        '21a.sql', '21b.sql', '21c.sql',
        '22a.sql', '22b.sql', '22c.sql', '22d.sql',
        '23a.sql', '23b.sql', '23c.sql',
        '24a.sql', '24b.sql',
        '25a.sql', '25b.sql', '25c.sql',
        '26a.sql', '26b.sql', '26c.sql',
        '27a.sql', '27b.sql', '27c.sql',
        '28a.sql', '28b.sql', '28c.sql',
        '29a.sql', '29b.sql', '29c.sql',
        '30a.sql', '30b.sql', '30c.sql',
        '31a.sql', '31b.sql', '31c.sql',
        '32a.sql', '32b.sql',
        '33a.sql', '33b.sql', '33c.sql']

    print(all_file_list)
    files_list = []
    for file in all_file_list:
        files_list.append(res_path + file)
    return files_list


def custom_sort(item):
    # 提取数字和字母部分
    match = re.match(r'(\d+)(\D+)', item)
    # 将数字部分转换为整数以进行比较
    num_part = int(match.group(1))
    # 返回元组以按数字和字母排序
    return (num_part, match.group(2))


def file_filter(f):
    if f[-4:] == '.sql' and 'schema' not in f and 'fkindexes' not in f:
        return True
    else:
        return False


def get_sql_from_file(file_name):
    file = open(file_name)
    lines = file.readlines().copy()
    sql = ''
    for line in lines:
        sql += line
    sql = sql.replace('\n', ' ').replace('   ', ' ').replace('  ', ' ')
    file.close()
    return sql


def test_hint_from_file(sql_file):
    db = Database()
    sql = get_sql_from_file(sql_file)
    success, result_cont = db.execute_sql(sql)
    print(success, result_cont)


def test_all():
    sql_files = all_sql_files()

    for sql_file in list(sql_files)[:-10]:
        if sql_file:
            test_hint_from_file(sql_file)


def test_one():
    res_path = "{}/join-order-benchmark-master/".format(
        os.path.dirname(os.path.abspath(__file__)))
    test_hint_from_file(res_path + '1a.sql')


if __name__ == '__main__':
    for i in range(0, REPEATCOUNT):
        TIMELOG.write(str(int(time.time()))+";")
        test_all()
        TIMELOG.write(str(int(time.time()))+"\n")
        TIMELOG.flush()

    TIMELOG.close()

