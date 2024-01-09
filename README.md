<div align= "center">
    <h1> <img src="img/dbagent.png" width="100px">数字运维员工</h1>
</div>

<div align="center">
  <a href="https://github.com/TsinghuaDatabaseGroup/DB-GPT/tree/main/localized_llms">
    本地模型
  </a> 🔥
</div>

<p align="center">
<a href="#-contact">👫 欢迎扫码加入微信群！</a> <bar> <a href="https://www.benchcouncil.org/evaluation/opencs/annual.html#Achievements">🏆 Top 100 开源项目!
</p>

<p align="center">
  <a href="#-demo">演示</a> •
  <a href="#-quickstart">快速开始</a> •
  <a href="#-anomalies">警报与异常</a> •  
  <a href="#-customize">知识与工具</a> • 
  <a href="#-FAQ">常见问题</a> •  
  <a href="#-community">社区</a> •  
  <a href="#-contributors">贡献者</a>
</p>

<p align="center">
    <img src="img/overview_v3.png" width="800px">
</p>

🦾 构建您的个人数据库管理员（D-Bot）🧑‍💻, 擅长*阅读文件，使用各种工具，编写分析报告！*

**一个重要的主版本更新即将上传！敬请期待！** 📣 🔜


<span id="-demo"></span>

## 🗺 在线演示

