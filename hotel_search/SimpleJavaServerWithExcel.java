import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import java.io.File;
import java.io.FileInputStream;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

/**
 * 使用Excel数据的Java HTTP服务器
 * 提供酒店搜索和建议API
 */
public class SimpleJavaServerWithExcel {
    
    private static final int PORT = 8080;
    private static final String HOST = "0.0.0.0";
    private static final ObjectMapper mapper = new ObjectMapper();
    private static final String EXCEL_FILE_PATH = "../日本东京酒店v2.xlsx";
    
    // 酒店数据
    private static final List<Map<String, Object>> hotels = new ArrayList<>();
    
    static {
        loadHotelsFromExcel();
    }
    
    /**
     * 从Excel文件加载酒店数据
     */
    private static void loadHotelsFromExcel() {
        try {
            System.out.println("正在从Excel文件加载酒店数据: " + EXCEL_FILE_PATH);
            
            File file = new File(EXCEL_FILE_PATH);
            if (!file.exists()) {
                System.err.println("Excel文件不存在: " + EXCEL_FILE_PATH);
                loadSampleData();
                return;
            }
            
            System.out.println("Excel文件存在，大小: " + file.length() + " 字节");
            
            FileInputStream fis = new FileInputStream(file);
            System.out.println("正在打开Excel工作簿...");
            Workbook workbook = new XSSFWorkbook(fis);
            System.out.println("Excel工作簿打开成功，工作表数量: " + workbook.getNumberOfSheets());
            
            Sheet sheet = workbook.getSheetAt(0); // 第一个工作表
            System.out.println("正在读取第一个工作表: " + sheet.getSheetName());
            System.out.println("工作表行数: " + sheet.getPhysicalNumberOfRows());
            
            int rowCount = 0;
            for (Row row : sheet) {
                if (rowCount == 0) {
                    // 跳过标题行
                    rowCount++;
                    continue;
                }
                
                try {
                    Map<String, Object> hotel = new HashMap<>();
                    
                    // 根据Excel列结构读取数据
                    // 假设列结构：ID, 酒店名称, 英文名称, 城市, 英文城市, 区域, 地址, 国家, 搜索次数, 纬度, 经度
                    hotel.put("id", getCellValueAsString(row.getCell(0)));
                    hotel.put("nameCn", getCellValueAsString(row.getCell(1)));
                    hotel.put("nameEn", getCellValueAsString(row.getCell(2)));
                    hotel.put("cityCn", getCellValueAsString(row.getCell(3)));
                    hotel.put("cityEn", getCellValueAsString(row.getCell(4)));
                    hotel.put("region", getCellValueAsString(row.getCell(5)));
                    hotel.put("address", getCellValueAsString(row.getCell(6)));
                    hotel.put("country", getCellValueAsString(row.getCell(7)));
                    
                    // 搜索次数，默认为1000
                    String searchCountStr = getCellValueAsString(row.getCell(8));
                    int searchCount = 1000;
                    if (searchCountStr != null && !searchCountStr.trim().isEmpty()) {
                        try {
                            searchCount = Integer.parseInt(searchCountStr);
                        } catch (NumberFormatException e) {
                            searchCount = 1000;
                        }
                    }
                    hotel.put("searchCount", searchCount);
                    
                    // 经纬度
                    String latStr = getCellValueAsString(row.getCell(9));
                    String lngStr = getCellValueAsString(row.getCell(10));
                    if (latStr != null && !latStr.trim().isEmpty() && lngStr != null && !lngStr.trim().isEmpty()) {
                        try {
                            hotel.put("latitude", Double.parseDouble(latStr));
                            hotel.put("longitude", Double.parseDouble(lngStr));
                        } catch (NumberFormatException e) {
                            hotel.put("latitude", 35.6762);
                            hotel.put("longitude", 139.6503);
                        }
                    } else {
                        hotel.put("latitude", 35.6762);
                        hotel.put("longitude", 139.6503);
                    }
                    
                    // 只添加有基本信息的酒店
                    if (hotel.get("nameCn") != null && !hotel.get("nameCn").toString().trim().isEmpty()) {
                        hotels.add(hotel);
                    }
                    
                } catch (Exception e) {
                    System.err.println("处理第" + (rowCount + 1) + "行数据时出错: " + e.getMessage());
                }
                
                rowCount++;
            }
            
            workbook.close();
            fis.close();
            
            System.out.println("✅ 成功从Excel加载了 " + hotels.size() + " 个酒店数据");
            
        } catch (Exception e) {
            System.err.println("加载Excel文件失败: " + e.getMessage());
            e.printStackTrace();
            loadSampleData();
        }
    }
    
