# 酒店搜索系统启动脚本使用说明

## 概述

本项目提供了两个启动脚本来简化酒店搜索系统的编译、打包和启动过程：

1. **`build-and-run.sh`** - 功能完整的构建启动脚本
2. **`quick-start.sh`** - 快速启动脚本

## 环境要求

- Java 17 或更高版本
- Maven 3.6 或更高版本
- macOS/Linux 系统

## 脚本使用

### 1. 功能完整脚本 (build-and-run.sh)

这个脚本提供了完整的项目生命周期管理功能：

```bash
# 进入项目目录
cd hotel_search

# 查看帮助信息
./build-and-run.sh help

# 完整构建和启动（推荐）
./build-and-run.sh full

# 仅编译和打包
./build-and-run.sh build

# 仅启动服务
./build-and-run.sh start

# 停止服务
./build-and-run.sh stop

# 重启服务
./build-and-run.sh restart

# 查看服务状态
./build-and-run.sh status

# 查看服务日志
./build-and-run.sh logs

# 清理项目
./build-and-run.sh clean

# 运行测试
./build-and-run.sh test
```

### 2. 快速启动脚本 (quick-start.sh)

这个脚本提供了一键快速启动功能：

```bash
# 进入项目目录
cd hotel_search

# 快速启动（编译+启动）
./quick-start.sh
```

## 服务信息

启动成功后，服务将在以下地址提供API：

- **服务地址**: http://localhost:8080
- **健康检查**: http://localhost:8080/api/health
- **酒店搜索**: http://localhost:8080/api/hotel/search?query=酒店名
- **搜索建议**: http://localhost:8080/api/hotel/suggest?query=关键词

## 日志文件

- **完整脚本日志**: `hotel-search.log`
- **PID文件**: `hotel-search.pid`

## 故障排除

### 1. 端口被占用

如果8080端口被占用，脚本会自动尝试释放端口。如果失败，可以手动停止占用进程：

```bash
# 查看占用端口的进程
lsof -i :8080

# 停止占用进程
kill -9 <PID>
```

### 2. Java版本问题

确保安装了Java 17或更高版本：

```bash
java -version
```

### 3. Maven问题

确保Maven正确安装：

```bash
mvn -version
```

### 4. 权限问题

如果脚本无法执行，请添加执行权限：

```bash
chmod +x build-and-run.sh
chmod +x quick-start.sh
```

## 开发模式

在开发过程中，可以使用以下命令：

```bash
# 仅编译（不打包）
./build-and-run.sh clean
mvn compile

# 运行测试
./build-and-run.sh test

# 热重载开发（如果配置了spring-boot-devtools）
mvn spring-boot:run
```

## 生产部署

对于生产环境，建议：

1. 使用 `./build-and-run.sh build` 构建项目
2. 将生成的JAR文件部署到服务器
3. 使用系统服务（systemd）管理进程
4. 配置适当的日志轮转

## API测试

服务启动后，可以使用以下命令测试API：

```bash
# 健康检查
curl http://localhost:8080/api/health

# 酒店搜索
curl "http://localhost:8080/api/hotel/search?query=东京酒店"

# 搜索建议
curl "http://localhost:8080/api/hotel/suggest?query=东京"
```

## 注意事项

1. 首次启动可能需要较长时间来下载依赖
2. 确保有足够的磁盘空间用于Maven缓存
3. 在生产环境中，建议配置适当的内存参数
4. 定期清理Maven缓存：`mvn dependency:purge-local-repository` 