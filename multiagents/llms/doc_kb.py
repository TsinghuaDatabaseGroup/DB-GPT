from server.knowledge_base.kb_service.base import KBServiceFactory, KBService
from configs import EMBEDDING_MODEL, log_verbose, DEFAULT_VS_TYPES, VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD
from langchain.docstore.document import Document
from typing import List
from pydantic import BaseModel
import logging

FEEDBACK_KB_NAME = 'feedback'

class MyKnowledgeFile:
    def __init__(self, filename: str):
        self.filename = filename

class DocKnowledgeBase(BaseModel):
    knowledge_base_name: str = FEEDBACK_KB_NAME
    kbs: list = []
    def __init__(self, knowledge_base_name: str = FEEDBACK_KB_NAME, embed_model: str = EMBEDDING_MODEL):
        super().__init__(knowledge_base_name=knowledge_base_name, embed_model=embed_model)
        self.knowledge_base_name = knowledge_base_name
        self.kbs = []
        for vs_type in DEFAULT_VS_TYPES:
            kb = KBServiceFactory.get_service_by_name(knowledge_base_name, vs_type)
            if kb is not None:
                self.kbs.append(kb)
                continue
            kb = KBServiceFactory.get_service(knowledge_base_name, vs_type, embed_model=embed_model)
            try:
                kb.create_kb()
            except Exception as e:
                msg = f"创建知识库出错： {e}"
                logging.error(f'{e.__class__.__name__}: {msg}',
                            exc_info=e if log_verbose else None)
                continue
            self.kbs.append(kb)

    def add_docs(self, docs: List[Document]):
        for kb in self.kbs:
            kb.do_add_doc(docs)
            kb.save_vector_store()

    def delete_docs(self, docs: List[Document]):
        for kb in self.kbs:
            for doc in docs:
                kb.do_delete_doc(MyKnowledgeFile(doc.metadata['source']))
            kb.save_vector_store()
    
    def update_docs(self, docs: List[Document]):
        self.delete_docs(docs)
        self.add_docs(docs)

    def search_docs(self, query: str, metadata_filter: dict, top_k: int = VECTOR_SEARCH_TOP_K, score_threshold: float = SCORE_THRESHOLD) -> List[Document]:
        data = []
        for kb in self.kbs:
            docs = kb.search_docs(query, top_k * 2, score_threshold)

            filtered_docs = []
            for doc in docs:
                print(doc)
                if all([doc[0].dict()['metadata'].get(k) == v for k, v in metadata_filter.items()]):
                    filtered_docs.append(doc)

            data.extend([Document(page_content=x[0].page_content, metadata=x[0].dict()['metadata']) for x in filtered_docs])

            print(f"知识库采用其中的{len(filtered_docs)}条相关文档：")
            # print filtered_docs separated by \n
            # for doc in filtered_docs:
            #     print(doc[0].metadata)
            # print('*' * 100)
        # take the first top_k of docs 
        if len(data) > top_k:
            data = data[:top_k]
        
        return data

    