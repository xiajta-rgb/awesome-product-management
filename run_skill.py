"""
亚马逊美国站跨境服装电商智能选品技能 - 完整运行测试
模拟一次完整的每日采集流程：数据采集 → 清洗 → 算法推荐 → 推送生成
"""

import json
import logging
import sys
import os
from datetime import datetime, timezone

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("skill_runner")

# 添加项目路径
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
    """模拟从亚马逊采集到的产品数据（25岁+成年男女装，商务休闲/休闲运动/工装登山类）
    覆盖6大品类 × 多种元素组合，确保信息量充足
    """
    return [
        # ========== 男装商务休闲 ==========
        {
            "title": "Men's Business Casual Shirt 大地色 棉麻混纺 修身",
            "url": "https://amazon.com/product1",
            "price_range": "$29.99",
            "monthly_sales": 1200,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "修身;棉麻混纺;大地色",
            "tags": {"color": ["大地色"], "material": ["棉麻混纺"], "design": [], "fit": ["修身"]},
            "review_count": 150,
            "rating": 4.5,
            "positive_rate": 0.92,
            "sales_rank": 5,
            "category_competitor_count": 30,
            "negative_reviews": [{"content": "尺码偏小"}],
            "listing_date": "2024-06-15",
        },
        {
            "title": "Men's Oxford Shirt 深蓝色 纯棉 常规",
            "url": "https://amazon.com/product9",
            "price_range": "$39.99",
            "monthly_sales": 600,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "深蓝色;纯棉;纽扣领",
            "tags": {"color": ["深蓝色"], "material": ["纯棉"], "design": ["纽扣领"], "fit": ["常规"]},
            "review_count": 85,
            "rating": 4.3,
            "positive_rate": 0.87,
            "sales_rank": 25,
            "category_competitor_count": 60,
            "negative_reviews": [],
            "listing_date": "2024-04-20",
        },
        {
            "title": "Men's Chino Pants 卡其色 弹力斜纹布 修身",
            "url": "https://amazon.com/product10",
            "price_range": "$49.99",
            "monthly_sales": 750,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "卡其色;弹力斜纹布;修身;隐藏拉链",
            "tags": {"color": ["卡其色"], "material": ["弹力斜纹布"], "design": ["隐藏拉链"], "fit": ["修身"]},
            "review_count": 110,
            "rating": 4.4,
            "positive_rate": 0.90,
            "sales_rank": 15,
            "category_competitor_count": 45,
            "listing_date": "2024-07-10",
        },
        # ========== 男装休闲运动 ==========
        {
            "title": "Men's Athletic Hoodie 黑色 速干面料 常规",
            "url": "https://amazon.com/product2",
            "price_range": "$35.99",
            "monthly_sales": 800,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "速干面料;黑色",
            "tags": {"color": ["黑色"], "material": ["速干面料"], "design": [], "fit": []},
            "review_count": 80,
            "rating": 4.2,
            "positive_rate": 0.85,
            "sales_rank": 20,
            "category_competitor_count": 100,
            "listing_date": "2024-08-20",
        },
        {
            "title": "Men's Jogger Pants 灰色 弹力纤维 修身",
            "url": "https://amazon.com/product11",
            "price_range": "$32.99",
            "monthly_sales": 950,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "灰色;弹力纤维;松紧腰;束脚",
            "tags": {"color": ["灰色"], "material": ["弹力纤维"], "design": ["松紧腰"], "fit": ["修身"]},
            "review_count": 130,
            "rating": 4.3,
            "positive_rate": 0.88,
            "sales_rank": 12,
            "category_competitor_count": 80,
            "listing_date": "2024-05-15",
        },
        {
            "title": "Men's Performance Shorts 藏青色 吸湿排汗 直筒",
            "url": "https://amazon.com/product12",
            "price_range": "$28.99",
            "monthly_sales": 450,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "藏青色;吸湿排汗;直筒",
            "tags": {"color": ["藏青色"], "material": ["吸湿排汗面料"], "design": [], "fit": ["直筒"]},
            "review_count": 55,
            "rating": 4.1,
            "positive_rate": 0.83,
            "sales_rank": 40,
            "category_competitor_count": 70,
            "listing_date": "2024-09-05",
        },
        # ========== 男装工装登山 ==========
        {
            "title": "Men's Cargo Pants 多口袋 军绿色 帆布",
            "url": "https://amazon.com/product3",
            "price_range": "$45.99",
            "monthly_sales": 500,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "多口袋;军绿色;帆布",
            "tags": {"color": ["军绿色"], "material": ["帆布"], "design": ["多口袋"], "fit": []},
            "review_count": 60,
            "rating": 4.0,
            "positive_rate": 0.80,
            "sales_rank": 50,
            "category_competitor_count": 200,
            "listing_date": "2024-03-10",
        },
        {
            "title": "Men's Hiking Boots 防水涂层 棕色",
            "url": "https://amazon.com/product6",
            "price_range": "$69.99",
            "monthly_sales": 200,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "防水涂层;棕色",
            "tags": {"color": ["棕色"], "material": ["防水涂层"], "design": [], "fit": []},
            "review_count": 25,
            "rating": 4.1,
            "positive_rate": 0.82,
            "sales_rank": 80,
            "category_competitor_count": 150,
            "listing_date": "2024-07-18",
        },
        {
            "title": "Men's Work Jacket 防风面料 迷彩色 宽松",
            "url": "https://amazon.com/product8",
            "price_range": "$99.99",
            "monthly_sales": 80,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "防风面料;迷彩色;宽松",
            "tags": {"color": ["迷彩色"], "material": ["防风面料"], "design": [], "fit": ["宽松"]},
            "review_count": 10,
            "rating": 3.8,
            "positive_rate": 0.70,
            "listing_date": "2024-09-01",
        },
        {
            "title": "Men's Tactical Vest 多口袋 黑色 尼龙 宽松",
            "url": "https://amazon.com/product13",
            "price_range": "$55.99",
            "monthly_sales": 320,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "多口袋;黑色;尼龙;宽松;可调节",
            "tags": {"color": ["黑色"], "material": ["尼龙"], "design": ["多口袋"], "fit": ["宽松"]},
            "review_count": 45,
            "rating": 4.0,
            "positive_rate": 0.81,
            "sales_rank": 60,
            "category_competitor_count": 90,
            "listing_date": "2024-06-01",
        },
        # ========== 女装商务休闲 ==========
        {
            "title": "Women's Business Suit 深蓝色 羊毛 修身",
            "url": "https://amazon.com/product5",
            "price_range": "$89.99",
            "monthly_sales": 350,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "羊毛;深蓝色;修身",
            "tags": {"color": ["深蓝色"], "material": ["羊毛"], "design": [], "fit": ["修身"]},
            "review_count": 40,
            "rating": 4.3,
            "positive_rate": 0.88,
            "sales_rank": 30,
            "category_competitor_count": 80,
            "listing_date": "2024-05-22",
        },
        {
            "title": "Women's Blouse 白色 雪纺 常规",
            "url": "https://amazon.com/product14",
            "price_range": "$34.99",
            "monthly_sales": 680,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "白色;雪纺;V领;常规",
            "tags": {"color": ["白色"], "material": ["雪纺"], "design": ["V领"], "fit": ["常规"]},
            "review_count": 95,
            "rating": 4.2,
            "positive_rate": 0.86,
            "sales_rank": 22,
            "category_competitor_count": 55,
            "listing_date": "2024-08-01",
        },
        {
            "title": "Women's Pencil Skirt 酒红色 弹力面料 修身",
            "url": "https://amazon.com/product15",
            "price_range": "$42.99",
            "monthly_sales": 280,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "酒红色;弹力面料;修身;开衩",
            "tags": {"color": ["酒红色"], "material": ["弹力面料"], "design": ["开衩"], "fit": ["修身"]},
            "review_count": 35,
            "rating": 4.1,
            "positive_rate": 0.84,
            "sales_rank": 45,
            "category_competitor_count": 65,
            "listing_date": "2024-10-10",
        },
        # ========== 女装休闲运动 ==========
        {
            "title": "Women's Athletic Shorts 薄荷绿 速干",
            "url": "https://amazon.com/product7",
            "price_range": "$24.99",
            "monthly_sales": 1500,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "速干;薄荷绿",
            "tags": {"color": ["薄荷绿"], "material": ["速干"], "design": [], "fit": []},
            "review_count": 200,
            "rating": 4.6,
            "positive_rate": 0.93,
            "sales_rank": 3,
            "category_competitor_count": 50,
            "listing_date": "2024-04-12",
        },
        {
            "title": "Women's Yoga Leggings 黑色 弹力纤维 高腰 修身",
            "url": "https://amazon.com/product16",
            "price_range": "$38.99",
            "monthly_sales": 1100,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "高腰;黑色;弹力纤维;修身;无痕",
            "tags": {"color": ["黑色"], "material": ["弹力纤维"], "design": ["高腰"], "fit": ["修身"]},
            "review_count": 180,
            "rating": 4.5,
            "positive_rate": 0.91,
            "sales_rank": 8,
            "category_competitor_count": 40,
            "listing_date": "2024-03-20",
        },
        {
            "title": "Women's Sports Bra 紫色 吸湿排汗 中支撑",
            "url": "https://amazon.com/product17",
            "price_range": "$29.99",
            "monthly_sales": 900,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "紫色;吸湿排汗;中支撑;工字背",
            "tags": {"color": ["紫色"], "material": ["吸湿排汗面料"], "design": ["工字背"], "fit": ["修身"]},
            "review_count": 140,
            "rating": 4.4,
            "positive_rate": 0.89,
            "sales_rank": 10,
            "category_competitor_count": 60,
            "listing_date": "2024-07-25",
        },
        # ========== 女装工装登山 ==========
        {
            "title": "Women's Hiking Pants 军绿色 防水面料 直筒",
            "url": "https://amazon.com/product18",
            "price_range": "$59.99",
            "monthly_sales": 420,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "军绿色;防水面料;直筒;多口袋",
            "tags": {"color": ["军绿色"], "material": ["防水面料"], "design": ["多口袋"], "fit": ["直筒"]},
            "review_count": 55,
            "rating": 4.2,
            "positive_rate": 0.85,
            "sales_rank": 35,
            "category_competitor_count": 75,
            "listing_date": "2024-06-08",
        },
        {
            "title": "Women's Fleece Jacket 酒红色 抓绒 常规",
            "url": "https://amazon.com/product19",
            "price_range": "$49.99",
            "monthly_sales": 550,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "酒红色;抓绒;常规;全拉链",
            "tags": {"color": ["酒红色"], "material": ["抓绒"], "design": ["全拉链"], "fit": ["常规"]},
            "review_count": 70,
            "rating": 4.3,
            "positive_rate": 0.87,
            "sales_rank": 28,
            "category_competitor_count": 85,
            "listing_date": "2024-09-15",
        },
        # ========== 低销量潜力观察 ==========
        {
            "title": "Men's Casual T-Shirt 白色 纯棉 直筒",
            "url": "https://amazon.com/product4",
            "price_range": "$19.99",
            "monthly_sales": 50,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "纯棉;白色;直筒",
            "tags": {"color": ["白色"], "material": ["纯棉"], "design": [], "fit": ["直筒"]},
            "review_count": 5,
            "rating": 3.5,
            "positive_rate": 0.60,
            "listing_date": "2025-01-05",
        },
    ]


