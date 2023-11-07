
ANOMALY_DESC_PROMPT='''
Please describe the following anomaly event in natural language:  
{anomaly_str}

Note do not miss any important information in each line of the event. And the description templates should be like: 

1. "During the inspection, it was found that from xx to xx time, the database's CPU usage was relatively high, approximately 80% to 90%. It is a *critical problem*, please solve it as soon as possible."

2. "During the inspection, it was found that from xx to xx time, the database's CPU usage was relatively high, approximately 80% to 90%. It is just a *warning*, please take time to solve it carefully."
'''

ANOMALY_TITLE_PROMPT='''
Please give a title for the following anomaly event within 15 words:
{anomaly_str}

Note the title template is like: 
Analysis Report of High CPU Usage
'''

