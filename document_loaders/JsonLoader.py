import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

class JSONLoader(BaseLoader):
    def __init__(
        self,
        file_path: Union[str, Path],
        content_key: Optional[str] = "",
        metadata_func: Optional[Callable[[dict, dict], dict]] = None,
    ):
        """
        Initializes the JSONLoader with a file path, an optional content key to extract specific content,
        and an optional metadata function to extract metadata from each record.
        """
        self.file_path = Path(file_path).resolve()
        self.content_key = content_key
        self.metadata_func = metadata_func

    def create_documents(self, processed_data):
        """
        Creates Document objects from processed data.
        """
        documents = []
        for item in processed_data:
            content = item.get('content', '')
            metadata = item.get('metadata', {})
            document = Document(page_content=content, metadata=metadata)
            documents.append(document)
        return documents

    def process_json(self, data):
        """
        Processes JSON data to prepare for document creation, extracting content based on the content_key
        and applying the metadata function if provided.
        """
        processed_data = []
        if isinstance(data, list):
            for item in data:
                content = item.get(self.content_key, '') if self.content_key else ''
                item.setdefault('source', self.file_path)
                metadata = {}
                if self.metadata_func and isinstance(item, dict):
                    metadata = self.metadata_func(item, {})
                processed_data.append({'content': content, 'metadata': metadata})
        return processed_data

    def load(self) -> List[Document]:
        """
        Load and return documents from the JSON file.
        """
        docs = []
        with open(self.file_path, mode="r", encoding="utf-8") as json_file:
            try:
                data = json.load(json_file)
                processed_json = self.process_json(data)
                docs = self.create_documents(processed_json)
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in the file.")
        return docs