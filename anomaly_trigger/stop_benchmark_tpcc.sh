#!/bin/bash

pid=`ps -ef| grep "./tpcc.lua"|grep -v grep|awk '{print $2}'|uniq`
if [[ -n "$pid" ]]
then
  echo "结束Benchmark TPCC进程, 进程PID为： $pid"
  kill -9 $pid
else
  echo "Benchmark TPCC未运行!"
  exit -1
fi
