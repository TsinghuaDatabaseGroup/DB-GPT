import json
from difflib import ndiff
import psycopg2
import time

def execute_sql(sql):
    conn = psycopg2.connect(database='tpch10x',
                            user='postgres',
                            password='xxx',
                            host='166.111.121.55',
                            port=15432)

    cur = conn.cursor()
    cur.execute(sql)
    # res = cur.fetchall()[0][0][0]
    res = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    return len(res)

# Load the JSON file as a dictionary
data = {}
with open('text2res_single_table.json', 'r') as f:
    data = json.load(f)

# Select only the diverse SQL statements
# Find SQL statements with an edit distance of less than 10
selected_sql = []
for sql1 in data:

    if 'sql' in sql1:
        sql1 = sql1['sql']
        print("==========sql", sql1)
        start_time = time.time()
        res_cnt = execute_sql(sql1)
        end_time = time.time()
        elapsed_time = end_time - start_time

        print(res_cnt, elapsed_time)

        selected_sql.append({f"sql": sql1, 'res_cnt': res_cnt, 'execution_time': elapsed_time})


# Write the dictionary to a JSON file
with open("text2res_single_table2.json", "w") as f:
    json.dump(selected_sql, f)


# # Select only the diverse SQL statements
# # Find SQL statements with an edit distance of less than 10
# selected_sql = []
# for workload in data:
#     queries = workload['workload']
    
#     for i, sql1 in enumerate(queries):
#         selected = 1
#         if 'sql' in sql1:
#             sql1 = sql1['sql']
#             print("==========sql", sql1)
#             start_time = time.time()
#             res_cnt = execute_sql(sql1)
#             end_time = time.time()
#             elapsed_time = end_time - start_time

#             print(res_cnt, elapsed_time)
#             if res_cnt != 0:
#                 # verify the sql result is not null

#                 for j, sql2 in enumerate(selected_sql):
#                     res = [1 for line in ndiff(sql1, sql2) if line.startswith('?')]

#                     if len(res) > 14:
#                         selected = 0
#                         break
#                 if selected:
#                     selected_sql.append([sql1,res_cnt,elapsed_time])
#                     if len(selected_sql) == 50:
#                         print("Finished!")
#                         sql_dict = [{f"sql": sql[0], 'res_cnt': sql[1], 'execution_time': sql[2]} for i, sql in enumerate(selected_sql)]

#                         # Write the dictionary to a JSON file
#                         with open("test_query.json", "w") as f:
#                             json.dump(sql_dict, f)
#                         exit(0)
#     print(len(selected_sql))