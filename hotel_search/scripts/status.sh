#!/bin/bash

# 酒店搜索服务状态检查脚本

PID_FILE="hotel-search.pid"
PORT=${PORT:-8080}

echo "=== 酒店搜索服务状态 ==="

# 检查PID文件
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "✅ 服务正在运行 (PID: $PID)"
    else
        echo "❌ 服务未运行 (PID文件存在但进程不存在)"
        rm -f "$PID_FILE"
    fi
else
    echo "❌ 服务未运行 (PID文件不存在)"
fi

# 检查端口
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ 端口 $PORT 正在监听"
else
    echo "❌ 端口 $PORT 未监听"
fi

# 健康检查
echo "=== 健康检查 ==="
if curl -s "http://localhost:$PORT/health" >/dev/null 2>&1; then
    echo "✅ 健康检查通过"
    echo "服务响应:"
    curl -s "http://localhost:$PORT/health" | python3 -m json.tool 2>/dev/null || curl -s "http://localhost:$PORT/health"
else
    echo "❌ 健康检查失败"
fi

# API测试
echo "=== API测试 ==="
if curl -s "http://localhost:$PORT/api/v1/hotel/stats" >/dev/null 2>&1; then
    echo "✅ API接口正常"
    echo "服务统计:"
    curl -s "http://localhost:$PORT/api/v1/hotel/stats" | python3 -m json.tool 2>/dev/null || curl -s "http://localhost:$PORT/api/v1/hotel/stats"
else
    echo "❌ API接口异常"
fi 