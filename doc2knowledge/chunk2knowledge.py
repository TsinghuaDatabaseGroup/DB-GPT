from utilss import *
import ast
import os

global llm

def Initialize(doc, target_dir):
    doc_path = pjoin("./docs/", doc)
    CreateFolder(pjoin(doc_path, target_dir))

def Summarize(idx, title, content, summary_min_length=400):
    
    return llm.Query(SUMMARIZE_PROMPT_MSG + MSG(CONTENT_TEMPLATE.format(idx=idx,title=title,content=content)))["content"] if len(content)>=summary_min_length else content

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
    
    relevant_nodes = ['1.5', '1.1', '1.3', '1.2', '1.4']
    #RULES_EXTRACTION_PROMPT_MSG[0]['content'] = RULES_EXTRACTION_PROMPT_MSG[0]['content'].replace('${alert_info}', ' '.join(r['children']))
    RULES_EXTRACTION_PROMPT_MSG[0]['content'] = RULES_EXTRACTION_PROMPT_MSG[0]['content'].replace('${alert_info}', str(relevant_nodes))

    messages = RULES_EXTRACTION_PROMPT_MSG + MSG(r['full_summary'])
    extracted_rules = []

    new_source_sections = source_sections
    while iteration:

        function_response = llm.Query(messages, functions=[LOOKUP_FUNCTION, SUBMIT_RULE_FUNCTION])
        #print("========================================")
        #print("Extraction Thought:\n" + COLOR1("```\n{0}\n```".format(response['content'])))
        
        response = {"function_call": {}}
        if function_response != None and "function_call" in function_response:
            response["function_call"]["name"] = function_response["function_call"]["name"]
            response["function_call"]["arguments"] = function_response["function_call"]["arguments"]

        if response["function_call"] != {}:
            if response["function_call"]["name"] == "submit_rule":
                
                print("Extraction Action:", SUCCESS("Submitting a rule..."))
                try:
                    rule = response["function_call"]["arguments"]

                    # import pdb; pdb.set_trace()
                    # assert (rule.startswith('{\n  "rules": "') and rule.endswith('"\n}'))

                    rule = rule[len('{\n  "rules": '):-len('\n}')]
                    rule = rule.replace('"{','{')
                    # rule = rule.replace('"}','}')
                    rule = rule.replace('}"','}')
                    rule = rule.replace('\\"', '"')

                    if '['  in rule:
                        rule = rule.replace('"[', '[')
                        rule = rule.replace(']"', ']')
                        rule = rule.strip()

                    if not os.path.exists(target_file):
                        with open(target_file, 'w') as wf:
                            wf.write('')
                        knowledge_strs = {}
                    else:
                        with open(target_file, 'r') as rf:
                            # load json file
                            knowledge_strs = json.load(rf)

                    rule = ast.literal_eval(rule)

                    if isinstance(rule, dict):
                        rules = [rule]
                    else:
                        rules = rule

                    try:
                        for rule in rules:
                        # evaluate redundancy
                            new_knowledge = {'source_sections':str(new_source_sections), 'rule':rule}
                            # create target_file if not exist

                            not_exist = 1
                            for knowledge_id in knowledge_strs:
                                exist_knowledge = str(knowledge_strs[knowledge_id])

                                prompt = LOGICAL_VERIFICATION_PROMPT.format(exist_knowledge=exist_knowledge, new_knowledge=str(new_knowledge))
                                judgment = llm.Query(MSG(prompt))["content"].split('Answer:')[-1].strip().strip('.').lower().strip()
                                if "yes" in judgment.lower():
                                    not_exist = 0
                                    break

                            if not_exist:
                                extracted_rules.append(rule)
                                message = "Success!"
                                print(COLOR1("```\n{0}\n```".format(rule)))

                                # append to the json file in pretty format
                                knowledge_strs[str(len(knowledge_strs))] = new_knowledge
                            else:
                                knowledge_strs[knowledge_id] = new_knowledge
                                print(COLOR1("```\n{0}\n```".format(rule)))
                                print(f"source sections: {str(new_source_sections)}")

                                print(COLOR2("Redundant knowledge."))

                            with open(target_file, 'w') as wf:
                                json.dump(knowledge_strs, wf, indent=4)

                            new_source_sections = source_sections
                    except:
                        import pdb; pdb.set_trace()
                        rules = ""

                except:
                    import pdb; pdb.set_trace()
                    message = "Invaid Rule."
                    print(ERROR(message))
                    rules = ""
                messages += [{'role': "function", "name":"submit_rule", 'content': rules}]
            else:
                idx = json.loads(response["function_call"]["arguments"])["index"]
                print("Extraction Action:", SUCCESS(f"Looking up '{idx}'..."))
                try:
                    assert idx in nodes_mapping
                    new_source_sections.append(nodes_mapping[idx]['name'])
                    message = nodes_mapping[idx]['content']
                    print(COLOR1(f"Document Received."))
                except:
                    message = "Invalid Index."
                    print(ERROR(message))
                messages += [{'role': "function", "name":"look_up", 'content': message}]
            num_tokens = count_num_tokens(messages)
            import pdb; pdb.set_trace()
            print("num_tokens:", num_tokens)
            if num_tokens > 100000:
                break
            iteration -= 1
            # print("========================================")
            if iteration:
                print(WARNING("Waiting for next iteration..."))
                time.sleep(1)
        
    return extracted_rules


