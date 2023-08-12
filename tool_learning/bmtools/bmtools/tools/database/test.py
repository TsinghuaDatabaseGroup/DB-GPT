from bmtools.agent.singletool import load_single_tools, STQuestionAnswerer
import json
import pdb

# read a json file
def read_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    return data

# save a json file
def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


tool_name, tool_url = 'database',  "http://127.0.0.1:8079/tools/database/"
tool_name, tool_config = load_single_tools(tool_name, tool_url)
print(tool_name, tool_config)
stqa =  STQuestionAnswerer()

agent = stqa.load_tools(tool_name, tool_config, prompt_type="react-with-tool-description") # langchain: react-with-tool-description

# read json from the rule-sql file
rule_sql = read_json("calcite_rules_filtered.json")

rule_sql = rule_sql[:2]

for sample in rule_sql:

    input_sql = sample["input_sql"]
    output_sql = sample["output_sql"]

    # langchain
    agent(""" Decide the transformation api that can convert the input sql into the output sql.

    The input sql is: \"{}\"

    The output sql is: \"{}\"

    Note. 1) Only obtain the database schema once;
    2) If an API is successfully called, do not call the same API again; 
    3) Do not use any image in the output; 
    """.format(input_sql, output_sql))

# # langchain
# agent(""" You are a query optimizer.

# First rewrite the SQL query by choosing some logical rewrite rules one by one.

# Next, obtain the physical plan of the rewritten SQL query and optimize some bad phsyical operators if the plan is not good enough.

# Finally, output the optimzed physical plan / optimized SQL+hints.

# You can execute the following actions:
# 1) Estimate the cost of the input query, taken as 'origin cost'.

# 2) Select a logical rule to rewrite the query, an API whose name is ended with '_rule'.

# 3) Select a physical hint to optimize the query, an API whose name is started with 'enable_or_disable_'.

# 4) Change the selection strategy of logical rules and physical hints if the feedback cost is higher than the origin cost.

# 5) Use the matched knowledge to select similar logical rules and physical hints.

# 6) Give optimization advice (e.g., creating indexes) if failing to reduce the feedback cost.

# Note. 1) Only obtain the database schema once;
# 2) If an API is successfully called, do not call the same API again; 
# 3) Do not use any image in the output; 
# """.format(text))

# for each sql pair, as what rule has been used to gain the pair, and save the action in a new json file

# autogpt
# agent.run([""" First get the database schema via get_database_schema. Next generate the sql query exactly based on the schema and the following description:
# \"{}\" 

# Next rewrite the SQL query and output the total number of rows in the database results of the rewritten SQL query.

# Note. 1) Only obtain the database schema once;
# 2) If an API is successfully called, do not call the same API again; 
# 3) Do not use any image in the output; 
# 4) The db_name is tpch10x; 
# 5) Count the rows of query results by your own and do not output the whole query results.
# """.format(text)])

# # unit test: get_database_schema
# agent.run([""" 
# Fetch the database schema from a postgresql database named tpch10x.\"
# """])

# # unit test: rewrite_sql
# agent("Rewrite the input query: select * from customer limit 2")

# # unit test: select_database_data
# agent(""" 
# Output the total number of rows in the query results from a postgresql database based on the following description: 

# \"Retrieve all the data from the 'customer' table and limit the output to only the first 2 rows.\"
# """)

''' output (autogpt)
> Entering new LLMChain chain...
Prompt after formatting:
System: You are Tom, Assistant
Your decisions must always be made independently 
            without seeking user assistance. Play to your strengths 
            as an LLM and pursue simple strategies with no legal complications. 
            If you have completed all your tasks, 
            make sure to use the "finish" command.

GOALS:

{input prompt}

Constraints:
1. ~4000 word limit for short term memory. Your short term memory is short, so immediately save important information to files.
2. If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.
3. No user assistance
4. Exclusively use the commands listed in double quotes e.g. "command name"

Commands:
1. get_database_schema: . Your input should be a json (args json schema): {{"db_name" : string, }} The Action to trigger this API should be get_database_schema and the input parameters should be a json dict string. Pay attention to the type of parameters.
2. select_database_data: Read the data stored in database. Your input should be a json (args json schema): {{"query" : string, }} The Action to trigger this API should be select_database_data and the input parameters should be a json dict string. Pay attention to the type of parameters.
3. rewrite_sql: Get rewritten sql from rewriter. Your input should be a json (args json schema): {{"sql" : string, }} The Action to trigger this API should be rewrite_sql and the input parameters should be a json dict string. Pay attention to the type of parameters.
4. finish: use this to signal that you have finished all your objectives, args: "response": "final response to let people know you have finished your objectives"

Resources:
1. Internet access for searches and information gathering.
2. Long Term memory management.
3. GPT-3.5 powered Agents for delegation of simple tasks.
4. File output.

Performance Evaluation:
1. Continuously review and analyze your actions to ensure you are performing to the best of your abilities.
2. Constructively self-criticize your big-picture behavior constantly.
3. Reflect on past decisions and strategies to refine your approach.
4. Every command has a cost, so be smart and efficient. Aim to complete tasks in the least number of steps.

You should only respond in JSON format as described below 
Response Format: 
{
    "thoughts": {
        "text": "thought",
        "reasoning": "reasoning",
        "plan": "- short bulleted\n- list that conveys\n- long-term plan",
        "criticism": "constructive self-criticism",
        "speak": "thoughts summary to say to user"
    },
    "command": {
        "name": "command name",
        "args": {
            "arg name": "value"
        }
    }
} 
Ensure the response can be parsed by Python json.loads
System: The current time and date is Wed Apr 26 11:02:25 2023
System: This reminds you of these events from your past:
[]

Human: Determine which next command to use, and respond using the format specified above:

> Finished chain.


{
    "thoughts": {
        "text": "Since the 'get_database_schema' command did not work, I will try to retrieve the schema manually. I will use the following SQL query to retrieve the schema: 'SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public' ORDER BY table_name, ordinal_position;'",
        "reasoning": "If the 'get_database_schema' command is not working, I can manually retrieve the schema using an SQL query. This query will retrieve the names of all the tables and columns in the 'public' schema of the database.",
        "plan": "- Use the SQL query 'SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public' ORDER BY table_name, ordinal_position;' to retrieve the schema\n- Generate SQL query based on given description\n- Use 'select_database_data' command to retrieve query results\n- Count number of rows in query results using Python code",
        "criticism": "I need to make sure that I am using the correct table and column names from the schema in the SQL query. I also need to make sure that I am using the correct syntax for the SQL query.",
        "speak": "I will try to retrieve the schema manually using an SQL query."
    },
    "command": {
        "name": "select_database_data",
        "args": {
            "query": "SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public' ORDER BY table_name, ordinal_position;"
        }
    }
}

'''