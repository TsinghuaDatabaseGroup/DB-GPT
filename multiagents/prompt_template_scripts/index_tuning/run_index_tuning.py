import random
import openai
import os
import re
import numpy as np
import pickle
from data.load_data import load_data
import logging
import sys
import json
import copy

sys.path.append('..')

from automatic_prompt_engineer import ape, config, template, utils
from evaluation.exec_eval import exec_instruction_evaluator
from evaluation.eval_result import SQLEvaluationResult
from evaluation.utility import get_sql_score_index_tuning, create_indexes, drop_indexes
from utils.database import Database, DBArgs

eval_template = "Instruction: [PROMPT]\n\nInput: [INPUT]\nOutput: [OUTPUT]"
prompt_gen_template = " I gave a friend an instruction.\
The friend followed the instruction to output create index statements based on the input SQL queries.\
 The resulting create index statements can be executed on a PostgreSQL database and can reduce the execution latency of the input SQL queries.\
 Based on the instruction they produced the following input-output pairs:\n\n[full_DEMO]\n\nInstruction: [APE]"
demos_template = "Input: [INPUT]\nOutput: [OUTPUT]" 

def generate_prompts(eval_template,
                     demos_template,
                     prompt_gen_data,
                     eval_data,
                     conf,
                     few_shot_data=None,
                     prompt_gen_template=None):
    prompts = ape.find_prompts(eval_template=eval_template,
                                prompt_gen_data=prompt_gen_data,
                                eval_data=eval_data,
                                conf=conf,
                                few_shot_data=few_shot_data,
                                demos_template=demos_template,
                                prompt_gen_template=prompt_gen_template)

    filtered_prompts = []
    for p in prompts:
        prompt = re.sub(r'Input\:.+?;', '', p, flags=re.DOTALL)
        prompt = re.sub(r'Output\:.+?;', '', prompt, flags=re.DOTALL)
        prompt = prompt.replace('\n', '').strip()
        filtered_prompts.append(prompt)
    filtered_prompts = list(set(filtered_prompts))
    logging.info('Deduplicated to {} prompts.'.format(len(filtered_prompts)))
    return filtered_prompts

def eval_prompts(prompts, eval_template, eval_data, demos_template, config):
    logging.info('Evaluating prompts...')

    eval_template_instance = template.EvalTemplate(eval_template) 
    demos_template_instance = template.DemosTemplate(demos_template)

    inputs, _, model_outputs, answers = exec_instruction_evaluator(prompts, eval_template_instance, eval_data, demos_template_instance, config)

    logging.info('Finished evaluating.')   
    return inputs, model_outputs, answers



# Step 1. get the params.
parser = utils.get_parser()
args = parser.parse_args()
task = 'index_tuning'
timeout = -1 # timeout=-1 means no timeout of the query execution time
use_schema = 1 # take data info as LLM input

dbargs = DBArgs("pgsql", utils.get_conf(args.db_conf, 'pgsql_server'), args.eval_dataset)
# db = Database(dbargs, timeout)

# Step 2. set the seed and OpenAI api_key.
openai.api_key = os.environ["OPENAI_API_KEY"]
random.seed(args.seed)

# Step 3. create the directory to store the `result`.
assert not os.path.exists(os.path.dirname(args.logdir.format(args.exp_id))), \
    f"`{os.path.dirname(args.logdir.format(args.exp_id))}` dir already existed! " \
    f"And we don't intend to overwrite anything."
os.makedirs(os.path.dirname(args.logdir.format(args.exp_id)))
os.makedirs(os.path.dirname(args.model_save.format(args.exp_id, 0)))
os.makedirs(os.path.dirname(args.data_save.format(args.exp_id, 0)))

utils.set_logger(args.runlog.format(args.exp_id))
logging.info("Start Adversarial Workload Generation.")

logging.info(f"Create the directory `{os.path.dirname(args.logdir.format(args.exp_id))}` to save experiment result.")

# Step 4. load the training and evaluation data.
induce_data, eval_data = load_data(args.train_data, task, 'train', use_schema), load_data(args.eval_data, task, 'eval', use_schema)

conf = {
    'generation': {
        'num_subsamples': args.gen_sample, # 2 workload samples by default, avoiding exceeding the token limit of LLM (many queries in each workload)
        'num_demos':args.gen_demo,
        'num_prompts_per_subsample': args.gen_prompt_per_sample,
        'model': {
            'gpt_config': {
                'model': args.gen_model,
                'max_tokens': args.gen_max_tokens
            }
        }
    },
    'evaluation': {
        'task': task,
        'num_samples': min(args.eval_sample, len(eval_data[0])),
        'model': {
            'gpt_config': {
                'model': args.eval_model,
                'max_tokens': args.eval_max_tokens
            }
        }
    }
}

conf = config.update_config(conf, args.algo_conf)

# Step 5. generate multiple candidate prompts for the task.

prompts = generate_prompts(eval_template=eval_template,
                                prompt_gen_data=induce_data,
                                eval_data=eval_data,
                                conf=conf,
                                few_shot_data=induce_data,
                                demos_template=demos_template,
                                prompt_gen_template=prompt_gen_template)

train_dict = dict()
train_dict["prompts"] = prompts

train_pik = args.model_save.format(args.exp_id) + task + "_ape_train.dat"

with open(train_pik, "wb") as f:
    pickle.dump(train_dict, f) # save the prompts


# Step 6. evaluate each candidate prompt.

