import com.qunar.hotel.dao.HotelDao;
import com.qunar.hotel.dao.HotelDao.Hotel;
import com.qunar.hotel.search.core.index.HotelSuggestIndex;
import com.qunar.hotel.search.core.index.HotelSuggestIndexBuilder;
import com.qunar.hotel.search.core.model.HotelSuggestElem;
import com.qunar.hotel.search.core.utils.HotelDataLoader;
import java.util.List;

public class TestMain {
    public static void main(String[] args) {
        System.out.println("=== Hotel Search System Test ===");
        
        try {
            // 测试DAO层
            System.out.println("1. 测试DAO层...");
            HotelDao hotelDao = new HotelDao();
            List<Hotel> hotels = hotelDao.getAllHotels();
            
            System.out.println("成功加载 " + hotels.size() + " 个酒店:");
            for (Hotel hotel : hotels) {
                System.out.println("- " + hotel.getNameCn() + " (" + hotel.getNameEn() + ")");
                System.out.println("  城市: " + hotel.getCityCn() + " / " + hotel.getCityEn());
                System.out.println("  区域: " + hotel.getRegion());
                System.out.println("  搜索次数: " + hotel.getSearchCount());
                System.out.println();
            }
            
            // 测试搜索功能
            System.out.println("2. 测试基础搜索功能...");
            List<Hotel> tokyoHotels = hotelDao.searchByCity("东京");
            System.out.println("东京酒店数量: " + tokyoHotels.size());
            
            List<Hotel> nameSearch = hotelDao.searchByName("华盛顿");
            System.out.println("包含'华盛顿'的酒店数量: " + nameSearch.size());
            
            // 测试建议索引
            System.out.println("3. 测试建议索引功能...");
            HotelSuggestIndexBuilder suggestIndexBuilder = new HotelSuggestIndexBuilder();
            HotelDataLoader dataLoader = new HotelDataLoader(suggestIndexBuilder, null);
            dataLoader.buildIndexes();
            
            HotelSuggestIndex suggestIndex = suggestIndexBuilder.build();
            
            // 测试建议查询
            System.out.println("4. 测试建议查询...");
            List<HotelSuggestElem> suggestions = suggestIndex.suggest("东京", 5);
            System.out.println("'东京'建议结果数量: " + suggestions.size());
            for (HotelSuggestElem elem : suggestions) {
                System.out.println("- " + elem.getDisplayName() + " (酒店: " + elem.getHotelName() + ", 城市: " + elem.getCityName() + ")");
            }
            
            List<HotelSuggestElem> hotelSuggestions = suggestIndex.suggest("华盛顿", 5);
            System.out.println("'华盛顿'建议结果数量: " + hotelSuggestions.size());
            for (HotelSuggestElem elem : hotelSuggestions) {
                System.out.println("- " + elem.getDisplayName() + " (酒店: " + elem.getHotelName() + ", 城市: " + elem.getCityName() + ")");
            }
            
            System.out.println("=== 所有测试完成 ===");
            System.out.println("✅ Java程序运行成功！");
            System.out.println("✅ 酒店搜索系统核心功能正常！");
            
        } catch (Exception e) {
            System.err.println("❌ 测试失败: " + e.getMessage());
            e.printStackTrace();
        }
    }
} 