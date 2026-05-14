"""调试脚本 - 查看标准化后的数据和趋势匹配过程"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processor.deduplicator import DataDeduplicator
from src.processor.denoiser import DataDenoiser
from src.processor.standardizer import DataStandardizer
from src.processor.trend_classifier import TrendClassifier
from src.algorithm.rule1_base_filter import BaseFilter
from src.algorithm.rule2_trend_match import TrendMatcher
from src.common.ontology_engine import OntologyEngine

# 测试标准化映射
ontology = OntologyEngine()
print("=== 标签标准化测试 ===")
print(f"大地色 -> color -> {ontology.standardize_tag('大地色', 'color')}")
print(f"棉麻混纺 -> material -> {ontology.standardize_tag('棉麻混纺', 'material')}")
print(f"简约刺绣 -> design -> {ontology.standardize_tag('简约刺绣', 'design')}")
print(f"修身 -> fit -> {ontology.standardize_tag('修身', 'fit')}")

# 产品数据
sample_products = [
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
        "element_value": "简约刺绣",
        "heat_score": 75,
        "data_source": "instagram",
    },
    {
        "element_type": "fit",
        "element_value": "修身",
        "heat_score": 82,
        "data_source": "tiktok",
    },
]

print("\n=== 处理流程 ===")

# 去重
deduplicator = DataDeduplicator()
deduped_products = deduplicator.deduplicate_products(sample_products)
deduped_trends = deduplicator.deduplicate_trends(sample_trends)

# 去噪
denoiser = DataDenoiser()
denoised_products = denoiser.denoise_products(deduped_products)
denoised_trends = denoiser.denoise_trends(deduped_trends)

print(f"\n去噪后产品数: {len(denoised_products)}")
print(f"去噪后趋势数: {len(denoised_trends)}")

# 标准化
standardizer = DataStandardizer()
standardized_products = standardizer.batch_standardize_products(denoised_products)
standardized_trends = standardizer.batch_standardize_trends(denoised_trends)

print(f"\n=== 标准化产品 ===")
for p in standardized_products:
    print(f"标题: {p.get('title')}")
    print(f"standardized_features: {p.get('standardized_features')}")
    print()

print(f"\n=== 标准化趋势 ===")
for t in standardized_trends:
    print(f"element_value: {t.get('element_value')} -> standardized_tag: {t.get('standardized_tag')}")

# 趋势分类
trend_classifier = TrendClassifier()
for t in standardized_trends:
    result = trend_classifier.classify_trend(t)
    t.update(result)
    print(f"\n趋势分类: {t.get('element_value')}")
    print(f"  element_type: {t.get('element_type')}")
    print(f"  standardized_tag: {t.get('standardized_tag')}")
    print(f"  heat_level: {t.get('heat_level')}")

# 基础筛选
base_filter = BaseFilter()
filtered_products = base_filter.filter(standardized_products)
print(f"\n=== 基础筛选 ===")
print(f"筛选后: {len(filtered_products)} 条")

# 趋势匹配
matcher = TrendMatcher()
print(f"\n=== 趋势匹配调试 ===")

# 查看趋势元素
trend_elements = matcher._extract_trend_elements(standardized_trends)
print(f"提取的趋势元素: {trend_elements}")

# 查看产品元素
for p in filtered_products:
    product_elements = matcher._extract_product_elements(p)
    print(f"\n产品: {p.get('title')}")
    print(f"  标准化特征: {p.get('standardized_features')}")
    print(f"  提取的产品元素: {product_elements}")
    
    score = matcher.calculate_match_score(p, standardized_trends)
    print(f"  匹配分数: {score}")
    print(f"  阈值: {matcher.MATCH_THRESHOLD}")
    print(f"  是否匹配: {score >= matcher.MATCH_THRESHOLD}")
