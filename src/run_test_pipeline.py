"""
亚马逊美国站跨境服装电商智能选品技能 - 完整流程测试运行脚本
模拟一次完整的采集、清洗、算法分析、推送内容生成流程
"""

import json
import logging
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
from src.push.content_builder import ContentBuilder
from src.push.product_push import ProductPushBuilder
from src.push.element_push import ElementPushBuilder
from src.push.pitfall_push import PitfallPushBuilder
from src.push.uniqueness_push import UniquenessPushBuilder
from src.common.ontology_engine import OntologyEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("run_test")


def get_mock_products():
    """模拟采集到的原始产品数据（模拟爬虫结果）"""
    return [
        {
            "title": "Men's Business Casual Shirt 大地色 棉麻混纺 Slim Fit",
            "url": "https://amazon.com/dp/B08XYZ1234",
            "price_range": "$29.99",
            "monthly_sales": 1200,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "修身;棉麻混纺;大地色;简约刺绣",
            "tags": {"color": ["大地色"], "material": ["棉麻混纺"], "design": ["简约刺绣"], "fit": ["修身"]},
            "review_count": 150,
            "rating": 4.5,
            "positive_rate": 0.92,
            "sales_rank": 5,
            "category_competitor_count": 30,
            "negative_reviews": [{"content": "Runs small in chest area"}],
            "listing_date": "2024-06-15",
        },
        {
            "title": "Women's Athletic Hoodie 速干面料 黑色 Running",
            "url": "https://amazon.com/dp/B08ABC5678",
            "price_range": "$35.99",
            "monthly_sales": 800,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "速干;黑色;机能拉链;抽绳设计",
            "tags": {"color": ["黑色"], "material": ["速干面料"], "design": ["机能拉链"], "fit": ["常规版型"]},
            "review_count": 80,
            "rating": 4.2,
            "positive_rate": 0.85,
            "sales_rank": 20,
            "category_competitor_count": 100,
            "listing_date": "2024-08-20",
        },
        {
            "title": "Men's Cargo Pants 多口袋 军绿色 帆布",
            "url": "https://amazon.com/dp/B08DEF9012",
            "price_range": "$45.99",
            "monthly_sales": 500,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "多口袋;军绿色;帆布;宽松",
            "tags": {"color": ["军绿色"], "material": ["帆布"], "design": ["多口袋"], "fit": ["宽松"]},
            "review_count": 60,
            "rating": 4.0,
            "positive_rate": 0.80,
            "sales_rank": 50,
            "category_competitor_count": 200,
            "listing_date": "2024-03-10",
        },
        {
            "title": "Men's Casual T-Shirt 白色 纯棉 圆领",
            "url": "https://amazon.com/dp/B08GHI3456",
            "price_range": "$19.99",
            "monthly_sales": 50,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "纯棉;白色;圆领",
            "tags": {"color": ["白色"], "material": ["纯棉"], "design": [], "fit": ["常规版型"]},
            "review_count": 5,
            "rating": 3.5,
            "positive_rate": 0.60,
            "listing_date": "2025-01-05",
        },
        {
            "title": "Women's Business Suit 深蓝色 羊毛 修身",
            "url": "https://amazon.com/dp/B08JKL7890",
            "price_range": "$89.99",
            "monthly_sales": 350,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "羊毛;深蓝色;修身;纽扣开合",
            "tags": {"color": ["深蓝色"], "material": ["羊毛"], "design": ["纽扣开合"], "fit": ["修身"]},
            "review_count": 40,
            "rating": 4.3,
            "positive_rate": 0.88,
            "sales_rank": 30,
            "category_competitor_count": 80,
            "listing_date": "2024-05-22",
        },
        {
            "title": "Men's Hiking Boots 防水涂层 棕色 牛皮",
            "url": "https://amazon.com/dp/B08MNO1234",
            "price_range": "$69.99",
            "monthly_sales": 200,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "防水涂层;棕色;牛皮;透气设计",
            "tags": {"color": ["棕色"], "material": ["牛皮"], "design": ["透气设计"], "fit": ["常规版型"]},
            "review_count": 25,
            "rating": 4.1,
            "positive_rate": 0.82,
            "sales_rank": 80,
            "category_competitor_count": 150,
            "listing_date": "2024-07-18",
        },
        {
            "title": "Women's Athletic Shorts 薄荷绿 速干",
            "url": "https://amazon.com/dp/B08PQR5678",
            "price_range": "$24.99",
            "monthly_sales": 1500,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "速干;薄荷绿;松紧腰;侧口袋",
            "tags": {"color": ["薄荷绿"], "material": ["速干"], "design": ["松紧腰"], "fit": ["常规版型"]},
            "review_count": 200,
            "rating": 4.6,
            "positive_rate": 0.93,
            "sales_rank": 3,
            "category_competitor_count": 50,
            "listing_date": "2024-04-12",
        },
        {
            "title": "Men's Windbreaker Jacket 迷彩色 防风面料 宽松",
            "url": "https://amazon.com/dp/B08STU9012",
            "price_range": "$99.99",
            "monthly_sales": 80,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "防风面料;迷彩色;宽松;连帽设计",
            "tags": {"color": ["迷彩色"], "material": ["防风面料"], "design": ["连帽设计"], "fit": ["宽松"]},
            "review_count": 10,
            "rating": 3.8,
            "positive_rate": 0.70,
            "listing_date": "2024-09-01",
        },
        {
            "title": "Men's Business Casual Shirt 大地色 棉麻混纺 Slim Fit",
            "url": "https://amazon.com/dp/B08XYZ1234",
            "price_range": "$29.99",
            "monthly_sales": 1200,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "修身;棉麻;大地色;简约刺绣",
            "tags": {"color": ["大地色"], "material": ["棉麻混纺"], "design": ["简约刺绣"], "fit": ["修身"]},
            "review_count": 150,
            "rating": 4.5,
            "positive_rate": 0.92,
            "sales_rank": 5,
            "category_competitor_count": 30,
            "listing_date": "2024-06-15",
        },
        {
            "title": "",
            "url": "https://unknown-site.com/spam",
            "monthly_sales": 0,
            "data_source": "unknown_blog",
            "compliance_status": "compliant",
        },
        {
            "title": "Women's Yoga Leggings 高腰 紫色 弹力面料",
            "url": "https://amazon.com/dp/B08VWX3456",
            "price_range": "$32.99",
            "monthly_sales": 950,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "高腰;紫色;四向弹力;吸湿排汗",
            "tags": {"color": ["紫色"], "material": ["弹力纤维"], "design": ["高腰"], "fit": ["弹力修身"]},
            "review_count": 120,
            "rating": 4.4,
            "positive_rate": 0.90,
            "sales_rank": 12,
            "category_competitor_count": 75,
            "listing_date": "2024-02-28",
        },
    ]


