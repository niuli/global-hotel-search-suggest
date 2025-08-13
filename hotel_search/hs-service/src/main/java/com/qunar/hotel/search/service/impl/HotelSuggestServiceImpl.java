package com.qunar.hotel.search.service.impl;

import com.qunar.hotel.search.core.index.HotelSuggestIndex;
import com.qunar.hotel.search.core.model.HotelSuggestElem;
import com.qunar.hotel.search.service.service.HotelSuggestService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.List;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel suggest service implementation
 */
@Slf4j
@Service
public class HotelSuggestServiceImpl implements HotelSuggestService {
    
    private final HotelSuggestIndex suggestIndex;
    
    @Autowired
    public HotelSuggestServiceImpl(HotelSuggestIndex suggestIndex) {
        this.suggestIndex = suggestIndex;
    }
    
    @Override
    public List<HotelSuggestElem> suggest(String query, int count) {
        try {
            log.info("Hotel suggest request: query={}, count={}", query, count);
            List<HotelSuggestElem> result = suggestIndex.suggest(query, count);
            log.info("Hotel suggest response: query={}, resultSize={}", query, result.size());
            return result;
        } catch (Exception e) {
            log.error("Error in hotel suggest: query={}", query, e);
            return List.of();
        }
    }
    
    @Override
    public List<HotelSuggestElem> suggest(String query) {
        return suggest(query, 10);
    }
} 