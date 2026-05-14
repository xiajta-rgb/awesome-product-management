import pytest
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


@pytest.fixture
def sample_products():
    return [
        {
            "title": "男士商务休闲衬衫 大地色 棉麻混纺 修身",
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
        },
        {
            "title": "女士运动卫衣 速干面料 黑色",
            "url": "https://amazon.com/product2",
            "price_range": "$35.99",
            "monthly_sales": 800,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "速干;黑色",
            "tags": {"color": ["黑色"], "material": ["速干面料"], "design": [], "fit": []},
            "review_count": 80,
            "rating": 4.2,
            "positive_rate": 0.85,
            "sales_rank": 20,
            "category_competitor_count": 100,
        },
        {
            "title": "男士工装裤 多口袋 军绿色 帆布",
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
        },
        {
            "title": "男士休闲T恤 白色 纯棉 直筒",
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
        },
        {
            "title": "女士商务西装套 深蓝色 羊毛 修身",
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
        },
        {
            "title": "男士登山鞋 防水涂层 棕色",
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
        },
        {
            "title": "女士运动短裤 薄荷绿 速干",
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
        },
        {
            "title": "男士防风冲锋衣 迷彩色 防风面料 宽松",
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
        },
        {
            "title": "男士商务休闲衬衫 大地色 棉麻混纺 修身",
            "url": "https://amazon.com/product1",
            "price_range": "$29.99",
            "monthly_sales": 1200,
            "stock_status": "in_stock",
            "data_source": "amazon",
            "compliance_status": "compliant",
            "features": "修身;棉麻;大地色",
            "tags": {"color": ["大地色"], "material": ["棉麻混纺"], "design": [], "fit": ["修身"]},
        },
        {
            "title": "",
            "url": "https://amazon.com/spam",
            "monthly_sales": 0,
            "data_source": "unknown_source",
            "compliance_status": "compliant",
        },
    ]


@pytest.fixture
def sample_trends():
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
            "element_value": "反光条",
            "heat_score": 40,
            "data_source": "statista",
        },
    ]


