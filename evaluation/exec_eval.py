from utils import llm, data
from evaluation import utility
import random


def get_query(prompt, eval_template, input_, output_, demo_data, demos_template):
    demos = demos_template.fill(demo_data)
    query = eval_template.fill(prompt=prompt,
                               input=input_,
                               output='',
                               full_demo=demos)
    return query

def exec_instruction_evaluator(prompts, eval_template, eval_data, demos_template, config):
    inputs = []
    queries = []
    answers = []
    for prompt in prompts:
        subsampled_data = data.subsample_data(
            eval_data, config['num_samples'])
        for d in zip(*subsampled_data):
            input_, output_ = d
            demo_data = [], []
            query = get_query(
                prompt, eval_template, input_, output_, demo_data, demos_template)
            inputs.append(input_)
            queries.append(query)
            answers.append(output_)

    # Instantiate the LLM
    model = llm.model_from_config(config['model'])
    model_outputs = model.generate_text(queries, 1)

    return inputs, queries, model_outputs, answers

def filter_sample_num(prompt, eval_template, input_, output_, demos_template, demo_data, max_tokens):
    tmp_demo_data = [], []
    tmp_query = get_query(
            prompt, eval_template, input_, output_, tmp_demo_data, demos_template)
    max_nchars = 4097 - len(tmp_query) - max_tokens
    filtered_demo_data = [], []
    for i in range(len(demo_data[0])):
        slen = len(demo_data[0][i]) + len(demo_data[1][i])
        if i > 0:
            slen += len(demos_template.delimiter)
        if max_nchars >= slen:
            filtered_demo_data[0].append(demo_data[0][i])
            filtered_demo_data[1].append(demo_data[1][i])
            max_nchars -= slen

    return filtered_demo_data

def exec_prompt_evaluator(prompts, eval_template, test_corpus, test_labels, train_corpus, train_labels, kNN_test_train, demos_template, config, descend=False):
    inputs = []
    queries = []
    answers = []
    for prompt in prompts:
        subsampled_indices = random.sample(range(len(test_corpus)), config['num_samples'])
        for i in subsampled_indices:
            input_, output_ = test_corpus[i], test_labels[i]
            train_indices = kNN_test_train[i][:config['num_few_shot']]
            demo_data = [train_corpus[i] for i in train_indices], [train_labels[i] for i in train_indices]
            demo_data = filter_sample_num(prompt, eval_template, input_, output_, demos_template, demo_data, config['model']['gpt_config']['max_tokens'])
            if descend:
                demo_data = list(reversed(demo_data[0])), list(reversed(demo_data[1]))
            query = get_query(
                prompt, eval_template, input_, output_, demo_data, demos_template)
            inputs.append(input_)
            queries.append(query)
            answers.append(output_)

    # Instantiate the LLM
    model = llm.model_from_config(config['model'])
    model_outputs = model.generate_text(queries, 1)

    return inputs, queries, model_outputs, answers
