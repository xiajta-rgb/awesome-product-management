import pytest
from src.processor.denoiser import DataDenoiser, RELIABLE_SOURCES
from src.algorithm.rule1_base_filter import BaseFilter
from src.push.product_push import ProductPushBuilder
from src.push.element_push import ElementPushBuilder
from src.push.pitfall_push import PitfallPushBuilder


class TestDataSourceField:

    def test_hit_product_push_has_data_source(self):
        builder = ProductPushBuilder()
        products = [
            {"title": "test", "url": "http://a.com", "features": {}, "price": 10.0, "data_source": "amazon", "expected_margin": 0.4, "uniqueness_coefficient": 0.5, "reviews": [{"content": "good"}], "selling_points": [], "trend_match_points": []},
        ]
        result = builder.build_hit_product_list(products)
        for p in result["products"]:
            assert "data_source" in p

    def test_potential_product_push_has_data_source(self):
        builder = ProductPushBuilder()
        products = [
            {"title": "test", "url": "http://a.com", "features": {}, "price": 10.0, "data_source": "amazon", "expected_margin": 0.4, "uniqueness_coefficient": 0.5, "reviews": [], "selling_points": [], "trend_match_points": [], "growth_potential": "high", "supply_chain_feasibility": "medium"},
        ]
        result = builder.build_potential_product_list(products)
        for p in result["products"]:
            assert "data_source" in p

    def test_top10_elements_push_has_data_source(self):
        builder = ElementPushBuilder()
        elements = [
            {"description": "test", "application_scene": "scene", "matched_category": "cat", "data_source": "google_trends", "standardized_tags": ["tag1"]},
        ]
        result = builder.build_top10_elements(elements)
        for e in result["elements"]:
            assert "data_source" in e

    def test_element_matching_push_has_data_source(self):
        builder = ElementPushBuilder()
        elements = [
            {"matched_category": "cat", "combination": "combo", "target_audience": "aud", "description": "desc", "data_source": "pinterest"},
        ]
        result = builder.build_element_matching_suggestions(elements)
        for s in result["suggestions"]:
            assert "data_source" in s

    def test_visual_diff_push_has_data_source(self):
        builder = ElementPushBuilder()
        suggestions = [
            {"visual_element": "elem", "differentiation_strategy": "strat", "reference_examples": [], "data_source": "instagram"},
        ]
        result = builder.build_visual_diff_suggestions(suggestions)
        for s in result["suggestions"]:
            assert "data_source" in s

    def test_pitfall_push_has_data_source(self):
        builder = PitfallPushBuilder()
        products = [
            {
                "title": "test product",
                "data_source": "amazon",
                "reviews": [{"pain_points": ["Size Too Small"]}],
            },
        ]
        result = builder.build_pitfall_reminders(products)
        for pitfall in result["pitfalls"]:
            assert "data_source" in pitfall


class TestUnreliableSourceFiltered:

    def test_denoiser_filters_unreliable_product_source(self):
        denoiser = DataDenoiser()
        products = [
            {"title": "Valid Product", "monthly_sales": 100, "data_source": "amazon"},
            {"title": "Invalid Product", "monthly_sales": 100, "data_source": "random_blog"},
            {"title": "No Source Product", "monthly_sales": 100, "data_source": ""},
        ]
        result = denoiser.denoise_products(products)
        sources = [p.get("data_source", "").lower() for p in result]
        assert "random_blog" not in sources

    def test_denoiser_filters_unreliable_trend_source(self):
        denoiser = DataDenoiser()
        trends = [
            {"element_value": "Earth Tone", "data_source": "google_trends"},
            {"element_value": "Slim Fit", "data_source": "unknown_site"},
        ]
        result = denoiser.denoise_trends(trends)
        assert len(result) == 1
        assert result[0]["data_source"] == "google_trends"

    def test_rule1_filters_unreliable_source(self):
        bf = BaseFilter()
        products = [
            {"monthly_sales": 500, "compliance_status": "compliant", "data_source": "amazon", "stock_status": "in_stock"},
            {"monthly_sales": 500, "compliance_status": "compliant", "data_source": "random_blog", "stock_status": "in_stock"},
        ]
        result = bf.filter(products)
        assert len(result) == 1
        assert result[0]["data_source"] == "amazon"

    def test_empty_source_filtered_by_rule1(self):
        bf = BaseFilter()
        products = [
            {"monthly_sales": 500, "compliance_status": "compliant", "data_source": "", "stock_status": "in_stock"},
        ]
        result = bf.filter(products)
        assert len(result) == 0


class TestSourceReliabilityCheck:

    def test_reliable_sources_set(self):
        expected = {"amazon_bestseller", "amazon", "google_trends", "pinterest", "statista", "instagram", "tiktok", "wgsn"}
        assert RELIABLE_SOURCES == expected

    def test_reliable_source_accepted(self):
        denoiser = DataDenoiser()
        for source in RELIABLE_SOURCES:
            trends = [{"element_value": "test", "data_source": source}]
            result = denoiser.denoise_trends(trends)
            assert len(result) == 1

    def test_unreliable_source_rejected(self):
        denoiser = DataDenoiser()
        unreliable_sources = ["random_blog", "unknown_site", "fake_data", "spam_source"]
        for source in unreliable_sources:
            trends = [{"element_value": "test", "data_source": source}]
            result = denoiser.denoise_trends(trends)
            assert len(result) == 0

    def test_rule1_reliable_sources(self):
        bf = BaseFilter()
        for source in bf.RELIABLE_SOURCES:
            products = [{"monthly_sales": 500, "compliance_status": "compliant", "data_source": source, "stock_status": "in_stock"}]
            result = bf.filter(products)
            assert len(result) == 1

    def test_case_insensitive_source_check(self):
        denoiser = DataDenoiser()
        trends = [
            {"element_value": "test", "data_source": "Amazon"},
            {"element_value": "test2", "data_source": "GOOGLE_TRENDS"},
        ]
        result = denoiser.denoise_trends(trends)
        assert len(result) == 2
