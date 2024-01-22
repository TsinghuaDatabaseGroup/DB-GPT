import sys
sys.path.append("..")

from text_splitter.structured_document_splitter import StructuredDocumentSplitter, read_structured_docx
import os

if __name__ == "__main__":

    ROOT_DIR_NAME = "docs/enmo/reports"

    text_splitter = StructuredDocumentSplitter(
        keep_separator=True,
        is_separator_regex=True,
        chunk_size=50,
        chunk_overlap=0,
        section_style_prefix=["Heading"]
    )
    
    for root, dirs, files in os.walk(ROOT_DIR_NAME):
        for file in files:
            if (file.endswith(".docx")) and not file.startswith("~$"):
                document_path = os.path.join(root, file)

                # split by section structures
                try:
                    read_structured_docx(root, document_path)
                except Exception as e:
                    import pdb; pdb.set_trace()
                    print("Fail to read file: ", file)

    # ls = []
    # for file in files:
    #     if ".doc" in file:
    #         try:
    #             ls.append([file, read_structured_docx("../knowledge_base/yun_he_en_mo/" + file)])
    #         except:
    #             print("Fail to read file: ", file)

    # for inum, element in enumerate(ls):
    #     print("\n*************** ", element[0], " ***************\n")
    #     chunks = text_splitter._split_doc_tree(element[1])