import json

with open('text2res_origin.json', 'r') as json_file:
    json_data = json.load(json_file)

total_time = 0

for i,item in enumerate(json_data):
    print(item['execution_time'])
    total_time = total_time + float(item['execution_time'])

print(total_time)