package com.qunar.hotel.search.webapp.controller;

import com.qunar.hotel.search.core.model.HotelSuggestElem;
import com.qunar.hotel.search.service.service.HotelSuggestService;
import com.qunar.hotel.search.webapp.model.ApiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel suggest API controller
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/hotel/suggest")
public class HotelSuggestController {
    
    private final HotelSuggestService suggestService;
    
    @Autowired
    public HotelSuggestController(HotelSuggestService suggestService) {
        this.suggestService = suggestService;
    }
    
    /**
     * 获取酒店建议
     *
     * @param query 查询词
     * @param count 返回数量（可选，默认10）
     * @return 建议列表
     */
    @GetMapping
    public ApiResponse<List<HotelSuggestElem>> suggest(
            @RequestParam("q") String query,
            @RequestParam(value = "count", defaultValue = "10") int count) {
        
        log.info("Hotel suggest API request: query={}, count={}", query, count);
        
        try {
            if (query == null || query.trim().isEmpty()) {
                return ApiResponse.error("Query parameter is required");
            }
            
            if (count <= 0 || count > 50) {
                count = 10;
            }
            
            List<HotelSuggestElem> result = suggestService.suggest(query.trim(), count);
            return ApiResponse.success(result);
            
        } catch (Exception e) {
            log.error("Error in hotel suggest API: query={}", query, e);
            return ApiResponse.error("Internal server error");
        }
    }
    
    /**
     * 获取酒店建议（POST方式）
     *
     * @param request 请求参数
     * @return 建议列表
     */
    @PostMapping
    public ApiResponse<List<HotelSuggestElem>> suggestPost(@RequestBody SuggestRequest request) {
        
        log.info("Hotel suggest POST API request: {}", request);
        
        try {
            if (request.getQuery() == null || request.getQuery().trim().isEmpty()) {
                return ApiResponse.error("Query parameter is required");
            }
            
            int count = request.getCount() != null ? request.getCount() : 10;
            if (count <= 0 || count > 50) {
                count = 10;
            }
            
            List<HotelSuggestElem> result = suggestService.suggest(request.getQuery().trim(), count);
            return ApiResponse.success(result);
            
        } catch (Exception e) {
            log.error("Error in hotel suggest POST API: request={}", request, e);
            return ApiResponse.error("Internal server error");
        }
    }
    
    /**
     * 请求参数类
     */
    public static class SuggestRequest {
        private String query;
        private Integer count;
        
        public String getQuery() {
            return query;
        }
        
        public void setQuery(String query) {
            this.query = query;
        }
        
        public Integer getCount() {
            return count;
        }
        
        public void setCount(Integer count) {
            this.count = count;
        }
        
        @Override
        public String toString() {
            return "SuggestRequest{query='" + query + "', count=" + count + "}";
        }
    }
} 