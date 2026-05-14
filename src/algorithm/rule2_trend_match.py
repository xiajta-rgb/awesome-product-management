from src.common.ontology_engine import OntologyEngine


class TrendMatcher:
    MATCH_THRESHOLD = 80.0

    def __init__(self):
        self.ontology_engine = OntologyEngine()

    def match(self, products, trends):
        matched_products = []
        trend_elements = self._extract_trend_elements(trends)
        if not trend_elements:
            return matched_products
        trend_elements_lower = {e.lower(): e for e in trend_elements}
        for product in products:
            score = self.calculate_match_score(product, trends)
            if score >= self.MATCH_THRESHOLD:
                product_elements = self._extract_product_elements(product)
                matched = [trend_elements_lower[e.lower()] for e in product_elements if e.lower() in trend_elements_lower]
                product["trend_match_score"] = score
                product["matched_elements"] = matched
                matched_products.append(product)
        return matched_products

    def calculate_match_score(self, product, trends):
        trend_elements = self._extract_trend_elements(trends)
        if not trend_elements:
            return 0.0
        product_elements = self._extract_product_elements(product)
        if not product_elements:
            return 0.0
        trend_elements_lower = {e.lower() for e in trend_elements}
        matched_count = 0
        for element in product_elements:
            if element.lower() in trend_elements_lower:
                matched_count += 1
        # 匹配分数 = (匹配的元素数量 / 产品元素总数) * 100
        # 这样更合理：产品有多少比例的元素是当前趋势
        score = (matched_count / len(product_elements)) * 100
        return round(score, 2)

    def _extract_product_elements(self, product):
        elements = []
        features = product.get("standardized_features", {})
        if not features or not isinstance(features, dict):
            title = product.get("title", "")
            if title:
                elements.append(title.lower())
            return elements
        for dimension in ("color", "material", "design", "fit"):
            tags = features.get(dimension, [])
            if isinstance(tags, list):
                for tag in tags:
                    standardized = self.ontology_engine.standardize_tag(tag, dimension)
                    elements.append(standardized)
            elif isinstance(tags, str):
                standardized = self.ontology_engine.standardize_tag(tags, dimension)
                elements.append(standardized)
        return elements

    def _extract_trend_elements(self, trends):
        elements = []
        for trend in trends:
            heat_level = trend.get("heat_level", "")
            if heat_level not in ("high", "中", "medium", "高热度", "中热度"):
                continue
            tag = trend.get("standardized_tag", "")
            if tag:
                elements.append(tag)
            else:
                value = trend.get("element_value", "")
                if value:
                    elements.append(value)
        return list(set(elements))
