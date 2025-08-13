# 酒店搜索服务部署包

## 文件说明
- `hotel-search-deploy-1.0.0.jar`: 主程序JAR包
- `start.sh`: 启动脚本
- `stop.sh`: 停止脚本
- `status.sh`: 状态检查脚本
- `tomcat-setup.sh`: Tomcat部署脚本
- `data/`: 数据文件目录

## 部署方式

### 方式1: 直接运行JAR包
```bash
# 启动服务
./start.sh

# 停止服务
./stop.sh

# 查看状态
./status.sh
```

### 方式2: Tomcat部署
```bash
# 以root用户运行
sudo ./tomcat-setup.sh

# 启动Tomcat
sudo systemctl start tomcat

# 查看状态
sudo systemctl status tomcat
```

## API接口
- 建议接口: `GET /api/v1/hotel/suggest?q={查询词}&count={数量}`
- 搜索接口: `GET /api/v1/hotel/search?q={查询词}&page={页码}&pageSize={每页大小}`
- 统计接口: `GET /api/v1/hotel/stats`
- 健康检查: `GET /health`

## 系统要求
- Java 17或更高版本
- 内存: 至少1GB
- 磁盘: 至少100MB可用空间

## 端口配置
默认端口: 8080
可通过环境变量PORT修改: `export PORT=9090`

版本: 1.0.0
部署环境: 阿里云
