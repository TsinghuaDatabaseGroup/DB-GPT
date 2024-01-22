from subprocess import Popen, PIPE
from fastapi import File, UploadFile
from configs import (logger, ORIGINAL_KNOWLEDGE_FILES_PATH, )
from typing import Iterator
import threading
from server.utils import BaseResponse, save_file

current_task = {"thread": None, "output": ""}

def run_knowledge_extraction_script(file_path: str) -> Iterator[str]:
    try:
        process = Popen(["python3", "run_diagnose.py", "--anomaly_file", file_path], stdout=PIPE, text=True)
        current_task["output"] = ""
        while True:
            output = process.stdout.readline()
            if process.poll() is not None and output == '':
                break
            if output:
                print('诊断输出:', output.strip())
                current_task["output"] += f"{output.strip()}\n"
    except Exception as e:
        error_message = f"Error executing task: {e}"
        logger.error(error_message)
        current_task["output"] += error_message


def run_knowledge_extraction(file: UploadFile = File(..., description="上传文件，支持多文件")):
    if current_task["thread"] and current_task["thread"].is_alive():
        return BaseResponse(code=400, msg="A task is already running")
    save_file_result = save_file(ORIGINAL_KNOWLEDGE_FILES_PATH, file, True)
    file_path = save_file_result["data"]["file_path"]

    current_task["thread"] = threading.Thread(target=run_knowledge_extraction_script, args=(file_path,), name='KnowledgeExtraction')
    current_task["thread"].start()
    current_task["thread"].join(5)

    # 检查线程是否仍在运行
    if current_task["thread"].is_alive():
        # 任务在2秒后仍在运行，因此我们假设它已成功启动并将继续运行
        return BaseResponse(code=200, msg="Success")
    else:
        # 任务在2秒后已经完成，可能是由于出错而结束
        # 我们从输出中获取错误消息，如果没有输出，那就默认一个错误消息
        error_message = current_task["output"] if current_task["output"] else "An unknown error occurred."
        return BaseResponse(code=500, msg=error_message)


def get_knowledge_extraction_output():
    is_alive = current_task["thread"] and current_task["thread"].is_alive()
    msg = "Success" if is_alive else "No task is running"
    return BaseResponse(code=200, msg=msg, data={"is_alive": is_alive, "output": current_task["output"]})

