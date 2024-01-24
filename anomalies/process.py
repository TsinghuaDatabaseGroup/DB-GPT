import json

# def extract_alert(alerts):

#     alert_list = []
#     for alert in alerts:
#         alert_list.append(alert['alerts'][0]['labels']['alertname'])

#     return str(alert_list)

# with open("testing_set_with_workload_new.json", 'r') as f:
#     cases = json.load(f)

# alerts = {}
# for id in cases:
#     # cases[id]
#     new_alert = extract_alert(cases[id]["alerts"])
#     if  new_alert not in alerts:
#         alerts[new_alert] = [cases[id]]
#     elif len(alerts[new_alert]) < 2:
#         alerts[new_alert].append(cases[id])

# alert_json = {}

# num = 0
# for alert in alerts:
#     print(alert, len(alerts[alert]))
#     for case in alerts[alert]:
#         alert_json[str(num)] = case
#         num += 1

# with open("batch_testing_set.json", 'w') as f:
#     json.dump(alert_json, f)

with open("../test_cases/batch_testing_set.json", 'r') as f:
    dicts = json.load(f)

for dict in dicts:
    print(dicts[dict]["labels"])