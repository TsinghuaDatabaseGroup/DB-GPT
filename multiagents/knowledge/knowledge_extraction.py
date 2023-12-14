import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
three_up_path = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
sys.path.append(three_up_path)

import json
import os
import requests
import numpy as np
import paramiko

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
from nltk.tokenize import word_tokenize
import nltk
nltk.data.path.append('./nltk_data')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import wordnet

from multiagents.knowledge.info_retrieval_algorithm import bm25

# match with external knowledge for in-context learning
class KnowledgeExtraction():

    def __init__(self, file_path, topk=1, keyword_matching_func=bm25):
        
        # select an attribute in the jsons to embed
        self.names = {"matched_attr": "cause_name"}
        self.cause_name = self.names["matched_attr"]

        # nltk.download('stopwords')
        # nltk.download('stopwords')
        # nltk.download('punkt')
        # nltk.download('averaged_perceptron_tagger')
        # nltk.download('wordnet')
        
        self.wnl = WordNetLemmatizer()
        self.keyword_matching_func = keyword_matching_func

        self.topk = topk

        self.corpus, self.preprocessed_corpus, self.matched_attr, self.stop_words = self.knowledge_load(file_path)

    def knowledge_load(self, file_path):

        # file_path = "/bmtools/tools/db_diag/root_causes_dbmind.jsonl"
        with open(str(os.getcwd()) + file_path, 'r') as f:
            self.data = json.load(f)
            self.corpus = [example["desc"] for example in self.data]
            self.matched_attr = [example[self.names["matched_attr"]] for example in self.data]
        self.stop_words = set(stopwords.words('english'))

        self.preprocessed_corpus = []
        for example in self.data:
            
            word_tokens = [w.lower() for w in word_tokenize(example["metrics"]) if w != '-']
            self.preprocessed_corpus.append([self.wnl.lemmatize(w,pos='n') for w in word_tokens if not w in self.stop_words]) # remove useless words and standardize words #slow

        return self.corpus, self.preprocessed_corpus, self.matched_attr, self.stop_words

    def match(self, detailed_metrics):

        metrics_str = []

        for metrics in detailed_metrics.keys():
            metrics = metrics.replace("_"," ") 
            word_tokens = word_tokenize(metrics)
            metrics_str.extend([self.wnl.lemmatize(w,pos='n') for w in word_tokens if not w in self.stop_words])
        metrics_str = list(set(metrics_str))

        best_index = self.keyword_matching_func(self.topk, metrics_str, self.preprocessed_corpus)

        best_docs = [self.corpus[b] for b in best_index]
        best_names = [self.matched_attr[b] for b in best_index]
        docs_str = ""

        for i, docs in enumerate(best_docs):
            docs_str = docs_str + "{}: ".format(best_names[i]) + docs + "\n\n"

        # print("best_docs: ", best_docs)

        return docs_str
    

if __name__ == "__main__":
    matcher = KnowledgeExtraction("/root_causes_dbmind.jsonl")
    print(matcher.match({"memory_resource_contention":123, "node_scrape_collector_duration_seconds": 1293}))
