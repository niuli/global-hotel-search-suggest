# 酒店搜索系统 (Hotel Search System)

基于 coach_global_search 架构设计的酒店搜索系统，支持酒店建议搜索和全文搜索功能。

## 系统架构

### 模块结构
```
hotel_search/
├── hs-core/          # 核心模块：索引、模型、工具类
├── hs-service/       # 服务层：业务逻辑
├── hs-webapp/        # Web层：API接口和前端页面
└── pom.xml          # 父级Maven配置
```

### 核心设计思想

#### 1. FST (Finite State Transducer) 前缀索引架构
- 使用 Apache Lucene 的 FST 数据结构构建高效的前缀索引
- 支持快速的前缀匹配和自动补全功能
- 内存加载，支持定时重载

#### 2. 多维度归一化处理
- **文本预处理**：去除停用词（酒店、hotel、旅馆、inn等）
- **多音字处理**：支持多音字的多种拼音变体
- **繁简转换**：自动处理繁体字和简体字
- **拼音转换**：支持连续拼音和拼音首字母匹配

#### 3. 智能评分算法
```
score = log(search_count+1) * 0.2 + edit_distance_score * 0.6 + length_factor + city_boost + region_boost
```

评分因素包括：
- **搜索热度权重** (20%)：基于历史搜索次数
- **编辑距离权重** (60%)：字符串相似度
- **长度因子**：短文本优先
- **城市权重**：城市类型结果权重翻倍
- **区域权重**：区域匹配权重提升

#### 4. 分层召回策略
- **精确匹配**：完全匹配的候选词
- **前缀匹配**：FST 前缀索引快速召回
- **模糊匹配**：基于编辑距离的相似度匹配

## API 接口

### 1. 酒店建议搜索 API

#### GET /api/v1/hotel/suggest
获取酒店建议列表

**参数：**
- `q` (必需): 查询词
- `count` (可选): 返回数量，默认10，最大50

**示例：**
```bash
GET /api/v1/hotel/suggest?q=东京&count=10
```

#### POST /api/v1/hotel/suggest
POST方式获取酒店建议

**请求体：**
```json
{
  "query": "东京",
  "count": 10
}
```

### 2. 酒店全文搜索 API

#### GET /api/v1/hotel/search
搜索酒店

**参数：**
- `q` (必需): 查询词
- `page` (可选): 页码，默认1
- `pageSize` (可选): 每页大小，默认20，最大100

**示例：**
```bash
GET /api/v1/hotel/search?q=新宿&page=1&pageSize=20
```

#### GET /api/v1/hotel/search/geo
带地理位置的酒店搜索

**参数：**
- `q` (必需): 查询词
- `lat` (必需): 纬度
- `lng` (必需): 经度
- `page` (可选): 页码，默认1
- `pageSize` (可选): 每页大小，默认20

**示例：**
```bash
GET /api/v1/hotel/search/geo?q=新宿&lat=35.6938&lng=139.7034&page=1&pageSize=20
```

#### POST /api/v1/hotel/search
POST方式搜索酒店

**请求体：**
```json
{
  "query": "新宿",
  "page": 1,
  "pageSize": 20,
  "latitude": 35.6938,
  "longitude": 139.7034
}
```

## 响应格式

所有API都返回统一的JSON格式：

```json
{
  "success": true,
  "message": "success",
  "data": [...],
  "timestamp": 1640995200000
}
```

### 建议搜索响应示例
```json
{
  "success": true,
  "message": "success",
  "data": [
    {
      "displayName": "新宿华盛顿酒店 (Japan)",
      "hotelName": "新宿华盛顿酒店",
      "cityName": "东京",
      "regionName": "新宿地区",
      "country": "Japan",
      "hotelId": "994914"
    }
  ],
  "timestamp": 1640995200000
}
```

### 搜索响应示例
```json
{
  "success": true,
  "message": "success",
  "data": {
    "hotels": [
      {
        "hotelId": "994914",
        "hotelNameCn": "新宿华盛顿酒店",
        "hotelNameEn": "Shinjuku Washington Hotel",
        "cityNameCn": "东京",
        "cityNameEn": "Tokyo",
        "regionName": "新宿地区",
        "address": "东京都新宿区歌舞伎町1-30-1",
        "country": "Japan",
        "searchCount": 1000,
        "latitude": 35.6938,
        "longitude": 139.7034,
        "score": 0.95
      }
    ],
    "totalCount": 1,
    "page": 1,
    "pageSize": 20,
    "totalPages": 1
  },
  "timestamp": 1640995200000
}
```

## 构建和运行

### 环境要求
- Java 8+
- Maven 3.6+
- Tomcat 8.5+ 或其他Servlet容器

### 构建步骤

1. **编译项目**
```bash
cd hotel_search
mvn clean compile
```

2. **打包项目**
```bash
mvn clean package
```

3. **部署到Tomcat**
```bash
# 将生成的 war 包部署到 Tomcat webapps 目录
cp hs-webapp/target/hs-webapp-1.0.0.war $TOMCAT_HOME/webapps/hotel-search.war
```

4. **启动应用**
```bash
# 启动 Tomcat
$TOMCAT_HOME/bin/startup.sh
```

5. **访问应用**
```
http://localhost:8080/hotel-search/
```

## 数据源

系统目前使用模拟数据，基于 `日本东京酒店v2.xlsx` 文件的结构。实际项目中可以：

1. 集成数据库连接
2. 实现Excel文件读取功能
3. 添加数据同步机制

## 扩展功能

### 1. 拼音支持
可以集成 pinyin4j 等拼音转换库，提供更准确的拼音匹配。

### 2. 地理位置搜索
可以集成 Elasticsearch 的地理位置搜索功能，支持距离排序和地理围栏。

### 3. 多语言支持
可以扩展支持更多语言，如日语、韩语等。

### 4. 缓存优化
可以集成 Redis 等缓存系统，提高查询性能。

## 技术栈

- **后端框架**: Spring MVC
- **索引引擎**: Apache Lucene
- **构建工具**: Maven
- **日志框架**: SLF4J + Logback
- **JSON处理**: Jackson
- **前端**: HTML5 + JavaScript

## 性能优化

1. **索引优化**: FST 前缀索引提供高效的前缀匹配
2. **内存加载**: 索引全量加载到内存，避免磁盘IO
3. **缓存机制**: 编辑距离计算缓存，避免重复计算
4. **分页查询**: 支持分页，避免大量数据传输

## 监控和日志

系统提供详细的日志记录，包括：
- 查询请求和响应日志
- 索引构建日志
- 错误和异常日志
- 性能监控日志

可以通过配置 logback.xml 来调整日志级别和输出格式。 