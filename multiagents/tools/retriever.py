from multiagents.llms.sentence_embedding import sentence_embedding
from multiagents.tools.api_retrieval import APICaller

from typing import List, Dict
from queue import PriorityQueue
import os
import requests
import time
import json


class api_matcher:
    def __init__(self,
                 model: str = "text-embedding-ada-002"):

        self.model = model
        self.apis = dict()

    def add_tool(self, apis: APICaller) -> None:

        for api in apis.functions:
            api_content = apis.functions[api]

            self.apis[str(api)] = {
                "desc": str(api_content["desc"]),
                "embedding": api_content["embedding"]
            }

    def query(self, query: str, topk: int = 5) -> List[str]:
        query_embedding = sentence_embedding(sentence=query, model=self.model)

        queue = PriorityQueue()
        for api_name, api_info in self.apis.items():
            api_embedding = api_info["embedding"]
            api_sim = self.similarity(query_embedding, api_embedding)
            queue.put([-api_sim, api_name, api_info["desc"]])

        result = {}
        for i in range(min(topk, len(queue.queue))):
            api = queue.get()
            result[api[1]] = api[2]
        
        return result

    def similarity(self, query: List[float], document: List[float]) -> float:
        return sum([i * j for i, j in zip(query, document)])