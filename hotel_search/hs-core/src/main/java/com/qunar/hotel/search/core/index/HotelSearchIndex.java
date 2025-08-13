package com.qunar.hotel.search.core.index;

import java.io.IOException;
import java.util.*;

import com.qunar.hotel.search.core.normalizer.HotelQueryNormalizer;
import org.apache.commons.lang3.StringUtils;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.*;
import org.apache.lucene.index.*;
import org.apache.lucene.search.*;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.RAMDirectory;

import com.qunar.hotel.search.core.model.HotelSearchResult;
import com.qunar.hotel.search.core.model.HotelInfo;

import lombok.extern.slf4j.Slf4j;

/**
 * @author hotel-search
 * @version 1.0
 * @description Hotel search index for full-text search functionality.
 *
 * 1. 全文搜索索引 使用 Lucene 建立全文搜索索引
 *    索引字段：酒店名(中英)、城市名(中英)、区域名、地址描述
 *
 * 2. 搜索功能 支持模糊搜索、精确匹配、多字段搜索
 *    支持按距离、评分、价格等排序
 *
 * 3. 查询优化 使用 BooleanQuery 组合多个查询条件
 *    支持权重调整和相关性评分
 */
@Slf4j
public class HotelSearchIndex {
    private static final String HOTEL_ID_FIELD = "hotelId";
    private static final String HOTEL_NAME_CN_FIELD = "hotelNameCn";
    private static final String HOTEL_NAME_EN_FIELD = "hotelNameEn";
    private static final String CITY_NAME_CN_FIELD = "cityNameCn";
    private static final String CITY_NAME_EN_FIELD = "cityNameEn";
    private static final String REGION_NAME_FIELD = "regionName";
    private static final String ADDRESS_FIELD = "address";
    private static final String COUNTRY_FIELD = "country";
    private static final String SEARCH_COUNT_FIELD = "searchCount";
    private static final String LATITUDE_FIELD = "latitude";
    private static final String LONGITUDE_FIELD = "longitude";
    
    private final Directory directory;
    private final Analyzer analyzer;
    private final HotelQueryNormalizer queryNormalizer;
    private IndexWriter indexWriter;
    private IndexReader indexReader;
    private IndexSearcher indexSearcher;

    public HotelSearchIndex() throws IOException {
        this.directory = new RAMDirectory();
        this.analyzer = new StandardAnalyzer();
        this.queryNormalizer = new HotelQueryNormalizer();
        initializeIndex();
    }

