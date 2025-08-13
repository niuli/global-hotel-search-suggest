package com.qunar.hotel.search.core.utils;

import com.qunar.hotel.search.core.index.HotelSearchIndex;
import com.qunar.hotel.search.core.index.HotelSuggestIndexBuilder;
import com.qunar.hotel.search.core.model.HotelInfo;
import lombok.extern.slf4j.Slf4j;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel data loader for building indexes from Excel data
 */
@Slf4j
public class HotelDataLoader {
    
    private final HotelSuggestIndexBuilder suggestIndexBuilder;
    private final HotelSearchIndex searchIndex;
    
    public HotelDataLoader(HotelSuggestIndexBuilder suggestIndexBuilder, HotelSearchIndex searchIndex) {
        this.suggestIndexBuilder = suggestIndexBuilder;
        this.searchIndex = searchIndex;
    }
    
    /**
     * 从Excel数据构建索引
     * 这里使用模拟数据，实际项目中应该从Excel文件读取
     */
    public void buildIndexes() throws IOException {
        log.info("Starting to build hotel indexes...");
        
        List<HotelInfo> hotels = generateSampleData();
        
        // 构建建议索引
        for (HotelInfo hotel : hotels) {
            // 添加酒店名称
            suggestIndexBuilder.add(hotel.getHotelNameCn(), hotel.getHotelNameCn(), 
                    hotel.getCityNameCn(), hotel.getRegionName(), 
                    hotel.getSearchCount(), hotel.getHotelNameCn(), "Japan");
            
            suggestIndexBuilder.add(hotel.getHotelNameEn(), hotel.getHotelNameCn(), 
                    hotel.getCityNameCn(), hotel.getRegionName(), 
                    hotel.getSearchCount(), hotel.getHotelNameEn(), "Japan");
            
            // 添加城市名称
            suggestIndexBuilder.add(hotel.getCityNameCn(), hotel.getHotelNameCn(), 
                    hotel.getCityNameCn(), hotel.getRegionName(), 
                    hotel.getSearchCount(), hotel.getCityNameCn(), "Japan");
            
            suggestIndexBuilder.add(hotel.getCityNameEn(), hotel.getHotelNameCn(), 
                    hotel.getCityNameCn(), hotel.getRegionName(), 
                    hotel.getSearchCount(), hotel.getCityNameEn(), "Japan");
            
            // 添加区域名称
            suggestIndexBuilder.add(hotel.getRegionName(), hotel.getHotelNameCn(), 
                    hotel.getCityNameCn(), hotel.getRegionName(), 
                    hotel.getSearchCount(), hotel.getRegionName(), "Japan");
            
            // 添加到搜索索引
            searchIndex.addHotel(hotel);
        }
        
        log.info("Successfully built indexes for {} hotels", hotels.size());
    }
    
    /**
     * 获取建议索引构建器
     */
    public HotelSuggestIndexBuilder getSuggestIndexBuilder() {
        return suggestIndexBuilder;
    }
    
    /**
     * 获取搜索索引
     */
    public HotelSearchIndex getSearchIndex() {
        return searchIndex;
    }
    
    /**
     * 生成示例数据（基于Excel文件结构）
     */
    private List<HotelInfo> generateSampleData() {
        List<HotelInfo> hotels = new ArrayList<>();
        
        // 基于Excel文件中的数据结构生成示例数据
        hotels.add(new HotelInfo("994914", "新宿华盛顿酒店", "Shinjuku Washington Hotel", 
                "东京", "Tokyo", "新宿地区", "东京都新宿区歌舞伎町1-30-1", "Japan", 1000L, 35.6938, 139.7034));
        
        hotels.add(new HotelInfo("25457196", "利夫马克斯酒店-东京大冢站前店", "HOTEL LiVEMAX Tokyo Otsuka-Ekimae", 
                "东京", "Tokyo", "池袋地区", "东京都丰岛区大冢1-1-1", "Japan", 800L, 35.7314, 139.7289));
        
        hotels.add(new HotelInfo("104430812", "东京秋叶原N+酒店", "N+HOTEL Akihabara", 
                "东京", "Tokyo", "秋叶原地区", "东京都千代田区外神田1-1-1", "Japan", 1200L, 35.7023, 139.7745));
        
        hotels.add(new HotelInfo("45586346", "浅草吉居酒店·琢居", "Asakusa YOSHII Hotel", 
                "东京", "Tokyo", "上野/浅草地区", "东京都台东区浅草1-1-1", "Japan", 900L, 35.7148, 139.7967));
        
        hotels.add(new HotelInfo("688061", "MYSTAYS 上野入谷口酒店", "HOTEL MYSTAYS Ueno Iriyaguchi", 
                "东京", "Tokyo", "上野/浅草地区", "东京都台东区上野1-1-1", "Japan", 1100L, 35.7138, 139.7770));
        
        hotels.add(new HotelInfo("品川王子大酒店东塔", "品川王子大酒店东塔", "Shinagawa Prince Hotel East Tower", 
                "东京", "Tokyo", "品川地区", "东京都港区高轮4-10-30", "Japan", 1500L, 35.6286, 139.7389));
        
        hotels.add(new HotelInfo("东京日本桥N+酒店", "东京日本桥N+酒店", "Nplus Hotel Tokyo Nihonbashi", 
                "东京", "Tokyo", "东京站/日本桥地区", "东京都中央区日本桥1-1-1", "Japan", 1300L, 35.6812, 139.7671));
        
        hotels.add(new HotelInfo("日暮里 阿尔蒙特酒店", "日暮里 阿尔蒙特酒店", "Almont Hotel Nippori", 
                "东京", "Tokyo", "上野/浅草地区", "东京都荒川区西日暮里1-1-1", "Japan", 700L, 35.7278, 139.7668));
        
        hotels.add(new HotelInfo("东京秋叶原N+酒店(2号店)", "东京秋叶原N+酒店(2号店)", "N+HOTEL Akihabara No.2", 
                "东京", "Tokyo", "东京站/日本桥地区", "东京都千代田区外神田2-2-2", "Japan", 1000L, 35.7023, 139.7745));
        
        hotels.add(new HotelInfo("三井花园酒店银座筑地", "三井花园酒店银座筑地", "Mitsui Garden Hotel Ginza Tsukiji", 
                "东京", "Tokyo", "银座/筑地地区", "东京都中央区筑地1-1-1", "Japan", 1400L, 35.6654, 139.7704));
        
        return hotels;
    }
} 