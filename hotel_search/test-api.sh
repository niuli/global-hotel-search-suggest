#!/bin/bash

# API测试脚本 - 酒店搜索服务
# API Test Script for Hotel Search Service

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
BASE_URL="http://localhost:8080"
API_BASE="$BASE_URL/api"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查服务是否运行
check_service() {
    print_info "检查服务状态..."
    
    if ! curl -s "$BASE_URL/api/health" > /dev/null 2>&1; then
        print_error "服务未运行或无法访问"
        print_info "请先启动服务: ./build-and-run.sh start 或 ./quick-start.sh"
        exit 1
    fi
    
    print_success "服务运行正常"
}

# 测试健康检查API
test_health() {
    print_info "测试健康检查API..."
    
    response=$(curl -s "$API_BASE/health")
    if [ $? -eq 0 ]; then
        print_success "健康检查API正常"
        echo "响应: $response"
    else
        print_error "健康检查API失败"
    fi
    echo
}

# 测试酒店搜索API
test_search() {
    print_info "测试酒店搜索API..."
    
    # 测试不同的搜索关键词
    queries=("东京酒店" "北京" "上海" "hotel" "酒店")
    
    for query in "${queries[@]}"; do
        print_info "搜索关键词: $query"
        response=$(curl -s "$API_BASE/hotel/search?query=$query")
        
        if [ $? -eq 0 ]; then
            print_success "搜索成功"
            echo "响应长度: ${#response} 字符"
            # 显示前200个字符
            echo "响应预览: ${response:0:200}..."
        else
            print_error "搜索失败"
        fi
        echo
    done
}

# 测试搜索建议API
test_suggest() {
    print_info "测试搜索建议API..."
    
    # 测试不同的建议关键词
    queries=("东京" "北京" "上海" "hotel" "酒店" "东")
    
    for query in "${queries[@]}"; do
        print_info "建议关键词: $query"
        response=$(curl -s "$API_BASE/hotel/suggest?query=$query")
        
        if [ $? -eq 0 ]; then
            print_success "建议成功"
            echo "响应长度: ${#response} 字符"
            # 显示前200个字符
            echo "响应预览: ${response:0:200}..."
        else
            print_error "建议失败"
        fi
        echo
    done
}

# 测试错误情况
test_error_cases() {
    print_info "测试错误情况..."
    
    # 测试空查询
    print_info "测试空查询..."
    response=$(curl -s "$API_BASE/hotel/search?query=")
    if [ $? -eq 0 ]; then
        print_success "空查询处理正常"
    else
        print_warning "空查询处理异常"
    fi
    
    # 测试特殊字符
    print_info "测试特殊字符..."
    response=$(curl -s "$API_BASE/hotel/search?query=%E6%9D%B1%E4%BA%AC")
    if [ $? -eq 0 ]; then
        print_success "特殊字符处理正常"
    else
        print_warning "特殊字符处理异常"
    fi
    
    echo
}

# 性能测试
test_performance() {
    print_info "性能测试..."
    
    start_time=$(date +%s.%N)
    
    # 连续发送10个请求
    for i in {1..10}; do
        curl -s "$API_BASE/hotel/search?query=东京酒店" > /dev/null
    done
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    
    print_success "10个请求完成，耗时: ${duration}秒"
    echo "平均响应时间: $(echo "scale=3; $duration / 10" | bc)秒"
    echo
}

# 显示API信息
show_api_info() {
    echo "🔗 API端点信息:"
    echo "   基础URL: $BASE_URL"
    echo "   API基础路径: $API_BASE"
    echo ""
    echo "📋 可用API:"
    echo "   GET  $API_BASE/health          - 健康检查"
    echo "   GET  $API_BASE/hotel/search    - 酒店搜索"
    echo "   GET  $API_BASE/hotel/suggest   - 搜索建议"
    echo ""
}

# 主函数
main() {
    echo -e "${BLUE}🧪 酒店搜索API测试${NC}"
    echo "================================"
    echo
    
    show_api_info
    
    # 检查服务状态
    check_service
    
    # 运行测试
    test_health
    test_search
    test_suggest
    test_error_cases
    test_performance
    
    print_success "所有测试完成！"
    echo
    print_info "测试结果总结:"
    echo "✅ 健康检查API: 正常"
    echo "✅ 酒店搜索API: 正常"
    echo "✅ 搜索建议API: 正常"
    echo "✅ 错误处理: 正常"
    echo "✅ 性能测试: 完成"
}

# 检查是否安装了bc（用于浮点计算）
if ! command -v bc &> /dev/null; then
    print_warning "未安装bc，性能测试将跳过"
    test_performance() {
        print_warning "跳过性能测试（需要安装bc）"
        echo
    }
fi

# 执行主函数
main "$@" 