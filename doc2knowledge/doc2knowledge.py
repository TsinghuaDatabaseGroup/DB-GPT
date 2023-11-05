from utilss import *

global llm

def Initialize(doc, target_dir):
    doc_path = pjoin("./docs/", doc)
    CreateFolder(pjoin(doc_path, target_dir))

def Summarize(idx, title, content, summary_min_length=400):
    return llm.Query(SUMMARIZE_PROMPT_MSG + MSG(CONTENT_TEMPLATE.format(idx=idx,title=title,content=content)))['content'] if len(content)>=summary_min_length else content

def CascadingSummary(args):
    doc_path = pjoin("./docs/", args.doc)
    chunks_path = pjoin(doc_path, "raw")
    
    nodes = [{
        'id': parse_id(chunk_name),
        'id_str': '.'.join([str(x) for x in parse_id(chunk_name)]),
        'name': chunk_name,
        'title': chunk_name.split(' ', 1)[-1][:-4],
        'content': read_txt(pjoin(chunks_path, chunk_name)),
        'father': None,
        'children': [],
    } for chunk_name in ListFiles(chunks_path) if chunk_name.endswith('.txt')]

    nodes_mapping = {node['id_str']: node for node in nodes}
    
    for node1, node2 in itertools.permutations(nodes_mapping.values(), 2):
        if is_father(node1['name'], node2['name']):
            nodes_mapping[node1['id_str']]['children'].append(node2['id_str'])
            nodes_mapping[node2['id_str']]['father'] = node1['id_str']
    nodes = topo_sort(list(nodes_mapping.values()))
    
    nodes_mapping = {node['id_str']: node for node in nodes}
    for i, v in enumerate(TQDM(nodes)):
        children = sorted([c for c in v['children']], key=lambda x:str2id(x))
        nodes[i]['index'] = [INDEX_TEMPLATE.format(idx=v['id_str'], title=v['title'])] + [
            INDEX_TEMPLATE.format(idx=c, title=nodes_mapping[c]['title']) for c in children
        ]
        nodes[i]['full_index'] = [INDEX_TEMPLATE.format(idx=v['id_str'], title=v['title'])] + sum(
            [nodes_mapping[c]['full_index'] for c in children], []
        )
        nodes[i]['content_summary'] = Summarize(
            idx = v['id_str'],
            title = v['title'],
            content = v['content'],
            summary_min_length = args.summary_min_length
        )
        nodes[i]['summaries'] = [CONTENT_TEMPLATE.format(idx=v['id_str'], title=v['title'], content=nodes[i]['content_summary'])] + [
            CONTENT_TEMPLATE.format(idx=nodes_mapping[c]['id_str'], title=nodes_mapping[c]['title'], content=nodes_mapping[c]['summary']) for c in children
        ]
        nodes[i]['summary'] = Summarize(
            idx = v['id_str'],
            title = v['title'],
            content = "\n\n".join(nodes[i]['summaries']),
            summary_min_length = 0
        ) if len(nodes[i]['summaries'])>1 else nodes[i]['content_summary']
        nodes[i]['full_summary'] =  DOCUMENT_VIEW_TEMPALTE.format(
            summaries = "\n\n".join(nodes[i]['summaries']),
            index = "\n".join(nodes[i]['full_index']),
        )

    return nodes

def count_num_tokens(messages):
    return len(str(messages).split())


