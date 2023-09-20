<div align= "center">
    <h1> <img src="imgs/dbagent.png" width="100px"> 数字DBA员工</h1>
</div>

<p align="center">
  <a href="#-features">特点</a> •
  <a href="#-news">最新动态</a> •
  <a href="#-quickstart">快速开始</a> •
  <a href="#-anomalies">案例分析</a> •    
  <a href="#-customize">自定义知识和工具</a> •    
  <a href="#-FAQ">常见问题</a> •  
  <a href="#-community">社区</a> •  
  <a href="#-contributors">贡献者</a>
</p>


<p align="center">
    【<a href="README.md">English</a> | 中文</a>】
</p>


<!-- <br>
<div align="center">
<img src="imgs/dbagent.png" width="400px">
</div>
<br> -->

🧗 我们的目标是提供一套实用、有一定门槛、且易于使用的数据库管理工具。该套工具以LLMs为基础构建，包括 **查询优化**（*在线演示*）、**系统诊断**（*D-Bot*）、**异常模拟**（*attacker*）

<br>
<div align="center">
<img src="imgs/dbgpt-v2.png" width="800px">
</div>
<br>


<span id="-features"></span>

## 特点

### 系统诊断（*D-Bot*）

- **有根据的诊断**：D-Bot可以利用相关的数据库知识（使用*document2experience*）提供有根据的诊断。

- **实用工具使用**：D-Bot可以利用监控和优化工具来提高维护能力（使用*tool learning*和*tree of thought*）。

- **深度推理**：与普通的LLM相比，D-Bot将实现竞争性的推理能力，以分析根本原因（使用*multi-llm通信*）。

<br>
    <div align="center">
    <img src="imgs/frontendv3.png" width="800px">
    </div>
<br>

**演示如何使用D-Bot**

https://github.com/OpenBMB/AgentVerse/assets/11704492/c633419d-afbb-47d4-bb12-6bb512e7af3a


<span id="-news"></span>

## 最新动态
<!-- - [x] **[2023/8/23]** 100\% accurate tool calling and refined diagnosis <a href="#-solid_response">🔗</a> -->

- [x] **[2023/9/10]** 添加诊断日志 [🔗 link](logs/diag_training_data.txt) 和前端的回放按钮 [⏱ link](logs/info.log)

- [x] **[2023/9/09]** 添加典型异常 <a href="#-anomalies">🔗 link</a>

- [x] **[2023/9/05]** 统一的诊断框架已经可用！只需一个命令即可开始诊断+工具服务，体验5倍的速度提升！！ <a href="#-diagnosis">🚀 链接</a>

- [x] **[2023/8/25]** 支持基于vue的网站界面。更加灵活和美观！ <a href="#-frontend">🔗 链接</a>

- [x] **[2023/8/22]** 支持60多个API的工具检索 [🔗 链接](multiagents/tools)

- [x] **[2023/8/16]** 支持多级优化功能 <a href="#-tools">🔗 链接</a>

