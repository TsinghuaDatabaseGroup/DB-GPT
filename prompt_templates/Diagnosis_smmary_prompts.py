
DIAGNOSIS_SUMMARYY_PROMPT='''
Please provide a searchable summary of the input diagnosis procedures or recommended solutions without lossing important information. The input is as follows:
{diagnosis_messages}

=============
Note 
1. you are an expert and do not miss any important information!!!
2. response with a list of key points of the input diagnosis procedures or recommended solutions (e.g. "1. ...<br>2. ...<br>3. ..."). Do not add any additional content!!!
3. The key points should be strictly separated by <br> ("1. ...<br>2. ...<br>3. ...")!!!! Do not use markdown format and # headings!!!
4. Do not mention anything about what are the charts like!! Ignore charts!!!
5. Do not say anything like "As an AI"!!
'''