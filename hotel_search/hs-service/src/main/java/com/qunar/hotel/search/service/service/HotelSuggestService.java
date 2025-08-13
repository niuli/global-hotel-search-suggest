package com.qunar.hotel.search.service.service;

import com.qunar.hotel.search.core.model.HotelSuggestElem;
import java.util.List;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel suggest service interface
 */
public interface HotelSuggestService {
    
    /**
     * 获取酒店建议
     *
     * @param query 查询词
     * @param count 返回数量
     * @return 建议列表
     */
    List<HotelSuggestElem> suggest(String query, int count);
    
    /**
     * 获取酒店建议（默认返回10个）
     *
     * @param query 查询词
     * @return 建议列表
     */
    List<HotelSuggestElem> suggest(String query);
} 