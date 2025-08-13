#!/bin/bash

# 酒店搜索服务启动脚本
# 适用于阿里云部署

# 设置Java环境
export JAVA_HOME=${JAVA_HOME:-/usr/lib/jvm/java-17-openjdk}
export PATH=$JAVA_HOME/bin:$PATH

# 服务配置
APP_NAME="hotel-search"
JAR_FILE="hotel-search-deploy-1.0.0.jar"
PID_FILE="hotel-search.pid"
LOG_FILE="hotel-search.log"
PORT=${PORT:-8080}

# 检查Java环境
if ! command -v java &> /dev/null; then
    echo "错误: 未找到Java环境，请安装Java 17或更高版本"
    exit 1
fi

echo "Java版本:"
java -version

# 检查JAR文件
if [ ! -f "$JAR_FILE" ]; then
    echo "错误: 未找到JAR文件: $JAR_FILE"
    exit 1
fi

# 检查端口是否被占用
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "警告: 端口 $PORT 已被占用"
    echo "正在停止现有服务..."
    if [ -f "$PID_FILE" ]; then
        kill $(cat "$PID_FILE") 2>/dev/null
        rm -f "$PID_FILE"
        sleep 2
    fi
fi

# 启动服务
echo "=== 启动酒店搜索服务 ==="
echo "服务名称: $APP_NAME"
echo "JAR文件: $JAR_FILE"
echo "端口: $PORT"
echo "日志文件: $LOG_FILE"
echo "====================================="

# 启动服务
nohup java -Xms512m -Xmx2g -jar "$JAR_FILE" "$PORT" > "$LOG_FILE" 2>&1 &

# 保存PID
echo $! > "$PID_FILE"

# 等待服务启动
sleep 3

# 检查服务状态
if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
    echo "✅ 服务启动成功！"
    echo "PID: $(cat $PID_FILE)"
    echo "端口: $PORT"
    echo "日志: $LOG_FILE"
    echo "健康检查: curl http://localhost:$PORT/health"
    echo "API测试: curl http://localhost:$PORT/api/v1/hotel/suggest?q=Tokyo"
else
    echo "❌ 服务启动失败！"
    echo "请检查日志文件: $LOG_FILE"
    exit 1
fi 