import psycopg2
from utils.database import DB_CONFIG, SERVER_CONFIG

def createdatabase(name):
    # 连接到 PostgreSQL 服务器的默认数据库 "postgres"
    conn = psycopg2.connect(
        dbname="sysbench",  # 连接到默认的 "postgres" 数据库
        user=DB_CONFIG['user'],  # 替换为你的数据库用户名
        password=DB_CONFIG['password'],  # 替换为你的数据库密码
        host=DB_CONFIG['host'],  # 替换为你的数据库主机地址
    )
    conn.autocommit = True
    # 创建一个数据库游标
    cur = conn.cursor()

    # 执行创建数据库的 SQL 语句
    cur.execute(f"CREATE DATABASE {name}")

    # 提交更改
    conn.commit()

    # 关闭游标和数据库连接
    cur.close()
    conn.close()
