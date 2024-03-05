
ANOMALY_DESC_PROMPT='''
Please describe the following anomaly event in natural language:  
{anomaly_str}

Note do not miss any important information in each line of the event. And the description templates should be like: 

1. "During the inspection, it was found that from xx to xx time, the database's CPU usage was relatively high, approximately 80% to 90%. It is a *critical problem*, please solve it as soon as possible."

2. "During the inspection, it was found that from xx to xx time, the database's CPU usage was relatively high, approximately 80% to 90%. It is just a *warning*, please take time to solve it carefully."
'''

ANOMALY_DESC_PROMPT_zh = '''
请用自然语言描述下面的一条或多条异常事件：
{anomaly_str}

请注意不要遗漏事件中的任何重要信息。对每条异常事件，描述模板如下：
在检查过程中发现，从时间xx到xx，出现了xx现象，这是个严重问题/警告，请立即/仔细解决。
'''

ANOMALY_TITLE_PROMPT='''
Please give a title for the following anomaly event within 15 words:
{anomaly_str}

Note the title template is like: 
Analysis Report of High CPU Usage
'''

ANOMALY_TITLE_PROMPT_zh = '''
请给下面的异常事件取一个标题：
{anomaly_str}

标题的模板类似：高CPU使用率的分析报告
'''

