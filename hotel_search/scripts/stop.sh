#!/bin/bash

# 酒店搜索服务停止脚本

PID_FILE="hotel-search.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo "正在停止酒店搜索服务 (PID: $PID)..."
    
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        echo "已发送停止信号"
        
        # 等待进程结束
        for i in {1..10}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                echo "✅ 服务已停止"
                rm -f "$PID_FILE"
                exit 0
            fi
            sleep 1
        done
        
        # 强制停止
        echo "强制停止服务..."
        kill -9 "$PID"
        rm -f "$PID_FILE"
        echo "✅ 服务已强制停止"
    else
        echo "服务未运行"
        rm -f "$PID_FILE"
    fi
else
    echo "PID文件不存在，服务可能未运行"
fi 