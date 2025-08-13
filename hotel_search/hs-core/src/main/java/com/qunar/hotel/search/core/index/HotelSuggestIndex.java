package com.qunar.hotel.search.core.index;

import java.io.IOException;
import java.util.*;

import com.qunar.hotel.search.core.normalizer.HotelQueryNormalizer;
import org.apache.commons.lang3.StringUtils;
import org.apache.lucene.search.suggest.fst.FSTCompletion;

import com.google.common.base.Predicate;
import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;
import com.qunar.hotel.search.core.utils.StringComputeUtils;
import com.qunar.hotel.search.core.model.HotelSuggestElem;

import lombok.extern.slf4j.Slf4j;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel suggest facade and scoring system, bridge between FST and hotel model.
 *
 * 1. 归一化 建索引和查询时采用相同方式归一化，具体步骤：
 *    去掉停用词，包括：酒店、hotel、旅馆、inn、宾馆、guesthouse、度假村、resort；
 *    转化为连续拼音、拼音首字母，多音字可能有多个结果，要全部召回；
 *
 * 2. 建索引 离线建索引，search_count 取酒店搜索热度值，
 *    线上查询前，全部加载到内存中，定时 reload。
 *    建索引时文本使用：酒店名(中英)、城市名(中英)、区域名
 *
 * 3. 查询 查询时：归一化后查前缀索引，完全匹配的全部召回，然后按打分排序，取 top N；
 *    打分方法：score = log(search_count+1) * 0.2 + edit_distance_score * 0.6 + length_factor + city_boost
 */
@Slf4j
public class HotelSuggestIndex {
    public static final String UNKNOWN_COUNTRY = "UNKNOWN";
    private static final double SEARCH_COUNT_WEIGHT = 0.2;
    private static final double DISTANCE_WEIGHT = 0.6;
    private static final double LENGTH_FACTOR = 2.0;
    private static final double CITY_FACTOR = 2.0;
    private static final double REGION_FACTOR = 1.5;
    private static final double DEFAULT_FACTOR = 1.0;
    private static final double CONTAIN_FACTOR = 10.0;
    private static final int MAX_WORD_LENGTH = 4096;
    
    private final FSTCompletion completion;
    private final HotelQueryNormalizer queryNormalizer;

    /**
     * 构造函数
     *
     * @param completion FST
     */
    public HotelSuggestIndex(FSTCompletion completion) throws IOException {
        this.completion = completion;
        this.queryNormalizer = new HotelQueryNormalizer();
    }

    /**
     * 使用 FST 建立索引计算候选集
     * 使用 log(search_count+1) * X + edit_distance_score * Y 打分
     * 多音字，繁体简体转换，词组长度，城市权重，其他语言及其缩写。
     * 搜索处理时，分精确匹配，前缀匹配，模糊匹配来返回
     *
     * @param input 用户输入
     * @param count 返回词条个数
     */
    public List<HotelSuggestElem> suggest(String input, final int count) {
        input = input.trim();
        if (StringUtils.isEmpty(input) || (input.length() <= 1 && input.charAt(0) < 255)) {
            return Collections.emptyList();
        }
        List<HotelCandidate> candidates = recallEx(input);
        score(candidates, input);
        sort(candidates);
        List<HotelSuggestElem> result = extractEx(candidates, count);
        log.debug("Suggest result for {}: {}", input, result);
        return result;
    }

    private Set<HotelSurface> getSurfaces(String input) {
        Set<HotelSurface> surfaces = new HashSet<>();
        for (String s : queryNormalizer.normalize(input, false)) {
            if (s.length() < 2 && (input.length() >= 2 || input.charAt(0) > 255)) {
                // only recall relative results
                continue;
            }
            for (FSTCompletion.Completion item : completion.lookup(s, Integer.MAX_VALUE)) {
                surfaces.add(new HotelSurface(s, item.utf8.utf8ToString()));
            }
        }
        return surfaces;
    }

    private List<HotelCandidate> extractCandidates(Set<HotelSurface> surfaces) {
        List<HotelCandidate> result = new ArrayList<>(surfaces.size());
        for (HotelSurface surface : surfaces) {
            String[] cols = surface.surface.split("\\|");
            if (cols.length != 8) {
                log.warn("Invalid surface: " + surface);
                continue;
            }
            result.add(new HotelCandidate(surface.query, cols[0], cols[1], cols[2], cols[3], 
                    cols[4], Long.parseLong(cols[5]), Boolean.parseBoolean(cols[6]), cols[7]));
        }
        return result;
    }

