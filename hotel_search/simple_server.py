#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的HTTP服务器
用于提供Excel酒店搜索系统的Web服务
"""

import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs

class HotelSearchHandler(http.server.SimpleHTTPRequestHandler):
    """酒店搜索HTTP处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # 处理API请求
        if path.startswith('/api/'):
            self.handle_api_request(path, parsed_url.query)
            return
        
        # 处理静态文件
        if path == '/':
            path = '/excel_web_demo_real.html'
        
        # 设置正确的MIME类型
        if path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
        elif path.endswith('.json'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
        else:
            return super().do_GET()
        
        # 读取并发送文件
        try:
            file_path = os.path.join(os.getcwd(), path.lstrip('/'))
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                self.wfile.write(content)
            else:
                self.send_error(404, 'File not found')
        except Exception as e:
            self.send_error(500, f'Server error: {str(e)}')
    
    def handle_api_request(self, path, query):
        """处理API请求"""
        if path == '/api/search':
            self.handle_search_api(query)
        elif path == '/api/suggest':
            self.handle_suggest_api(query)
        elif path == '/api/stats':
            self.handle_stats_api()
        else:
            self.send_error(404, 'API not found')
    
    def handle_search_api(self, query):
        """处理搜索API"""
        try:
            params = parse_qs(query)
            query_text = params.get('q', [''])[0]
            # 处理URL编码
            import urllib.parse
            query_text = urllib.parse.unquote(query_text)
            
            # 加载酒店数据
            hotels = self.load_hotel_data()
            
            # 执行搜索
            results = self.search_hotels(hotels, query_text, 'search')
            
            # 返回结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'query': query_text,
                'total': len(results),
                'results': results[:20]  # 限制返回20个结果
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f'Search error: {str(e)}')
    
    def handle_suggest_api(self, query):
        """处理建议API"""
        try:
            params = parse_qs(query)
            query_text = params.get('q', [''])[0]
            # 处理URL编码
            import urllib.parse
            query_text = urllib.parse.unquote(query_text)
            
            # 加载酒店数据
            hotels = self.load_hotel_data()
            
            # 执行建议搜索
            results = self.search_hotels(hotels, query_text, 'suggest')
            
            # 返回结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'query': query_text,
                'total': len(results),
                'results': results[:10]  # 限制返回10个建议
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f'Suggest error: {str(e)}')
    
    def handle_stats_api(self):
        """处理统计API"""
        try:
            # 加载酒店数据
            hotels = self.load_hotel_data()
            
            # 计算统计信息
            stats = self.calculate_stats(hotels)
            
            # 返回结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'stats': stats
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f'Stats error: {str(e)}')
    
    def load_hotel_data(self):
        """加载酒店数据"""
        try:
            with open('data/excel_hotels.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('hotels', [])
        except Exception as e:
            print(f"加载酒店数据失败: {e}")
            return []
    
    def search_hotels(self, hotels, query, search_type):
        """搜索酒店"""
        if not query or not hotels:
            return []
        
        query_lower = query.lower()
        results = []
        
        for hotel in hotels:
            score = 0
            
            if search_type == 'suggest':
                # 智能建议搜索
                if hotel.get('hotel_name_cn', '').lower().find(query_lower) >= 0:
                    score += 0.8
                if hotel.get('hotel_name_en', '').lower().find(query_lower) >= 0:
                    score += 0.7
                if hotel.get('city_name_cn', '').lower().find(query_lower) >= 0:
                    score += 0.9
                if hotel.get('region_name', '').lower().find(query_lower) >= 0:
                    score += 0.6
                
                # 搜索热度影响
                search_count = hotel.get('search_count', 500)
                score += (search_count / 1000) * 0.1
                
            else:
                # 精确搜索
                if (hotel.get('hotel_name_cn', '').lower().find(query_lower) >= 0 or
                    hotel.get('hotel_name_en', '').lower().find(query_lower) >= 0):
                    score = 1.0
            
            if score > 0.3:
                results.append({
                    **hotel,
                    'score': score
                })
        
        # 按评分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def calculate_stats(self, hotels):
        """计算统计信息"""
        if not hotels:
            return {}
        
        # 城市统计
        cities = {}
        for hotel in hotels:
            city = hotel.get('city_name_cn', '未知城市')
            cities[city] = cities.get(city, 0) + 1
        
        # 区域统计
        regions = {}
        for hotel in hotels:
            region = hotel.get('region_name', '未知区域')
            regions[region] = regions.get(region, 0) + 1
        
        return {
            'total_hotels': len(hotels),
            'total_cities': len(cities),
            'tokyo_hotels': cities.get('东京', 0),
            'top_cities': sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10],
            'top_regions': sorted(regions.items(), key=lambda x: x[1], reverse=True)[:10]
        }

def start_server(port=8000):
    """启动服务器"""
    with socketserver.TCPServer(("", port), HotelSearchHandler) as httpd:
        print(f"🚀 Excel酒店搜索服务器已启动")
        print(f"📊 访问地址: http://localhost:{port}")
        print(f"🗾 数据规模: 2377家酒店")
        print(f"🌐 支持功能: 搜索、建议、统计")
        print(f"⏹️  按 Ctrl+C 停止服务器")
        print("-" * 50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")

if __name__ == "__main__":
    start_server() 