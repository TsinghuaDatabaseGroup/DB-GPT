# Localized D-Bot
We record the diagnosis processes of D-Bot(GPT-4), and fine-tune LLMs to simulate the corresponding D-Bot(GPT-4) response (after cleaned). We fine-tune three localized LLMs, i.e., [Llama 2-13B](https://huggingface.co/meta-llama/Llama-2-13b), [CodeLlama-13B](https://github.com/facebookresearch/codellama), [Baichuan2-13B](https://github.com/baichuan-inc/Baichuan2). 
## 🗺 Demo
A demo of comparing diagnosis performance of <font color=magenta>D-Bot(GPT-4)</font> and our <font color=cyan>Localized D-Bot</font>:

<div align="center">

<img src="../assets/demo.gif" width="700px">

</div>

## 🕹 QuickStart

(optional) Step 1: Download Pretrained Model Parameters: 
* [diag-baichuan2](https://huggingface.co/curtis-sun/diag-baichuan2/tree/main), fine-tuned from Baichuan2-13B
* [diag-baichuan2-4bit](https://huggingface.co/curtis-sun/diag-baichuan2-4bit/tree/main), a 4bit version of diag-baichuan2
* [diag-codellama](https://huggingface.co/curtis-sun/diag-codellama/tree/main), fine-tuned from CodeLlama-13B
* [diag-llama2](https://huggingface.co/curtis-sun/diag-llama2/tree/main), fine-tuned from Llama2-13B

You may also require to replace the ``load'' argument in [inference.py](inference.py) with your download path, e.g., 
```Python
class DiagBaichuan2Args(BaseModel):
    load: str = Field(default="curtis-sun/diag-baichuan2")
```

Step 2: Configure Agents Equipped with localized LLM, e.g., rename [config_diag-baichuan2-4bit.yaml](../agent_conf/config_diag-baichuan2-4bit.yaml) as config.yaml.

Then run the project the same as with OpenAI APIs.