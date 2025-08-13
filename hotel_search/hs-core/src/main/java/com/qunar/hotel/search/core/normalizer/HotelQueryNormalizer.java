package com.qunar.hotel.search.core.normalizer;

import java.util.*;

import org.apache.commons.lang3.StringUtils;

import lombok.extern.slf4j.Slf4j;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel query normalizer for processing search queries
 */
@Slf4j
public class HotelQueryNormalizer {
    
    private static final Set<String> STOP_WORDS = new HashSet<>(Arrays.asList(
        "酒店", "hotel", "旅馆", "inn", "宾馆", "guesthouse", "度假村", "resort",
        "饭店", "restaurant", "住宿", "accommodation", "公寓", "apartment",
        "民宿", "hostel", "青年旅社", "youth hostel", "商务酒店", "business hotel"
    ));

    /**
     * 归一化查询词
     *
     * @param input 输入查询
     * @return 归一化后的查询词集合
     */
    public Set<String> normalize(String input) {
        return normalize(input, true);
    }

    /**
     * 归一化查询词
     *
     * @param input 输入查询
     * @param removeStopWords 是否移除停用词
     * @return 归一化后的查询词集合
     */
    public Set<String> normalize(String input, boolean removeStopWords) {
        Set<String> result = new HashSet<>();
        if (StringUtils.isEmpty(input)) {
            return result;
        }

        // 基本清理
        String cleaned = cleanInput(input);
        
        // 移除停用词
        if (removeStopWords) {
            cleaned = removeStopWords(cleaned);
        }

        if (StringUtils.isNotEmpty(cleaned)) {
            result.add(cleaned);
            
            // 添加拼音变体
            result.addAll(generatePinyinVariants(cleaned));
            
            // 添加英文变体
            result.addAll(generateEnglishVariants(cleaned));
        }

        return result;
    }

    /**
     * 清理输入
     */
    private String cleanInput(String input) {
        return input.trim()
                .toLowerCase()
                .replaceAll("[\\s\\-_]+", "")
                .replaceAll("[^a-zA-Z0-9\\u4e00-\\u9fa5]", "");
    }

    /**
     * 移除停用词
     */
    private String removeStopWords(String input) {
        String result = input;
        for (String stopWord : STOP_WORDS) {
            result = result.replace(stopWord, "");
        }
        return result.trim();
    }

    /**
     * 生成拼音变体
     */
    private Set<String> generatePinyinVariants(String input) {
        Set<String> variants = new HashSet<>();
        
        // 这里可以集成拼音转换库，如 pinyin4j
        // 暂时返回空集合，后续可以扩展
        if (containsChinese(input)) {
            // 简单的拼音首字母提取
            String pinyin = extractPinyinInitials(input);
            if (StringUtils.isNotEmpty(pinyin)) {
                variants.add(pinyin);
            }
        }
        
        return variants;
    }

    /**
     * 生成英文变体
     */
    private Set<String> generateEnglishVariants(String input) {
        Set<String> variants = new HashSet<>();
        
        if (containsEnglish(input)) {
            // 添加小写变体
            variants.add(input.toLowerCase());
            
            // 添加首字母大写变体
            if (input.length() > 0) {
                variants.add(input.substring(0, 1).toUpperCase() + input.substring(1).toLowerCase());
            }
        }
        
        return variants;
    }

    /**
     * 检查是否包含中文字符
     */
    private boolean containsChinese(String input) {
        return input.matches(".*[\\u4e00-\\u9fa5].*");
    }

    /**
     * 检查是否包含英文字符
     */
    private boolean containsEnglish(String input) {
        return input.matches(".*[a-zA-Z].*");
    }

    /**
     * 提取拼音首字母（简化实现）
     */
    private String extractPinyinInitials(String input) {
        // 这里是一个简化的实现，实际项目中应该使用专业的拼音转换库
        // 例如：北京 -> bj, 上海 -> sh
        Map<String, String> commonPinyin = new HashMap<>();
        commonPinyin.put("北京", "bj");
        commonPinyin.put("上海", "sh");
        commonPinyin.put("广州", "gz");
        commonPinyin.put("深圳", "sz");
        commonPinyin.put("杭州", "hz");
        commonPinyin.put("南京", "nj");
        commonPinyin.put("成都", "cd");
        commonPinyin.put("武汉", "wh");
        commonPinyin.put("西安", "xa");
        commonPinyin.put("重庆", "cq");
        commonPinyin.put("天津", "tj");
        commonPinyin.put("苏州", "sz");
        commonPinyin.put("厦门", "xm");
        commonPinyin.put("长沙", "cs");
        commonPinyin.put("青岛", "qd");
        commonPinyin.put("大连", "dl");
        commonPinyin.put("宁波", "nb");
        commonPinyin.put("无锡", "wx");
        commonPinyin.put("佛山", "fs");
        commonPinyin.put("东莞", "dg");
        commonPinyin.put("郑州", "zz");
        commonPinyin.put("济南", "jn");
        commonPinyin.put("福州", "fz");
        commonPinyin.put("合肥", "hf");
        commonPinyin.put("昆明", "km");
        commonPinyin.put("哈尔滨", "heb");
        commonPinyin.put("沈阳", "sy");
        commonPinyin.put("长春", "cc");
        commonPinyin.put("石家庄", "sjz");
        commonPinyin.put("太原", "ty");
        commonPinyin.put("南昌", "nc");
        commonPinyin.put("南宁", "nn");
        commonPinyin.put("贵阳", "gy");
        commonPinyin.put("兰州", "lz");
        commonPinyin.put("银川", "yc");
        commonPinyin.put("西宁", "xn");
        commonPinyin.put("乌鲁木齐", "wlmq");
        commonPinyin.put("拉萨", "ls");
        commonPinyin.put("海口", "hk");
        commonPinyin.put("三亚", "sy");
        commonPinyin.put("台北", "tb");
        commonPinyin.put("香港", "hk");
        commonPinyin.put("澳门", "am");
        commonPinyin.put("东京", "dj");
        commonPinyin.put("大阪", "os");
        commonPinyin.put("京都", "jd");
        commonPinyin.put("横滨", "hb");
        commonPinyin.put("名古屋", "mgy");
        commonPinyin.put("神户", "sb");
        commonPinyin.put("福冈", "fk");
        commonPinyin.put("札幌", "zl");
        commonPinyin.put("仙台", "xt");
        commonPinyin.put("广岛", "hd");
        commonPinyin.put("新宿", "xs");
        commonPinyin.put("涩谷", "sg");
        commonPinyin.put("池袋", "cd");
        commonPinyin.put("秋叶原", "qyy");
        commonPinyin.put("浅草", "qc");
        commonPinyin.put("上野", "sy");
        commonPinyin.put("银座", "yz");
        commonPinyin.put("筑地", "zd");
        commonPinyin.put("品川", "pc");
        commonPinyin.put("日本桥", "rbq");
        commonPinyin.put("日暮里", "rml");
        
        return commonPinyin.getOrDefault(input, "");
    }
} 