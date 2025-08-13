# 酒店搜索系统文件结构说明

## 📁 项目结构

```
hotel_search/
├── data/                          # 数据文件目录
│   ├── japan_hotels.json         # 日本酒店数据文件 (44家)
│   └── excel_hotels.json         # Excel酒店数据文件 (2377家)
├── excel_data_loader.py           # Excel数据读取器
├── test_excel_hotels.py          # Excel酒店数据测试脚本
├── excel_test_report.md          # Excel数据测试报告
├── data_loader.py                 # 数据加载器模块
├── simple_test.py                 # 简化测试代码
├── test_japan_hotels.py          # 完整测试代码
├── japan_hotel_test.py           # 原始测试代码（已重构）
├── test_demo.py                  # 基础演示代码
├── api_test.py                   # API测试代码
├── web_demo.html                 # Web演示页面
├── japan_web_demo.html           # 日本酒店Web演示页面
├── test_report.md                # 测试报告
├── japan_test_report.md          # 日本酒店测试报告
└── README_FILE_STRUCTURE.md      # 本文件
```

## 📊 数据文件

### `data/japan_hotels.json`
- **格式**: JSON
- **内容**: 44家日本酒店数据
- **字段**: 
  - `hotel_id`: 酒店ID
  - `hotel_name_cn/en/jp`: 中日英酒店名称
  - `city_name_cn/en/jp`: 中日英城市名称
  - `region_name`: 区域名称
  - `address`: 详细地址
  - `country`: 国家
  - `search_count`: 搜索热度
  - `latitude/longitude`: 经纬度
  - `price_range`: 价格范围
  - `star_rating`: 星级

### `data/excel_hotels.json`
- **格式**: JSON
- **内容**: 2377家日本酒店数据 (从Excel文件读取)
- **数据来源**: 日本东京酒店v2.xlsx
- **字段**: 与japan_hotels.json相同
- **特点**: 
  - 覆盖37个城市
  - 主要集中东京地区 (2176家)
  - 包含真实酒店数据
  - 支持大规模测试

## 🔧 核心模块

### `excel_data_loader.py` - Excel数据读取器
**功能**: 专门从Excel文件读取酒店数据

**主要类**:
- `ExcelHotelData`: Excel酒店数据结构
- `ExcelDataLoader`: Excel数据加载器类

**主要方法**:
- `load_excel_data()`: 从Excel文件加载数据
- `_parse_row_to_hotel()`: 解析Excel行数据
- `_extract_hotel_name_cn/en/jp()`: 提取酒店名称
- `_extract_city_name_cn/en/jp()`: 提取城市名称
- `_extract_coordinates()`: 提取经纬度
- `save_to_json()`: 保存为JSON格式
- `get_data_statistics()`: 获取数据统计

**使用示例**:
```python
from excel_data_loader import ExcelDataLoader

loader = ExcelDataLoader()
hotels = loader.load_excel_data()  # 读取2377家酒店
stats = loader.get_data_statistics(hotels)
```

### `data_loader.py` - 数据加载器
**功能**: 专门处理数据文件的加载和解析

**主要类**:
- `HotelData`: 酒店数据结构
- `DataLoader`: 数据加载器类

**主要方法**:
- `load_japan_hotels()`: 加载日本酒店数据
- `load_hotel_data()`: 加载通用酒店数据
- `save_hotel_data()`: 保存酒店数据
- `get_data_statistics()`: 获取数据统计信息
- `filter_hotels_by_city()`: 按城市筛选
- `filter_hotels_by_star_rating()`: 按星级筛选
- `search_hotels_by_name()`: 按名称搜索

**使用示例**:
```python
from data_loader import DataLoader

loader = DataLoader()
hotels = loader.load_japan_hotels()
stats = loader.get_data_statistics(hotels)
```

## 🧪 测试代码

### `test_excel_hotels.py` - Excel酒店数据测试脚本
**特点**: 
- 使用Excel数据读取器
- 测试2377家酒店数据
- 全面的功能测试

**主要功能**:
- 城市搜索测试 (37个城市)
- 东京地区搜索测试
- 英文搜索测试
- 酒店品牌搜索测试
- 性能测试 (120次查询)
- 详细数据分析

**测试结果**:
- 平均响应时间: 62.75毫秒
- QPS: 15.94
- 成功率: 83.33%

**使用示例**:
```bash
python3 test_excel_hotels.py
```

