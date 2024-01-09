import random
import openai
import os
import re
import numpy as np
import pickle
from data.load_data import load_data
import logging
import sys

sys.path.append('..')

from automatic_prompt_engineer import ape, config, template, utils
from evaluation.exec_eval import exec_instruction_evaluator
from evaluation.eval_result import SQLEvaluationResult
from evaluation.utility import get_sql_latc_cost
from utils.database import DBArgs

eval_template = "Instruction: [PROMPT]\n\nInput: [INPUT]\nOutput: [OUTPUT]"
prompt_gen_template = "I gave a friend an instruction. The friend followed the instruction to rewrite the input SQL query to produce an equivalent SQL query. The resulting output SQL query can be executed on a PostgreSQL database with decreased latency. Based on the instruction they produced the following input-output pairs:\n\n[full_DEMO]\n\nInstruction: [APE]"

#  Accordingly they produced the following input-output pairs:

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


''' 
    The following code is used to evaluate the generated prompts.   
'''
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
task = 'query_rewrite'

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
induce_data, eval_data = load_data(args.train_data, task, 'train'), load_data(args.eval_data, task, 'eval')

conf = {
    'generation': {
        'num_subsamples': args.gen_sample,
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

print(os.path.join( os.path.dirname(__file__), args.algo_conf))
conf = config.update_config(conf, os.path.join( os.path.dirname(__file__), args.algo_conf))

# Step 5. generate instructions.

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
    pickle.dump(train_dict, f)

# Step 6. evaluate instructions.

inputs, model_outputs, answers = eval_prompts(prompts, eval_template, eval_data, demos_template, conf['evaluation'])

scores = []
flags = []
costs = []
for prediction, ans_ in zip(model_outputs, answers):
    dbargs = DBArgs("pgsql", utils.get_conf(args.db_conf, 'pgsql_server'), ans_['dataset'])
    flag, cost, latency = get_sql_latc_cost(prediction, ans_, dbargs, 60)
    scores.append([flag, latency, float(ans_['input_latency']), float(ans_['output_latency']), cost, float(ans_['input_cost']), float(ans_['output_cost'])])

scores = np.array(scores).reshape(len(prompts), conf['evaluation']['num_samples'], 7)
res = SQLEvaluationResult(prompts, scores)
sorted_results = res.sorted_latc()
logging.info('Accuracy\tNormalized Rewrite Latency\tRewrite Latency\tInput Latency\tAnswer Latency\tPrompt')
for acc, norm_latency, latency, input_latency, output_latency, cost, input_cost, output_cost, prompt in sorted_results[:10]:
    logging.info(f'{acc}\t{norm_latency}\t{latency}\t{input_latency}\t{output_latency}\t{prompt}')

eval_dict = dict()
eval_dict["task"] = task
eval_dict["config"] = conf
eval_dict['prompts'] = prompts
eval_dict["inputs"] = inputs
eval_dict["outputs"] = model_outputs
eval_dict["answers"] = answers
eval_dict["scores"] = scores
eval_dict["results"] = sorted_results

eval_pik = args.data_save.format(args.exp_id) + task + "_ape_eval.dat"

with open(eval_pik, "wb") as f:
    pickle.dump(eval_dict, f)

