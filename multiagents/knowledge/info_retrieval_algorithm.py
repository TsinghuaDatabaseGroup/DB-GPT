import numpy as np
from typing import List
import heapq
import openai
# import editdistance
# from rank_bm25 import BM25Okapi
import math
import numpy as np
from multiprocessing import Pool, cpu_count
import json
import nltk
nltk.data.path.append('./nltk_data')
from nltk import pos_tag
from nltk.corpus import wordnet

# from nltk.stem import WordNetLemmatizer
# from nltk.corpus import wordnet, stopwords
# from nltk.tokenize import word_tokenize 

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


'''
Inherited from the BM25Okapi API of rank_bm25 package
'''

class BM25:
    def __init__(self, corpus, tokenizer=None):
        self.corpus_size = 0
        self.avgdl = 0
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
        self.tokenizer = tokenizer

        if tokenizer:
            corpus = self._tokenize_corpus(corpus)

        nd = self._initialize(corpus)
        self._calc_idf(nd)

    def _initialize(self, corpus):
        nd = {}  # word -> number of documents with word
        num_doc = 0
        for document in corpus: # each document is a knowledge chunk
            self.doc_len.append(len(document))
            num_doc += len(document)

            frequencies = {}

            for word in document:
                if word not in frequencies:
                    frequencies[word] = 0
                frequencies[word] += 1
            self.doc_freqs.append(frequencies)

            for word, freq in frequencies.items():
                try:
                    nd[word]+=1
                except KeyError:
                    nd[word] = 1

            self.corpus_size += 1

        self.avgdl = num_doc / self.corpus_size
        return nd

    def _tokenize_corpus(self, corpus):
        pool = Pool(cpu_count())
        tokenized_corpus = pool.map(self.tokenizer, corpus)
        return tokenized_corpus

    def _calc_idf(self, nd):
        raise NotImplementedError()

    def get_scores(self, query):
        raise NotImplementedError()

    def get_batch_scores(self, query, doc_ids):
        raise NotImplementedError()

    def get_top_n(self, query, documents, n=5):

        assert self.corpus_size == len(documents), "The documents given don't match the index corpus!"

        scores = self.get_scores(query)
        top_n = np.argsort(scores)[::-1][:n]
        return [documents[i] for i in top_n]

class BM25_call(BM25):
    def __init__(self, corpus, tokenizer=None, k1=1.5, b=0.75, epsilon=0.25):
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon
        super().__init__(corpus, tokenizer)

    def _calc_idf(self, nd):
        """
        Calculates frequencies of terms in documents and in corpus.
        This algorithm sets a floor on the idf values to eps * average_idf
        """
        # collect idf sum to calculate an average idf for epsilon value
        idf_sum = 0
        # collect words with negative idf to set them a special epsilon value.
        # idf can be negative if word is contained in more than half of documents
        negative_idfs = []
        for word, freq in nd.items():
            idf = math.log(self.corpus_size - freq + 0.5) - math.log(freq + 0.5)
            self.idf[word] = idf
            idf_sum += idf
            if idf < 0:
                negative_idfs.append(word)
        self.average_idf = idf_sum / len(self.idf)

        eps = self.epsilon * self.average_idf
        for word in negative_idfs:
            self.idf[word] = eps

    def get_scores(self, query):
        """
        The ATIRE BM25 variant uses an idf function which uses a log(idf) score. To prevent negative idf scores,
        this algorithm also adds a floor to the idf value of epsilon.
        See [Trotman, A., X. Jia, M. Crane, Towards an Efficient and Effective Search Engine] for more info
        :param query:
        :return:
        """
        score = np.zeros(self.corpus_size)
        doc_len = np.array(self.doc_len)
        for q in query:            
            q_freq = np.zeros(self.corpus_size)
            synonymous_q = None
            for i, doc in enumerate(self.doc_freqs):
                for w in doc:
                    if are_synonyms(q, w):
                        q_freq[i] += doc[w]
                        synonymous_q = w

            score += (self.idf.get(synonymous_q) or 0) * (q_freq * (self.k1 + 1) /
                                               (q_freq + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)))

        return score

    def get_batch_scores(self, query, doc_ids):
        """
        Calculate bm25 scores between query and subset of all docs
        """
        assert all(di < len(self.doc_freqs) for di in doc_ids)
        score = np.zeros(len(doc_ids))
        doc_len = np.array(self.doc_len)[doc_ids]
        for q in query:
            q_freq = np.array([(self.doc_freqs[di].get(q) or 0) for di in doc_ids])
            score += (self.idf.get(q) or 0) * (q_freq * (self.k1 + 1) /
                                               (q_freq + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)))
        return score.tolist()


def are_synonyms(word1, word2):
    """Check if two words are synonyms using WordNet."""
    synonyms1 = {lemma.name() for synset in wordnet.synsets(word1) for lemma in synset.lemmas()}
    synonyms2 = {lemma.name() for synset in wordnet.synsets(word2) for lemma in synset.lemmas()}
    return not synonyms1.isdisjoint(synonyms2)

def simple_tok(sent:str):
    return sent.split()

def bm25(k, target:List[str], sample:List[List[str]]):

    tok_corpus = sample
    bm25 = BM25_call(tok_corpus)
    query = target
    scores = bm25.get_scores(query)

    best_docs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    best_docs_none_zero = []
    for d in best_docs:
        if scores[d] != 0:
            best_docs_none_zero.append(d)
    return best_docs_none_zero