def get_mock_trends():
    """模拟采集到的趋势数据（模拟趋势爬虫结果）"""
    return [
        {
            "element_type": "color",
            "element_value": "大地色",
            "heat_score": 95,
            "data_source": "google_trends",
        },
        {
            "element_type": "material",
            "element_value": "棉麻混纺",
            "heat_score": 88,
            "data_source": "pinterest",
        },
        {
            "element_type": "design",
            "element_value": "多口袋",
            "heat_score": 75,
            "data_source": "instagram",
        },
        {
            "element_type": "fit",
            "element_value": "修身",
            "heat_score": 82,
            "data_source": "tiktok",
        },
        {
            "element_type": "color",
            "element_value": "军绿色",
            "heat_score": 60,
            "data_source": "wgsn",
        },
        {
            "element_type": "material",
            "element_value": "速干面料",
            "heat_score": 70,
            "data_source": "google_trends",
        },
        {
            "element_type": "color",
            "element_value": "薄荷绿",
            "heat_score": 50,
            "data_source": "unknown_blog",
        },
        {
            "element_type": "design",
            "element_value": "高腰",
            "heat_score": 85,
            "data_source": "statista",
        },
        {
            "element_type": "color",
            "element_value": "深蓝色",
            "heat_score": 65,
            "data_source": "pinterest",
        },
        {
            "element_type": "material",
            "element_value": "羊毛",
            "heat_score": 55,
            "data_source": "wgsn",
        },
    ]


