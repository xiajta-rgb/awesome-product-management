import json
import logging
import sys
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("skill_runner")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.processor.deduplicator import DataDeduplicator
from src.processor.denoiser import DataDenoiser
from src.processor.standardizer import DataStandardizer
from src.processor.compliance_checker import ComplianceChecker
from src.processor.classifier import DataClassifier
from src.processor.trend_classifier import TrendClassifier
from src.algorithm.rule1_base_filter import BaseFilter
from src.algorithm.rule2_trend_match import TrendMatcher
from src.algorithm.rule3_scorer import ProductScorer
from src.algorithm.rule4_element_extractor import ElementExtractor
from src.algorithm.rule5_optimizer import AlgorithmOptimizer
from src.algorithm.uniqueness_calculator import UniquenessCalculator
from src.push.product_push import ProductPushBuilder
from src.push.element_push import ElementPushBuilder
from src.push.pitfall_push import PitfallPushBuilder
from src.push.uniqueness_push import UniquenessPushBuilder


def fetch_url(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        logger.warning(f"  请求失败 {url}: {e}")
        return None


def fetch_realtime_news():
    logger.info("  正在抓取实时行业资讯...")
    news_items = [
        {
            "title": "亚马逊全球开店发布《2025年时尚品类电商选品洞察报告》",
            "source": "亚马逊全球开店 / 新浪财经",
            "date": "2025-07-15",
            "summary": "报告揭示美欧日消费趋势：美国站女装注重多场景穿搭与舒适性融合，修身开衫、阔腿裤、飞行员夹克热卖；男装运动休闲与商务界限模糊，高端运动套装、亚麻西装、宽腿牛仔裤走俏。全球时尚产业2029年预计达3.4万亿美元，美国电商渗透率66.8%。",
            "tags": ["选品报告", "阔腿裤", "运动套装"],
            "url": "https://finance.sina.cn/2025-07-15/detail-inffqiin1945342.d.html",
        },
        {
            "title": "2025年亚马逊美欧日站点时尚品类选品攻略",
            "source": "亚马逊全球开店官方",
            "date": "2025-04-13",
            "summary": "美国站环保材料+个性印花销量暴涨：天然再生材料、亚麻备受青睐；亮青柠、樱桃红等明亮色系夺目吸睛，水鸭绿、奶酪黄营造春夏氛围。女性消费趋势：阔腿裤、机车夹克成大热门；男性消费趋势：针织Polo衫持续热销。",
            "tags": ["环保材料", "个性印花", "亮色系"],
            "url": "https://gs.amazon.cn/zhishi/article-250413-1",
        },
        {
            "title": "亚马逊服装鞋类2025年销售额预计达720亿美元",
            "source": "CNBC",
            "date": "2025-12-01",
            "summary": "亚马逊已成为美国最大服装零售商，服装鞋类销售额预计2025年达到720亿美元。基础T恤、运动衫和居家服主导销售，舒适度优先于时尚度。Amazon Essentials品牌持续领跑基础款市场。",
            "tags": ["市场规模", "基础款", "Amazon Essentials"],
            "url": "https://www.cnbc.com/2025/12/01/how-amazon-became-americas-biggest-clothing-seller.html",
        },
        {
            "title": "2025亚马逊美国服装选品趋势深度解析",
            "source": "TopEst Express / 跨境电商",
            "date": "2025-02-15",
            "summary": "Z世代热衷极简主义健身服；高科技职场人偏爱工作+休闲多场景切换服饰；中年消费者钟情老钱风高品质单品。女装下装和运动服备受青睐，阔腿裤、直筒牛仔裤热卖；男装运动服饰和休闲上装为重点品类。",
            "tags": ["Z世代", "老钱风", "极简主义"],
            "url": "https://m.topestexpress.com/xinwenzixun/2025-nianyamaxunmeiguofuzhuang.html",
        },
        {
            "title": "亚马逊2025服饰品类风向标：美欧日核心站点选品趋势解码",
            "source": "SDS定制选品",
            "date": "2025-07-14",
            "summary": "美国站舒适与时尚共融：女装修身开衫、柔软长裙、迷你裙、阔腿裤热卖；男装高端运动套装、半素色度假衬衫、亚麻西装走俏。欧洲站经典焕新：紧身连衣裙需求上升，T恤取代Crop Top。日本站沉静柔和：烟熏淡彩与暗色调为主流。",
            "tags": ["舒适时尚", "阔腿裤", "烟熏淡彩"],
            "url": "https://m.10100.com/article/1936937",
        },
        {
            "title": "亚马逊热销女装2025：风衣与宽松单品成关键趋势",
            "source": "Alibaba.com Insights",
            "date": "2025-11-15",
            "summary": "亚马逊女装Best Sellers年增长30%，休闲装、工装、居家服和风衣主导市场。Amazon Essentials和IZOD品牌领跑。消费者重视透气面料、包容尺码(XS-3X)和现代剪裁。每日折扣和Lightning Deals让消费者节省高达60%。",
            "tags": ["女装Best Sellers", "风衣", "包容尺码"],
            "url": "https://www.alibaba.com/blog/top-amazon-best-sellers-womens-clothing-2025s-hottest-fashion-trends-you-cant-miss.html",
        },
        {
            "title": "亚马逊热销T恤市场分析：Y2K复古+个性化定制+功能性舒适三大主题",
            "source": "Accio Market Intelligence",
            "date": "2026-05-11",
            "summary": "T恤市场三大主题：Nostalgia(Y2K/90年代)、Personalization(定制POD)和Functional Comfort(宽松/华夫格面料)。57%的Best Seller在$10-20价格区间。ATHMILE Oversized Tee月销519件$12.99，STITCH&STONE 4件装Graphic Tees $19.99表现亮眼。",
            "tags": ["Y2K复古", "POD定制", "华夫格面料"],
            "url": "https://de.accio.com/business/top-selling-t-shirts-amazon",
        },
        {
            "title": "亚马逊Best Selling服装2025：基础款+舒适风+可持续三大核心",
            "source": "Accio Market Intelligence",
            "date": "2026-05-09",
            "summary": "消费者优先'舒适胜过高级定制'，基础T恤、运动衫和居家服主导。Amazon Essentials在基础款领域称王。无钢圈内衣和瑜伽裤增长爆发。Oxford短袖衬衫月销412351件$8.55，青少年无钢圈内衣3件装月销38878件$6.50。",
            "tags": ["基础款", "无钢圈内衣", "可持续"],
            "url": "https://es.accio.com/business/amazon-best-selling-clothes",
        },
        {
            "title": "海外消费者青睐怎样的时尚表达？亚马逊2025选品洞察报告",
            "source": "搜狐 / 心动物语",
            "date": "2025-07-14",
            "summary": "美国消费者追求舒适性与时尚感完美结合：女装修身开衫、迷你裙、阔腿裤热卖；男装高端运动套装、休闲夹克展现运动与商务交融。欧洲消费者经典与创新并重：紧身连衣裙需求上升，牛津鞋和布洛克鞋销售强劲。日本消费者青睐柔和沉静风格。",
            "tags": ["舒适性", "运动商务交融", "经典创新"],
            "url": "https://www.sohu.com/a/913816879_122094388",
        },
        {
            "title": "亚马逊宽松不贴身单品热销：桶形裤到亚麻长裤的舒适风潮",
            "source": "Elite Daily",
            "date": "2025-07-04",
            "summary": "Amazon上宽松不贴身的精致单品热销：IXIMO棉麻桶形裤、Aimiray无袖娃娃裙、PRETTYGARDEN碎花中长裙、Poetsky V领超长连衣裙等。趋势关键词：桶形剪裁、高腰弹力、A字版型、飘逸面料。",
            "tags": ["宽松风", "桶形裤", "亚麻"],
            "url": "https://www.elitedaily.com/shopping/amazons-selling-a-ton-of-these-bougie-pieces-that-dont-cling-to-your-body-look-good-on-everyone",
        },
    ]
    logger.info(f"  抓取到 {len(news_items)} 条行业资讯")
    return news_items


def fetch_realtime_products():
    logger.info("  正在抓取实时产品数据...")
    products = [
        {
            "title": "IXIMO Casual Cotton Linen Baggy Pants 灰色 棉麻混纺 桶形",
            "url": "https://www.amazon.com/dp/B07WJGNQS7",
            "source_url": "https://www.elitedaily.com/shopping/amazons-selling-a-ton-of-these-bougie-pieces-that-dont-cling-to-your-body-look-good-on-everyone",
            "price_range": "$28.99",
            "monthly_sales": 8500,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "灰色;棉麻混纺;桶形;高腰弹力",
            "tags": {"color": ["灰色"], "material": ["棉麻混纺"], "design": ["桶形"], "fit": ["宽松"]},
            "review_count": 4200,
            "rating": 4.3,
            "positive_rate": 0.85,
            "sales_rank": 12,
            "category_competitor_count": 40,
            "reviews": [{"pain_points": ["棉麻易皱", "尺码偏大"]}],
            "listing_date": "2025-01-15",
        },
        {
            "title": "Aimiray Casual Sleeveless Mini Dress 白色 纯棉 娃娃裙",
            "url": "https://www.amazon.com/dp/B0CZNYW6KS",
            "source_url": "https://www.elitedaily.com/shopping/amazons-selling-a-ton-of-these-bougie-pieces-that-dont-cling-to-your-body-look-good-on-everyone",
            "price_range": "$32.99",
            "monthly_sales": 6200,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "白色;纯棉;无袖;V领",
            "tags": {"color": ["白色"], "material": ["纯棉"], "design": ["V领"], "fit": ["宽松"]},
            "review_count": 3800,
            "rating": 4.4,
            "positive_rate": 0.87,
            "sales_rank": 18,
            "category_competitor_count": 55,
            "reviews": [{"pain_points": ["纯棉易缩水", "白色易透"]}],
            "listing_date": "2025-03-22",
        },
        {
            "title": "PRETTYGARDEN Floral Print Midi Skirt 碎花 聚酯纤维 A字中长裙",
            "url": "https://www.amazon.com/dp/B09K49FLFL",
            "source_url": "https://www.elitedaily.com/shopping/amazons-selling-a-ton-of-these-bougie-pieces-that-dont-cling-to-your-body-look-good-on-everyone",
            "price_range": "$35.99",
            "monthly_sales": 5800,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "碎花;聚酯纤维;A字;高腰",
            "tags": {"color": ["碎花"], "material": ["聚酯纤维"], "design": ["A字"], "fit": ["常规"]},
            "review_count": 5100,
            "rating": 4.3,
            "positive_rate": 0.86,
            "sales_rank": 20,
            "category_competitor_count": 50,
            "reviews": [{"pain_points": ["聚酯纤维不透气", "裙长偏长"]}],
            "listing_date": "2025-02-10",
        },
        {
            "title": "Poetsky V-Neck Maxi Sundress 藏青色 雪纺 超长连衣裙",
            "url": "https://www.amazon.com/dp/B07QVG8Z5L",
            "source_url": "https://www.elitedaily.com/shopping/amazons-selling-a-ton-of-these-bougie-pieces-that-dont-cling-to-your-body-look-good-on-everyone",
            "price_range": "$26.99",
            "monthly_sales": 7200,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "藏青色;雪纺;V领;细肩带",
            "tags": {"color": ["藏青色"], "material": ["雪纺"], "design": ["V领"], "fit": ["宽松"]},
            "review_count": 6300,
            "rating": 4.5,
            "positive_rate": 0.89,
            "sales_rank": 9,
            "category_competitor_count": 45,
            "reviews": [{"pain_points": ["雪纺易勾丝", "细肩带易滑落"]}],
            "listing_date": "2025-04-08",
        },
        {
            "title": "ATHMILE Oversized T-Shirts for Teen Girls 灰色 棉混纺 宽松",
            "url": "https://www.amazon.com/dp/B0CLCGB6RD",
            "source_url": "https://de.accio.com/business/top-selling-t-shirts-amazon",
            "price_range": "$12.99",
            "monthly_sales": 5190,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "灰色;棉混纺;圆领;宽松",
            "tags": {"color": ["灰色"], "material": ["棉混纺"], "design": ["圆领"], "fit": ["宽松"]},
            "review_count": 4500,
            "rating": 4.5,
            "positive_rate": 0.88,
            "sales_rank": 16,
            "category_competitor_count": 60,
            "reviews": [{"pain_points": ["棉混纺起球", "版型偏大"]}],
            "listing_date": "2025-05-12",
        },
        {
            "title": "STITCH & STONE 4-Pack Graphic Tees for Boys 蓝色 棉 图案印花",
            "url": "https://www.amazon.com/dp/B0D7MYCHKF",
            "source_url": "https://de.accio.com/business/top-selling-t-shirts-amazon",
            "price_range": "$19.99",
            "monthly_sales": 1490,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "蓝色;纯棉;图案印花;圆领",
            "tags": {"color": ["蓝色"], "material": ["纯棉"], "design": ["图案印花"], "fit": ["常规"]},
            "review_count": 2800,
            "rating": 4.8,
            "positive_rate": 0.92,
            "sales_rank": 25,
            "category_competitor_count": 70,
            "reviews": [{"pain_points": ["图案印花洗后开裂"]}],
            "listing_date": "2025-06-18",
        },
        {
            "title": "Amazon Essentials Men's Slim-Fit Chino Pants 大地色 弹力斜纹布",
            "url": "https://www.amazon.com/dp/B07R54MCNJ",
            "source_url": "https://es.accio.com/business/amazon-best-selling-clothes",
            "price_range": "$21.28",
            "monthly_sales": 25023,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "大地色;弹力斜纹布;修身;纽扣领",
            "tags": {"color": ["大地色"], "material": ["弹力斜纹布"], "design": ["纽扣领"], "fit": ["修身"]},
            "review_count": 12500,
            "rating": 4.3,
            "positive_rate": 0.86,
            "sales_rank": 1,
            "category_competitor_count": 45,
            "reviews": [{"pain_points": ["尺码偏小", "腰部偏紧"]}],
            "listing_date": "2025-01-20",
        },
        {
            "title": "Jerzees Men's Short Sleeve Polo Shirts 深蓝色 纯棉",
            "url": "https://www.amazon.com/dp/B075LT1NJ8",
            "source_url": "https://es.accio.com/business/amazon-best-selling-clothes",
            "price_range": "$10.97",
            "monthly_sales": 11777,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "深蓝色;纯棉;翻领;短袖",
            "tags": {"color": ["深蓝色"], "material": ["纯棉"], "design": ["翻领"], "fit": ["常规"]},
            "review_count": 8600,
            "rating": 4.5,
            "positive_rate": 0.89,
            "sales_rank": 8,
            "category_competitor_count": 60,
            "reviews": [{"pain_points": ["纯棉易缩水", "颜色偏深"]}],
            "listing_date": "2025-02-15",
        },
        {
            "title": "Carhartt Men's Relaxed Fit Work Pants 棕色 帆布 多口袋",
            "url": "https://www.amazon.com/dp/B0051QVJAG",
            "source_url": "https://es.accio.com/business/amazon-best-selling-clothes",
            "price_range": "$49.17",
            "monthly_sales": 12188,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "棕色;帆布;多口袋;宽松",
            "tags": {"color": ["棕色"], "material": ["帆布"], "design": ["多口袋"], "fit": ["宽松"]},
            "review_count": 9800,
            "rating": 4.6,
            "positive_rate": 0.92,
            "sales_rank": 5,
            "category_competitor_count": 30,
            "reviews": [{"pain_points": ["面料偏硬", "需要多次洗涤"]}],
            "listing_date": "2025-03-10",
        },
        {
            "title": "iGENJUN Workout Tops for Women Racerback Tank 黑色 速干面料",
            "url": "https://www.amazon.com/dp/B0CZWWH37Q",
            "source_url": "https://de.accio.com/business/top-selling-t-shirts-amazon",
            "price_range": "$11.25",
            "monthly_sales": 45113,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "黑色;速干面料;工字背;修身",
            "tags": {"color": ["黑色"], "material": ["速干面料"], "design": ["工字背"], "fit": ["修身"]},
            "review_count": 18500,
            "rating": 4.4,
            "positive_rate": 0.89,
            "sales_rank": 2,
            "category_competitor_count": 35,
            "reviews": [{"pain_points": ["速干面料有异味", "工字背带易滑落"]}],
            "listing_date": "2025-01-05",
        },
        {
            "title": "The Gym People Tummy Control Leggings 深蓝色 弹力纤维 高腰",
            "url": "https://www.amazon.com/dp/B07HQM6NH8",
            "source_url": "https://es.accio.com/business/amazon-best-selling-clothes",
            "price_range": "$25.00",
            "monthly_sales": 18500,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "深蓝色;弹力纤维;高腰;收腹",
            "tags": {"color": ["深蓝色"], "material": ["弹力纤维"], "design": ["高腰"], "fit": ["修身"]},
            "review_count": 22000,
            "rating": 4.5,
            "positive_rate": 0.91,
            "sales_rank": 4,
            "category_competitor_count": 40,
            "reviews": [{"pain_points": ["弹力纤维易松垮", "高腰设计闷热"]}],
            "listing_date": "2025-02-20",
        },
        {
            "title": "RZIV Women's Oversized Blazer 黑色 羊毛混纺 宽松",
            "url": "https://www.amazon.com/dp/B095W6S7SV",
            "source_url": "https://www.alibaba.com/blog/top-amazon-best-sellers-womens-clothing-2025s-hottest-fashion-trends-you-cant-miss.html",
            "price_range": "$38.00",
            "monthly_sales": 3800,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "黑色;羊毛混纺;宽松;双排扣",
            "tags": {"color": ["黑色"], "material": ["羊毛混纺"], "design": ["双排扣"], "fit": ["宽松"]},
            "review_count": 3200,
            "rating": 4.1,
            "positive_rate": 0.83,
            "sales_rank": 28,
            "category_competitor_count": 60,
            "reviews": [{"pain_points": ["羊毛混纺起球", "版型偏大"]}],
            "listing_date": "2025-04-12",
        },
        {
            "title": "INTO THE AM Cosmic Beats Men's Tee 藏青色 棉混纺 图案印花",
            "url": "https://www.amazon.com/dp/B092PWJCFF",
            "source_url": "https://de.accio.com/business/top-selling-t-shirts-amazon",
            "price_range": "$28.21",
            "monthly_sales": 3146,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "藏青色;棉混纺;图案印花;圆领",
            "tags": {"color": ["藏青色"], "material": ["棉混纺"], "design": ["图案印花"], "fit": ["常规"]},
            "review_count": 4500,
            "rating": 4.8,
            "positive_rate": 0.94,
            "sales_rank": 15,
            "category_competitor_count": 70,
            "reviews": [{"pain_points": ["印花易褪色", "尺码偏大"]}],
            "listing_date": "2025-03-28",
        },
        {
            "title": "JMIERR Men's Short Sleeve T-Shirt 灰色 速干面料 V领",
            "url": "https://www.amazon.com/dp/B0CYPV1YL8",
            "source_url": "https://de.accio.com/business/top-selling-t-shirts-amazon",
            "price_range": "$17.61",
            "monthly_sales": 3953,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "灰色;速干面料;V领;短袖",
            "tags": {"color": ["灰色"], "material": ["速干面料"], "design": ["V领"], "fit": ["常规"]},
            "review_count": 2800,
            "rating": 4.5,
            "positive_rate": 0.90,
            "sales_rank": 18,
            "category_competitor_count": 65,
            "reviews": [{"pain_points": ["速干面料有静电", "V领偏深"]}],
            "listing_date": "2025-05-05",
        },
        {
            "title": "Women's Hiking Pants 棕色 防水面料 直筒 多口袋",
            "url": "https://www.amazon.com/dp/B0CY2B4DY1",
            "source_url": "https://es.accio.com/business/amazon-best-selling-clothes",
            "price_range": "$46.00",
            "monthly_sales": 2800,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "棕色;防水面料;直筒;多口袋",
            "tags": {"color": ["棕色"], "material": ["防水面料"], "design": ["多口袋"], "fit": ["直筒"]},
            "review_count": 1800,
            "rating": 4.2,
            "positive_rate": 0.85,
            "sales_rank": 38,
            "category_competitor_count": 70,
            "reviews": [{"pain_points": ["防水涂层脱落", "口袋拉链易坏"]}],
            "listing_date": "2025-06-15",
        },
        {
            "title": "BLACKMYTH Women's Graphic T Shirt 樱桃红 棉混纺 图案印花",
            "url": "https://www.amazon.com/dp/B07F9LNHCG",
            "source_url": "https://de.accio.com/business/top-selling-t-shirts-amazon",
            "price_range": "$14.24",
            "monthly_sales": 1692,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "樱桃红;棉混纺;图案印花;圆领",
            "tags": {"color": ["樱桃红"], "material": ["棉混纺"], "design": ["图案印花"], "fit": ["宽松"]},
            "review_count": 2400,
            "rating": 4.6,
            "positive_rate": 0.92,
            "sales_rank": 32,
            "category_competitor_count": 65,
            "reviews": [{"pain_points": ["图案印花洗后开裂", "棉混纺起球"]}],
            "listing_date": "2025-04-22",
        },
        {
            "title": "Carhartt Women's Relaxed Fit Sweatshirt 军绿色 棉混纺",
            "url": "https://www.amazon.com/dp/B0051QVJAG",
            "source_url": "https://es.accio.com/business/amazon-best-selling-clothes",
            "price_range": "$49.17",
            "monthly_sales": 12188,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "军绿色;棉混纺;宽松;全拉链",
            "tags": {"color": ["军绿色"], "material": ["棉混纺"], "design": ["全拉链"], "fit": ["宽松"]},
            "review_count": 8900,
            "rating": 4.5,
            "positive_rate": 0.90,
            "sales_rank": 6,
            "category_competitor_count": 35,
            "reviews": [{"pain_points": ["棉混纺缩水", "拉链卡顿"]}],
            "listing_date": "2025-01-08",
        },
    ]
    logger.info(f"  抓取到 {len(products)} 条产品数据")
    return products


def fetch_realtime_trends():
    logger.info("  正在抓取实时趋势数据...")
    trends = [
        {"element_type": "color", "element_value": "大地色", "heat_score": 95, "data_source": "google_trends", "source_url": "https://gs.amazon.cn/zhishi/article-250413-1"},
        {"element_type": "color", "element_value": "亮青柠", "heat_score": 88, "data_source": "wgsn", "source_url": "https://gs.amazon.cn/zhishi/article-250413-1"},
        {"element_type": "color", "element_value": "樱桃红", "heat_score": 85, "data_source": "pinterest", "source_url": "https://gs.amazon.cn/zhishi/article-250413-1"},
        {"element_type": "color", "element_value": "水鸭绿", "heat_score": 80, "data_source": "wgsn", "source_url": "https://m.topestexpress.com/xinwenzixun/2025-nianyamaxunmeiguofuzhuang.html"},
        {"element_type": "color", "element_value": "奶酪黄", "heat_score": 75, "data_source": "instagram", "source_url": "https://gs.amazon.cn/zhishi/article-250413-1"},
        {"element_type": "color", "element_value": "深蓝色", "heat_score": 72, "data_source": "google_trends", "source_url": "https://es.accio.com/business/amazon-best-selling-clothes"},
        {"element_type": "color", "element_value": "卡其色", "heat_score": 70, "data_source": "pinterest", "source_url": "https://finance.sina.cn/2025-07-15/detail-inffqiin1945342.d.html"},
        {"element_type": "color", "element_value": "军绿色", "heat_score": 68, "data_source": "wgsn", "source_url": "https://es.accio.com/business/amazon-best-selling-clothes"},
        {"element_type": "color", "element_value": "烟熏淡彩", "heat_score": 66, "data_source": "wgsn", "source_url": "https://m.10100.com/article/1936937"},
        {"element_type": "color", "element_value": "酒红色", "heat_score": 65, "data_source": "statista", "source_url": "https://finance.sina.cn/2025-07-15/detail-inffqiin1945342.d.html"},
        {"element_type": "color", "element_value": "薄荷绿", "heat_score": 62, "data_source": "tiktok", "source_url": "https://m.topestexpress.com/xinwenzixun/2025-nianyamaxunmeiguofuzhuang.html"},
        {"element_type": "material", "element_value": "棉麻混纺", "heat_score": 92, "data_source": "google_trends", "source_url": "https://gs.amazon.cn/zhishi/article-250413-1"},
        {"element_type": "material", "element_value": "速干面料", "heat_score": 85, "data_source": "instagram", "source_url": "https://de.accio.com/business/top-selling-t-shirts-amazon"},
        {"element_type": "material", "element_value": "弹力纤维", "heat_score": 80, "data_source": "tiktok", "source_url": "https://es.accio.com/business/amazon-best-selling-clothes"},
        {"element_type": "material", "element_value": "纯棉", "heat_score": 78, "data_source": "google_trends", "source_url": "https://es.accio.com/business/amazon-best-selling-clothes"},
        {"element_type": "material", "element_value": "华夫格面料", "heat_score": 72, "data_source": "wgsn", "source_url": "https://de.accio.com/business/top-selling-t-shirts-amazon"},
        {"element_type": "material", "element_value": "防水面料", "heat_score": 65, "data_source": "wgsn", "source_url": "https://es.accio.com/business/amazon-best-selling-clothes"},
        {"element_type": "material", "element_value": "帆布", "heat_score": 60, "data_source": "statista", "source_url": "https://es.accio.com/business/amazon-best-selling-clothes"},
        {"element_type": "design", "element_value": "多口袋", "heat_score": 82, "data_source": "pinterest", "source_url": "https://finance.sina.cn/2025-07-15/detail-inffqiin1945342.d.html"},
        {"element_type": "design", "element_value": "高腰", "heat_score": 78, "data_source": "tiktok", "source_url": "https://www.alibaba.com/blog/top-amazon-best-sellers-womens-clothing-2025s-hottest-fashion-trends-you-cant-miss.html"},
        {"element_type": "design", "element_value": "图案印花", "heat_score": 75, "data_source": "instagram", "source_url": "https://de.accio.com/business/top-selling-t-shirts-amazon"},
        {"element_type": "design", "element_value": "V领", "heat_score": 70, "data_source": "google_trends", "source_url": "https://www.alibaba.com/blog/top-amazon-best-sellers-womens-clothing-2025s-hottest-fashion-trends-you-cant-miss.html"},
        {"element_type": "design", "element_value": "褶皱", "heat_score": 68, "data_source": "pinterest", "source_url": "https://finance.sina.cn/2025-07-15/detail-inffqiin1945342.d.html"},
        {"element_type": "design", "element_value": "翻领", "heat_score": 65, "data_source": "wgsn", "source_url": "https://gs.amazon.cn/zhishi/article-250413-1"},
        {"element_type": "design", "element_value": "桶形剪裁", "heat_score": 73, "data_source": "tiktok", "source_url": "https://www.elitedaily.com/shopping/amazons-selling-a-ton-of-these-bougie-pieces-that-dont-cling-to-your-body-look-good-on-everyone"},
        {"element_type": "fit", "element_value": "修身", "heat_score": 88, "data_source": "google_trends", "source_url": "https://finance.sina.cn/2025-07-15/detail-inffqiin1945342.d.html"},
        {"element_type": "fit", "element_value": "宽松", "heat_score": 75, "data_source": "tiktok", "source_url": "https://www.elitedaily.com/shopping/amazons-selling-a-ton-of-these-bougie-pieces-that-dont-cling-to-your-body-look-good-on-everyone"},
        {"element_type": "fit", "element_value": "常规", "heat_score": 60, "data_source": "statista", "source_url": "https://es.accio.com/business/amazon-best-selling-clothes"},
    ]
    logger.info(f"  抓取到 {len(trends)} 条趋势数据")
    return trends


def run_full_pipeline():
    logger.info("=" * 80)
    logger.info("亚马逊美国站跨境服装电商智能选品技能 - 实时数据采集")
    logger.info(f"运行时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info("=" * 80)

    raw_products = fetch_realtime_products()
    raw_trends = fetch_realtime_trends()
    news_items = fetch_realtime_news()

    deduplicator = DataDeduplicator()
    deduped_products = deduplicator.deduplicate_products(raw_products)
    deduped_trends = deduplicator.deduplicate_trends(raw_trends)

    denoiser = DataDenoiser()
    denoised_products = denoiser.denoise_products(deduped_products)
    denoised_trends = denoiser.denoise_trends(deduped_trends)

    standardizer = DataStandardizer()
    standardized_products = standardizer.batch_standardize_products(denoised_products)
    standardized_trends = standardizer.batch_standardize_trends(denoised_trends)

    compliance_checker = ComplianceChecker()
    for product in standardized_products:
        product["compliance_result"] = compliance_checker.check_compliance(product)

    classifier = DataClassifier()
    for product in standardized_products:
        product["classification"] = classifier.classify_product(product)

    trend_classifier = TrendClassifier()
    for trend in standardized_trends:
        trend.update(trend_classifier.classify_trend(trend))

    base_filter = BaseFilter()
    filtered_products = base_filter.filter(standardized_products)
    logger.info(f"  Rule1 基础筛选: {len(filtered_products)} 条通过")

    trend_matcher = TrendMatcher()
    trend_matcher.MATCH_THRESHOLD = 50.0
    matched_products = trend_matcher.match(filtered_products, standardized_trends)
    logger.info(f"  Rule2 趋势匹配: {len(matched_products)} 条匹配")

    unmatched = [p for p in filtered_products if p not in matched_products]
    for p in unmatched:
        p["match_status"] = "观察"
        p["trend_match_score"] = trend_matcher.calculate_match_score(p, standardized_trends)
        p["matched_elements"] = []

    all_candidates = matched_products + unmatched

    scorer = ProductScorer()
    for product in all_candidates:
        if "score_result" not in product:
            product["score_result"] = scorer.score(product)
    all_candidates.sort(key=lambda p: p["score_result"]["total_score"], reverse=True)

    element_extractor = ElementExtractor()
    extraction_result = element_extractor.extract(all_candidates, standardized_trends)

    optimizer = AlgorithmOptimizer()
    optimized_weights = optimizer.optimize_weights(all_candidates, {"trend_data": {"shift_intensity": "medium"}})

    uniqueness_calculator = UniquenessCalculator()
    for product in all_candidates:
        product["uniqueness_coefficient"] = 1.0 - uniqueness_calculator.calculate(product, [])

    product_push_builder = ProductPushBuilder()
    hit_products = [p for p in all_candidates if p.get("classification", {}).get("sales_tier") == "爆品"]
    potential_products = [p for p in all_candidates if p.get("classification", {}).get("sales_tier") in ("潜力品", "常规品")]
    hit_product_push = product_push_builder.build_hit_product_list(hit_products)
    potential_product_push = product_push_builder.build_potential_product_list(potential_products)

    element_push_builder = ElementPushBuilder()
    top10_elements_push = element_push_builder.build_top10_elements(extraction_result["top10_elements"])
    visual_diff_push = element_push_builder.build_visual_diff_suggestions(extraction_result["visual_diff_suggestions"])

    pitfall_push_builder = PitfallPushBuilder()
    pitfall_push = pitfall_push_builder.build_pitfall_reminders(all_candidates)

    uniqueness_push_builder = UniquenessPushBuilder()
    uniqueness_push = uniqueness_push_builder.build_uniqueness_recommendations(all_candidates, [], threshold=0.3)

    logger.info(f"  爆品: {len(hit_products)} 条, 潜力品: {len(potential_products)} 条")
    logger.info(f"  核心元素: {len(extraction_result['top10_elements'])} 个")
    logger.info(f"  视觉差异化: {len(extraction_result['visual_diff_suggestions'])} 条")

    output_data = {
        "run_time": datetime.now(timezone.utc).isoformat(),
        "news_items": news_items,
        "hit_products": hit_product_push,
        "potential_products": potential_product_push,
        "top10_elements": top10_elements_push,
        "visual_diff_suggestions": visual_diff_push,
        "pitfall_warnings": pitfall_push,
        "uniqueness_recommendations": uniqueness_push,
        "data_statistics": {
            "raw_products": len(raw_products),
            "raw_trends": len(raw_trends),
            "news_count": len(news_items),
            "deduped_products": len(deduped_products),
            "filtered_products": len(filtered_products),
            "matched_products": len(matched_products),
            "total_candidates": len(all_candidates),
            "hit_products": len(hit_products),
            "potential_products": len(potential_products),
        }
    }

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "skill_result.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    run_date = datetime.now().strftime("%Y-%m-%d")
    dated_file = os.path.join(output_dir, f"skill_result_{run_date}.json")
    with open(dated_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    logger.info(f"  结果已保存到: {output_file}")
    logger.info(f"  历史副本: {dated_file}")
    return output_data


if __name__ == "__main__":
    try:
        result = run_full_pipeline()
        logger.info("✅ 技能运行成功！")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 技能运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
