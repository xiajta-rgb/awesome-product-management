"""调试脚本 - 查看标准化后的特征和趋势匹配详情"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.processor.deduplicator import DataDeduplicator
from src.processor.denoiser import DataDenoiser
from src.processor.standardizer import DataStandardizer
from src.processor.classifier import DataClassifier
from src.processor.trend_classifier import TrendClassifier
from src.algorithm.rule1_base_filter import BaseFilter
from src.algorithm.rule2_trend_match import TrendMatcher
from src.common.ontology_engine import OntologyEngine

# 测试标准化映射
print("=== 标签标准化测试 ===")
ontology = OntologyEngine()
test_tags = {
    "color": ["大地色"],
    "material": ["棉麻混纺"],
    "design": [],
    "fit": ["修身"],
}
print(f"输入标签: {test_tags}")
standardized = {}
for dim in ("color", "material", "design", "fit"):
    standardized[dim] = ontology.standardize_tags(test_tags[dim], dim)
print(f"标准化后: {standardized}")

# 简化产品数据
sample_products = [
    {
        "title": "Men's Business Casual Shirt 大地色 棉麻混纺 修身",
        "url": "https://amazon.com/product1",
        "price_range": "$29.99",
        "monthly_sales": 1200,
        "stock_status": "in_stock",
        "data_source": "amazon",
        "compliance_status": "compliant",
        "features": "修身;棉麻;大地色",
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
]

sample_trends = [
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
        "element_type": "design",
        "element_value": "反光条",
        "heat_score": 40,
        "data_source": "statista",
    },
]

print("\n=== 处理流程 ===")

# 去重
deduplicator = DataDeduplicator()
deduped_products = deduplicator.deduplicate_products(sample_products)
deduped_trends = deduplicator.deduplicate_trends(sample_trends)
print(f"去重后: 产品 {len(deduped_products)} 条, 趋势 {len(deduped_trends)} 条")

# 去噪
denoiser = DataDenoiser()
denoised_products = denoiser.denoise_products(deduped_products)
denoised_trends = denoiser.denoise_trends(deduped_trends)
print(f"去噪后: 产品 {len(denoised_products)} 条, 趋势 {len(denoised_trends)} 条")

# 标准化
standardizer = DataStandardizer()
standardized_products = standardizer.batch_standardize_products(denoised_products)
standardized_trends = standardizer.batch_standardize_trends(denoised_trends)

print("\n=== 标准化后的产品 ===")
for i, p in enumerate(standardized_products):
    print(f"产品 {i}: {p.get('title')}")
    print(f"  standardized_features: {p.get('standardized_features')}")

print("\n=== 标准化后的趋势 ===")
for i, t in enumerate(standardized_trends):
    print(f"趋势 {i}: element_value={t.get('element_value')} -> standardized_tag={t.get('standardized_tag')}")

# 趋势分类
trend_classifier = TrendClassifier()
for t in standardized_trends:
    result = trend_classifier.classify_trend(t)
    t.update(result)
    print(f"  -> element_type={t.get('element_type')}, standardized_tag={t.get('standardized_tag')}, heat_level={t.get('heat_level')}")

# 基础筛选
base_filter = BaseFilter()
filtered_products = base_filter.filter(standardized_products)
print(f"\n=== 基础筛选 ===")
print(f"筛选后: {len(filtered_products)} 条")
for i, p in enumerate(filtered_products):
    print(f"  {i}: {p.get('title')} (sales={p.get('monthly_sales')})")
    print(f"     standardized_features: {p.get('standardized_features')}")

# 趋势匹配
matcher = TrendMatcher()
print(f"\n=== 趋势匹配调试 ===")
print(f"MATCH_THRESHOLD: {matcher.MATCH_THRESHOLD}")

# 查看趋势元素提取
trend_elements = matcher._extract_trend_elements(standardized_trends)
print(f"提取的趋势元素: {trend_elements}")

# 查看每个产品的匹配
for p in filtered_products:
    print(f"\n产品: {p.get('title')}")
    product_elements = matcher._extract_product_elements(p)
    print(f"  提取的产品元素: {product_elements}")
    
    score = matcher.calculate_match_score(p, standardized_trends)
    print(f"  匹配分数: {score}")
    print(f"  阈值: {matcher.MATCH_THRESHOLD}")
    print(f"  是否匹配: {score >= matcher.MATCH_THRESHOLD}")
