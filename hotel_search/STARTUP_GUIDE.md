# 🚀 酒店搜索系统启动指南

## 📋 快速开始

### 1. 环境检查
确保您的系统已安装：
- Java 17+ (`java -version`)
- Maven 3.6+ (`mvn -version`)

### 2. 一键启动（推荐）
```bash
cd hotel_search
./quick-start.sh
```

### 3. 验证服务
```bash
# 测试API
./test-api.sh

# 或手动测试
curl http://localhost:8080/api/health
```

## 🔧 详细使用

### 脚本说明

| 脚本 | 功能 | 适用场景 |
|------|------|----------|
| `quick-start.sh` | 一键编译启动 | 快速开发测试 |
| `build-and-run.sh` | 完整生命周期管理 | 生产环境部署 |
| `test-api.sh` | API功能测试 | 验证服务功能 |

### 完整脚本命令

```bash
# 查看帮助
./build-and-run.sh help

# 完整构建启动
./build-and-run.sh full

# 分步操作
./build-and-run.sh build    # 仅构建
./build-and-run.sh start    # 仅启动
./build-and-run.sh stop     # 停止服务
./build-and-run.sh restart  # 重启服务
./build-and-run.sh status   # 查看状态
./build-and-run.sh logs     # 查看日志
```

## 🌐 API接口

### 基础信息
- **服务地址**: http://localhost:8080
- **API前缀**: /api

### 可用接口

| 接口 | 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|------|
| 健康检查 | GET | `/api/health` | 无 | 服务状态检查 |
| 酒店搜索 | GET | `/api/hotel/search` | `query` | 搜索酒店 |
| 搜索建议 | GET | `/api/hotel/suggest` | `query` | 获取搜索建议 |

### 使用示例

```bash
# 健康检查
curl http://localhost:8080/api/health

# 酒店搜索
curl "http://localhost:8080/api/hotel/search?query=东京酒店"

# 搜索建议
curl "http://localhost:8080/api/hotel/suggest?query=东京"
```

## 📊 监控和日志

### 日志文件
- **应用日志**: `hotel-search.log`
- **PID文件**: `hotel-search.pid`

### 监控命令
```bash
# 查看服务状态
./build-and-run.sh status

# 实时查看日志
./build-and-run.sh logs

# 或直接查看
tail -f hotel-search.log
```

## 🛠️ 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :8080

# 释放端口
kill -9 <PID>
```

#### 2. Java版本问题
```bash
# 检查Java版本
java -version

# 需要Java 17+
```

#### 3. Maven依赖问题
```bash
# 清理Maven缓存
mvn dependency:purge-local-repository

# 重新下载依赖
mvn clean compile
```

#### 4. 权限问题
```bash
# 添加执行权限
chmod +x *.sh
```

### 错误诊断

#### 服务启动失败
1. 检查日志文件: `cat hotel-search.log`
2. 确认端口未被占用: `lsof -i :8080`
3. 验证JAR文件存在: `ls -la target/*.jar`

#### API请求失败
1. 确认服务正在运行: `./build-and-run.sh status`
2. 测试健康检查: `curl http://localhost:8080/api/health`
3. 检查防火墙设置

## 🔄 开发模式

### 热重载开发
```bash
# 使用Spring Boot开发模式
mvn spring-boot:run

# 或使用devtools（如果配置了）
mvn spring-boot:run -Dspring-boot.run.profiles=dev
```

### 调试模式
```bash
# 启用调试
java -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005 -jar target/hotel-search-deploy-1.0.0.jar
```

## 🚀 生产部署

### 推荐配置
```bash
# 生产环境启动
java -Xms2g -Xmx4g -jar target/hotel-search-deploy-1.0.0.jar --spring.profiles.active=prod
```

### 系统服务配置
创建systemd服务文件 `/etc/systemd/system/hotel-search.service`:
```ini
[Unit]
Description=Hotel Search Service
After=network.target

[Service]
Type=simple
User=hotel-search
ExecStart=/usr/bin/java -jar /opt/hotel-search/hotel-search-deploy-1.0.0.jar
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 📈 性能优化

### JVM参数调优
```bash
# 生产环境推荐参数
java -Xms2g -Xmx4g \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -jar target/hotel-search-deploy-1.0.0.jar
```

### 监控指标
- 响应时间: 目标 < 100ms
- 内存使用: 监控堆内存使用率
- CPU使用: 监控CPU负载
- 并发连接: 监控活跃连接数

## 🔐 安全建议

### 生产环境安全
1. 使用HTTPS
2. 配置防火墙规则
3. 定期更新依赖
4. 启用访问日志
5. 配置适当的CORS策略

### 配置示例
```properties
# application-prod.properties
server.ssl.enabled=true
server.ssl.key-store=classpath:keystore.p12
server.ssl.key-store-password=your-password
logging.level.org.springframework.security=DEBUG
```

## 📞 支持

### 获取帮助
```bash
# 查看脚本帮助
./build-and-run.sh help

# 查看详细文档
cat README_SCRIPTS.md
```

### 日志分析
```bash
# 查看错误日志
grep ERROR hotel-search.log

# 查看性能日志
grep "response time" hotel-search.log
```

---

**注意**: 首次启动可能需要较长时间来下载Maven依赖，请耐心等待。 