    /**
     * 获取单元格值作为字符串
     */
    private static String getCellValueAsString(Cell cell) {
        if (cell == null) {
            return "";
        }
        
        switch (cell.getCellType()) {
            case STRING:
                return cell.getStringCellValue();
            case NUMERIC:
                if (DateUtil.isCellDateFormatted(cell)) {
                    return cell.getDateCellValue().toString();
                } else {
                    return String.valueOf((long) cell.getNumericCellValue());
                }
            case BOOLEAN:
                return String.valueOf(cell.getBooleanCellValue());
            case FORMULA:
                return cell.getCellFormula();
            default:
                return "";
        }
    }
    
    /**
     * 加载示例数据（备用）
     */
    private static void loadSampleData() {
        System.out.println("使用示例数据...");
        
        Map<String, Object> hotel1 = new HashMap<>();
        hotel1.put("id", "994914");
        hotel1.put("nameCn", "新宿华盛顿酒店");
        hotel1.put("nameEn", "Shinjuku Washington Hotel");
        hotel1.put("cityCn", "东京");
        hotel1.put("cityEn", "Tokyo");
        hotel1.put("region", "新宿地区");
        hotel1.put("searchCount", 1000);
        hotels.add(hotel1);
        
        Map<String, Object> hotel2 = new HashMap<>();
        hotel2.put("id", "994915");
        hotel2.put("nameCn", "利夫马克斯酒店-东京大冢站前店");
        hotel2.put("nameEn", "HOTEL LiVEMAX Tokyo Otsuka-Ekimae");
        hotel2.put("cityCn", "东京");
        hotel2.put("cityEn", "Tokyo");
        hotel2.put("region", "池袋地区");
        hotel2.put("searchCount", 800);
        hotels.add(hotel2);
        
        Map<String, Object> hotel3 = new HashMap<>();
        hotel3.put("id", "994916");
        hotel3.put("nameCn", "东京希尔顿酒店");
        hotel3.put("nameEn", "Hilton Tokyo");
        hotel3.put("cityCn", "东京");
        hotel3.put("cityEn", "Tokyo");
        hotel3.put("region", "新宿地区");
        hotel3.put("searchCount", 1200);
        hotels.add(hotel3);
    }
    
    public static void main(String[] args) throws IOException {
        System.out.println("=== 启动酒店搜索Java服务器（Excel数据版） ===");
        System.out.println("服务器地址: " + HOST + ":" + PORT);
        System.out.println("数据源: " + EXCEL_FILE_PATH);
        System.out.println("加载酒店数量: " + hotels.size());
        System.out.println("API接口:");
        System.out.println("  GET  /api/v1/hotel/suggest?q={查询词}&count={数量}");
        System.out.println("  GET  /api/v1/hotel/search?q={查询词}&page={页码}&pageSize={每页大小}");
        System.out.println("  GET  /api/v1/hotel/stats");
        System.out.println("=====================================");
        
        HttpServer server = HttpServer.create(new InetSocketAddress(HOST, PORT), 0);
        
        // 设置线程池
        ExecutorService executor = Executors.newFixedThreadPool(10);
        server.setExecutor(executor);
        
        // 注册API处理器
        server.createContext("/api/v1/hotel/suggest", new SuggestHandler());
        server.createContext("/api/v1/hotel/search", new SearchHandler());
        server.createContext("/api/v1/hotel/stats", new StatsHandler());
        
        // 启动服务器
        server.start();
        System.out.println("✅ 服务器启动成功！");
        System.out.println("🌐 访问地址: http://localhost:" + PORT);
        System.out.println("📝 测试命令: curl \"http://localhost:" + PORT + "/api/v1/hotel/suggest?q=东京\"");
    }
    
