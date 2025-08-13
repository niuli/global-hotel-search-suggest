package com.qunar.hotel.search.service.impl;

import com.qunar.hotel.search.core.index.HotelSearchIndex;
import com.qunar.hotel.search.core.model.HotelSearchResult;
import com.qunar.hotel.search.service.service.HotelSearchService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.IOException;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel search service implementation
 */
@Slf4j
@Service
public class HotelSearchServiceImpl implements HotelSearchService {
    
    private final HotelSearchIndex searchIndex;
    
    @Autowired
    public HotelSearchServiceImpl(HotelSearchIndex searchIndex) {
        this.searchIndex = searchIndex;
    }
    
    @Override
    public HotelSearchResult search(String query, int page, int pageSize) {
        try {
            log.info("Hotel search request: query={}, page={}, pageSize={}", query, page, pageSize);
            HotelSearchResult result = searchIndex.search(query, page, pageSize);
            log.info("Hotel search response: query={}, totalCount={}, resultSize={}", 
                    query, result.getTotalCount(), result.getHotels().size());
            return result;
        } catch (IOException e) {
            log.error("Error in hotel search: query={}", query, e);
            return new HotelSearchResult();
        }
    }
    
    @Override
    public HotelSearchResult search(String query, Double latitude, Double longitude, int page, int pageSize) {
        try {
            log.info("Hotel search request: query={}, lat={}, lng={}, page={}, pageSize={}", 
                    query, latitude, longitude, page, pageSize);
            HotelSearchResult result = searchIndex.search(query, latitude, longitude, page, pageSize);
            log.info("Hotel search response: query={}, totalCount={}, resultSize={}", 
                    query, result.getTotalCount(), result.getHotels().size());
            return result;
        } catch (IOException e) {
            log.error("Error in hotel search: query={}, lat={}, lng={}", query, latitude, longitude, e);
            return new HotelSearchResult();
        }
    }
    
    @Override
    public HotelSearchResult search(String query) {
        return search(query, 1, 20);
    }
} 