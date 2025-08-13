#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
酒店搜索系统演示脚本
测试核心搜索逻辑和API接口
"""

import json
import re
from typing import List, Dict, Set
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class HotelInfo:
    """酒店信息"""
    hotel_id: str
    hotel_name_cn: str
    hotel_name_en: str
    city_name_cn: str
    city_name_en: str
    region_name: str
    address: str
    country: str
    search_count: int
    latitude: float = None
    longitude: float = None

@dataclass
class HotelSuggestElem:
    """酒店建议元素"""
    display_name: str
    hotel_name: str
    city_name: str
    region_name: str
    country: str
    hotel_id: str

@dataclass
class HotelSearchResult:
    """酒店搜索结果"""
    hotels: List[HotelInfo]
    total_count: int
    page: int
    page_size: int
    total_pages: int

class HotelQueryNormalizer:
    """酒店查询归一化器"""
    
    STOP_WORDS = {
        "酒店", "hotel", "旅馆", "inn", "宾馆", "guesthouse", "度假村", "resort",
        "饭店", "restaurant", "住宿", "accommodation", "公寓", "apartment",
        "民宿", "hostel", "青年旅社", "youth hostel", "商务酒店", "business hotel"
    }
    
    # 常见城市拼音映射
    PINYIN_MAP = {
        "北京": "bj", "上海": "sh", "广州": "gz", "深圳": "sz", "杭州": "hz",
        "南京": "nj", "成都": "cd", "武汉": "wh", "西安": "xa", "重庆": "cq",
        "天津": "tj", "苏州": "sz", "厦门": "xm", "长沙": "cs", "青岛": "qd",
        "大连": "dl", "宁波": "nb", "无锡": "wx", "佛山": "fs", "东莞": "dg",
        "郑州": "zz", "济南": "jn", "福州": "fz", "合肥": "hf", "昆明": "km",
        "哈尔滨": "heb", "沈阳": "sy", "长春": "cc", "石家庄": "sjz", "太原": "ty",
        "南昌": "nc", "南宁": "nn", "贵阳": "gy", "兰州": "lz", "银川": "yc",
        "西宁": "xn", "乌鲁木齐": "wlmq", "拉萨": "ls", "海口": "hk", "三亚": "sy",
        "台北": "tb", "香港": "hk", "澳门": "am", "东京": "dj", "大阪": "os",
        "京都": "jd", "横滨": "hb", "名古屋": "mgy", "神户": "sb", "福冈": "fk",
        "札幌": "zl", "仙台": "xt", "广岛": "hd", "新宿": "xs", "涩谷": "sg",
        "池袋": "cd", "秋叶原": "qyy", "浅草": "qc", "上野": "sy", "银座": "yz",
        "筑地": "zd", "品川": "pc", "日本桥": "rbq", "日暮里": "rml"
    }
    
    def normalize(self, input_text: str, remove_stop_words: bool = True) -> Set[str]:
        """归一化查询词"""
        if not input_text:
            return set()
        
        # 基本清理
        cleaned = self._clean_input(input_text)
        
        # 移除停用词
        if remove_stop_words:
            cleaned = self._remove_stop_words(cleaned)
        
        result = {cleaned} if cleaned else set()
        
        # 添加拼音变体
        result.update(self._generate_pinyin_variants(cleaned))
        
        # 添加英文变体
        result.update(self._generate_english_variants(cleaned))
        
        return result
    
    def _clean_input(self, input_text: str) -> str:
        """清理输入"""
        return re.sub(r'[^\w\u4e00-\u9fa5]', '', input_text.lower().strip())
    
    def _remove_stop_words(self, input_text: str) -> str:
        """移除停用词"""
        result = input_text
        for stop_word in self.STOP_WORDS:
            result = result.replace(stop_word, '')
        return result.strip()
    
    def _generate_pinyin_variants(self, input_text: str) -> Set[str]:
        """生成拼音变体"""
        variants = set()
        if self._contains_chinese(input_text):
            pinyin = self.PINYIN_MAP.get(input_text, '')
            if pinyin:
                variants.add(pinyin)
        return variants
    
    def _generate_english_variants(self, input_text: str) -> Set[str]:
        """生成英文变体"""
        variants = set()
        if self._contains_english(input_text):
            variants.add(input_text.lower())
            if input_text:
                variants.add(input_text[0].upper() + input_text[1:].lower())
        return variants
    
    def _contains_chinese(self, text: str) -> bool:
        """检查是否包含中文字符"""
        return bool(re.search(r'[\u4e00-\u9fa5]', text))
    
    def _contains_english(self, text: str) -> bool:
        """检查是否包含英文字符"""
        return bool(re.search(r'[a-zA-Z]', text))

class StringComputeUtils:
    """字符串计算工具类"""
    
    @staticmethod
    def compute_distance_score(str1: str, str2: str, normalize: bool = True) -> float:
        """计算编辑距离分数"""
        if not str1 or not str2:
            return 0.0
        
        distance = StringComputeUtils._compute_levenshtein_distance(str1, str2)
        max_length = max(len(str1), len(str2))
        
        if max_length == 0:
            return 1.0
        
        similarity = 1.0 - (distance / max_length)
        
        if normalize:
            similarity = similarity ** 0.5
        
        return similarity
    
    @staticmethod
    def _compute_levenshtein_distance(str1: str, str2: str) -> int:
        """计算Levenshtein编辑距离"""
        len1, len2 = len(str1), len(str2)
        
        # 创建矩阵
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        # 初始化第一行和第一列
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        # 填充矩阵
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if str1[i-1] == str2[j-1] else 1
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,
                    matrix[i][j-1] + 1,
                    matrix[i-1][j-1] + cost
                )
        
        return matrix[len1][len2]

class HotelSearchSystem:
    """酒店搜索系统"""
    
    def __init__(self):
        self.normalizer = HotelQueryNormalizer()
        self.hotels = self._load_sample_data()
        self.suggest_index = self._build_suggest_index()
    
    def _load_sample_data(self) -> List[HotelInfo]:
        """加载示例数据"""
        return [
            HotelInfo("994914", "新宿华盛顿酒店", "Shinjuku Washington Hotel", 
                     "东京", "Tokyo", "新宿地区", "东京都新宿区歌舞伎町1-30-1", "Japan", 1000, 35.6938, 139.7034),
            HotelInfo("25457196", "利夫马克斯酒店-东京大冢站前店", "HOTEL LiVEMAX Tokyo Otsuka-Ekimae", 
                     "东京", "Tokyo", "池袋地区", "东京都丰岛区大冢1-1-1", "Japan", 800, 35.7314, 139.7289),
            HotelInfo("104430812", "东京秋叶原N+酒店", "N+HOTEL Akihabara", 
                     "东京", "Tokyo", "秋叶原地区", "东京都千代田区外神田1-1-1", "Japan", 1200, 35.7023, 139.7745),
            HotelInfo("45586346", "浅草吉居酒店·琢居", "Asakusa YOSHII Hotel", 
                     "东京", "Tokyo", "上野/浅草地区", "东京都台东区浅草1-1-1", "Japan", 900, 35.7148, 139.7967),
            HotelInfo("688061", "MYSTAYS 上野入谷口酒店", "HOTEL MYSTAYS Ueno Iriyaguchi", 
                     "东京", "Tokyo", "上野/浅草地区", "东京都台东区上野1-1-1", "Japan", 1100, 35.7138, 139.7770),
            HotelInfo("品川王子大酒店东塔", "Shinagawa Prince Hotel East Tower", 
                     "东京", "Tokyo", "品川地区", "东京都港区高轮4-10-30", "Japan", 1500, 35.6286, 139.7389),
            HotelInfo("东京日本桥N+酒店", "Nplus Hotel Tokyo Nihonbashi", 
                     "东京", "Tokyo", "东京站/日本桥地区", "东京都中央区日本桥1-1-1", "Japan", 1300, 35.6812, 139.7671),
            HotelInfo("日暮里 阿尔蒙特酒店", "Almont Hotel Nippori", 
                     "东京", "Tokyo", "上野/浅草地区", "东京都荒川区西日暮里1-1-1", "Japan", 700, 35.7278, 139.7668),
            HotelInfo("东京秋叶原N+酒店(2号店)", "N+HOTEL Akihabara No.2", 
                     "东京", "Tokyo", "东京站/日本桥地区", "东京都千代田区外神田2-2-2", "Japan", 1000, 35.7023, 139.7745),
            HotelInfo("三井花园酒店银座筑地", "Mitsui Garden Hotel Ginza Tsukiji", 
                     "东京", "Tokyo", "银座/筑地地区", "东京都中央区筑地1-1-1", "Japan", 1400, 35.6654, 139.7704),
        ]
    
    def _build_suggest_index(self) -> Dict[str, List[HotelInfo]]:
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
                    display_name=f"{hotel.hotel_name_cn} ({hotel.country})",
                    hotel_name=hotel.hotel_name_cn,
                    city_name=hotel.city_name_cn,
                    region_name=hotel.region_name,
                    country=hotel.country,
                    hotel_id=hotel.hotel_id
                ))
        
        return result
    
    def search(self, query: str, page: int = 1, page_size: int = 20) -> HotelSearchResult:
        """酒店全文搜索"""
        if not query:
            return HotelSearchResult([], 0, page, page_size, 0)
        
        query = query.strip()
        candidates = []
        
        # 搜索匹配的酒店
        for hotel in self.hotels:
            score = self._compute_search_score(hotel, query)
            if score > 0:
                candidates.append((hotel, score))
        
        # 排序
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        page_hotels = candidates[start:end]
        
        return HotelSearchResult(
            hotels=[hotel for hotel, score in page_hotels],
            total_count=len(candidates),
            page=page,
            page_size=page_size,
            total_pages=(len(candidates) + page_size - 1) // page_size
        )
    
    def _compute_suggest_score(self, hotel: HotelInfo, query: str) -> float:
        """计算建议评分"""
        search_count_score = (hotel.search_count + 1) ** 0.2
        
        # 计算编辑距离分数
        distance_scores = []
        for field in [hotel.hotel_name_cn, hotel.hotel_name_en, hotel.city_name_cn, hotel.city_name_en, hotel.region_name]:
            distance_scores.append(StringComputeUtils.compute_distance_score(field, query))
        
        distance_score = max(distance_scores) if distance_scores else 0
        
        # 长度因子
        length_factor = 2.0 / len(hotel.hotel_name_cn)
        
        # 包含因子
        contain_boost = 10.0 if query in hotel.hotel_name_cn or query in hotel.city_name_cn else 1.0
        
        return (search_count_score * 0.2 + distance_score * 0.6 + length_factor) * contain_boost
    
    def _compute_search_score(self, hotel: HotelInfo, query: str) -> float:
        """计算搜索评分"""
        score = 0
        
        # 检查各个字段的匹配
        fields = [
            hotel.hotel_name_cn, hotel.hotel_name_en,
            hotel.city_name_cn, hotel.city_name_en,
            hotel.region_name, hotel.address
        ]
        
        for field in fields:
            if query.lower() in field.lower():
                score += 1
            score += StringComputeUtils.compute_distance_score(field, query) * 0.5
        
        return score

def test_system():
    """测试系统功能"""
    print("🏨 酒店搜索系统测试")
    print("=" * 50)
    
    system = HotelSearchSystem()
    
    # 测试建议搜索
    print("\n📋 测试建议搜索:")
    test_queries = ["东京", "新宿", "秋叶原", "tokyo", "shinjuku", "akihabara"]
    
    for query in test_queries:
        print(f"\n查询: '{query}'")
        suggestions = system.suggest(query, 5)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.display_name} - {suggestion.city_name} {suggestion.region_name}")
    
    # 测试全文搜索
    print("\n\n🔍 测试全文搜索:")
    test_search_queries = ["新宿", "秋叶原", "上野", "银座"]
    
    for query in test_search_queries:
        print(f"\n搜索: '{query}'")
        result = system.search(query, 1, 5)
        print(f"找到 {result.total_count} 个结果:")
        for i, hotel in enumerate(result.hotels, 1):
            print(f"  {i}. {hotel.hotel_name_cn} ({hotel.hotel_name_en})")
            print(f"     城市: {hotel.city_name_cn} | 区域: {hotel.region_name} | 热度: {hotel.search_count}")
    
    # 测试归一化
    print("\n\n🔄 测试查询归一化:")
    test_normalize_queries = ["东京酒店", "Tokyo Hotel", "新宿地区", "秋叶原"]
    
    for query in test_normalize_queries:
        normalized = system.normalizer.normalize(query)
        print(f"'{query}' -> {normalized}")

if __name__ == "__main__":
    test_system() 