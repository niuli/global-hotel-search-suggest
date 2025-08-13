#!/bin/bash

echo "=== 启动Spring Boot酒店搜索服务 ==="

# 设置Java环境
source "$HOME/.sdkman/bin/sdkman-init.sh"

# 检查Java版本
echo "Java版本:"
java -version

# 检查Maven版本
echo "Maven版本:"
mvn -version

# 清理并编译
echo "清理并编译项目..."
mvn clean compile

if [ $? -eq 0 ]; then
    echo "编译成功！"
    
    # 安装到本地仓库
    echo "安装到本地仓库..."
    mvn clean install -DskipTests
    
    if [ $? -eq 0 ]; then
        echo "安装成功！"
        
        # 启动Spring Boot应用
        echo "启动Spring Boot应用..."
        echo "端口: 8080"
        echo "访问地址: http://localhost:8080"
        echo "API测试: curl \"http://localhost:8080/api/v1/hotel/suggest?q=东京\""
        echo "====================================="
        
        mvn spring-boot:run -pl hs-webapp
    else
        echo "安装失败！"
        exit 1
    fi
else
    echo "编译失败！"
    exit 1
fi 