- [x] **[2023/8/10]** 我们的愿景论文已发布（持续更新）

    * *LLM作为数据库管理员.* [[论文]](https://arxiv.org/abs/2308.05481) [[中文解读]](https://mp.weixin.qq.com/s/i0-Fdde7DX9YE1jACxB9_Q) [[推特]](https://twitter.com/omarsar0/status/1689811820272353280?s=61&t=MlkXRcM6bNQYHnTIQVUmVw) [[幻灯片]](materials/slides)

    * *DB-GPT: 大型语言模型遇上数据库.* [[论文]](http://dbgroup.cs.tsinghua.edu.cn/ligl/papers/dbgpt-dse.pdf)

> 这个项目正在不断引入新特性 👫👫<br/> 
> 不要忘记点赞 ⭐ 并关注 👀 以保持最新信息 :)



<span id="-quickstart"></span>

## 快速入门

<!-- <br>
<div align="center">
<img src="imgs/workflow.png" width="800px">
</div>
<br> -->

### 系统诊断（*D-Bot*）

#### 文件夹结构

    .
    ├── multiagents
    │   ├── agent_conf                        # 每个代理的设置
    │   ├── agents                            # 不同类型代理的实现
    │   ├── environments                      # 例如，聊天顺序 / 聊天更新 / 终端条件
    │   ├── knowledge                         # 文档中的诊断经验
    │   ├── llms                              # 支持的模型
    │   ├── memory                            # 聊天历史的内容和摘要
    │   ├── response_formalize_scripts        # 模型响应的无用内容删除
    │   ├── tools                             # 用于模型的外部监控/优化工具
    │   └── utils                             # 其他功能（例如，数据库/JSON/YAML操作）



#### 1. 先决条件

- PostgreSQL v12或更高版本

    > 此外，安装扩展如 *[pg_stat_statements](https://pganalyze.com/docs/install/01_enabling_pg_stat_statements)*（跟踪慢查询）、*[pg_hint_plan](https://pg-hint-plan.readthedocs.io/en/latest/installation.html)*（优化物理运算符）和 *[hypopg](https://github.com/HypoPG/hypopg)*（创建假设索引）。

- Prometheus ~~和Grafana（[教程](https://grafana.com/docs/grafana/latest/get-started/get-started-grafana-prometheus/)）~~

    查看 [prometheus.md](materials/help_documents/prometheus.md) 以获取详细的安装指南。

    > 使用我们基于vue的前端，Grafana不再是必需的。


#### 2. 包安装

步骤1：安装Python包。


```bash
pip install -r requirements.txt
```

步骤2：配置环境变量。

- 导出您的OpenAI API密钥
```bash
# macos
export OPENAI_API_KEY="your_api_key_here"
```

```bash
# windows
set OPENAI_API_KEY="your_api_key_here"
```

步骤3：将数据库/异常/Prometheus的设置添加到 tool_config_example.yaml 并重命名为 tool_config.yaml：

    ```bash
    POSTGRESQL:
      host: 182.92.xxx.x
      port: 5432
      user: xxxx
      password: xxxxx
      dbname: postgres

    BENCHSERVER:
      server_address: 8.131.xxx.xx
      username: root
      password: xxxxx
      remote_directory: /root/benchmark

    PROMETHEUS:
      api_url: http://8.131.xxx.xx:9090/
      postgresql_exporter_instance: 172.27.xx.xx:9187
      node_exporter_instance: 172.27.xx.xx:9100
    ```

> 您可以忽略BENCHSERVER的设置，在此版本中未使用。

- 如果通过VPN访问openai服务，请执行以下命令：

```bash
# macos
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 all_proxy=socks5://127.0.0.1:7890
```

- 测试您的openai密钥

```bash
cd others
python openai_test.py
```

<span id="-diagnosis"></span>

#### 3. 诊断和优化

<span id="-frontend"></span>

##### 网站界面

我们还为此环境提供了本地网站演示。您可以使用以下命令启动它：

```shell
# cd website
cd front_demo
rm -rf node_modules/
rm -r package-lock.json
# 第一次运行时安装依赖项（建议使用nodejs，建议使用^16.13.1）
npm install  --legacy-peer-deps
# 返回根目录
cd ..
# 启动本地服务器并打开网站
sh run_demo.sh
```

> 如果安装了多个版本的Python，请在run_demo.sh中仔细决定“python app.py”命令。

成功启动本地服务器后，访问 http://127.0.0.1:9228/ 触发诊断过程。


##### 命令行界面


```shell
python main.py
```


<span id="-anomalies"></span>

## AlertManager
我们支持Prometheus的AlertManager。您可以在此处找到有关如何配置AlertManager的更多信息：[alertmanager.md](https://prometheus.io/docs/alerting/latest/configuration/)。

- 我们提供了AlertManager相关的配置文件，包含alertmanager.yml、node_rules.yml、pgsql_rules.yml。路径为根目录下的config [🔗 link](./config/) 文件夹内，您可以将其部署到您的Prometheus服务器中，用来获取相关的异常。
- 我们还提供了支持获取Alert的webhook server。路径为根目录下的webhook文件夹，您可以将它部署到您的服务器中，用来获取并存储Prometheus的Alert。诊断模型会从该服务器中定时抓取Alert信息，该文件获取方式为SSh，您需要在config文件夹下的tool_config.yaml [🔗 link](./config/tool_config_example.yaml) 中配置您的服务器信息。 
- [node_rules.yml](./config/node_rules.yml) and [pgsql_rules.yml](./config/pgsql_rules.yml) 是引用 https://github.com/Vonng/pigsty 这个开源项目中的代码，他们的监控做的非常棒，感谢他们的付出。

## 🎩 异常案例

在anomaly_trigger目录中，我们旨在提供可能导致典型异常的脚本，例如，


| 根因          | 描述                                           | 案例                 |
|---------------------|-------------------------------------------------------|----------------------|
| ![](https://img.shields.io/badge/-INSERT_LARGE_DATA-Informational)    | 大量数据插入的长时间执行 insertions         |                      |
| ![](https://img.shields.io/badge/-FETCH_LARGE_DATA-Informational)    | 大量数据获取的长时间执行 fetching           |                      |
| ![](https://img.shields.io/badge/-MISSING_INDEXES-Informational)     | 缺少索引导致性能问题	            |   [🔗 link](case_analysis/missing_indexes.txt)     |
| ![](https://img.shields.io/badge/-REDUNDANT_INDEX-Informational)      | 表中不必要和多余的索引	           |                      |
| ![](https://img.shields.io/badge/-VACUUM-Informational)              |  数据修改导致未使用的空间	       |                      |
| ![](https://img.shields.io/badge/-POOR_JOIN_PERFORMANCE-Informational) | Join操作的性能差	                  |                      |
| ![](https://img.shields.io/badge/-CORRELATED_SUBQUERY-Informational) | SQL中难以优化的子查询	                      |                      |
| ![](https://img.shields.io/badge/-LACK_STATISTIC_INFO-Informational) | 过时的统计信息影响执行计划质量    |                      |
| ![](https://img.shields.io/badge/-LOCK_CONTENTION-informational)     | 锁竞争问题                                |                      |
| ![](https://img.shields.io/badge/-CPU_CONTENTION-informational)      | 严重的外部CPU资源争用	               |                      |
| ![](https://img.shields.io/badge/-IO_CONTENTION-informational)       | 影响SQL性能的IO资源争用	      |                      |
| ![](https://img.shields.io/badge/-INSERT_CONTENTION-informational) | 影响SQL执行的高并发插入	        |   [🔗 link](case_analysis/concurrent_inserts.txt)     |
| ![](https://img.shields.io/badge/-COMMIT_CONTENTION-informational) | 影响SQL执行的高并发提交	        |   [🔗 link](case_analysis/concurrent_commits.txt)     |
| ![](https://img.shields.io/badge/-WORKLOAD_CONTENTION-informational) | 影响SQL执行的工作负载集中	        |   [🔗 link](case_analysis/workload_contention.txt)     |
| ![](https://img.shields.io/badge/-SMALL_MEMORY_ALLOC-red)    | 分配的内存空间太小	（shared_buffer）              |                      |
| ![](https://img.shields.io/badge/-IO_SATURATION-red)     | 达到最大I/O容量或吞吐量	               |                      |



<span id="-customize"></span>

## 自定义您的知识库和工具


#### 1. 知识准备


- 从代码（./knowledge_json/knowledge_from_code）和文档（./knowledge_json/knowledge_from_document）中提取知识。

    - 将代码块添加到 diagnosis_code.txt 文件中 -> 重新运行 extract_knowledge.py 脚本 -> 检查更新结果并同步到 root_causes_dbmind.jsonl。



<span id="-tools"></span>

#### 2. 工具准备


- 工具API（用于优化）

    | 模块                  | 功能 |
    |-------------------------|-----------|
    | [索引推荐](multiagents/tools/index_advisor) (equipped)          | *启发式算法*  |
    | [查询重写](multiagents/tools/query_advisor) (equipped)           | *45条规则*  |
    | [物理hint](multiagents/tools/query_advisor) (equipped)           | *15条规则*  |

    对于[query_rewrite, physical_hint]中的功能，您可以使用api_test.py脚本来验证其有效性。

    如果实际上功能正常工作，请将其附加到相应模块的api.py中。

<span id="-tot"></span>

- 工具使用算法（tree of thought）

    ```bash
    cd tree_of_thought
    python test_database.py
    ```

    > 历史消息可能占用很多tokens，因此仔细决定回合数。

<!-- ## Prompt Template Generation (optional)

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
``` -->

<span id="-FAQ"></span>

## 常见问题

<details><summary><b>🤨 在 Windows 系统上无法执行 '.sh' 脚本命令。</b></summary>
切换到 *git bash* 或使用 *git bash* 执行 '.sh' 脚本。
</details>
<details><summary><b>🤨 在 Windows 系统上出现 "No module named 'xxx'" 错误。</b></summary>
这个错误是由于 Python 运行环境路径的问题引起的。您需要执行以下步骤：
步骤 1：检查环境变量。

<div align="center">
<img src="imgs/faq2.png" width="800px">
</div>
您必须在环境变量中配置 "Scripts"。

步骤 2：检查 IDE 设置。

对于 VS Code，请下载适用于代码的 Python 扩展。对于 PyCharm，请为当前项目指定 Python 版本。

</details>

## 待办事项

- [ ] ~~项目清理~~
- [ ] 支持更多异常
- [ ] 添加更多通信机制
- [ ] 公开生成的异常训练数据
- [ ] 微调本地化私有模型
- [ ] 在演示网站中集成准备组件
- [ ] 支持其他数据库，如 MySQL
- [ ] 收集更多知识并存储在矢量数据库中（./knowledge_vector_db）

<span id="-community"></span>

## 社区


- [清华大学](https://www.tsinghua.edu.cn/en/)
- [面壁](https://modelbest.cn/)

<span id="-projects"></span>

## 相关项目

https://github.com/OpenBMB/AgentVerse

https://github.com/OpenBMB/BMTools

<span id="-citation"></span>

## 引用

如果您喜欢这个项目，欢迎引用我们。

```bibtex
@misc{zhou2023llm4diag,
      title={LLM As DBA}, 
      author={Xuanhe Zhou, Guoliang Li, Zhiyuan Liu},
      year={2023},
      eprint={2308.05481},
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

## 贡献者


<!-- Copy-paste in your Readme.md file -->

<a href="https://github.com/TsinghuaDatabaseGroup/DB-GPT/network/dependencies">
  <img src="https://contrib.rocks/image?repo=TsinghuaDatabaseGroup/DB-GPT" />
</a>

其他贡献者: [Wei Zhou](https://github.com/Beliefuture), [Kunyi Li](https://github.com/LikyThu).

我们感谢所有为这个项目做出贡献的人。如果您希望参与或贡献，请不要犹豫！