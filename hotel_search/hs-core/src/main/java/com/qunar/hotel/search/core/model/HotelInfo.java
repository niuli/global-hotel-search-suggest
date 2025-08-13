package com.qunar.hotel.search.core.model;

import lombok.Data;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel information model
 */
@Data
public class HotelInfo {
    private String hotelId;
    private String hotelNameCn;
    private String hotelNameEn;
    private String cityNameCn;
    private String cityNameEn;
    private String regionName;
    private String address;
    private String country;
    private Long searchCount;
    private Double latitude;
    private Double longitude;
    private Float score;

    public HotelInfo() {
    }

    public HotelInfo(String hotelId, String hotelNameCn, String hotelNameEn, 
                    String cityNameCn, String cityNameEn, String regionName, 
                    String address, String country, Long searchCount, 
                    Double latitude, Double longitude) {
        this.hotelId = hotelId;
        this.hotelNameCn = hotelNameCn;
        this.hotelNameEn = hotelNameEn;
        this.cityNameCn = cityNameCn;
        this.cityNameEn = cityNameEn;
        this.regionName = regionName;
        this.address = address;
        this.country = country;
        this.searchCount = searchCount;
        this.latitude = latitude;
        this.longitude = longitude;
    }
} 