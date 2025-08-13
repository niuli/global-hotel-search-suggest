#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
酒店搜索系统 API 测试脚本
模拟HTTP请求测试API接口
"""

import json
import time
from typing import Dict, Any
from test_demo import HotelSearchSystem

class MockAPIServer:
    """模拟API服务器"""
    
    def __init__(self):
        self.system = HotelSearchSystem()
    
    def suggest_api(self, query: str, count: int = 10) -> Dict[str, Any]:
        """建议搜索API"""
        try:
            if not query or query.strip() == "":
                return {
                    "success": False,
                    "message": "Query parameter is required",
                    "data": None,
                    "timestamp": int(time.time() * 1000)
                }
            
            if count <= 0 or count > 50:
                count = 10
            
            suggestions = self.system.suggest(query.strip(), count)
            
            return {
                "success": True,
                "message": "success",
                "data": [
                    {
                        "displayName": s.display_name,
                        "hotelName": s.hotel_name,
                        "cityName": s.city_name,
                        "regionName": s.region_name,
                        "country": s.country,
                        "hotelId": s.hotel_id
                    }
                    for s in suggestions
                ],
                "timestamp": int(time.time() * 1000)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": None,
                "timestamp": int(time.time() * 1000)
            }
    
    def search_api(self, query: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """全文搜索API"""
        try:
            if not query or query.strip() == "":
                return {
                    "success": False,
                    "message": "Query parameter is required",
                    "data": None,
                    "timestamp": int(time.time() * 1000)
                }
            
            if page <= 0:
                page = 1
            if page_size <= 0 or page_size > 100:
                page_size = 20
            
            result = self.system.search(query.strip(), page, page_size)
            
            return {
                "success": True,
                "message": "success",
                "data": {
                    "hotels": [
                        {
                            "hotelId": h.hotel_id,
                            "hotelNameCn": h.hotel_name_cn,
                            "hotelNameEn": h.hotel_name_en,
                            "cityNameCn": h.city_name_cn,
                            "cityNameEn": h.city_name_en,
                            "regionName": h.region_name,
                            "address": h.address,
                            "country": h.country,
                            "searchCount": h.search_count,
                            "latitude": h.latitude,
                            "longitude": h.longitude
                        }
                        for h in result.hotels
                    ],
                    "totalCount": result.total_count,
                    "page": result.page,
                    "pageSize": result.page_size,
                    "totalPages": result.total_pages
                },
                "timestamp": int(time.time() * 1000)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": None,
                "timestamp": int(time.time() * 1000)
            }

def test_suggest_api():
    """测试建议搜索API"""
    print("🔍 测试酒店建议搜索 API")
    print("=" * 60)
    
    server = MockAPIServer()
    
    # 测试用例
    test_cases = [
        {"query": "东京", "count": 5},
        {"query": "新宿", "count": 3},
        {"query": "秋叶原", "count": 2},
        {"query": "tokyo", "count": 5},
        {"query": "shinjuku", "count": 3},
        {"query": "akihabara", "count": 2},
        {"query": "上野", "count": 4},
        {"query": "银座", "count": 2},
        {"query": "", "count": 5},  # 空查询
        {"query": "不存在的酒店", "count": 5},  # 无结果
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 测试用例 {i}: 查询='{case['query']}', count={case['count']}")
        print("-" * 40)
        
        response = server.suggest_api(case["query"], case["count"])
        
        print(f"响应状态: {'✅ 成功' if response['success'] else '❌ 失败'}")
        print(f"响应消息: {response['message']}")
        print(f"响应时间: {response['timestamp']}")
        
        if response['success'] and response['data']:
            print(f"返回结果数量: {len(response['data'])}")
            for j, suggestion in enumerate(response['data'], 1):
                print(f"  {j}. {suggestion['displayName']}")
                print(f"     酒店: {suggestion['hotelName']}")
                print(f"     城市: {suggestion['cityName']} | 区域: {suggestion['regionName']}")
        elif response['success']:
            print("返回结果: 空")
        else:
            print(f"错误信息: {response['message']}")
        
        print()

def test_search_api():
    """测试全文搜索API"""
    print("🔎 测试酒店全文搜索 API")
    print("=" * 60)
    
    server = MockAPIServer()
    
    # 测试用例
    test_cases = [
        {"query": "新宿", "page": 1, "page_size": 5},
        {"query": "秋叶原", "page": 1, "page_size": 3},
        {"query": "上野", "page": 1, "page_size": 4},
        {"query": "银座", "page": 1, "page_size": 2},
        {"query": "tokyo", "page": 1, "page_size": 5},
        {"query": "shinjuku", "page": 1, "page_size": 3},
        {"query": "不存在的酒店", "page": 1, "page_size": 5},  # 无结果
        {"query": "", "page": 1, "page_size": 5},  # 空查询
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 测试用例 {i}: 查询='{case['query']}', page={case['page']}, page_size={case['page_size']}")
        print("-" * 40)
        
        response = server.search_api(case["query"], case["page"], case["page_size"])
        
        print(f"响应状态: {'✅ 成功' if response['success'] else '❌ 失败'}")
        print(f"响应消息: {response['message']}")
        print(f"响应时间: {response['timestamp']}")
        
        if response['success'] and response['data']:
            data = response['data']
            print(f"总结果数: {data['totalCount']}")
            print(f"当前页: {data['page']}/{data['totalPages']}")
            print(f"每页大小: {data['pageSize']}")
            print(f"当前页结果数: {len(data['hotels'])}")
            
            for j, hotel in enumerate(data['hotels'], 1):
                print(f"  {j}. {hotel['hotelNameCn']} ({hotel['hotelNameEn']})")
                print(f"     城市: {hotel['cityNameCn']} | 区域: {hotel['regionName']}")
                print(f"     地址: {hotel['address']}")
                print(f"     搜索热度: {hotel['searchCount']}")
        elif response['success']:
            print("返回结果: 空")
        else:
            print(f"错误信息: {response['message']}")
        
        print()

def test_api_performance():
    """测试API性能"""
    print("⚡ 测试API性能")
    print("=" * 60)
    
    server = MockAPIServer()
    
    # 性能测试用例
    performance_tests = [
        {"name": "建议搜索性能测试", "api": "suggest", "queries": ["东京", "新宿", "秋叶原", "tokyo", "shinjuku"] * 20},
        {"name": "全文搜索性能测试", "api": "search", "queries": ["新宿", "秋叶原", "上野", "银座", "tokyo"] * 20},
    ]
    
    for test in performance_tests:
        print(f"\n📊 {test['name']}")
        print("-" * 40)
        
        start_time = time.time()
        success_count = 0
        total_count = len(test['queries'])
        
        for query in test['queries']:
            if test['api'] == 'suggest':
                response = server.suggest_api(query, 5)
            else:
                response = server.search_api(query, 1, 5)
            
            if response['success']:
                success_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / total_count * 1000  # 转换为毫秒
        
        print(f"总查询数: {total_count}")
        print(f"成功查询数: {success_count}")
        print(f"成功率: {success_count/total_count*100:.2f}%")
        print(f"总耗时: {total_time:.3f}秒")
        print(f"平均耗时: {avg_time:.2f}毫秒")
        print(f"QPS: {total_count/total_time:.2f}")

def test_api_edge_cases():
    """测试API边界情况"""
    print("🔬 测试API边界情况")
    print("=" * 60)
    
    server = MockAPIServer()
    
    # 边界测试用例
    edge_cases = [
        {"name": "空查询", "query": "", "count": 5},
        {"name": "单字符查询", "query": "a", "count": 5},
        {"name": "超长查询", "query": "这是一个非常长的查询字符串用来测试系统的处理能力", "count": 5},
        {"name": "特殊字符查询", "query": "!@#$%^&*()", "count": 5},
        {"name": "数字查询", "query": "12345", "count": 5},
        {"name": "混合字符查询", "query": "东京Tokyo123", "count": 5},
        {"name": "零count", "query": "东京", "count": 0},
        {"name": "超大count", "query": "东京", "count": 100},
        {"name": "负数count", "query": "东京", "count": -1},
    ]
    
    for case in edge_cases:
        print(f"\n📋 {case['name']}: 查询='{case['query']}', count={case['count']}")
        print("-" * 40)
        
        response = server.suggest_api(case['query'], case['count'])
        
        print(f"响应状态: {'✅ 成功' if response['success'] else '❌ 失败'}")
        print(f"响应消息: {response['message']}")
        
        if response['success'] and response['data']:
            print(f"返回结果数量: {len(response['data'])}")
        elif response['success']:
            print("返回结果: 空")
        else:
            print(f"错误信息: {response['message']}")

def main():
    """主测试函数"""
    print("🏨 酒店搜索系统 API 测试")
    print("=" * 80)
    
    # 运行所有测试
    test_suggest_api()
    test_search_api()
    test_api_performance()
    test_api_edge_cases()
    
    print("\n🎉 所有测试完成！")

if __name__ == "__main__":
    main() 