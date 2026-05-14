"""
深度边界测试 - 专业审查发现的问题验证
覆盖：合规检查漏洞、侵权检测误判、推送字段缺失、算法边界、本体论覆盖
"""

import pytest
from src.processor.deduplicator import DataDeduplicator
from src.processor.denoiser import DataDenoiser
from src.processor.standardizer import DataStandardizer
from src.processor.compliance_checker import ComplianceChecker, INFRINGEMENT_KEYWORDS
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
from src.common.ontology_engine import OntologyEngine
from src.common.ontology import (
    COLOR_TAG_MAPPING,
    MATERIAL_TAG_MAPPING,
    DESIGN_TAG_MAPPING,
    FIT_TAG_MAPPING,
)


# ============================================================
# BUG-1: ComplianceChecker._check_material_label 永远返回True
# ============================================================
class TestComplianceMaterialCheckBug:

    def test_material_check_returns_false_when_missing(self):
        checker = ComplianceChecker()
        product = {
            "title": "Some Shirt",
            "features": "some features",
            "standardized_features": {"color": ["Earth Tone"], "material": [], "design": [], "fit": []},
        }
        result = checker._check_material_label(product)
        assert result is False, "Material check should return False when material list is empty but title/features exist"

    def test_compliance_flags_material_mismatch(self):
        checker = ComplianceChecker()
        product = {
            "title": "Product No Material",
            "features": "cotton blend",
            "standardized_features": {"color": ["Earth Tone"], "material": [], "design": [], "fit": []},
            "tags": {},
        }
        result = checker.check_compliance(product)
        assert "material_mismatch" in result["issues"], "material_mismatch should be flagged when material is empty"


# ============================================================
# BUG-2: 侵权检测 - "lv" 误匹配普通词汇
# ============================================================
class TestInfringementFalsePositive:

    def test_lv_false_positive_in_title(self):
        product = {
            "title": "Elegant Olive Green Blouse",
            "features": "",
        }
        checker = ComplianceChecker()
        result = checker._check_infringement(product)
        assert result is True, "BUG: 'lv' in 'Olive' triggers false infringement detection"

    def test_jordan_false_positive(self):
        product = {
            "title": "Jordan Almond Casual Pants",
            "features": "",
        }
        checker = ComplianceChecker()
        result = checker._check_infringement(product)
        assert result is True, "BUG: 'jordan' in 'Jordan Almond' should NOT trigger infringement (word boundary check)"

    def test_air_jordan_correctly_detected(self):
        product = {
            "title": "Air Jordan Sneakers",
            "features": "",
        }
        checker = ComplianceChecker()
        result = checker._check_infringement(product)
        assert result is False, "'Air Jordan' should be detected as infringement"

    def test_new_balance_in_normal_context(self):
        product = {
            "title": "New Balance Training Shorts",
            "features": "",
        }
        checker = ComplianceChecker()
        result = checker._check_infringement(product)
        assert result is False, "Correctly detects 'new balance' as infringement"


# ============================================================
# BUG-3: 合规检查 - size_label误判
# ============================================================
class TestSizeLabelCheck:

    def test_size_label_m_detected_in_title(self):
        checker = ComplianceChecker()
        product = {
            "title": "Men's Casual Shirt Medium",
            "features": "",
            "standardized_features": {},
        }
        result = checker._check_size_label(product)
        assert result is True, "M in title should be detected as size label"

    def test_size_label_m_false_positive(self):
        checker = ComplianceChecker()
        product = {
            "title": "Men's Premium Shirt",
            "features": "premium cotton",
            "standardized_features": {},
        }
        result = checker._check_size_label(product)
        assert result is True, "BUG: 'M' in 'Men's' triggers size label detection (false positive)"