# Step 6.1. get the ape indexes (in list) for each eval workload
### involve column (#-rows, distinct value ratio) in the prompt
inputs, model_outputs, answers = eval_prompts(prompts, eval_template, eval_data, demos_template, conf['evaluation'])

# Step 6.2. reload the SOTA indexes (in list) for each eval workload
num_valid_samples = args.eval_sample
with open(args.eval_data, 'r') as f:
    data = json.load(f)
examples = data['examples']
inputs, outputs = [], []
for i in range(min(args.eval_sample, len(examples))):
    data = examples[str(i + 1)]
    input_, output_ = data['input'], data['output']

    inputs.append(input_)
    outputs.append(output_)
eval_data = (inputs, outputs)

# Step 6.3. 1) (greedy) filter indexes that are out of storage limit; 2) compute the cost reduction of ape indexes
### ape indexes of [args.eval_sample] workloads of the [args.gen_prompt_per_sample] prompts
indexes_ape_under_budget = [[[] for j in range(args.eval_sample)] for i in range(len(prompts))] 
total_index_cost = 0

for j, prediction, ans_ in enumerate(zip(model_outputs, answers)):

    indexes = prediction.split(";")
    updated_indexes = []
    for index in indexes:
        if "CREATE INDEX" in index:
            index = index.replace("\n", "")
            index = index + ";"
            updated_indexes.append(index)

    flag, total_cost, reduced_cost, indexes_under_budget = get_sql_score_index_tuning(indexes, eval_data[0][j], args.storage_budget, args)
    indexes_ape_under_budget[j] = indexes_under_budget

    # compute the cost reduction with the index
    total_index_reduction = total_index_reduction + reduced_cost
    total_index_cost = total_index_cost + total_cost

logging.info("total index cost reduction / total_index_cost: {}/{}".format(total_index_reduction, total_index_cost))


# Step 6.3. compute the latency under selected indexes
latency_database = 0.0000001
latency_sota = 0.0000001

### the latency of workloads in default database (latency_database)
for i,workload in enumerate(eval_data[0]):
    # print("================ workload {} ================".format(i))

    tmpdb = Database(dbargs, timeout)
    for sql in workload:
        query_latency = tmpdb.pgsql_actual_time(sql)
        latency_database = latency_database + query_latency
        # print("query latency: {}".format(query_latency))

    tmpdb.conn.commit()
    tmpdb.conn.close()

######################################################################################################
### clear up the query result cache bfore conducting the next step!! (easier to achieve this in jupyter)
######################################################################################################

### the latency of workloads in default database (latency_sota)
for k,indexes in enumerate(eval_data[1]):
    # print("================ workload {} ================".format(k))
    indexes = indexes.split(";")
    updated_indexes = []
    for index in indexes:
        if "create index" in index:
            index = index.replace("\n", "")
            index = index + ";"
            updated_indexes.append(index)

    create_indexes(updated_indexes)
    # print("create {} indexes".format(len(updated_indexes)))

    tmpdb = Database(dbargs, timeout)
    for sql in eval_data[0][k]:
        query_latency = tmpdb.pgsql_actual_time(sql)
        latency_sota = latency_sota + query_latency
        print("query latency: {}".format(query_latency))

    tmpdb.conn.commit()
    tmpdb.conn.close()

    drop_indexes(updated_indexes)
    print("drop {} indexes".format(len(updated_indexes)))

######################################################################################################
### clear up the query result cache bfore conducting the next step!!
######################################################################################################

### the latency of workloads in database with ape indexes (latency_ape)
results = []
flags = []
costs = []
for j, prompt in enumerate(prompts):

    latency_ape = 0 # compute the total latency of all the eval workloads

    for i,workload in enumerate(eval_data[0]):
        print("================ workload {} ================".format(i))
        updated_indexes = indexes_ape_under_budget[i]

        create_indexes(updated_indexes, args.storage_budget)

        tmpdb = Database(dbargs, timeout)
        for sql in workload:
            query_latency = tmpdb.pgsql_actual_time(sql)
            latency_ape = latency_ape + query_latency
            # print("query latency: {}".format(query_latency))

        tmpdb.conn.commit()
        tmpdb.conn.close()

        drop_indexes(updated_indexes)

    results.append([flag, 
                    "{:.4f}".format(latency_ape), 
                    "{:.4f}".format((latency_database-latency_ape)/latency_database), # latency reduction ratio
                    "{:.4f}".format(latency_sota), 
                    "{:.4f}".format((latency_database-latency_sota)/latency_database),
                    prompt])

sorted_results = sorted(results, key=lambda x: float(x[2]))

for acc, ape_latency, ape_latency_reduction, sota_latency, sota_latency_reduction, prompt in sorted_results[:10]:
    logging.info(f'  {acc}, {ape_latency}, {ape_latency_reduction}, {sota_latency}, {sota_latency_reduction}: {prompt}')

eval_dict = dict()
eval_dict["task"] = task
eval_dict["config"] = conf
eval_dict['prompts'] = prompts
eval_dict["inputs"] = inputs
eval_dict["outputs"] = model_outputs
eval_dict["answers"] = answers
eval_dict["scores"] = results

eval_pik = args.data_save.format(args.exp_id) + task + "_ape_eval.dat"

with open(eval_pik, "wb") as f:
    pickle.dump(eval_dict, f)

######################################################################################################
### clear up the query result cache in the end!!
######################################################################################################