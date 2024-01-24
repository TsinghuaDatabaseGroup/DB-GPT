from utilss import *
import ast
import os

global llm

def Summarize(idx, title, content, summary_min_length=400):
    
    return llm.Query(SUMMARIZE_PROMPT_MSG + MSG(CONTENT_TEMPLATE.format(idx=idx,title=title,content=content)))["content"] if len(content)>=summary_min_length else content

def CascadingSummary(chunks_path):
    
    nodes = [{
                'id': parse_id("0 root"),
                'id_str': '0',
                'name': "0 root",
                'title': 'root',
                'content': '',
                'father': None,
                'children': [],
            }]
    for chunk_name in ListFiles(chunks_path):
        if chunk_name.endswith('.txt'):
            nodes.append({
                'id': parse_id(chunk_name),
                'id_str': '.'.join([str(x) for x in parse_id(chunk_name)]),
                'name': chunk_name,
                'title': chunk_name.split(' ', 1)[-1][:-4],
                'content': read_txt(pjoin(chunks_path, chunk_name)),
                'father': None,
                'children': [],
            })

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
    
    RULES_EXTRACTION_PROMPT_MSG[0]['content'] = RULES_EXTRACTION_PROMPT_MSG[0]['content'].replace('${relevant_chapters}', ' '.join(r['children']))

    # relevant_nodes = ['1.5', '1.1', '1.3', '1.2', '1.4']
    # RULES_EXTRACTION_PROMPT_MSG[0]['content'] = RULES_EXTRACTION_PROMPT_MSG[0]['content'].replace('${relevant_chapters}', str(relevant_nodes))

    if os.path.exists(target_file):
        return []
        with open(target_file, 'r') as rf:
            # if rf content is empty
            if rf.read() == '':
                knowledge_strs = {}
            else:
                rf.seek(0)
                knowledge_strs = json.load(rf)    
    else:
        knowledge_strs = {}

    messages = RULES_EXTRACTION_PROMPT_MSG + MSG(r['full_summary'])
    messages[0]['content'] = messages[0]['content'].replace('${existing_rules}', str(knowledge_strs))

    extracted_rules = []
    used_chapters = []

    # copy the values of source_sections for new_source_sections
    new_source_sections = source_sections.copy()

    while iteration:
        print("The {}th iteration ...".format(iteration))

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

                    # rule = rule.replace('"{','{')
                    # # rule = rule.replace('"}','}')
                    # rule = rule.replace('}"','}')
                    # rule = rule.replace('\\"', '"')

                    # if '['  in rule:
                    #     rule = rule.replace('"[', '[')
                    #     rule = rule.replace(']"', ']')
                    #     rule = rule.strip()

                    # if rule.startswith('{\n  "blocks": "') and rule.endswith('"\n}'):
                    #     rule = rule[len('{\n  "blocks": '):-len('\n}')]

                    rule = ast.literal_eval(rule)

                    if 'blocks' in rule:
                        rule = rule['blocks']
                        if isinstance(rule, str):
                            rule = rule.replace('\n', '\\n')
                            rule = ast.literal_eval(rule)

                    if isinstance(rule, dict):
                        rules = [rule]
                    else:
                        rules = rule

                    if not os.path.exists(target_file):
                        with open(target_file, 'w') as wf:
                            wf.write('')
                        knowledge_strs = {}
                    else:
                        with open(target_file, 'r') as rf:
                            # if rf content is empty
                            if rf.read() == '':
                                knowledge_strs = {}
                            else:
                                rf.seek(0)
                                knowledge_strs = json.load(rf)                            

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

                            with open(target_file, 'w', encoding='utf-8') as wf:
                                json.dump(knowledge_strs, wf, ensure_ascii=False, indent=4)

                            # update the prompt (explore similar nodes from scratch)
                            messages = RULES_EXTRACTION_PROMPT_MSG + MSG(r['full_summary'])
                            messages[0]['content'] = messages[0]['content'].replace('${existing_rules}', str(knowledge_strs))

                            for chatper in new_source_sections:
                                if chatper not in used_chapters:
                                    used_chapters.append(chatper)

                            messages[0]['content'] = messages[0]['content'].replace('${used_chapters}', str(used_chapters))

                        new_source_sections = source_sections.copy()
                    except:
                        rules = ""

                except Exception as e:
                    # import pdb; pdb.set_trace()
                    message = "Invaid Rule."
                    print(ERROR(message))
                    rules = ""
                    iteration += 3
                messages += [{'role': "function", "name":"submit_rule", 'content': str(rules)}]
                
            else:
                idx = json.loads(response["function_call"]["arguments"])["index"]
                print("Extraction Action:", SUCCESS(f"Looking up '{idx}'..."))
                try:
                    assert idx in nodes_mapping

                    if nodes_mapping[idx]['name'] in new_source_sections:
                        message = f"Redundant Source Section {nodes_mapping[idx]['name']}."
                        print(ERROR(message))
                    else:
                        new_source_sections.append(nodes_mapping[idx]['name'])
                        message = nodes_mapping[idx]['content']
                        print(COLOR1(f"Document Received."))
                except:
                    message = "Invalid Index."
                    print(ERROR(message))
                messages += [{'role': "function", "name":"look_up", 'content': message}]
            num_tokens = count_num_tokens(messages)
            print("num_tokens:", num_tokens)
            if num_tokens > 2000:
                break
        iteration -= 1
        # print("========================================")
        if iteration % 10 == 0:
            print(WARNING("Waiting for next 10 iterations ... "))
            time.sleep(1)
        
    return extracted_rules





if __name__=="__main__":

    args = HeavenArguments.from_parser([
        LiteralArgumentDescriptor("backend", default="gpt-4", choices=['gpt-4']),
        StrArgumentDescriptor("doc", short='d', default="docs/enmo/reports"),
        StrArgumentDescriptor("root_index", short='r', default="0"), # e.g., section 0
        IntArgumentDescriptor("summary_min_length", short='l', default=200),
        IntArgumentDescriptor("num_iteration", short='K', default=30),
        IntArgumentDescriptor("iteration_gap", short='T', default=1),
        SwitchArgumentDescriptor("clear_cache", short='c', default=True),
    ])

    if args.c:
        clear_cache()
    target_dir = "extracted_knowledge"

    llm = LLMCore(backend=f"openai_{args.backend}")

    # get the sections of all the files that within the args.doc directory
    doc_section_dirs = []
    for root, dirs, files in os.walk(args.doc):
        for dir in dirs:
            doc_section_dirs.append(pjoin(root, dir))


    num_with_multi_sections = 0

    for i,section_dir in enumerate(doc_section_dirs):
        
        print(f"Processing {i+1}/{len(doc_section_dirs)}: {section_dir}")

        target_file = os.path.abspath(os.path.join(args.doc, f"knowledge_from_{section_dir.split('/')[-2]}.jsonl"))
        if os.path.exists(target_file):
            continue

        if len(ListFiles(section_dir)) > 1:
            num_with_multi_sections += 1
            print(f"Multi-sections: {section_dir}")
        else:
            continue

        # generate the cascading summary index
        nodes = CascadingSummary(section_dir)
        nodes_mapping = {node['id_str']: node for node in nodes}

        if (args.root_index) not in nodes_mapping:
            print(f"Invalid root index: {section_dir}")
            continue        

        extracted_knowlege_chunks = ExtractKnowledge(nodes_mapping, root_index=args.root_index, iteration=args.num_iteration, iteration_gap=args.iteration_gap, source_file=args.doc,target_file=target_file)
    
    print(f"num_with_multi_sections: {num_with_multi_sections}")