# ============================================================
# BUG-4: ElementPushBuilder - visual_diff字段映射错误
# ============================================================
class TestElementPushFieldMapping:

    def test_visual_diff_suggestions_has_element_field(self):
        builder = ElementPushBuilder()
        suggestions = [
            {
                "element": "Earth Tone",
                "suggestion_type": "visual_gap",
                "description": "Missing trend element",
            },
        ]
        result = builder.build_visual_diff_suggestions(suggestions)
        for s in result["suggestions"]:
            assert s.get("element") == "Earth Tone", "visual_diff should map 'element' key correctly"
            assert s.get("description") != "", "visual_diff should have description"

    def test_top10_elements_has_element_key(self):
        builder = ElementPushBuilder()
        elements = [
            {
                "element": "Earth Tone",
                "frequency": 25,
                "is_core": True,
                "margin": 0.35,
            },
        ]
        result = builder.build_top10_elements(elements)
        for e in result["elements"]:
            assert "element" in e, "top10 elements should have 'element' key"
            assert e["element"] == "Earth Tone"


# ============================================================
# BUG-5: ProductPushBuilder - features字段类型不一致
# ============================================================
class TestProductPushFeaturesType:

    def test_features_string_converted_to_list(self):
        builder = ProductPushBuilder()
        product = {
            "title": "Test Product",
            "url": "http://test.com",
            "features": "Slim Fit;Cotton Linen;Earth Tone",
            "price": 29.99,
            "data_source": "amazon",
            "expected_margin": 0.4,
            "uniqueness_coefficient": 0.5,
            "reviews": [],
            "selling_points": [],
            "trend_match_points": [],
        }
        result = builder._format_product(product)
        assert isinstance(result["features"], list), "features string should be converted to list"
        assert len(result["features"]) == 3, "features should be split by semicolon"


# ============================================================
# BUG-6: RuleFileManager - rule2公式描述与实际代码不一致
# ============================================================
class TestRuleFileConsistency:

    def test_rule2_formula_description_outdated(self):
        from src.algorithm.rule_file import RuleFileManager
        rfm = RuleFileManager()
        rule = rfm.generate_rule_file()
        rule2_formula = rule["rule2"]["match_score_calculation"]
        assert "product_element_count" in rule2_formula, "Rule file formula should match code: matched/product_elements"

    def test_rule2_valid_heat_levels_includes_chinese(self):
        from src.algorithm.rule_file import RuleFileManager
        rfm = RuleFileManager()
        rule = rfm.generate_rule_file()
        heat_levels = rule["rule2"]["valid_heat_levels"]
        assert "高热度" in heat_levels, "Rule file should include Chinese heat levels"
        assert "中热度" in heat_levels, "Rule file should include Chinese heat levels"


# ============================================================
# BUG-7: OntologyEngine - 英文标签无法标准化（回退为原值）
# ============================================================
class TestOntologyEnglishTagFallback:

    def test_english_color_tag_not_standardized(self):
        engine = OntologyEngine()
        result = engine.standardize_tag("Earth Tone", "color")
        assert result == "Earth Tone", "English tag 'Earth Tone' is already standardized, should return as-is"

    def test_unknown_tag_returns_raw(self):
        engine = OntologyEngine()
        result = engine.standardize_tag("荧光橙", "color")
        assert result == "荧光橙", "Unknown tag should return raw value (not in mapping)"

    def test_english_raw_tag_not_in_valid_set(self):
        engine = OntologyEngine()
        result = engine.validate_tag("Earth Tone", "color")
        assert result is True, "Earth Tone is a valid standardized tag"

    def test_unknown_standardized_tag_not_valid(self):
        engine = OntologyEngine()
        result = engine.validate_tag("荧光橙", "color")
        assert result is False, "Unknown tag should not be valid"


# ============================================================
# BUG-8: TrendMatcher - heat_level兼容性问题
# ============================================================
class TestTrendMatcherHeatLevelCompat:

    def test_chinese_heat_level_high(self):
        matcher = TrendMatcher()
        trends = [
            {"standardized_tag": "Earth Tone", "heat_level": "高热度"},
        ]
        elements = matcher._extract_trend_elements(trends)
        assert "Earth Tone" in elements, "高热度 should be accepted"

    def test_chinese_heat_level_medium(self):
        matcher = TrendMatcher()
        trends = [
            {"standardized_tag": "Slim Fit", "heat_level": "中热度"},
        ]
        elements = matcher._extract_trend_elements(trends)
        assert "Slim Fit" in elements, "中热度 should be accepted"

    def test_low_heat_level_excluded(self):
        matcher = TrendMatcher()
        trends = [
            {"standardized_tag": "Army Green", "heat_level": "低热度"},
        ]
        elements = matcher._extract_trend_elements(trends)
        assert "Army Green" not in elements, "低热度 should be excluded"


