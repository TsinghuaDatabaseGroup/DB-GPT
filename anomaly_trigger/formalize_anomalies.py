import re
import datetime
#from alert import filter_alerts_by_time
import json
'''
def dataset_statistics():
    max_column = 0
    min_column = 100000000000000

    keywords = ["retail",
    "online marketplace",
    "online platform",
    "online store",
    "e-commerce",
    "sales"]

    keywords = ['iot']

    keywords = ['smart home']

    keywords = ['financial']

    keywords = ['social media']

    keywords = ['file sharing']

    # keyword = [
    # "data processing",
    # "data analytics",
    # "big data",
    # "data-intensive"]

    anomalies = []

    # read all lines in command-datasets.txt into commands in list
    count1 = 0
    commands = []
    with open('command-datasets.txt', 'r') as f:
        for line in f:
            if ',' in line:
                count1 += 1
            line = line.strip()
            commands.append(line)


    with open('nl-datasets.txt', 'r') as f:
        #print("lines:",len(f.readlines()))
        for i,line in enumerate(f):
            yes = 0
            for keyword in keywords:
                if keyword in line.lower():
                    yes = 1
                    break

            if yes == 1:

                # write into a file named nl-datasets-iot.txt
                # with open('nl-datasets-bi.txt', 'a') as f2:
                #     line = line.strip()
                #     f2.write(line+'\n\n')

                # re: detect the "columns" substring in the line string and extract the string before "columns"
                # before_columns = re.search(r'(.*)columns', line.lower())
                # if before_columns is None:
                #     continue
                # before_columns = before_columns.group(1)
                # before_columns = before_columns.split()
                # column_value = before_columns[-1]
                # # if column_value is a string of numbers
                # if column_value.isdigit():
                #     column_value = int(column_value)
                #     if column_value > max_column:
                #         max_column = column_value
                #     if column_value < min_column:
                #         min_column = column_value

                # match anomalies

                command = commands[i]
                #import pdb; pdb.set_trace()

                # command_words = command.split()[3]
                # command_words = command_words.split(',')
                # for word in command_words:
                #     if word not in anomalies:
                #         anomalies.append(word)
                if "ncolumn" in command:
                    col_num = command.split()[7]
                    if col_num.isdigit():
                        col_num = int(col_num)
                        if col_num > max_column:
                            max_column = col_num
                        if col_num < min_column:
                            min_column = col_num

    print('num of ,:',count1)
    print("max_column: ", max_column)
    print("min_column: ", min_column)
'''
def time_stamps():

    splitting_token = """


import"""

    #dir_name = "up_to_date_dataset/"

    # target_datetime = datetime.datetime(2023, 10, 10, 3, 0, 0)

    alert_cnt = 0
    commands = []

    root_causes = {
        "INSERT_LARGE_DATA": ["highly concurrent commits or highly concurrent inserts"],
        "LOCK_CONTENTION": ["highly concurrent updates"],
        "VACUUM": ["highly deletes"],
        "REDUNDANT_INDEX": ["too many indexes"],
        "MISSING_INDEXES": ["missing indexes"],
        "INSERT_LARGE_DATA,IO_CONTENTION": ["INSERT_LARGE_DATA","IO_CONTENTION"],
        "FETCH_LARGE_DATA,CORRELATED_SUBQUERY": ["FETCH_LARGE_DATA","CORRELATED SUBQUERY"],
        "POOR_JOIN_PERFORMANCE,CPU_CONTENTION": ["POOR JOIN PERFORMANCE","CPU CONTENTION"],
    }


    with open('m_i_naturallanguage.txt', 'r') as f:
        # read f content into nlps in list
        desc_blocks = f.readlines()

    with open('m_i_code.txt', 'r') as f:
        # read all the f content into nlps in a text
        nlps = f.read()
        code_blocks = nlps.split(splitting_token)
        new_code_blocks = []
        for code_block in code_blocks:            
            new_code_blocks.append('import ' + code_block)
        code_blocks = new_code_blocks

    anomaly_jsons = []

    with open('missingindex_with_timestamp.txt', 'r') as f:
        #print("lines:",len(f.readlines()))

        while True:
            line1 = f.readline()
            line2 = f.readline()
            
            if not line1:
                break

            content = {"start_time": "111233","end_time": "111433", "start_timestamp": "111233","end_timestamp": "111433", "alerts": [], "labels":[], "command": "", "script": "", "description": ""}

            #import pdb; pdb.set_trace()

            timestamp = line1.split()[-1]
            command = line1.split()[0:4]
            command_str= ' '.join(command)
            if command_str not in commands:
                commands.append(command_str)

            content["command"] = command_str
            content["start_time"] = timestamp
            if timestamp.isdigit():
                timestamp = int(timestamp)
                # convert seconds to datetime (year, month, day, hour, minute, second)
                dt_object = datetime.datetime.fromtimestamp(timestamp)
                # 2023-10-10 03:00:00
                formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                content["start_timestamp"] = formatted_time

            timestamp = line2.split()[-1]
            content["end_time"] = timestamp
            if timestamp.isdigit():
                timestamp = int(timestamp)
                # convert seconds to datetime (year, month, day, hour, minute, second)
                dt_object = datetime.datetime.fromtimestamp(timestamp)
                # 2023-10-10 03:00:00
                formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                content["end_timestamp"] = formatted_time
            
            # alerts
            '''alerts = filter_alerts_by_time("alert.txt", content["start_time"], content["end_time"])
            content["alerts"] = alerts
            if alerts!=[]:
                print(alert_cnt, alerts)
                alert_cnt = alert_cnt + 1'''

            # labels
            for cause in root_causes:
                if cause in command_str:
                    content["labels"] = root_causes[cause]

            if len(anomaly_jsons) >= len(code_blocks):
                break

            # script
            content["script"] = code_blocks[len(anomaly_jsons)]
                                
            # description
            content["description"] = desc_blocks[len(anomaly_jsons)]

            anomaly_jsons.append(content)


            # record the content in well-formatted json into a file
            with open('anomaly_jsons.txt', 'a') as f2:
                f2.write(json.dumps(content, indent=4) + '\n')

    print("alert_cnt:", alert_cnt)

    return anomaly_jsons

anomaly_jsons = time_stamps()