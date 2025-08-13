package com.qunar.hotel.search.core.utils;

import org.apache.commons.lang3.StringUtils;

/**
 * @author hotel-search
 * @version 1.0
 * @description String computation utilities for distance and similarity calculation
 */
public class StringComputeUtils {

    /**
     * 计算编辑距离分数
     *
     * @param str1 字符串1
     * @param str2 字符串2
     * @param normalize 是否归一化
     * @return 相似度分数 (0-1)
     */
    public static double computeDistanceScore(String str1, String str2, boolean normalize) {
        if (StringUtils.isEmpty(str1) || StringUtils.isEmpty(str2)) {
            return 0.0;
        }

        int distance = computeLevenshteinDistance(str1, str2);
        int maxLength = Math.max(str1.length(), str2.length());
        
        if (maxLength == 0) {
            return 1.0;
        }

        double similarity = 1.0 - (double) distance / maxLength;
        
        if (normalize) {
            // 应用非线性变换，提高相似度
            similarity = Math.pow(similarity, 0.5);
        }
        
        return similarity;
    }

    /**
     * 计算 Levenshtein 编辑距离
     *
     * @param str1 字符串1
     * @param str2 字符串2
     * @return 编辑距离
     */
    public static int computeLevenshteinDistance(String str1, String str2) {
        int len1 = str1.length();
        int len2 = str2.length();

        // 创建矩阵
        int[][] matrix = new int[len1 + 1][len2 + 1];

        // 初始化第一行和第一列
        for (int i = 0; i <= len1; i++) {
            matrix[i][0] = i;
        }
        for (int j = 0; j <= len2; j++) {
            matrix[0][j] = j;
        }

        // 填充矩阵
        for (int i = 1; i <= len1; i++) {
            for (int j = 1; j <= len2; j++) {
                int cost = (str1.charAt(i - 1) == str2.charAt(j - 1)) ? 0 : 1;
                matrix[i][j] = Math.min(
                    Math.min(matrix[i - 1][j] + 1, matrix[i][j - 1] + 1),
                    matrix[i - 1][j - 1] + cost
                );
            }
        }

        return matrix[len1][len2];
    }

    /**
     * 计算 Jaro-Winkler 相似度
     *
     * @param str1 字符串1
     * @param str2 字符串2
     * @return 相似度分数 (0-1)
     */
    public static double computeJaroWinklerSimilarity(String str1, String str2) {
        if (StringUtils.isEmpty(str1) || StringUtils.isEmpty(str2)) {
            return 0.0;
        }

        if (str1.equals(str2)) {
            return 1.0;
        }

        // 计算 Jaro 相似度
        double jaro = computeJaroSimilarity(str1, str2);
        
        // 计算 Winkler 修正
        int prefixLength = 0;
        int maxPrefixLength = Math.min(4, Math.min(str1.length(), str2.length()));
        
        for (int i = 0; i < maxPrefixLength; i++) {
            if (str1.charAt(i) == str2.charAt(i)) {
                prefixLength++;
            } else {
                break;
            }
        }

        double winkler = jaro + (0.1 * prefixLength * (1.0 - jaro));
        return Math.min(winkler, 1.0);
    }

    /**
     * 计算 Jaro 相似度
     *
     * @param str1 字符串1
     * @param str2 字符串2
     * @return Jaro 相似度分数
     */
    private static double computeJaroSimilarity(String str1, String str2) {
        if (str1.equals(str2)) {
            return 1.0;
        }

        int len1 = str1.length();
        int len2 = str2.length();

        // 匹配窗口大小
        int matchWindow = Math.max(len1, len2) / 2 - 1;
        if (matchWindow < 0) {
            matchWindow = 0;
        }

        // 找到匹配的字符
        boolean[] str1Matches = new boolean[len1];
        boolean[] str2Matches = new boolean[len2];

        int matches = 0;
        int transpositions = 0;

        // 在 str1 中查找 str2 的匹配字符
        for (int i = 0; i < len1; i++) {
            int start = Math.max(0, i - matchWindow);
            int end = Math.min(len2, i + matchWindow + 1);

            for (int j = start; j < end; j++) {
                if (!str2Matches[j] && str1.charAt(i) == str2.charAt(j)) {
                    str1Matches[i] = true;
                    str2Matches[j] = true;
                    matches++;
                    break;
                }
            }
        }

        if (matches == 0) {
            return 0.0;
        }

        // 计算转置
        int k = 0;
        for (int i = 0; i < len1; i++) {
            if (str1Matches[i]) {
                while (!str2Matches[k]) {
                    k++;
                }
                if (str1.charAt(i) != str2.charAt(k)) {
                    transpositions++;
                }
                k++;
            }
        }

        double jaro = (matches / (double) len1 + matches / (double) len2 + 
                      (matches - transpositions / 2.0) / matches) / 3.0;
        
        return jaro;
    }

    /**
     * 计算余弦相似度
     *
     * @param str1 字符串1
     * @param str2 字符串2
     * @return 余弦相似度分数 (0-1)
     */
    public static double computeCosineSimilarity(String str1, String str2) {
        if (StringUtils.isEmpty(str1) || StringUtils.isEmpty(str2)) {
            return 0.0;
        }

        // 字符频率统计
        int[] freq1 = new int[256];
        int[] freq2 = new int[256];

        for (char c : str1.toCharArray()) {
            freq1[c]++;
        }
        for (char c : str2.toCharArray()) {
            freq2[c]++;
        }

        // 计算点积
        double dotProduct = 0.0;
        double norm1 = 0.0;
        double norm2 = 0.0;

        for (int i = 0; i < 256; i++) {
            dotProduct += freq1[i] * freq2[i];
            norm1 += freq1[i] * freq1[i];
            norm2 += freq2[i] * freq2[i];
        }

        if (norm1 == 0.0 || norm2 == 0.0) {
            return 0.0;
        }

        return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
    }
} 