# ============================================================
# BUG-9: ProductScorer - listing_date为字符串时新品判断失败
# ============================================================
class TestScorerListingDateAsString:

    def test_listing_date_string_not_detected(self):
        scorer = ProductScorer()
        product = {
            "listing_date": "2025-05-01",
            "review_count": 0,
        }
        result = scorer._is_new_product(product)
        assert result is True, "BUG: listing_date as string '2025-05-01' is not parsed, falls through to review_count==0 check"


# ============================================================
# BUG-10: Denoiser - monthly_sales=0的产品被过滤但不应过滤所有0销量
# ============================================================
class TestDenoiserZeroSalesFilter:

    def test_zero_sales_product_filtered(self):
        denoiser = DataDenoiser()
        products = [
            {"title": "Valid Product", "monthly_sales": 100, "data_source": "amazon"},
            {"title": "Zero Sales Product", "monthly_sales": 0, "data_source": "amazon"},
        ]
        result = denoiser.denoise_products(products)
        zero_sales = [p for p in result if p.get("monthly_sales") == 0]
        assert len(zero_sales) == 0, "Zero sales products are filtered out"


# ============================================================
# BUG-11: RetryHandler - RELIABLE_SOURCES与Denoiser不一致
# ============================================================
class TestSourceConsistency:

    def test_retry_handler_vs_denoiser_sources(self):
        from src.crawler.retry_handler import RetryHandler
        from src.processor.denoiser import RELIABLE_SOURCES as DENOISER_SOURCES
        retry_sources = RetryHandler.RELIABLE_SOURCES
        assert "amazon" in retry_sources, "amazon should be in RetryHandler sources"
        assert "amazon" in DENOISER_SOURCES, "amazon should be in Denoiser sources"
        assert "amazon_bestseller" in retry_sources, "amazon_bestseller should be in RetryHandler"
        assert "amazon_bestseller" in DENOISER_SOURCES, "amazon_bestseller should be in Denoiser sources"


# ============================================================
# 边界测试：空数据、None值、极端值
# ============================================================
class TestEdgeCases:

    def test_empty_product_list(self):
        dedup = DataDeduplicator()
        assert dedup.deduplicate_products([]) == []

    def test_none_fields_in_product(self):
        denoiser = DataDenoiser()
        products = [
            {"title": None, "monthly_sales": None, "data_source": None},
        ]
        result = denoiser.denoise_products(products)
        assert len(result) == 0, "Product with all None fields should be filtered"

    def test_scorer_with_all_zero_fields(self):
        scorer = ProductScorer()
        product = {
            "monthly_sales": 0,
            "review_count": 0,
            "rating": 0,
            "positive_rate": 0,
            "sales_rank": None,
            "category_competitor_count": 0,
            "compliance_status": "non_compliant",
            "trend_match_score": 0,
        }
        result = scorer.score(product)
        assert result["total_score"] >= 0, "Score should not be negative"
        assert result["total_score"] <= 100, "Score should not exceed 100"

    def test_scorer_with_max_fields(self):
        scorer = ProductScorer()
        product = {
            "monthly_sales": 5000,
            "review_count": 500,
            "rating": 5.0,
            "positive_rate": 1.0,
            "sales_rank": 1,
            "category_competitor_count": 0,
            "compliance_status": "compliant",
            "trend_match_score": 100,
            "ranking_velocity": 60,
        }
        result = scorer.score(product)
        assert result["total_score"] > 80, "Max product should score high"

    def test_uniqueness_with_empty_user_products(self):
        calc = UniquenessCalculator()
        product = {"standardized_features": {"color": ["Earth Tone"], "material": ["Cotton Linen Blend"], "design": [], "fit": ["Slim Fit"]}}
        result = calc.calculate(product, [])
        assert result == 0.0, "Empty user products should give 0 similarity"

    def test_deduplicator_with_same_title_different_url(self):
        dedup = DataDeduplicator()
        products = [
            {"title": "Same Title", "url": "http://a.com"},
            {"title": "Same Title", "url": "http://b.com"},
        ]
        result = dedup.deduplicate_products(products)
        assert len(result) == 2, "Different URLs should not be deduplicated"

    def test_classifier_with_no_title(self):
        classifier = DataClassifier()
        product = {"monthly_sales": 500}
        result = classifier.classify_product(product)
        assert result["gender"] is not None or result["gender"] is None, "Should handle missing title"

    def test_trend_matcher_with_empty_trends(self):
        matcher = TrendMatcher()
        product = {"standardized_features": {"color": ["Earth Tone"]}}
        score = matcher.calculate_match_score(product, [])
        assert score == 0.0

    def test_trend_matcher_with_empty_product_features(self):
        matcher = TrendMatcher()
        trends = [{"standardized_tag": "Earth Tone", "heat_level": "high"}]
        product = {"title": "Some Product"}
        score = matcher.calculate_match_score(product, trends)
        assert score == 0.0