if __name__=="__main__":

    args = HeavenArguments.from_parser([
        LiteralArgumentDescriptor("backend", default="gpt-4", choices=['gpt-4']),
        StrArgumentDescriptor("doc", short='d', default="docs/case_guide"),
        StrArgumentDescriptor("root_index", short='r', default="1"), # e.g., section 1
        IntArgumentDescriptor("summary_min_length", short='l', default=400),
        IntArgumentDescriptor("num_iteration", short='K', default=200),
        IntArgumentDescriptor("iteration_gap", short='T', default=200),
        SwitchArgumentDescriptor("clear_cache", short='c', default=True),
    ])

    if args.c:
        clear_cache()
    target_dir = "extracted_knowledge"

    llm = LLMCore(backend=f"openai_{args.backend}")

    # get all the files that within the args.doc+target_dir directory
    files = os.listdir(pjoin(args.doc, "raw"))

    chunks = []
    for file in files:
        if "copy" in file:
            # open the file and get the content split by "=========================================================================================="
            with open(pjoin(args.doc, "raw", file), 'r') as rf:
                content = rf.read().split("==========================================================================================")
                chunks = chunks + content

    target_file = args.doc + '/extracted_knowledge/' + "extracted_knowledge_from_chunks.jsonl"

    if not os.path.exists(target_file):
        with open(target_file, 'w') as wf:
            wf.write('')
        knowledge_strs = {}
    else:
        with open(target_file, 'r') as rf:
            # load json file
            if rf.read() == '':
                knowledge_strs = {}
            else:
                rf.seek(0)
                knowledge_strs = json.load(rf)


    extracted_rules = []
    extraction_prompt = RULES_EXTRACTION_PROMPT_MSG[0]['content']
    for chunkd_id, chunk in enumerate(chunks):
        new_rules = []
        print("chunk id: ", chunkd_id)
        for i in range(3):

            # convert new_rules into a string separated by lines
            new_rules_str = ""
            for single_rule in new_rules:
                new_rules_str += str(single_rule) + "\n"

            RULES_EXTRACTION_PROMPT_MSG[0]['content'] = RULES_EXTRACTION_PROMPT_MSG[0]['content'].replace('${existing_rules}', str(new_rules_str))

            messages = RULES_EXTRACTION_PROMPT_MSG + MSG(str(chunk))
            response = llm.Query(messages)
            RULES_EXTRACTION_PROMPT_MSG[0]['content'] = extraction_prompt
            
            if response != None and 'content' in response:
                print("Extraction Action:", SUCCESS("Submitting a rule..."))
                try:
                    rule = response['content']

                    # import pdb; pdb.set_trace()
                    # assert (rule.startswith('{\n  "rules": "') and rule.endswith('"\n}'))

                    # rule = rule[len('{\n  "rules": '):-len('\n}')]
                    rule = rule.replace('"{','{')
                    # rule = rule.replace('"}','}')
                    rule = rule.replace('}"','}')
                    rule = rule.replace('\\"', '"')

                    if '['  in rule:
                        rule = rule.replace('"[', '[')
                        rule = rule.replace(']"', ']')
                    rule = rule.strip()

                    rules = rule.split('\n\n')

                    try:
                        for rule in rules:
                        
                            rule = json.loads(rule)

                            if rule not in new_rules:
                                new_rules.append(rule)
                                print(COLOR1("```\n{0}\n```".format(rule)))
                            else:
                                print(COLOR2("Redundant knowledge."))
                            # new_source_sections = source_sections
                    except:
                        rules = ""

                except:
                    message = "Invaid Rule."
                    print(ERROR(message))
                    rules = ""

        for rule in new_rules:
            if rule not in knowledge_strs.values():
                knowledge_strs[str(len(knowledge_strs))] = rule

        with open(target_file, 'w') as wf:
            json.dump(knowledge_strs, wf, indent=4)


    # # First: input the document
    # Initialize(args.doc, target_dir)

    # # Second: generate the cascading summary index
    # nodes = CascadingSummary(args)
    # nodes_mapping = {node['id_str']: node for node in nodes}

    # assert (args.root_index) in nodes_mapping, f"Invalid root index: {args.root_index}"

    # target_file = "./docs/" + args.doc + '/' + target_dir + '/' + "extracted_knowledge_test.jsonl"
    # extracted_rules = ExtractKnowledge(nodes_mapping, root_index=args.root_index, iteration=args.num_iteration, iteration_gap=args.iteration_gap, source_file=args.doc,target_file=target_file)