class TestE2EPipeline:

    def test_deduplication(self, sample_products):
        deduplicator = DataDeduplicator()
        result = deduplicator.deduplicate_products(sample_products)
        assert len(result) == 9
        titles = [p["title"] for p in result]
        assert titles.count("男士商务休闲衬衫 大地色 棉麻混纺 修身") == 1

    def test_denoising(self, sample_products):
        deduplicator = DataDeduplicator()
        deduped = deduplicator.deduplicate_products(sample_products)
        denoiser = DataDenoiser()
        result = denoiser.denoise_products(deduped)
        assert len(result) < len(deduped)
        for p in result:
            assert p.get("title", "").strip() != ""
            assert len(p.get("title", "").strip()) >= 3
            assert p.get("monthly_sales", 0) != 0
            source = p.get("data_source", "").lower()
            from src.processor.denoiser import RELIABLE_SOURCES
            assert source in {s.lower() for s in RELIABLE_SOURCES}

    def test_denoising_trends(self, sample_trends):
        denoiser = DataDenoiser()
        result = denoiser.denoise_trends(sample_trends)
        for t in result:
            source = t.get("data_source", "").lower()
            from src.processor.denoiser import RELIABLE_SOURCES
            assert source in {s.lower() for s in RELIABLE_SOURCES}

    def test_standardization(self, sample_products):
        deduplicator = DataDeduplicator()
        deduped = deduplicator.deduplicate_products(sample_products)
        denoiser = DataDenoiser()
        denoised = denoiser.denoise_products(deduped)
        standardizer = DataStandardizer()
        result = standardizer.batch_standardize_products(denoised)
        assert len(result) == len(denoised)
        for p in result:
            assert "standardized_features" in p
            sf = p["standardized_features"]
            assert isinstance(sf, dict)
            assert "color" in sf
            assert "material" in sf
            assert "design" in sf
            assert "fit" in sf

    def test_compliance_check(self, sample_products):
        deduplicator = DataDeduplicator()
        deduped = deduplicator.deduplicate_products(sample_products)
        denoiser = DataDenoiser()
        denoised = denoiser.denoise_products(deduped)
        standardizer = DataStandardizer()
        standardized = standardizer.batch_standardize_products(denoised)
        checker = ComplianceChecker()
        for p in standardized:
            result = checker.check_compliance(p)
            assert "is_compliant" in result
            assert "issues" in result
            assert "risk_level" in result
            assert isinstance(result["is_compliant"], bool)
            assert isinstance(result["issues"], list)
            assert result["risk_level"] in ("low", "medium", "high")

    def test_classification(self, sample_products):
        deduplicator = DataDeduplicator()
        deduped = deduplicator.deduplicate_products(sample_products)
        denoiser = DataDenoiser()
        denoised = denoiser.denoise_products(deduped)
        standardizer = DataStandardizer()
        standardized = standardizer.batch_standardize_products(denoised)
        classifier = DataClassifier()
        for p in standardized:
            result = classifier.classify_product(p)
            assert "sales_tier" in result
            assert "gender" in result
            assert "category_main" in result
            assert "category_sub" in result
            assert "pain_points" in result
            assert result["sales_tier"] in ("爆品", "潜力品", "常规品", "滞销品")

    def test_trend_classification(self, sample_trends):
        denoiser = DataDenoiser()
        denoised = denoiser.denoise_trends(sample_trends)
        standardizer = DataStandardizer()
        standardized = standardizer.batch_standardize_trends(denoised)
        tc = TrendClassifier()
        for t in standardized:
            result = tc.classify_trend(t)
            assert "element_type" in result
            assert "standardized_tag" in result
            assert "trend_cycle" in result
            assert "heat_level" in result
            assert result["heat_level"] in ("高热度", "中热度", "低热度")

    def test_rule1_base_filter(self, sample_products):
        deduplicator = DataDeduplicator()
        deduped = deduplicator.deduplicate_products(sample_products)
        denoiser = DataDenoiser()
        denoised = denoiser.denoise_products(deduped)
        standardizer = DataStandardizer()
        standardized = standardizer.batch_standardize_products(denoised)
        base_filter = BaseFilter()
        filtered = base_filter.filter(standardized)
        for p in filtered:
            assert p.get("monthly_sales", 0) >= 300
            assert p.get("stock_status", "") in ("in_stock", "available")
            assert p.get("compliance_status", "") == "compliant"

    def test_rule2_trend_match(self, sample_products, sample_trends):
        deduplicator = DataDeduplicator()
        deduped = deduplicator.deduplicate_products(sample_products)
        denoiser = DataDenoiser()
        denoised = denoiser.denoise_products(deduped)
        standardizer = DataStandardizer()
        standardized = standardizer.batch_standardize_products(denoised)
        base_filter = BaseFilter()
        filtered = base_filter.filter(standardized)

        denoised_trends = denoiser.denoise_trends(sample_trends)
        standardized_trends = standardizer.batch_standardize_trends(denoised_trends)
        tc = TrendClassifier()
        classified_trends = [tc.classify_trend(t) for t in standardized_trends]
        for i, t in enumerate(standardized_trends):
            t.update(classified_trends[i])

        matcher = TrendMatcher()
        matched = matcher.match(filtered, standardized_trends)
        for p in matched:
            assert p.get("trend_match_score", 0) >= 80.0

    def test_rule3_scorer(self, sample_products, sample_trends):
        deduplicator = DataDeduplicator()
        deduped = deduplicator.deduplicate_products(sample_products)
        denoiser = DataDenoiser()
        denoised = denoiser.denoise_products(deduped)
        standardizer = DataStandardizer()
        standardized = standardizer.batch_standardize_products(denoised)
        base_filter = BaseFilter()
        filtered = base_filter.filter(standardized)

        denoised_trends = denoiser.denoise_trends(sample_trends)
        standardized_trends = standardizer.batch_standardize_trends(denoised_trends)
        tc = TrendClassifier()
        classified_trends = [tc.classify_trend(t) for t in standardized_trends]
        for i, t in enumerate(standardized_trends):
            t.update(classified_trends[i])

        matcher = TrendMatcher()
        matched = matcher.match(filtered, standardized_trends)

        scorer = ProductScorer()
        for p in matched:
            result = scorer.score(p)
            assert "total_score" in result
            assert "s_sales" in result
            assert "s_trend" in result
            assert "s_review" in result
            assert "s_comp" in result
            assert "s_compliance" in result
            assert isinstance(result["total_score"], float)
            assert 0 <= result["total_score"] <= 100

    def test_rule4_element_extractor(self, sample_products, sample_trends):
        deduplicator = DataDeduplicator()
        deduped = deduplicator.deduplicate_products(sample_products)
        denoiser = DataDenoiser()
        denoised = denoiser.denoise_products(deduped)
        standardizer = DataStandardizer()
        standardized = standardizer.batch_standardize_products(denoised)
        base_filter = BaseFilter()
        filtered = base_filter.filter(standardized)

        denoised_trends = denoiser.denoise_trends(sample_trends)
        standardized_trends = standardizer.batch_standardize_trends(denoised_trends)
        tc = TrendClassifier()
        classified_trends = [tc.classify_trend(t) for t in standardized_trends]
        for i, t in enumerate(standardized_trends):
            t.update(classified_trends[i])

        matcher = TrendMatcher()
        matched = matcher.match(filtered, standardized_trends)

        extractor = ElementExtractor()
        result = extractor.extract(matched)
        assert "top10_elements" in result
        assert "visual_diff_suggestions" in result
        assert isinstance(result["top10_elements"], list)
        assert len(result["top10_elements"]) <= 10

    def test_full_pipeline_counts(self, sample_products, sample_trends):
        deduplicator = DataDeduplicator()
        deduped = deduplicator.deduplicate_products(sample_products)
        assert len(deduped) < len(sample_products)

        denoiser = DataDenoiser()
        denoised = denoiser.denoise_products(deduped)
        assert len(denoised) <= len(deduped)

        standardizer = DataStandardizer()
        standardized = standardizer.batch_standardize_products(denoised)
        assert len(standardized) == len(denoised)

        base_filter = BaseFilter()
        filtered = base_filter.filter(standardized)
        assert len(filtered) <= len(standardized)

        denoised_trends = denoiser.denoise_trends(sample_trends)
        standardized_trends = standardizer.batch_standardize_trends(denoised_trends)
        tc = TrendClassifier()
        classified_trends = [tc.classify_trend(t) for t in standardized_trends]
        for i, t in enumerate(standardized_trends):
            t.update(classified_trends[i])

        matcher = TrendMatcher()
        matched = matcher.match(filtered, standardized_trends)
        assert len(matched) <= len(filtered)

        scorer = ProductScorer()
        scored = []
        for p in matched:
            score_result = scorer.score(p)
            p["score_result"] = score_result
            scored.append(p)
        assert len(scored) == len(matched)

        extractor = ElementExtractor()
        extraction_result = extractor.extract(scored)
        assert isinstance(extraction_result, dict)
