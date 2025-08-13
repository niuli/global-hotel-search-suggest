package com.qunar.hotel.search.core.model;

import lombok.Data;
import java.util.List;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel search result model
 */
@Data
public class HotelSearchResult {
    private List<HotelInfo> hotels;
    private long totalCount;
    private int page;
    private int pageSize;
    private int totalPages;

    public HotelSearchResult(List<HotelInfo> hotels, long totalCount, int page, int pageSize) {
        this.hotels = hotels;
        this.totalCount = totalCount;
        this.page = page;
        this.pageSize = pageSize;
        this.totalPages = (int) Math.ceil((double) totalCount / pageSize);
    }

    public HotelSearchResult() {
    }
} 