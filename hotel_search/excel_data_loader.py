#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel数据读取器
从日本东京酒店v2.xlsx文件读取酒店数据
"""

import pandas as pd
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
import re

@dataclass
class ExcelHotelData:
    """Excel酒店数据结构"""
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
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    price_range: str = ""
    star_rating: int = 0
    # Excel特有字段
    original_data: Dict = None

class ExcelDataLoader:
    """Excel数据加载器"""
    
    def __init__(self, excel_file: str = "../日本东京酒店v2.xlsx"):
        self.excel_file = excel_file
        self.data = None
    
    def load_excel_data(self) -> List[ExcelHotelData]:
        """从Excel文件加载酒店数据"""
        try:
            print(f"📖 正在读取Excel文件: {self.excel_file}")
            
            # 读取Excel文件
            df = pd.read_excel(self.excel_file, engine='openpyxl')
            
            print(f"✅ 成功读取Excel文件，共 {len(df)} 行数据")
            print(f"📊 列名: {list(df.columns)}")
            
            # 显示前几行数据
            print(f"\n📋 数据预览:")
            print(df.head())
            
            hotels = []
            
            for index, row in df.iterrows():
                try:
                    hotel = self._parse_row_to_hotel(row, index)
                    if hotel:
                        hotels.append(hotel)
                except Exception as e:
                    print(f"⚠️ 解析第 {index+1} 行数据时出错: {e}")
                    continue
            
            print(f"\n✅ 成功解析 {len(hotels)} 家酒店数据")
            return hotels
            
        except FileNotFoundError:
            print(f"❌ Excel文件未找到: {self.excel_file}")
            return []
        except Exception as e:
            print(f"❌ 读取Excel文件时发生错误: {e}")
            return []
    
    def _parse_row_to_hotel(self, row: pd.Series, index: int) -> Optional[ExcelHotelData]:
        """将Excel行数据解析为酒店对象"""
        try:
            # 获取原始数据字典
            original_data = row.to_dict()
            
            # 提取酒店ID
            hotel_id = self._extract_hotel_id(row, index)
            
            # 提取酒店名称
            hotel_name_cn = self._extract_hotel_name_cn(row)
            hotel_name_en = self._extract_hotel_name_en(row)
            hotel_name_jp = self._extract_hotel_name_jp(row)
            
            # 提取城市信息
            city_name_cn = self._extract_city_name_cn(row)
            city_name_en = self._extract_city_name_en(row)
            city_name_jp = self._extract_city_name_jp(row)
            
            # 提取区域信息
            region_name = self._extract_region_name(row)
            
            # 提取地址
            address = self._extract_address(row)
            
            # 提取价格信息
            price_range = self._extract_price_range(row)
            
            # 提取星级信息
            star_rating = self._extract_star_rating(row)
            
            # 提取搜索热度（模拟）
            search_count = self._generate_search_count(star_rating, price_range)
            
            # 提取经纬度
            latitude, longitude = self._extract_coordinates(row, city_name_cn, region_name)
            
            hotel = ExcelHotelData(
                hotel_id=hotel_id,
                hotel_name_cn=hotel_name_cn,
                hotel_name_en=hotel_name_en,
                hotel_name_jp=hotel_name_jp,
                city_name_cn=city_name_cn,
                city_name_en=city_name_en,
                city_name_jp=city_name_jp,
                region_name=region_name,
                address=address,
                country="Japan",
                search_count=search_count,
                latitude=latitude,
                longitude=longitude,
                price_range=price_range,
                star_rating=star_rating,
                original_data=original_data
            )
            
            return hotel
            
        except Exception as e:
            print(f"⚠️ 解析第 {index+1} 行时出错: {e}")
            return None
    
    def _extract_hotel_id(self, row: pd.Series, index: int) -> str:
        """提取酒店ID"""
        # 尝试从不同列名中提取ID
        id_columns = ['ID', 'id', 'hotel_id', 'Hotel ID', '酒店ID', '编号']
        for col in id_columns:
            if col in row and pd.notna(row[col]):
                return str(row[col])
        
        # 如果没有找到ID，使用行号
        return f"excel_{index+1:06d}"
    
    def _extract_hotel_name_cn(self, row: pd.Series) -> str:
        """提取中文酒店名称"""
        name_columns = ['酒店名称(中)', '酒店名称', 'Hotel Name CN', '中文名称', '名称', 'name_cn']
        for col in name_columns:
            if col in row and pd.notna(row[col]):
                name = str(row[col]).strip()
                # 处理包含英文名称的情况，提取中文部分
                if '(' in name and ')' in name:
                    # 提取括号前的中文部分
                    chinese_part = name.split('(')[0].strip()
                    if chinese_part:
                        return chinese_part
                return name
        return "未知酒店"
    
    def _extract_hotel_name_en(self, row: pd.Series) -> str:
        """提取英文酒店名称"""
        name_columns = ['酒店名称(英)', 'Hotel Name EN', '英文名称', 'English Name', 'name_en']
        for col in name_columns:
            if col in row and pd.notna(row[col]):
                return str(row[col]).strip()
        
        # 从中文名称中提取英文部分
        cn_name_col = '酒店名称(中)'
        if cn_name_col in row and pd.notna(row[cn_name_col]):
            name = str(row[cn_name_col]).strip()
            if '(' in name and ')' in name:
                # 提取括号内的英文部分
                english_part = name.split('(')[1].split(')')[0].strip()
                if english_part:
                    return english_part
        
        # 如果没有英文名称，尝试翻译中文名称
        cn_name = self._extract_hotel_name_cn(row)
        if cn_name != "未知酒店":
            return self._translate_to_english(cn_name)
        return "Unknown Hotel"
    
    def _extract_hotel_name_jp(self, row: pd.Series) -> str:
        """提取日文酒店名称"""
        name_columns = ['Hotel Name JP', '日文名称', 'Japanese Name', 'name_jp']
        for col in name_columns:
            if col in row and pd.notna(row[col]):
                return str(row[col]).strip()
        
        # 如果没有日文名称，使用中文名称
        cn_name = self._extract_hotel_name_cn(row)
        if cn_name != "未知酒店":
            return cn_name + "ホテル"
        return "不明ホテル"
    
    def _extract_city_name_cn(self, row: pd.Series) -> str:
        """提取中文城市名称"""
        city_columns = ['城市名称(中)', '城市', 'City CN', '中文城市', 'city_cn']
        for col in city_columns:
            if col in row and pd.notna(row[col]):
                return str(row[col]).strip()
        
        # 从地址中提取城市信息
        address = self._extract_address(row)
        return self._extract_city_from_address(address)
    
    def _extract_city_name_en(self, row: pd.Series) -> str:
        """提取英文城市名称"""
        city_columns = ['城市名称(英)', 'City EN', '英文城市', 'English City', 'city_en']
        for col in city_columns:
            if col in row and pd.notna(row[col]):
                return str(row[col]).strip()
        
        # 翻译中文城市名
        cn_city = self._extract_city_name_cn(row)
        return self._translate_city_to_english(cn_city)
    
    def _extract_city_name_jp(self, row: pd.Series) -> str:
        """提取日文城市名称"""
        city_columns = ['City JP', '日文城市', 'Japanese City', 'city_jp']
        for col in city_columns:
            if col in row and pd.notna(row[col]):
                return str(row[col]).strip()
        
        # 翻译中文城市名
        cn_city = self._extract_city_name_cn(row)
        return self._translate_city_to_japanese(cn_city)
    
    def _extract_region_name(self, row: pd.Series) -> str:
        """提取区域名称"""
        region_columns = ['所属区域', '区域', 'Region', '地区', 'area', 'district']
        for col in region_columns:
            if col in row and pd.notna(row[col]):
                region = str(row[col]).strip()
                if region and region != 'nan':
                    return region
        
        # 从地址中提取区域信息
        address = self._extract_address(row)
        return self._extract_region_from_address(address)
    
    def _extract_address(self, row: pd.Series) -> str:
        """提取地址"""
        address_columns = ['酒店详细地址', '地址描述', '地址', 'Address', '详细地址', 'location']
        for col in address_columns:
            if col in row and pd.notna(row[col]):
                address = str(row[col]).strip()
                if address and address != 'nan':
                    return address
        return "地址不详"
    
    def _extract_price_range(self, row: pd.Series) -> str:
        """提取价格范围"""
        price_columns = ['价格', 'Price', '价格范围', 'price_range', '费用']
        for col in price_columns:
            if col in row and pd.notna(row[col]):
                price = str(row[col]).strip()
                return self._format_price_range(price)
        
        # 根据星级生成模拟价格
        star_rating = self._extract_star_rating(row)
        return self._generate_price_by_stars(star_rating)
    
    def _extract_star_rating(self, row: pd.Series) -> int:
        """提取星级"""
        star_columns = ['星级', 'Star Rating', '星级评定', 'stars', '等级']
        for col in star_columns:
            if col in row and pd.notna(row[col]):
                try:
                    rating = str(row[col]).strip()
                    # 提取数字
                    numbers = re.findall(r'\d+', rating)
                    if numbers:
                        star = int(numbers[0])
                        return min(max(star, 1), 5)  # 限制在1-5星
                except:
                    pass
        
        # 默认3星
        return 3
    
    def _generate_search_count(self, star_rating: int, price_range: str) -> int:
        """根据星级和价格生成搜索热度"""
        base_count = 500
        
        # 星级影响
        star_multiplier = {1: 0.5, 2: 0.8, 3: 1.0, 4: 1.5, 5: 2.0}
        count = base_count * star_multiplier.get(star_rating, 1.0)
        
        # 价格影响（低价更受欢迎）
        if "¥5,000" in price_range or "¥6,000" in price_range:
            count *= 1.2
        elif "¥20,000" in price_range or "¥30,000" in price_range:
            count *= 0.8
        
        return int(count)
    
    def _extract_coordinates(self, row: pd.Series, city_name: str, region_name: str) -> tuple:
        """提取经纬度坐标"""
        # 尝试从Excel中提取经纬度
        lat_cols = ['纬度', 'latitude', 'lat']
        lng_cols = ['经度', 'longitude', 'lng']
        
        latitude = None
        longitude = None
        
        # 提取纬度
        for col in lat_cols:
            if col in row and pd.notna(row[col]):
                try:
                    latitude = float(row[col])
                    break
                except:
                    pass
        
        # 提取经度
        for col in lng_cols:
            if col in row and pd.notna(row[col]):
                try:
                    longitude = float(row[col])
                    break
                except:
                    pass
        
        # 如果都提取到了，返回实际坐标
        if latitude is not None and longitude is not None:
            return (latitude, longitude)
        
        # 否则生成模拟坐标
        return self._generate_coordinates(city_name, region_name)
    
    def _generate_coordinates(self, city_name: str, region_name: str) -> tuple:
        """生成经纬度坐标"""
        # 东京主要区域的坐标
        tokyo_coordinates = {
            "新宿": (35.6938, 139.7034),
            "涩谷": (35.6580, 139.7016),
            "池袋": (35.7314, 139.7289),
            "秋叶原": (35.7023, 139.7745),
            "浅草": (35.7148, 139.7967),
            "上野": (35.7138, 139.7770),
            "银座": (35.6654, 139.7704),
            "筑地": (35.6654, 139.7704),
            "品川": (35.6286, 139.7389),
            "日本桥": (35.6812, 139.7671),
            "日暮里": (35.7278, 139.7668),
            "台场": (35.6300, 139.7800),
            "丰洲": (35.6580, 139.7960),
            "六本木": (35.6614, 139.7300),
            "原宿": (35.6702, 139.7016),
            "表参道": (35.6654, 139.7120),
            "青山": (35.6654, 139.7120),
            "代官山": (35.6480, 139.7030),
            "惠比寿": (35.6470, 139.7100),
            "中目黑": (35.6430, 139.6980),
            "目黑": (35.6410, 139.6980),
            "五反田": (35.6260, 139.7230),
            "大崎": (35.6190, 139.7280),
            "田町": (35.6450, 139.7470),
            "滨松町": (35.6550, 139.7570),
            "有乐町": (35.6750, 139.7630),
            "新桥": (35.6660, 139.7590),
            "汐留": (35.6640, 139.7600)
        }
        
        # 查找匹配的区域
        for region, coords in tokyo_coordinates.items():
            if region in region_name or region in city_name:
                return coords
        
        # 默认返回东京中心坐标
        return (35.6762, 139.6503)
    
    def _translate_to_english(self, cn_name: str) -> str:
        """简单的中文到英文翻译"""
        translations = {
            "酒店": "Hotel",
            "旅馆": "Inn",
            "宾馆": "Guesthouse",
            "度假村": "Resort",
            "新宿": "Shinjuku",
            "华盛顿": "Washington",
            "利夫马克斯": "LiVEMAX",
            "秋叶原": "Akihabara",
            "浅草": "Asakusa",
            "吉居": "YOSHII",
            "琢居": "Takumi",
            "上野": "Ueno",
            "入谷口": "Iriyaguchi",
            "王子": "Prince",
            "品川": "Shinagawa",
            "日本桥": "Nihonbashi",
            "阿尔蒙特": "Almont",
            "日暮里": "Nippori",
            "三井花园": "Mitsui Garden",
            "银座": "Ginza",
            "筑地": "Tsukiji"
        }
        
        result = cn_name
        for cn, en in translations.items():
            result = result.replace(cn, en)
        
        return result
    
    def _translate_city_to_english(self, cn_city: str) -> str:
        """城市名翻译"""
        city_translations = {
            "东京": "Tokyo",
            "大阪": "Osaka",
            "京都": "Kyoto",
            "横滨": "Yokohama",
            "名古屋": "Nagoya",
            "神户": "Kobe",
            "福冈": "Fukuoka",
            "札幌": "Sapporo",
            "仙台": "Sendai",
            "广岛": "Hiroshima",
            "奈良": "Nara",
            "长野": "Nagano",
            "金泽": "Kanazawa",
            "冲绳": "Okinawa",
            "函馆": "Hakodate"
        }
        return city_translations.get(cn_city, cn_city)
    
    def _translate_city_to_japanese(self, cn_city: str) -> str:
        """城市名翻译为日文"""
        city_translations = {
            "东京": "東京",
            "大阪": "大阪",
            "京都": "京都",
            "横滨": "横浜",
            "名古屋": "名古屋",
            "神户": "神戸",
            "福冈": "福岡",
            "札幌": "札幌",
            "仙台": "仙台",
            "广岛": "広島",
            "奈良": "奈良",
            "长野": "長野",
            "金泽": "金沢",
            "冲绳": "沖縄",
            "函馆": "函館"
        }
        return city_translations.get(cn_city, cn_city)
    
    def _extract_city_from_address(self, address: str) -> str:
        """从地址中提取城市名"""
        if "东京" in address or "東京都" in address:
            return "东京"
        elif "大阪" in address:
            return "大阪"
        elif "京都" in address:
            return "京都"
        elif "横滨" in address or "横浜" in address:
            return "横滨"
        elif "名古屋" in address:
            return "名古屋"
        elif "神户" in address or "神戸" in address:
            return "神户"
        elif "福冈" in address or "福岡" in address:
            return "福冈"
        elif "札幌" in address:
            return "札幌"
        elif "仙台" in address:
            return "仙台"
        elif "广岛" in address or "広島" in address:
            return "广岛"
        else:
            return "东京"  # 默认东京
    
    def _extract_region_from_address(self, address: str) -> str:
        """从地址中提取区域名"""
        regions = ["新宿", "涩谷", "池袋", "秋叶原", "浅草", "上野", "银座", "筑地", 
                  "品川", "日本桥", "日暮里", "台场", "丰洲", "六本木", "原宿", 
                  "表参道", "青山", "代官山", "惠比寿", "中目黑", "目黑", "五反田", 
                  "大崎", "田町", "滨松町", "有乐町", "新桥", "汐留"]
        
        for region in regions:
            if region in address:
                return region + "地区"
        
        return "东京地区"
    
    def _format_price_range(self, price: str) -> str:
        """格式化价格范围"""
        # 提取数字
        numbers = re.findall(r'\d+', price)
        if len(numbers) >= 2:
            min_price = int(numbers[0])
            max_price = int(numbers[1])
            return f"¥{min_price:,}-{max_price:,}"
        elif len(numbers) == 1:
            price_val = int(numbers[0])
            return f"¥{price_val:,}-{price_val*1.5:,.0f}"
        else:
            return "¥8,000-15,000"  # 默认价格
    
    def _generate_price_by_stars(self, star_rating: int) -> str:
        """根据星级生成价格范围"""
        price_ranges = {
            1: "¥3,000-6,000",
            2: "¥5,000-10,000", 
            3: "¥8,000-15,000",
            4: "¥15,000-30,000",
            5: "¥25,000-50,000"
        }
        return price_ranges.get(star_rating, "¥8,000-15,000")
    
    def save_to_json(self, hotels: List[ExcelHotelData], filename: str = "data/excel_hotels.json") -> bool:
        """保存数据到JSON文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # 转换为字典格式
            hotel_dicts = []
            for hotel in hotels:
                hotel_dict = {
                    'hotel_id': hotel.hotel_id,
                    'hotel_name_cn': hotel.hotel_name_cn,
                    'hotel_name_en': hotel.hotel_name_en,
                    'hotel_name_jp': hotel.hotel_name_jp,
                    'city_name_cn': hotel.city_name_cn,
                    'city_name_en': hotel.city_name_en,
                    'city_name_jp': hotel.city_name_jp,
                    'region_name': hotel.region_name,
                    'address': hotel.address,
                    'country': hotel.country,
                    'search_count': hotel.search_count,
                    'latitude': hotel.latitude,
                    'longitude': hotel.longitude,
                    'price_range': hotel.price_range,
                    'star_rating': hotel.star_rating
                }
                hotel_dicts.append(hotel_dict)
            
            data = {'hotels': hotel_dicts}
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 成功保存 {len(hotels)} 家酒店数据到 {filename}")
            return True
            
        except Exception as e:
            print(f"❌ 保存数据时发生错误: {e}")
            return False
    
    def get_data_statistics(self, hotels: List[ExcelHotelData]) -> Dict:
        """获取数据统计信息"""
        if not hotels:
            return {}
        
        # 城市统计
        cities = {}
        for hotel in hotels:
            city = hotel.city_name_cn
            if city not in cities:
                cities[city] = {'count': 0, 'hotels': []}
            cities[city]['count'] += 1
            cities[city]['hotels'].append(hotel.hotel_name_cn)
        
        # 星级统计
        star_ratings = {}
        for hotel in hotels:
            rating = hotel.star_rating
            star_ratings[rating] = star_ratings.get(rating, 0) + 1
        
        # 价格范围统计
        price_ranges = {}
        for hotel in hotels:
            price_range = hotel.price_range
            price_ranges[price_range] = price_ranges.get(price_range, 0) + 1
        
        return {
            'total_hotels': len(hotels),
            'total_cities': len(cities),
            'cities': cities,
            'star_ratings': star_ratings,
            'price_ranges': price_ranges,
            'countries': list(set(hotel.country for hotel in hotels))
        }

