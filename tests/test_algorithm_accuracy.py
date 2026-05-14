import pytest
from src.algorithm.rule1_base_filter import BaseFilter
from src.algorithm.rule2_trend_match import TrendMatcher
from src.algorithm.rule3_scorer import ProductScorer
from src.algorithm.rule4_element_extractor import ElementExtractor
from src.algorithm.rule5_optimizer import AlgorithmOptimizer


class TestRule1BaseFilter:

    def test_slow_seller_excluded(self):
        bf = BaseFilter()
        products = [
            {"monthly_sales": 50, "compliance_status": "compliant", "data_source": "amazon", "stock_status": "in_stock"},
            {"monthly_sales": 80, "compliance_status": "compliant", "data_source": "amazon", "stock_status": "in_stock"},
            {"monthly_sales": 99, "compliance_status": "compliant", "data_source": "amazon", "stock_status": "in_stock"},
        ]
        result = bf.filter(products)
        assert len(result) == 0

    def test_slow_seller_threshold(self):
        bf = BaseFilter()
        product = {
            "monthly_sales": 100,
            "compliance_status": "compliant",
            "data_source": "amazon",
            "stock_status": "in_stock",
        }
        assert bf._is_slow_seller(product) is False

    def test_high_sales_pass(self):
        bf = BaseFilter()
        products = [
            {
                "monthly_sales": 300,
                "compliance_status": "compliant",
                "data_source": "amazon",
                "stock_status": "in_stock",
            },
            {
                "monthly_sales": 500,
                "compliance_status": "compliant",
                "data_source": "amazon",
                "stock_status": "available",
            },
            {
                "monthly_sales": 1000,
                "compliance_status": "compliant",
                "data_source": "amazon",
                "stock_status": "in_stock",
            },
        ]
        result = bf.filter(products)
        assert len(result) == 3

    def test_non_compliant_excluded(self):
        bf = BaseFilter()
        products = [
            {"monthly_sales": 500, "compliance_status": "non_compliant", "data_source": "amazon", "stock_status": "in_stock"},
            {"monthly_sales": 500, "compliance_status": "严重风险", "data_source": "amazon", "stock_status": "in_stock"},
        ]
        result = bf.filter(products)
        assert len(result) == 0

    def test_unreliable_source_excluded(self):
        bf = BaseFilter()
        products = [
            {"monthly_sales": 500, "compliance_status": "compliant", "data_source": "unknown_blog", "stock_status": "in_stock"},
        ]
        result = bf.filter(products)
        assert len(result) == 0

    def test_out_of_stock_excluded(self):
        bf = BaseFilter()
        products = [
            {"monthly_sales": 500, "compliance_status": "compliant", "data_source": "amazon", "stock_status": "out_of_stock"},
        ]
        result = bf.filter(products)
        assert len(result) == 0

    def test_sales_below_300_excluded(self):
        bf = BaseFilter()
        products = [
            {"monthly_sales": 299, "compliance_status": "compliant", "data_source": "amazon", "stock_status": "in_stock"},
        ]
        result = bf.filter(products)
        assert len(result) == 0

    def test_stable_stock_pass(self):
        bf = BaseFilter()
        products = [
            {"monthly_sales": 300, "compliance_status": "compliant", "data_source": "amazon", "stock_status": "in_stock"},
            {"monthly_sales": 300, "compliance_status": "compliant", "data_source": "amazon", "stock_status": "available"},
        ]
        result = bf.filter(products)
        assert len(result) == 2


