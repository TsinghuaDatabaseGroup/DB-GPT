import requests

model = "text-embedding-ada-002"
api_key = "xxx"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + api_key
}

if __name__ == '__main__':

    input_text = "The CPU usage is abnormal. Based on the three CPU relevant metric values, the load over the last 1 minute is less than 1, the load over the last 5 minutes is greater than 1, and the load over the last 15 minutes is greater than 1."

    # embed the key text into a vector

    response = requests.post('https://api.openai.com/v1/embeddings', json={"input": input_text, "model": model},
                             headers=headers)
    
    print(response.json())

    # store the embeddings to vector database


    # store the embedding and values into databas
    # 
    # 数据、工程bug、链路、