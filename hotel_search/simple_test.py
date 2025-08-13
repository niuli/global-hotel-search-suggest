#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的日本酒店测试代码
使用数据加载器模块，专注于测试逻辑
"""

import time
from typing import List, Dict, Set
from dataclasses import dataclass
from collections import defaultdict

# 导入数据加载器
from data_loader import DataLoader, HotelData

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
        "新宿": "xs", "秋叶原": "qyy", "浅草": "qc", "上野": "sy", "银座": "yz"
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

class HotelSearchSystem:
    """酒店搜索系统"""
    
    def __init__(self):
        # 使用数据加载器
        self.data_loader = DataLoader()
        self.hotels = self.data_loader.load_japan_hotels()
        self.normalizer = QueryNormalizer()
        self.suggest_index = self._build_suggest_index()
    
    def _build_suggest_index(self) -> Dict[str, List[HotelData]]:
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
    
    def _compute_suggest_score(self, hotel: HotelData, query: str) -> float:
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

def run_basic_tests():
    """运行基础测试"""
    print("🗾 日本酒店搜索系统 - 简化测试")
    print("=" * 60)
    
    # 初始化搜索系统
    system = HotelSearchSystem()
    
    if not system.hotels:
        print("❌ 无法加载酒店数据，测试终止")
        return
    
    # 测试主要城市
    print("\n🏙️ 主要城市搜索测试:")
    cities = ["东京", "大阪", "京都", "横滨", "名古屋"]
    
    for city in cities:
        print(f"\n📍 搜索: '{city}'")
        suggestions = system.suggest(city, 3)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.display_name}")
            print(f"     区域: {suggestion.region_name} | 价格: {suggestion.price_range} | 星级: {suggestion.star_rating}星")
    
    # 测试英文搜索
    print("\n🌏 英文搜索测试:")
    english_queries = ["Tokyo", "Osaka", "Kyoto"]
    
    for query in english_queries:
        print(f"\n🔍 搜索: '{query}'")
        suggestions = system.suggest(query, 2)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.display_name}")
    
    # 测试酒店品牌
    print("\n🏨 品牌搜索测试:")
    brands = ["威斯汀", "三井花园", "MYSTAYS"]
    
    for brand in brands:
        print(f"\n🏢 搜索: '{brand}'")
        suggestions = system.suggest(brand, 2)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.display_name}")
            print(f"     价格: {suggestion.price_range} | 星级: {suggestion.star_rating}星")

def run_performance_test():
    """运行性能测试"""
    print("\n\n⚡ 性能测试:")
    print("=" * 60)
    
    system = HotelSearchSystem()
    
    if not system.hotels:
        print("❌ 无法加载酒店数据，性能测试终止")
        return
    
    # 测试查询
    test_queries = ["东京", "大阪", "京都", "新宿", "秋叶原", "tokyo", "osaka", "kyoto"] * 10
    
    start_time = time.time()
    success_count = 0
    
    for query in test_queries:
        try:
            suggestions = system.suggest(query, 5)
            if suggestions:
                success_count += 1
        except Exception as e:
            print(f"查询 '{query}' 时发生错误: {e}")
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / len(test_queries) * 1000  # 转换为毫秒
    
    print(f"总查询数: {len(test_queries)}")
    print(f"成功查询数: {success_count}")
    print(f"成功率: {success_count/len(test_queries)*100:.2f}%")
    print(f"总耗时: {total_time:.3f}秒")
    print(f"平均耗时: {avg_time:.2f}毫秒")
    print(f"QPS: {len(test_queries)/total_time:.2f}")

def run_data_analysis():
    """运行数据分析"""
    print("\n\n📊 数据分析:")
    print("=" * 60)
    
    # 使用数据加载器获取统计信息
    loader = DataLoader()
    hotels = loader.load_japan_hotels()
    
    if not hotels:
        print("❌ 无法加载酒店数据")
        return
    
    stats = loader.get_data_statistics(hotels)
    
    print(f"📈 基础统计:")
    print(f"  总酒店数: {stats['total_hotels']}")
    print(f"  总城市数: {stats['total_cities']}")
    print(f"  涉及国家: {', '.join(stats['countries'])}")
    
    print(f"\n🏙️ 城市分布 (前5名):")
    sorted_cities = sorted(stats['cities'].items(), key=lambda x: x[1]['count'], reverse=True)
    for i, (city, info) in enumerate(sorted_cities[:5], 1):
        print(f"  {i}. {city}: {info['count']}家酒店")
    
    print(f"\n⭐ 星级分布:")
    for stars, count in sorted(stats['star_ratings'].items()):
        print(f"  {stars}星: {count}家酒店")
    
    # 测试筛选功能
    print(f"\n🔍 筛选功能测试:")
    tokyo_hotels = loader.filter_hotels_by_city(hotels, "东京")
    high_star_hotels = loader.filter_hotels_by_star_rating(hotels, 4)
    westin_hotels = loader.search_hotels_by_name(hotels, "威斯汀")
    
    print(f"  东京酒店: {len(tokyo_hotels)}家")
    print(f"  4星以上酒店: {len(high_star_hotels)}家")
    print(f"  威斯汀酒店: {len(westin_hotels)}家")

if __name__ == "__main__":
    # 运行基础测试
    run_basic_tests()
    
    # 运行性能测试
    run_performance_test()
    
    # 运行数据分析
    run_data_analysis() 