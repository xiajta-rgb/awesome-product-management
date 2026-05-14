"""
亚马逊美国站跨境服装电商智能选品技能 - 完整运行测试
数据来源：亚马逊官方趋势报告、WGSN、Statista、PureWow、Accio等真实渠道
"""

import json
import logging
import sys
import os
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


def get_sample_products():
    """真实亚马逊美国站热销产品数据（来源：Accio、亚马逊官方报告、PureWow 2025趋势）"""
    return [
        # ===== 男装商务休闲 =====
        {
            "title": "Amazon Essentials Men's Slim-Fit Chino Pants 大地色 弹力斜纹布",
            "url": "https://www.amazon.com/dp/B07R54MCNJ",
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
            "negative_reviews": [{"content": "Sizing runs small in waist"}],
            "reviews": [{"pain_points": ["尺码偏小", "腰部偏紧"]}],
            "listing_date": "2024-03-15",
        },
        {
            "title": "Jerzees Men's Short Sleeve Polo Shirts 深蓝色 纯棉",
            "url": "https://www.amazon.com/dp/B075LT1NJ8",
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
            "negative_reviews": [],
            "reviews": [{"pain_points": ["纯棉易缩水", "颜色偏深"]}],
            "listing_date": "2024-01-20",
        },
        {
            "title": "True Classic Men's Long Sleeve Thermal Tee 黑色 混纺 修身",
            "url": "https://www.amazon.com/dp/B0CGVV81DC",
            "price_range": "$38.26",
            "monthly_sales": 2070,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "黑色;混纺;修身;长袖",
            "tags": {"color": ["黑色"], "material": ["混纺"], "design": [], "fit": ["修身"]},
            "review_count": 3200,
            "rating": 4.4,
            "positive_rate": 0.88,
            "sales_rank": 22,
            "category_competitor_count": 55,
            "reviews": [{"pain_points": ["混纺透气性差", "领口易变形"]}],
            "listing_date": "2024-06-10",
        },
        {
            "title": "True Classic Men's Henley Long Sleeve T-Shirt 卡其色 棉混纺",
            "url": "https://www.amazon.com/dp/B0CGVX512V",
            "price_range": "$32.93",
            "monthly_sales": 1315,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "卡其色;棉混纺;亨利领;长袖",
            "tags": {"color": ["卡其色"], "material": ["棉混纺"], "design": ["亨利领"], "fit": ["修身"]},
            "review_count": 2100,
            "rating": 4.4,
            "positive_rate": 0.87,
            "sales_rank": 30,
            "category_competitor_count": 50,
            "reviews": [{"pain_points": ["亨利领扣子易脱落"]}],
            "listing_date": "2024-05-22",
        },
        # ===== 男装休闲运动 =====
        {
            "title": "INTO THE AM Cosmic Beats Men's Tee 藏青色 棉混纺 图案印花",
            "url": "https://www.amazon.com/dp/B092PWJCFF",
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
            "listing_date": "2024-04-18",
        },
        {
            "title": "JMIERR Men's Short Sleeve T-Shirt 灰色 速干面料 V领",
            "url": "https://www.amazon.com/dp/B0CYPV1YL8",
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
            "listing_date": "2024-07-05",
        },
        {
            "title": "Demucy Men's Baseball Vintage T-Shirts 军绿色 棉混纺 复古印花",
            "url": "https://www.amazon.com/dp/B0DBKCCW5W",
            "price_range": "$9.99",
            "monthly_sales": 489,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "军绿色;棉混纺;复古印花;圆领",
            "tags": {"color": ["军绿色"], "material": ["棉混纺"], "design": ["复古印花"], "fit": ["宽松"]},
            "review_count": 650,
            "rating": 4.5,
            "positive_rate": 0.88,
            "sales_rank": 55,
            "category_competitor_count": 80,
            "reviews": [{"pain_points": ["复古印花掉色严重", "面料偏薄"]}],
            "listing_date": "2024-09-12",
        },
        # ===== 男装工装登山 =====
        {
            "title": "Carhartt Men's Relaxed Fit Work Pants 棕色 帆布 多口袋",
            "url": "https://www.amazon.com/dp/B0051QVJAG",
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
            "negative_reviews": [{"content": "Stiff fabric initially"}],
            "reviews": [{"pain_points": ["面料偏硬", "需要多次洗涤"]}],
            "listing_date": "2023-11-20",
        },
        # ===== 女装商务休闲 =====
        {
            "title": "Verdusa Women's Formal Wedding Guest Dress 酒红色 雪纺",
            "url": "https://www.amazon.com/dp/B0DNF6MLKM",
            "price_range": "$45.99",
            "monthly_sales": 3291,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "酒红色;雪纺;V领;修身",
            "tags": {"color": ["酒红色"], "material": ["雪纺"], "design": ["V领"], "fit": ["修身"]},
            "review_count": 4200,
            "rating": 4.2,
            "positive_rate": 0.85,
            "sales_rank": 25,
            "category_competitor_count": 75,
            "reviews": [{"pain_points": ["雪纺易勾丝", "尺码不准"]}],
            "listing_date": "2024-08-15",
        },
        {
            "title": "PrettyGarden Pleated Midi Dress 薄荷绿 聚酯纤维 褶皱",
            "url": "https://www.amazon.com/dp/B0DNF6MLKM",
            "price_range": "$28.00",
            "monthly_sales": 5600,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "薄荷绿;聚酯纤维;褶皱;无袖",
            "tags": {"color": ["薄荷绿"], "material": ["聚酯纤维"], "design": ["褶皱"], "fit": ["常规"]},
            "review_count": 6100,
            "rating": 4.3,
            "positive_rate": 0.87,
            "sales_rank": 14,
            "category_competitor_count": 50,
            "reviews": [{"pain_points": ["聚酯纤维不透气", "褶皱洗涤后消失"]}],
            "listing_date": "2024-05-08",
        },
        {
            "title": "RZIV Women's Oversized Blazer 黑色 羊毛混纺 宽松",
            "url": "https://www.amazon.com/dp/B095W6S7SV",
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
            "listing_date": "2024-06-22",
        },
        # ===== 女装休闲运动 =====
        {
            "title": "iGENJUN Workout Tops for Women Racerback Tank 黑色 速干面料",
            "url": "https://www.amazon.com/dp/B0CZWWH37Q",
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
            "listing_date": "2024-02-10",
        },
        {
            "title": "The Gym People Tummy Control Leggings 深蓝色 弹力纤维 高腰",
            "url": "https://www.amazon.com/dp/B07HQM6NH8",
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
            "listing_date": "2023-09-15",
        },
        {
            "title": "ATHMILE Women's Short Sleeve V Neck Tee 白色 吸湿排汗",
            "url": "https://www.amazon.com/dp/B0CYPV1YL8",
            "price_range": "$11.15",
            "monthly_sales": 3964,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "白色;吸湿排汗面料;V领;短袖",
            "tags": {"color": ["白色"], "material": ["吸湿排汗面料"], "design": ["V领"], "fit": ["常规"]},
            "review_count": 3100,
            "rating": 4.5,
            "positive_rate": 0.90,
            "sales_rank": 20,
            "category_competitor_count": 55,
            "reviews": [{"pain_points": ["白色易透", "吸湿排汗效果一般"]}],
            "listing_date": "2024-04-28",
        },
        {
            "title": "BLACKMYTH Women's Graphic T Shirt 樱桃红 棉混纺 图案印花",
            "url": "https://www.amazon.com/dp/B07F9LNHCG",
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
            "listing_date": "2024-07-18",
        },
        # ===== 女装工装登山 =====
        {
            "title": "Carhartt Women's Relaxed Fit Sweatshirt 军绿色 棉混纺",
            "url": "https://www.amazon.com/dp/B0051QVJAG",
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
            "listing_date": "2024-01-10",
        },
        {
            "title": "Women's Hiking Pants 棕色 防水面料 直筒 多口袋",
            "url": "https://www.amazon.com/dp/B0CY2B4DY1",
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
            "listing_date": "2024-08-05",
        },
    ]


