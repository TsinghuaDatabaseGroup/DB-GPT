
DIAGNOSIS_SUMMARY_PROMPT = '''
Please provide a searchable summary of the input diagnosis procedures or recommended solutions without losing important information. The input is as follows:
{diagnosis_messages}

=============
Note 
1. you are an expert and do not miss any important information!!!
2. response with a list of key points of the input diagnosis procedures or recommended solutions (e.g. "1. ...<br>2. ...<br>3. ..."). Do not add any additional content!!!
3. The key points should be strictly separated by <br> ("1. ...<br>2. ...<br>3. ...")!!!! Do not use markdown format and # headings!!!
4. Do not mention anything about what are the charts like!! Ignore charts!!!
5. Do not say anything like "As an AI"!!
'''

DIAGNOSIS_SUMMARY_PROMPT_zh = '''
给下列诊断过程和推荐的解决方案做一个总结。内容如下：
{diagnosis_messages}

请注意：
1. 不要丢失任何重要信息！
2. 回复用关键点一一列出来（例如 1. ...<br>2. ...<br>3. ...）。不要添加任何额外的内容！
3. 关键点严格用<br>分隔（例如 1. ...<br>2. ...<br>3. ...）。不要使用markdown格式。
4. 不要提任何与图表相关的内容！忽略图表！
'''