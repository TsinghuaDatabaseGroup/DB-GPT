from configs import (
    EMBEDDING_MODEL, ZH_TITLE_ENHANCE,
    CHUNK_SIZE, OVERLAP_SIZE,
    logger, log_verbose, DEFAULT_VS_TYPES
)

from server.knowledge_base.utils import (
    get_file_path, list_kbs_from_folder,
    list_files_from_folder, files2docs_in_thread,
    KnowledgeFile
)
from server.knowledge_base.kb_service.base import KBServiceFactory
from server.db.models.conversation_model import ConversationModel
from server.db.models.message_model import MessageModel
from server.db.repository.knowledge_file_repository import add_file_to_db # ensure Models are imported
from server.db.repository.knowledge_metadata_repository import add_summary_to_db

from server.db.base import Base, engine
from server.db.session import session_scope
import os
from dateutil.parser import parse
from typing import Literal, List


def create_tables():
    Base.metadata.create_all(bind=engine)


def reset_tables():
    Base.metadata.drop_all(bind=engine)
    create_tables()


def import_from_db(
        sqlite_path: str = None,
        # csv_path: str = None,
) -> bool:
    """
    在知识库与向量库无变化的情况下，从备份数据库中导入数据到 info.db。
    适用于版本升级时，info.db 结构变化，但无需重新向量化的情况。
    请确保两边数据库表名一致，需要导入的字段名一致
    当前仅支持 sqlite
    """
    import sqlite3 as sql
    from pprint import pprint

    models = list(Base.registry.mappers)

    try:
        con = sql.connect(sqlite_path)
        con.row_factory = sql.Row
        cur = con.cursor()
        tables = [x["name"] for x in cur.execute("select name from sqlite_master where type='table'").fetchall()]
        for model in models:
            table = model.local_table.fullname
            if table not in tables:
                continue
            print(f"processing table: {table}")
            with session_scope() as session:
                for row in cur.execute(f"select * from {table}").fetchall():
                    data = {k: row[k] for k in row.keys() if k in model.columns}
                    if "create_time" in data:
                        data["create_time"] = parse(data["create_time"])
                    pprint(data)
                    session.add(model.class_(**data))
        con.close()
        return True
    except Exception as e:
        print(f"无法读取备份数据库：{sqlite_path}。错误信息：{e}")
        return False


def file_to_kbfile(kb_name: str, files: List[str]) -> List[KnowledgeFile]:
    kb_files = []
    for file in files:
        try:
            kb_file = KnowledgeFile(filename=file, knowledge_base_name=kb_name)
            kb_files.append(kb_file)
        except Exception as e:
            msg = f"{e}，已跳过"
            logger.error(f'{e.__class__.__name__}: {msg}',
                         exc_info=e if log_verbose else None)
    return kb_files

def folder2db(
        kb_names: List[str],
        mode: Literal["recreate_vs", "update_in_db", "increament"],
        vs_types: List[Literal["faiss", "milvus", "pg", "chromadb"]] = DEFAULT_VS_TYPES,
        embed_model: str = EMBEDDING_MODEL,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = OVERLAP_SIZE,
        zh_title_enhance: bool = ZH_TITLE_ENHANCE,
):
    """
    use existed files in local folder to populate database and/or vector store.
    set parameter `mode` to:
        recreate_vs: recreate all vector store and fill info to database using existed files in local folder
        fill_info_only(disabled): do not create vector store, fill info to db using existed files only
        update_in_db: update vector store and database info using local files that existed in database only
        increament: create vector store and database info for local files that not existed in database only
    """

    def files2vs(kb_name: str, kb_files: List[KnowledgeFile]):
        for success, result in files2docs_in_thread(kb_files,
                                                    chunk_size=chunk_size,
                                                    chunk_overlap=chunk_overlap,
                                                    zh_title_enhance=zh_title_enhance):
            if success:
                _, filename, docs = result
                print(f"正在将 {kb_name}/{filename} 添加到向量库，共包含{len(docs)}条文档")
                kb_file = KnowledgeFile(filename=filename, knowledge_base_name=kb_name)
                kb_file.splited_docs = docs
                kb.add_doc(kb_file=kb_file, not_refresh_vs_cache=True)
            else:
                print(result)

    kb_names = kb_names or list_kbs_from_folder()

    for vs_type in vs_types:
        for kb_name in kb_names:
            kb = KBServiceFactory.get_service(kb_name, vs_type, embed_model)
            if not kb.exists():
                kb.create_kb()

            if mode == "recreate_vs":
                kb.clear_vs()
                kb.create_kb()
                kb_files = file_to_kbfile(kb_name, list_files_from_folder(kb_name))
                files2vs(kb_name, kb_files)
                kb.save_vector_store()

            elif mode == "update_in_db":
                files = kb.list_files()
                kb_files = file_to_kbfile(kb_name, files)
                files2vs(kb_name, kb_files)
                kb.save_vector_store()

            elif mode == "increament":
                db_files = kb.list_files()
                folder_files = list_files_from_folder(kb_name)
                files = list(set(folder_files) - set(db_files))
                kb_files = file_to_kbfile(kb_name, files)
                files2vs(kb_name, kb_files)
                kb.save_vector_store()

            else:
                print(f"unspported migrate mode: {mode}")


def prune_db_docs(kb_names: List[str]):
    """
    delete docs in database that not existed in local folder.
    it is used to delete database docs after user deleted some doc files in file browser
    """
    for kb_name in kb_names:
        kb = KBServiceFactory.get_service_by_name(kb_name, DEFAULT_VS_TYPES[0])
        if kb is not None:
            files_in_db = kb.list_files()
            files_in_folder = list_files_from_folder(kb_name)
            files = list(set(files_in_db) - set(files_in_folder))
            kb_files = file_to_kbfile(kb_name, files)
            for kb_file in kb_files:
                kb.delete_doc(kb_file, not_refresh_vs_cache=True)
                print(f"success to delete docs for file: {kb_name}/{kb_file.filename}")
            kb.save_vector_store()


def prune_folder_files(kb_names: List[str]):
    """
    delete doc files in local folder that not existed in database.
    it is used to free local disk space by delete unused doc files.
    """
    for kb_name in kb_names:
        kb = KBServiceFactory.get_service_by_name(kb_name, DEFAULT_VS_TYPES[0])
        if kb is not None:
            files_in_db = kb.list_files()
            files_in_folder = list_files_from_folder(kb_name)
            files = list(set(files_in_folder) - set(files_in_db))
            for file in files:
                os.remove(get_file_path(kb_name, file))
                print(f"success to delete file: {kb_name}/{file}")
