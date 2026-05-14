import pytest
from src.common.ontology_engine import OntologyEngine
from src.common.ontology import CLOTHING_ONTOLOGY


class TestColorTagMapping:

    def test_earth_tone_mapping(self):
        engine = OntologyEngine()
        assert engine.standardize_tag("大地色", "color") == "Earth Tone"

    def test_khaki_mapping(self):
        engine = OntologyEngine()
        assert engine.standardize_tag("卡其色", "color") == "Earth Tone"


class TestMaterialTagMapping:

    def test_cotton_linen_blend_mapping(self):
        engine = OntologyEngine()
        assert engine.standardize_tag("棉麻混纺", "material") == "Cotton Linen Blend"


class TestFitTagMapping:

    def test_slim_fit_mapping(self):
        engine = OntologyEngine()
        assert engine.standardize_tag("修身", "fit") == "Slim Fit"


class TestDesignTagMapping:

    def test_multi_pocket_mapping(self):
        engine = OntologyEngine()
        assert engine.standardize_tag("多口袋", "design") == "Multi Pocket"


class TestCategoryMatching:

    def test_menswear_business_casual(self):
        engine = OntologyEngine()
        result = engine.match_category("男士商务衬衫 大地色", {"color": ["Earth Tone"]})
        assert result["gender"] == "Menswear"
        assert result["category_main"] == "Business Casual"

    def test_menswear_casual_sport(self):
        engine = OntologyEngine()
        result = engine.match_category("男士运动卫衣 黑色", {"color": ["Solid Basic"]})
        assert result["gender"] == "Menswear"
        assert result["category_main"] == "Casual Sport"

    def test_menswear_workwear_outdoor(self):
        engine = OntologyEngine()
        result = engine.match_category("男士工装裤 军绿色", {"color": ["Army Green"]})
        assert result["gender"] == "Menswear"
        assert result["category_main"] == "Workwear Outdoor"

    def test_womenswear_business_casual(self):
        engine = OntologyEngine()
        result = engine.match_category("女士商务西装套 深蓝色", {"color": ["Navy Blue"]})
        assert result["gender"] == "Womenswear"
        assert result["category_main"] == "Business Casual"

    def test_womenswear_casual_sport(self):
        engine = OntologyEngine()
        result = engine.match_category("女士运动短裤 速干", {"color": ["Pastel Sport"]})
        assert result["gender"] == "Womenswear"
        assert result["category_main"] == "Casual Sport"

    def test_womenswear_workwear_outdoor(self):
        engine = OntologyEngine()
        result = engine.match_category("女士户外外套 防风", {"color": ["Earth Tone"]})
        assert result["gender"] == "Womenswear"
        assert result["category_main"] == "Workwear Outdoor"

    def test_category_hierarchy_structure(self):
        assert "Menswear" in CLOTHING_ONTOLOGY
        assert "Womenswear" in CLOTHING_ONTOLOGY
        for gender in ("Menswear", "Womenswear"):
            assert "Business Casual" in CLOTHING_ONTOLOGY[gender]
            assert "Casual Sport" in CLOTHING_ONTOLOGY[gender]
            assert "Workwear Outdoor" in CLOTHING_ONTOLOGY[gender]


class TestDynamicUpdate:

    def test_add_tag_mapping(self):
        engine = OntologyEngine()
        engine.add_tag_mapping("珊瑚色", "Coral", "color")
        assert engine.standardize_tag("珊瑚色", "color") == "Coral"
        assert engine.validate_tag("Coral", "color") is True

    def test_update_tag_mapping(self):
        engine = OntologyEngine()
        engine.add_tag_mapping("珊瑚色", "Coral", "color")
        engine.update_tag_mapping("珊瑚色", "Coral Pink", "color")
        assert engine.standardize_tag("珊瑚色", "color") == "Coral Pink"
        assert engine.validate_tag("Coral Pink", "color") is True

    def test_update_nonexistent_tag_raises(self):
        engine = OntologyEngine()
        with pytest.raises(KeyError):
            engine.update_tag_mapping("不存在的标签", "NewTag", "color")

    def test_remove_tag_mapping(self):
        engine = OntologyEngine()
        engine.add_tag_mapping("珊瑚色", "Coral", "color")
        engine.remove_tag_mapping("珊瑚色", "color")
        result = engine.standardize_tag("珊瑚色", "color")
        assert result == "珊瑚色"

    def test_remove_nonexistent_tag_raises(self):
        engine = OntologyEngine()
        with pytest.raises(KeyError):
            engine.remove_tag_mapping("不存在的标签", "color")

    def test_add_sub_category(self):
        engine = OntologyEngine()
        engine.add_sub_category("Menswear", "Business Casual", "新子品类")
        hierarchy = engine.get_category_hierarchy("Menswear")
        assert "新子品类" in hierarchy["Business Casual"]

    def test_add_sub_category_chinese_gender(self):
        engine = OntologyEngine()
        engine.add_sub_category("男装", "Casual Sport", "新运动品类")
        hierarchy = engine.get_category_hierarchy("Menswear")
        assert "新运动品类" in hierarchy["Casual Sport"]

    def test_add_sub_category_invalid_gender_raises(self):
        engine = OntologyEngine()
        with pytest.raises(ValueError):
            engine.add_sub_category("儿童", "Business Casual", "新子品类")

    def test_add_sub_category_invalid_category_raises(self):
        engine = OntologyEngine()
        with pytest.raises(ValueError):
            engine.add_sub_category("Menswear", "InvalidCategory", "新子品类")

    def test_add_duplicate_sub_category_no_duplication(self):
        engine = OntologyEngine()
        original = engine.get_category_hierarchy("Menswear")
        original_count = len(original["Business Casual"])
        engine.add_sub_category("Menswear", "Business Casual", "商务衬衫")
        after = engine.get_category_hierarchy("Menswear")
        assert len(after["Business Casual"]) == original_count

    def test_invalid_dimension_raises(self):
        engine = OntologyEngine()
        with pytest.raises(ValueError):
            engine.standardize_tag("test", "invalid_dimension")
