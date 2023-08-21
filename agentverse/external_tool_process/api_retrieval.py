from langchain.embeddings import OpenAIEmbeddings
from typing import List
from queue import PriorityQueue
import os

class api_retriever:
    def __init__(self,
                 openai_api_key: str = None,
                 model: str = "text-embedding-ada-002"):
        if openai_api_key is None:
            openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.embed = OpenAIEmbeddings(openai_api_key=openai_api_key, model=model)

    def query(self, query: str, apis: list, topk: int = 5) -> List[str]:
        query_embedding = self.embed.embed_query(query)

        queue = PriorityQueue()
        for api in apis:
            tool_embedding = self.embed.embed_query(api.description)
            tool_sim = self.similarity(query_embedding, tool_embedding)
            queue.put([-tool_sim, api])

        result = []
        for i in range(min(topk, len(queue.queue))):
            tool = queue.get()
            result.append(tool[1])

        return result

    def similarity(self, query: List[float], document: List[float]) -> float:
        return sum([i * j for i, j in zip(query, document)])