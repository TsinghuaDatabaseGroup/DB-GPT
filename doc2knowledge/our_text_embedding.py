from openai import OpenAI
import numpy as np
import json
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.decomposition import FastICA
from sklearn.decomposition import TruncatedSVD

from sklearn.feature_extraction.text import TfidfVectorizer

import matplotlib.pyplot as plt
import os
import requests
import time
import ast

texts = []
# with open('root_causes_dbmind.jsonl', 'r') as rf:
#     # convert the file content into list format
#     samples = json.load(rf)
#     for sample in samples:
#         texts.append({"cause_name": sample['cause_name'], "desc": sample['desc'], "metrics": sample['metrics']})

with open('./docs/case_guide/extracted_knowledge/extracted_knowledge_from_chunks.jsonl', 'r') as rf:
    # convert the file content into list format
    samples = json.load(rf)

    for sample_id in samples:
        texts.append({"cause_name": samples[str(sample_id)]['name'], "desc": samples[str(sample_id)]['content'], "steps": samples[str(sample_id)]['steps'], "metrics": str(samples[str(sample_id)]['metrics'])})

with open('./docs/overall_guide/extracted_knowledge/extracted_knowledge_from_chunks.jsonl', 'r') as rf:
    # convert the file content into list format
    samples = json.load(rf)
    for sample_id in samples:
        texts.append({"cause_name": samples[str(sample_id)]['name'], "desc": samples[str(sample_id)]['content'], "steps": samples[str(sample_id)]['steps'], "metrics": str(samples[str(sample_id)]['metrics'])})


existing_knowledge_dir = './docs/extracted_knowledge_chunks'
file_names = os.listdir(existing_knowledge_dir)

for i,file_name in enumerate(file_names):
    if "jsonl" in file_name:
        new_texts = []
        with open(existing_knowledge_dir+f'/{file_name}', 'r') as rf:
            prefix= file_name.split('.')[0]
            content = rf.read()
            content = content.split('\n\n')
            for text in content:
                if text == '':
                    continue
                
                text = text.strip()
                # json.loads(data_string.replace("'", "\"").replace("\\\"", "'"))
                try:
                    text = ast.literal_eval(text)
                except:
                    print(f"[invalid chunk] ({prefix})", text)
                for t in texts:
                    if text['content'] in t['desc']:
                        new_texts.append(t)
                        break
            
            # write new_texts into file in pretty format with json.dumps
            # print(f"prefix: {prefix}, num: {len(new_texts)}")
            # with open(f'./docs/knowledge_chunks/dbgpt_usage/{prefix}.jsonl', 'w') as wf:
            #     # write in list
            #     wf.write(json.dumps(new_texts, indent=4))


texts = []
labels = []
for i,file_name in enumerate(file_names):
    print(file_name)
    if "jsonl" in file_name:
        # read content split by '\n\n'
        with open(existing_knowledge_dir+f'/{file_name}', 'r') as rf:
            prefix= file_name.split('.')[0]
            content = rf.read()
            content = content.split('\n\n')
            for text in content:
                
                if text == '':
                    continue
                labels.append(i)
                text = text.strip()
                # json.loads(data_string.replace("'", "\"").replace("\\\"", "'"))
                try:
                    text = ast.literal_eval(text)
                except:
                    print(f"[invalid chunk] ({prefix})", text)
                    
                if prefix not in text['name']:
                    text['name'] = prefix + '_' + text['name']
                texts.append(text)

## add similar text (x1)
api_key = os.environ.get("OPENAI_API_KEY")
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + api_key
}
url = "https://api.aiaiapi.com/v1/chat/completions"

# if './embeddings_array.npy' not exists
# if not os.path.exists('./embeddings_array.npy'):

old_texts = []
for text in texts:
    old_texts.append(text)

print("total num: ", len(old_texts))

for i,text in enumerate(old_texts):

    prompt = f"Given the following knowledge block:\n{text['content']}\n\nGive a similar description of the knowledge block:\n"

    message = [{'role': 'user', 'content': prompt}]
    payload = {
        "model": "gpt-3.5-turbo-16k", # "gpt-4-1106-preview", # "gpt-3.5-turbo-16k",#"gpt-4-32k-0613",
        "messages": message,
        "temperature": 0.5,
        "max_tokens": 32,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": ["\n\n"]
    }

    timeout=10
    ok = 0
    while timeout>0:
        try:
            response = requests.post(url, json=payload, headers=headers)
            ok = 1
            break
        except Exception as e:
            time.sleep(.01)
            timeout -= 1
    
    if ok == 0:
        raise Exception("Failed to get response from API!")

    new_text = {}
    new_text['name'] = text['name']
    new_text['content'] = json.loads(response.text)["choices"][0]["message"]["content"]

    labels.append(labels[texts.index(text)])
    texts.append(text)

    print(f"enriched {i} text")
