import json
import os
import requests

import openai

openai.api_key = os.environ["OPENAI_API_KEY"]

schema = "{\'part\': [\'p_partkey\', \'p_name\', \'p_mfgr\', \'p_brand\', \'p_type\', \'p_size\', \'p_container\', \'p_retailprice\', \'p_comment\'], \'supplier\': [\'s_suppkey\', \'s_name\', \'s_address\', \'s_nationkey\', \'s_phone\', \'s_acctbal\', \'s_comment\'], \'partsupp\': [\'ps_partkey\', \'ps_suppkey\', \'ps_availqty\', \'ps_supplycost\', \'ps_comment\'], \'customer\': [\'c_custkey\', \'c_name\', \'c_address\', \'c_nationkey\', \'c_phone\', \'c_acctbal\', \'c_mktsegment\', \'c_comment\'], \'orders\': [\'o_orderkey\', \'o_custkey\', \'o_orderstatus\', \'o_totalprice\', \'o_orderdate\', \'o_orderpriority\', \'o_clerk\', \'o_shippriority\', \'o_comment\'], \'lineitem\': [\'l_orderkey\', \'l_partkey\', \'l_suppkey\', \'l_linenumber\', \'l_quantity\', \'l_extendedprice\', \'l_discount\', \'l_tax\', \'l_returnflag\', \'l_linestatus\', \'l_shipdate\', \'l_commitdate\', \'l_receiptdate\', \'l_shipinstruct\', \'l_shipmode\', \'l_comment\'], \'nation\': [\'n_nationkey\', \'n_name\', \'n_regionkey\', \'n_comment\'], \'region\': [\'r_regionkey\', \'r_name\', \'r_comment\']}"
description = "Retrieve the comments of suppliers, size of parts, and supply cost of part-supplier combinations where the available quantity of the part is 6331, the type of the part is greater than 'LARGE POLISHED NICKEL', and the retail price of the part is less than 1758.76. The results should be sorted in descending order based on the comments of the suppliers."

prompt = """Translate the natural language description into an semantic equivalent SQL query.
The table and column names used in the sql must exactly appear in the schema. Any other table and column names are unacceptable.
The schema is:\n
{}

The description is:\n
{}

The SQL query is:
""".format(schema, description)

# Set up the OpenAI GPT-3 model
model_engine = "gpt-3.5-turbo"
prompt_response = openai.ChatCompletion.create(
    model=model_engine,
    messages=[
        {"role": "assistant", "content": "The table schema is as follows: " + schema},
        {"role": "user", "content": prompt}
        ]
)

output_text = prompt_response['choices'][0]['message']['content']

print(output_text)
