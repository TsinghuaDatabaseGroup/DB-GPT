from configs import SCORE_THRESHOLD, kbs_config
from server.knowledge_base.kb_service.base import KBService, SupportedVSType, EmbeddingsFunAdapter, \
    score_threshold_process
from server.knowledge_base.utils import KnowledgeFile, get_kb_path, get_vs_path
from langchain.docstore.document import Document
from typing import List, Dict
from langchain.vectorstores import Chroma

class ChromaKBService(KBService):
    vs_path: str
    kb_path: str
    vector_name: str = None
    chroma: Chroma

    def vs_type(self) -> str:
        return SupportedVSType.CHROMADB

    def get_vs_path(self):
        return get_vs_path(self.kb_name, self.vector_name)

    def get_kb_path(self):
        return get_kb_path(self.kb_name)
    
    def save_vector_store(self):
        print("==============save_vector_store=================")
        pass
    
    def get_doc_by_ids(self, ids: List[str]) -> List[Document]:
        results = self.chroma.get(ids)
        return [Document(page_content=result["text"], metadata=result["metadata"]) for result in results]

    def _load_chroma(self):
        self.chroma = Chroma(embedding_function=EmbeddingsFunAdapter(self.embed_model), collection_name=self.kb_name,
                             persist_directory=kbs_config.get("chromadb").get('persist_directory'))

    def do_init(self):
        self.vector_name = self.vector_name or self.embed_model
        self.kb_path = self.get_kb_path()
        self.vs_path = self.get_vs_path()
        self._load_chroma()

    def do_create_kb(self):
        pass

    def do_drop_kb(self):
        print("==============do_drop_kb=================")
        pass

    def do_search(self,
                  query: str,
                  top_k: int,
                  score_threshold: float = SCORE_THRESHOLD,
                  ) -> List[Document]:
        self._load_chroma()
        # TODO: 取消score_threshold_process，使用chromadb自己的距离计算
        docs = self.chroma.similarity_search_with_score(query, top_k)
        print("********do_search:", docs)
        return score_threshold_process(score_threshold, top_k, docs)

    def do_add_doc(self,
                   docs: List[Document],
                   **kwargs,
                   ) -> List[Dict]:
        print(f"server.knowledge_base.kb_service.chroma_kb_service.do_add_doc 输入的docs参数长度为:{len(docs)}")
        print("*" * 100)
        texts = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]
        ids = self.chroma.add_texts(texts, metadatas)
        doc_infos = [{"id": id, "metadata": metadata} for id, metadata in zip(ids, metadatas)]
        print("写入数据成功.")
        print("*" * 100)
        return doc_infos

    def do_delete_doc(self,
                      kb_file: KnowledgeFile,
                      **kwargs):
        ids = self.chroma.get(where={"source": kb_file.filename}).get('ids')
        if len(ids) > 0:
            self.chroma.delete(ids)

    def do_clear_vs(self):
        print("==============do_clear_vs=================")
        pass


if __name__ == '__main__':
    chromaService = ChromaKBService("test")
    chromaService.add_doc(KnowledgeFile("C:\\Users\\hd\\Desktop\\Data-Chat\\README.md", "test"))
    # chromaService.delete_doc(KnowledgeFile("C:\\Users\\hd\\Desktop\\Data-Chat\\README.md", "test"), False)
    # ids = chromaService.chroma.get(where={"source": "C:\\Users\\hd\\Desktop\\Data-Chat\\README.md"}).get('ids')
    # print(ids)
    docs = chromaService.search_docs(query="")
    print(docs)