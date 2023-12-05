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

existing_knowledge_dir = './docs/extracted_knowledge_chunks'
embedding_file_name = './embeddings_array_v2.npy'
file_names = os.listdir(existing_knowledge_dir)

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


if not os.path.exists(embedding_file_name):

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
    np.save(embedding_file_name, embeddings_array)
else:
    # reload embeddings_array from file
    embeddings_array = np.load(embedding_file_name)


svd = PCA(n_components=3)
reduced_embeddings = svd.fit_transform(embeddings_array)

# Plotting in 3-D
fig = plt.figure(figsize=(10, 6))
fig.patch.set_facecolor('none')
ax = fig.add_subplot(projection='3d')
ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False
ax.grid(True, linestyle='dotted', linewidth=0.5, color='black')


import pdb; pdb.set_trace()
scatter = ax.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], reduced_embeddings[:, 2], c=labels, cmap='viridis')

# plt.title("Knowledge Clustering (Ada-002)")
cbar = fig.colorbar(scatter, ax=ax, shrink=0.7)

#plt.colorbar(scatter)
ax.set_xlabel("PCA 1")
ax.set_ylabel("PCA 2")
ax.set_zlabel("PCA 3")

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

plt.savefig('./knowledge_clustering_3d.png')

