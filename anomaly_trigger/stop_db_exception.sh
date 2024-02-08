#!/bin/bash

pid=`ps -ef| grep "python3 DBException.py"|grep -v grep|awk '{print $2}'|uniq`
if [[ -n "$pid" ]]
then
  echo "结束DBException进程, 进程PID为： $pid"
  kill -9 $pid
else
  echo "DBException未运行!"
  exit -1
fi