    private double computeScore(String candidate, String query) {
        int len = Math.min(candidate.length(), query.length());
        String a = candidate.substring(0, len);
        String b = query.substring(0, len);
        return StringComputeUtils.computeDistanceScore(a, b, true);
    }

    /**
     * 召回
     *
     * @param input 用户输入
     * @return List 召回的酒店候选
     */
    private List<HotelCandidate> recallEx(String input) {
        Set<HotelSurface> surfaces = getSurfaces(input);
        return extractCandidates(surfaces);
    }

    public List<HotelCandidate> filter(List<HotelCandidate> candidateList) {
        return Lists.newArrayList(Iterables.filter(candidateList, new Predicate<HotelCandidate>() {
            @Override
            public boolean apply(HotelCandidate candidate) {
                return !candidate.hotelName.contains("-");
            }
        }));
    }

    /**
     * 使用 FST 建立索引计算候选集
     * 使用 log(search_count+1) * X + edit_distance_score * Y 打分
     * 多音字，繁体简体转换，词组长度，城市权重，其他语言及其缩写。
     * 搜索处理时，分精确匹配，前缀匹配，模糊匹配来返回
     *
     * @param candidates 候选酒店集合
     * @param input      用户输入
     */
    private void score(List<HotelCandidate> candidates, String input) {
        Map<String, Double> distanceScoreCache = new HashMap<>(MAX_WORD_LENGTH);

        for (HotelCandidate candidate : candidates) {
            double searchCountScore = Math.log10(candidate.searchCount + 1);
            String scoreCacheKey = candidate.candidate + "|" + candidate.query;
            double distanceScore;
            if (distanceScoreCache.containsKey(scoreCacheKey)) {
                distanceScore = distanceScoreCache.get(scoreCacheKey);
            } else {
                distanceScore = computeScore(candidate.candidate, candidate.query);
                distanceScoreCache.put(scoreCacheKey, distanceScore);
            }
            double boost = (candidate.hotelName.contains(input) || candidate.cityName.contains(input)) 
                    ? CONTAIN_FACTOR : DEFAULT_FACTOR;

            // city boost
            double isCity = (candidate.isCity ? CITY_FACTOR : DEFAULT_FACTOR);
            // region boost
            double regionBoost = (candidate.regionName.contains(input) ? REGION_FACTOR : DEFAULT_FACTOR);
            
            candidate.score = (searchCountScore * SEARCH_COUNT_WEIGHT + distanceScore * DISTANCE_WEIGHT
                    + LENGTH_FACTOR * 1.0 / candidate.hotelName.length() + CITY_FACTOR * isCity 
                    + regionBoost) * boost;
            
            log.debug("Recalled {} candidate: {} query: {} score {} = {} * ({} * {} + {} * {} + {} * {} + {} * {} + {})",
                    candidate.hotelName, candidate.candidate, candidate.query, candidate.score, boost, searchCountScore,
                    SEARCH_COUNT_WEIGHT, distanceScore, DISTANCE_WEIGHT, 1.0 / candidate.hotelName.length(), LENGTH_FACTOR,
                    CITY_FACTOR, isCity, regionBoost);
        }
    }

    private void sort(List<HotelCandidate> candidates) {
        Collections.sort(candidates, new Comparator<HotelCandidate>() {
            @Override
            public int compare(HotelCandidate o1, HotelCandidate o2) {
                return -Double.compare(o1.score, o2.score);
            }
        });
    }

    private List<HotelSuggestElem> extractEx(List<HotelCandidate> candidates, int count) {
        List<HotelSuggestElem> result = new ArrayList<>();
        List<HotelCandidate> candidateList = filter(candidates);
        HashSet<String> noDupSet = new HashSet<>();
        for (HotelCandidate candidate : candidateList) {
            if (noDupSet.contains(candidate.hotelName)) {
                continue;
            }
            noDupSet.add(candidate.hotelName);
            if (result.size() >= count) {
                break;
            }
            if (result.contains(candidate.hotelName)) {
                continue;
            }

            String display;
            if (StringUtils.equals(candidate.country, UNKNOWN_COUNTRY)) {
                display = candidate.displayName;
            } else {
                display = candidate.displayName + " (" + candidate.country + ")";
            }

            HotelSuggestElem elem = new HotelSuggestElem(display, candidate.hotelName, 
                    candidate.cityName, candidate.regionName, candidate.country, candidate.hotelId);
            result.add(elem);
        }
        return result;
    }
} 