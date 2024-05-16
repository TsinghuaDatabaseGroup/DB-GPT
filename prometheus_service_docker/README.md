# Prometheus And AlertManager Deployment Tutorial

<p align="center">
    【English | <a href="README_Chinese.md">中文</a>】
</p>

1) As an affiliated project of DB-GPT, it serves as a preliminary project in the workflow of DB-GPT, used to collect and store relevant diagnostic information of the database and generate diagnostic files to be provided to DB-GPT for diagnosis.
2) By using prometheus_service_docker and Docker, you can easily accomplish the above tasks.
3) If Prometheus and Alertmanager are already built into your environment, you only need to use app.py to start the webhook and collect information.
4) If you do not have Prometheus and Alertmanager built in, you can use docker-compose.yml to install Prometheus, Alertmanager, and the webhook server.


## Explanation of Prometheus and AlertManager

1) Prometheus is an open-source monitoring system, and AlertManager is an open-source alerting system. Refer to their respective documentation for specific usage methods.
2) DB-GPT needs to configure Prometheus and AlertManager to collect and send alert information.
3) You need to install [node_exporter](https://github.com/prometheus/node_exporter) and [pg_exporter](https://github.com/Vonng/pg_exporter) in Prometheus. Follow the Prometheus tutorial to monitor database server metrics.
4) AlertManager is needed to send alert information when anomalies are detected. The rules for detecting anomalies can be found in [node_rules.yml](./node_rules.yml) and [pgsql_rules.yml](./pgsql_rules.yml). Webhooks need to be configured in AlertManager, and the configuration can be found in [alertmanager.yml](./alertmanager.yml).


## Installation instructions for the webhook server:
1) When the webhook receives an alert message, it will collect Prometheus metrics and slow query statements during the alert period based on the alert information and generate diagnostic files to be provided to DB-GPT for diagnosis.
2) You need to modify the PROMETHEUS_CONFIG configuration in the prometheus_abnormal_metric.py file.

```shell
PROMETHEUS_CONFIG = {
    "api_url": "http://8.131.129.55:9090/", # Prometheus API Address
    "postgresql_exporter_instance": "112.27.58.65:9187", # postgresql_exporter instance address
    "node_exporter_instance": "171.27.58.65:9100" # node_exporter instance address
}
```

TIP: If you need the webhook to collect slow query information, you need to fill in the SERVER_CONFIG information in get_slow_queries.py. The SSH information in SERVER_CONFIG should have the necessary permissions to access the slow query logs.

### 1. Install dependencies

First, you need to install the required dependencies for the project. Execute the following command in the command line:


```bash
pip install -r requirements.txt
```

This will use the pip package manager to install all necessary dependencies for the project. Make sure you are in the correct working directory and have set up the Python environment.


### 2. Run the program

Before running the prometheus_service program, you can adjust the configuration as needed. Open the app.py file and find the following code:


```python
    uvicorn.run(
        app = app,
        host = "0.0.0.0",
        port = 8023
    )
```

Here, you can modify the port parameter to specify the port number that prometheus_service will listen on.


The method for running the webhook server depends on your operating system and deployment environment. On Unix-like systems, you can use the terminal or a shell script to execute the following command:


```bash
sh run.sh
```

This will start the webhook server and begin listening on the specified port.


### 3. Verify installation

After installation, you can use the curl command to test if prometheus_service is working properly. Execute the following command in the terminal:


```bash
curl http://127.0.0.1:8023/test
```

If everything is working correctly, you should receive the following JSON response:


```json
{
  "code": 0,
  "msg": "success",
  "data": "prometheus service is running"
}
```

This indicates that the webhook server is running and that access to the /test endpoint was successful.


### 4. webhook Endpoint

The main endpoint of the webhook server is `/alert`, which uses the HTTP POST method. You can send webhook notifications to this endpoint to handle alerts or other related tasks.

In summary, installing prometheus service involves the following steps: installing dependencies, running the program, verifying the installation, and configuring the webhook endpoint. By following these steps, you should be able to successfully set up and test the prometheus service.