<div align= "center">
    <h1> <img src="img/dbagent.png" width="100px"> LLM As Database Administrator</h1>
</div>

<!-- <p align="center">
    <a href="https://github.com/TsinghuaDatabaseGroup/DB-GPT/blob/main/LICENSE">
        <img alt="License: Apache2" src="https://img.shields.io/badge/License-Apache_2.0-green.svg">
    </a>
    <a href="https://github.com/OpenBMB/AgentVerse/blob/main/LICENSE">
        <img alt="License: Apache2" src="https://img.shields.io/badge/License-Apache_2.0-green.svg">
    </a>
</p> -->

<div align="center">

<a href="https://github.com/TsinghuaDatabaseGroup/DB-GPT/tree/main/anomalies/public_testing_set/all_anomalies.jsonl">![Dialogues](https://img.shields.io/badge/Anomalies-539-red?style=flat-square)</a>
<a href="https://github.com/TsinghuaDatabaseGroup/DB-GPT/tree/main/multiagents/tools">![Dialogues](https://img.shields.io/badge/Tool\_APIs-60+-red?style=flat-square)</a>
<a href="https://github.com/TsinghuaDatabaseGroup/DB-GPT/tree/main/localized_llms/training_data">![Dialogues](https://img.shields.io/badge/Training\_Data-2813-red?style=flat-square)</a>
<a href="https://cloud.tsinghua.edu.cn/f/6e8a3ad547204303a5ae/?dl=1">![Dialogues](https://img.shields.io/badge/Local\_Text\_Embed-1-red?style=flat-square)</a>
<a href="https://github.com/TsinghuaDatabaseGroup/DB-GPT/tree/main/multiagents/llms">![Dialogues](https://img.shields.io/badge/Local\_LLMs-3-red?style=flat-square)</a>

</div>


<!-- <div align="center">
  <a href="https://github.com/TsinghuaDatabaseGroup/DB-GPT/tree/main/localized_llms">
    <em style="color: red;">DiagLLM</em> 
  </a> 🔥
</div> -->

<p align="center">
  <!-- <a href="#-features">Features</a> • -->
  <a href="#-demo">Demo</a> •
  <a href="#-quickstart">QuickStart</a> •
  <a href="#-anomalies">Alerts And Anomalies</a> •  
  <a href="#-customize">Knowledge And Tools</a> • 
  <a href="#-FAQ">FAQ</a> •  
  <a href="#-community">Community</a> •  
  <a href="#-citation">Citation</a> •    
  <a href="#-contributors">Contributors</a>
</p>

<p align="center">
<a href="#-contact">👫 Join Us on WeChat!</a> <bar> <a href="https://www.benchcouncil.org/evaluation/opencs/annual.html#Achievements">🏆 Top 100 Open Project!</a>
</p>

<p align="center">
    【English | <a href="README_Chinese11-7_update.md">中文</a>】
</p>


<p align="center">
    <img src="img/overview_v3.png" width="800px">
</p>

🦾 Build your personal database administrator (D-Bot)🧑‍💻, which is good at *reading documents, using various tools, writing analysis reports!* 

**An important, major version update is coming soon, stay tuned!** 📣 🔜



<!-- >Besides, to extend the database maintenance capability, we are also finetuning LLMs to support localized diagnosis, *query rewriting* and *anomaly simulation* (comming soon). -->


<span id="-demo"></span>

## 🗺 Online Demo

In the online website ([http://dbgpt.dbmind.cn](http://dbgpt.dbmind.cn)), you can browse all the historical diagnosis results, used metrics, and the detailed diagnosis processes.

<p align="center">
  <a href="http://dbgpt.dbmind.cn">
    <img src="img/frontend_v2_1.png" width="800px" alt="frontend_v2">
  </a>
</p>


<p align="center">
  <a href="http://dbgpt.dbmind.cn">
    <img src="img/frontend_v2_2.png" width="800px" alt="frontend_v2">
  </a>
</p>

<p align="center">
  <a href="./assets/dbot2_v2.gif">Demo Video</a>
</p>

Here is the [Old Version](https://github.com/TsinghuaDatabaseGroup/DB-GPT/tree/old_version) of D-Bot.

<span id="-news"></span>

## 📰 Updates

- [ ] Extreme Speed Version for localized llms

- [x] 8 new expert roles by the clustering of extracted *Knowledge*

- [x] Upgrade the LLM-based diagnosis mechanism: 

    * [x] *Task Dispatching -> Concurrent Diagnosis -> Cross Review -> Report Generation*

- [x] Add typical anomalies and alerts (Pigsty) <a href="#-anomalies">🔗 link</a>

<!-- - [x] An end-to-end framework is available! <a href="#-diagnosis">🚀 link</a> -->

<!-- - [x] **[2023/8/25]** Support vue-based website interface. More flexible and beautiful! <a href="#-frontend">🔗 link</a> -->

- [ ] Support monitoring and optimization tools in multiple levels [🔗 link](multiagents/tools)

    * [x] Monitoring metrics (Prometheus)
    * [ ] Flame graph in code level
    * [x] Diagnosis knowledge retrieval (dbmind)
    * [x] Logical query transformations (Calcite)
    * [x] Index optimization algorithms (for PostgreSQL)
    * [x] Physical operator hints (for PostgreSQL)
    * [ ] Backup and Point-in-time Recovery (Pigsty)


- [x] Papers and experimental reports are continuously updated

    * *D-Bot: Database Diagnosis System using Large Language Models.* [[paper]](https://arxiv.org/pdf/2312.01454.pdf)

    * *LLM As DBA.* [[vision]](https://arxiv.org/abs/2308.05481) [[中文解读]](https://mp.weixin.qq.com/s/i0-Fdde7DX9YE1jACxB9_Q) [[twitter]](https://twitter.com/omarsar0/status/1689811820272353280?s=61&t=MlkXRcM6bNQYHnTIQVUmVw) [[slides]](materials/slides)

    * *DB-GPT: Large Language Model Meets Database.* [[vision]](http://dbgroup.cs.tsinghua.edu.cn/ligl/papers/dbgpt-dse.pdf)

> This project is evolving with new features 👫👫<br/> 
> Don't forget to star ⭐ and watch 👀 to stay up to date :)



<span id="-quickstart"></span>

## 🕹 QuickStart

## Quick Start

### Environment Setup

First, make sure your machine has Python 3.10 installed.

```
$ python --version
Python 3.10.12
```

Then, create a virtual environment and install the project's dependencies within the virtual environment.

```shell

# Clone Code
$ git clone https://github.com/TsinghuaDatabaseGroup/DB-GPT.git

# cd directory
$ cd Langchain-Chatchat

# install dependencies
$ pip3 install -r requirements.txt 
$ pip3 install -r requirements_api.txt # if you just want to use the API, please install requirements_api.txt

# The default dependency includes the base runtime environment (Chroma-DB vector library). If you want to use other vector libraries, uncomment the corresponding dependencies in requirements.txt before installing them.

# If you want to run the Web UI, you also need to install the dependency packages in the front-end project. Here the UI is more complicated, so I wrote a separate front page using VUE.
cd webui_pages/reports/reports_ui
rm -rf node_modules/
rm -r package-lock.json
# First run installation dependencies (nodejs recommended, ^16.13.1)
npm install  --legacy-peer-deps
npm install -g cross-env
```

### Model Download

If you need to run this project locally or in an offline environment, you must first download the required models for
the project. Typically, open-source LLM and Embedding models can be downloaded from HuggingFace.

To download the models, you need to first
install [Git LFS](https://docs.github.com/zh/repositories/working-with-files/managing-large-files/installing-git-large-file-storage)
and then run:

```Shell
$ git lfs install
$ git clone https://huggingface.co/moka-ai/m3e-base
```

### Initializing the Knowledge Base and Config File

Follow the steps below to initialize your own knowledge base and config file:

```shell
$ python copy_config_example.py
# The generated configuration file is in the configs/ directory
# basic_config.py is the base configuration file and does not need to be modified
# diagnose_config.py is a diagnostic profile that needs to be modified to fit your environment.
# kb_config.py is the configuration file of the knowledge base. You can modify DEFAULT_VS_TYPE to specify the storage vector library of the knowledge base, or modify the related path.
# model_config.py is the model configuration file, you can modify LLM_MODELS to specify the model to use, the current model configuration is mainly for knowledge base search, diagnostic related models and some hard-coded code, will be unified here later.
# prompt_config.py is a prompt configuration file, which is mainly prompt for LLM conversations and knowledge bases.
# server_config.py is the service configuration file, mainly the port number of the service, etc.
```
Init Database
```shell
$ python init_database.py --recreate-vs
 ```

### One-Click Launch

To start the project, run the following command:

```shell
$ python startup.py -a
```

### Example of Launch Interface

1. FastAPI docs interface

![](img/fastapi_docs_026.png)

2. webui page

- Web UI dialog page:

![img](img/LLM_success.png)

- Web UI knowledge base management page:

![](img/init_knowledge_base.jpg)

- Web UI Reports page：

![](img/db-gpt-report.png)


### Diagnosis Side

<span id="-prerequisites"></span>

#### 1. Prerequisites

- PostgreSQL v12 (Our development tests are based on PostgreSQL v12 and we do not guarantee compatibility with other versions of PostgreSQL.)

    > Make sure your database supports remote connection ([link](https://support.cpanel.net/hc/en-us/articles/4419265023383-How-to-enable-remote-PostgreSQL-access))

    > Additionally, install extensions like *[pg_stat_statements](https://pganalyze.com/docs/install/01_enabling_pg_stat_statements)* (track frequent queries), *[pg_hint_plan](https://pg-hint-plan.readthedocs.io/en/latest/installation.html)* (optimize physical operators), and *[hypopg](https://github.com/HypoPG/hypopg)* (create hypothetical Indexes).

    > Note *pg_stat_statements* continuosly accumulate query statistics over time. So you need to clear the statistics from time to time: 1) To discard all the statistics, execute *"SELECT pg_stat_statements_reset();"*; 2) To discard the statistics of specific query, execute *"SELECT pg_stat_statements_reset(userid, dbid, queryid);"*.

- Enable slow query log in PostgreSQL ([link](https://ubiq.co/database-blog/how-to-enable-slow-query-log-in-postgresql/))

    > (1) For *"systemctl restart postgresql"*, the service name can be different (e.g., postgresql-12.service); 
    
    > (2) Use absolute log path name like *"log_directory = '/var/lib/pgsql/12/data/log'"*; 
    
    > (3) Set *"log_line_prefix = '%m [%p] [%d]'"* in postgresql.conf (to record the database names of different queries).

- Prometheus

    > Check [prometheus.md](materials/help_documents/prometheus.md) for detailed installation guides.
  

Step 1: Download [Sentence Trasformer](https://cloud.tsinghua.edu.cn/f/6e8a3ad547204303a5ae/?dl=1) model parameters

- Create new directory ./multiagents/localized_llms/sentence_embedding/

- Move the downloaded sentence-transformer.zip to ./multiagents/localized_llms/sentence_embedding/ directory, and unzip it.

#### 2. Generate New Diagnosis Report

- Test single case

```shell
python3 run_diagnosis.py --anomaly_file ./diagnostic_files/testing_cases_5.json
```


<span id="-anomalies"></span>

## 🎩 Alerts And Anomalies

### Alert Management

We support AlertManager for Prometheus. You can find more information about how to configure alertmanager here: [alertmanager.md](https://prometheus.io/docs/alerting/latest/configuration/).

- We provide AlertManager-related configuration files, including [alertmanager.yml](./prometheus_service/alertmanager.yml), [node_rules.yml](prometheus_service/node_rules.yml), and [pgsql_rules.yml](prometheus_service/pgsql_rules.yml), which you can deploy to your Prometheus server to retrieve the associated exceptions.
- We also provide servers that support getting alerts and metrics, which you can deploy to your server to get and store Prometheus alerts and TOP metrics for the corresponding time period. You can get this information at prometheus_service.- Currently, the alert file is obtained using SSh. You need to configure your server information in the [diagnose_config.py](./configs/diagnose_config.py) in the config folder.
- [node_rules.yml](prometheus_service/node_rules.yml) and [pgsql_rules.yml](prometheus_service/pgsql_rules.yml) is a reference https://github.com/Vonng/pigsty code in this open source project, their monitoring do very well, thank them for their effort.


### Anomaly Simulation

#### Script-Triggered Anomalies

We offer scripts that could incur typical anomalies. Check out different anomaly cases in [http://dbgpt.dbmind.cn](http://dbgpt.dbmind.cn)

| Root Cause          | Description                                           | Potential Alerts                 |
|---------------------|-------------------------------------------------------|----------------------|
| INSERT_LARGE_DATA    | Long execution time for large data insert         |    ![](https://img.shields.io/badge/-NodeOutOfMem-informational)   |
| FETCH_LARGE_DATA    | Long execution time for large data fetch           |   ![](https://img.shields.io/badge/-NodeLoadHigh-Informational)   |
| REDUNDANT_INDEX      | Unnecessary and redundant indexes in tables           |  ![](https://img.shields.io/badge/-NodeLoadHigh-Informational)     |
| VACUUM              |       Unused space caused by data modifications       |  ![](https://img.shields.io/badge/-NodeOutOfMem-informational)    |
| POOR_JOIN_PERFORMANCE | Poor performance of join operators                  |   ![](https://img.shields.io/badge/-NodeLoadHigh-Informational)    |
| CORRELATED_SUBQUERY | Non-promotable subqueries in SQL statements                      |     ![](https://img.shields.io/badge/-NodeLoadHigh-Informational),![](https://img.shields.io/badge/-PostgresDown-red) |
| LOCK_CONTENTION     | Lock contention issues                                |  ![](https://img.shields.io/badge/-NodeCpuHigh-Informational) ![](https://img.shields.io/badge/-PostgresRestart-red) |
| CPU_CONTENTION      | Severe CPU resource contention               |   ![](https://img.shields.io/badge/-NodeLoadHigh-Informational)   |
| IO_CONTENTION       | IO resource contention affecting SQL performance      |   ![](https://img.shields.io/badge/-NodeLoadHigh-Informational) ![](https://img.shields.io/badge/-NodeOutOfMem-informational)      |
| COMMIT_CONTENTION | Highly concurrent commits affecting SQL execution        |   ![](https://img.shields.io/badge/-NodeLoadHigh-Informational) ![](https://img.shields.io/badge/-NodeOutOfMem-informational)   |
| SMALL_MEMORY_ALLOC    | Too small allocated memory space              |                      |


#### Manually Designed Anomalies

*[Click to check 29 typical anomalies together with expert analysis](./anomaly_trigger/29种性能异常与根因分析.pdf) (supported by the DBMind team)*


<span id="-customize"></span>

## 📎 Customize Knowledge And Tools

<span id="-doc2knowledge"></span>

### 1. Knowledge Extraction 

(Basic version by [Zui Chen](https://scholar.google.com/citations?user=WJdZtGAAAAAJ&hl=en))

Step 1. Rename *doc2knowledge/config_template.json* into *doc2knowledge/config.json*. And add the value for "api_key" ("organization" is optional)

> GPT-4 is necessary to utilize the *function calling* feature. I will try to solve this limit.

Step 2. Split documents into separated section files by the section indexes (e.g., section1, section1.1, section2 ...). And copy the section files into the *docs/<your_document_name>/raw/*. For example:

    .
    ├── docs
    │   ├── report_example
    |   │   ├── raw    
    |   │   |    ├── 1 title.txt    
    |   │   |    ├── 1.1 category.txt

> It is a laborious work and hard to find a better way than manually splitting the given document

> You can jump over this step and directly run the *report_example* case

Step 3. Modify the arguments in *doc2knowledge.py* script and run the script:

```bash
cd doc2knowledge/
python doc2knowledge.py
```

> The summary for the same document sections is cached. You can delete this file if do not like to reuse the previous caches.

Step 4. With the extracted knowledge, you can visualize their clustering results:

```bash
cd doc2knowledge/
python knowledge_clustering.py
```


<span id="-tools"></span>

### 2. Tool Preparation

- Tool APIs (for optimization)

    | Module                  | Functions |
    |-------------------------|-----------|
    | [index_selection](multiagents/tools/index_advisor) (equipped)          | *heuristic* algorithm  |
    | [query_rewrite](multiagents/tools/query_advisor) (equipped)           | *45* rules  |
    | [physical_hint](multiagents/tools/query_advisor) (equipped)           | *15* parameters  |

    For functions within [[query_rewrite](multiagents/tools/query_advisor), [physical_hint](multiagents/tools/query_advisor)], you can use *api_test.py* script to verify the effectiveness. 

    If the function actually works, append it to the *api.py* of corresponding module.


<span id="-FAQ"></span>

## 💁 FAQ

<details><summary><b>🤨 The '.sh' script command cannot be executed on windows system.</b></summary>
Switch the shell to *git bash* or use *git bash* to execute the '.sh' script.
</details>

<details><summary><b>🤨 "No module named 'xxx'" on windows system.</b></summary>
This error is caused by issues with the Python runtime environment path. You need to perform the following steps:

Step 1: Check Environment Variables.

<div align="center">
<img src="img/faq2.png" width="800px">
</div>

You must configure the "Scripts" in the environment variables.

Step 2: Check IDE Settings.

For VS Code, download the Python extension for code. For PyCharm, specify the Python version for the current project.
</details>


## ⏱ Todo

- ~~Project cleaning~~
- ~~Support more anomalies~~
- ~~Support more knowledge sources~~
- ~~Query log option (potential to take up disk space and we need to consider it carefully)~~
- ~~Add more communication mechanisms~~
- ~~Localized model that reaches D-bot(gpt4)'s capability~~
- Project engineering, solving dependency problems and hard-coding problems in code
- Localized llms that are tailored with domain knolwedge and can generate precise and straigtforward analysis.
- Support other databases (e.g., mysql/redis)


<span id="-community"></span>

## 👫 Community

- [Tsinghua University](https://www.tsinghua.edu.cn/en/)
- [ModelBest](https://modelbest.cn/)


<span id="-projects"></span>

## 🤗 Relevant Projects

https://github.com/OpenBMB/AgentVerse

https://github.com/Vonng/pigsty

https://github.com/UKPLab/sentence-transformers


<span id="-citation"></span>

## 📒 Citation
Feel free to cite us ([paper link](https://arxiv.org/pdf/2312.01454.pdf)) if you like this project.

```bibtex
@misc{zhou2023llm4diag,
      title={D-Bot: Database Diagnosis System using Large Language Models}, 
      author={Xuanhe Zhou, Guoliang Li, Zhaoyan Sun, Zhiyuan Liu, Weize Chen, Jianming Wu, Jiesi Liu, Ruohang Feng, Guoyang Zeng},
      year={2023},
      eprint={2312.01454},
      archivePrefix={arXiv},
      primaryClass={cs.DB}
}
```


```bibtex
@misc{zhou2023dbgpt,
      title={DB-GPT: Large Language Model Meets Database}, 
      author={Xuanhe Zhou, Zhaoyan Sun, Guoliang Li},
      year={2023},
      archivePrefix={Data Science and Engineering},
}
```

<span id="-contributors"></span>

## 📧 Contributors

<!-- Copy-paste in your Readme.md file -->

<a href="https://github.com/TsinghuaDatabaseGroup/DB-GPT/network/dependencies">
  <img src="https://contrib.rocks/image?repo=TsinghuaDatabaseGroup/DB-GPT" />
</a>

Other Collaborators: [Wei Zhou](https://github.com/Beliefuture), [Kunyi Li](https://github.com/LikyThu).

The project framework is based on [Langchain-Chatchat] (https://github.com/chatchat-space/Langchain-Chatchat), thanks to their open source!

We thank all the contributors to this project. Do not hesitate if you would like to get involved or contribute! 

<span id="-contact"></span>

## Contact Information
👏🏻Welcome to our wechat group!
<div align= "center">
<img src="img/group.png" width="400px">
</div>

<!-- ## ⭐️ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=TsinghuaDatabaseGroup/DB-GPT&type=Date)](https://star-history.com/#TsinghuaDatabaseGroup/DB-GPT&Date) -->

