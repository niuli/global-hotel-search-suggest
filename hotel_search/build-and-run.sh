#!/bin/bash

# Hotel Search Maven Build and Run Script
# 酒店搜索系统编译启动脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="hotel-search"
MAIN_CLASS="com.qunar.hotel.search.webapp.HotelSearchApplication"
JAR_NAME="hotel-search-deploy-1.0.0.jar"
PORT=8080
PID_FILE="hotel-search.pid"
LOG_FILE="hotel-search.log"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Java版本
check_java() {
    print_info "检查Java版本..."
    if ! command -v java &> /dev/null; then
        print_error "Java未安装，请先安装Java 17或更高版本"
        exit 1
    fi
    
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f1)
    if [ "$JAVA_VERSION" -lt 17 ]; then
        print_error "Java版本过低，需要Java 17或更高版本，当前版本: $JAVA_VERSION"
        exit 1
    fi
    
    print_success "Java版本检查通过: $(java -version 2>&1 | head -n 1)"
}

# 检查Maven
check_maven() {
    print_info "检查Maven..."
    if ! command -v mvn &> /dev/null; then
        print_error "Maven未安装，请先安装Maven"
        exit 1
    fi
    
    print_success "Maven版本: $(mvn -version | head -n 1)"
}

# 清理项目
clean_project() {
    print_info "清理项目..."
    mvn clean
    print_success "项目清理完成"
}

# 编译项目
compile_project() {
    print_info "编译项目..."
    mvn compile -q
    print_success "项目编译完成"
}

# 运行测试
run_tests() {
    print_info "运行测试..."
    if mvn test -q; then
        print_success "测试通过"
    else
        print_warning "测试失败，但继续构建"
    fi
}

# 打包项目
package_project() {
    print_info "打包项目..."
    mvn package -DskipTests -q
    print_success "项目打包完成"
}

# 检查服务是否已运行
check_service_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # 服务正在运行
        else
            rm -f "$PID_FILE"
        fi
    fi
    return 1  # 服务未运行
}

# 停止服务
stop_service() {
    if check_service_running; then
        print_info "停止现有服务..."
        PID=$(cat "$PID_FILE")
        kill "$PID" 2>/dev/null || true
        sleep 2
        if ps -p "$PID" > /dev/null 2>&1; then
            print_warning "强制停止服务..."
            kill -9 "$PID" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
        print_success "服务已停止"
    else
        print_info "服务未运行"
    fi
}

# 启动服务
start_service() {
    print_info "启动酒店搜索服务..."
    
    # 检查JAR文件是否存在
    JAR_PATH="target/$JAR_NAME"
    if [ ! -f "$JAR_PATH" ]; then
        print_error "JAR文件不存在: $JAR_PATH"
        print_info "请先运行编译和打包步骤"
        exit 1
    fi
    
    # 检查端口是否被占用
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口 $PORT 已被占用，尝试停止占用进程..."
        lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # 启动服务
    nohup java -jar "$JAR_PATH" > "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    
    print_info "服务启动中，PID: $PID"
    print_info "日志文件: $LOG_FILE"
    
    # 等待服务启动
    sleep 3
    
    # 检查服务是否成功启动
    if check_service_running; then
        print_success "酒店搜索服务启动成功！"
        print_info "服务地址: http://localhost:$PORT"
        print_info "API文档: http://localhost:$PORT/swagger-ui.html (如果配置了Swagger)"
        print_info "停止服务: ./build-and-run.sh stop"
        print_info "查看日志: tail -f $LOG_FILE"
    else
        print_error "服务启动失败，请检查日志: $LOG_FILE"
        exit 1
    fi
}

# 显示服务状态
show_status() {
    if check_service_running; then
        PID=$(cat "$PID_FILE")
        print_success "服务正在运行，PID: $PID"
        print_info "服务地址: http://localhost:$PORT"
        print_info "日志文件: $LOG_FILE"
    else
        print_info "服务未运行"
    fi
}

# 显示日志
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        print_warning "日志文件不存在"
    fi
}

# 显示帮助信息
show_help() {
    echo "酒店搜索系统编译启动脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  build     编译和打包项目"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  status    显示服务状态"
    echo "  logs      显示服务日志"
    echo "  clean     清理项目"
    echo "  test      运行测试"
    echo "  full      完整构建和启动（清理+编译+测试+打包+启动）"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 full    # 完整构建和启动"
    echo "  $0 start   # 仅启动服务"
    echo "  $0 stop    # 停止服务"
}

# 主函数
main() {
    case "${1:-help}" in
        "build")
            check_java
            check_maven
            clean_project
            compile_project
            package_project
            ;;
        "start")
            start_service
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            stop_service
            sleep 2
            start_service
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "clean")
            check_maven
            clean_project
            ;;
        "test")
            check_java
            check_maven
            run_tests
            ;;
        "full")
            check_java
            check_maven
            clean_project
            compile_project
            run_tests
            package_project
            start_service
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@" 