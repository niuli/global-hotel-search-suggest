#!/bin/bash

# 快速启动脚本 - 酒店搜索服务
# Quick Start Script for Hotel Search Service

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 酒店搜索服务快速启动${NC}"
echo "=================================="

# 检查Java和Maven
echo -e "${BLUE}📋 检查环境...${NC}"
if ! command -v java &> /dev/null; then
    echo -e "${RED}❌ Java未安装${NC}"
    exit 1
fi

if ! command -v mvn &> /dev/null; then
    echo -e "${RED}❌ Maven未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 环境检查通过${NC}"

# 清理并编译
echo -e "${BLUE}🔨 编译项目...${NC}"
mvn clean package -DskipTests -q
echo -e "${GREEN}✅ 编译完成${NC}"

# 检查JAR文件
JAR_FILE="target/hotel-search-deploy-1.0.0.jar"
if [ ! -f "$JAR_FILE" ]; then
    echo -e "${RED}❌ JAR文件不存在: $JAR_FILE${NC}"
    exit 1
fi

# 停止现有服务
echo -e "${BLUE}🛑 停止现有服务...${NC}"
pkill -f "hotel-search-deploy" 2>/dev/null || true
sleep 2

# 启动服务
echo -e "${BLUE}🚀 启动服务...${NC}"
nohup java -jar "$JAR_FILE" > hotel-search.log 2>&1 &
PID=$!

# 等待启动
sleep 5

# 检查服务状态
if ps -p $PID > /dev/null; then
    echo -e "${GREEN}✅ 服务启动成功！${NC}"
    echo "📊 服务信息:"
    echo "   PID: $PID"
    echo "   URL: http://localhost:8080"
    echo "   日志: hotel-search.log"
    echo ""
    echo "🔗 可用API:"
    echo "   - 搜索: GET /api/hotel/search?query=酒店名"
    echo "   - 建议: GET /api/hotel/suggest?query=关键词"
    echo "   - 健康检查: GET /api/health"
    echo ""
    echo "💡 停止服务: pkill -f hotel-search-deploy"
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    echo "请检查日志文件: hotel-search.log"
    exit 1
fi 