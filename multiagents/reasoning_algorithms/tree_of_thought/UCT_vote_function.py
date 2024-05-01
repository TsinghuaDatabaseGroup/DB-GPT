from multiagents.reasoning_algorithms.tree_of_thought.Tree.Tree import my_tree, tree_node
from copy import deepcopy
from multiagents.reasoning_algorithms import base_search_method
from multiagents.prompt_templates.tree_search_prompts import (
    DIVERSITY_PROMPT,
    VOTE_BEST_SYSTEM_PROMPT, VOTE_BEST_SYSTEM_PROMPT_zh,
    VOTE_BEST_USER_PROMPT, VOTE_BEST_USER_PROMPT_zh,
)
from multiagents.prompt_templates.reflexion_prompts import (
    MAKE_REFLEXION_USER_PROMPT, MAKE_REFLEXION_USER_PROMPT_zh
)
from termcolor import colored
from multiagents.utils.utils import AgentAction
from multiagents.memory import BaseMemory
import numpy as np
import re
import json
from pydantic import Field
import datetime
import time
from tqdm import tqdm
from multiagents.utils.interact import add_display_message

def node_to_chain(node):
    chain = {
        "prompt": "",
        "query": "",
        "chains": [],
        "answer": "",
    }

    step = {}
    for i, message in enumerate(node.messages):
        if message["role"] == "system":
            chain["prompt"] = message["content"]
        elif message["role"] == "user":
            chain["query"] += message["content"]
        elif message["role"] == "assistant":
            if "function_call" in message:
                function_call = message["function_call"]
                if function_call["name"] == "Finish":
                    chain["answer"] = function_call["arguments"]
                else:
                    step["action"] = function_call["name"]
                    step["action_input"] = function_call["arguments"]
            else:
                step["thought"] = message["content"]
        elif message["role"] == "function":
            step["observation"] = message["content"]
            chain["chains"].append(step)
            step = {}

    return chain

