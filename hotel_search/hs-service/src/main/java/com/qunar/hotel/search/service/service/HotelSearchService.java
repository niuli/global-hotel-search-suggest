package com.qunar.hotel.search.service.service;

import com.qunar.hotel.search.core.model.HotelSearchResult;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel search service interface
 */
public interface HotelSearchService {
    
    /**
     * 搜索酒店
     *
     * @param query 查询词
     * @param page 页码
     * @param pageSize 每页大小
     * @return 搜索结果
     */
    HotelSearchResult search(String query, int page, int pageSize);
    
    /**
     * 搜索酒店（带地理位置）
     *
     * @param query 查询词
     * @param latitude 纬度
     * @param longitude 经度
     * @param page 页码
     * @param pageSize 每页大小
     * @return 搜索结果
     */
    HotelSearchResult search(String query, Double latitude, Double longitude, int page, int pageSize);
    
    /**
     * 搜索酒店（默认分页）
     *
     * @param query 查询词
     * @return 搜索结果
     */
    HotelSearchResult search(String query);
} 