import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()

@app.get('/test')
async def test():
    return {
        "code": 0,
        "msg": "success",
        "data": "webhook is running"
    }

@app.post('/alert')
async def alert(request: Request):
    """
    return add alert
    :return:
    """
    args = await request.json()
    # 将obj写入文件中
    with open("alert.txt", "a") as f:
        f.write(str(args) + "\n")
    return {
        "code": 0,
        "msg": "success",
        "data": ""
    }

if __name__ == "__main__":
    uvicorn.run(
        app = app,
        host = "0.0.0.0",
        port = 8023
    )