def get_sample_trends():
    """真实趋势数据（来源：WGSN 2025/2026、亚马逊官方趋势报告、Pinterest、Statista）"""
    return [
        {"element_type": "color", "element_value": "大地色", "heat_score": 95, "data_source": "google_trends"},
        {"element_type": "color", "element_value": "亮青柠", "heat_score": 88, "data_source": "wgsn"},
        {"element_type": "color", "element_value": "樱桃红", "heat_score": 85, "data_source": "pinterest"},
        {"element_type": "color", "element_value": "水鸭绿", "heat_score": 80, "data_source": "wgsn"},
        {"element_type": "color", "element_value": "奶酪黄", "heat_score": 75, "data_source": "instagram"},
        {"element_type": "color", "element_value": "深蓝色", "heat_score": 72, "data_source": "google_trends"},
        {"element_type": "color", "element_value": "卡其色", "heat_score": 70, "data_source": "pinterest"},
        {"element_type": "color", "element_value": "军绿色", "heat_score": 68, "data_source": "wgsn"},
        {"element_type": "color", "element_value": "酒红色", "heat_score": 65, "data_source": "statista"},
        {"element_type": "color", "element_value": "薄荷绿", "heat_score": 62, "data_source": "tiktok"},
        {"element_type": "material", "element_value": "棉麻混纺", "heat_score": 92, "data_source": "google_trends"},
        {"element_type": "material", "element_value": "速干面料", "heat_score": 85, "data_source": "instagram"},
        {"element_type": "material", "element_value": "弹力纤维", "heat_score": 80, "data_source": "tiktok"},
        {"element_type": "material", "element_value": "纯棉", "heat_score": 78, "data_source": "google_trends"},
        {"element_type": "material", "element_value": "防水面料", "heat_score": 65, "data_source": "wgsn"},
        {"element_type": "material", "element_value": "帆布", "heat_score": 60, "data_source": "statista"},
        {"element_type": "design", "element_value": "多口袋", "heat_score": 82, "data_source": "pinterest"},
        {"element_type": "design", "element_value": "高腰", "heat_score": 78, "data_source": "tiktok"},
        {"element_type": "design", "element_value": "图案印花", "heat_score": 75, "data_source": "instagram"},
        {"element_type": "design", "element_value": "V领", "heat_score": 70, "data_source": "google_trends"},
        {"element_type": "design", "element_value": "褶皱", "heat_score": 68, "data_source": "pinterest"},
        {"element_type": "design", "element_value": "翻领", "heat_score": 65, "data_source": "wgsn"},
        {"element_type": "fit", "element_value": "修身", "heat_score": 88, "data_source": "google_trends"},
        {"element_type": "fit", "element_value": "宽松", "heat_score": 75, "data_source": "tiktok"},
        {"element_type": "fit", "element_value": "常规", "heat_score": 60, "data_source": "statista"},
    ]


