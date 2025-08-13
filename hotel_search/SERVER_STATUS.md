# Java服务状态报告

## 📋 配置信息

### 服务器配置
- **端口**: 8080
- **IP地址**: 0.0.0.0 (所有网络接口)
- **开发环境IP**: localhost
- **应用名称**: hotel-search

### 配置文件位置
- `hs-webapp/src/main/resources/application.properties` - 主配置文件
- `hs-webapp/src/main/resources/application-dev.properties` - 开发环境配置

## 🔧 当前状态

### 服务状态
- ❌ **服务未运行**
- ❌ **端口8080未被占用** (除了WeChat的连接)

## 🚀 手动启动命令

### 方法1: 使用启动脚本 (推荐)
```bash
cd hotel_search
./start_server.sh
```

### 方法2: 直接运行简单Java服务器
```bash
cd hotel_search
source "$HOME/.sdkman/bin/sdkman-init.sh"

# 编译
javac -cp "hs-dao/target/classes:hs-core/target/classes:$(mvn dependency:build-classpath -q -Dmdep.outputFile=/dev/stdout)" SimpleJavaServer.java

# 运行
java -cp ".:hs-dao/target/classes:hs-core/target/classes:$(mvn dependency:build-classpath -q -Dmdep.outputFile=/dev/stdout)" SimpleJavaServer
```

### 方法3: 使用Maven Spring Boot插件 (如果Spring Boot可用)
```bash
cd hotel_search
source "$HOME/.sdkman/bin/sdkman-init.sh"
mvn spring-boot:run -pl hs-webapp
```

## 🌐 API接口

### 建议接口 (Suggest API)
```
GET http://localhost:8080/api/v1/hotel/suggest?q={查询词}&count={数量}
```

**示例:**
```bash
curl "http://localhost:8080/api/v1/hotel/suggest?q=东京"
curl "http://localhost:8080/api/v1/hotel/suggest?q=华盛顿&count=5"
```

### 搜索接口 (Search API)
```
GET http://localhost:8080/api/v1/hotel/search?q={查询词}&page={页码}&pageSize={每页大小}
```

**示例:**
```bash
curl "http://localhost:8080/api/v1/hotel/search?q=东京&page=1&pageSize=10"
```

### 统计接口 (Stats API)
```
GET http://localhost:8080/api/v1/hotel/stats
```

**示例:**
```bash
curl "http://localhost:8080/api/v1/hotel/stats"
```

## 📝 测试命令

### 启动后验证
```bash
# 测试建议接口
curl "http://localhost:8080/api/v1/hotel/suggest?q=东京"

# 测试搜索接口
curl "http://localhost:8080/api/v1/hotel/search?q=东京&page=1&pageSize=5"

# 测试统计接口
curl "http://localhost:8080/api/v1/hotel/stats"
```

## 🔍 故障排除

### 常见问题
1. **端口被占用**: 修改 `SimpleJavaServer.java` 中的 `PORT` 常量
2. **依赖问题**: 运行 `mvn clean install`
3. **权限问题**: 确保有足够权限运行Java应用
4. **编译错误**: 检查Java版本和依赖

### 日志查看
- 应用启动日志会显示在控制台
- 每个API请求都会在控制台显示日志

## 📊 服务器功能

### 当前支持的API
- ✅ **建议查询** - 根据关键词返回酒店建议
- ✅ **搜索查询** - 根据关键词搜索酒店，支持分页
- ✅ **统计信息** - 返回服务器状态和酒店数量
- ✅ **跨域支持** - 支持前端跨域访问
- ✅ **JSON响应** - 所有接口返回标准JSON格式

### 数据源
- 当前使用内置的模拟酒店数据
- 包含3个东京酒店示例
- 支持中英文搜索 