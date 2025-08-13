package com.qunar.hotel.search.webapp.config;

import com.qunar.hotel.search.core.index.HotelSearchIndex;
import com.qunar.hotel.search.core.index.HotelSuggestIndex;
import com.qunar.hotel.search.core.index.HotelSuggestIndexBuilder;
import com.qunar.hotel.search.core.utils.HotelDataLoader;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ComponentScan;

import java.io.IOException;
import java.util.List;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel Search Configuration
 */
@Configuration
@ComponentScan(basePackages = {
    "com.qunar.hotel.search.core",
    "com.qunar.hotel.search.service",
    "com.qunar.hotel.search.webapp"
})
public class HotelSearchConfig {
    
    /**
     * 初始化建议索引构建器
     */
    @Bean
    public HotelSuggestIndexBuilder hotelSuggestIndexBuilder() throws IOException {
        return new HotelSuggestIndexBuilder();
    }
    
    /**
     * 初始化搜索索引
     */
    @Bean
    public HotelSearchIndex hotelSearchIndex() {
        return new HotelSearchIndex();
    }
    
    /**
     * 初始化酒店数据加载器
     */
    @Bean
    public HotelDataLoader hotelDataLoader() throws IOException {
        HotelSuggestIndexBuilder suggestBuilder = hotelSuggestIndexBuilder();
        HotelSearchIndex searchIndex = hotelSearchIndex();
        return new HotelDataLoader(suggestBuilder, searchIndex);
    }
    
    /**
     * 初始化建议索引
     */
    @Bean
    public HotelSuggestIndex hotelSuggestIndex() throws IOException {
        HotelDataLoader dataLoader = hotelDataLoader();
        dataLoader.buildIndexes();
        return dataLoader.getSuggestIndexBuilder().build();
    }
} 