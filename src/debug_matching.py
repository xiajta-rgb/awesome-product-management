"""调试脚本 - 查看标准化后的数据和匹配过程"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processor.deduplicator import DataDeduplicator
from src.processor.denoiser import DataDenoiser
from src.processor.standardizer import DataStandardizer
from src.processor.trend_classifier import TrendClassifier
from src.algorithm.rule1_base_filter import BaseFilter
from src.algorithm.rule2_trend_match import TrendMatcher

sample_products = [
    {
        "title": "Men's Business Casual Shirt Earth Tone Cotton Linen Slim Fit",
        "url": "https://amazon.com/dp/B08XYZ1234",
        "price_range": "$29.99",
        "monthly_sales": 1200,
        "stock_status": "in_stock",
        "data_source": "amazon",
        "compliance_status": "compliant",
        "features": "Slim Fit;Cotton Linen;Earth Tone;Button Down",
        "tags": {"color": ["Earth Tone"], "material": ["Cotton Linen"], "design": ["Button Down"], "fit": ["Slim Fit"]},
        "review_count": 150,
        "rating": 4.5,
        "positive_rate": 0.92,
        "sales_rank": 5,
        "category_competitor_count": 30,
        "listing_date": "2024-06-15",
    },
    {
        "title": "Women's Athletic Hoodie Quick Dry Black Running",
        "url": "https://amazon.com/dp/B08ABC5678",
        "price_range": "$35.99",
        "monthly_sales": 800,
        "stock_status": "in_stock",
        "data_source": "amazon",
        "compliance_status": "compliant",
        "features": "Quick Dry;Black;Zip Up;Thumb Holes",
        "tags": {"color": ["Black"], "material": ["Quick Dry Fabric"], "design": ["Zip Up"], "fit": ["Regular"]},
        "review_count": 80,
        "rating": 4.2,
        "positive_rate": 0.85,
        "sales_rank": 20,
        "category_competitor_count": 100,
        "listing_date": "2024-08-20",
    },
]

sample_trends = [
    {
        "element_type": "color",
        "element_value": "Earth Tone",
        "heat_score": 95,
        "data_source": "google_trends",
    },
    {
        "element_type": "material",
        "element_value": "Cotton Linen",
        "heat_score": 88,
        "data_source": "pinterest",
    },
    {
        "element_type": "design",
        "element_value": "Multi Pocket",
        "heat_score": 75,
        "data_source": "instagram",
    },
    {
        "element_type": "fit",
        "element_value": "Slim Fit",
        "heat_score": 82,
        "data_source": "tiktok",
    },
]

# Step 1: 去重
deduplicator = DataDeduplicator()
deduped_products = deduplicator.deduplicate_products(sample_products)
deduped_trends = deduplicator.deduplicate_trends(sample_trends)

# Step 2: 去噪
denoiser = DataDenoiser()
denoised_products = denoiser.denoise_products(deduped_products)
denoised_trends = denoiser.denoise_trends(deduped_trends)

print("=== 去噪后的产品 ===")
for i, p in enumerate(denoised_products):
    print(f"产品 {i}: {p.get('title')}")
    print(f"  tags: {p.get('tags')}")

print("\n=== 去噪后的趋势 ===")
for i, t in enumerate(denoised_trends):
    print(f"趋势 {i}: {t.get('element_value')} (heat_score={t.get('heat_score')})")

# Step 3: 标准化
standardizer = DataStandardizer()
standardized_products = standardizer.batch_standardize_products(denoised_products)
standardized_trends = standardizer.batch_standardize_trends(denoised_trends)

print("\n=== 标准化后的产品 ===")
for i, p in enumerate(standardized_products):
    print(f"产品 {i}: {p.get('title')}")
    print(f"  standardized_features: {p.get('standardized_features')}")

print("\n=== 标准化后的趋势 ===")
for i, t in enumerate(standardized_trends):
    print(f"趋势 {i}: {t.get('element_value')} -> standardized_tag: {t.get('standardized_tag')}")

# Step 4: 趋势分类
trend_classifier = TrendClassifier()
classified_trends = []
for i, t in enumerate(standardized_trends):
    result = trend_classifier.classify_trend(t)
    t.update(result)
    classified_trends.append(t)
    print(f"\n趋势 {i} 分类结果:")
    print(f"  element_type: {t.get('element_type')}")
    print(f"  standardized_tag: {t.get('standardized_tag')}")
    print(f"  heat_level: {t.get('heat_level')}")

# Step 5: 基础筛选
base_filter = BaseFilter()
filtered_products = base_filter.filter(standardized_products)
print(f"\n=== 基础筛选结果 ===")
print(f"筛选前: {len(standardized_products)} 条")
print(f"筛选后: {len(filtered_products)} 条")
for p in filtered_products:
    print(f"  - {p.get('title')} (sales={p.get('monthly_sales')})")

# Step 6: 趋势匹配
matcher = TrendMatcher()
print(f"\n=== 趋势匹配调试 ===")

# 查看趋势元素提取
trend_elements = matcher._extract_trend_elements(classified_trends)
print(f"提取的趋势元素: {trend_elements}")

for p in filtered_products:
    print(f"\n产品: {p.get('title')}")
    product_elements = matcher._extract_product_elements(p)
    print(f"  产品元素: {product_elements}")
    
    score = matcher.calculate_match_score(p, classified_trends)
    print(f"  匹配分数: {score}")
    print(f"  阈值: {matcher.MATCH_THRESHOLD}")
    print(f"  是否匹配: {score >= matcher.MATCH_THRESHOLD}")
