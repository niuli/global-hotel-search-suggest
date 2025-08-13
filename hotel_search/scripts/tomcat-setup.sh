#!/bin/bash

# Tomcat部署脚本
# 适用于阿里云ECS部署

TOMCAT_VERSION="9.0.83"
TOMCAT_DIR="/opt/tomcat"
APP_NAME="hotel-search"
JAR_FILE="hotel-search-deploy-1.0.0.jar"

echo "=== Tomcat部署脚本 ==="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用root用户运行此脚本"
    exit 1
fi

# 安装Java
echo "安装Java 17..."
if command -v yum &> /dev/null; then
    # CentOS/RHEL
    yum update -y
    yum install -y java-17-openjdk java-17-openjdk-devel
elif command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    apt-get update
    apt-get install -y openjdk-17-jdk
else
    echo "不支持的包管理器"
    exit 1
fi

# 设置JAVA_HOME
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
echo "JAVA_HOME: $JAVA_HOME"

# 下载并安装Tomcat
echo "下载Tomcat $TOMCAT_VERSION..."
cd /tmp
wget "https://archive.apache.org/dist/tomcat/tomcat-9/v$TOMCAT_VERSION/bin/apache-tomcat-$TOMCAT_VERSION.tar.gz"
tar -xzf "apache-tomcat-$TOMCAT_VERSION.tar.gz"
mv "apache-tomcat-$TOMCAT_VERSION" "$TOMCAT_DIR"

# 创建应用目录
mkdir -p "$TOMCAT_DIR/webapps/$APP_NAME"
mkdir -p "$TOMCAT_DIR/webapps/$APP_NAME/WEB-INF/lib"

# 复制JAR文件
if [ -f "$JAR_FILE" ]; then
    cp "$JAR_FILE" "$TOMCAT_DIR/webapps/$APP_NAME/WEB-INF/lib/"
    echo "JAR文件已复制到Tomcat"
else
    echo "警告: 未找到JAR文件 $JAR_FILE"
fi

# 创建web.xml
cat > "$TOMCAT_DIR/webapps/$APP_NAME/WEB-INF/web.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee
         http://xmlns.jcp.org/xml/ns/javaee/web-app_3_1.xsd"
         version="3.1">
    
    <display-name>Hotel Search Service</display-name>
    <description>Hotel search system with suggest and search functionality</description>
    
    <!-- 欢迎页面 -->
    <welcome-file-list>
        <welcome-file>index.html</welcome-file>
    </welcome-file-list>
    
    <!-- 错误页面 -->
    <error-page>
        <error-code>404</error-code>
        <location>/error/404.html</location>
    </error-page>
    
    <error-page>
        <error-code>500</error-code>
        <location>/error/500.html</location>
    </error-page>
</web-app>
EOF

# 创建欢迎页面
cat > "$TOMCAT_DIR/webapps/$APP_NAME/index.html" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>酒店搜索服务</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .api { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .method { color: #007cba; font-weight: bold; }
        .url { color: #333; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏨 酒店搜索服务</h1>
        <p>欢迎使用酒店搜索API服务！</p>
        
        <h2>API接口</h2>
        
        <div class="api">
            <div class="method">GET</div>
            <div class="url">/api/v1/hotel/suggest?q={查询词}&count={数量}</div>
            <p>酒店建议接口</p>
        </div>
        
        <div class="api">
            <div class="method">GET</div>
            <div class="url">/api/v1/hotel/search?q={查询词}&page={页码}&pageSize={每页大小}</div>
            <p>酒店搜索接口</p>
        </div>
        
        <div class="api">
            <div class="method">GET</div>
            <div class="url">/api/v1/hotel/stats</div>
            <p>服务统计接口</p>
        </div>
        
        <div class="api">
            <div class="method">GET</div>
            <div class="url">/health</div>
            <p>健康检查接口</p>
        </div>
        
        <h2>测试链接</h2>
        <ul>
            <li><a href="/api/v1/hotel/stats">服务统计</a></li>
            <li><a href="/health">健康检查</a></li>
            <li><a href="/api/v1/hotel/suggest?q=Tokyo">搜索Tokyo</a></li>
        </ul>
        
        <p><small>版本: 1.0.0 | 部署环境: 阿里云</small></p>
    </div>
</body>
</html>
EOF

# 设置权限
chown -R tomcat:tomcat "$TOMCAT_DIR" 2>/dev/null || chmod -R 755 "$TOMCAT_DIR"

# 创建systemd服务
cat > /etc/systemd/system/tomcat.service << EOF
[Unit]
Description=Apache Tomcat Web Application Container
After=network.target

[Service]
Type=forking
Environment=JAVA_HOME=$JAVA_HOME
Environment=CATALINA_PID=$TOMCAT_DIR/temp/tomcat.pid
Environment=CATALINA_HOME=$TOMCAT_DIR
Environment=CATALINA_BASE=$TOMCAT_DIR
ExecStart=$TOMCAT_DIR/bin/startup.sh
ExecStop=$TOMCAT_DIR/bin/shutdown.sh
User=tomcat
Group=tomcat
UMask=0007
RestartSec=10
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 创建tomcat用户
useradd -r -s /bin/false tomcat 2>/dev/null || echo "tomcat用户已存在"

# 重新加载systemd
systemctl daemon-reload

echo "=== Tomcat部署完成 ==="
echo "Tomcat目录: $TOMCAT_DIR"
echo "应用目录: $TOMCAT_DIR/webapps/$APP_NAME"
echo ""
echo "启动Tomcat: systemctl start tomcat"
echo "停止Tomcat: systemctl stop tomcat"
echo "查看状态: systemctl status tomcat"
echo "设置开机启动: systemctl enable tomcat" 