package com.qunar.hotel.search.core.index;

import com.qunar.hotel.search.core.normalizer.HotelQueryNormalizer;

import java.io.IOException;
import java.util.Set;

/**
 * @author hotel-search
 * @version 1.0
 *
 * @description For building hotel suggest index.
 */
public class HotelSuggestIndexBuilder {
    HotelPrefixIndexBuilder prefixIndexBuilder = new HotelPrefixIndexBuilder();
    HotelQueryNormalizer queryNormalizer;
    private final static int CLICK_COUNT_FACTOR = 10000;
    private final static int CLICK_COUNT_DEFAULT = 9;

    public HotelSuggestIndexBuilder() throws IOException {
        this.queryNormalizer = new HotelQueryNormalizer();
    }

    /**
     * For add hotel text into index before build. The value must not be null.
     *
     * @param input  The name of hotel or place.
     * @param hotelName The hotel name.
     * @param cityName The city name.
     * @param regionName The region name.
     * @param searchCount search count.
     * @param display For suggest displaying.
     * @param country The country.
     */
    public void add(String input, String hotelName, String cityName, String regionName, 
                   long searchCount, String display, String country) throws IOException {
        add(input, hotelName, cityName, regionName, searchCount, false, display, country);
    }

    /**
     * For add hotel text into index before build. The value must not be null.
     *
     * @param input  The name of hotel or place.
     * @param hotelName The hotel name.
     * @param cityName The city name.
     * @param regionName The region name.
     * @param searchCount search count.
     * @param isCity boolean.
     * @param display For suggest displaying.
     * @param country The country.
     */
    public void add(String input, String hotelName, String cityName, String regionName,
                   long searchCount, boolean isCity, String display, String country) throws IOException {
        Set<String> candidates = queryNormalizer.normalize(input);
        for (String candidate : candidates) {
            String surface = candidate + "|" + hotelName + "|" + cityName + "|" + regionName + "|" + 
                           searchCount + "|" + isCity + "|" + display + "|" + country;
            int weight = (int) Math.min(searchCount / CLICK_COUNT_FACTOR, CLICK_COUNT_DEFAULT);
            prefixIndexBuilder.add(surface, weight);
        }
    }

    /***
     * builder 模式
     *
     * @return HotelSuggestIndex 对象
     * @throws IOException
     */
    public HotelSuggestIndex build() throws IOException {
        return new HotelSuggestIndex(prefixIndexBuilder.build());
    }
} 