import json
import os
import time
import subprocess
from fastapi import File, UploadFile, Body
from configs import (
    DIAGNOSTIC_FILES_PATH,
    DIAGNOSTIC_CONFIG_FILE,
    DIAGNOSE_RUN_LOG_PATH,
    DIAGNOSE_RUN_PID_PATH,
    DIAGNOSE_USER_FEEDBACK_PATH,
    DIAGNOSE_RUN_DATA_PATH)
import threading
from server.utils import BaseResponse, save_file

current_task = {"thread": None, "output": "", "process": None}

THREADNAME = "run_diagnose"


def status():
    threads = threading.enumerate()
    runing = False
    for thread in threads:
        if thread.name == THREADNAME:
            runing = True
            break
    return runing


def diagnose_status():
    return BaseResponse(code=200, msg="Success", data={"is_alive": status()})


def run_diagnose_script(file_path: str, config_file_path: str = "config.yaml"):
    with open(DIAGNOSE_RUN_LOG_PATH, 'w') as log_txt:
        cmd = [
            "python3",
            f"{os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))}/run_diagnose.py",
            "--anomaly_file",
            file_path,
            "--config_file",
            config_file_path
        ]
        process = subprocess.Popen(
            cmd,
            shell=False,
            stdout=log_txt,
            stderr=log_txt)
        with open(DIAGNOSE_RUN_PID_PATH, "w") as pid_file:
            pid_file.write(str(process.pid))
        process.wait(3600)


def save_diagnose_file(file: UploadFile = File(..., description="上传文件")):
    try:
        save_file_result = save_file(DIAGNOSTIC_FILES_PATH, file, True)
        file_path = save_file_result["data"]["file_path"]
        with open(file_path, "r") as f:
            anomaly_json = json.load(f)
        return BaseResponse(
            code=200,
            msg="Success",
            data={
                "file_path": file_path,
                "anomaly_json": anomaly_json})
    except Exception as e:
        return BaseResponse(code=500, msg=f"Failed to save file: {e}")


def run_diagnose(file: UploadFile = File(..., description="上传文件，支持多文件")):

    if status():
        return BaseResponse(code=500, msg="A task is already running")

    save_file_result = save_file(DIAGNOSTIC_FILES_PATH, file, True)
    file_path = save_file_result["data"]["file_path"]

    with open(DIAGNOSE_RUN_LOG_PATH, "w") as f:
        f.write("")

    t = threading.Thread(
        target=run_diagnose_script,
        args=(file_path, DIAGNOSTIC_CONFIG_FILE),
        name=THREADNAME)
    t.start()

    time.sleep(5)

    if status():
        return BaseResponse(code=200, msg="Success")
    else:
        return BaseResponse(
            code=500,
            msg="Failed to start diagnose task, error is " +
            log_output())


def stop_diagnose():
    current_run_pid = open(DIAGNOSE_RUN_PID_PATH, "r+")
    pid = current_run_pid.readline()
    subprocess.run("kill -9 " + pid + "", shell=True)
    current_run_pid.close()
    time.sleep(3)
    if status():
        return BaseResponse(
            code=500,
            msg="Failed to stop diagnose task, Please try again")
    else:
        return BaseResponse(code=200, msg="Success")


def log_output():

    if not os.path.exists(DIAGNOSE_RUN_LOG_PATH):
        with open(DIAGNOSE_RUN_LOG_PATH, "w") as f:
            f.write("")

    with open(DIAGNOSE_RUN_LOG_PATH, "r") as config_file:
        lines = config_file.readlines()
        content = ""
        for line in lines:
            content += line
        return content


def get_diagnose_terminal_output():
    return BaseResponse(code=200, msg="Success", data={"output": log_output()})


def get_diagnose_serialization_output():
    file_path = DIAGNOSE_RUN_DATA_PATH
    if not os.path.exists(file_path):
        return BaseResponse(code=404, msg="无对应的诊断文件")
    if file_path.endswith(".json") or file_path.endswith(".jsonl"):
        # 打开文件并读取JSON数据
        with open(file_path, "r") as file:
            json_data = json.load(file)
            return BaseResponse(code=200, msg="Success", data=json_data)
    else:
        return BaseResponse(code=400, msg="无对应的文件")

def diagnose_user_feedback(
        user_input: str = Body(..., description="用户输入", examples=["yes"], embed=True),
) -> BaseResponse:
    if not status():
        return BaseResponse(code=500, msg="Diagnose is not running")
    if not user_input:
        return BaseResponse(code=500, msg="User input is empty")
    with open(DIAGNOSE_USER_FEEDBACK_PATH, "w") as f:
        f.write(user_input)
    return BaseResponse(code=200, msg="Success")
