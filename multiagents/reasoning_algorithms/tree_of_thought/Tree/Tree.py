from termcolor import colored
import numpy as np


class my_tree:
    def __init__(self):
        self.root = tree_node()
        self.now_deal_node = self.root



    def get_former_trice(self,start_node,target_node,valid_types=["Thought","Action","Action Input","Observation"]):
        '''
        获取从start_node节点到target_node节点的所有操作，包含target_node自己和start_node
        '''
        node = target_node
        now_str = ""
        while node != self.root and node != start_node.father:
            node_info = ""
            if node.node_type in valid_types:
                node_info = node_info + f"{node.node_type}: {node.description}\n"
            if node.observation != "" and "Observation" in valid_types:
                node_info = node_info + f"Observation: {node.observation}\n"
            now_str = node_info + now_str

            node = node.father
        
        return now_str

    def add_child(self,new_node):
        '''
        对现在处理的节点添加子节点
        '''
        new_node.father = self.now_deal_node
        self.now_deal_node.children.append(new_node)
        self.now_deal_node = new_node

    def backup(self):
        self.now_deal_node = self.now_deal_node.father


    def to_json_recursive(self):
        tree_structure =  self.root.to_json_recursive()
        js_obj = {
            "size": self.root.get_size(),
            "max_length":self.root.get_max_depth(),
            "tree": tree_structure,
        }
        return js_obj

    def chain_tree_to_json(self):
        json_obj = []
        now_node = self.root
        while True:

            
            json_obj.append(now_node.to_json())

            
            if now_node.children != []:
                assert len(now_node.children) == 1
                now_node = now_node.children[0]
            else:
                break
        return json_obj
    
    def chain_tree_to_str(self):
        now_prefix = ""
        json_obj = self.chain_tree_to_json()
        for k,ins in enumerate(json_obj):
            # print(ins)
            if k != 0:
                now_prefix += f"\n{ins['node_type']}: "
            now_prefix += f"{ins['description']}"
            if 'observation' in ins.keys():
                now_prefix += f"\nObservation: {ins['description']}"
        return now_prefix


    @classmethod
    def from_chain_tree_json(self, js_obj):
        tree = my_tree()
        for k, ins in enumerate(js_obj):
            temp_node = tree_node.from_json(ins)
            if k == 0:
                tree.root = temp_node
                tree.now_deal_node = tree.root
            else:
                tree.add_child(temp_node)

        return tree

class tree_node:

    def __init__(self):
        '''
        ss
        '''
        self.is_terminal = False

        self.node_type = None
        self.description = ""
        self.observation = ""
        self.knowledge_list = []
        self.children = []

        self.father = None


        self.env = None
        self.score = None

        self.reflection = []
        self.generated_reflection = ""

        self.pruned = False #节点是否被剪枝，用于BFS算法
        self.expand_num = 0 #用于DFS


        '''
        用于UCT算法
        '''
        self.values = [] #每次投票获得的value
        self.vote_counts = [] #每次投票的得票数


        '''
        用于0613接口
        '''
        self.messages = []

    def compute_weight(self):
        '''
        用于uct算法，计算选择时每个儿子的节点权重
        '''
        if len(self.values) == 0: #还没有投过票
            return 0.0
        else:
            return np.mean(np.array(self.values))

    def get_max_depth(self):
        '''
        包含自己在内的子树的最大深度
        '''
        max_depth = 0
        for child in self.children:
            max_depth = max(max_depth,child.get_max_depth())
        return max_depth + 1

    def get_depth(self):
        if self.father == None:
            return 0
        return self.father.get_depth() + 1

    def get_size(self):
        '''
        子树，包含自己
        '''
        size = 1
        for child in self.children:
            size += child.get_size()
        return size
    
    def prune(self):
        '''
        将子树剪枝掉
        '''
        self.pruned = True
        for child in self.children:
            child.prune()

    def print(self):
        color_converter = {"Thought":"red", "Action": "blue", "Action Input": "cyan","Final Answer": "green","Reflection":"blue"}
        print(colored(f"{self.node_type}: {self.description}",color = color_converter[self.node_type]))
        if self.observation != "":
            print(colored(f"Observation: {self.observation}",color="yellow"))


    @classmethod
    def from_json(self,json_obj):
        # print(json_obj)
        node = tree_node()
        node.is_terminal = json_obj["is_terminal"]
        node.node_type = json_obj["node_type"]
        node.description = json_obj["description"]
        if "observation" in json_obj.keys():
            node.observation = json_obj["observation"]
        return node
    
    def have_brother(self):
        if self.father == None:
            return False
        return len(self.father.children) > 1

    def to_json_recursive(self):
        js_obj = self.to_json()
        js_obj["children"] = []
        for child in self.children:
            js_obj["children"].append(child.to_json_recursive())
        return js_obj

    def get_chain_result_from_this_node(self):
        '''
        返回链式结果，从这个节点开始向上到根节点
        '''
        now_node = self
        result = []
        while now_node != None:
            result = [now_node.to_json()] + result
            now_node = now_node.father
        return result

    def to_json(self):
        
        json_obj = {}
        json_obj["is_terminal"] = False
        json_obj["pruned"] = self.pruned
        json_obj["depth"] = self.get_depth()
        json_obj["node_type"] = self.node_type
        json_obj["description"] = self.description
        if self.observation != "":
            json_obj["observation"] = self.observation
        json_obj["child_count"] = len(self.children)
        if self.expand_num != 0:
            json_obj["expand_num"] = self.expand_num

        if self.env != None and self.node_type == "Action Input":
            json_obj["env"] = self.env.to_json()
        if self.score != None:
            json_obj["score"] = self.score

        if self.reflection != []:
            json_obj["reflection"] = self.reflection
        if self.generated_reflection != "":
            json_obj["generated_reflection"] = self.generated_reflection
        if self.values != []:
            # json_obj["values"] = self.values
            json_obj["mean_value"] = np.mean(np.array(self.values))
            json_obj["mean_votes"] = np.mean(np.array(self.vote_counts))
            # json_obj["vote_counts"] = self.vote_counts


        return json_obj

    def describe_children(self):
        assert self.node_type == "Action Input"
        assert len(self.children) > 0
        des_str = ""
        for i in range(min(len(self.children),10)):
            thought_node = self.children[i]
            temp_str = f"<former_attempt_{i+1}>\nThought: {thought_node.description}\n"
            if len(thought_node.children) > 0:
                action_node = thought_node.children[0]
                temp_str = temp_str + f"Action: {action_node.description}\n"
                if len(action_node.children) > 0:
                    action_input_node = action_node.children[0]
                    temp_str = temp_str + f"Action Input: {action_input_node.description}\nObservation: {action_input_node.observation}\n"
            des_str = des_str + temp_str

        return des_str