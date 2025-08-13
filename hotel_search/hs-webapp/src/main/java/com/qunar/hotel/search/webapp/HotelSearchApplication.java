package com.qunar.hotel.search.webapp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel Search Application Main Class
 */
@SpringBootApplication
@ComponentScan(basePackages = "com.qunar.hotel.search")
public class HotelSearchApplication {
    
    public static void main(String[] args) {
        System.out.println("Starting Hotel Search Application...");
        SpringApplication.run(HotelSearchApplication.class, args);
        System.out.println("Hotel Search Application started successfully!");
    }
} 