#!/user/bin/env python3
"""
File_Name: es_kb_service.py
Author: TangGuoLiang
Email: 896165277@qq.com
Created: 2023-09-05
"""
from typing import List
import os
import shutil

import jieba
import jieba.analyse
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores.elasticsearch import ElasticsearchStore
from configs import KB_ROOT_PATH, EMBEDDING_MODEL, EMBEDDING_DEVICE, CACHED_VS_NUM, VS_TYPE_PROMPT_TOTAL_BYTE_SIZE
from server.knowledge_base.kb_service.base import KBService, SupportedVSType
from server.utils import load_local_embeddings
from elasticsearch import Elasticsearch
from configs import logger
from configs import kbs_config


class ESKBService(KBService):

    def do_init(self):
        self.kb_path = self.get_kb_path(self.kb_name)
        self.index_name = self.kb_name
        self.IP = kbs_config[self.vs_type()]['host']
        self.PORT = kbs_config[self.vs_type()]['port']
        self.user = kbs_config[self.vs_type()].get("user", '')
        self.password = kbs_config[self.vs_type()].get("password", '')

        self.embeddings_model = load_local_embeddings(
            self.embed_model, EMBEDDING_DEVICE)
        try:
            # ES python客户端连接（仅连接）
            if self.user != "" and self.password != "":
                self.es_client_python = Elasticsearch(
                    f"http://{self.IP}:{self.PORT}",
                    basic_auth=(
                        self.user,
                        self.password))
            else:
                logger.warning("ES未配置用户名和密码")
                self.es_client_python = Elasticsearch(
                    f"http://{self.IP}:{self.PORT}")
            self.es_client_python.indices.create(index=self.index_name)
        except ConnectionError:
            logger.error("连接到 Elasticsearch 失败！")
        except Exception as e:
            logger.error(f"Error 发生 : {e}")

        try:
            # langchain ES 连接、创建索引
            if self.user != "" and self.password != "":
                self.db_init = ElasticsearchStore(
                    es_url=f"http://{self.IP}:{self.PORT}",
                    index_name=self.index_name,
                    query_field="context",
                    vector_query_field="dense_vector",
                    embedding=self.embeddings_model,
                    es_user=self.user,
                    es_password=self.password
                )
            else:
                logger.warning("ES未配置用户名和密码")
                self.db_init = ElasticsearchStore(
                    es_url=f"http://{self.IP}:{self.PORT}",
                    index_name=self.index_name,
                    query_field="context",
                    vector_query_field="dense_vector",
                    embedding=self.embeddings_model,
                )
        except ConnectionError:
            print("### 连接到 Elasticsearch 失败！")
            logger.error("### 连接到 Elasticsearch 失败！")
        except Exception as e:
            logger.error(f"Error 发生 : {e}")

    @staticmethod
    def get_kb_path(knowledge_base_name: str):
        return os.path.join(KB_ROOT_PATH, knowledge_base_name)

    @staticmethod
    def get_vs_path(knowledge_base_name: str):
        return os.path.join(ESKBService.get_kb_path(
            knowledge_base_name), "vector_store")

    def do_create_kb(self):
        if os.path.exists(self.doc_path):
            if not os.path.exists(os.path.join(self.kb_path, "vector_store")):
                os.makedirs(os.path.join(self.kb_path, "vector_store"))
            else:
                logger.warning("directory `vector_store` already exists.")

    def vs_type(self) -> str:
        return SupportedVSType.ES

    def _load_es(self, docs, embed_model):
        # 将docs写入到ES中
        try:
            # 连接 + 同时写入文档
            if self.user != "" and self.password != "":
                self.db = ElasticsearchStore.from_documents(
                    documents=docs,
                    embedding=embed_model,
                    es_url=f"http://{self.IP}:{self.PORT}",
                    index_name=self.index_name,
                    distance_strategy="COSINE",
                    query_field="context",
                    vector_query_field="dense_vector",
                    verify_certs=False,
                    es_user=self.user,
                    es_password=self.password
                )
            else:
                self.db = ElasticsearchStore.from_documents(
                    documents=docs,
                    embedding=embed_model,
                    es_url=f"http://{self.IP}:{self.PORT}",
                    index_name=self.index_name,
                    distance_strategy="COSINE",
                    query_field="context",
                    vector_query_field="dense_vector",
                    verify_certs=False)
        except ConnectionError as ce:
            print(ce)
            print("连接到 Elasticsearch 失败！")
            logger.error("连接到 Elasticsearch 失败！")
        except Exception as e:
            logger.error(f"Error 发生 : {e}")
            print(e)

    def do_search(self, query: str, top_k: int, score_threshold: float):
        # TODO: 语义分词后期配置可换
        print(
            f"server.knowledge_base.kb_service.es_kb_service.do_search 输入的query参数为:{query}")
        query_list = jieba.analyse.textrank(query, topK=20, withWeight=False)
        if len(query_list) == 0:
            query_list = [query]
        body = {
            "query": {
                "match": {
                    "context": " ".join(query_list)
                }
            }
        }
        search_results = self.es_client_python.search(
            index=self.index_name, body=body, size=top_k)
        search_results = search_results['hits']['hits']

        # 判断搜索结果是否为空
        if not search_results:
            return []

        info_docs = []
        byte_count = 0

        for result in search_results:
            source = result["_source"]
            context = source["context"]
            metadata = source["metadata"]
            score = result["_score"]

            # 如果下一个context会超过总字节数限制，则截断context
            if (byte_count + len(context)) > VS_TYPE_PROMPT_TOTAL_BYTE_SIZE:
                context = context[:VS_TYPE_PROMPT_TOTAL_BYTE_SIZE - byte_count]

            doc_with_score = [Document(page_content=context, metadata=metadata), score]
            info_docs.append(doc_with_score)

            byte_count += len(context)

            # 如果字节数已经达到限制，则结束循环
            if byte_count >= VS_TYPE_PROMPT_TOTAL_BYTE_SIZE:
                break
        print(f"ES搜索到{len(info_docs)}个结果：")
        # 将结果写入文件
        result_file = open("es_search_results.txt", "w", encoding="utf-8")
        result_file.write(f"query:{query}")
        result_file.write(f"ES搜索到{len(info_docs)}个结果：\n")
        for item in info_docs:
            doc = item[0]
            result_file.write(doc.page_content + "\n")
            result_file.write("*" * 20)
            result_file.write("\n")
            result_file.flush()
            print(doc.page_content + "\n")
            print("*" * 20)
            print("\n")
        result_file.close()
        # print(f"server.knowledge_base.kb_service.es_kb_service.do_search 输出的info_docs参数为:{info_docs}")
        return info_docs

    def do_delete_doc(self, kb_file, **kwargs):
        try:
            if self.es_client_python.indices.exists(index=self.index_name):
                # 从向量数据库中删除索引(文档名称是Keyword)
                query = {
                    "query": {
                        "term": {
                            "metadata.source.keyword": kb_file.filepath
                        }
                    }
                }
                # 注意设置size，默认返回10个。
                search_results = self.es_client_python.search(body=query, size=50)
                delete_list = [hit["_id"]
                               for hit in search_results['hits']['hits']]
                if len(delete_list) == 0:
                    return None
                else:
                    for doc_id in delete_list:
                        try:
                            self.es_client_python.delete(index=self.index_name,
                                                         id=doc_id,
                                                         refresh=True)
                        except Exception as e:
                            logger.error("ES Docs Delete Error!")

                # self.db_init.delete(ids=delete_list)
                # self.es_client_python.indices.refresh(index=self.index_name)
        except Exception as e:
            logger.error(f"Error 发生 : {e}")
            return None
    def do_add_doc(self, docs: List[Document], **kwargs):
        '''向知识库添加文件'''
        print(
            f"server.knowledge_base.kb_service.es_kb_service.do_add_doc 输入的docs参数长度为:{len(docs)}")
        print("*" * 100)
        self._load_es(docs=docs, embed_model=self.embeddings_model)
        # 获取 id 和 source , 格式：[{"id": str, "metadata": dict}, ...]
        print("写入数据成功.")
        print("*" * 100)

        if self.es_client_python.indices.exists(index=self.index_name):
            file_path = docs[0].metadata.get("source")
            query = {
                "query": {
                    "term": {
                        "metadata.source.keyword": file_path
                    }
                }
            }
            search_results = self.es_client_python.search(body=query)
            if len(search_results["hits"]["hits"]) == 0:
                return []
            info_docs = [{"id": hit["_id"], "metadata": hit["_source"]["metadata"]} for hit in search_results["hits"]["hits"]]
            return info_docs
        else:
            return []

    def do_clear_vs(self):
        """从知识库删除全部向量"""
        if self.es_client_python.indices.exists(index=self.kb_name):
            self.es_client_python.indices.delete(index=self.kb_name)

    def do_drop_kb(self):
        """删除知识库"""
        # self.kb_file: 知识库路径
        if os.path.exists(self.kb_path):
            shutil.rmtree(self.kb_path)
