import requests
MetaAgentvere_URL = "http://configuration_expert"

# 将获取到的数据发送到MetaAgentvere，启动一个任务
requests.post(
    MetaAgentvere_URL + ":5050/launch_goal",
    json={
        "goal": "Here is the anomaly detection result. You should discuss and come up with a plan with detailed anaylsis based on the information. Here is the information: ",
        "team_up_depth": 1,  # the depth limit of nested teaming up
    },
)
