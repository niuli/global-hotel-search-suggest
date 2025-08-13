#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日本酒店搜索系统专项测试
专门测试日本城市和酒店的搜索功能
"""

import json
import time
from typing import List, Dict, Set
from dataclasses import dataclass
from collections import defaultdict

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
    
    def __init__(self):
        self.normalizer = JapanHotelQueryNormalizer()
        self.hotels = self._load_japan_hotel_data()
        self.suggest_index = self._build_suggest_index()
    
    def _load_japan_hotel_data(self) -> List[JapanHotelInfo]:
        """加载日本酒店数据"""
        return [
            # 东京都酒店
            JapanHotelInfo("994914", "新宿华盛顿酒店", "Shinjuku Washington Hotel", "新宿ワシントンホテル", 
                          "东京", "Tokyo", "東京", "新宿地区", "东京都新宿区歌舞伎町1-30-1", "Japan", 1000, 35.6938, 139.7034, "¥8,000-15,000", 3),
            JapanHotelInfo("25457196", "利夫马克斯酒店-东京大冢站前店", "HOTEL LiVEMAX Tokyo Otsuka-Ekimae", "ホテルリブマックス東京大塚駅前", 
                          "东京", "Tokyo", "東京", "池袋地区", "东京都丰岛区大冢1-1-1", "Japan", 800, 35.7314, 139.7289, "¥6,000-12,000", 3),
            JapanHotelInfo("104430812", "东京秋叶原N+酒店", "N+HOTEL Akihabara", "N+ホテル秋葉原", 
                          "东京", "Tokyo", "東京", "秋叶原地区", "东京都千代田区外神田1-1-1", "Japan", 1200, 35.7023, 139.7745, "¥7,000-14,000", 3),
            JapanHotelInfo("45586346", "浅草吉居酒店·琢居", "Asakusa YOSHII Hotel", "浅草吉居ホテル・琢居", 
                          "东京", "Tokyo", "東京", "上野/浅草地区", "东京都台东区浅草1-1-1", "Japan", 900, 35.7148, 139.7967, "¥9,000-18,000", 4),
            JapanHotelInfo("688061", "MYSTAYS 上野入谷口酒店", "HOTEL MYSTAYS Ueno Iriyaguchi", "ホテルマイステイズ上野入谷口", 
                          "东京", "Tokyo", "東京", "上野/浅草地区", "东京都台东区上野1-1-1", "Japan", 1100, 35.7138, 139.7770, "¥8,000-16,000", 3),
            JapanHotelInfo("品川王子大酒店东塔", "Shinagawa Prince Hotel East Tower", "品川プリンスホテルイーストタワー", 
                          "东京", "Tokyo", "東京", "品川地区", "东京都港区高轮4-10-30", "Japan", 1500, 35.6286, 139.7389, "¥15,000-30,000", 4),
            JapanHotelInfo("东京日本桥N+酒店", "Nplus Hotel Tokyo Nihonbashi", "Nプラスホテル東京日本橋", 
                          "东京", "Tokyo", "東京", "东京站/日本桥地区", "东京都中央区日本桥1-1-1", "Japan", 1300, 35.6812, 139.7671, "¥12,000-25,000", 4),
            JapanHotelInfo("日暮里 阿尔蒙特酒店", "Almont Hotel Nippori", "アルモントホテル日暮里", 
                          "东京", "Tokyo", "東京", "上野/浅草地区", "东京都荒川区西日暮里1-1-1", "Japan", 700, 35.7278, 139.7668, "¥6,000-12,000", 3),
            JapanHotelInfo("东京秋叶原N+酒店(2号店)", "N+HOTEL Akihabara No.2", "N+ホテル秋葉原2号店", 
                          "东京", "Tokyo", "東京", "东京站/日本桥地区", "东京都千代田区外神田2-2-2", "Japan", 1000, 35.7023, 139.7745, "¥7,000-14,000", 3),
            JapanHotelInfo("三井花园酒店银座筑地", "Mitsui Garden Hotel Ginza Tsukiji", "三井ガーデンホテル銀座築地", 
                          "东京", "Tokyo", "東京", "银座/筑地地区", "东京都中央区筑地1-1-1", "Japan", 1400, 35.6654, 139.7704, "¥18,000-35,000", 4),
            
            # 大阪府酒店
            JapanHotelInfo("大阪威斯汀酒店", "The Westin Osaka", "ウェスティンホテル大阪", 
                          "大阪", "Osaka", "大阪", "梅田地区", "大阪府大阪市北区梅田1-1-1", "Japan", 1600, 34.7024, 135.4959, "¥20,000-40,000", 5),
            JapanHotelInfo("大阪丽思卡尔顿酒店", "The Ritz-Carlton Osaka", "ザ・リッツ・カールトン大阪", 
                          "大阪", "Osaka", "大阪", "梅田地区", "大阪府大阪市北区梅田2-2-2", "Japan", 1800, 34.7024, 135.4959, "¥35,000-70,000", 5),
            JapanHotelInfo("大阪难波东方酒店", "Hotel Oriental Express Osaka Namba", "ホテルオリエンタルエクスプレス大阪難波", 
                          "大阪", "Osaka", "大阪", "难波地区", "大阪府大阪市中央区难波3-3-3", "Japan", 1200, 34.6667, 135.5000, "¥8,000-16,000", 3),
            JapanHotelInfo("大阪心斋桥酒店", "Hotel Shinsaibashi Osaka", "ホテル心斎橋大阪", 
                          "大阪", "Osaka", "大阪", "心斋桥地区", "大阪府大阪市中央区心斋桥4-4-4", "Japan", 1100, 34.6667, 135.5000, "¥7,000-14,000", 3),
            JapanHotelInfo("大阪天王寺酒店", "Hotel Tennoji Osaka", "ホテル天王寺大阪", 
                          "大阪", "Osaka", "大阪", "天王寺地区", "大阪府大阪市天王寺区天王寺5-5-5", "Japan", 900, 34.6667, 135.5000, "¥6,000-12,000", 3),
            
            # 京都府酒店
            JapanHotelInfo("京都威斯汀都酒店", "The Westin Miyako Kyoto", "ウェスティンホテル都京都", 
                          "京都", "Kyoto", "京都", "东山地区", "京都府京都市东山区粟田口华顶町1-1-1", "Japan", 1700, 35.0116, 135.7681, "¥25,000-50,000", 5),
            JapanHotelInfo("京都四条乌丸酒店", "Hotel Shijo Karasuma Kyoto", "ホテル四条烏丸京都", 
                          "京都", "Kyoto", "京都", "四条地区", "京都府京都市下京区四条通乌丸东入6-6-6", "Japan", 1300, 35.0116, 135.7681, "¥10,000-20,000", 4),
            JapanHotelInfo("京都祗园酒店", "Hotel Gion Kyoto", "ホテル祇園京都", 
                          "京都", "Kyoto", "京都", "祗园地区", "京都府京都市东山区祗园町7-7-7", "Japan", 1400, 35.0116, 135.7681, "¥15,000-30,000", 4),
            JapanHotelInfo("京都清水寺酒店", "Hotel Kiyomizu Kyoto", "ホテル清水寺京都", 
                          "京都", "Kyoto", "京都", "清水寺地区", "京都府京都市东山区清水8-8-8", "Japan", 1200, 35.0116, 135.7681, "¥12,000-25,000", 4),
            JapanHotelInfo("京都岚山酒店", "Hotel Arashiyama Kyoto", "ホテル嵐山京都", 
                          "京都", "Kyoto", "京都", "岚山地区", "京都府京都市右京区岚山9-9-9", "Japan", 1100, 35.0116, 135.7681, "¥18,000-35,000", 4),
            
            # 横滨市酒店
            JapanHotelInfo("横滨皇家花园酒店", "Yokohama Royal Park Hotel", "横浜ロイヤルパークホテル", 
                          "横滨", "Yokohama", "横浜", "港未来地区", "神奈川县横滨市西区港未来2-2-1", "Japan", 1300, 35.4437, 139.6380, "¥20,000-40,000", 5),
            JapanHotelInfo("横滨关内酒店", "Hotel Kannai Yokohama", "ホテル関内横浜", 
                          "横滨", "Yokohama", "横浜", "关内地区", "神奈川县横滨市中区关内3-3-3", "Japan", 1000, 35.4437, 139.6380, "¥8,000-16,000", 3),
            JapanHotelInfo("横滨中华街酒店", "Hotel Chinatown Yokohama", "ホテル中華街横浜", 
                          "横滨", "Yokohama", "横浜", "中华街地区", "神奈川县横滨市中区山下町4-4-4", "Japan", 900, 35.4437, 139.6380, "¥7,000-14,000", 3),
            
            # 名古屋市酒店
            JapanHotelInfo("名古屋威斯汀城堡酒店", "The Westin Nagoya Castle", "ウェスティンホテル名古屋キャッスル", 
                          "名古屋", "Nagoya", "名古屋", "荣地区", "爱知县名古屋市中区荣5-5-5", "Japan", 1400, 35.1815, 136.9066, "¥18,000-35,000", 5),
            JapanHotelInfo("名古屋大须酒店", "Hotel Osu Nagoya", "ホテル大須名古屋", 
                          "名古屋", "Nagoya", "名古屋", "大须地区", "爱知县名古屋市中区大须6-6-6", "Japan", 1100, 35.1815, 136.9066, "¥9,000-18,000", 3),
            JapanHotelInfo("名古屋站前酒店", "Hotel Nagoya Station", "ホテル名古屋駅前", 
                          "名古屋", "Nagoya", "名古屋", "名古屋站地区", "爱知县名古屋市中村区名古屋站7-7-7", "Japan", 1200, 35.1815, 136.9066, "¥10,000-20,000", 4),
            
            # 神户市酒店
            JapanHotelInfo("神户美利坚公园东方酒店", "Kobe Meriken Park Oriental Hotel", "神戸メリケンパークオリエンタルホテル", 
                          "神户", "Kobe", "神戸", "港地区", "兵库县神户市中央区港岛8-8-8", "Japan", 1500, 34.6901, 135.1955, "¥25,000-50,000", 5),
            JapanHotelInfo("神户三宫酒店", "Hotel Sannomiya Kobe", "ホテル三宮神戸", 
                          "神户", "Kobe", "神戸", "三宫地区", "兵库县神户市中央区三宫町9-9-9", "Japan", 1200, 34.6901, 135.1955, "¥12,000-25,000", 4),
            JapanHotelInfo("神户元町酒店", "Hotel Motomachi Kobe", "ホテル元町神戸", 
                          "神户", "Kobe", "神戸", "元町地区", "兵库县神户市中央区元町通10-10-10", "Japan", 1000, 34.6901, 135.1955, "¥8,000-16,000", 3),
            
            # 福冈市酒店
            JapanHotelInfo("福冈博多酒店", "Hotel Hakata Fukuoka", "ホテル博多福岡", 
                          "福冈", "Fukuoka", "福岡", "博多地区", "福冈县福冈市博多区博多站前11-11-11", "Japan", 1300, 33.5902, 130.4017, "¥10,000-20,000", 4),
            JapanHotelInfo("福冈天神酒店", "Hotel Tenjin Fukuoka", "ホテル天神福岡", 
                          "福冈", "Fukuoka", "福岡", "天神地区", "福冈县福冈市中央区天神12-12-12", "Japan", 1400, 33.5902, 130.4017, "¥15,000-30,000", 4),
            JapanHotelInfo("福冈中洲酒店", "Hotel Nakasu Fukuoka", "ホテル中洲福岡", 
                          "福冈", "Fukuoka", "福岡", "中洲地区", "福冈县福冈市博多区中洲13-13-13", "Japan", 1100, 33.5902, 130.4017, "¥8,000-16,000", 3),
            
            # 札幌市酒店
            JapanHotelInfo("札幌大通酒店", "Hotel Odori Sapporo", "ホテル大通札幌", 
                          "札幌", "Sapporo", "札幌", "大通地区", "北海道札幌市中央区大通西14-14-14", "Japan", 1200, 43.0618, 141.3545, "¥12,000-25,000", 4),
            JapanHotelInfo("札幌薄野酒店", "Hotel Susukino Sapporo", "ホテル薄野札幌", 
                          "札幌", "Sapporo", "札幌", "薄野地区", "北海道札幌市中央区南5条西15-15-15", "Japan", 1000, 43.0618, 141.3545, "¥8,000-16,000", 3),
            JapanHotelInfo("札幌站前酒店", "Hotel Sapporo Station", "ホテル札幌駅前", 
                          "札幌", "Sapporo", "札幌", "札幌站地区", "北海道札幌市北区北6条西16-16-16", "Japan", 1300, 43.0618, 141.3545, "¥10,000-20,000", 4),
            
            # 仙台市酒店
            JapanHotelInfo("仙台威斯汀酒店", "The Westin Sendai", "ウェスティンホテル仙台", 
                          "仙台", "Sendai", "仙台", "仙台站地区", "宫城县仙台市青叶区中央17-17-17", "Japan", 1400, 38.2688, 140.8721, "¥18,000-35,000", 5),
            JapanHotelInfo("仙台一番町酒店", "Hotel Ichibancho Sendai", "ホテル一番町仙台", 
                          "仙台", "Sendai", "仙台", "一番町地区", "宫城县仙台市青叶区一番町18-18-18", "Japan", 1100, 38.2688, 140.8721, "¥12,000-25,000", 4),
            
            # 广岛市酒店
            JapanHotelInfo("广岛格兰王子酒店", "Grand Prince Hotel Hiroshima", "グランドプリンスホテル広島", 
                          "广岛", "Hiroshima", "広島", "广岛站地区", "广岛县广岛市中区基町19-19-19", "Japan", 1300, 34.3853, 132.4553, "¥20,000-40,000", 5),
            JapanHotelInfo("广岛本通酒店", "Hotel Hondori Hiroshima", "ホテル本通広島", 
                          "广岛", "Hiroshima", "広島", "本通地区", "广岛县广岛市中区本通20-20-20", "Japan", 1000, 34.3853, 132.4553, "¥8,000-16,000", 3),
            
            # 其他城市酒店
            JapanHotelInfo("奈良东大寺酒店", "Hotel Todaiji Nara", "ホテル東大寺奈良", 
                          "奈良", "Nara", "奈良", "东大寺地区", "奈良县奈良市杂司町21-21-21", "Japan", 900, 34.6851, 135.8050, "¥15,000-30,000", 4),
            JapanHotelInfo("长野善光寺酒店", "Hotel Zenkoji Nagano", "ホテル善光寺長野", 
                          "长野", "Nagano", "長野", "善光寺地区", "长野县长野市元善町22-22-22", "Japan", 800, 36.6489, 138.1948, "¥12,000-25,000", 4),
            JapanHotelInfo("金泽兼六园酒店", "Hotel Kenrokuen Kanazawa", "ホテル兼六園金沢", 
                          "金泽", "Kanazawa", "金沢", "兼六园地区", "石川县金泽市兼六町23-23-23", "Japan", 1200, 36.5613, 136.6562, "¥18,000-35,000", 4),
            JapanHotelInfo("冲绳那霸酒店", "Hotel Naha Okinawa", "ホテル那覇沖縄", 
                          "冲绳", "Okinawa", "沖縄", "那霸地区", "冲绳县那霸市国际通24-24-24", "Japan", 1500, 26.2124, 127.6809, "¥15,000-30,000", 4),
            JapanHotelInfo("函馆五棱郭酒店", "Hotel Goryokaku Hakodate", "ホテル五稜郭函館", 
                          "函馆", "Hakodate", "函館", "五棱郭地区", "北海道函馆市五棱郭町25-25-25", "Japan", 1000, 41.7688, 140.7289, "¥12,000-25,000", 4),
        ]
    
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
    print("🗾 日本酒店搜索系统专项测试")
    print("=" * 60)
    
    system = JapanHotelSearchSystem()
    
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

if __name__ == "__main__":
    test_japan_hotels() 