class UCT_vote_function(base_search_method):
    class Config:
        arbitrary_types_allowed = True
    memory: BaseMemory = Field

    def __init__(self, diag_id, enable_prometheus, start_time, end_time,
                 agent_name, role_description, prompt_template, llm, env,
                 output_parser, alert_dict, alert_str, agent, language='en'):
        super(UCT_vote_function, self).__init__()
        '''
        偏序驱动的信心上限树算法:
        1.由value决定回传什么节点
        2.回传反思，同时做偏序 
        '''
        self.diag_id = diag_id
        self.enable_prometheus = enable_prometheus
        self.name = agent_name
        self.role_description = role_description
        self.prompt_template = prompt_template
        self.llm = llm
        self.env = env
        self.output_parser = output_parser
        # self.simulations = []
        self.start_time = start_time
        self.end_time = end_time
        self.alert_dict = alert_dict
        self.alert_str = alert_str

        self.restart(agent)
        self.language = language
    
    # def to_json(self):
    
    #     js_obj = {
    #         "win": self.status == 1,
    #         "simulation_count": self.now_simulation_count,
    #         "simulations": self.simulations,
    #         "tree":self.tree.to_json_recursive()
    #     }
    
    #     js_obj["answer_generation"] = {
    #         "valid_data": False,
    #         "final_answer": "",
    #         "chain": [],
    #     }

    #     if len(self.terminal_node) > 0:
    #         final_terminal_node = sorted(self.terminal_node, key=lambda x: sum(x.values)/(len(x.values)+1e-8), reverse=True)[0]
    #         js_obj["answer_generation"]["valid_data"] = True
    #         js_obj["answer_generation"]["final_answer"] = final_terminal_node.description
    #         js_obj["answer_generation"]["chain"] = final_terminal_node.get_chain_result_from_this_node()

    #     return js_obj

    def restart(self, agent): # 理论上用不到，清空所有的tree
        self.tree = my_tree()
        self.tree.root.node_type = "Action Input"
        self.tree.root.env = deepcopy(self.env)

        # prefix = DEFAULT_POLICY_SYSTEM_PROMPT
        # prefix = prefix.replace("{task_description}",self.env.task_description)
        # self.tree.root.messages.append({
        #     "role":"system",
        #     "content": prefix,
        # })

        # prefix = DEFAULT_POLICY_USER_PROMPT
        # prefix = prefix.replace("{input_description}",self.env.input_description)
        
        tool_observation = [self.tree.root.env.tool_memory.to_string()]
        #prompt = agent._fill_prompt_template(self.tree.root.env.tool, self.tree.root.env.task_description, tool_observation, self.tree.root.messages)
        prompt = agent._fill_prompt_template(self.tree.root.env.task_description, tool_observation)
        
        self.role_description = agent.role_description

        now_time = datetime.datetime.now()
        now_time = now_time.strftime("%H:%M:%S")

        self.tree.root.messages.append({
            "role":"user",
            "content": prompt,
            "time": str(now_time)
        })

        self.status = 0
        self.now_simulation_count = 0
        # self.simulations = []
        self.terminal_node = []
        self.total_vote = 0
        self.good_vote = 0
        
        pass

    def start(self,
              simulation_count, # chain的个数
              epsilon_new_node, # 开新节点的value
              choice_count, # vote随机次数
              vote_candidates, # vote叶节点个数
              vote_count, # 投票次数
              single_chain_max_step):
        
        '''
        epsilon_new_node：以多大概率扩展新节点
        vote_candidates：每次投票时选择多少candidate
        vote_count：每次投票时投多少票
        '''

        top_abnormal_metric_values = []

        while self.now_simulation_count < simulation_count:
            
            '''
            执行一次模拟，从根节点出发
            '''
            this_simulation = []
            now_node = self.tree.root
            while len(now_node.children) > 0:
                '''
                有儿子节点，在每个地方都决定是去扩展新节点还是选择已有节点
                '''
                # decision = self.make_decision(now_node)
                decision = self.make_decision_by_value(now_node, epsilon_new_node)
                
                if decision == -1:
                    print(colored("decide to make new node!","green"))
                    break
                # print(colored(f"decide to go down child {decision}","green"))

                now_node = now_node.children[decision]
                this_simulation.append({"choice":decision,"new_generated":False,"score":now_node.env.get_score()})
                
                while now_node.node_type != "Action Input" and len(now_node.children) > 0:
                    now_node = now_node.children[0]
                    this_simulation.append({"choice":0,"new_generated":False,"score":now_node.env.get_score()})
                
            if now_node.is_terminal:
                # print(colored(f"randomly go down to terminal nodes","green"))
                pass
            else:
                begin_default_policy_node = now_node

                end_node, top_abnormal_metric_values = self.default_policy(now_node,this_simulation,single_chain_max_step)
                # self.pruned self.env.check_success() 

                self.now_simulation_count += 1
                # self.simulations.append(this_simulation)

                if end_node.pruned is not True: # the node is not pruned
                    self.terminal_node.append(end_node)

                if end_node.env.status == 1:
                    self.status = 1
                    # self.llm.display_conversation()
                    # return 1

                '''
                生成反思，并且回传
                '''
                self.make_reflection(begin_default_policy_node,end_node)

            '''
            针对candidate投票
            '''
            self.vote(choice_count,vote_candidates,vote_count)

        if self.terminal_node == []:
            # print(colored("No terminal node found!","red"))

            return None, top_abnormal_metric_values
            
        else:
            final_terminal_node = sorted(self.terminal_node, key=lambda x: sum(x.values), reverse=True)[0]
            
            if final_terminal_node.pruned is True:
                # print(colored("Final answer is pruned!","red"))
                return None, top_abnormal_metric_values

            return final_terminal_node, top_abnormal_metric_values

    def vote(self,choice_count,vote_candidates,vote_count):
        '''
        进行投票
        每次选vote_candidates个样本
        投出vote_count票
        '''
        # if len(self.terminal_node) < vote_candidates:
        #     return

        for choice_count in range(choice_count):
            ordered = list(range(len(self.terminal_node)))
            np.random.shuffle(ordered)

            choices = ordered[:vote_candidates] #随机选择，然后从小到大排序
            choices.sort()
            messages = []
            prompt = VOTE_BEST_SYSTEM_PROMPT_zh if self.language == 'zh' else VOTE_BEST_SYSTEM_PROMPT
            prompt = prompt.replace("{task_description}",self.env.task_description)

            now_time = datetime.datetime.now()
            now_time = now_time.strftime("%H:%M:%S")

            messages.append({
                "role": "system",
                "content": prompt,
                "time": str(now_time)                
            })

            prompt = VOTE_BEST_USER_PROMPT_zh if self.language == 'zh' else VOTE_BEST_USER_PROMPT
            prompt = prompt.replace("{input_description}",self.env.input_description)

            candidates_description = ""
            for k, child_id in enumerate(choices):
                trice = self.tree.get_former_trice(self.tree.root,self.terminal_node[child_id],valid_types=["Action","Action Input","Observation"])
                candidates_description += f"<candidate_{k}>\n{trice}"
                # reflection = f"Reflection: {self.terminal_node[child_id].generated_reflection.strip()}\n"
                # candidates_description += reflection
                candidates_description += "*"*30 + "\n"
            prompt = prompt.replace("{candidate_description}",candidates_description)

            now_time = datetime.datetime.now()
            now_time = now_time.strftime("%H:%M:%S")

            messages.append({
                "role": "user",
                "content": prompt,
                "time": str(now_time)                
            })

            real_score = [-1]*len(choices)
            max_score = self.tree.root.env.get_score()
            max_position = -1
            for k, child_id in enumerate(choices):
                now_node = self.terminal_node[child_id]
                while now_node != None:
                    real_score[k] = max(now_node.env.get_score(),real_score[k])
                    now_node = now_node.father
                if real_score[k] > max_score:
                    max_position = k
                    max_score = real_score[k]

            votes = [0]*len(choices)
            vaild_votes = 0
            for i in range(vote_count):
                '''
                多次投票
                '''
                self.llm.change_messages("", messages)

                print(colored(f"- Voting ...","grey"))
                #with tqdm(total=1, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
                message = self.llm.parse(role=self.name, task='mcts_vote')
                #    pbar.update(1)

                vote = message["content"]
                # print(vote)
                # best_candiate_line = vote.split("\n")[-1]
                # print(best_candiate_line)
                re_pattern = r"[\"<]?candidate[ \_](\d+)[\">]?"
                # re_result = re.findall(re_pattern,best_candiate_line.lower())
                re_result = re.findall(re_pattern, vote)[-1:]  # 直接把最后的拿到
                if re_result != []:
                    if not len(re_result) == 1:
                        # print(best_candiate_line)
                        # exit()
                        return
                    vote_to = int(re_result[0])
                    self.total_vote += 1
                    if vote_to >= 0 and vote_to < len(votes):
                        votes[vote_to] += 1
                        self.good_vote += (vote_to == max_position)
                        vaild_votes += 1
                        # print(colored(f"valid vote to {choices[vote_to]}","yellow"))
                    else:
                        self.good_vote += (-1 == max_position)
                        # print(colored(f"vote to Invalid candidates, both candidate punished","yellow"))
                else:
                    self.good_vote += (-1 == max_position)
                    # print(colored(f"vote to Nothing, both candidate punished","yellow"))
                    for k,child_id in enumerate(choices):
                        now_node = self.terminal_node[child_id]
                        while now_node != None:
                            now_node.pruned = True
                            now_node = now_node.father

            if vaild_votes > 0:
                for k,child_id in enumerate(choices):
                    vote_count_this_turn = votes[k]
                    value = (vote_count_this_turn / vaild_votes  - 1 / vote_candidates) / np.sqrt(vaild_votes)
                    # print(value)
                    now_node = self.terminal_node[child_id]
                    while now_node != None:
                        now_node.values.append(value)
                        now_node.vote_counts.append(vote_count_this_turn)
                        now_node = now_node.father  
        
        if self.total_vote > 0:
            # print(f"ratio={self.good_vote}/{self.total_vote}={self.good_vote/self.total_vote}")
            pass

    def make_decision_by_value(self, now_node, epsilon_new_node):
        '''
        epsilon_new_node概率选择新节点
        否则选择当前value最高的
        '''
        # assert len(now_node.children) > 0
        # if np.random.random() < epsilon_new_node / len(now_node.children):
        #     return -1


        weights = [child.compute_weight() for child in now_node.children] + [epsilon_new_node]
        def my_softmax(x):
            exp_x = np.exp(x)
            return exp_x/np.sum(exp_x)
        
        weights = my_softmax(np.array(weights))
        # print(weights)
        result = np.random.multinomial(1,weights)
        for k, v in enumerate(result[:-1]):
            if v == 1:
                return k
        return -1

    def make_reflection(self,start_node,end_node):
        '''
        从start_node开始生成了新儿子，一路走到了end_node,对于过去的自己start_node有没有什么想说的
        '''
        if self.language == "zh":
            make_reflection_prompt = MAKE_REFLEXION_USER_PROMPT_zh
        else:
            make_reflection_prompt = MAKE_REFLEXION_USER_PROMPT

        now_time = datetime.datetime.now()
        now_time = now_time.strftime("%H:%M:%S")

        new_message = {
            "role": "user",
            "content": make_reflection_prompt,
            "time": str(now_time)
        }

        message_list = end_node.messages.copy()
        # message_list = [end_node.messages[0], end_node.messages[-1]]
        message_list.append(new_message)

        self.llm.change_messages(self.role_description, message_list)

        # with tqdm(total=1, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
        new_message = self.llm.parse(role=self.name, task='mcts_reflect')
        #    pbar.update(1)

        reflection = new_message['content']
        if self.language == "zh":
            reflect_message = f"反思内容：{reflection}"
        else:
            reflect_message = reflection
            if not reflect_message.lower().startswith('reflection:'):
                reflect_message = f"Reflection: {reflect_message}"
        print(colored(reflect_message,"green"))

        add_display_message('expertDiagnosis', self.name, reflect_message, time.strftime("%H:%M:%S", time.localtime()))

        now_time = datetime.datetime.now()
        now_time = now_time.strftime("%H:%M:%S")

        reflect_message = {
            "role": "assistant",
            "content": reflection,
            "time": str(now_time)
        }
        start_node.reflection.append(reflection)
        start_node.messages.append(reflect_message)
        if start_node != self.tree.root:
            self.tree.root.reflection.append(reflection)
            self.tree.root.messages.append(reflect_message)

        return reflection

    def default_policy(self,now_node,this_simulation,single_chain_max_step):
        assert not now_node.is_terminal
        assert now_node.messages != []
        # self.pruned self.env.check_success()
        first_time = True
        top_abnormal_metric_values = []

        while now_node.get_depth() < single_chain_max_step and not now_node.is_terminal and not now_node.env.status:
            if first_time:
                '''
                第一次要拼接diversity prompt
                '''
                if len(now_node.children) > 0:
                    diverse_prompt = DIVERSITY_PROMPT
                    former_candidates_des = ""
                    js_list = []
                    for k, child in enumerate(now_node.children):
                        temp_node = child
                        while not temp_node.is_terminal and temp_node.node_type != "Action Input" and len(temp_node.children) > 0:
                            temp_node = temp_node.children[0]
                        # child_des = self.get_former_trice(child,temp_node)
                        # former_candidates_des = former_candidates_des + f"<candidate_{k+1}>\n{child_des}"
                        if temp_node.node_type == "Action Input":
                            # if temp_node.description is str:
                            if isinstance(temp_node.description, str):
                                try:
                                    temp_node.description = json.loads(temp_node.description)
                                    obj_dict = {
                                        "name": temp_node.father.description,
                                        "arguments": temp_node.description,
                                        "function_output": temp_node.observation,
                                        "mento-carlo-action-value": temp_node.compute_weight(),
                                    }
                                    js_list.append(obj_dict)
                                except:
                                    pass
                    
                    if len(js_list) > 0:
                        former_candidates_des = former_candidates_des + f"{json.dumps(js_list,indent=2)}\n"
                        if now_node.observation != "":
                            former_candidates_des = former_candidates_des + f"again, your former observation: {now_node.observation}\n"
                        diverse_prompt = diverse_prompt.replace("{previous_candidate}",former_candidates_des)
                        # record current time in hour-minutes-seconds

                        now_time = datetime.datetime.now()
                        now_time = now_time.strftime("%H:%M:%S")
                        
                        now_node.messages.append({"role":"user", "content":diverse_prompt, "time": str(now_time)})

                        self.llm.change_messages(self.role_description, now_node.messages)
                        # self.llm.display_conversation()
            
            self.llm.change_messages(self.role_description, now_node.messages)
            # self.llm.display_conversation()

            # print(colored(f"- Analyzing with tools ...","grey"))
            #with tqdm(total=1, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
            new_message = self.llm.parse(role=self.name, task="mcts_action")
            #    pbar.update(1)

            # print(f"New message:\t{new_message['content']}")
            assert new_message["role"] == "assistant"
            if new_message not in now_node.messages:
                now_node.messages.append(new_message)
            
            if first_time:
                first_time = False
                '''
                如果拼接了diversity prompt，要去掉
                '''
                try:
                    if "This is not the first time you try this task" in now_node.messages[-1]["content"]:
                        now_node.messages = now_node.messages[:-1]
                except BaseException as e:
                    # print(e)
                    pass
            
            if "content" in new_message.keys() and new_message["content"] != None:
                
                for _ in range(3):
                    parsed_response = self.output_parser.parse(new_message)
                    
                    if parsed_response != None:
                        break
                    
                    print("Fail to parse the response, retrying ...")
                    time.sleep(0.5)

                    # print(colored(f"- Analyzing with tools ...","grey"))
                    # with tqdm(total=1, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
                    new_message = self.llm.parse(role=self.name, task="mcts_action")
                    #    pbar.update(1)
                
                # action --> temp_node
                temp_node = tree_node()
                temp_node.node_type = "Thought"
                temp_node.description = new_message["content"]
                
                child_env = deepcopy(now_node.env)
                
                temp_node.env = child_env
                temp_node.is_terminal = False
                temp_node.messages = now_node.messages.copy()
                # temp_node.messages.append(new_message)
                temp_node.father = now_node
                now_node.children.append(temp_node)
                # temp_node.print()
                now_node = temp_node
                this_simulation.append({"choice":0,"new_generated":True,"score":now_node.env.get_score()})

                if isinstance(parsed_response, AgentAction):
                    # If the response is an action, call the tool
                    # and append the observation to tool_observation
                    parameters = []
                    knowledge_list = []
                    if "whether_is_abnormal_metric" in parsed_response.tool:
                        
                        metric_name = self.name.lower()
                        metric_name = metric_name.replace("expert","")
                        metric_name = metric_name.strip()

                        if "cpu" not in metric_name and "memory" not in metric_name:
                            # random select metric_name as cpu or memory
                            metric_name = np.random.choice(["cpu","memory"])
                            
                        metric_name = metric_name + "_" + "usage"

                        parameters = {"start_time": self.start_time,      
                                    "end_time": self.end_time,
                                    "metric_name": metric_name, 
                                    "diag_id": str(self.diag_id),
                                    "enable_prometheus": self.enable_prometheus}
                        
                    elif "match_diagnose_knowledge" in parsed_response.tool and self.alert_dict != None:
                        # node_load1{instance="$instance"}
                        for alert in self.alert_dict:
                            metric_name = alert["alert_desc"].split('[')[0]
                            host = alert["alert_exporter"]
                            alert_metric = f"{metric_name}{{instance=\"{host}\"}}"

                            metric_name = self.name.lower()
                            metric_name = metric_name.replace("expert","") + "_" + "usage"

                            parameters.append({"start_time": self.start_time, "end_time": self.end_time, "metric_name": self.name, "alert_metric": alert_metric, "diag_id": str(self.diag_id), "enable_prometheus": self.enable_prometheus})
                    else:
                        
                        try:
                            parameters = json.loads(parsed_response.tool_input)
                        except:
                            parameters = None


                    tmp_start_time = time.time()  # capture starting time
                    observation = None
                    if "obtain_start_and_end_time_of_anomaly" in parsed_response.tool and self.alert_dict != [] and self.alert_dict != None:
                        observation = f"The start time is {self.start_time}, and the end time is {self.end_time}."
                    else:
                        tool_calling_message = f"- 使用工具API ...\n  Name: {parsed_response.tool}\n  Parameters: {parameters}"
                        add_display_message('expertDiagnosis', self.name, tool_calling_message, time.strftime("%H:%M:%S", time.localtime()))
                        print(tool_calling_message)
                        if isinstance(parameters, list):
                            observation = []
                            for parameter in parameters:
                                result = temp_node.env.tool.call_function(parsed_response.tool, **parameter)
                                if isinstance(result, (tuple, list)):
                                    observation.append(result[0])
                                    top_abnormal_metric_values = result[1]
                                    if "match_diagnose_knowledge" in parsed_response.tool:
                                        knowledge_list.extend(result[2])
                                else:
                                    observation.append(result)                               
                        elif parameters != None:
                            # observation = temp_node.env.tool.call_function(parsed_response.tool, **parameters)
                            result = temp_node.env.tool.call_function(parsed_response.tool, **parameters)

                            if isinstance(result, (tuple, list)):
                                observation = result[0]
                                top_abnormal_metric_values = result[1]
                                if "match_diagnose_knowledge" in parsed_response.tool:
                                    knowledge_list = result[2]
                            else:
                                observation = result

                    # tmp_end_time = time.time()  # capture ending time
                    # tmp_time_diff = tmp_end_time - tmp_start_time
                    # # tmp_time_diff reserves .2f
                    # tmp_time_diff = round(tmp_time_diff, 2)

                    # # write into the log file (append to the last line)
                    # with open("tool_response_time_tmp.txt", "a") as f:
                    #     f.write(f"{tmp_time_diff}\n")


                    # tool_observation.append(
                    #     parsed_response.log.strip()
                    #     + f"\nObservation: {str(observation).strip()}"
                    # )
                    if observation == None:
                        now_node.pruned = True
                        # now_node.messages.append(new_message)
                        return now_node, top_abnormal_metric_values

                    # new the Action node
                    temp_node = tree_node()
                    temp_node.node_type = "Action"
                    temp_node.description = parsed_response.tool # check
                    child_env = deepcopy(now_node.env)
                    
                    temp_node.env = child_env
                    temp_node.is_terminal = False
                    temp_node.messages = now_node.messages.copy()
                    temp_node.father = now_node
                    now_node.children.append(temp_node) # the action node is child of the thought node

                    # temp_node.print()
                    now_node = temp_node
                    this_simulation.append({"choice":0,"new_generated":True,"score":now_node.env.get_score()})

                    # new the Action Input and Observation node
                    function_input = parameters
                    temp_node = tree_node()
                    temp_node.node_type = "Action Input"
                    temp_node.description = function_input
                    child_env = deepcopy(now_node.env)
                    
                    # observation, status = child_env.step(action_name=now_node.description, action_input=function_input)
                    temp_node.observation = observation
                    temp_node.knowledge_list = knowledge_list
                    temp_node.env = child_env
                    temp_node.is_terminal = False
                    temp_node.messages = now_node.messages.copy()

                    now_time = datetime.datetime.now()
                    now_time = now_time.strftime("%H:%M:%S")
                    temp_message = {
                        "role": "assistant",
                        "content": f'Observation: {observation}',
                        "time": str(now_time)
                    }
                    if temp_message not in temp_node.messages:
                        temp_node.messages.append(temp_message)

                    temp_node.father = now_node
                    now_node.children.append(temp_node)
                    now_node = temp_node
                    this_simulation.append({"choice":0,"new_generated":True,"score":now_node.env.get_score()})
                else:
                    pass

            # if now_node.node_type == "Action Input":

            #     now_time = datetime.datetime.now()
            #     now_time = now_time.strftime("%H:%M:%S")

            #     now_node.messages.append({
            #         "role":"function",
            #         "name": parsed_response.tool,
            #         "content": str(now_node.observation),
            #         "time": str(now_time)
            #     })
            # else:
            #     now_node.messages.append(new_message)
            
            now_node.is_terminal = now_node.env.check_success(now_node.messages[-1])

            # evaluate whether optimization solutions are proposed in the now_node (terminal status)
        
        return now_node, top_abnormal_metric_values