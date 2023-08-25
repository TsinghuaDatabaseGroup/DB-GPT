#!/usr/bin/env sh

# 切换到前端目录并启动开发服务器
cd front_demo && npm run dev &

# 启动Flask APP
python3 app.py


