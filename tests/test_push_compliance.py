import pytest
from src.push.product_push import ProductPushBuilder
from src.push.pitfall_push import PitfallPushBuilder


class TestNoASINInPush:

    def test_hit_product_no_asin(self):
        builder = ProductPushBuilder()
        products = [
            {
                "title": "Test Product B001ABC123",
                "url": "http://amazon.com/dp/B001ABC123",
                "features": {},
                "price": 29.99,
                "data_source": "amazon",
                "expected_margin": 0.4,
                "uniqueness_coefficient": 0.5,
                "reviews": [{"content": "good"}],
                "selling_points": [],
                "trend_match_points": [],
                "asin": "B001ABC123",
            },
        ]
        result = builder.build_hit_product_list(products)
        for p in result["products"]:
            assert "asin" not in p
            assert "ASIN" not in p

    def test_potential_product_no_asin(self):
        builder = ProductPushBuilder()
        products = [
            {
                "title": "Test Product B002DEF456",
                "url": "http://amazon.com/dp/B002DEF456",
                "features": {},
                "price": 39.99,
                "data_source": "amazon",
                "expected_margin": 0.35,
                "uniqueness_coefficient": 0.6,
                "reviews": [],
                "selling_points": [],
                "trend_match_points": [],
                "growth_potential": "high",
                "supply_chain_feasibility": "medium",
                "asin": "B002DEF456",
            },
        ]
        result = builder.build_potential_product_list(products)
        for p in result["products"]:
            assert "asin" not in p
            assert "ASIN" not in p


class TestNoReviewMarking:

    def test_no_review_marked(self):
        builder = ProductPushBuilder()
        products = [
            {
                "title": "Test",
                "url": "http://a.com",
                "features": {},
                "price": 10.0,
                "data_source": "amazon",
                "expected_margin": 0.4,
                "uniqueness_coefficient": 0.5,
                "reviews": [],
                "selling_points": [],
                "trend_match_points": [],
            },
        ]
        result = builder.build_hit_product_list(products)
        assert result["products"][0]["review_status"] == "无有效评论"

    def test_with_review_not_marked(self):
        builder = ProductPushBuilder()
        products = [
            {
                "title": "Test",
                "url": "http://a.com",
                "features": {},
                "price": 10.0,
                "data_source": "amazon",
                "expected_margin": 0.4,
                "uniqueness_coefficient": 0.5,
                "reviews": [{"content": "Great product"}],
                "selling_points": [],
                "trend_match_points": [],
            },
        ]
        result = builder.build_hit_product_list(products)
        assert result["products"][0]["review_status"] == "有有效评论"

    def test_no_reviews_key_marked(self):
        builder = ProductPushBuilder()
        products = [
            {
                "title": "Test",
                "url": "http://a.com",
                "features": {},
                "price": 10.0,
                "data_source": "amazon",
                "expected_margin": 0.4,
                "uniqueness_coefficient": 0.5,
                "selling_points": [],
                "trend_match_points": [],
            },
        ]
        result = builder.build_hit_product_list(products)
        assert result["products"][0]["review_status"] == "无有效评论"


class TestLowMarginAlert:

    def test_low_margin_alert(self):
        builder = ProductPushBuilder()
        products = [
            {
                "title": "Test",
                "url": "http://a.com",
                "features": {},
                "price": 10.0,
                "data_source": "amazon",
                "expected_margin": 0.25,
                "uniqueness_coefficient": 0.5,
                "reviews": [],
                "selling_points": [],
                "trend_match_points": [],
            },
        ]
        result = builder.build_hit_product_list(products)
        assert result["products"][0]["margin_alert"] == "低毛利预警"

    def test_margin_below_30_percent(self):
        builder = ProductPushBuilder()
        products = [
            {
                "title": "Test",
                "url": "http://a.com",
                "features": {},
                "price": 10.0,
                "data_source": "amazon",
                "expected_margin": 0.29,
                "uniqueness_coefficient": 0.5,
                "reviews": [],
                "selling_points": [],
                "trend_match_points": [],
            },
        ]
        result = builder.build_hit_product_list(products)
        assert result["products"][0]["margin_alert"] == "低毛利预警"

    def test_margin_at_30_percent_no_alert(self):
        builder = ProductPushBuilder()
        products = [
            {
                "title": "Test",
                "url": "http://a.com",
                "features": {},
                "price": 10.0,
                "data_source": "amazon",
                "expected_margin": 0.30,
                "uniqueness_coefficient": 0.5,
                "reviews": [],
                "selling_points": [],
                "trend_match_points": [],
            },
        ]
        result = builder.build_hit_product_list(products)
        assert result["products"][0]["margin_alert"] == ""

    def test_high_margin_no_alert(self):
        builder = ProductPushBuilder()
        products = [
            {
                "title": "Test",
                "url": "http://a.com",
                "features": {},
                "price": 10.0,
                "data_source": "amazon",
                "expected_margin": 0.50,
                "uniqueness_coefficient": 0.5,
                "reviews": [],
                "selling_points": [],
                "trend_match_points": [],
            },
        ]
        result = builder.build_hit_product_list(products)
        assert result["products"][0]["margin_alert"] == ""


class TestPitfallOnlyReliableReviews:

    def test_pitfall_only_with_reviews(self):
        builder = PitfallPushBuilder()
        products = [
            {
                "title": "Product A",
                "data_source": "amazon",
                "reviews": [{"pain_points": ["Size Too Small"]}],
            },
            {
                "title": "Product B",
                "data_source": "amazon",
                "reviews": [],
            },
        ]
        result = builder.build_pitfall_reminders(products)
        pitfall_titles = [p.get("title", "") for p in result["pitfalls"]]
        assert "Product A" in pitfall_titles
        assert "Product B" not in pitfall_titles

    def test_pitfall_no_review_products_excluded(self):
        builder = PitfallPushBuilder()
        products = [
            {
                "title": "No Review Product",
                "data_source": "amazon",
                "reviews": [],
            },
        ]
        result = builder.build_pitfall_reminders(products)
        assert len(result["pitfalls"]) == 0

    def test_pitfall_filter_internal(self):
        builder = PitfallPushBuilder()
        products = [
            {"title": "A", "data_source": "amazon", "reviews": [{"pain_points": ["bad"]}]},
            {"title": "B", "data_source": "amazon", "reviews": []},
            {"title": "C", "data_source": "amazon"},
        ]
        filtered = builder._filter_no_review_products(products)
        assert len(filtered) == 1
        assert filtered[0]["title"] == "A"
