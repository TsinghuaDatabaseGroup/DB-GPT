# Prometheus和AlertManager安装介绍

1) 作为DB-GPT的附属项目，在工作流程上是DB-GPT的前置项目，用来收集、存储诊断数据库的相关信息，并生成诊断文件，以提供给DB-GPT进行诊断。
2) 使用prometheus_service_docker和Docker，你可以轻松地完成上面的工作。
3) 如果你的环境中已经内置了Promethues和alertmanager，那么只需要使用app.py,开启webhook收集信息即可。
4) 如果你没有内置Promethues和alertmanager，那么你可以使用docker-compose.yml来安装Promethues和alertmanager以及webhook server。


## Prometheus和AlertManager说明：
1) Prometheus是一个开源的监控系统，AlertManager是一个开源的告警系统。具体使用方法查询对应的文档。
2) DB-GPT需要配置Prometheus和AlertManager，以便收集和发送告警信息。
3) Prometheus中需要安装[node_exporter](https://github.com/prometheus/node_exporter)和[pg_exporter](https://github.com/Vonng/pg_exporter)，请根据Prometheus教程，监控数据库服务器的指标。
4) 异常需要用到AlertManager来发送告警信息，发现异常的rules 可以参考[node_rules.yml](./node_rules.yml)和[pgsql_rules.yml](./pgsql_rules.yml)。AlertManager中需要配置webhook，webhook的配置可以参考[alertmanager.yml](./alertmanager.yml)。


## webhook server的安装说明：
1) webhook在收到alert消息后，会根据alert信息，收集alert时间内的Prometheus指标和慢查询语句等信息，并生成诊断文件，以提供给DB-GPT进行诊断。
2) 需要修改prometheus_abnormal_metric.py文件中的PROMETHEUS_CONFIG配置。
```shell
PROMETHEUS_CONFIG = {
    "api_url": "http://8.131.129.55:9090/", # Prometheus的API地址
    "postgresql_exporter_instance": "112.27.58.65:9187", # postgresql_exporter的实例地址
    "node_exporter_instance": "171.27.58.65:9100" # node_exporter的实例地址
}
```


**TIP**：如果你需要webhook来收集慢查询信息，需要在get_slow_queries.py中填写SERVER_CONFIG的相关信息，该SERVER_CONFIG中填写的ssh信息，能够有权限拿到慢查询日志。

### 1. 安装依赖

首先，你需要安装项目所需的依赖。在命令行中执行以下命令：

```bash
pip install -r requirements.txt
```

这将使用pip包管理器安装项目所需的所有依赖项。确保你已经在正确的工作目录下，并且已经设置好了Python环境。

### 2. 运行程序

运行prometheus_service程序之前，你可以根据需要调整配置。打开`app.py`文件，并找到以下代码：

```python
    uvicorn.run(
        app = app,
        host = "0.0.0.0",
        port = 8023
    )
```

在这里，可以修改`port`参数来指定prometheus_service监听的端口号。

运行webhook server程序的方式取决于你的操作系统和部署环境。在Unix类系统上，你可以使用终端或shell脚本执行以下命令：

```bash
sh run.sh
```

这将启动webhook server并开始监听指定的端口。

### 3. 验证安装

安装完成后，你可以使用curl命令测试prometheus_service是否正常工作。在终端中执行以下命令：

```bash
curl http://127.0.0.1:8023/test
```

如果一切正常，你应该会收到以下JSON响应：

```json
{
  "code": 0,
  "msg": "success",
  "data": "prometheus service is running"
}
```

这表明webhook server正在运行，且访问`/test`接口成功。

### 4. webhook接口

webhook server的主要接口是`/alert`，使用HTTP POST方法。你可以向该接口发送Webhook通知，用于处理告警或其他相关任务。

总结而言，安装prometheus service涉及以下步骤：安装依赖项、运行程序、验证安装和配置webhook接口。根据这些步骤，你应该能够成功搭建并测试prometheus service。