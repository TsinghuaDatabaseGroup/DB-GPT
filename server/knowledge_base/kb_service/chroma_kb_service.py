from configs import SCORE_THRESHOLD, kbs_config, VS_TYPE_PROMPT_TOTAL_BYTE_SIZE
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
        # print(f"server.knowledge_base.kb_service.chroma_kb_service.do_search 输入的query参数为:{query}")
        self._load_chroma()
        # TODO: 取消score_threshold_process，使用chromadb自己的距离计算
        docs = self.chroma.similarity_search_with_score(query, top_k)
        results = score_threshold_process(score_threshold, top_k, docs)
        byte_count = 0
        info_docs = []
        for doc in results:
            source = doc[0]
            context = source.page_content
            metadata = source.metadata
            score = doc[1]

            if (byte_count + len(context)) > VS_TYPE_PROMPT_TOTAL_BYTE_SIZE:
                context = context[:VS_TYPE_PROMPT_TOTAL_BYTE_SIZE - byte_count]

            doc_with_score = [Document(page_content=context, metadata=metadata), score]
            info_docs.append(doc_with_score)
            byte_count += len(context)

            if byte_count >= VS_TYPE_PROMPT_TOTAL_BYTE_SIZE:
                break
        print(f"ChromaDB搜索到{len(info_docs)}个结果")
        # 将结果写入文件
        result_file = open("chromadb_search_results.txt", "w", encoding="utf-8")
        result_file.write(f"query:{query}")
        result_file.write(f"ChromaDB搜索到{len(info_docs)}个结果：\n")
        for item in info_docs:
            doc = item[0]
            result_file.write(doc.page_content + "\n")
            result_file.write("*" * 20)
            result_file.write("\n")
            result_file.flush()
            # print(doc.page_content + "\n")
            # print("*" * 20)
            # print("\n")
        result_file.close()
        # print(f"server.knowledge_base.kb_service.chroma_kb_service.do_search 输出的info_docs参数为:{info_docs}")
        return info_docs
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
        print("*"*100)
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
    chromaService = ChromaKBService("samples")
    # chromaService.add_doc(KnowledgeFile("C:\\Users\\hd\\Desktop\\Data-Chat\\README.md", "test"))
    # chromaService.delete_doc(KnowledgeFile("C:\\Users\\hd\\Desktop\\Data-Chat\\README.md", "test"), False)
    # ids = chromaService.chroma.get(where={"source": "C:\\Users\\hd\\Desktop\\Data-Chat\\README.md"}).get('ids')
    # print(ids)
    docs = chromaService.do_search(query="清华大学捐赠资金由哪些部门进行管理", top_k=3, score_threshold=1)
    print(docs)

