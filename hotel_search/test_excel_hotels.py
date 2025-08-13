#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel酒店数据测试脚本
使用从Excel文件读取的2377家酒店数据进行测试
"""

import time
from typing import List, Dict, Set
from dataclasses import dataclass
from collections import defaultdict

# 导入Excel数据加载器
from excel_data_loader import ExcelDataLoader, ExcelHotelData

@dataclass
class HotelSuggestElem:
    """酒店建议元素"""
    display_name: str
    hotel_name: str
    city_name: str
    region_name: str
    country: str
    hotel_id: str
    price_range: str = ""
    star_rating: int = 0

class QueryNormalizer:
    """查询归一化器"""
    
    STOP_WORDS = {
        "酒店", "hotel", "旅馆", "inn", "宾馆", "guesthouse", "度假村", "resort",
        "饭店", "restaurant", "住宿", "accommodation", "公寓", "apartment",
        "民宿", "hostel", "青年旅社", "youth hostel", "商务酒店", "business hotel",
        "ホテル", "旅館", "宿", "民宿", "ビジネスホテル"
    }
    
    # 日本城市拼音映射
    JAPAN_PINYIN_MAP = {
        "东京": "dj", "大阪": "os", "京都": "jd", "横滨": "hb", "名古屋": "mgy",
        "神户": "sb", "福冈": "fk", "札幌": "zl", "仙台": "xt", "广岛": "hd",
        "奈良": "nl", "长野": "cn", "金泽": "jz", "冲绳": "cs", "函馆": "hg",
        "新宿": "xs", "秋叶原": "qyy", "浅草": "qc", "上野": "sy", "银座": "yz",
        "浦安": "pa", "成田": "ct", "町田": "md", "川崎": "cs", "八王子": "bwz"
    }
    
    def normalize(self, input_text: str, remove_stop_words: bool = True) -> Set[str]:
        """归一化查询词"""
        if not input_text:
            return set()
        
        # 基本清理
        cleaned = input_text.lower().strip()
        
        # 移除停用词
        if remove_stop_words:
            for stop_word in self.STOP_WORDS:
                cleaned = cleaned.replace(stop_word.lower(), '')
            cleaned = cleaned.strip()
        
        result = {cleaned} if cleaned else set()
        
        # 添加拼音变体
        if self._contains_chinese(cleaned):
            pinyin = self.JAPAN_PINYIN_MAP.get(cleaned, '')
            if pinyin:
                result.add(pinyin)
        
        # 添加英文变体
        if self._contains_english(cleaned):
            result.add(cleaned.lower())
            if cleaned:
                result.add(cleaned[0].upper() + cleaned[1:].lower())
        
        return result
    
    def _contains_chinese(self, text: str) -> bool:
        """检查是否包含中文字符"""
        return any('\u4e00' <= char <= '\u9fff' for char in text)
    
    def _contains_english(self, text: str) -> bool:
        """检查是否包含英文字符"""
        return any(char.isalpha() and ord(char) < 128 for char in text)

class ExcelHotelSearchSystem:
    """Excel酒店搜索系统"""
    
    def __init__(self):
        # 使用Excel数据加载器
        self.excel_loader = ExcelDataLoader()
        self.hotels = self.excel_loader.load_excel_data()
        self.normalizer = QueryNormalizer()
        self.suggest_index = self._build_suggest_index()
    
    def _build_suggest_index(self) -> Dict[str, List[ExcelHotelData]]:
        """构建建议索引"""
        index = defaultdict(list)
        
        for hotel in self.hotels:
            # 添加酒店名称
            for normalized in self.normalizer.normalize(hotel.hotel_name_cn):
                index[normalized].append(hotel)
            for normalized in self.normalizer.normalize(hotel.hotel_name_en):
                index[normalized].append(hotel)
            
            # 添加城市名称
            for normalized in self.normalizer.normalize(hotel.city_name_cn):
                index[normalized].append(hotel)
            for normalized in self.normalizer.normalize(hotel.city_name_en):
                index[normalized].append(hotel)
            
            # 添加区域名称
            for normalized in self.normalizer.normalize(hotel.region_name):
                index[normalized].append(hotel)
        
        return dict(index)
    
    def suggest(self, query: str, count: int = 10) -> List[HotelSuggestElem]:
        """酒店建议搜索"""
        if not query or len(query.strip()) <= 1:
            return []
        
        query = query.strip()
        candidates = []
        
        # 查找匹配的酒店
        for normalized_query in self.normalizer.normalize(query, False):
            for prefix in self.suggest_index.keys():
                if prefix.startswith(normalized_query) or normalized_query.startswith(prefix):
                    candidates.extend(self.suggest_index[prefix])
        
        # 去重和评分
        hotel_scores = defaultdict(float)
        for hotel in candidates:
            score = self._compute_suggest_score(hotel, query)
            hotel_scores[hotel.hotel_id] = max(hotel_scores[hotel.hotel_id], score)
        
        # 排序和返回
        sorted_hotels = sorted(hotel_scores.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        seen_hotels = set()
        
        for hotel_id, score in sorted_hotels:
            if len(result) >= count:
                break
            
            hotel = next(h for h in self.hotels if h.hotel_id == hotel_id)
            if hotel.hotel_id not in seen_hotels:
                seen_hotels.add(hotel.hotel_id)
                result.append(HotelSuggestElem(
                    display_name=f"{hotel.hotel_name_cn} ({hotel.city_name_cn})",
                    hotel_name=hotel.hotel_name_cn,
                    city_name=hotel.city_name_cn,
                    region_name=hotel.region_name,
                    country=hotel.country,
                    hotel_id=hotel.hotel_id,
                    price_range=hotel.price_range,
                    star_rating=hotel.star_rating
                ))
        
        return result
    
    def _compute_suggest_score(self, hotel: ExcelHotelData, query: str) -> float:
        """计算建议评分"""
        search_count_score = (hotel.search_count + 1) ** 0.2
        
        # 计算编辑距离分数
        distance_scores = []
        for field in [hotel.hotel_name_cn, hotel.hotel_name_en, 
                     hotel.city_name_cn, hotel.city_name_en, hotel.region_name]:
            distance_scores.append(self._edit_distance(field, query))
        
        distance_score = max(distance_scores) if distance_scores else 0
        
        # 长度因子
        length_factor = 2.0 / len(hotel.hotel_name_cn)
        
        # 包含因子
        contain_boost = 10.0 if query in hotel.hotel_name_cn or query in hotel.city_name_cn else 1.0
        
        return (search_count_score * 0.2 + distance_score * 0.6 + length_factor) * contain_boost
    
    def _edit_distance(self, str1: str, str2: str) -> float:
        """计算编辑距离相似度"""
        len1, len2 = len(str1), len(str2)
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if str1[i-1] == str2[j-1] else 1
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,
                    matrix[i][j-1] + 1,
                    matrix[i-1][j-1] + cost
                )
        
        distance = matrix[len1][len2]
        max_len = max(len1, len2)
        return 1.0 - (distance / max_len) if max_len > 0 else 1.0

def run_excel_data_tests():
    """运行Excel数据测试"""
    print("🗾 Excel酒店数据测试 - 2377家酒店")
    print("=" * 70)
    
    # 初始化搜索系统
    system = ExcelHotelSearchSystem()
    
    if not system.hotels:
        print("❌ 无法加载Excel酒店数据，测试终止")
        return
    
    # 获取数据统计
    stats = system.excel_loader.get_data_statistics(system.hotels)
    
    print(f"📊 数据概览:")
    print(f"  总酒店数: {stats['total_hotels']}")
    print(f"  总城市数: {stats['total_cities']}")
    print(f"  涉及国家: {', '.join(stats['countries'])}")
    
    # 显示主要城市分布
    print(f"\n🏙️ 主要城市分布 (前10名):")
    sorted_cities = sorted(stats['cities'].items(), key=lambda x: x[1]['count'], reverse=True)
    for i, (city, info) in enumerate(sorted_cities[:10], 1):
        print(f"  {i}. {city}: {info['count']}家酒店")
    
    # 测试主要城市搜索
    print(f"\n🔍 主要城市搜索测试:")
    major_cities = ["东京", "浦安", "成田", "町田", "川崎", "八王子"]
    
    for city in major_cities:
        print(f"\n📍 搜索城市: '{city}'")
        suggestions = system.suggest(city, 3)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.display_name}")
            print(f"     区域: {suggestion.region_name} | 价格: {suggestion.price_range} | 星级: {suggestion.star_rating}星")
    
    # 测试东京地区搜索
    print(f"\n🏢 东京地区搜索测试:")
    tokyo_areas = ["新宿", "涩谷", "池袋", "秋叶原", "浅草", "上野", "银座", "品川"]
    
    for area in tokyo_areas:
        print(f"\n🏨 搜索区域: '{area}'")
        suggestions = system.suggest(area, 2)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.display_name}")
            print(f"     价格: {suggestion.price_range} | 星级: {suggestion.star_rating}星")
    
    # 测试英文搜索
    print(f"\n🌏 英文搜索测试:")
    english_queries = ["Tokyo", "Shinjuku", "Akihabara", "Asakusa", "Ginza"]
    
    for query in english_queries:
        print(f"\n🔍 英文搜索: '{query}'")
        suggestions = system.suggest(query, 2)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.display_name}")
    
    # 测试酒店品牌搜索
    print(f"\n🏨 酒店品牌搜索测试:")
    hotel_brands = ["华盛顿", "Washington", "利夫马克斯", "LiVEMAX", "MYSTAYS", "三井花园"]
    
    for brand in hotel_brands:
        print(f"\n🏢 搜索品牌: '{brand}'")
        suggestions = system.suggest(brand, 3)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.display_name}")
            print(f"     价格: {suggestion.price_range} | 星级: {suggestion.star_rating}星")

def run_performance_test():
    """运行性能测试"""
    print(f"\n\n⚡ 性能测试:")
    print("=" * 70)
    
    system = ExcelHotelSearchSystem()
    
    if not system.hotels:
        print("❌ 无法加载Excel酒店数据，性能测试终止")
        return
    
    # 测试查询
    test_queries = ["东京", "新宿", "秋叶原", "tokyo", "shinjuku", "akihabara"] * 20
    
    start_time = time.time()
    success_count = 0
    total_results = 0
    
    for query in test_queries:
        try:
            suggestions = system.suggest(query, 5)
            if suggestions:
                success_count += 1
                total_results += len(suggestions)
        except Exception as e:
            print(f"查询 '{query}' 时发生错误: {e}")
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / len(test_queries) * 1000  # 转换为毫秒
    
    print(f"总查询数: {len(test_queries)}")
    print(f"成功查询数: {success_count}")
    print(f"成功率: {success_count/len(test_queries)*100:.2f}%")
    print(f"总返回结果数: {total_results}")
    print(f"平均每查询结果数: {total_results/success_count:.1f}")
    print(f"总耗时: {total_time:.3f}秒")
    print(f"平均耗时: {avg_time:.2f}毫秒")
    print(f"QPS: {len(test_queries)/total_time:.2f}")

def run_data_analysis():
    """运行数据分析"""
    print(f"\n\n📊 详细数据分析:")
    print("=" * 70)
    
    # 使用Excel数据加载器获取统计信息
    loader = ExcelDataLoader()
    hotels = loader.load_excel_data()
    
    if not hotels:
        print("❌ 无法加载Excel酒店数据")
        return
    
    stats = loader.get_data_statistics(hotels)
    
    print(f"📈 基础统计:")
    print(f"  总酒店数: {stats['total_hotels']}")
    print(f"  总城市数: {stats['total_cities']}")
    print(f"  涉及国家: {', '.join(stats['countries'])}")
    
    print(f"\n🏙️ 城市分布 (前15名):")
    sorted_cities = sorted(stats['cities'].items(), key=lambda x: x[1]['count'], reverse=True)
    for i, (city, info) in enumerate(sorted_cities[:15], 1):
        print(f"  {i:2d}. {city}: {info['count']:4d}家酒店")
    
    print(f"\n⭐ 星级分布:")
    for stars, count in sorted(stats['star_ratings'].items()):
        print(f"  {stars}星: {count}家酒店")
    
    print(f"\n💰 价格范围分布 (前10个):")
    sorted_prices = sorted(stats['price_ranges'].items(), key=lambda x: x[1], reverse=True)
    for i, (price_range, count) in enumerate(sorted_prices[:10], 1):
        print(f"  {i:2d}. {price_range}: {count:4d}家酒店")
    
    # 分析区域分布
    print(f"\n🗺️ 区域分布分析:")
    region_stats = defaultdict(int)
    for hotel in hotels:
        region_stats[hotel.region_name] += 1
    
    sorted_regions = sorted(region_stats.items(), key=lambda x: x[1], reverse=True)
    for i, (region, count) in enumerate(sorted_regions[:15], 1):
        print(f"  {i:2d}. {region}: {count:4d}家酒店")

if __name__ == "__main__":
    # 运行Excel数据测试
    run_excel_data_tests()
    
    # 运行性能测试
    run_performance_test()
    
    # 运行数据分析
    run_data_analysis() 