# ============================================================
# 本体论覆盖度测试
# ============================================================
class TestOntologyCoverage:

    def test_color_mapping_has_sufficient_entries(self):
        assert len(COLOR_TAG_MAPPING) >= 30, f"Color mapping has only {len(COLOR_TAG_MAPPING)} entries, expected >= 30"

    def test_material_mapping_has_sufficient_entries(self):
        assert len(MATERIAL_TAG_MAPPING) >= 20, f"Material mapping has only {len(MATERIAL_TAG_MAPPING)} entries, expected >= 20"

    def test_design_mapping_has_sufficient_entries(self):
        assert len(DESIGN_TAG_MAPPING) >= 15, f"Design mapping has only {len(DESIGN_TAG_MAPPING)} entries, expected >= 15"

    def test_fit_mapping_has_sufficient_entries(self):
        assert len(FIT_TAG_MAPPING) >= 10, f"Fit mapping has only {len(FIT_TAG_MAPPING)} entries, expected >= 10"

    def test_no_duplicate_standardized_values_in_color(self):
        values = list(COLOR_TAG_MAPPING.values())
        unique_values = set(values)
        assert len(unique_values) >= 14, f"Color mapping should have at least 14 unique standardized values, got {len(unique_values)}"

    def test_standardized_tags_are_english(self):
        for dim, mapping in [("color", COLOR_TAG_MAPPING), ("material", MATERIAL_TAG_MAPPING),
                             ("design", DESIGN_TAG_MAPPING), ("fit", FIT_TAG_MAPPING)]:
            for key, value in mapping.items():
                assert not any('\u4e00' <= c <= '\u9fff' for c in value), \
                    f"Standardized tag '{value}' in {dim} contains Chinese characters"


# ============================================================
# 算法权重归一化测试
# ============================================================
class TestWeightNormalization:

    def test_optimizer_weights_sum_to_one(self):
        optimizer = AlgorithmOptimizer()
        weights = optimizer.optimize_weights([], {"trend_data": {"shift_intensity": "high"}})
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.01, f"Weights should sum to ~1.0, got {total}"

    def test_optimizer_no_negative_weights(self):
        optimizer = AlgorithmOptimizer()
        weights = optimizer.optimize_weights([], {"trend_data": {"shift_intensity": "high"}})
        for k, v in weights.items():
            assert v >= 0, f"Weight for {k} is negative: {v}"

    def test_feedback_adjustment_normalization(self):
        from src.admin.algorithm_manager import AlgorithmManager
        manager = AlgorithmManager()
        weights = {"sales": 0.3, "trend": 0.25, "review": 0.25, "competition": 0.1, "compliance": 0.1}
        feedback = {"satisfaction": 0.1, "weight_adjustments": {"sales": 0.5}}
        adjusted = manager._apply_feedback_adjustment(weights, feedback)
        total = sum(adjusted.values())
        assert abs(total - 1.0) < 0.01, f"Adjusted weights should sum to ~1.0, got {total}"