def run_full_pipeline():
    """运行完整的采集→清洗→算法→推送流程"""
    
    print("=" * 80)
    print("  亚马逊美国站跨境服装电商智能选品技能 - 完整流程测试")
    print(f"  运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # ===== 第一步：模拟数据采集 =====
    print("【第一步：数据采集】模拟爬虫采集原始数据")
    print("-" * 80)
    
    raw_products = get_mock_products()
    raw_trends = get_mock_trends()
    
    print(f"  采集产品数据: {len(raw_products)} 条")
    print(f"  采集趋势数据: {len(raw_trends)} 条")
    print()
    
    # ===== 第二步：数据清洗 =====
    print("【第二步：数据清洗与标准化】")
    print("-" * 80)
    
    # 2.1 去重
    deduplicator = DataDeduplicator()
    deduped_products = deduplicator.deduplicate_products(raw_products)
    deduped_trends = deduplicator.deduplicate_trends(raw_trends)
    print(f"  2.1 去重: 产品 {len(raw_products)} → {len(deduped_products)} 条")
    print(f"        趋势 {len(raw_trends)} → {len(deduped_trends)} 条")
    
    # 2.2 去噪
    denoiser = DataDenoiser()
    denoised_products = denoiser.denoise_products(deduped_products)
    denoised_trends = denoiser.denoise_trends(deduped_trends)
    print(f"  2.2 去噪: 产品 {len(deduped_products)} → {len(denoised_products)} 条")
    print(f"        趋势 {len(deduped_trends)} → {len(denoised_trends)} 条")
    
    # 2.3 标准化
    standardizer = DataStandardizer()
    standardized_products = standardizer.batch_standardize_products(denoised_products)
    standardized_trends = standardizer.batch_standardize_trends(denoised_trends)
    print(f"  2.3 标准化: 产品 {len(denoised_products)} 条, 趋势 {len(denoised_trends)} 条")
    
    # 2.4 合规检查
    checker = ComplianceChecker()
    for p in standardized_products:
        compliance_result = checker.check_compliance(p)
        p["compliance_check"] = compliance_result
    compliant_count = sum(1 for p in standardized_products if p["compliance_check"]["is_compliant"])
    print(f"  2.4 合规检查: {compliant_count}/{len(standardized_products)} 条合规")
    
    # 2.5 产品分类
    classifier = DataClassifier()
    for p in standardized_products:
        classification = classifier.classify_product(p)
        p["classification"] = classification
    print(f"  2.5 分类完成: 产品已按销量/性别/品类分类")
    
    # 2.6 趋势分类
    trend_classifier = TrendClassifier()
    for t in standardized_trends:
        trend_class = trend_classifier.classify_trend(t)
        t.update(trend_class)
    high_heat = sum(1 for t in standardized_trends if t.get("heat_level") == "高热度")
    print(f"  2.6 趋势分类完成: {high_heat} 条高热度趋势")
    print()
    
    # ===== 第三步：算法推荐 =====
    print("【第三步：算法推荐处理】")
    print("-" * 80)
    
    # 3.1 Rule1: 基础筛选
    base_filter = BaseFilter()
    filtered_products = base_filter.filter(standardized_products)
    print(f"  Rule1 基础筛选: {len(standardized_products)} → {len(filtered_products)} 条")
    
    # 3.2 Rule2: 趋势匹配
    matcher = TrendMatcher()
    matcher.MATCH_THRESHOLD = 40.0  # 降低阈值以演示完整流程（生产环境建议80%）
    matched_products = matcher.match(filtered_products, standardized_trends)
    print(f"  Rule2 趋势匹配: {len(matched_products)} 条产品匹配到趋势（阈值{matcher.MATCH_THRESHOLD}%）")
    
    # 3.3 Rule3: 权重打分
    scorer = ProductScorer()
    scored_products = []
    for p in matched_products:
        score_result = scorer.score(p)
        p["score_result"] = score_result
        scored_products.append(p)
    
    scored_products.sort(key=lambda x: x["score_result"]["total_score"], reverse=True)
    print(f"  Rule3 权重打分: {len(scored_products)} 条产品完成打分")
    if scored_products:
        print(f"           最高分: {scored_products[0]['score_result']['total_score']:.1f}")
        print(f"           最低分: {scored_products[-1]['score_result']['total_score']:.1f}")
    
    # 3.4 Rule4: 元素提取
    extractor = ElementExtractor()
    extraction_result = extractor.extract(scored_products)
    print(f"  Rule4 元素提取: 提取 {len(extraction_result.get('top10_elements', []))} 个核心元素")
    
    # 3.5 Rule5: 动态优化
    optimizer = AlgorithmOptimizer()
    optimization_result = optimizer.optimize_weights(scored_products, {"trend_data": {"shift_intensity": "medium"}})
    print(f"  Rule5 动态优化: 权重已优化")
    print(f"           当前权重: {optimization_result}")
    
    # 3.6 独特性计算
    calculator = UniquenessCalculator()
    uniqueness_result = {"product_count": len(scored_products), "unique_products": []}
    if scored_products:
        unique_products = calculator.filter_by_uniqueness(scored_products, [], threshold=0.7)
        uniqueness_result["unique_products"] = unique_products
        uniqueness_result["unique_count"] = len(unique_products)
    print(f"  独特性计算: 完成 {uniqueness_result.get('product_count', 0)} 个产品计算")
    print()
    
    # ===== 第四步：推送内容生成 =====
    print("【第四步：推送内容生成】")
    print("-" * 80)
    
    # 4.1 爆品推荐推送
    product_push_builder = ProductPushBuilder()
    hit_products = [p for p in scored_products if p.get("classification", {}).get("sales_tier") == "爆品"]
    potential_products = [p for p in scored_products if p.get("classification", {}).get("sales_tier") in ("潜力品", "常规品")]
    
    hit_push = product_push_builder.build_hit_product_list(hit_products)
    potential_push = product_push_builder.build_potential_product_list(potential_products)
    
    print(f"  爆品推荐: {len(hit_push.get('products', []))} 条")
    print(f"  潜力推荐: {len(potential_push.get('products', []))} 条")
    
    # 4.2 爆品元素推送
    element_push_builder = ElementPushBuilder()
    top_elements_push = element_push_builder.build_top10_elements(extraction_result.get("top10_elements", []))
    visual_diff_push = element_push_builder.build_visual_diff_suggestions(extraction_result.get("visual_diff_suggestions", []))
    
    print(f"  核心元素: {len(top_elements_push.get('elements', []))} 个")
    print(f"  视觉差异化: {len(visual_diff_push.get('suggestions', []))} 条")
    
    # 4.3 避坑预警推送
    pitfall_push_builder = PitfallPushBuilder()
    pitfall_push = pitfall_push_builder.build_pitfall_reminders(scored_products)
    print(f"  避坑预警: {len(pitfall_push.get('pitfalls', []))} 条")
    
    # 4.4 独特性推送
    uniqueness_push_builder = UniquenessPushBuilder()
    uniqueness_push = uniqueness_push_builder.build_uniqueness_recommendations(scored_products, [])
    print(f"  独特性推荐: {len(uniqueness_push.get('recommendations', []))} 条")
    
    # 4.5 内容构建器生成综合推送
    content_builder = ContentBuilder()
    market_trends = content_builder.build_market_trends(standardized_trends[:5])
    print(f"  市场趋势: {len(market_trends.get('content', []))} 条")
    print()
    
    # ===== 第五步：输出结果摘要 =====
    print("【第五步：结果摘要】")
    print("=" * 80)
    
    print("\n  爆品推荐列表 (按分数降序):")
    print("  " + "-" * 76)
    for i, p in enumerate(scored_products[:5], 1):
        title = p.get("title", "Unknown")[:50]
        score = p["score_result"]["total_score"]
        tier = p.get("classification", {}).get("sales_tier", "未知")
        sales = p.get("monthly_sales", 0)
        print(f"  {i}. [{tier}] {title}")
        print(f"     分数: {score:.1f} | 月销: {sales} | 评论: {p.get('review_count', 0)} | 评分: {p.get('rating', 0)}")
        print()
    
    print("  核心趋势元素 (Top 5):")
    print("  " + "-" * 76)
    for i, elem in enumerate(extraction_result.get("top10_elements", [])[:5], 1):
        desc = elem.get("description", "Unknown")[:50]
        print(f"  {i}. {desc}")
    print()
    
    print("  数据处理统计:")
    print("  " + "-" * 76)
    print(f"    原始采集: {len(raw_products)} 产品, {len(raw_trends)} 趋势")
    print(f"    去重后:   {len(deduped_products)} 产品, {len(deduped_trends)} 趋势")
    print(f"    去噪后:   {len(denoised_products)} 产品, {len(denoised_trends)} 趋势")
    print(f"    筛选后:   {len(filtered_products)} 产品")
    print(f"    最终推荐: {len(scored_products)} 产品")
    print()
    
    print("=" * 80)
    print("  测试运行完成！")
    print("=" * 80)
    
    # 保存结果到JSON文件
    output = {
        "run_time": datetime.now().isoformat(),
        "pipeline_summary": {
            "raw_products": len(raw_products),
            "raw_trends": len(raw_trends),
            "deduped_products": len(deduped_products),
            "deduped_trends": len(deduped_trends),
            "denoised_products": len(denoised_products),
            "denoised_trends": len(denoised_trends),
            "filtered_products": len(filtered_products),
            "scored_products": len(scored_products),
        },
        "top_products": [
            {
                "title": p.get("title"),
                "score": p["score_result"]["total_score"],
                "sales_tier": p.get("classification", {}).get("sales_tier"),
                "monthly_sales": p.get("monthly_sales"),
                "rating": p.get("rating"),
            }
            for p in scored_products[:5]
        ],
        "top_elements": extraction_result.get("top10_elements", [])[:5],
    }
    
    output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "run_result.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n  结果已保存到: {output_file}")
    
    return output


if __name__ == "__main__":
    try:
        result = run_full_pipeline()
        print("\n运行成功！")
        sys.exit(0)
    except Exception as e:
        logger.error(f"运行失败: {str(e)}", exc_info=True)
        sys.exit(1)