### `simple_test.py` - 简化测试代码
**特点**: 
- 使用数据加载器模块
- 专注于测试逻辑
- 代码结构清晰

**主要功能**:
- 基础搜索测试
- 性能测试
- 数据分析

**使用示例**:
```bash
python3 simple_test.py
```

### `test_japan_hotels.py` - 完整测试代码
**特点**:
- 从JSON文件加载数据
- 完整的测试用例
- 详细的测试报告

**主要功能**:
- 日本城市搜索测试
- 区域细分搜索测试
- 英文搜索测试
- 酒店品牌搜索测试
- 查询归一化测试

**使用示例**:
```bash
python3 test_japan_hotels.py
```

### `test_demo.py` - 基础演示代码
**特点**:
- 内置示例数据
- 快速演示功能
- 适合入门学习

### `api_test.py` - API测试代码
**特点**:
- 模拟API接口
- 完整的API测试
- 性能基准测试

## 🌐 Web演示

### `web_demo.html` - 通用Web演示
**功能**:
- 现代化UI设计
- 实时搜索建议
- 标签页切换
- 性能统计显示

### `japan_web_demo.html` - 日本酒店Web演示
**功能**:
- 日本风格设计
- 城市卡片展示
- 品牌搜索功能
- 价格范围筛选

## 📋 测试报告

### `excel_test_report.md` - Excel酒店数据测试报告
**内容**:
- 2377家酒店数据测试结果
- 37个城市覆盖测试
- 性能测试指标 (QPS: 15.94)
- 详细数据分析

### `test_report.md` - 通用测试报告
**内容**:
- 功能测试结果
- 性能测试指标
- 边界测试情况
- 系统架构验证

### `japan_test_report.md` - 日本酒店专项测试报告
**内容**:
- 日本城市覆盖测试
- 酒店品牌识别测试
- 多语言支持验证
- 地区细分测试

## 🔄 数据与代码分离的优势

### 1. **数据独立性**
- 数据文件可以独立更新
- 支持多种数据格式
- 便于数据版本管理

### 2. **代码复用性**
- 数据加载器可被多个测试使用
- 统一的错误处理机制
- 标准化的数据接口

### 3. **维护便利性**
- 数据变更不影响测试逻辑
- 测试代码专注于业务逻辑
- 模块化设计便于扩展

### 4. **测试灵活性**
- 可以轻松切换数据源
- 支持不同规模的数据测试
- 便于进行A/B测试

## 🚀 使用建议

### 开发阶段
1. 使用 `simple_test.py` 进行快速测试
2. 使用 `data_loader.py` 进行数据验证
3. 使用 `web_demo.html` 进行UI测试

### 测试阶段
1. 使用 `test_japan_hotels.py` 进行完整测试
2. 使用 `api_test.py` 进行API测试
3. 查看测试报告了解系统性能

### 生产阶段
1. 使用 `data_loader.py` 加载生产数据
2. 使用 `simple_test.py` 进行回归测试
3. 使用Web演示页面进行用户验收测试

## 📈 性能指标

### 当前系统性能 (Excel数据)
- **数据加载**: 2377家酒店，加载时间 < 2s
- **搜索响应**: 平均 62.75ms
- **QPS**: 15.94
- **成功率**: 83.33%

### 数据覆盖 (Excel数据)
- **城市数量**: 37个城市
- **主要城市**: 东京 (2176家)
- **酒店品牌**: 华盛顿、利夫马克斯、MYSTAYS、三井花园等
- **价格范围**: ¥8,000-15,000 (默认)
- **星级范围**: 3星 (默认)

### 小规模数据性能 (JSON数据)
- **数据加载**: 44家酒店，加载时间 < 100ms
- **搜索响应**: 平均 0.46ms
- **QPS**: 2181.51
- **成功率**: 87.50%

### 小规模数据覆盖 (JSON数据)
- **城市数量**: 15个主要日本城市
- **酒店品牌**: 8个主要品牌
- **价格范围**: ¥6,000-70,000
- **星级范围**: 3-5星

## 🔧 扩展建议

### 数据扩展
1. 添加更多日本城市
2. 增加酒店详细信息
3. 支持更多语言

### 功能扩展
1. 添加地理位置搜索
2. 实现价格筛选功能
3. 增加用户评价系统

### 性能优化
1. 实现数据缓存机制
2. 优化搜索算法
3. 添加数据库支持

---

*最后更新: 2024年1月*
*文件结构版本: v1.0* 