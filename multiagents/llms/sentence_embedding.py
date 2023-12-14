import logging
import os
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from multiagents.llms.base import LLMResult
from . import llm_registry
import requests
import json
import aiohttp
import asyncio
import time
import random
import re
from termcolor import colored
from tqdm import tqdm
from openai import OpenAI
import pickle

from sentence_transformers import SentenceTransformer


#def sentence_embedding(sentence: str, model: str = "text-embedding-ada-002"):
def sentence_embedding(sentence: str, model: str = "sentence-transformer"):

    if model == "sentence-transformer":

        model_path = './localized_llms/sentence_embedding/sentence-transformer/'
        try:
            embedder = SentenceTransformer(model_path)
        except FileNotFoundError:
            # load from remote
            embedder = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

        embedding = embedder.encode([sentence], convert_to_tensor=True)[0]

    elif model == "text-embedding-ada-002":
        api_key = os.environ.get("OPENAI_API_KEY")

        client = OpenAI(api_key=api_key)
        timeout=10
        ok = 0
        while timeout>0:
            try:
                response = client.embeddings.create(input=[sentence], model=model)
                ok = 1
                break
            except Exception as e:
                time.sleep(.01)
                timeout -= 1

        if ok == 0:
            raise Exception("Failed to get response from API!")
        
        embedding = response.data[0].embedding

        # payload = {
        #     "input": [sentence],
        #     "model": model
        # }
        # url = "https://api.aiaiapi.com/v1/embeddings"
        # headers = {
        #     "Content-Type": "application/json",
        #     "Authorization": "Bearer " + api_key
        # }

        # timeout=10
        # ok = 0
        # while timeout>0:
        #     try:
        #         response = requests.post(url, json=payload, headers=headers)
        #         ok = 1
        #         break
        #     except Exception as e:
        #         time.sleep(.01)
        #         timeout -= 1
        
        # if ok == 0:
        #     raise Exception("Failed to get response from openai API!")

        # embedding = json.loads(response.text)['data'][0]['embedding']
        
    return embedding
