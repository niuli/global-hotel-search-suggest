#!/bin/bash

# 酒店搜索服务部署打包脚本
# 生成适用于阿里云部署的JAR包和部署包

echo "=== 酒店搜索服务部署打包 ==="

# 设置Java环境
source "$HOME/.sdkman/bin/sdkman-init.sh" 2>/dev/null || echo "SDKMAN未安装，使用系统Java"

# 检查Java版本
echo "Java版本:"
java -version

# 检查Maven
if ! command -v mvn &> /dev/null; then
    echo "错误: 未找到Maven，请安装Maven"
    exit 1
fi

echo "Maven版本:"
mvn -version

# 清理之前的构建
echo "清理之前的构建..."
rm -rf target/
rm -f *.jar
rm -f *.tar.gz
rm -f *.zip

# 编译Java文件
echo "编译Java文件..."
javac -cp "$(mvn dependency:build-classpath -q -Dmdep.outputFile=/dev/stdout -f pom-deploy.xml):/Users/liniu/.m2/repository/org/apache/poi/poi/5.2.3/poi-5.2.3.jar:/Users/liniu/.m2/repository/org/apache/poi/poi-ooxml/5.2.3/poi-ooxml-5.2.3.jar:/Users/liniu/.m2/repository/org/apache/poi/poi-ooxml-lite/5.2.3/poi-ooxml-lite-5.2.3.jar:/Users/liniu/.m2/repository/org/apache/xmlbeans/xmlbeans/5.1.1/xmlbeans-5.1.1.jar:/Users/liniu/.m2/repository/org/apache/commons/commons-collections4/4.4/commons-collections4-4.4.jar:/Users/liniu/.m2/repository/commons-io/commons-io/2.11.0/commons-io-2.11.0.jar:/Users/liniu/.m2/repository/org/apache/commons/commons-compress/1.21/commons-compress-1.21.jar" HotelSearchServer.java

if [ $? -ne 0 ]; then
    echo "编译失败！"
    exit 1
fi

echo "编译成功！"

# 使用Maven打包
echo "使用Maven打包..."
mvn clean package -f pom-deploy.xml

if [ $? -ne 0 ]; then
    echo "Maven打包失败！"
    exit 1
fi

echo "Maven打包成功！"

# 检查生成的JAR文件
JAR_FILE="target/hotel-search-deploy-1.0.0.jar"
if [ ! -f "$JAR_FILE" ]; then
    echo "错误: 未找到生成的JAR文件: $JAR_FILE"
    exit 1
fi

echo "JAR文件大小: $(ls -lh $JAR_FILE | awk '{print $5}')"

# 复制Excel数据文件
echo "复制数据文件..."
cp ../日本东京酒店v2.xlsx data/ 2>/dev/null || echo "Excel文件不存在，跳过"

# 设置脚本权限
chmod +x scripts/*.sh

# 创建部署包
echo "创建部署包..."

# 创建目录结构
mkdir -p deploy/hotel-search
cp "$JAR_FILE" deploy/hotel-search/
cp scripts/*.sh deploy/hotel-search/
cp -r data/ deploy/hotel-search/ 2>/dev/null || echo "数据目录为空"

# 创建README
cat > deploy/hotel-search/README.md << EOF
# 酒店搜索服务部署包

## 文件说明
- \`hotel-search-deploy-1.0.0.jar\`: 主程序JAR包
- \`start.sh\`: 启动脚本
- \`stop.sh\`: 停止脚本
- \`status.sh\`: 状态检查脚本
- \`tomcat-setup.sh\`: Tomcat部署脚本
- \`data/\`: 数据文件目录

## 部署方式

### 方式1: 直接运行JAR包
\`\`\`bash
# 启动服务
./start.sh

# 停止服务
./stop.sh

# 查看状态
./status.sh
\`\`\`

### 方式2: Tomcat部署
\`\`\`bash
# 以root用户运行
sudo ./tomcat-setup.sh

# 启动Tomcat
sudo systemctl start tomcat

# 查看状态
sudo systemctl status tomcat
\`\`\`

## API接口
- 建议接口: \`GET /api/v1/hotel/suggest?q={查询词}&count={数量}\`
- 搜索接口: \`GET /api/v1/hotel/search?q={查询词}&page={页码}&pageSize={每页大小}\`
- 统计接口: \`GET /api/v1/hotel/stats\`
- 健康检查: \`GET /health\`

## 系统要求
- Java 17或更高版本
- 内存: 至少1GB
- 磁盘: 至少100MB可用空间

## 端口配置
默认端口: 8080
可通过环境变量PORT修改: \`export PORT=9090\`

版本: 1.0.0
部署环境: 阿里云
EOF

# 创建压缩包
cd deploy
tar -czf hotel-search-deploy-1.0.0.tar.gz hotel-search/
zip -r hotel-search-deploy-1.0.0.zip hotel-search/
cd ..

echo "=== 打包完成 ==="
echo "部署包位置:"
echo "  - deploy/hotel-search-deploy-1.0.0.tar.gz"
echo "  - deploy/hotel-search-deploy-1.0.0.zip"
echo ""
echo "部署包内容:"
ls -la deploy/hotel-search/
echo ""
echo "JAR文件大小: $(ls -lh $JAR_FILE | awk '{print $5}')"
echo "部署包大小: $(ls -lh deploy/hotel-search-deploy-1.0.0.tar.gz | awk '{print $5}')"
echo ""
echo "✅ 打包完成！可以上传到阿里云进行部署。" 