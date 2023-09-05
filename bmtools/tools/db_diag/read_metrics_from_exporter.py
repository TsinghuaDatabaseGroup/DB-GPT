import json
import re


def remove_datname(string):
    pattern = r',?\s*datname=~"\$datname"\s*,?'
    result = re.sub(pattern, '', string)
    return result


def remove_release(string):
    pattern = r',?\s*release="\$release"\s*,?'
    result = re.sub(pattern, '', string)
    return result


def remove_mountpoint(string):
    # pattern = r'\s*,?\s*mountpoint=~"\maxmount"\s*,?\s*'
    # result = re.sub(pattern, '', string)
    return string.replace('mountpoint="$maxmount",', '')


if __name__ == '__main__':
    pg_ignores_name = ["General Counters, CPU, Memory and File Descriptor Stats", "Version", "Start Time", "Max Connections", ""]
    node_ignores_name = ["system running time", "#-CPU-Cores"]
    exprs = []
    pg_path = './pg_exporter.json'
    node_path = './node_exporter.json'
    with open(pg_path, "r+") as f:
        json_data = json.load(f)
        json_data = json_data['panels']
        print(type(json_data))
        for data in json_data:
            title = data.get('title', '')
            if title in node_ignores_name:
                continue
            print(title)
            targets = data.get('targets', [])
            for target in targets:
                expr = target.get('expr', '')
                expr = remove_datname(expr)
                expr = remove_release(expr)
                # expr = remove_mountpoint(expr)
                exprs.append({'title': title, 'expr': expr})
                print(expr)

    metrics_file = open('./pg_metrics.txt', 'w+')
    metrics_file.write(json.dumps(exprs))
    metrics_file.close()