    private void initializeIndex() throws IOException {
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE);
        this.indexWriter = new IndexWriter(directory, config);
        this.indexReader = DirectoryReader.open(directory);
        this.indexSearcher = new IndexSearcher(indexReader);
    }

    /**
     * 添加酒店信息到索引
     */
    public void addHotel(HotelInfo hotelInfo) throws IOException {
        Document doc = new Document();
        
        // 酒店ID
        doc.add(new StringField(HOTEL_ID_FIELD, hotelInfo.getHotelId(), Field.Store.YES));
        
        // 酒店名称
        doc.add(new TextField(HOTEL_NAME_CN_FIELD, hotelInfo.getHotelNameCn(), Field.Store.YES));
        doc.add(new TextField(HOTEL_NAME_EN_FIELD, hotelInfo.getHotelNameEn(), Field.Store.YES));
        
        // 城市名称
        doc.add(new TextField(CITY_NAME_CN_FIELD, hotelInfo.getCityNameCn(), Field.Store.YES));
        doc.add(new TextField(CITY_NAME_EN_FIELD, hotelInfo.getCityNameEn(), Field.Store.YES));
        
        // 区域名称
        doc.add(new TextField(REGION_NAME_FIELD, hotelInfo.getRegionName(), Field.Store.YES));
        
        // 地址
        doc.add(new TextField(ADDRESS_FIELD, hotelInfo.getAddress(), Field.Store.YES));
        
        // 国家
        doc.add(new StringField(COUNTRY_FIELD, hotelInfo.getCountry(), Field.Store.YES));
        
        // 搜索次数
        doc.add(new LongPoint(SEARCH_COUNT_FIELD, hotelInfo.getSearchCount()));
        doc.add(new StoredField(SEARCH_COUNT_FIELD, hotelInfo.getSearchCount()));
        
        // 经纬度
        if (hotelInfo.getLatitude() != null && hotelInfo.getLongitude() != null) {
            doc.add(new DoublePoint(LATITUDE_FIELD, hotelInfo.getLatitude()));
            doc.add(new DoublePoint(LONGITUDE_FIELD, hotelInfo.getLongitude()));
            doc.add(new StoredField(LATITUDE_FIELD, hotelInfo.getLatitude()));
            doc.add(new StoredField(LONGITUDE_FIELD, hotelInfo.getLongitude()));
        }
        
        indexWriter.addDocument(doc);
        indexWriter.commit();
        
        // 重新打开 reader 和 searcher
        IndexReader newReader = DirectoryReader.openIfChanged((DirectoryReader) indexReader);
        if (newReader != null) {
            indexReader.close();
            indexReader = newReader;
            indexSearcher = new IndexSearcher(indexReader);
        }
    }

    /**
     * 搜索酒店
     */
    public HotelSearchResult search(String query, int page, int pageSize) throws IOException {
        return search(query, null, null, page, pageSize);
    }

    /**
     * 搜索酒店（带地理位置）
     */
    public HotelSearchResult search(String query, Double latitude, Double longitude, 
                                   int page, int pageSize) throws IOException {
        if (StringUtils.isEmpty(query)) {
            return new HotelSearchResult(Collections.emptyList(), 0, page, pageSize);
        }

        // 构建查询
        BooleanQuery.Builder queryBuilder = new BooleanQuery.Builder();
        
        // 归一化查询词
        Set<String> normalizedQueries = queryNormalizer.normalize(query, true);
        
        for (String normalizedQuery : normalizedQueries) {
            // 酒店名称查询
            BooleanQuery.Builder hotelQuery = new BooleanQuery.Builder();
            hotelQuery.add(new FuzzyQuery(new Term(HOTEL_NAME_CN_FIELD, normalizedQuery)), BooleanClause.Occur.SHOULD);
            hotelQuery.add(new FuzzyQuery(new Term(HOTEL_NAME_EN_FIELD, normalizedQuery)), BooleanClause.Occur.SHOULD);
            queryBuilder.add(hotelQuery.build(), BooleanClause.Occur.SHOULD);
            
            // 城市名称查询
            BooleanQuery.Builder cityQuery = new BooleanQuery.Builder();
            cityQuery.add(new FuzzyQuery(new Term(CITY_NAME_CN_FIELD, normalizedQuery)), BooleanClause.Occur.SHOULD);
            cityQuery.add(new FuzzyQuery(new Term(CITY_NAME_EN_FIELD, normalizedQuery)), BooleanClause.Occur.SHOULD);
            queryBuilder.add(cityQuery.build(), BooleanClause.Occur.SHOULD);
            
            // 区域名称查询
            queryBuilder.add(new FuzzyQuery(new Term(REGION_NAME_FIELD, normalizedQuery)), BooleanClause.Occur.SHOULD);
            
            // 地址查询
            queryBuilder.add(new FuzzyQuery(new Term(ADDRESS_FIELD, normalizedQuery)), BooleanClause.Occur.SHOULD);
        }

        // 执行搜索
        int start = (page - 1) * pageSize;
        TopDocs topDocs = indexSearcher.search(queryBuilder.build(), start + pageSize);
        
        // 构建排序
        Sort sort = new Sort();
        if (latitude != null && longitude != null) {
            // 按距离排序
            sort = new Sort(new SortField("_geo_distance", SortField.Type.DOUBLE));
        } else {
            // 按搜索次数和相关性排序
            sort = new Sort(
                new SortField(SEARCH_COUNT_FIELD, SortField.Type.LONG, true),
                SortField.FIELD_SCORE
            );
        }
        
        TopDocs sortedDocs = indexSearcher.search(queryBuilder.build(), start + pageSize, sort);
        
        // 提取结果
        List<HotelInfo> hotels = new ArrayList<>();
        int end = Math.min(start + pageSize, sortedDocs.scoreDocs.length);
        
        for (int i = start; i < end; i++) {
            ScoreDoc scoreDoc = sortedDocs.scoreDocs[i];
            Document doc = indexSearcher.doc(scoreDoc.doc);
            hotels.add(extractHotelInfo(doc, scoreDoc.score));
        }
        
        return new HotelSearchResult(hotels, sortedDocs.totalHits.value, page, pageSize);
    }

    private HotelInfo extractHotelInfo(Document doc, float score) {
        HotelInfo hotelInfo = new HotelInfo();
        hotelInfo.setHotelId(doc.get(HOTEL_ID_FIELD));
        hotelInfo.setHotelNameCn(doc.get(HOTEL_NAME_CN_FIELD));
        hotelInfo.setHotelNameEn(doc.get(HOTEL_NAME_EN_FIELD));
        hotelInfo.setCityNameCn(doc.get(CITY_NAME_CN_FIELD));
        hotelInfo.setCityNameEn(doc.get(CITY_NAME_EN_FIELD));
        hotelInfo.setRegionName(doc.get(REGION_NAME_FIELD));
        hotelInfo.setAddress(doc.get(ADDRESS_FIELD));
        hotelInfo.setCountry(doc.get(COUNTRY_FIELD));
        
        String searchCountStr = doc.get(SEARCH_COUNT_FIELD);
        if (searchCountStr != null) {
            hotelInfo.setSearchCount(Long.parseLong(searchCountStr));
        }
        
        String latitudeStr = doc.get(LATITUDE_FIELD);
        String longitudeStr = doc.get(LONGITUDE_FIELD);
        if (latitudeStr != null && longitudeStr != null) {
            hotelInfo.setLatitude(Double.parseDouble(latitudeStr));
            hotelInfo.setLongitude(Double.parseDouble(longitudeStr));
        }
        
        hotelInfo.setScore(score);
        return hotelInfo;
    }

    /**
     * 关闭索引
     */
    public void close() throws IOException {
        if (indexWriter != null) {
            indexWriter.close();
        }
        if (indexReader != null) {
            indexReader.close();
        }
        if (directory != null) {
            directory.close();
        }
    }
} 