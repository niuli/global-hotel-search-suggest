package com.qunar.hotel.dao;

import lombok.Data;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.ArrayList;

/**
 * Hotel Data Access Object
 * 酒店数据访问对象
 */
@Repository
public class HotelDao {
    
    /**
     * 获取所有酒店数据
     * @return 酒店列表
     */
    public List<Hotel> getAllHotels() {
        // 这里应该从数据库或文件加载数据
        // 目前返回模拟数据
        List<Hotel> hotels = new ArrayList<>();
        
        Hotel hotel1 = new Hotel();
        hotel1.setId("994914");
        hotel1.setNameCn("新宿华盛顿酒店");
        hotel1.setNameEn("Shinjuku Washington Hotel");
        hotel1.setCityCn("东京");
        hotel1.setCityEn("Tokyo");
        hotel1.setRegion("新宿地区");
        hotel1.setSearchCount(1000);
        hotels.add(hotel1);
        
        Hotel hotel2 = new Hotel();
        hotel2.setId("25457196");
        hotel2.setNameCn("利夫马克斯酒店-东京大冢站前店");
        hotel2.setNameEn("HOTEL LiVEMAX Tokyo Otsuka-Ekimae");
        hotel2.setCityCn("东京");
        hotel2.setCityEn("Tokyo");
        hotel2.setRegion("池袋地区");
        hotel2.setSearchCount(800);
        hotels.add(hotel2);
        
        return hotels;
    }
    
    /**
     * 根据城市搜索酒店
     * @param city 城市名
     * @return 酒店列表
     */
    public List<Hotel> searchByCity(String city) {
        List<Hotel> allHotels = getAllHotels();
        List<Hotel> result = new ArrayList<>();
        
        for (Hotel hotel : allHotels) {
            if (hotel.getCityCn().contains(city) || hotel.getCityEn().toLowerCase().contains(city.toLowerCase())) {
                result.add(hotel);
            }
        }
        
        return result;
    }
    
    /**
     * 根据酒店名称搜索
     * @param name 酒店名称
     * @return 酒店列表
     */
    public List<Hotel> searchByName(String name) {
        List<Hotel> allHotels = getAllHotels();
        List<Hotel> result = new ArrayList<>();
        
        for (Hotel hotel : allHotels) {
            if (hotel.getNameCn().contains(name) || hotel.getNameEn().toLowerCase().contains(name.toLowerCase())) {
                result.add(hotel);
            }
        }
        
        return result;
    }
    
    /**
     * 酒店实体类
     */
    @Data
    public static class Hotel {
        private String id;
        private String nameCn;
        private String nameEn;
        private String cityCn;
        private String cityEn;
        private String region;
        private int searchCount;
        private String priceRange;
        private int starRating;
    }
} 