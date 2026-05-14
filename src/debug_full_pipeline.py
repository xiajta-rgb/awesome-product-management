"""调试完整pipeline - 查看标准化后的特征和趋势匹配"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processor.deduplicator import DataDeduplicator
from src.processor.denoiser import DataDenoiser
from src.processor.standardizer import DataStandardizer
from src.processor.trend_classifier import TrendClassifier
from src.algorithm.rule1_base_filter import BaseFilter
from src.algorithm.rule2_trend_match import TrendMatcher

# 从run_test_pipeline导入数据
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
from run_test_pipeline import get_mock_products, get_mock_trends

raw_products = get_mock_products()
raw_trends = get_mock_trends()

print(f"原始产品: {len(raw_products)} 条")
print(f"原始趋势: {len(raw_trends)} 条")

# 去重
deduplicator = DataDeduplicator()
deduped_products = deduplicator.deduplicate_products(raw_products)
deduped_trends = deduplicator.deduplicate_trends(raw_trends)
print(f"\n去重后: 产品 {len(deduped_products)}, 趋势 {len(deduped_trends)}")

# 去噪
denoiser = DataDenoiser()
denoised_products = denoiser.denoise_products(deduped_products)
denoised_trends = denoiser.denoise_trends(deduped_trends)
print(f"去噪后: 产品 {len(denoised_products)}, 趋势 {len(denoised_trends)}")

# 标准化
standardizer = DataStandardizer()
standardized_products = standardizer.batch_standardize_products(denoised_products)
standardized_trends = standardizer.batch_standardize_trends(denoised_trends)

print(f"\n=== 标准化产品特征 ===")
for i, p in enumerate(standardized_products):
    print(f"\n产品 {i}: {p.get('title', '')[:50]}")
    print(f"  standardized_features: {p.get('standardized_features')}")

print(f"\n=== 标准化趋势 ===")
for i, t in enumerate(standardized_trends):
    print(f"\n趋势 {i}: {t.get('element_value')}")
    print(f"  standardized_tag: {t.get('standardized_tag')}")

# 趋势分类
trend_classifier = TrendClassifier()
for t in standardized_trends:
    result = trend_classifier.classify_trend(t)
    t.update(result)
    print(f"\n趋势: {t.get('element_value')}")
    print(f"  element_type: {t.get('element_type')}")
    print(f"  standardized_tag: {t.get('standardized_tag')}")
    print(f"  heat_level: {t.get('heat_level')}")

# 基础筛选
base_filter = BaseFilter()
filtered_products = base_filter.filter(standardized_products)
print(f"\n=== 基础筛选 ===")
print(f"筛选后: {len(filtered_products)} 条")
for i, p in enumerate(filtered_products):
    print(f"  {i}: {p.get('title', '')[:50]}")
    print(f"     standardized_features: {p.get('standardized_features')}")

# 趋势匹配
matcher = TrendMatcher()
print(f"\n=== 趋势匹配 ===")
trend_elements = matcher._extract_trend_elements(standardized_trends)
print(f"提取的趋势元素: {trend_elements}")

for p in filtered_products:
    product_elements = matcher._extract_product_elements(p)
    print(f"\n产品: {p.get('title', '')[:50]}")
    print(f"  标准化特征: {p.get('standardized_features')}")
    print(f"  提取的产品元素: {product_elements}")
    
    score = matcher.calculate_match_score(p, standardized_trends)
    print(f"  匹配分数: {score}")
    print(f"  阈值: {matcher.MATCH_THRESHOLD}")
    print(f"  是否匹配: {score >= matcher.MATCH_THRESHOLD}")
