#!/bin/bash

echo "=== 启动酒店搜索Java服务器 ==="

# 设置Java环境
source "$HOME/.sdkman/bin/sdkman-init.sh"

# 编译服务器
echo "编译服务器..."
javac -cp "hs-dao/target/classes:hs-core/target/classes:$(mvn dependency:build-classpath -q -Dmdep.outputFile=/dev/stdout)" SimpleJavaServer.java

if [ $? -eq 0 ]; then
    echo "编译成功！"
    
    # 启动服务器
    echo "启动服务器..."
    java -cp ".:hs-dao/target/classes:hs-core/target/classes:$(mvn dependency:build-classpath -q -Dmdep.outputFile=/dev/stdout)" SimpleJavaServer
else
    echo "编译失败！"
    exit 1
fi 