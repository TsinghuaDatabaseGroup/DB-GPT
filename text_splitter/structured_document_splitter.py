import re
from typing import List, Optional, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
from docx import Document
import os
from text_splitter.summary_llm.openai import OpenAISummary, prompt_generation

logger = logging.getLogger(__name__)


def read_structured_docx(base_path, file_path):
    doc = Document(file_path)

    all_styles = []
    for style in doc.styles:
        all_styles.append(style.name)
    
    tree = []
    current_node = tree
    path = [tree]  # Stack to keep track of current position in the tree

    new_node = {}
    content_text = ""
    for para in doc.paragraphs:
        
        para.text = para.text.strip()
        if para.text == "" or "云和恩墨" in para.text:
            continue

        style = para.style.name

        if style.startswith('Heading'):
            if new_node != {}:
                new_node['text'] = content_text
            content_text = ""
            
            level = int(style.replace('Heading ', ''))
            
            # Ensure the path stack is only as deep as the current level
            path = path[:level]
            
            # Create a new node for the current heading
            new_node = {'name': para.text, 'text': '', 'children': []}
            
            # Add the new node to its parent
            if path:
                path[-1].append(new_node)
            
            # Update the current node and path
            current_node = new_node['children']
            path.append(current_node)
        else:
            content_text = content_text + '\n\n' + para.text

    if content_text != "":
        if new_node != {}:
            new_node['text'] = content_text
        else:
            new_node = {'name': "root", 'text': content_text, 'children': []}
            tree = [new_node]

    doc_split_path = os.path.join(base_path, file_path.split("/")[-1].split(".")[0])

    if os.path.exists(doc_split_path):
        import shutil
        shutil.rmtree(doc_split_path)
    os.makedirs(doc_split_path)

    write_tree_to_files(tree, base_path=doc_split_path)
    
    return tree


def write_tree_to_files(tree, base_path, section_prefix=""):

    for idx, node in enumerate(tree):

        section_number = f"{section_prefix}.{idx + 1}" if section_prefix != "" else str(idx + 1)
        filename = f"{section_number} {node['name']}.txt"
        file_path = os.path.join(base_path, filename)

        print(" ==================== ")
        print(f"{filename}: {node['text']}")
        print(" ==================== ")

        # Write the node text to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(node['text'])

        # Recursively process children nodes, if any
        if node['children']:
            write_tree_to_files(node['children'], base_path, section_number)

# Example usage
# Assuming 'tree' is your data structure



def traverse_and_print_leaf_texts(node):
    # Check if the node is a leaf node
    if not node['children']:
        chunks = [node['text']]
    else:
        # If the node has children, recursively call this function for each child
        chunks = []
        for child in node['children']:
            chunks = chunks + traverse_and_print_leaf_texts(child)
    return chunks

def _split_text_with_regex_from_end(
        text: str, separator: str, keep_separator: bool
) -> List[str]:
    # Now that we have the separator, split the text
    if separator:
        if keep_separator:
            # The parentheses in the pattern keep the delimiters in the result.
            _splits = re.split(f"({separator})", text)
            splits = ["".join(i) for i in zip(_splits[0::2], _splits[1::2])]
            if len(_splits) % 2 == 1:
                splits += _splits[-1:]
            # splits = [_splits[0]] + splits
        else:
            splits = re.split(separator, text)
    else:
        splits = list(text)
    return [s for s in splits if s != ""]



class StructuredDocumentSplitter(RecursiveCharacterTextSplitter):
    def __init__(
            self,
            separators: Optional[List[str]] = None,
            keep_separator: bool = True,
            is_separator_regex: bool = True,
            section_style_prefix: Optional[List[str]] = ["Heading"],
            **kwargs: Any,
    ) -> None:
        """Create a new TextSplitter."""
        super().__init__(keep_separator=keep_separator, **kwargs)
        self._separators = separators or [
            "\n\n",
            "\n",
            "。|！|？",
            "\.\s|\!\s|\?\s",
            "；|;\s",
            "，|,\s"
        ]
        self._is_separator_regex = is_separator_regex
        self._section_style_prefix = section_style_prefix

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Split incoming text and return chunks."""
        final_chunks = []
        # Get appropriate separator to use
        separator = separators[-1]
        new_separators = []
        for i, _s in enumerate(separators):
            _separator = _s if self._is_separator_regex else re.escape(_s)
            if _s == "":
                separator = _s
                break
            if re.search(_separator, text):
                separator = _s
                new_separators = separators[i + 1:]
                break

        _separator = separator if self._is_separator_regex else re.escape(separator)
        splits = _split_text_with_regex_from_end(text, _separator, self._keep_separator)

        # Now go merging things, recursively splitting longer texts.
        _good_splits = []
        _separator = "" if self._keep_separator else separator
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(_good_splits, _separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    other_info = self._split_text(s, new_separators)
                    final_chunks.extend(other_info)
        if _good_splits:
            merged_text = self._merge_splits(_good_splits, _separator)
            final_chunks.extend(merged_text)
        return [re.sub(r"\n{2,}", "\n", chunk.strip()) for chunk in final_chunks if chunk.strip()!=""]

    def _split_doc_tree(self, tree: list) -> List[str]: 
        chunks = []
        for root in tree:
            chunks = chunks + traverse_and_print_leaf_texts(root)

        summary_model = OpenAISummary()

        final_chunks = []
        for chunk in chunks:
            if self._length_function(chunk) > self._chunk_size:
                # first summarize by llm
                new_prompt = prompt_generation(chunk, self._chunk_size)
                chunk_summary = summary_model.generate_response(new_prompt)

                final_chunks.append(chunk_summary)

                print("=====================================")
                print("origin: ", chunk, "\n")
                print("summary: ", chunk_summary, "\n")

                # next reserve the details of the origin text
                detail_chunks = self._split_text(chunk, self._separators)
                final_chunks = final_chunks + detail_chunks

                for detail_chunk in detail_chunks:
                    print("detail: ", detail_chunk, "\n")
                
                print("=====================================")
            else:
                print("=====================================")
                print("origin: ", chunk, "\n")
                print("=====================================")

                final_chunks.append(chunk)

        return final_chunks


if __name__ == "__main__":

    # we first split by the leaf nodes in the section-based tree. For any tree whose chunk size is larger than the limit, summarize it with llm and reserve the chunks (details) by .

    text_splitter = StructuredDocumentSplitter(
        keep_separator=True,
        is_separator_regex=True,
        chunk_size=50,
        chunk_overlap=0,
        section_style_prefix=["Heading"]
    )

    files = os.listdir("./example_docs/")

    ls = []
    for file in files:
        if ".doc" in file:
            try:
                ls.append([file, read_structured_docx("../knowledge_base/yun_he_en_mo/" + file)])
            except:
                print("Fail to read file: ", file)

    for inum, element in enumerate(ls):
        print("\n*************** ", element[0], " ***************\n")
        chunks = text_splitter._split_doc_tree(element[1])