def test_excel_loader():
    """测试Excel数据加载器"""
    print("📊 Excel数据加载器测试")
    print("=" * 60)
    
    # 初始化Excel数据加载器
    loader = ExcelDataLoader()
    
    # 加载Excel数据
    hotels = loader.load_excel_data()
    
    if not hotels:
        print("❌ 无法加载Excel数据")
        return
    
    # 获取统计信息
    stats = loader.get_data_statistics(hotels)
    
    print(f"\n📈 数据统计:")
    print(f"总酒店数: {stats['total_hotels']}")
    print(f"总城市数: {stats['total_cities']}")
    print(f"涉及国家: {', '.join(stats['countries'])}")
    
    print(f"\n🏙️ 城市分布:")
    for city, info in stats['cities'].items():
        print(f"  {city}: {info['count']}家酒店")
    
    print(f"\n⭐ 星级分布:")
    for stars, count in sorted(stats['star_ratings'].items()):
        print(f"  {stars}星: {count}家酒店")
    
    print(f"\n💰 价格范围分布 (前5个):")
    sorted_prices = sorted(stats['price_ranges'].items(), key=lambda x: x[1], reverse=True)
    for i, (price_range, count) in enumerate(sorted_prices[:5], 1):
        print(f"  {i}. {price_range}: {count}家酒店")
    
    # 显示前5家酒店的详细信息
    print(f"\n🏨 酒店数据示例 (前5家):")
    for i, hotel in enumerate(hotels[:5], 1):
        print(f"  {i}. {hotel.hotel_name_cn}")
        print(f"     英文: {hotel.hotel_name_en}")
        print(f"     城市: {hotel.city_name_cn} ({hotel.city_name_en})")
        print(f"     区域: {hotel.region_name}")
        print(f"     价格: {hotel.price_range} | 星级: {hotel.star_rating}星")
        print(f"     搜索热度: {hotel.search_count}")
        print()
    
    # 保存到JSON文件
    print(f"💾 保存数据到JSON文件:")
    success = loader.save_to_json(hotels, "data/excel_hotels.json")
    
    if success:
        print("✅ 数据保存成功，可用于后续测试")

if __name__ == "__main__":
    test_excel_loader() 