在在线网站（[http://dbgpt.dbmind.cn](http://dbgpt.dbmind.cn)），您可以浏览所有历史诊断结果、使用的指标和详细的诊断过程。

<p align="center">
  <a href="http://dbgpt.dbmind.cn">
    <img src="./assets/dbot2.gif" width="800px">
  </a>
</p>

<p align="center">
  <a href="http://dbgpt.dbmind.cn">
    <img src="img/frontend_v2_2.png" width="800px" alt="frontend_v2">
  </a>
</p>

<span id="-news"></span>

## 📰 更新

- [ ] 加速本地模型（极速版dbot）
- [x] 根据 *知识聚类结果* 新增8种专家角色
- [x] 升级基于 LLM 的诊断机制:
  - [x] _任务分派 -> 并行诊断 -> 交叉审查 -> 报告生成_
- [x] 添加典型异常和警报 (Pigsty) <a href="#-anomalies">🔗 链接</a>
- [x] 提供端到端框架！<a href="#-diagnosis">🚀 链接</a>
- [ ] 在多个层次上支持监控和优化工具 [🔗 链接](multiagents/tools)

  - [x] 监控指标 (Prometheus)
  - [ ] 代码级别的火焰图分析，定位算子、配置等问题
  - [x] 诊断知识检索 (dbmind)
  - [x] 逻辑查询转换 (Calcite)
  - [x] 索引优化算法 (适用于 PostgreSQL)
  - [x] 物理操作符提示 (适用于 PostgreSQL)
  - [ ] 备份和时间点恢复 (Pigsty)

- [x] 我们的愿景论文已发布 (持续更新)
  - _LLM As DBA_ [[论文]](https://arxiv.org/abs/2308.05481) [[中文解读]](https://mp.weixin.qq.com/s/i0-Fdde7DX9YE1jACxB9_Q) [[推特]](https://twitter.com/omarsar0/status/1689811820272353280?s=61&t=MlkXRcM6bNQYHnTIQVUmVw) [[幻灯片]](materials/slides)
  - _DB-GPT: Large Language Model Meets Database_ [[论文]](http://dbgroup.cs.tsinghua.edu.cn/ligl/papers/dbgpt-dse.pdf)

> 该项目正在不断引入新特性 👫👫<br/>
> 不要忘记星标 ⭐ 并关注 👀 以同步最新进展 :)

<span id="-quickstart"></span>

## 🕹 快速开始

## 快速上手

### 1. 环境配置

+ 首先，确保你的机器安装了 Python 3.8 - 3.10
```
$ python --version
Python 3.10.12
```
接着，创建一个虚拟环境，并在虚拟环境内安装项目的依赖
```shell

# 拉取仓库
$ git clone https://github.com/TsinghuaDatabaseGroup/DB-GPT.git

# 进入目录
$ cd Langchain-Chatchat

# 安装全部依赖
$ pip3 install -r requirements.txt 
$ pip3 install -r requirements_api.txt
$ pip3 install -r requirements_webui.txt  

# 默认依赖包括基本运行环境（Chroma-DB向量库）。如果要使用其它向量库，请将 requirements.txt 中相应依赖取消注释再安装。

# 如果要运行Web UI，还需要安装前端项目中的依赖包。此处UI较为复杂，所以使用VUE单独写了个前端页面。
cd webui_pages/reports/reports_ui
rm -rf node_modules/
rm -r package-lock.json
# 首次运行安装依赖项（推荐使用nodejs, ^16.13.1）
npm install  --legacy-peer-deps
npm install -g cross-env
```
### 2， 模型下载

如需在本地或离线环境下运行本项目，需要首先将项目所需的模型下载至本地，通常开源 LLM 与 Embedding 模型可以从 [HuggingFace](https://huggingface.co/models) 下载。

以本项目中默认使用的 LLM 模型 [THUDM/ChatGLM2-6B](https://huggingface.co/THUDM/chatglm2-6b) 与 Embedding 模型 [moka-ai/m3e-base](https://huggingface.co/moka-ai/m3e-base) 为例：

下载模型需要先[安装 Git LFS](https://docs.github.com/zh/repositories/working-with-files/managing-large-files/installing-git-large-file-storage)，然后运行

```Shell
$ git lfs install
$ git clone https://huggingface.co/moka-ai/m3e-base
```
### 3. 初始化知识库和配置文件

按照下列方式初始化自己的知识库和简单的复制配置文件
```shell
$ python copy_config_example.py
$ python init_database.py --recreate-vs
 ```
### 4. 一键启动

按照以下命令启动项目
```shell
$ python startup.py -a
```
### 5. 启动界面示例

如果正常启动，你将能看到以下界面

1. FastAPI Docs 界面

![](img/fastapi_docs_026.png)

2. Web UI 启动界面示例：

- Web UI 对话界面：

![img](img/LLM_success.png)

- Web UI 知识库管理页面：

![](img/init_knowledge_base.jpg)


### 诊断

<span id="-prerequisites"></span>

#### 1. 先决条件

- PostgreSQL v12 或更高版本

  > 确保您的数据库支持远程连接 ([链接](https://support.cpanel.net/hc/en-us/articles/4419265023383-How-to-enable-remote-PostgreSQL-access))

  > 此外，安装扩展如 _[pg_stat_statements](https://pganalyze.com/docs/install/01_enabling_pg_stat_statements)_（跟踪频繁查询), _[pg_hint_plan](https://pg-hint-plan.readthedocs.io/en/latest/installation.html)_（优化物理操作符), 和 _[hypopg](https://github.com/HypoPG/hypopg)_（创建假设索引）。

  > 注意 _pg_stat_statements_ 会持续累积查询统计数据。因此您需要定期清除统计数据：1) 要丢弃所有统计数据，执行 _"SELECT pg_stat_statements_reset();"_; 2) 要丢弃特定查询的统计数据，执行 _"SELECT pg_stat_statements_reset(userid, dbid, queryid);"_。

- 在 PostgreSQL 中启用慢查询日志 ([链接](https://ubiq.co/database-blog/how-to-enable-slow-query-log-in-postgresql/))

  > (1) 对于 _"systemctl restart postgresql"_，服务名可以不同（例如，postgresql-12.service）;

  > (2) 使用绝对日志路径名称如 _"log_directory = '/var/lib/pgsql/12/data/log'"_;

  > (3) 在 postgresql.conf 中设置 _"log_line_prefix = '%m [%p] [%d]'"_（记录不同查询的数据库名）。

- Prometheus

  > 查看[prometheus.md](materials/help_documents/prometheus.md)了解详细的安装指南。
  
步骤1: 下载 [Sentence Trasformer](https://cloud.tsinghua.edu.cn/f/6e8a3ad547204303a5ae/?dl=1) 模型参数

- 创建新目录 ./multiagents/localized_llms/sentence_embedding/

- 将下载的sentence-transformer.zip压缩包放置在./multiagents/localized_llms/sentence_embedding/目录下；解压压缩包。

#### 2. 诊断

- 测试单个案例

```shell
python3 run_diagnose.py --anomaly_file ./diagnostic_files/testing_cases_5.json
```

<span id="-anomalies"></span>

## 🎩 告警和异常

### 告警管理

我们支持 Prometheus 的 AlertManager。您可以在这里找到有关如何配置 alertmanager 的更多信息：[alertmanager.md](https://prometheus.io/docs/alerting/latest/configuration/)。

- 我们提供与 AlertManager 相关的配置文件，包括[alertmanager.yml](./prometheus_service/alertmanager.yml)、[node_rules.yml](prometheus_service/node_rules.yml)和[pgsql_rules.yml](prometheus_service/pgsql_rules.yml)。路径位于根目录的[config folder](./config/)中，您可以将其部署到您的 Prometheus 服务器以检索相关的异常。
- 我们还提供支持获取警报的 webhook 服务器。路径是根目录中的 webhook 文件夹，您可以将其部署到您的服务器以获取和存储 Prometheus 的警报。这个文件是使用 SSH 获取的。您需要在 config 文件夹中的[diagnose_config.py](./configs/diagnose_config.py)中配置您的服务器信息。
- [node_rules.yml](prometheus_service/node_rules.yml)和[pgsql_rules.yml](prometheus_service/pgsql_rules.yml)是引用[https://github.com/Vonng/pigsty](https://github.com/Vonng/pigsty)开源项目，他们的监控做得非常好，感谢他们的努力。

### 异常模拟

#### 脚本触发的异常

我们提供可能引起典型异常的脚本。在 [http://dbgpt.dbmind.cn](http://dbgpt.dbmind.cn) 查看不同的异常案例。

| 根本原因              | 描述                        | 可能的警报                                                                                                                  |
| --------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| INSERT_LARGE_DATA     | 插入大量数据的执行时间较长  | ![](https://img.shields.io/badge/-NodeOutOfMem-informational)                                                               |
| FETCH_LARGE_DATA      | 获取大量数据的执行时间较长  | ![](https://img.shields.io/badge/-NodeLoadHigh-Informational)                                                               |
| REDUNDANT_INDEX       | 表中不必要且多余的索引      | ![](https://img.shields.io/badge/-NodeLoadHigh-Informational)                                                               |
| VACUUM                | 数据修改导致的未使用空间    | ![](https://img.shields.io/badge/-NodeOutOfMem-informational)                                                               |
| POOR_JOIN_PERFORMANCE | Join 操作符的性能差         | ![](https://img.shields.io/badge/-NodeLoadHigh-Informational)                                                               |
| CORRELATED_SUBQUERY   | SQL 中不可提升的子查询      | ![](https://img.shields.io/badge/-NodeLoadHigh-Informational),![](https://img.shields.io/badge/-PostgresDown-red)           |
| LOCK_CONTENTION       | 锁争用问题                  | ![](https://img.shields.io/badge/-NodeCpuHigh-Informational) ![](https://img.shields.io/badge/-PostgresRestart-red)         |
| CPU_CONTENTION        | 严重的外部 CPU 资源争用     | ![](https://img.shields.io/badge/-NodeLoadHigh-Informational)                                                               |
| IO_CONTENTION         | 影响 SQL 性能的 IO 资源争用 | ![](https://img.shields.io/badge/-NodeLoadHigh-Informational) ![](https://img.shields.io/badge/-NodeOutOfMem-informational) |
| COMMIT_CONTENTION     | 高并发提交影响 SQL 执行     | ![](https://img.shields.io/badge/-NodeLoadHigh-Informational) ![](https://img.shields.io/badge/-NodeOutOfMem-informational) |
| SMALL_MEMORY_ALLOC    | 工具分配的内存空间过小      |                                                                                                                             |

#### 手动触发异常

_[点击查看 29 种典型异常与专家分析](./anomaly_trigger/29种性能异常与根因分析.pdf)（由 DBMind 团队支持）_

<span id="-customize"></span>

## 📎 自定义知识和工具

### 1. 知识提取 (陈醉)

<span id="-doc2knowledge"></span>

步骤 1. 将*./doc2knowledge/config_template.json*重命名为*doc2knowledge/config.json*。并为"api_key"添加值（"organization"是可选的）

> GPT-4 是使用*function call*功能所必需的。我将尝试解决这个限制。

步骤 2. 按章节索引将文档分割为单独的章节文件（例如，section1, section1.1, section2 ...）。并将章节文件复制到 _docs/<your_document_name>/raw/_。例如：

    .
    ├── docs
    │   ├── report_example
    |   │   ├── raw
    |   │   |    ├── 1 title.txt
    |   │   |    ├── 1.1 category.txt

> 这是一项费力的工作，很难找到比手动分割给定文档更好的方法

> 您可以跳过这一步，直接运行 _report_example_ 案例

步骤 3. 修改*doc2knowledge.py*脚本中的参数并运行脚本：

```bash
cd doc2knowledge/
python doc2knowledge.py
```

> 缓存相同文档章节的摘要。如果不想重复使用以前的缓存，可以删除该文件。

<span id="-tools"></span>

### 2. 工具准备

- 工具 API（用于优化）

  | 模块                                                         | 功能          |
  | ------------------------------------------------------------ | ------------- |
  | [index_selection](multiagents/tools/index_advisor)（已装备） | _启发式_ 算法 |
  | [query_rewrite](multiagents/tools/query_advisor)（已装备）   | _45_ 条规则   |
  | [physical_hint](multiagents/tools/query_advisor)（已装备）   | _15_ 个参数   |

  对于[[query_rewrite](multiagents/tools/query_advisor), [physical_hint](multiagents/tools/query_advisor)]内的功能，你可以使用*api_test.py* 脚本来验证其有效性。

  如果功能确实有效，请将其添加到相应模块的*api.py*中。

<span id="-FAQ"></span>

## 💁 常见问题解答

<details><summary><b>🤨 '.sh' 脚本命令无法在Windows系统上执行。</b></summary>
将Shell切换到*git bash*或使用*git bash*来执行'.sh'脚本。
</details>

<details><summary><b>🤨 Windows系统上出现“找不到名为'xxx'的模块”。</b></summary>
这个错误是由Python运行时环境路径问题引起的。你需要进行以下步骤：

步骤 1：检查环境变量。

<div align="center">
<img src="img/faq2.png" width="800px">
</div>

你必须在环境变量中配置"Scripts"。

步骤 2：检查 IDE 设置。

对于 VS Code，下载 Python 扩展。对于 PyCharm，为当前项目指定 Python 版本。

</details>

## ⏱ 待办事项

- ~~项目清理~~
- ~~支持更多异常~~
- 根据匹配的知识严格限制 llm 输出（过多不相关信息）
- ~~查询日志选项（可能会占用磁盘空间，我们需要仔细考虑）~~
- ~~添加更多通信机制~~
- ~~支持更多知识来源~~
- 达到 D-bot(gpt4)能力的本地化模型
- 支持其他数据库（例如，mysql/redis）

<span id="-community"></span>

## 👫 社区

- [清华大学](https://www.tsinghua.edu.cn/en/)
- [面壁科技](https://modelbest.cn/)

<span id="-projects"></span>

## 🤗 相关项目

https://github.com/OpenBMB/AgentVerse

https://github.com/Vonng/pigsty

<span id="-citation"></span>

## 📒 引用


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
      title={DB-GPT: 大型语言模型遇上数据库},
      author={Xuanhe Zhou, Zhaoyan Sun, Guoliang Li},
      year={2023},
      archivePrefix={Data Science and Engineering},
}
```

<span id="-contributors"></span>

## 📧 贡献者

<!-- 在你的Readme.md文件中复制粘贴 -->

<a href="https://github.com/TsinghuaDatabaseGroup/DB-GPT/network/dependencies">
  <img src="https://contrib.rocks/image?repo=TsinghuaDatabaseGroup/DB-GPT" />
</a>

其他合作者: [Wei Zhou](https://github.com/Beliefuture), [Kunyi Li](https://github.com/LikyThu)。

我们感谢所有对这个项目的贡献者。如果你想参与或贡献，不要犹豫！


<span id="-contact"></span>

## 联系我们
👏🏻欢迎加入我们的微信群
<div align= "center">
<img src="img/group.png" width="400px">
</div>
