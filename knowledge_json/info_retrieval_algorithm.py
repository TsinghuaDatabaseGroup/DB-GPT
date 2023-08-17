import numpy as np
from typing import List
import heapq
import openai
# import editdistance
from rank_bm25 import BM25Okapi
import json
from nltk import pos_tag
# from nltk.stem import WordNetLemmatizer
# from nltk.corpus import wordnet, stopwords
# from nltk.tokenize import word_tokenize 
# import nltk



# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# wnl = WordNetLemmatizer()

# corpus = []
# with open("/Users/4paradigm/Desktop/work/2023_05_22/root_causes_dbmind.jsonl", 'r') as f:
#     data = json.load(f)
#     corpus = [example["desc"] for example in data]
#     metrics = [example["metrics"] for example in data]
# stop_words = set(stopwords.words('english')) 

# preprocessed_corpus = []
# for c in corpus:
#     word_tokens = word_tokenize(c) 
#     preprocessed_corpus.append([wnl.lemmatize(w,pos='n') for w in word_tokens if not w in stop_words])


# def embedding(input:str):
#     response = openai.Embedding.create(
#         input=input,
#         model="text-embedding-ada-002"
#     )
#     embeddings = response['data'][0]['embedding']
#     # print("\n-----\ntext:{}\n embeddings:{}\n-----\n".format(input, embeddings))
#     return embeddings

# def euclidean_distance(target:List[float], sample:List[float]):
#     """
#     return the euclidean distance of two vectors
#     """
#     return np.sqrt(np.sum(np.square(np.asarray(target) - np.asarray(sample))))

# def cosine_distance(target:List[float], sample:List[float]):
#     """
#     return the euclidean distance of two vectors
#     """
#     return 1 - np.dot(target,sample)/(np.linalg.norm(target)*np.linalg.norm(sample))

# def linear_search(k:int, target:List[float], samples:List[List[float]]):
#     """
#     k: the top-k examples
#     target: incoming metrics
#     samples: examples
#     """
#     func_distance = cosine_distance
#     # func_distance = cosine_distance
#     dist = []
#     for s in samples:
#         dist.append(func_distance(target, s))
#     index = heapq.nlargest(k, range(len(dist)), dist.__getitem__)
#     return index

    
# THRESHOLD = 0.5

# def editdis_linear(k:int, target:List[str], samples:List[List[str]]):
#     dist = []
#     for sample in samples:
#         dis = len(target)
#         for t in target:
#             dis_samples = [editdistance.eval(t, s)/max(len(t), len(s)) for s in sample]
#             if min(dis_samples) < THRESHOLD:
#                 dis -= 1
#         dist.append(dis)
#     index = heapq.nsmallest(k, range(len(dist)), dist.__getitem__)
#     return index
    
def simple_tok(sent:str):
    return sent.split()

# def get_wordnet_pos(tag):
#     if tag.startswith('J'):
#         return wordnet.ADJ
#     elif tag.startswith('V'):
#         return wordnet.VERB
#     elif tag.startswith('N'):
#         return wordnet.NOUN
#     elif tag.startswith('R'):
#         return wordnet.ADV
#     else:
#         return None

def bm25(k, target:List[str], sample:List[List[str]]):
    tok_corpus = sample
    bm25 = BM25Okapi(tok_corpus)
    query = target
    scores = bm25.get_scores(query)

    best_docs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    best_docs_none_zero = []
    for d in best_docs:
        if scores[d] != 0:
            best_docs_none_zero.append(d)
    return best_docs_none_zero