    /**
     * 建议API处理器
     */
    static class SuggestHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"GET".equals(exchange.getRequestMethod())) {
                sendResponse(exchange, 405, "Method Not Allowed");
                return;
            }
            
            try {
                // 解析查询参数
                String query = exchange.getRequestURI().getQuery();
                String searchQuery = "";
                int count = 10;
                
                if (query != null) {
                    String[] params = query.split("&");
                    for (String param : params) {
                        String[] kv = param.split("=");
                        if (kv.length == 2) {
                            if ("q".equals(kv[0])) {
                                searchQuery = java.net.URLDecoder.decode(kv[1], "UTF-8");
                            } else if ("count".equals(kv[0])) {
                                count = Integer.parseInt(kv[1]);
                            }
                        }
                    }
                }
                
                System.out.println("🔍 建议查询: " + searchQuery + ", 数量: " + count);
                
                // 搜索逻辑
                List<Map<String, Object>> results = new ArrayList<>();
                String queryLower = searchQuery.toLowerCase();
                
                for (Map<String, Object> hotel : hotels) {
                    String nameCn = hotel.get("nameCn").toString().toLowerCase();
                    String nameEn = hotel.get("nameEn").toString().toLowerCase();
                    String cityCn = hotel.get("cityCn").toString().toLowerCase();
                    String cityEn = hotel.get("cityEn").toString().toLowerCase();
                    String region = hotel.get("region").toString().toLowerCase();
                    
                    if (nameCn.contains(queryLower) || nameEn.contains(queryLower) ||
                        cityCn.contains(queryLower) || cityEn.contains(queryLower) ||
                        region.contains(queryLower)) {
                        
                        Map<String, Object> result = new HashMap<>(hotel);
                        result.put("score", calculateScore(hotel, queryLower));
                        results.add(result);
                    }
                }
                
                // 按分数排序并限制数量
                results.sort((a, b) -> Double.compare((Double) b.get("score"), (Double) a.get("score")));
                if (results.size() > count) {
                    results = results.subList(0, count);
                }
                
                // 构建响应
                ObjectNode response = mapper.createObjectNode();
                response.put("success", true);
                response.put("query", searchQuery);
                response.put("count", results.size());
                
                ArrayNode resultsArray = mapper.createArrayNode();
                for (Map<String, Object> result : results) {
                    ObjectNode hotelNode = mapper.createObjectNode();
                    hotelNode.put("id", (String) result.get("id"));
                    hotelNode.put("nameCn", (String) result.get("nameCn"));
                    hotelNode.put("nameEn", (String) result.get("nameEn"));
                    hotelNode.put("cityCn", (String) result.get("cityCn"));
                    hotelNode.put("cityEn", (String) result.get("cityEn"));
                    hotelNode.put("region", (String) result.get("region"));
                    hotelNode.put("searchCount", (Integer) result.get("searchCount"));
                    hotelNode.put("score", (Double) result.get("score"));
                    resultsArray.add(hotelNode);
                }
                response.set("results", resultsArray);
                
                sendJsonResponse(exchange, 200, response.toString());
                
            } catch (Exception e) {
                System.err.println("建议查询错误: " + e.getMessage());
                sendResponse(exchange, 500, "Internal Server Error");
            }
        }
    }
    
    /**
     * 搜索API处理器
     */
    static class SearchHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"GET".equals(exchange.getRequestMethod())) {
                sendResponse(exchange, 405, "Method Not Allowed");
                return;
            }
            
            try {
                // 解析查询参数
                String query = exchange.getRequestURI().getQuery();
                String searchQuery = "";
                int page = 1;
                int pageSize = 20;
                
                if (query != null) {
                    String[] params = query.split("&");
                    for (String param : params) {
                        String[] kv = param.split("=");
                        if (kv.length == 2) {
                            if ("q".equals(kv[0])) {
                                searchQuery = java.net.URLDecoder.decode(kv[1], "UTF-8");
                            } else if ("page".equals(kv[0])) {
                                page = Integer.parseInt(kv[1]);
                            } else if ("pageSize".equals(kv[0])) {
                                pageSize = Integer.parseInt(kv[1]);
                            }
                        }
                    }
                }
                
                System.out.println("🔍 搜索查询: " + searchQuery + ", 页码: " + page + ", 每页: " + pageSize);
                
                // 搜索逻辑
                List<Map<String, Object>> allResults = new ArrayList<>();
                String queryLower = searchQuery.toLowerCase();
                
                for (Map<String, Object> hotel : hotels) {
                    String nameCn = hotel.get("nameCn").toString().toLowerCase();
                    String nameEn = hotel.get("nameEn").toString().toLowerCase();
                    String cityCn = hotel.get("cityCn").toString().toLowerCase();
                    String cityEn = hotel.get("cityEn").toString().toLowerCase();
                    String region = hotel.get("region").toString().toLowerCase();
                    
                    if (nameCn.contains(queryLower) || nameEn.contains(queryLower) ||
                        cityCn.contains(queryLower) || cityEn.contains(queryLower) ||
                        region.contains(queryLower)) {
                        
                        Map<String, Object> result = new HashMap<>(hotel);
                        result.put("score", calculateScore(hotel, queryLower));
                        allResults.add(result);
                    }
                }
                
                // 按分数排序
                allResults.sort((a, b) -> Double.compare((Double) b.get("score"), (Double) a.get("score")));
                
                // 分页
                int start = (page - 1) * pageSize;
                int end = Math.min(start + pageSize, allResults.size());
                List<Map<String, Object>> pageResults = allResults.subList(start, end);
                
                // 构建响应
                ObjectNode response = mapper.createObjectNode();
                response.put("success", true);
                response.put("query", searchQuery);
                response.put("page", page);
                response.put("pageSize", pageSize);
                response.put("total", allResults.size());
                response.put("count", pageResults.size());
                
                ArrayNode resultsArray = mapper.createArrayNode();
                for (Map<String, Object> result : pageResults) {
                    ObjectNode hotelNode = mapper.createObjectNode();
                    hotelNode.put("id", (String) result.get("id"));
                    hotelNode.put("nameCn", (String) result.get("nameCn"));
                    hotelNode.put("nameEn", (String) result.get("nameEn"));
                    hotelNode.put("cityCn", (String) result.get("cityCn"));
                    hotelNode.put("cityEn", (String) result.get("cityEn"));
                    hotelNode.put("region", (String) result.get("region"));
                    hotelNode.put("searchCount", (Integer) result.get("searchCount"));
                    hotelNode.put("score", (Double) result.get("score"));
                    resultsArray.add(hotelNode);
                }
                response.set("results", resultsArray);
                
                sendJsonResponse(exchange, 200, response.toString());
                
            } catch (Exception e) {
                System.err.println("搜索查询错误: " + e.getMessage());
                sendResponse(exchange, 500, "Internal Server Error");
            }
        }
    }
    
    /**
     * 统计API处理器
     */
    static class StatsHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"GET".equals(exchange.getRequestMethod())) {
                sendResponse(exchange, 405, "Method Not Allowed");
                return;
            }
            
            try {
                ObjectNode response = mapper.createObjectNode();
                response.put("success", true);
                response.put("totalHotels", hotels.size());
                response.put("serverStatus", "running");
                response.put("port", PORT);
                response.put("host", HOST);
                response.put("dataSource", "Excel: " + EXCEL_FILE_PATH);
                
                sendJsonResponse(exchange, 200, response.toString());
                
            } catch (Exception e) {
                System.err.println("统计查询错误: " + e.getMessage());
                sendResponse(exchange, 500, "Internal Server Error");
            }
        }
    }
    
    /**
     * 计算搜索分数
     */
    private static double calculateScore(Map<String, Object> hotel, String query) {
        double score = 0.0;
        String nameCn = hotel.get("nameCn").toString().toLowerCase();
        String nameEn = hotel.get("nameEn").toString().toLowerCase();
        String cityCn = hotel.get("cityCn").toString().toLowerCase();
        String cityEn = hotel.get("cityEn").toString().toLowerCase();
        String region = hotel.get("region").toString().toLowerCase();
        Integer searchCount = (Integer) hotel.get("searchCount");
        
        // 名称匹配
        if (nameCn.contains(query)) score += 0.8;
        if (nameEn.contains(query)) score += 0.7;
        
        // 城市匹配
        if (cityCn.contains(query)) score += 0.9;
        if (cityEn.contains(query)) score += 0.8;
        
        // 区域匹配
        if (region.contains(query)) score += 0.6;
        
        // 搜索次数权重
        score += (searchCount / 1000.0) * 0.1;
        
        return score;
    }
    
    /**
     * 发送JSON响应
     */
    private static void sendJsonResponse(HttpExchange exchange, int code, String json) throws IOException {
        exchange.getResponseHeaders().add("Content-Type", "application/json; charset=UTF-8");
        exchange.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
        exchange.getResponseHeaders().add("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        exchange.getResponseHeaders().add("Access-Control-Allow-Headers", "Content-Type");
        
        byte[] response = json.getBytes("UTF-8");
        exchange.sendResponseHeaders(code, response.length);
        
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(response);
        }
    }
    
    /**
     * 发送文本响应
     */
    private static void sendResponse(HttpExchange exchange, int code, String message) throws IOException {
        exchange.getResponseHeaders().add("Content-Type", "text/plain; charset=UTF-8");
        exchange.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
        
        byte[] response = message.getBytes("UTF-8");
        exchange.sendResponseHeaders(code, response.length);
        
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(response);
        }
    }
} 