# import pdb; pdb.set_trace()


# Get embeddings for each text
api_key = os.environ.get("OPENAI_API_KEY")
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + api_key
}
url = "https://api.aiaiapi.com/v1/embeddings"

embeddings = []
for i,text in enumerate(texts):
    payload = {
        "input": [text["name"]],
        "model": "text-embedding-ada-002"        
    }

    timeout=10
    ok = 0
    while timeout>0:
        try:
            response = requests.post(url, json=payload, headers=headers)
            ok = 1
            break
        except Exception as e:
            time.sleep(.01)
            timeout -= 1
    
    if ok == 0:
        raise Exception("Failed to get response from API!")

    embedding = json.loads(response.text)['data'][0]['embedding']
    embeddings.append(embedding)
    print(f"embedded {i} text")

# Convert embeddings list to a NumPy array
embeddings_array = np.array(embeddings)
np.save('./embeddings_array.npy', embeddings_array)


# reload embeddings_array from file
embeddings_array = np.load('./embeddings_array.npy')
# import pdb; pdb.set_trace()
labels = labels + labels

svd = PCA(n_components=3)
reduced_embeddings = svd.fit_transform(embeddings_array)


# plt.figure(figsize=(10, 6))
# scatter = plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], c=labels, cmap='viridis', s=10)
# plt.title("Knowledge Clustering (Ada-002)")
# plt.colorbar(scatter)
# plt.xlabel("PCA 1")
# plt.ylabel("PCA 2")
# # save the figure
# plt.savefig('./knowledge_clustering.png')
# exit(1)

# Plotting in 3-D
fig = plt.figure(figsize=(10, 6))
fig.patch.set_facecolor('none')
ax = fig.add_subplot(projection='3d')
ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False
ax.grid(True, linestyle='dotted', linewidth=0.5, color='black')

scatter = ax.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], reduced_embeddings[:, 2], c=labels, cmap='viridis')

# plt.title("Knowledge Clustering (Ada-002)")
cbar = fig.colorbar(scatter, ax=ax, shrink=0.7)

#plt.colorbar(scatter)
ax.set_xlabel("SVD 1")
ax.set_ylabel("SVD 2")
ax.set_zlabel("SVD 3")

unique_labels = np.unique(labels)
label_names = ["index", "", "workload", "I/O", "writes", "memory", "", "CPU", "query", ""]

ax.text(-0.12357282, -0.02821038, -0.08682948, "index", fontsize=12, weight='bold', ha='center', va='center')
ax.text(0.24026489, -0.00548978, 0.10369949, "workload", fontsize=12, weight='bold', ha='center', va='center')
ax.text(-0.16701542, -0.0196591 ,  0.22820786, "I/O", fontsize=12, weight='bold', ha='center', va='center')
ax.text(-0.14342373, -0.06689665,  0.00210631, "writes", fontsize=12, weight='bold', ha='center', va='center')
ax.text(-0.15936546,  0.1986972 , -0.06664728, "memory", fontsize=12, weight='bold', ha='center', va='center')
ax.text(-0.11849676,  0.17963724, -0.004809, "CPU", fontsize=12, weight='bold', ha='center', va='center')
ax.text(-0.18277633, -0.22516701, -0.21521835, "query", fontsize=12, weight='bold', ha='center', va='center')

ax.set_xlim(-0.3, 0.2)
ax.set_ylim(-0.2, 0.45)
ax.set_zlim(-0.3, 0.2)

# for label in unique_labels:
#     centroid = np.mean(reduced_embeddings[labels == label], axis=0)
#     import pdb; pdb.set_trace()
#     ax.text(centroid[0], centroid[1], centroid[2], str(label_names[int(label)]), fontsize=12, weight='bold', ha='center', va='center')

# save the figure
plt.savefig('./knowledge_clustering_3d.png')
exit(1)


# root_causes_dbmind.jsonl
## read from the json file 
texts = []
with open('root_causes_dbmind.jsonl', 'r') as rf:
    # convert the file content into list format
    samples = json.load(rf)
    for sample in samples:
        texts.append({"name": sample['cause_name'], "content": sample['desc']})

