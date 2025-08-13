#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日本酒店搜索系统测试代码
从JSON文件加载测试数据，执行各种测试用例
"""

import json
import time
from typing import List, Dict, Set
from dataclasses import dataclass
from collections import defaultdict
import os

@dataclass
class JapanHotelInfo:
    """日本酒店信息"""
    hotel_id: str
    hotel_name_cn: str
    hotel_name_en: str
    hotel_name_jp: str
    city_name_cn: str
    city_name_en: str
    city_name_jp: str
    region_name: str
    address: str
    country: str
    search_count: int
    latitude: float = None
    longitude: float = None
    price_range: str = ""
    star_rating: int = 0

@dataclass
class JapanHotelSuggestElem:
    """日本酒店建议元素"""
    display_name: str
    hotel_name: str
    city_name: str
    region_name: str
    country: str
    hotel_id: str
    price_range: str = ""
    star_rating: int = 0

class JapanHotelQueryNormalizer:
    """日本酒店查询归一化器"""
    
    STOP_WORDS = {
        "酒店", "hotel", "旅馆", "inn", "宾馆", "guesthouse", "度假村", "resort",
        "饭店", "restaurant", "住宿", "accommodation", "公寓", "apartment",
        "民宿", "hostel", "青年旅社", "youth hostel", "商务酒店", "business hotel",
        "ホテル", "旅館", "宿", "民宿", "ビジネスホテル"
    }
    
    # 日本城市拼音映射
    JAPAN_PINYIN_MAP = {
        # 东京都
        "东京": "dj", "新宿": "xs", "涩谷": "sg", "池袋": "cd", "秋叶原": "qyy", 
        "浅草": "qc", "上野": "sy", "银座": "yz", "筑地": "zd", "品川": "pc", 
        "日本桥": "rbq", "日暮里": "rml", "六本木": "lbm", "原宿": "ys", "表参道": "bcd",
        "青山": "qs", "代官山": "dgs", "惠比寿": "hbs", "中目黑": "zmm", "目黑": "mm",
        "五反田": "wft", "大崎": "ds", "田町": "tm", "滨松町": "bsm", "东京站": "djz",
        "有乐町": "ylt", "新桥": "xq", "汐留": "xl", "台场": "tc", "丰洲": "fz",
        
        # 大阪府
        "大阪": "os", "梅田": "md", "难波": "nb", "心斋桥": "xzb", "道顿堀": "ddk",
        "天王寺": "twz", "新大阪": "xos", "淀屋桥": "dyq", "本町": "bm", "西梅田": "xmd",
        "东梅田": "dmd", "北新地": "bxd", "南森町": "nsm", "天满桥": "tmq", "京桥": "jq",
        "谷町": "gt", "森之宫": "szg", "玉造": "yz", "鹤桥": "hq", "今里": "jl",
        
        # 京都府
        "京都": "jd", "四条": "st", "三条": "st", "二条": "et", "乌丸": "wm",
        "河原町": "hym", "祗园": "zy", "清水寺": "qss", "金阁寺": "jgs", "银阁寺": "ygs",
        "岚山": "ls", "伏见": "fj", "稻荷": "dn", "东福寺": "dfs", "南禅寺": "nzs",
        "西阵": "xz", "上京": "sj", "中京": "zj", "下京": "xj", "左京": "zj",
        
        # 横滨市
        "横滨": "hb", "关内": "gn", "樱木町": "ymm", "石川町": "scm", "山手": "ss",
        "元町": "ym", "中华街": "zhj", "港未来": "gwl", "横滨站": "hbz", "新横滨": "xhb",
        "保土谷": "bty", "东神奈川": "dsnj", "横滨桥": "hbq", "平沼桥": "pnq", "西横滨": "xhb",
        
        # 名古屋市
        "名古屋": "mgy", "荣": "r", "大须": "ds", "名古屋站": "mgyz", "金山": "js",
        "东别院": "dby", "上前津": "sqt", "矢场町": "ycm", "久屋大通": "jydt", "伏见": "fj",
        "丸之内": "wzn", "锦": "j", "大津通": "dzt", "新荣": "xr", "今池": "jc",
        
        # 神户市
        "神户": "sb", "三宫": "sg", "元町": "ym", "神户站": "sbz", "新神户": "xsb",
        "六甲": "lj", "滩": "t", "东滩": "dt", "西宫": "xg", "芦屋": "ly",
        "明石": "ms", "姬路": "jl", "加古川": "jkg", "高砂": "ts", "西明石": "xms",
        
        # 福冈市
        "福冈": "fk", "博多": "bd", "天神": "ts", "中洲": "zz", "福冈站": "fkz",
        "博多站": "bdz", "西新": "xx", "大濠公园": "dhgy", "药院": "yy", "赤坂": "cs",
        "六本松": "lbs", "西公园": "xgy", "东公园": "dgy", "百道": "bd", "早良": "zl",
        
        # 札幌市
        "札幌": "zl", "大通": "dt", "薄野": "bn", "札幌站": "zlz", "新札幌": "xzl",
        "白石": "bs", "厚别": "hb", "清田": "qt", "丰平": "fp", "南区": "nq",
        "西区": "xq", "北区": "bq", "东区": "dq", "中央区": "zyq", "手稻": "sd",
        
        # 仙台市
        "仙台": "xt", "仙台站": "xtz", "青叶通": "qyt", "一番町": "yfm", "二番町": "efm",
        "三番町": "sfm", "四番町": "sfm", "五番町": "wfm", "六番町": "lfm", "七番町": "qfm",
        "八番町": "bfm", "九番町": "jfm", "十番町": "sfm", "定禅寺通": "dzst", "广濑通": "hst",
        
        # 广岛市
        "广岛": "hd", "广岛站": "hdz", "八丁堀": "bcdk", "本通": "bt", "纸屋町": "zym",
        "胡町": "hm", "幟町": "zm", "中町": "zm", "袋町": "dm", "小町": "xm",
        "基町": "jm", "江波": "jb", "舟入": "fr", "千田": "qd", "佐伯区": "zbq",
        
        # 其他主要城市
        "奈良": "nl", "奈良站": "nlz", "东大寺": "dds", "春日大社": "csds", "兴福寺": "xfs",
        "长野": "cn", "长野站": "cnz", "善光寺": "sgs", "松本": "sb", "松本站": "sbz",
        "金泽": "jz", "金泽站": "jzz", "兼六园": "jly", "东茶屋街": "dcjj", "西茶屋街": "xcjj",
        "冲绳": "cs", "那霸": "nb", "那霸站": "nbz", "国际通": "gjt", "首里": "sl",
        "函馆": "hg", "函馆站": "hgz", "五棱郭": "wlk", "元町": "ym", "汤之川": "yzk"
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
        
        # 添加日文变体
        result.update(self._generate_japanese_variants(cleaned))
        
        return result
    
    def _clean_input(self, input_text: str) -> str:
        """清理输入"""
        return input_text.lower().strip()
    
    def _remove_stop_words(self, input_text: str) -> str:
        """移除停用词"""
        result = input_text
        for stop_word in self.STOP_WORDS:
            result = result.replace(stop_word.lower(), '')
        return result.strip()
    
    def _generate_pinyin_variants(self, input_text: str) -> Set[str]:
        """生成拼音变体"""
        variants = set()
        if self._contains_chinese(input_text):
            pinyin = self.JAPAN_PINYIN_MAP.get(input_text, '')
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
    
    def _generate_japanese_variants(self, input_text: str) -> Set[str]:
        """生成日文变体"""
        variants = set()
        if self._contains_japanese(input_text):
            # 这里可以添加日文假名转换逻辑
            variants.add(input_text)
        return variants
    
    def _contains_chinese(self, text: str) -> bool:
        """检查是否包含中文字符"""
        return any('\u4e00' <= char <= '\u9fff' for char in text)
    
    def _contains_english(self, text: str) -> bool:
        """检查是否包含英文字符"""
        return any(char.isalpha() and ord(char) < 128 for char in text)
    
    def _contains_japanese(self, text: str) -> bool:
        """检查是否包含日文字符"""
        return any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text)

class JapanHotelSearchSystem:
    """日本酒店搜索系统"""
    
    def __init__(self, data_file: str = "data/japan_hotels.json"):
        self.normalizer = JapanHotelQueryNormalizer()
        self.hotels = self._load_hotel_data(data_file)
        self.suggest_index = self._build_suggest_index()
    
    def _load_hotel_data(self, data_file: str) -> List[JapanHotelInfo]:
        """从JSON文件加载酒店数据"""
        try:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(current_dir, data_file)
            
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            hotels = []
            for hotel_data in data['hotels']:
                hotel = JapanHotelInfo(
                    hotel_id=hotel_data['hotel_id'],
                    hotel_name_cn=hotel_data['hotel_name_cn'],
                    hotel_name_en=hotel_data['hotel_name_en'],
                    hotel_name_jp=hotel_data['hotel_name_jp'],
                    city_name_cn=hotel_data['city_name_cn'],
                    city_name_en=hotel_data['city_name_en'],
                    city_name_jp=hotel_data['city_name_jp'],
                    region_name=hotel_data['region_name'],
                    address=hotel_data['address'],
                    country=hotel_data['country'],
                    search_count=hotel_data['search_count'],
                    latitude=hotel_data.get('latitude'),
                    longitude=hotel_data.get('longitude'),
                    price_range=hotel_data.get('price_range', ''),
                    star_rating=hotel_data.get('star_rating', 0)
                )
                hotels.append(hotel)
            
            print(f"✅ 成功加载 {len(hotels)} 家酒店数据")
            return hotels
            
        except FileNotFoundError:
            print(f"❌ 数据文件未找到: {data_file}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ JSON文件解析错误: {e}")
            return []
        except Exception as e:
            print(f"❌ 加载数据时发生错误: {e}")
            return []
    
    def _build_suggest_index(self) -> Dict[str, List[JapanHotelInfo]]:
        """构建建议索引"""
        index = defaultdict(list)
        
        for hotel in self.hotels:
            # 添加酒店名称
            for normalized in self.normalizer.normalize(hotel.hotel_name_cn):
                index[normalized].append(hotel)
            for normalized in self.normalizer.normalize(hotel.hotel_name_en):
                index[normalized].append(hotel)
            for normalized in self.normalizer.normalize(hotel.hotel_name_jp):
                index[normalized].append(hotel)
            
            # 添加城市名称
            for normalized in self.normalizer.normalize(hotel.city_name_cn):
                index[normalized].append(hotel)
            for normalized in self.normalizer.normalize(hotel.city_name_en):
                index[normalized].append(hotel)
            for normalized in self.normalizer.normalize(hotel.city_name_jp):
                index[normalized].append(hotel)
            
            # 添加区域名称
            for normalized in self.normalizer.normalize(hotel.region_name):
                index[normalized].append(hotel)
        
        return dict(index)
    
    def suggest(self, query: str, count: int = 10) -> List[JapanHotelSuggestElem]:
        """日本酒店建议搜索"""
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
                result.append(JapanHotelSuggestElem(
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
    
    def _compute_suggest_score(self, hotel: JapanHotelInfo, query: str) -> float:
        """计算建议评分"""
        search_count_score = (hotel.search_count + 1) ** 0.2
        
        # 计算编辑距离分数
        distance_scores = []
        for field in [hotel.hotel_name_cn, hotel.hotel_name_en, hotel.hotel_name_jp, 
                     hotel.city_name_cn, hotel.city_name_en, hotel.city_name_jp, hotel.region_name]:
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

def test_japan_hotels():
    """测试日本酒店搜索功能"""
    print("🗾 日本酒店搜索系统测试")
    print("=" * 60)
    
    # 初始化搜索系统
    system = JapanHotelSearchSystem()
    
    if not system.hotels:
        print("❌ 无法加载酒店数据，测试终止")
        return
    
    # 测试日本主要城市
    print("\n🏙️ 测试日本主要城市搜索:")
    japan_cities = [
        "东京", "大阪", "京都", "横滨", "名古屋", "神户", "福冈", "札幌", "仙台", "广岛",
        "奈良", "长野", "金泽", "冲绳", "函馆"
    ]
    
    for city in japan_cities:
        print(f"\n📍 搜索城市: '{city}'")
        suggestions = system.suggest(city, 3)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.display_name}")
            print(f"     区域: {suggestion.region_name} | 价格: {suggestion.price_range} | 星级: {suggestion.star_rating}星")
    
    # 测试东京地区
    print("\n\n🏢 测试东京地区酒店:")
    tokyo_areas = ["新宿", "涩谷", "池袋", "秋叶原", "浅草", "上野", "银座", "筑地", "品川", "日本桥"]
    
    for area in tokyo_areas:
        print(f"\n🏨 搜索区域: '{area}'")
        suggestions = system.suggest(area, 2)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.display_name}")
            print(f"     价格: {suggestion.price_range} | 星级: {suggestion.star_rating}星")
    
    # 测试英文搜索
    print("\n\n🌏 测试英文搜索:")
    english_queries = ["Tokyo", "Osaka", "Kyoto", "Yokohama", "Nagoya", "Kobe", "Fukuoka", "Sapporo"]
    
    for query in english_queries:
        print(f"\n🔍 英文搜索: '{query}'")
        suggestions = system.suggest(query, 2)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.display_name}")
    
    # 测试酒店品牌
    print("\n\n🏨 测试酒店品牌搜索:")
    hotel_brands = ["威斯汀", "Westin", "王子", "Prince", "三井花园", "Mitsui Garden", "MYSTAYS"]
    
    for brand in hotel_brands:
        print(f"\n🏢 搜索品牌: '{brand}'")
        suggestions = system.suggest(brand, 3)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.display_name}")
            print(f"     价格: {suggestion.price_range} | 星级: {suggestion.star_rating}星")
    
    # 测试价格范围
    print("\n\n💰 测试价格范围搜索:")
    price_queries = ["便宜", "经济", "豪华", "高级", "商务"]
    
    for query in price_queries:
        print(f"\n💵 搜索价格: '{query}'")
        suggestions = system.suggest(query, 3)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.display_name}")
            print(f"     价格: {suggestion.price_range} | 星级: {suggestion.star_rating}星")
    
    # 测试归一化功能
    print("\n\n🔄 测试查询归一化:")
    normalize_tests = [
        "东京酒店", "Tokyo Hotel", "大阪ホテル", "京都旅馆", "横滨宾馆",
        "新宿地区", "梅田站前", "心斋桥附近", "祗园周边", "博多站"
    ]
    
    for query in normalize_tests:
        normalized = system.normalizer.normalize(query)
        print(f"'{query}' -> {normalized}")

def test_performance():
    """性能测试"""
    print("\n\n⚡ 性能测试:")
    print("=" * 60)
    
    system = JapanHotelSearchSystem()
    
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

if __name__ == "__main__":
    # 运行功能测试
    test_japan_hotels()
    
    # 运行性能测试
    test_performance() 