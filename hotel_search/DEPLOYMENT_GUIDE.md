# 酒店搜索服务阿里云部署指南

## 📦 部署包信息

- **JAR文件**: `hotel-search-deploy-1.0.0.jar` (21MB)
- **部署包**: `hotel-search-deploy-1.0.0.tar.gz` (19MB)
- **版本**: 1.0.0
- **Java要求**: Java 17或更高版本
- **内存要求**: 至少1GB
- **磁盘要求**: 至少100MB可用空间

## 🚀 部署方式

### 方式1: 直接运行JAR包（推荐）

#### 1. 上传部署包到阿里云ECS
```bash
# 使用scp上传
scp -i your-key.pem hotel-search-deploy-1.0.0.tar.gz root@your-ecs-ip:/opt/

# 或使用阿里云控制台上传
```

#### 2. 解压部署包
```bash
cd /opt
tar -xzf hotel-search-deploy-1.0.0.tar.gz
cd hotel-search
```

#### 3. 安装Java环境
```bash
# CentOS/RHEL
yum update -y
yum install -y java-17-openjdk java-17-openjdk-devel

# Ubuntu/Debian
apt-get update
apt-get install -y openjdk-17-jdk

# 验证Java安装
java -version
```

#### 4. 启动服务
```bash
# 设置执行权限
chmod +x *.sh

# 启动服务
./start.sh

# 查看状态
./status.sh

# 停止服务
./stop.sh
```

#### 5. 配置防火墙
```bash
# 开放8080端口
firewall-cmd --permanent --add-port=8080/tcp
firewall-cmd --reload

# 或使用iptables
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
service iptables save
```

### 方式2: Tomcat部署

#### 1. 运行Tomcat部署脚本
```bash
# 以root用户运行
sudo ./tomcat-setup.sh
```

#### 2. 启动Tomcat服务
```bash
# 启动Tomcat
sudo systemctl start tomcat

# 设置开机启动
sudo systemctl enable tomcat

# 查看状态
sudo systemctl status tomcat
```

#### 3. 访问应用
- **直接访问**: http://your-ecs-ip:8080
- **Tomcat访问**: http://your-ecs-ip:8080/hotel-search

## 🔧 配置说明

### 环境变量
```bash
# 设置端口（可选，默认8080）
export PORT=9090

# 设置Java内存（可选）
export JAVA_OPTS="-Xms512m -Xmx2g"
```

### 数据文件
- **Excel文件**: `日本东京酒店v2.xlsx` (278KB, 2377个酒店)
- **JSON文件**: `excel_hotels.json`, `japan_hotels.json` (备用数据)

## 🌐 API接口

### 1. 健康检查
```bash
curl http://your-ecs-ip:8080/health
```
**响应**:
```json
{
  "status": "UP",
  "timestamp": 1691923456789,
  "service": "hotel-search",
  "version": "1.0.0"
}
```

### 2. 服务统计
```bash
curl http://your-ecs-ip:8080/api/v1/hotel/stats
```
**响应**:
```json
{
  "success": true,
  "totalHotels": 2377,
  "serverStatus": "running",
  "port": 8080,
  "host": "0.0.0.0",
  "version": "1.0.0",
  "deployment": "aliyun"
}
```

### 3. 酒店建议
```bash
curl "http://your-ecs-ip:8080/api/v1/hotel/suggest?q=Tokyo&count=5"
```
**响应**:
```json
{
  "success": true,
  "query": "Tokyo",
  "count": 5,
  "results": [
    {
      "id": "994916",
      "nameCn": "东京希尔顿酒店",
      "nameEn": "Hilton Tokyo",
      "cityCn": "东京",
      "cityEn": "Tokyo",
      "region": "新宿地区",
      "searchCount": 1200,
      "score": 1.62
    }
  ]
}
```

### 4. 酒店搜索
```bash
curl "http://your-ecs-ip:8080/api/v1/hotel/search?q=Tokyo&page=1&pageSize=10"
```
**响应**:
```json
{
  "success": true,
  "query": "Tokyo",
  "page": 1,
  "pageSize": 10,
  "total": 150,
  "count": 10,
  "results": [...]
}
```

## 📊 监控和维护

### 服务状态检查
```bash
# 查看服务状态
./status.sh

# 查看进程
ps aux | grep hotel-search

# 查看日志
tail -f hotel-search.log

# 查看端口
netstat -tlnp | grep 8080
```

### 性能监控
```bash
# 查看内存使用
free -h

# 查看磁盘使用
df -h

# 查看CPU使用
top

# 查看网络连接
netstat -an | grep 8080
```

## 🔒 安全配置

### 1. 防火墙配置
```bash
# 只允许特定IP访问
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="your-ip" port port="8080" protocol="tcp" accept'

# 或使用安全组（推荐）
# 在阿里云控制台配置安全组规则
```

### 2. SSL配置（可选）
```bash
# 使用Nginx反向代理配置SSL
# 或使用阿里云SLB配置HTTPS
```

## 🚨 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :8080

# 杀死占用进程
kill -9 <PID>

# 或修改端口
export PORT=9090
./start.sh
```

#### 2. 内存不足
```bash
# 增加Java内存
export JAVA_OPTS="-Xms1g -Xmx4g"
./start.sh
```

#### 3. 数据文件读取失败
```bash
# 检查文件权限
ls -la *.xlsx

# 重新复制数据文件
cp 日本东京酒店v2.xlsx /opt/hotel-search/
```

#### 4. 服务无法启动
```bash
# 查看详细日志
java -jar hotel-search-deploy-1.0.0.jar 8080

# 检查Java版本
java -version
```

## 📞 技术支持

- **服务版本**: 1.0.0
- **部署环境**: 阿里云ECS
- **支持语言**: 中文、英文
- **数据源**: Excel文件 (日本东京酒店v2.xlsx)

## ✅ 部署检查清单

- [ ] 上传部署包到ECS
- [ ] 解压部署包
- [ ] 安装Java 17
- [ ] 设置脚本权限
- [ ] 启动服务
- [ ] 配置防火墙
- [ ] 测试API接口
- [ ] 配置监控
- [ ] 设置开机启动（可选）

---

**部署完成后，服务将在 http://your-ecs-ip:8080 上运行** 