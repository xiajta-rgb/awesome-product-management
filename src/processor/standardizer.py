import re

from src.common.ontology_engine import OntologyEngine
from src.common.ontology import MATERIAL_TAG_MAPPING


class DataStandardizer:

    def __init__(self):
        self.ontology_engine = OntologyEngine()

    def standardize_product(self, product):
        result = dict(product)
        price_raw = result.get("price_range", "") or result.get("price", "")
        if price_raw:
            result["price"] = self._normalize_price(price_raw)
        sales_raw = result.get("monthly_sales")
        if sales_raw is not None:
            result["monthly_sales"] = self._normalize_sales(str(sales_raw))
        features = result.get("features", "") or ""
        if features:
            result["review_keywords"] = self._tokenize_features(features)
        tags = result.get("tags", {})
        if isinstance(tags, dict):
            standardized_tags = {}
            for dimension in ("color", "material", "design", "fit"):
                raw_tags = tags.get(dimension, [])
                if isinstance(raw_tags, list):
                    standardized_tags[dimension] = self.ontology_engine.standardize_tags(
                        raw_tags, dimension
                    )
                else:
                    standardized_tags[dimension] = []
            result["standardized_features"] = standardized_tags
        elif not result.get("standardized_features"):
            result["standardized_features"] = {
                "color": [],
                "material": [],
                "design": [],
                "fit": [],
            }
        result = self._supplement_missing_features(result)
        return result

    def standardize_trend(self, trend):
        result = dict(trend)
        element_type = result.get("element_type", "") or ""
        element_value = result.get("element_value", "") or result.get("keyword", "") or ""
        dimension_map = {
            "color": "color",
            "material": "material",
            "design": "design",
            "fit": "fit",
            "版型": "fit",
            "颜色": "color",
            "材质": "material",
            "设计": "design",
        }
        dimension = dimension_map.get(element_type.lower(), "")
        if dimension and element_value:
            standardized = self.ontology_engine.standardize_tag(element_value, dimension)
            result["standardized_tag"] = standardized
        else:
            result["standardized_tag"] = element_value
        return result

    def batch_standardize_products(self, products):
        return [self.standardize_product(p) for p in products]

    def batch_standardize_trends(self, trends):
        return [self.standardize_trend(t) for t in trends]

    def _normalize_price(self, price_str):
        try:
            if isinstance(price_str, (int, float)):
                return round(float(price_str), 2)
            cleaned = re.sub(r"[^\d.]", "", str(price_str))
            if not cleaned:
                return 0.0
            parts = cleaned.split(".")
            if len(parts) > 2:
                cleaned = parts[0] + "." + "".join(parts[1:])
            return round(float(cleaned), 2)
        except (ValueError, TypeError):
            return 0.0

    def _normalize_sales(self, sales_str):
        try:
            if isinstance(sales_str, (int, float)):
                return int(sales_str)
            cleaned = re.sub(r"[^\d]", "", str(sales_str))
            if not cleaned:
                return 0
            return int(cleaned)
        except (ValueError, TypeError):
            return 0

    def _tokenize_features(self, features_str):
        tokens = []
        for part in re.split(r"[;；,，\n\r|]+", features_str):
            token = part.strip()
            if token:
                tokens.append(token)
        return tokens

    def _supplement_missing_features(self, product):
        features = product.get("standardized_features", {})
        if not isinstance(features, dict):
            features = {"color": [], "material": [], "design": [], "fit": []}
        material_tags = features.get("material", [])
        if not material_tags:
            title = product.get("title", "") or ""
            supplemented = []
            for cn_name, en_tag in MATERIAL_TAG_MAPPING.items():
                if cn_name in title:
                    standardized = self.ontology_engine.standardize_tag(cn_name, "material")
                    if standardized not in supplemented:
                        supplemented.append(standardized)
            image_result = product.get("image_recognition_result", {})
            if isinstance(image_result, dict):
                stitching = image_result.get("stitching_type", "")
                if stitching:
                    std = self.ontology_engine.standardize_tag(stitching, "material")
                    if std not in supplemented:
                        supplemented.append(std)
            if supplemented:
                features["material"] = supplemented
        product["standardized_features"] = features
        return product
