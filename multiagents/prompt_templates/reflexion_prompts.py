# MAKE_REFLEXION_PROMPT ='''I failed in the former tries, and I need to rethink the task.
# Then I will analyze the steps I took former and tell the reason I failed in the last try. I will make a reflexion.
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
3.reflections give tool APIs that you can use but not used in the former try.
Begin!
'''

MAKE_REFLEXION_USER_PROMPT_zh = '''
请注意，你正在执行蒙特卡洛搜索。现在你对前一次的尝试不太满意，请进行反思。
反思的信息可以继承到后续的尝试，反思的信息必须满足：
1. 反思信息比较短，最多不超过5句话。
2. 反思能让你更了解自己执行的任务。
3. 反思能给出工具API，你可以使用但是在前一次尝试中没有使用。
反思的回复无需调用工具，无需按照模板，没有固定格式。
'''


CAT_REFLEXION_USER_PROMPT = '''Now, let's start over and follow the revised plan. Hope you can do better. The environment restarted.'''


CAT_REFLEXION_PROMPT = '''
Reflexion: {reflexion}
Now with the reflexion of former fault in my mind, I will restart the task and do better:
{task_input}
'''