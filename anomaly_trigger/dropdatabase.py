import psycopg2

def dropdatabase(name):
    # 连接到 "postgres" 数据库
    conn = psycopg2.connect(
        dbname="xxx",            # 连接到默认的 "postgres" 数据库
        user="xxx",         # 替换为你的数据库用户名
        password="xxx",     # 替换为你的数据库密码
        host="xxx"              # 替换为你的数据库主机地址
    )

    conn.autocommit = True
    # 创建一个数据库游标
    cur = conn.cursor()

    # 删除数据库的 SQL 语句
    drop_database_query = f"DROP DATABASE IF EXISTS {name}"

    # 执行删除数据库的 SQL 语句
    cur.execute(drop_database_query)

    # 提交更改
    conn.commit()

    # 关闭游标和数据库连接
    cur.close()
    conn.close()