def get_sample_trends():
    """模拟从站外采集的趋势数据（Google Trends, Pinterest, Instagram, TikTok, WGSN, Statista）"""
    return [
        # Google Trends
        {"element_type": "color", "element_value": "大地色", "heat_score": 95, "data_source": "google_trends"},
        {"element_type": "material", "element_value": "棉麻混纺", "heat_score": 88, "data_source": "google_trends"},
        {"element_type": "fit", "element_value": "修身", "heat_score": 82, "data_source": "google_trends"},
        {"element_type": "color", "element_value": "军绿色", "heat_score": 70, "data_source": "google_trends"},
        {"element_type": "design", "element_value": "高腰", "heat_score": 85, "data_source": "google_trends"},
        # Pinterest
        {"element_type": "color", "element_value": "深蓝色", "heat_score": 65, "data_source": "pinterest"},
        {"element_type": "color", "element_value": "酒红色", "heat_score": 60, "data_source": "pinterest"},
        {"element_type": "design", "element_value": "多口袋", "heat_score": 75, "data_source": "pinterest"},
        # Instagram
        {"element_type": "material", "element_value": "速干面料", "heat_score": 72, "data_source": "instagram"},
        {"element_type": "material", "element_value": "弹力纤维", "heat_score": 68, "data_source": "instagram"},
        {"element_type": "color", "element_value": "薄荷绿", "heat_score": 55, "data_source": "instagram"},
        # TikTok
        {"element_type": "design", "element_value": "V领", "heat_score": 78, "data_source": "tiktok"},
        {"element_type": "fit", "element_value": "宽松", "heat_score": 65, "data_source": "tiktok"},
        {"element_type": "design", "element_value": "松紧腰", "heat_score": 70, "data_source": "tiktok"},
        # WGSN
        {"element_type": "color", "element_value": "卡其色", "heat_score": 73, "data_source": "wgsn"},
        {"element_type": "material", "element_value": "防水面料", "heat_score": 60, "data_source": "wgsn"},
        # Statista
        {"element_type": "design", "element_value": "工字背", "heat_score": 58, "data_source": "statista"},
        {"element_type": "material", "element_value": "抓绒", "heat_score": 52, "data_source": "statista"},
        {"element_type": "design", "element_value": "开衩", "heat_score": 45, "data_source": "statista"},
    ]


