#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据加载器模块
专门处理酒店数据的加载和解析
"""

import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class HotelData:
    """酒店数据结构"""
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

class DataLoader:
    """数据加载器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
    
    def load_japan_hotels(self, filename: str = "japan_hotels.json") -> List[HotelData]:
        """加载日本酒店数据"""
        file_path = os.path.join(self.data_dir, filename)
        return self._load_hotel_data(file_path)
    
    def load_hotel_data(self, filename: str) -> List[HotelData]:
        """加载通用酒店数据"""
        file_path = os.path.join(self.data_dir, filename)
        return self._load_hotel_data(file_path)
    
    def _load_hotel_data(self, file_path: str) -> List[HotelData]:
        """从JSON文件加载酒店数据"""
        try:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(current_dir, file_path)
            
            if not os.path.exists(full_path):
                print(f"❌ 数据文件未找到: {full_path}")
                return []
            
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            hotels = []
            for hotel_data in data.get('hotels', []):
                hotel = HotelData(
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
            print(f"❌ 数据文件未找到: {file_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ JSON文件解析错误: {e}")
            return []
        except KeyError as e:
            print(f"❌ 数据格式错误，缺少必要字段: {e}")
            return []
        except Exception as e:
            print(f"❌ 加载数据时发生错误: {e}")
            return []
    
    def save_hotel_data(self, hotels: List[HotelData], filename: str) -> bool:
        """保存酒店数据到JSON文件"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
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
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 成功保存 {len(hotels)} 家酒店数据到 {filename}")
            return True
            
        except Exception as e:
            print(f"❌ 保存数据时发生错误: {e}")
            return False
    
    def get_data_statistics(self, hotels: List[HotelData]) -> Dict:
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
    
    def filter_hotels_by_city(self, hotels: List[HotelData], city: str) -> List[HotelData]:
        """按城市筛选酒店"""
        return [hotel for hotel in hotels if hotel.city_name_cn == city]
    
    def filter_hotels_by_star_rating(self, hotels: List[HotelData], min_stars: int) -> List[HotelData]:
        """按星级筛选酒店"""
        return [hotel for hotel in hotels if hotel.star_rating >= min_stars]
    
    def filter_hotels_by_price_range(self, hotels: List[HotelData], max_price: str) -> List[HotelData]:
        """按价格范围筛选酒店"""
        # 这里可以实现更复杂的价格解析逻辑
        return hotels  # 简化实现
    
    def search_hotels_by_name(self, hotels: List[HotelData], keyword: str) -> List[HotelData]:
        """按酒店名称搜索"""
        keyword = keyword.lower()
        results = []
        
        for hotel in hotels:
            if (keyword in hotel.hotel_name_cn.lower() or 
                keyword in hotel.hotel_name_en.lower() or
                keyword in hotel.hotel_name_jp.lower()):
                results.append(hotel)
        
        return results

def test_data_loader():
    """测试数据加载器"""
    print("📊 数据加载器测试")
    print("=" * 50)
    
    # 初始化数据加载器
    loader = DataLoader()
    
    # 加载日本酒店数据
    hotels = loader.load_japan_hotels()
    
    if not hotels:
        print("❌ 无法加载酒店数据")
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
    
    # 测试筛选功能
    print(f"\n🔍 筛选测试:")
    
    # 按城市筛选
    tokyo_hotels = loader.filter_hotels_by_city(hotels, "东京")
    print(f"东京酒店: {len(tokyo_hotels)}家")
    
    # 按星级筛选
    high_star_hotels = loader.filter_hotels_by_star_rating(hotels, 4)
    print(f"4星以上酒店: {len(high_star_hotels)}家")
    
    # 按名称搜索
    westin_hotels = loader.search_hotels_by_name(hotels, "威斯汀")
    print(f"威斯汀酒店: {len(westin_hotels)}家")
    
    # 测试保存功能
    print(f"\n💾 保存测试:")
    test_filename = "test_hotels.json"
    success = loader.save_hotel_data(tokyo_hotels, test_filename)
    
    if success:
        # 重新加载测试
        loaded_hotels = loader.load_hotel_data(test_filename)
        print(f"重新加载测试数据: {len(loaded_hotels)}家酒店")
        
        # 清理测试文件
        try:
            os.remove(os.path.join("data", test_filename))
            print("✅ 清理测试文件完成")
        except:
            pass

if __name__ == "__main__":
    test_data_loader() 