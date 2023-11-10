# DiagLlama
We collect GPT-4 responses during DB-GPT diagnosis processes, and fine-tune [Llama2-13B](https://huggingface.co/meta-llama/Llama-2-13b) with them.
## 🗺 Demo
A demo of comparing diagnosis performance of <font color=magenta>GPT-4</font> and our <font color=cyan>DiagLlama</font>:

<div align="center">

<img src="../assets/demo.gif" width="700px">

</div>

## 🕹 QuickStart

Step 1: Install python packages.

```bash
pip install -r requirements.txt
```

Step 2: Download Pretrained Model Parameters from https://huggingface.co/curtis-sun/DiagLlama/tree/main.

Step 3: Pass File Paths to [inference.py](inference.py):

```Python
class DiagLlamaArgs(BaseModel):
    load: str = Field(default="xxxx/DiagLlama.pt")
    model_config: str = Field(default="xxxx/llama2-13b/config.json")
    vocab: str = Field(default="xxxx/llama2-13b")
```

Replace 'xxxx' with download path.

Step 4: Configure Agents Equipped with DiagLLama:

Rename [config_diag_llama.yaml](../multiagents/agent_conf/config_diag_llama.yaml) to be 'config.yaml'.

Then run the project the same as with OpenAI APIs.