def ExtractKnowledge(nodes_mapping, root_index, iteration=2, iteration_gap=1, source_file='report_example',  target_file="extracted_knowledge.jsonl"):
    r = nodes_mapping[root_index]
    source_sections = [r['name']]
    RULES_EXTRACTION_PROMPT_MSG[0]['content'] = RULES_EXTRACTION_PROMPT_MSG[0]['content'].replace('${alert_info}', ' '.join(r['children']))

    messages = RULES_EXTRACTION_PROMPT_MSG + MSG(r['full_summary'])
    extracted_rules = []

    new_source_sections = source_sections
    while iteration:
        response = llm.Query(messages, functions=[LOOKUP_FUNCTION, SUBMIT_RULE_FUNCTION])
        #print("========================================")
        #print("Extraction Thought:\n" + COLOR1("```\n{0}\n```".format(response['content'])))
        if "function_call" in response:
            if response["function_call"]["name"] == "submit_rule":
                print("Extraction Action:", SUCCESS("Submitting a rule..."))
                try:
                    rule = response["function_call"]["arguments"]
                    # assert (rule.startswith('{\n  "rules": "') and rule.endswith('"\n}'))
                    rule = rule[len('{\n  "rules": '):-len('\n}')]
                    rule = rule.replace('"{','{')
                    rule = rule.replace('"}','}')
                    rule = rule.replace('\\"', '"')

                    # evaluate redundancy
                    new_knowledge = {'source_sections':str(new_source_sections), 'id':len(extracted_rules)-1, 'rule':rule}
                    with open(target_file, 'r') as rf:
                        knowledge_strs = rf.read().split('\n====================\n')
                    not_exist = 1
                    for idx, exist_knowledge in enumerate(knowledge_strs):
                        prompt = LOGICAL_VERIFICATION_PROMPT.format(exist_knowledge=exist_knowledge, new_knowledge=str(new_knowledge))
                        judgment = llm.Query(MSG(prompt))['content'].split('Answer:')[-1].strip().strip('.').lower().strip()
                        if "yes" in judgment.lower():
                            not_exist = 0
                            break

                    if not_exist:
                        extracted_rules.append(rule)
                        message = "Success!"

                        print(COLOR1("```\n{0}\n```".format(rule)))

                        # append to the json file in pretty format
                        with open(target_file, 'a') as wf:
                            wf.write(json.dumps(new_knowledge, indent=4))
                            wf.write('\n====================\n')
                    else:
                        print("Redundant knowledge.")

                    new_source_sections = source_sections

                except:
                    message = "Invaid Rule."
                    print(ERROR(message))
                messages += [response, {'role': "function", "name":"submit_rule", 'content': message}]
            else:
                idx = json.loads(response["function_call"]["arguments"])["index"]
                print("Extraction Action:", SUCCESS(f"Looking up '{idx}'..."))
                try:
                    assert idx in nodes_mapping
                    new_source_sections.append(nodes_mapping[idx]['name'])
                    message = nodes_mapping[idx]['full_summary']
                    print(COLOR1(f"Document Received."))
                except:
                    message = "Invalid Index."
                    print(ERROR(message))
                messages += [response, {'role': "function", "name":"look_up", 'content': message}]
            num_tokens = count_num_tokens(messages)
            print("num_tokens:", num_tokens)
            if num_tokens > 1200:
                break
            iteration -= 1
            # print("========================================")
            if iteration:
                print(WARNING("Waiting for next iteration..."))
                time.sleep(1)
    return extracted_rules

if __name__=="__main__":

    # backend: used llm model
    # doc: document name
    # root_index:

    args = HeavenArguments.from_parser([
        LiteralArgumentDescriptor("backend", default="gpt-4", choices=['gpt-4']),
        StrArgumentDescriptor("doc", short='d', default="report_example"),
        StrArgumentDescriptor("root_index", short='r', default="1"), # e.g., section 1
        IntArgumentDescriptor("summary_min_length", short='l', default=400),
        IntArgumentDescriptor("num_iteration", short='K', default=50),
        IntArgumentDescriptor("iteration_gap", short='T', default=2),
        SwitchArgumentDescriptor("clear_cache", short='c', default=True),
    ])
    if args.c:
        clear_cache()
    target_dir = "extracted_knowledge"

    llm = LLMCore(backend=f"openai_{args.backend}")    

    # First: input the document
    Initialize(args.doc, target_dir)

    # Second: generate the cascading summary index
    nodes = CascadingSummary(args)
    nodes_mapping = {node['id_str']: node for node in nodes}

    assert (args.root_index) in nodes_mapping, f"Invalid root index: {args.root_index}"

    target_file = "./docs/" + args.doc + '/' + target_dir + '/' + "extracted_knowledge_4.jsonl"
    extracted_rules = ExtractKnowledge(nodes_mapping, root_index=args.root_index, iteration=args.num_iteration, iteration_gap=args.iteration_gap, source_file=args.doc,target_file=target_file)