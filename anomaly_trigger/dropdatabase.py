import psycopg2

def dropdatabase():
    # 连接到 "postgres" 数据库
    conn = psycopg2.connect(
        dbname="postgres",            # 连接到默认的 "postgres" 数据库
        user="dbmind",         # 替换为你的数据库用户名
        password="DBMINDdbmind2020",     # 替换为你的数据库密码
        host="172.27.58.65"              # 替换为你的数据库主机地址
    )

    conn.autocommit = True
    # 创建一个数据库游标
    cur = conn.cursor()

    # 删除数据库的 SQL 语句
    drop_database_query = "DROP DATABASE IF EXISTS tmp"

    # 执行删除数据库的 SQL 语句
    cur.execute(drop_database_query)

    # 提交更改
    conn.commit()

    # 关闭游标和数据库连接
    cur.close()
    conn.close()
