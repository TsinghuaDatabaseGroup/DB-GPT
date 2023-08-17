import os
import re
import time

import psycopg2


REPEATCOUNT = 1
TIMELOGPATH = str(int(time.time())) + "_tpch_trigger_time_log.txt"
TIMELOG = open(TIMELOGPATH, 'w+')


class Database():

    def __init__(self):
        self.conn = None
        self.conn = psycopg2.connect(database='tpch',
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
    res_path = "{}/tpch-queries/".format(
        os.path.dirname(os.path.abspath(__file__)))
    # all_file_list = list(filter(file_filter, os.listdir(res_path)))
    # all_file_list = sorted(all_file_list, key=custom_sort)
    all_file_list = [
        '4.explain.sql']

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

    for sql_file in list(sql_files):
        if sql_file:
            test_hint_from_file(sql_file)


def test_one():
    res_path = "{}/tpch-queries/".format(
        os.path.dirname(os.path.abspath(__file__)))
    test_hint_from_file(res_path + '1.explain.sql')


if __name__ == '__main__':
    for i in range(0, REPEATCOUNT):
        TIMELOG.write(str(int(time.time()))+";")
        test_all()
        TIMELOG.write(str(int(time.time()))+"\n")
        TIMELOG.flush()

    TIMELOG.close()