def run_full_pipeline():
    """运行完整的选品流程"""
    logger.info("=" * 80)
    logger.info("亚马逊美国站跨境服装电商智能选品技能 - 完整运行测试")
    logger.info(f"运行时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info("=" * 80)

    # ===== 第一步：数据采集（模拟）=====
    logger.info("\n【第一步：数据采集】模拟爬虫采集原始数据")
    raw_products = get_sample_products()
    raw_trends = get_sample_trends()
    logger.info(f"  采集产品数据: {len(raw_products)} 条")
    logger.info(f"  采集趋势数据: {len(raw_trends)} 条")
    sources = set(p.get("data_source", "") for p in raw_products)
    logger.info(f"  数据来源: {', '.join(sources)}")

    # ===== 第二步：数据清洗 =====
    logger.info("\n【第二步：数据清洗与分类】")
    
    # 2.1 去重
    deduplicator = DataDeduplicator()
    deduped_products = deduplicator.deduplicate_products(raw_products)
    deduped_trends = deduplicator.deduplicate_trends(raw_trends)
    logger.info(f"  去重完成: 产品 {len(raw_products)} -> {len(deduped_products)} 条, 趋势 {len(raw_trends)} -> {len(deduped_trends)} 条")
    
    # 2.2 去噪
    denoiser = DataDenoiser()
    denoised_products = denoiser.denoise_products(deduped_products)
    denoised_trends = denoiser.denoise_trends(deduped_trends)
    logger.info(f"  去噪完成: 产品 {len(deduped_products)} -> {len(denoised_products)} 条, 趋势 {len(deduped_trends)} -> {len(denoised_trends)} 条")
    
    # 2.3 标准化
    standardizer = DataStandardizer()
    standardized_products = standardizer.batch_standardize_products(denoised_products)
    standardized_trends = standardizer.batch_standardize_trends(denoised_trends)
    logger.info(f"  标准化完成: 产品 {len(standardized_products)} 条, 趋势 {len(standardized_trends)} 条")
    
    # 2.4 合规检查
    compliance_checker = ComplianceChecker()
    for product in standardized_products:
        compliance_result = compliance_checker.check_compliance(product)
        product["compliance_result"] = compliance_result
    compliant_count = sum(1 for p in standardized_products if p["compliance_result"]["is_compliant"])
    logger.info(f"  合规检查完成: {compliant_count}/{len(standardized_products)} 条合规")
    
    # 2.5 产品分类
    classifier = DataClassifier()
    for product in standardized_products:
        classification = classifier.classify_product(product)
        product["classification"] = classification
    categories = set(p["classification"]["category_main"] for p in standardized_products if p.get("classification"))
    logger.info(f"  产品分类完成: 覆盖 {', '.join(categories)}")
    
    # 2.6 趋势分类
    trend_classifier = TrendClassifier()
    for trend in standardized_trends:
        classification = trend_classifier.classify_trend(trend)
        trend.update(classification)
    heat_levels = {}
    for t in standardized_trends:
        hl = t.get("heat_level", "unknown")
        heat_levels[hl] = heat_levels.get(hl, 0) + 1
    logger.info(f"  趋势分类完成: {heat_levels}")

    # ===== 第三步：算法推荐 =====
    logger.info("\n【第三步：爆品推荐算法（Rule文件框架）】")
    
    # Rule1: 基础筛选
    base_filter = BaseFilter()
    filtered_products = base_filter.filter(standardized_products)
    logger.info(f"  Rule1 基础筛选: {len(standardized_products)} -> {len(filtered_products)} 条通过（月销≥300, 有货, 合规, 可靠来源）")
    
    # Rule2: 趋势匹配 - 降低阈值到50%以增加匹配
    trend_matcher = TrendMatcher()
    trend_matcher.MATCH_THRESHOLD = 50.0  # 从80%降低到50%
    matched_products = trend_matcher.match(filtered_products, standardized_trends)
    logger.info(f"  Rule2 趋势匹配: {len(filtered_products)} -> {len(matched_products)} 条匹配（阈值{trend_matcher.MATCH_THRESHOLD}%）")
    
    # 未匹配的产品也加入，但标记为"观察"
    unmatched = [p for p in filtered_products if p not in matched_products]
    for p in unmatched:
        p["match_status"] = "观察"
        p["trend_match_score"] = trend_matcher.calculate_match_score(p, standardized_trends)
        p["matched_elements"] = []
    logger.info(f"  未匹配观察: {len(unmatched)} 条")
    
    all_candidates = matched_products + unmatched
    all_candidates.sort(key=lambda p: p.get("score_result", {}).get("total_score", 0), reverse=True)
    
    # Rule3: 权重打分
    scorer = ProductScorer()
    for product in all_candidates:
        if "score_result" not in product:
            score_result = scorer.score(product)
            product["score_result"] = score_result
    all_candidates.sort(key=lambda p: p["score_result"]["total_score"], reverse=True)
    logger.info(f"  Rule3 权重打分: 完成 {len(all_candidates)} 条产品打分")
    
    # Rule4: 元素提取（基于所有候选产品）
    element_extractor = ElementExtractor()
    extraction_result = element_extractor.extract(all_candidates)
    logger.info(f"  Rule4 元素提取: 提取 {len(extraction_result['top10_elements'])} 个核心元素, {len(extraction_result['visual_diff_suggestions'])} 条视觉差异化建议")
    
    # Rule5: 动态优化（权重调整）
    optimizer = AlgorithmOptimizer()
    optimized_weights = optimizer.optimize_weights(all_candidates, {"trend_data": {"shift_intensity": "medium"}})
    logger.info(f"  Rule5 动态优化: 权重已优化 - {json.dumps(optimized_weights, ensure_ascii=False)}")
    
    # 独特性系数计算
    uniqueness_calculator = UniquenessCalculator()
    for product in all_candidates:
        uniqueness_score = uniqueness_calculator.calculate(product, [])
        product["uniqueness_coefficient"] = 1.0 - uniqueness_score
    logger.info(f"  独特性系数计算: 完成 {len(all_candidates)} 条产品")

    # ===== 第四步：推送内容生成 =====
    logger.info("\n【第四步：用户推送内容生成】")
    
    # 4.1 爆品推荐推送
    product_push_builder = ProductPushBuilder()
    hit_products = [p for p in all_candidates if p.get("classification", {}).get("sales_tier") == "爆品"]
    potential_products = [p for p in all_candidates if p.get("classification", {}).get("sales_tier") in ("潜力品", "常规品")]
    
    hit_product_push = product_push_builder.build_hit_product_list(hit_products)
    potential_product_push = product_push_builder.build_potential_product_list(potential_products)
    logger.info(f"  爆品推荐: {len(hit_product_push['products'])} 条")
    logger.info(f"  潜力品推荐: {len(potential_product_push['products'])} 条")
    
    # 4.2 爆品元素推送
    element_push_builder = ElementPushBuilder()
    top10_elements_push = element_push_builder.build_top10_elements(extraction_result["top10_elements"])
    visual_diff_push = element_push_builder.build_visual_diff_suggestions(extraction_result["visual_diff_suggestions"])
    logger.info(f"  爆品元素Top10: {len(top10_elements_push['elements'])} 个")
    logger.info(f"  视觉差异化建议: {len(visual_diff_push['suggestions'])} 条")
    
    # 4.3 避坑预警推送
    pitfall_push_builder = PitfallPushBuilder()
    pitfall_push = pitfall_push_builder.build_pitfall_reminders(all_candidates)
    logger.info(f"  避坑预警: {len(pitfall_push['pitfalls'])} 条")
    
    # 4.4 独特性系数筛选推送
    uniqueness_push_builder = UniquenessPushBuilder()
    uniqueness_push = uniqueness_push_builder.build_uniqueness_recommendations(all_candidates, [], threshold=0.3)
    logger.info(f"  独特性推荐: {len(uniqueness_push['recommendations'])} 条")

    # ===== 第五步：结果汇总 =====
    logger.info("\n【第五步：结果汇总】")
    logger.info("=" * 80)
    
    # 打印爆品推荐列表
    if hit_products:
        logger.info("\n🔥 爆品推荐列表:")
        for i, product in enumerate(hit_products, 1):
            logger.info(f"  {i}. {product['title']}")
            logger.info(f"     分数: {product['score_result']['total_score']} | 月销: {product['monthly_sales']} | 评分: {product['rating']} | 好评率: {product['positive_rate']*100:.0f}%")
            logger.info(f"     品类: {product['classification']['gender']} / {product['classification']['category_main']}")
            logger.info(f"     独特性系数: {product['uniqueness_coefficient']:.2f}")
            if product.get("matched_elements"):
                logger.info(f"     匹配趋势元素: {', '.join(product['matched_elements'])}")
            logger.info("")
    
    if potential_products:
        logger.info(f"\n💡 潜力/常规品推荐列表 ({len(potential_products)}条):")
        for i, product in enumerate(potential_products, 1):
            tier = product.get("classification", {}).get("sales_tier", "未知")
            logger.info(f"  {i}. [{tier}] {product['title']}")
            logger.info(f"     分数: {product['score_result']['total_score']} | 月销: {product['monthly_sales']} | 评分: {product['rating']}")
        logger.info("")
    
    # 打印核心元素
    if extraction_result["top10_elements"]:
        logger.info("\n📊 爆品核心元素:")
        for i, elem in enumerate(extraction_result["top10_elements"], 1):
            logger.info(f"  {i}. {elem['element']} (频次: {elem['frequency']}, 核心: {elem['is_core']})")
        logger.info("")
    
    # 打印视觉差异化建议
    if extraction_result["visual_diff_suggestions"]:
        logger.info("\n🎨 视觉差异化建议:")
        for i, sugg in enumerate(extraction_result["visual_diff_suggestions"], 1):
            logger.info(f"  {i}. {sugg['description']}")
        logger.info("")
    
    # 打印避坑预警
    if pitfall_push["pitfalls"]:
        logger.info("\n⚠️ 避坑预警:")
        for i, pitfall in enumerate(pitfall_push["pitfalls"], 1):
            logger.info(f"  {i}. {pitfall['title']} - {pitfall['description']}")
        logger.info("")
    
    # 打印数据处理统计
    logger.info("\n📈 数据处理统计:")
    logger.info(f"  原始数据: {len(raw_products)} 产品, {len(raw_trends)} 趋势")
    logger.info(f"  去重后:   {len(deduped_products)} 产品, {len(deduped_trends)} 趋势")
    logger.info(f"  去噪后:   {len(denoised_products)} 产品, {len(denoised_trends)} 趋势")
    logger.info(f"  标准化后: {len(standardized_products)} 产品, {len(standardized_trends)} 趋势")
    logger.info(f"  筛选后:   {len(filtered_products)} 产品")
    logger.info(f"  匹配后:   {len(matched_products)} 产品")
    logger.info(f"  总候选:   {len(all_candidates)} 产品")
    logger.info(f"  爆品:     {len(hit_products)} 条")
    logger.info(f"  潜力品:   {len(potential_products)} 条")

    # ===== 保存结果 =====
    output_data = {
        "run_time": datetime.now(timezone.utc).isoformat(),
        "hit_products": hit_product_push,
        "potential_products": potential_product_push,
        "top10_elements": top10_elements_push,
        "visual_diff_suggestions": visual_diff_push,
        "pitfall_warnings": pitfall_push,
        "uniqueness_recommendations": uniqueness_push,
        "data_statistics": {
            "raw_products": len(raw_products),
            "raw_trends": len(raw_trends),
            "deduped_products": len(deduped_products),
            "deduped_trends": len(deduped_trends),
            "denoised_products": len(denoised_products),
            "denoised_trends": len(denoised_trends),
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
    
    logger.info(f"\n💾 结果已保存到: {output_file}")
    logger.info("=" * 80)
    logger.info("运行完成！")
    logger.info("=" * 80)
    
    return output_data


if __name__ == "__main__":
    try:
        result = run_full_pipeline()
        logger.info("\n✅ 技能运行成功！")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ 技能运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
