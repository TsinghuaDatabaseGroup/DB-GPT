import json


new_dataset = {}
with open("testing_set/testing_set_with_workload.json") as f:

    data = json.load(f)

    for key, value in data.items():
        key_number = int(key)
        # key_number mode 10 ~ [0, 4] 
        if key_number % 10 <=4:

            alerts = value["alerts"]
            alert_info = []
            for alert in alerts:
                alert_info.append({"alert_name": alert["alerts"][0]['labels']['alertname'], "alert_level": alert["alerts"][0]['labels']['level'], "alert_severity": alert["alerts"][0]['labels']['severity']})

            new_dict = {
                "start_time": value["start_time"],
                "end_time": value["end_time"],
                "start_timestamp": value["start_timestamp"],
                "end_timestamp": value["end_timestamp"],
                "alerts": alert_info,
                "workload": value["workload"],
                "dba_diag": ""
            }

            new_dataset[key] = new_dict
            

# load dict in pretty format
with open("testing_set/testing_set_dba.json", "w") as f:
    json.dump(new_dataset, f, indent=4)