class TestRule2TrendMatch:

    def test_match_score_calculation(self):
        matcher = TrendMatcher()
        trends = [
            {"standardized_tag": "Earth Tone", "heat_level": "high"},
            {"standardized_tag": "Cotton Linen Blend", "heat_level": "high"},
            {"standardized_tag": "Slim Fit", "heat_level": "medium"},
            {"standardized_tag": "Multi Pocket", "heat_level": "中"},
        ]
        product = {
            "standardized_features": {
                "color": ["Earth Tone"],
                "material": ["Cotton Linen Blend"],
                "design": [],
                "fit": ["Slim Fit"],
            }
        }
        score = matcher.calculate_match_score(product, trends)
        # 新公式: (匹配数 / 产品元素数) * 100 = (3/3) * 100 = 100.0
        assert score == 100.0

    def test_match_threshold_80(self):
        matcher = TrendMatcher()
        trends = [
            {"standardized_tag": "Earth Tone", "heat_level": "high"},
            {"standardized_tag": "Cotton Linen Blend", "heat_level": "high"},
            {"standardized_tag": "Slim Fit", "heat_level": "medium"},
        ]
        product = {
            "standardized_features": {
                "color": ["Earth Tone"],
                "material": ["Cotton Linen Blend"],
                "design": [],
                "fit": ["Slim Fit"],
            }
        }
        score = matcher.calculate_match_score(product, trends)
        assert score >= 80.0

    def test_below_threshold_not_matched(self):
        matcher = TrendMatcher()
        trends = [
            {"standardized_tag": "Earth Tone", "heat_level": "high"},
            {"standardized_tag": "Cotton Linen Blend", "heat_level": "high"},
            {"standardized_tag": "Slim Fit", "heat_level": "medium"},
            {"standardized_tag": "Multi Pocket", "heat_level": "high"},
            {"standardized_tag": "Army Green", "heat_level": "high"},
        ]
        product = {
            "standardized_features": {
                "color": ["Earth Tone"],
                "material": ["Polyester"],
                "design": ["Print Design"],
                "fit": ["Loose Fit"],
            }
        }
        score = matcher.calculate_match_score(product, trends)
        # 新公式: 1个匹配(Earth Tone) / 4个产品元素 = 25.0
        assert score < 80.0

    def test_match_method_filters_by_threshold(self):
        matcher = TrendMatcher()
        trends = [
            {"standardized_tag": "Earth Tone", "heat_level": "high"},
            {"standardized_tag": "Cotton Linen Blend", "heat_level": "high"},
            {"standardized_tag": "Slim Fit", "heat_level": "medium"},
        ]
        products = [
            {
                "standardized_features": {
                    "color": ["Earth Tone"],
                    "material": ["Cotton Linen Blend"],
                    "design": [],
                    "fit": ["Slim Fit"],
                }
            },
            {
                "standardized_features": {
                    "color": ["Army Green"],
                    "material": [],
                    "design": [],
                    "fit": [],
                }
            },
        ]
        matched = matcher.match(products, trends)
        assert len(matched) == 1
        assert matched[0]["trend_match_score"] >= 80.0

    def test_empty_trends_zero_score(self):
        matcher = TrendMatcher()
        product = {
            "standardized_features": {
                "color": ["Earth Tone"],
                "material": [],
                "design": [],
                "fit": [],
            }
        }
        score = matcher.calculate_match_score(product, [])
        assert score == 0.0


class TestRule3Scorer:

    def test_score_formula(self):
        scorer = ProductScorer()
        product = {
            "monthly_sales": 1000,
            "trend_match_score": 100,
            "review_count": 100,
            "positive_rate": 0.95,
            "sales_rank": 5,
            "category_competitor_count": 0,
            "compliance_status": "compliant",
            "ranking_velocity": 0,
        }
        result = scorer.score(product)
        s_sales = result["s_sales"]
        s_trend = result["s_trend"]
        s_review = result["s_review"]
        s_comp = result["s_comp"]
        s_compliance = result["s_compliance"]
        raw = (s_sales * 0.3 + s_trend * 0.25 + s_review * 0.25 + s_comp * 0.1 + s_compliance * 0.1)
        max_weighted = 30.0 * 0.3 + 25.0 * 0.25 + 25.0 * 0.25 + 10.0 * 0.1 + 10.0 * 0.1
        expected = round((raw / max_weighted) * 100, 2)
        assert result["total_score"] == expected

    def test_new_product_no_review_base_15(self):
        scorer = ProductScorer()
        product = {
            "monthly_sales": 500,
            "trend_match_score": 50,
            "review_count": 0,
            "positive_rate": 0,
            "sales_rank": 50,
            "category_competitor_count": 100,
            "compliance_status": "compliant",
            "ranking_velocity": 0,
        }
        result = scorer.score(product)
        assert result["s_review"] == 15.0
        assert result["is_new_product"] is True

    def test_non_new_no_review_base_25(self):
        from datetime import datetime, timezone, timedelta
        scorer = ProductScorer()
        old_date = datetime.now(timezone.utc) - timedelta(days=60)
        product = {
            "monthly_sales": 500,
            "trend_match_score": 50,
            "review_count": 0,
            "positive_rate": 0,
            "sales_rank": 50,
            "category_competitor_count": 100,
            "compliance_status": "compliant",
            "ranking_velocity": 0,
            "listing_date": old_date,
        }
        result = scorer.score(product)
        assert result["s_review"] == 25.0

    def test_high_potential_threshold_80(self):
        scorer = ProductScorer()
        product = {
            "monthly_sales": 1000,
            "trend_match_score": 100,
            "review_count": 200,
            "positive_rate": 0.95,
            "sales_rank": 3,
            "category_competitor_count": 10,
            "compliance_status": "compliant",
            "ranking_velocity": 60,
        }
        result = scorer.score(product)
        assert result["total_score"] >= 80

    def test_potential_threshold_60_79(self):
        scorer = ProductScorer()
        product = {
            "monthly_sales": 500,
            "trend_match_score": 60,
            "review_count": 50,
            "positive_rate": 0.85,
            "sales_rank": 50,
            "category_competitor_count": 100,
            "compliance_status": "compliant",
            "ranking_velocity": 0,
        }
        result = scorer.score(product)
        assert 60 <= result["total_score"] <= 79

    def test_sales_score_levels(self):
        scorer = ProductScorer()
        assert scorer._score_sales({"monthly_sales": 1000}) == 30.0
        assert scorer._score_sales({"monthly_sales": 500}) == 25.0
        assert scorer._score_sales({"monthly_sales": 300}) == 20.0
        assert scorer._score_sales({"monthly_sales": 150}) < 20.0

    def test_trend_score_calculation(self):
        scorer = ProductScorer()
        assert scorer._score_trend({"trend_match_score": 100}) == 25.0
        assert scorer._score_trend({"trend_match_score": 80}) == 20.0
        assert scorer._score_trend({"trend_match_score": 0}) == 0.0

    def test_compliance_score(self):
        scorer = ProductScorer()
        assert scorer._score_compliance({"compliance_status": "compliant"}) == 10.0
        assert scorer._score_compliance({"compliance_status": "minor_risk"}) == 5.0
        assert scorer._score_compliance({"compliance_status": "non_compliant"}) == 0.0


