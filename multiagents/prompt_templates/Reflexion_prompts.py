# MAKE_REFLEXION_PROMPT ='''I failed in the former tries, and I need to rethink the task.
# Then I will analyze the steps I took former and tell the reason I failed in the last try. I wiil make a reflexion.
# The "Reflexion" ends with pattern "END REFLEXION"
# Reflexion: '''

MAKE_REFLEXION_PROMPT='''
{task_description}
{input_description}
Here is your former try:
{former_trice}{new_trice}
You will be given the history of a past experience in which you were placed in an environment and given a task to complete. You were unsuccessful in completing the task. Do not summarize your environment, but rather think about the strategy and path you took to attempt to complete the task. Devise a concise, new plan of action that accounts for your mistake with reference to specific actions that you should have taken. For example, if you tried A and B but forgot C, then devise a plan to achieve C with environment-specific actions. You will need this later when you are solving the same task. Give your plan after "PLAN".
Reflection: '''

MAKE_REFLEXION_USER_PROMPT_='''
Now That you lose in the former try, you were unsuccessful in completing the task. You will make a reflection of the former lose.
Do not summarize your environment, but rather think about the strategy and path you took to attempt to complete the task. Devise a concise, new plan of action that accounts for your mistake with reference to specific actions that you should have taken. For example, if you tried A and B but forgot C, then devise a plan to achieve C with environment-specific actions. You will need this later when you are solving the same task. Give your plan after "PLAN".'''

# MAKE_REFLEXION_USER_PROMPT='''
# Remember that you are performing a mento-carlo search. Now That you lose in the former try, you were unsuccessful in completing the task. You will make a reflection of the former lose.
# The reflection information can be inherit to later trails:
# 1.reflections is short, at most 5 sentence.
# 2.reflections give knowledge of the task you are performing.
# Begin!
# '''


MAKE_REFLEXION_USER_PROMPT='''
Remember that you are performing a mento-carlo search. Now That you have done an unsatisfied attempt in the former try, you were imperfect in completing the task. You will make a reflection of the former attempt.
The reflection information can be inherit to later trails:
1.reflections is short, at most 5 sentence.
2.reflections give knowledge of the task you are performing.
Begin!
'''

CAT_REFLEXION_USER_PROMPT = '''Now, let's start over and follow the revised plan. Hope you can do better. The enviornment restarted.'''


CAT_REFLEXION_PROMPT = '''
Reflexion: {reflexion}
Now with the reflexion of former fault in my mind, I will restart the task and do better:
{task_input}
'''