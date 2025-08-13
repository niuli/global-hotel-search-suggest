package com.qunar.hotel.search.core.model;

import lombok.Data;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel suggest element for API response
 */
@Data
public class HotelSuggestElem {
    private String displayName;
    private String hotelName;
    private String cityName;
    private String regionName;
    private String country;
    private String hotelId;

    public HotelSuggestElem(String displayName, String hotelName, String cityName, 
                           String regionName, String country, String hotelId) {
        this.displayName = displayName;
        this.hotelName = hotelName;
        this.cityName = cityName;
        this.regionName = regionName;
        this.country = country;
        this.hotelId = hotelId;
    }

    public HotelSuggestElem() {
    }
} 