class TestRule4ElementExtractor:

    def test_element_frequency_count(self):
        extractor = ElementExtractor()
        products = []
        for _ in range(25):
            products.append({
                "standardized_features": {
                    "color": ["Earth Tone"],
                    "material": ["Cotton Linen Blend"],
                    "design": ["Multi Pocket"],
                    "fit": ["Slim Fit"],
                }
            })
        for _ in range(15):
            products.append({
                "standardized_features": {
                    "color": ["Army Green"],
                    "material": ["Canvas"],
                    "design": [],
                    "fit": ["Straight Fit"],
                }
            })
        freq = extractor._count_element_frequency(products)
        assert freq.get("Earth Tone", 0) == 25
        assert freq.get("Cotton Linen Blend", 0) == 25
        assert freq.get("Multi Pocket", 0) == 25
        assert freq.get("Slim Fit", 0) == 25
        assert freq.get("Army Green", 0) == 15
        assert freq.get("Canvas", 0) == 15
        assert freq.get("Straight Fit", 0) == 15

    def test_top10_elements(self):
        extractor = ElementExtractor()
        extractor.CORE_FREQUENCY_THRESHOLD = 10
        products = []
        for _ in range(25):
            products.append({
                "standardized_features": {
                    "color": ["Earth Tone"],
                    "material": ["Cotton Linen Blend"],
                    "design": ["Multi Pocket"],
                    "fit": ["Slim Fit"],
                }
            })
        for _ in range(15):
            products.append({
                "standardized_features": {
                    "color": ["Army Green"],
                    "material": ["Canvas"],
                    "design": ["Reinforced Stitching"],
                    "fit": ["Straight Fit"],
                }
            })
        result = extractor.extract(products)
        assert len(result["top10_elements"]) <= 10
        for elem in result["top10_elements"]:
            assert "element" in elem
            assert "frequency" in elem
            assert "is_core" in elem

    def test_top10_sorted_by_frequency(self):
        extractor = ElementExtractor()
        extractor.CORE_FREQUENCY_THRESHOLD = 10
        products = []
        for _ in range(30):
            products.append({
                "standardized_features": {
                    "color": ["Earth Tone"],
                    "material": ["Cotton Linen Blend"],
                    "design": [],
                    "fit": ["Slim Fit"],
                }
            })
        for _ in range(15):
            products.append({
                "standardized_features": {
                    "color": ["Army Green"],
                    "material": [],
                    "design": [],
                    "fit": [],
                }
            })
        result = extractor.extract(products)
        if len(result["top10_elements"]) >= 2:
            assert result["top10_elements"][0]["frequency"] >= result["top10_elements"][1]["frequency"]


class TestRule5Optimizer:

    def test_weights_sum_to_one(self):
        optimizer = AlgorithmOptimizer()
        result = optimizer.optimize_weights({}, {})
        total = sum(result.values())
        assert abs(total - 1.0) < 0.01

    def test_default_weights_sum_to_one(self):
        total = sum(AlgorithmOptimizer.DEFAULT_WEIGHTS.values())
        assert abs(total - 1.0) < 0.01

    def test_season_adjusted_weights_sum_to_one(self):
        optimizer = AlgorithmOptimizer()
        result = optimizer.optimize_weights({}, {"trend_data": {"shift_intensity": "high"}})
        total = sum(result.values())
        assert abs(total - 1.0) < 0.01

    def test_medium_trend_shift_weights(self):
        optimizer = AlgorithmOptimizer()
        result = optimizer.optimize_weights({}, {"trend_data": {"shift_intensity": "medium"}})
        total = sum(result.values())
        assert abs(total - 1.0) < 0.01

    def test_low_trend_shift_weights(self):
        optimizer = AlgorithmOptimizer()
        result = optimizer.optimize_weights({}, {"trend_data": {"shift_intensity": "low"}})
        total = sum(result.values())
        assert abs(total - 1.0) < 0.01