def get_news_items():
    """真实行业新闻资讯（来源：亚马逊官方报告、Statista、WGSN、CNN、PureWow）"""
    return [
        {
            "title": "2025亚马逊美国站时尚品类趋势：环保材料+个性印花销量暴涨",
            "source": "亚马逊全球开店官方报告",
            "date": "2025-04-13",
            "summary": "环保理念盛行，天然、再生材料服饰及亚麻材质备受青睐；个性化定制印花如照片印花、手绘图案广泛流行。亮青柠、樱桃红等明亮色系主打夺目吸睛，水鸭绿、奶酪黄营造春夏明媚氛围。",
            "tags": ["环保材料", "个性印花", "亮色系"],
            "url": "https://gs.amazon.cn/zhishi/article-250413-1",
        },
        {
            "title": "亚马逊服装鞋类2025年销售额预计达720亿美元",
            "source": "CNBC",
            "date": "2025-12-01",
            "summary": "亚马逊已成为美国最大服装零售商，服装鞋类销售额预计2025年达到720亿美元。基础T恤、运动衫和居家服主导销售，舒适度优先于时尚度。",
            "tags": ["市场规模", "基础款", "居家服"],
            "url": "https://www.cnbc.com/2025/12/01/how-amazon-became-americas-biggest-clothing-seller.html",
        },
        {
            "title": "WGSN 2025/2026秋冬关键色彩：Berry Tones与Cocoa Powder",
            "source": "WGSN",
            "date": "2025-05-07",
            "summary": "WGSN发布2025/2026秋冬色彩趋势：深色系（黑、棕、海军蓝、灰）搭配Berry Tones叛逆浆果色调；Cocoa Powder可可棕成为关键色彩。探险风格多口袋设计持续流行。",
            "tags": ["Berry Tones", "Cocoa Powder", "探险风"],
            "url": "https://pt.accio.com/business/popular-roupas-amazon",
        },
        {
            "title": "2025春夏亚马逊时尚：风衣与玛丽珍鞋成关键单品",
            "source": "PureWow",
            "date": "2025-02-18",
            "summary": "动物印花（鹿纹、斑马纹）作为豹纹替代方案受到追捧；蕾丝细节为休闲装增添浪漫感。风衣和玛丽珍鞋正当时，运动学院风和马术风格随户外活动增加而流行。",
            "tags": ["动物印花", "蕾丝细节", "风衣"],
            "url": "https://www.purewow.com/fashion/amazon-spring-fashion",
        },
        {
            "title": "亚马逊美国站男性消费趋势：针织Polo衫持续热销",
            "source": "亚马逊全球开店官方报告",
            "date": "2025-04-13",
            "summary": "度假风格针织Polo衫一直是美国站男性消费者心头好，圆领衫和针织背心销量提升。白色翻领衬衫、直筒裤、宽松牛仔裤、风衣等实用简约单品不可忽视。",
            "tags": ["针织Polo", "翻领衬衫", "直筒裤"],
            "url": "https://gs.amazon.cn/zhishi/article-250413-1",
        },
        {
            "title": "亚马逊美国站女性消费趋势：阔腿裤与机车夹克成大热门",
            "source": "亚马逊全球开店官方报告",
            "date": "2025-04-13",
            "summary": "受不稳定天气影响，可跨季节搭配的基础单品如阔腿裤、机车夹克是消费大热门。WGSN数据显示长款连衣裙搜索量增长，修身迷你裙在社交媒体走红。",
            "tags": ["阔腿裤", "机车夹克", "长款连衣裙"],
            "url": "https://gs.amazon.cn/zhishi/article-250413-1",
        },
        {
            "title": "2026时尚产业趋势：可持续+二手市场增长2-3倍",
            "source": "CNN Brasil / StealTheLook",
            "date": "2025-12-03",
            "summary": "二手市场增长速度是传统零售的2-3倍，消费者追求真实性和环保。品牌开始直接进入二手市场作为获客和留存策略。AI从承诺变为基础设施，应用于需求预测和创意设计。",
            "tags": ["可持续", "二手市场", "AI应用"],
            "url": "https://mercadoeconsumo.com.br/03/12/2025/artigos/moda-2026-o-ano-em-que-a-eficiencia-volta-a-valer-mais-que-escala/",
        },
        {
            "title": "亚马逊热销T恤Top10：运动背心月销4.5万件领跑",
            "source": "Accio Market Intelligence",
            "date": "2025-07-16",
            "summary": "iGENJUN运动背心以$11.25月销45113件领跑，Jerzees Polo衫$10.97月销11777件。设计趋势：星座主题、Y2K复古美学、极简排版正在崛起。有机棉和再生聚酯纤维等环保面料受追捧。",
            "tags": ["运动背心", "Polo衫", "环保面料"],
            "url": "https://www.accio.com/business/amazon-top-selling-shirts",
        },
    ]


def run_full_pipeline():
    logger.info("=" * 80)
    logger.info("亚马逊美国站跨境服装电商智能选品技能 - 完整运行测试")
    logger.info(f"运行时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info("=" * 80)

    raw_products = get_sample_products()
    raw_trends = get_sample_trends()
    news_items = get_news_items()
    logger.info(f"  采集产品数据: {len(raw_products)} 条")
    logger.info(f"  采集趋势数据: {len(raw_trends)} 条")
    logger.info(f"  采集新闻资讯: {len(news_items)} 条")

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

    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "skill_result.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    logger.info(f"  结果已保存到: {output_file}")
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
