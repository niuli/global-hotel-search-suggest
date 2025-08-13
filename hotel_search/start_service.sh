#!/bin/bash

echo "=== 启动酒店搜索服务 ==="

# 设置Java环境
source "$HOME/.sdkman/bin/sdkman-init.sh"

# 检查Java版本
echo "Java版本:"
java -version

# 编译SimpleJavaServer
echo "编译SimpleJavaServer..."
javac -cp "hs-dao/target/classes:hs-core/target/classes:$(mvn dependency:build-classpath -q -Dmdep.outputFile=/dev/stdout)" SimpleJavaServer.java

if [ $? -eq 0 ]; then
    echo "编译成功！"
    
    # 启动服务
    echo "启动服务..."
    echo "端口: 8080"
    echo "访问地址: http://localhost:8080"
    echo "API测试: curl \"http://localhost:8080/api/v1/hotel/suggest?q=东京\""
    echo "====================================="
    
    java -cp ".:hs-dao/target/classes:hs-core/target/classes:$(mvn dependency:build-classpath -q -Dmdep.outputFile=/dev/stdout)" SimpleJavaServer
else
    echo "编译失败！"
    exit 1
fi 