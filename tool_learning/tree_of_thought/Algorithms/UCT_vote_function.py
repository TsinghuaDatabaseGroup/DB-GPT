import sys
sys.path.append('..')
sys.path.append('../..')

from Tree.Tree import my_tree, tree_node
from copy import deepcopy
from Algorithms.base_search import base_search_method
from prompt_templates.Tree_search_prompts import  MAKE_REFLECTION_RPOMPT,DIVERSITY_PROMPT,VOTE_BEST_SYSTEM_PROMPT,VOTE_BEST_USER_PROMPT,DEFAULT_POLICY_SYSTEM_PROMPT, DEFAULT_POLICY_USER_PROMPT
from prompt_templates.Reflexion_prompts import MAKE_REFLEXION_USER_PROMPT
from termcolor import colored
import numpy as np
import re
import json

from pprint import pprint
import pdb

class UCT_vote_function(base_search_method):
    def __init__(self,llm,io_func):
        super(UCT_vote_function, self).__init__()
        '''
        偏序驱动的信心上限树算法:
        1.适用于0613新版模型接口
        2.由value决定回传什么节点
        2.回传反思，同时做偏序 
        '''

        self.llm = llm
        self.io_func = io_func
        self.simulations = []
        self.restart()

    def to_json(self):
        js_obj = {
            "win": self.status == 1,
            "simulation_count": self.now_simulation_count,
            "simulations": self.simulations,
            "tree":self.tree.to_json_recursive()
        }

        js_obj["answer_generation"] = {
            "valid_data": False,
            "final_answer": "",
            "chain": [],
        }
        if len(self.terminal_node) > 0:
            final_terminal_node = sorted(self.terminal_node, key=lambda x: sum(x.values)/(len(x.values)+1e-8), reverse=True)[0]
            js_obj["answer_generation"]["valid_data"] = True
            js_obj["answer_generation"]["final_answer"] = final_terminal_node.description
            js_obj["answer_generation"]["chain"] = final_terminal_node.get_chain_result_from_this_node()
        return js_obj

    def restart(self): # 理论上用不到，清空所有的tree
        self.tree = my_tree()
        self.tree.root.node_type = "Action Input"
        self.tree.root.io_state = deepcopy(self.io_func)

        prefix = DEFAULT_POLICY_SYSTEM_PROMPT
        prefix = prefix.replace("{task_description}",self.io_func.task_description)
        self.tree.root.messages.append({
            "role":"system",
            "content": prefix,
        })

        prefix = DEFAULT_POLICY_USER_PROMPT
        prefix = prefix.replace("{input_description}",self.io_func.input_description)
        self.tree.root.messages.append({
            "role":"user",
            "content": prefix,
        })


        self.status = 0
        self.now_simulation_count = 0
        self.simulations = []
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
        epsilon_new_node:以多大概率扩展新节点
        vote_candidates：每次投票时选择多少candidate
        vote_count：每次投票时投多少票
        '''
        while self.now_simulation_count < simulation_count:
            print(colored("new trail start!","yellow"))
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
                print(colored(f"decide to go down child {decision}","green"))

                now_node = now_node.children[decision]
                this_simulation.append({"choice":decision,"new_generated":False,"score":now_node.io_state.get_score()})
                while now_node.node_type != "Action Input" and len(now_node.children) > 0:
                    now_node = now_node.children[0]
                    this_simulation.append({"choice":0,"new_generated":False,"score":now_node.io_state.get_score()})

            if now_node.is_terminal:
                print(colored(f"randomly go down to terminal nodes","green"))
            else:
                begin_default_policy_node = now_node
                end_node = self.default_policy(now_node,this_simulation,single_chain_max_step)

                self.now_simulation_count += 1
                self.simulations.append(this_simulation)
                if end_node.pruned is not True:
                    self.terminal_node.append(end_node)

                if end_node.io_state.check_success() == 1:
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

        return 0

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
            prompt = VOTE_BEST_SYSTEM_PROMPT
            prompt = prompt.replace("{task_description}",self.io_func.task_description)
            messages.append({
                "role":"system",
                "content": prompt,
            })

            prompt = VOTE_BEST_USER_PROMPT
            prompt = prompt.replace("{input_description}",self.io_func.input_description)


            candidates_description = ""
            for k, child_id in enumerate(choices):
                trice = self.tree.get_former_trice(self.tree.root,self.terminal_node[child_id],valid_types=["Action","Action Input","Observation"])
                candidates_description += f"<candidate_{k}>\n{trice}"
                # reflection = f"Reflection: {self.terminal_node[child_id].generated_reflection.strip()}\n"
                # candidates_description += reflection
                candidates_description += "*"*30 + "\n"
            prompt = prompt.replace("{candidate_description}",candidates_description)

            messages.append({
                "role":"user",
                "content": prompt,
            })

            # print(prompt)

            real_score = [-1]*len(choices)
            max_score = self.tree.root.io_state.get_score()
            max_position = -1
            for k, child_id in enumerate(choices):
                now_node = self.terminal_node[child_id]
                while now_node != None:
                    real_score[k] = max(now_node.io_state.get_score(),real_score[k])
                    now_node = now_node.father
                if real_score[k] > max_score:
                    max_position = k
                    max_score = real_score[k]
            # print(real_score)


            votes = [0]*len(choices)
            vaild_votes = 0
            for i in range(vote_count):
                '''
                多次投票
                '''
                self.llm.change_messages(messages)
                message = self.llm.parse(self.io_func.functions,function_call="none")
                vote = message["content"]
                # print(vote)
                best_candiate_line = vote.split("\n")[-1]
                print(best_candiate_line)
                re_pattern = r"\"?candidate[ \_](\d+)\"?"
                re_result = re.findall(re_pattern,best_candiate_line.lower())
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
                        print(colored(f"valid vote to {choices[vote_to]}","yellow"))
                    else:
                        self.good_vote += (-1 == max_position)
                        print(colored(f"vote to Invalid candidates, both candidate punished","yellow"))
                else:
                    self.good_vote += (-1 == max_position)
                    print(colored(f"vote to Nothing, both candidate punished","yellow"))
            if vaild_votes > 0:
                for k,child_id in enumerate(choices):
                    vote_count_this_turn = votes[k]
                    value = (vote_count_this_turn / vaild_votes  - 1 / vote_candidates) / np.sqrt(vaild_votes)
                    print(value)
                    now_node = self.terminal_node[child_id]
                    while now_node != None:
                        now_node.values.append(value)
                        now_node.vote_counts.append(vote_count_this_turn)
                        now_node = now_node.father  
        
        if self.total_vote > 0:
            print(f"ratio={self.good_vote}/{self.total_vote}={self.good_vote/self.total_vote}")

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
        print(weights)
        result = np.random.multinomial(1,weights)
        for k, v in enumerate(result[:-1]):
            if v == 1:
                return k
        return -1

    def make_reflection(self,start_node,end_node):
        '''
        从start_node开始生成了新儿子，一路走到了end_node,对于过去的自己start_node有没有什么想说的
        '''
        make_reflection_prompt = MAKE_REFLEXION_USER_PROMPT

        new_message = {
            "role": "user",
            "content":make_reflection_prompt,
        }

        message_list = end_node.messages.copy()
        message_list.append(new_message)

        self.llm.change_messages(message_list)
        new_message = self.llm.parse(self.io_func.functions,function_call="none")
        reflection = new_message['content']
        print(colored(f"Reflexion: {reflection}","green"))

        start_node.reflection.append(reflection)
        if start_node != self.tree.root:
            self.tree.root.reflection.append(reflection)


        return reflection

    def default_policy(self,now_node,this_simulation,single_chain_max_step):
        '''
        适用于0613模式
        '''
        assert not now_node.is_terminal
        assert now_node.messages != []

        first_time = True
        while now_node.get_depth() < single_chain_max_step and not now_node.is_terminal:

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
                            obj_dict = {
                                "name": temp_node.father.description,
                                "arguments": json.loads(temp_node.description),
                                "function_output": temp_node.observation,
                                "mento-carlo-action-value": temp_node.compute_weight(),
                            }
                            js_list.append(obj_dict)
                    
                    if len(js_list) > 0:
                        former_candidates_des = former_candidates_des + f"{json.dumps(js_list,indent=2)}\n"
                        if now_node.observation != "":
                            former_candidates_des = former_candidates_des + f"again, your former observation: {now_node.observation}\n"
                        diverse_prompt = diverse_prompt.replace("{previous_candidate}",former_candidates_des)
                        now_node.messages.append({"role":"user", "content":diverse_prompt})

                        self.llm.change_messages(now_node.messages)
                        self.llm.display_conversation()
            
            self.llm.change_messages(now_node.messages)
            # self.llm.display_conversation()
            new_message = self.llm.parse(self.io_func.functions)
            print(f"New message:\t{new_message}")
            assert new_message["role"] == "assistant"

            if first_time:
                first_time = False
                '''
                如果拼接了diversity prompt，要去掉
                '''
                try:
                    if "This is not the first time you try this task" in now_node.messages[-1]["content"]:
                        now_node.messages = now_node.messages[:-1]
                except BaseException as e:
                    print(e)
                    pdb.set_trace()
                    pass

            if "content" in new_message.keys() and new_message["content"] != None:
                # print(new_message["content"])
                temp_node = tree_node()
                temp_node.node_type = "Thought"
                temp_node.description = new_message["content"]
                child_io_state = deepcopy(now_node.io_state)
                
                temp_node.io_state = child_io_state
                temp_node.is_terminal = child_io_state.check_success() != 0 
                temp_node.messages = now_node.messages.copy()
                temp_node.father = now_node
                now_node.children.append(temp_node)
                temp_node.print()
                now_node = temp_node
                this_simulation.append({"choice":0,"new_generated":True,"score":now_node.io_state.get_score()})

            if "function_call" in new_message.keys():
                function_name = new_message["function_call"]["name"]
                # assert function_name in now_node.io_state.tool_names

                # new the Action node
                temp_node = tree_node()
                temp_node.node_type = "Action"
                temp_node.description = function_name
                child_io_state = deepcopy(now_node.io_state)
                
                temp_node.io_state = child_io_state
                temp_node.is_terminal = child_io_state.check_success() != 0 
                temp_node.messages = now_node.messages.copy()
                temp_node.father = now_node
                now_node.children.append(temp_node)

                temp_node.print()
                now_node = temp_node
                this_simulation.append({"choice":0,"new_generated":True,"score":now_node.io_state.get_score()})


                # new the Action Input and Observation node
                function_input = new_message["function_call"]["arguments"]
                temp_node = tree_node()
                temp_node.node_type = "Action Input"
                temp_node.description = function_input
                child_io_state = deepcopy(now_node.io_state)

                observation, status = child_io_state.step(action_name=now_node.description, action_input=function_input)
                temp_node.observation = observation
                temp_node.io_state = child_io_state
                temp_node.is_terminal = child_io_state.check_success() != 0 
                temp_node.messages = now_node.messages.copy()
                temp_node.father = now_node
                now_node.children.append(temp_node)
                temp_node.print()
                now_node = temp_node
                this_simulation.append({"choice":0,"new_generated":True,"score":now_node.io_state.get_score()})

                if status != 0: # 错误，需要剪枝
                    # 0代表正常返回
                    # 1代表没有对应api名字
                    # 2代表输入有错误
                    # 3代表生成结束，出现final answer
                    # 4代表模型自己决定剪枝
                    if status == 4:
                        now_node.pruned = True
                    now_node.messages.append(new_message)
                    return now_node
            
                    

            now_node.messages.append(new_message)
            if now_node.node_type == "Action Input":
                now_node.messages.append({
                    "role":"function",
                    "name": new_message["function_call"]["name"],
                    "content": now_node.observation,
                })

        now_node.pruned = True #链条过长被剪枝了
        return now_node

