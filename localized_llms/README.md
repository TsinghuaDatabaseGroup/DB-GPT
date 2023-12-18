# Localized D-Bot
We record the diagnosis processes of D-Bot(GPT-4), and fine-tune LLMs to simulate the corresponding D-Bot(GPT-4) response (after cleaned). We fine-tune three localized LLMs, i.e., [Llama 2-13B](https://huggingface.co/meta-llama/Llama-2-13b), [CodeLlama-13B](https://github.com/facebookresearch/codellama), [Baichuan2-13B](https://github.com/baichuan-inc/Baichuan2). 
## 🗺 Demo
A demo of comparing diagnosis performance of <font color=magenta>D-Bot(GPT-4)</font> and our <font color=cyan>Localized D-Bot</font>:

<div align="center">

<img src="../assets/demo.gif" width="700px">

</div>

## 🕹 QuickStart

Step 1: Install python packages.

```bash
pip install -r requirements.txt
```

Step 2: Download Pretrained Model Parameters from https://huggingface.co/curtis-sun/D-Bot/tree/main.

Step 3: Pass File Paths to [inference.py](inference.py):

```Python
class DiagBaichuan2Args(BaseModel):
    load: str = Field(default="xxxx/baichuan2-13b/diag-baichuan2.pt")
    model_config: str = Field(default="xxxx/baichuan2-13b/config.json")
    vocab: str = Field(default="xxxx/baichuan2-13b")
```

Replace 'xxxx' with download path.

Step 4: Configure Agents Equipped with diag-baichuan2:

Rename [config_diag_baichuan2.yaml](../multiagents/agent_conf/config_diag_baichuan2.yaml) to be 'config.yaml'.

Then run the project the same as with OpenAI APIs.