with open('./docs/case_guide/extracted_knowledge/extracted_knowledge_from_chunks.jsonl', 'r') as rf:
    # convert the file content into list format
    samples = json.load(rf)
    for sample_id in samples:
        texts.append({"name": samples[str(sample_id)]['name'], "content": samples[str(sample_id)]['content']})
        

with open('./docs/overall_guide/extracted_knowledge/extracted_knowledge_from_chunks.jsonl', 'r') as rf:
    # convert the file content into list format
    samples = json.load(rf)
    for sample_id in samples:
        texts.append({"name": samples[str(sample_id)]['name'], "content": samples[str(sample_id)]['content']})

# Your OpenAI client setup
api_key = os.environ.get("OPENAI_API_KEY")
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + api_key
}
url = "https://api.aiaiapi.com/v1/embeddings"

# Get embeddings for each text
# embeddings = []
# for text in texts:
#     payload = {
#         "input": [text["name"]],
#         "model": "text-embedding-ada-002"        
#     }

#     timeout=10
#     ok = 0
#     while timeout>0:
#         try:
#             response = requests.post(url, json=payload, headers=headers)
#             ok = 1
#             break
#         except Exception as e:
#             time.sleep(.01)
#             timeout -= 1
    
#     if ok == 0:
#         raise Exception("Failed to get response from API!")

#     embedding = json.loads(response.text)['data'][0]['embedding']
#     embeddings.append(embedding)

# # Convert embeddings list to a NumPy array
# embeddings_array = np.array(embeddings)

# # save embeddings_array to file
# np.save('./embeddings_array.npy', embeddings_array)

# reload embeddings_array from file
embeddings_array = np.load('./embeddings_array.npy')

# enrich embeddings_array with more similar embeddings with noises
# from sklearn.neighbors import NearestNeighbors
# neigh = NearestNeighbors(n_neighbors=2)
# neigh.fit(embeddings_array)
# distances, indices = neigh.kneighbors(embeddings_array)
# print(indices)
# print(distances)
## add more similar embeddings (for each embedding, add 10 nearby embeddings) with noises (distances) into embeddings_array

# for i in range(len(indices)):
#     for j in range(10):
#         embeddings_array = np.append(embeddings_array, [embeddings_array[indices[i][1]] + np.random.normal(0, distances[i][1], embeddings_array[0].shape)], axis=0)

'''
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(texts)

'''

# for eps in np.arange(.5, .7, 0.001):
#     for min_samples in range(2, 5):
#         dbscan = DBSCAN(eps=eps, min_samples=min_samples)
#         dbscan.fit(embeddings_array)
#         labels = dbscan.labels_
#         n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
#         # and the number of label -1 is lower than 50
#         if n_clusters_ > 1 and n_clusters_ <= 8 and len(np.where(labels==-1)[0]) < 50:
#             print(f"eps: {eps}, min_samples: {min_samples}")
#             unique, counts = np.unique(labels, return_counts=True)
#             print(dict(zip(unique, counts)))
# exit(1)

# eps: 0.53, min_samples: 4
# eps: 0.531, min_samples: 4

dbscan = DBSCAN(eps=0.5180000000000003, min_samples=3)
dbscan.fit(embeddings_array)
labels = dbscan.labels_

# for each cluster, save the corresponding texts within a file
for i in range(len(set(labels))):
    with open(f'./docs/knowledge_chunks/cluster_{i}.jsonl', 'w') as wf:
        for j in range(len(labels)):
            if labels[j] == i:
                wf.write(str(texts[j]) + '\n\n')

# Dimensionality reduction for visualization
svd = PCA(n_components=3)
reduced_embeddings = svd.fit_transform(embeddings_array)

# the number of lables
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

print(f"Number of clusters: {n_clusters_}")

# the number of elements in each cluster
unique, counts = np.unique(labels, return_counts=True)
print(dict(zip(unique, counts)))

# Plotting in 3-D
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(projection='3d')
scatter = ax.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], reduced_embeddings[:, 2], c=labels, cmap='viridis')
plt.title("Knowledge Clustering (Ada-002)")
plt.colorbar(scatter)
ax.set_xlabel("PCA 1")
ax.set_ylabel("PCA 2")
ax.set_zlabel("PCA 3")
# save the figure
plt.savefig('./knowledge_clustering_3d.png')

# plt.figure(figsize=(10, 6))
# scatter = plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], c=labels, cmap='viridis')
# plt.title("Knowledge Clustering (Ada-002)")
# plt.colorbar(scatter)
# plt.xlabel("PCA 1")
# plt.ylabel("PCA 2")
# # save the figure
# plt.savefig('./knowledge_clustering.png')