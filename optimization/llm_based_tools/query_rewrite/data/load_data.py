import json

def load_data(path, task, type):

    with open(path, 'r') as f:
        data = json.load(f)

    examples = data['examples']
    num_examples = len(examples)

    inputs, outputs = [], []
    for i in range(num_examples):
        data = examples[str(i + 1)]
        if task == 'query_rewrite':
            if type == 'train':
                input_, output_ = data['input'], data['output']
            else:
                input_, output_ = data['input'], {'output':data['output'], 'result':data['result'] if 'result' in data else None, 'result_len':data['result_len'], 'input_cost':data['input_cost'], 'output_cost':data['output_cost'], 'dataset':data['dataset'], 'input_latency':data['input_latency'], 'output_latency':data['output_latency']}

        inputs.append(input_)
        outputs.append(output_)
    return inputs, outputs
