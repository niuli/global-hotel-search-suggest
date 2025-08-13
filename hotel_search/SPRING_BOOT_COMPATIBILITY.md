# Spring Boot兼容性问题解决方案

## 🔧 问题描述

在启动Spring Boot应用时遇到以下兼容性问题：
1. Java版本不匹配（原配置使用Java 8，实际安装Java 17）
2. Spring Boot版本与Java版本不兼容
3. 依赖版本冲突

## ✅ 解决方案

### 1. 更新Java版本配置

**修改 `pom.xml` 中的Java版本：**
```xml
<properties>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <spring.version>5.3.31</spring.version>
    <spring-boot.version>2.7.18</spring-boot.version>
    <!-- 其他配置... -->
</properties>
```

### 2. 更新Maven编译器插件

**修改Maven编译器插件版本：**
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.11.0</version>
    <configuration>
        <source>17</source>
        <target>17</target>
        <encoding>UTF-8</encoding>
    </configuration>
</plugin>
```

### 3. 添加Spring Boot依赖管理

**在父pom.xml中添加Spring Boot依赖管理：**
```xml
<dependencyManagement>
    <dependencies>
        <!-- Spring Boot -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>${spring-boot.version}</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
            <version>${spring-boot.version}</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <version>${spring-boot.version}</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### 4. 简化hs-webapp模块依赖

**简化 `hs-webapp/pom.xml`：**
```xml
<dependencies>
    <!-- Service Module -->
    <dependency>
        <groupId>com.qunar.hotel</groupId>
        <artifactId>hs-service</artifactId>
        <version>1.0.0</version>
    </dependency>

    <!-- Spring Boot Starter Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- Lombok -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
    </dependency>
</dependencies>
```

## 🚀 启动命令

### 方法1: 使用Spring Boot启动脚本
```bash
cd hotel_search
./start_spring_boot.sh
```

### 方法2: 手动启动
```bash
cd hotel_search
source "$HOME/.sdkman/bin/sdkman-init.sh"

# 清理并编译
mvn clean compile

# 安装到本地仓库
mvn clean install -DskipTests

# 启动Spring Boot应用
mvn spring-boot:run -pl hs-webapp
```

### 方法3: 使用简单Java服务器（备选方案）
```bash
cd hotel_search
./start_server.sh
```

## 🌐 API接口

### Spring Boot API接口
- **建议接口**: `GET http://localhost:8080/api/v1/hotel/suggest?q={查询词}&count={数量}`
- **搜索接口**: `GET http://localhost:8080/api/v1/hotel/search?q={查询词}&page={页码}&pageSize={每页大小}`
- **统计接口**: `GET http://localhost:8080/api/v1/hotel/stats`

### 测试命令
```bash
# 测试建议接口
curl "http://localhost:8080/api/v1/hotel/suggest?q=东京"

# 测试搜索接口
curl "http://localhost:8080/api/v1/hotel/search?q=东京&page=1&pageSize=5"

# 测试统计接口
curl "http://localhost:8080/api/v1/hotel/stats"
```

## 📊 版本兼容性矩阵

| 组件 | 版本 | 兼容性 |
|------|------|--------|
| Java | 17 | ✅ 支持 |
| Maven | 3.9.10 | ✅ 支持 |
| Spring Boot | 2.7.18 | ✅ 支持 |
| Spring Framework | 5.3.31 | ✅ 支持 |
| Lucene | 8.11.2 | ✅ 支持 |

## 🔍 故障排除

### 常见问题
1. **编译错误**: 确保Java版本为17
2. **依赖冲突**: 运行 `mvn dependency:tree` 检查依赖
3. **端口占用**: 修改 `application.properties` 中的端口
4. **启动失败**: 检查日志输出，确保所有依赖正确加载

### 日志查看
- Spring Boot启动日志会显示在控制台
- 可以通过 `application.properties` 配置日志级别
- 使用 `--debug` 参数启动以获取详细日志

## ✅ 验证步骤

1. **编译验证**
   ```bash
   mvn clean compile
   ```

2. **安装验证**
   ```bash
   mvn clean install -DskipTests
   ```

3. **启动验证**
   ```bash
   mvn spring-boot:run -pl hs-webapp
   ```

4. **API验证**
   ```bash
   curl "http://localhost:8080/api/v1/hotel/suggest?q=东京"
   ```

## 📝 总结

通过以上配置更新，Spring Boot兼容性问题已解决：
- ✅ Java 17支持
- ✅ Spring Boot 2.7.18支持
- ✅ 所有依赖版本兼容
- ✅ 编译和启动正常
- ✅ API接口可用 