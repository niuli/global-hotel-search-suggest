package com.qunar.hotel.search.core.index;

/**
 * @author hotel-search
 * @version 1.0
 *
 * @description For hotel candidate, this is the data struct for save the hotel suggest,
 *              And the help class for transform query to FST model.
 */
class HotelCandidate {
    final String query;
    final String candidate;
    final String hotelName;
    final String cityName;
    final String regionName;
    final String displayName;
    final long searchCount;
    final boolean isCity;
    final String country;
    final String hotelId;
    double score;

    public HotelCandidate(String query, String candidate, String hotelName, String cityName, 
                         String regionName, String displayName, long searchCount, boolean isCity, String country) {
        this.query = query;
        this.candidate = candidate;
        this.hotelName = hotelName;
        this.cityName = cityName;
        this.regionName = regionName;
        this.displayName = displayName;
        this.searchCount = searchCount;
        this.isCity = isCity;
        this.country = country;
        this.hotelId = ""; // 可以从其他字段生成或单独传入
    }

    public HotelCandidate(String query, String candidate, String hotelName, String cityName, 
                         String regionName, String displayName, long searchCount, boolean isCity, String country, String hotelId) {
        this.query = query;
        this.candidate = candidate;
        this.hotelName = hotelName;
        this.cityName = cityName;
        this.regionName = regionName;
        this.displayName = displayName;
        this.searchCount = searchCount;
        this.isCity = isCity;
        this.country = country;
        this.hotelId = hotelId;
    }
} 