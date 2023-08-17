import json

data = {}
with open('/Users/xuanhe/Documents/our-paper/instructdb/code/BMTools/bmtools/tools/database/data/tpch10x/s103_tpch_1gb_w10_index_all.json', 'r') as f:
    data = json.load(f)

# Select only the diverse SQL statements
# Find SQL statements with an edit distance of less than 10
cnt = 0
end = 0
with open("extracted_sqls_s103_tpch_1gb.txt", 'w') as wf:

    selected_sql = []
    for workload in data:
        if end == 0:
            for query in workload["workload"]:
                if "sql" in query and end == 0:
                    wf.write(query['sql']+';\n')
                    cnt = cnt + 1
                    if cnt >= 10000:
                        end = 1
        else:
            break