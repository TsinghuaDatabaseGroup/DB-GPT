<div align= "center">
    <h1> LLM As Database Administrator</h1>
</div>

<p align="center">
  <a href="#-news">News</a> •
  <a href="#-features">Features</a> •
  <a href="#-quickstart">QuickStart</a> •
  <a href="#-cases">Cases</a> •
  <a href="#-community">Community</a> •  
  <a href="#-projects">Relevant Projects</a>
</p>


<br>
<div align="center">
<img src="imgs/demo_example.png" width="400px">
</div>
<br>


🧗 Database administrators (DBAs) play a crucial role in managing, maintaining and optimizing a database system to ensure data availability, performance, and reliability. However, it is hard and tedious for DBAs to manage a large number of database instances. Thus, we propose *D-Bot*, a LLM-based database administrator that can acquire database maintenance experience from textual sources, and provide **reasonable**, **well-founded**, **in-time** diagnosis and optimization advice for target databases.


<span id="-news"></span>

## What's New
- **[2023/8/13]** Support [**optimization functions**] during diagnosis.

- **[2023/8/10]** Our [**vision paper**](https://arxiv.org/abs/2308.05481) is released.


<span id="-features"></span>

## Features
- **Well-Founded Diagnosis**: D-Bot can provide founded diagnosis by utilizing relevant database knoweledge (with *document2experience*).

- **Practical Tool Utilization**: D-Bot can utilize both monitoring and optimization tools to improve the maintenance capability (with *tool learning* and *tree of thought*).

- **In-depth Reasoning**: Compared with vanilla LLMs, D-Bot will achieve competitive reasoning capability to analyze root causes (with *multi-llm communications*).

<br>
<div align="center">
<img src="imgs/overview.png" width="800px">
</div>
<br>


**A demo of using D-Bot**

https://github.com/OpenBMB/AgentVerse/assets/11704492/c633419d-afbb-47d4-bb12-6bb512e7af3a


<span id="-quickstart"></span>

## QuickStart

> Current version is developed from agentverse and bmtools, to which we previously contributed.

<br>
<div align="center">
<img src="imgs/workflow.png" width="800px">
</div>
<br>

### Prerequisites

- PostgreSQL v12 or higher

    Add database settings into [config.ini](tool_learning/bmtools/bmtools/tools/db_diag/config.ini) and rename into *my_config.ini*:

    ```bash
    [postgresql]
    host = xxx.xxx.xxx.xxx
    port = 5432
    user = xxx
    password = xxx
    dbname = postgres
    ```

    > Additionally, install extensions like *[pg_stat_statements](https://pganalyze.com/docs/install/01_enabling_pg_stat_statements)* (track slow queries) and *[pg_hint_plan](https://pg-hint-plan.readthedocs.io/en/latest/installation.html)* (optimize physical operators)

- Prometheus and Grafana ([tutorial](https://grafana.com/docs/grafana/latest/getting-started/get-started-grafana-prometheus/))



### Installation

Step1: Install python packages.

```bash
pip install -r requirements.txt
```

Step2: Configure environment variables.

- Export your OpenAI API key
```bash
# Export your OpenAI API key
export OPENAI_API_KEY="your_api_key_here"
```

- If accessing openai service via vpn, execute this command:
```bash
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 all_proxy=socks5://127.0.0.1:7890
```

### Preparation

#### Diagnosis Knowledge

- Extract knowledge from both code (./knowledge_json/knowledge_from_code) and documents (./knowledge_json/knowledge_from_document).

    - Add code blocks into [diagnosis_code.txt](./knowledge_json/knowledge_from_code/scripts/diagnosis_code.txt) file -> Rerun the *extract_knowledge.py* script -> Check the update results and sync to [root_causes_dbmind.jsonl](./tool_learning/bmtools/bmtools/tools/db_diag/root_causes_dbmind.jsonl).


#### Tool Usage

- Extract dozens of tool APIs to carry out different optimization functions (./tool_learning/tool_apis/).

    - Check the update results and sync to [api.py](./tool_learning/bmtools/bmtools/tools/db_diag/api.py).

- Start bmtools service (kept alive for <a href="#-tot">*tree of thought*</a> and <a href="#-diagnosis">*diagnosis*</a>).

```bash
cd tool_learning/bmtools
python host_local_tools.py
```

<span id="-tot"></span>

- Test tool utilization with *tree of thought* algorithm.

```bash
cd tool_learning/tree_of_thought
python test_database.py
```

> History messages may take up many tokens, and so carefully decide the *turn number*.

### Anomaly Generation & Detection

Within the *anomaly_scripts* directory, we offer scripts that could incur typical anomalies, e.g., 

(1) ./run_benchmark_tpcc.sh or ./run_db_exception.sh

    Example Anomalies: INSERT_LARGE_DATA, IO_CONTENTION

<details><summary><b>monitoring dashboard</b></summary>
<br>
<div align="center">
<img src="imgs/insert.png" width="800px">
</div>
<br>
</details>
  
---

(2) ./run_benchmark_job.sh

    Example Anomalies: POOR_JOIN_PERFORMANCE, CPU_CONTENTION


<details><summary><b>monitoring dashboard</b></summary>
<br>
<div align="center">
<img src="imgs/join.png" width="800px">
</div>
<br>
</details>

---

(3) ./run_benchmark_tpch.sh

    Example Anomalies: FETCH_LARGE_DATA (lineitem with 28GB); CORRELATED_SUBQUERY

<details><summary><b>monitoring dashboard</b></summary>
<br>
<div align="center">
<img src="imgs/subquery.png" width="800px">
</div>
<br>
</details>

<span id="-diagnosis"></span>

### Diagnosis & Optimization

#### Command-line Interface

```shell
python3 main.py --task db_diag
```

#### Website Interface

We also provide a local website demo for this environment. You can launch it with

```shell
python3 main_demo.py --task db_diag
```

After successfully launching the local server, you can visit [http://127.0.0.1:7860/](http://127.0.0.1:7860/) to trigger the diagnosis procedure (click the *Start Autoplay* button).


### Prompt Template Generation

Derive *high-quality prompt templates* from a small number of collected samples (splitting into training and evaluation sets), e.g.,

1. Prompts for index tuning optimization

```bash
cd prompt_template_scripts/index_tuning
./run.sh
```

2. Prompts for query rewrite optimization

```bash
cd prompt_template_scripts/query_rewrite
./run.sh
```

<span id="-cases"></span>

## Cases

<details><summary><b>INSUFFICIENT_MEMORY_ALLOCATION</b></summary>
<br>
<div align="center">
<img src="imgs/memory.png" width="800px">
</div>
<br>

```vim
[Chief DBA]: The anomaly started at 1691897340 and ended at 1691897430.

[CPU Agent]: Based on the CPU relevant metric values, the root cause of high CPU usage could be a high load value, too many active processes, blocked processes, high CPU scrape collector duration, and low entropy.
I suggest reviewing system logs and identifying any recent changes or updates. We should also analyze other relevant metrics such as memory usage, disk I/O, network traffic, and check for any abnormal behavior from specific processes or applications.
----------------------------
(matched knowledge) missing_index: This function checks for the presence of a required index using a workload-index-recommend interface. If the recommended index information is available, it indicates that a required index is missing and provides a suggestion for the recommended index. If the information is not available, it is not a root cause for the issue.

[Memory Agent]: The root cause of the high memory usage could be disk spill and insufficient memory allocation.
I suggest analyzing the actual resource usage during query execution, performing a thorough analysis of the query plans, and evaluating the system configuration settings related to memory allocation, such as 'work_mem' and 'shared_buffers.' More information about the sort spill count or hash spill count and the threshold values is needed to confirm if disk spill is the root cause. If the free memory is consistently low and close to the total memory capacity, consider increasing the memory allocation for the system.
----------------------------
(matched knowledge) disk_spill: This function checks whether there is a possibility of disk spill during the execution of SQL. If the plan parse information is not available, it checks whether the sort spill count or hash spill count exceeds the sort rate threshold. If the plan parse information is available, it calculates the total cost of the plan and checks whether the cost rate of the sort or hash operators exceeds the cost rate threshold. If abnormal operator details are found and the sort or hash spill count is greater than 0, it indicates that the SORT/HASH operation may spill.

[Chief DBA]: The identified root causes of the anomaly are high CPU usage due to high load value, too many active processes, blocked processes, high CPU scrape collector duration, and low entropy. The high memory usage could be due to disk spill and insufficient memory allocation.
----------------------------
(solution) To resolve the high CPU usage, we should review system logs and identify any recent changes or updates. We should also analyze other relevant metrics such as memory usage, disk I/O, network traffic, and check for any abnormal behavior from specific processes or applications.
To mitigate the high memory usage, we should analyze the actual resource usage during query execution, perform a thorough analysis of the query plans, and evaluate the system configuration settings related to memory allocation, such as 'work_mem' and 'shared_buffers.' More information about the sort spill count or hash spill count and the threshold values is needed to confirm if disk spill is the root cause. If the free memory is consistently low and close to the total memory capacity, consider increasing the memory allocation for the system.
```

</details>


<details><summary><b>POOR_JOIN_PERFORMANCE</b></summary>

https://github.com/TsinghuaDatabaseGroup/DB-GPT/assets/17394639/5a9a91bf-fc1f-415e-8a59-ec8ab5a705df

</details>


## Todo

- [ ] Project cleaning
- [ ] None-resource problem diagnosis
- [ ] (framework update) Integrate components as a whole 
- [ ] Public generated anomaly training data
- [ ] Fine-tune open-source Model
- [ ] Support other databases like *MySQL*
- [ ] Collect more knowledge and store in vector db (./knowledge_vector_db)

> The listed items are **urgent**, which we will fix within this month.

<span id="-community"></span>

## Community

- [Tsinghua University](https://www.tsinghua.edu.cn/en/)
- [ModelBest](https://modelbest.cn/)

<span id="-projects"></span>

## Relevant Projects

https://github.com/OpenBMB/AgentVerse

https://github.com/OpenBMB/BMTools

https://github.com/OpenBMB/ToolBench

<!--## Citation
Feel free to cite us if you like this project.
```bibtex
@misc{zhou2023llm4diag,
      title={LLM As DBA}, 
      author={Xuanhe Zhou, Guoliang Li, Zhiyuan Liu},
      year={2023},
      eprint={xxxx},
      archivePrefix={arXiv},
      primaryClass={xxxx}
}
```-->
