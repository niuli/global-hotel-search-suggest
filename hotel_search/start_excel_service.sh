#!/bin/bash

echo "=== 启动酒店搜索服务（Excel数据版） ==="

# 设置Java环境
source "$HOME/.sdkman/bin/sdkman-init.sh"

# 检查Java版本
echo "Java版本:"
java -version

# 检查Excel文件
EXCEL_FILE="../日本东京酒店v2.xlsx"
if [ ! -f "$EXCEL_FILE" ]; then
    echo "❌ Excel文件不存在: $EXCEL_FILE"
    echo "请确保Excel文件在正确位置"
    exit 1
fi

echo "✅ 找到Excel文件: $EXCEL_FILE"

# 编译SimpleJavaServerWithExcel
echo "编译SimpleJavaServerWithExcel..."
javac -cp "hs-dao/target/classes:hs-core/target/classes:$(mvn dependency:build-classpath -q -Dmdep.outputFile=/dev/stdout)" SimpleJavaServerWithExcel.java

if [ $? -eq 0 ]; then
    echo "编译成功！"
    
    # 启动服务
    echo "启动服务..."
    echo "端口: 8080"
    echo "数据源: $EXCEL_FILE"
    echo "访问地址: http://localhost:8080"
    echo "API测试: curl \"http://localhost:8080/api/v1/hotel/suggest?q=东京\""
    echo "====================================="
    
    java -cp ".:hs-dao/target/classes:hs-core/target/classes:$(mvn dependency:build-classpath -q -Dmdep.outputFile=/dev/stdout)" SimpleJavaServerWithExcel
else
    echo "编译失败！"
    exit 1
fi 