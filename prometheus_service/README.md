以下是prometheus_service的安装说明：

## 1. 安装依赖

首先，你需要安装项目所需的依赖。在命令行中执行以下命令：

```bash
pip install -r requirements.txt
```

这将使用pip包管理器安装项目所需的所有依赖项。确保你已经在正确的工作目录下，并且已经设置好了Python环境。

## 2. 运行程序

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

## 3. 验证安装

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

## 4. webhook接口

webhook server的主要接口是`/alert`，使用HTTP POST方法。你可以向该接口发送Webhook通知，用于处理告警或其他相关任务。

总结而言，安装prometheus service涉及以下步骤：安装依赖项、运行程序、验证安装和配置webhook接口。根据这些步骤，你应该能够成功搭建并测试prometheus service。