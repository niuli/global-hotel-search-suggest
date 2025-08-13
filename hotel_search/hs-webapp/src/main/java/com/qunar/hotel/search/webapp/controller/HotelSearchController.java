package com.qunar.hotel.search.webapp.controller;

import com.qunar.hotel.search.core.model.HotelSearchResult;
import com.qunar.hotel.search.service.service.HotelSearchService;
import com.qunar.hotel.search.webapp.model.ApiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel search API controller
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/hotel/search")
public class HotelSearchController {
    
    private final HotelSearchService searchService;
    
    @Autowired
    public HotelSearchController(HotelSearchService searchService) {
        this.searchService = searchService;
    }
    
    /**
     * 搜索酒店
     *
     * @param query 查询词
     * @param page 页码（可选，默认1）
     * @param pageSize 每页大小（可选，默认20）
     * @return 搜索结果
     */
    @GetMapping
    public ApiResponse<HotelSearchResult> search(
            @RequestParam("q") String query,
            @RequestParam(value = "page", defaultValue = "1") int page,
            @RequestParam(value = "pageSize", defaultValue = "20") int pageSize) {
        
        log.info("Hotel search API request: query={}, page={}, pageSize={}", query, page, pageSize);
        
        try {
            if (query == null || query.trim().isEmpty()) {
                return ApiResponse.error("Query parameter is required");
            }
            
            if (page <= 0) {
                page = 1;
            }
            if (pageSize <= 0 || pageSize > 100) {
                pageSize = 20;
            }
            
            HotelSearchResult result = searchService.search(query.trim(), page, pageSize);
            return ApiResponse.success(result);
            
        } catch (Exception e) {
            log.error("Error in hotel search API: query={}", query, e);
            return ApiResponse.error("Internal server error");
        }
    }
    
    /**
     * 搜索酒店（带地理位置）
     *
     * @param query 查询词
     * @param latitude 纬度
     * @param longitude 经度
     * @param page 页码（可选，默认1）
     * @param pageSize 每页大小（可选，默认20）
     * @return 搜索结果
     */
    @GetMapping("/geo")
    public ApiResponse<HotelSearchResult> searchWithGeo(
            @RequestParam("q") String query,
            @RequestParam("lat") Double latitude,
            @RequestParam("lng") Double longitude,
            @RequestParam(value = "page", defaultValue = "1") int page,
            @RequestParam(value = "pageSize", defaultValue = "20") int pageSize) {
        
        log.info("Hotel search with geo API request: query={}, lat={}, lng={}, page={}, pageSize={}", 
                query, latitude, longitude, page, pageSize);
        
        try {
            if (query == null || query.trim().isEmpty()) {
                return ApiResponse.error("Query parameter is required");
            }
            
            if (latitude == null || longitude == null) {
                return ApiResponse.error("Latitude and longitude parameters are required");
            }
            
            if (page <= 0) {
                page = 1;
            }
            if (pageSize <= 0 || pageSize > 100) {
                pageSize = 20;
            }
            
            HotelSearchResult result = searchService.search(query.trim(), latitude, longitude, page, pageSize);
            return ApiResponse.success(result);
            
        } catch (Exception e) {
            log.error("Error in hotel search with geo API: query={}, lat={}, lng={}", 
                    query, latitude, longitude, e);
            return ApiResponse.error("Internal server error");
        }
    }
    
    /**
     * 搜索酒店（POST方式）
     *
     * @param request 请求参数
     * @return 搜索结果
     */
    @PostMapping
    public ApiResponse<HotelSearchResult> searchPost(@RequestBody SearchRequest request) {
        
        log.info("Hotel search POST API request: {}", request);
        
        try {
            if (request.getQuery() == null || request.getQuery().trim().isEmpty()) {
                return ApiResponse.error("Query parameter is required");
            }
            
            int page = request.getPage() != null ? request.getPage() : 1;
            int pageSize = request.getPageSize() != null ? request.getPageSize() : 20;
            
            if (page <= 0) {
                page = 1;
            }
            if (pageSize <= 0 || pageSize > 100) {
                pageSize = 20;
            }
            
            HotelSearchResult result;
            if (request.getLatitude() != null && request.getLongitude() != null) {
                result = searchService.search(request.getQuery().trim(), 
                        request.getLatitude(), request.getLongitude(), page, pageSize);
            } else {
                result = searchService.search(request.getQuery().trim(), page, pageSize);
            }
            
            return ApiResponse.success(result);
            
        } catch (Exception e) {
            log.error("Error in hotel search POST API: request={}", request, e);
            return ApiResponse.error("Internal server error");
        }
    }
    
    /**
     * 请求参数类
     */
    public static class SearchRequest {
        private String query;
        private Integer page;
        private Integer pageSize;
        private Double latitude;
        private Double longitude;
        
        public String getQuery() {
            return query;
        }
        
        public void setQuery(String query) {
            this.query = query;
        }
        
        public Integer getPage() {
            return page;
        }
        
        public void setPage(Integer page) {
            this.page = page;
        }
        
        public Integer getPageSize() {
            return pageSize;
        }
        
        public void setPageSize(Integer pageSize) {
            this.pageSize = pageSize;
        }
        
        public Double getLatitude() {
            return latitude;
        }
        
        public void setLatitude(Double latitude) {
            this.latitude = latitude;
        }
        
        public Double getLongitude() {
            return longitude;
        }
        
        public void setLongitude(Double longitude) {
            this.longitude = longitude;
        }
        
        @Override
        public String toString() {
            return "SearchRequest{query='" + query + "', page=" + page + ", pageSize=" + pageSize + 
                   ", latitude=" + latitude + ", longitude=" + longitude + "}";
        }
    }
} 