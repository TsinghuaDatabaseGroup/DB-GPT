
DIAGNOSIS_SUMMARYY_PROMPT='''
Please provide a searchable summary of the input document without lossing important information. The input is as follows:
{document text}

=============
Note 
1. you are an expert and do not miss any important information!!!
2. response with only the summary content. Do not add any additional content!!!
3. the summary should be within {max words} characters.
4. Do not say anything like "As an AI"!!
5. If the input text is in english, the summary should be english. If the input text is in chinese, the summary should be chinese.
'''