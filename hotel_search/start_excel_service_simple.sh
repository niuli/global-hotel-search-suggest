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
javac -cp "hs-dao/target/classes:hs-core/target/classes:$(mvn dependency:build-classpath -q -Dmdep.outputFile=/dev/stdout):/Users/liniu/.m2/repository/org/apache/poi/poi/5.2.3/poi-5.2.3.jar:/Users/liniu/.m2/repository/org/apache/poi/poi-ooxml/5.2.3/poi-ooxml-5.2.3.jar:/Users/liniu/.m2/repository/org/apache/poi/poi-ooxml-lite/5.2.3/poi-ooxml-lite-5.2.3.jar:/Users/liniu/.m2/repository/org/apache/xmlbeans/xmlbeans/5.1.1/xmlbeans-5.1.1.jar:/Users/liniu/.m2/repository/org/apache/commons/commons-collections4/4.4/commons-collections4-4.4.jar:/Users/liniu/.m2/repository/commons-io/commons-io/2.11.0/commons-io-2.11.0.jar" SimpleJavaServerWithExcel.java

if [ $? -eq 0 ]; then
    echo "编译成功！"
    
    # 启动服务
    echo "启动服务..."
    echo "端口: 8080"
    echo "数据源: $EXCEL_FILE"
    echo "访问地址: http://localhost:8080"
    echo "API测试: curl \"http://localhost:8080/api/v1/hotel/suggest?q=东京\""
    echo "====================================="
    
    java -cp ".:hs-dao/target/classes:hs-core/target/classes:$(mvn dependency:build-classpath -q -Dmdep.outputFile=/dev/stdout):/Users/liniu/.m2/repository/org/apache/poi/poi/5.2.3/poi-5.2.3.jar:/Users/liniu/.m2/repository/org/apache/poi/poi-ooxml/5.2.3/poi-ooxml-5.2.3.jar:/Users/liniu/.m2/repository/org/apache/poi/poi-ooxml-lite/5.2.3/poi-ooxml-lite-5.2.3.jar:/Users/liniu/.m2/repository/org/apache/xmlbeans/xmlbeans/5.1.1/xmlbeans-5.1.1.jar:/Users/liniu/.m2/repository/org/apache/commons/commons-collections4/4.4/commons-collections4-4.4.jar:/Users/liniu/.m2/repository/commons-io/commons-io/2.11.0/commons-io-2.11.0.jar" SimpleJavaServerWithExcel
else
    echo "编译失败！"
    exit 1
fi 