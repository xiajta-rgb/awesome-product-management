from src.common.ontology_engine import OntologyEngine


class ElementExtractor:
    CORE_FREQUENCY_THRESHOLD = 2
    MARGIN_THRESHOLD = 0.3

    def __init__(self):
        self.ontology_engine = OntologyEngine()

    def extract(self, hit_products, trends=None):
        freq = self._count_element_frequency(hit_products)
        top10 = self._get_top10_elements(freq)
        visual_suggestions = self._generate_visual_suggestions(hit_products, trends or [])
        return {
            "top10_elements": top10,
            "visual_diff_suggestions": visual_suggestions,
        }

    def _count_element_frequency(self, products):
        freq = {}
        for product in products:
            elements = self._extract_product_elements(product)
            for element in elements:
                if element in freq:
                    freq[element] += 1
                else:
                    freq[element] = 1
        return freq

    def _get_top10_elements(self, freq):
        filtered = {
            k: v for k, v in freq.items() if v >= self.CORE_FREQUENCY_THRESHOLD
        }
        sorted_elements = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
        top10 = []
        for element, count in sorted_elements[:10]:
            margin = self._estimate_element_margin(element, freq)
            entry = {
                "element": element,
                "frequency": count,
                "is_core": count >= self.CORE_FREQUENCY_THRESHOLD,
                "margin": margin,
            }
            entry = self._apply_margin_penalty(entry, margin)
            top10.append(entry)
        return top10

    def _generate_visual_suggestions(self, hit_products, trends):
        suggestions = []
        trend_elements = set()
        for trend in trends:
            tag = trend.get("standardized_tag", "")
            if tag:
                trend_elements.add(tag)

        hit_elements = set()
        for product in hit_products:
            elements = self._extract_product_elements(product)
            for e in elements:
                hit_elements.add(e)

        missing_in_hits = trend_elements - hit_elements
        for element in missing_in_hits:
            suggestions.append({
                "element": element,
                "suggestion_type": "visual_gap",
                "description": f"站外趋势元素 '{element}' 在站内爆品中缺失，建议补充视觉呈现",
            })

        unique_in_hits = hit_elements - trend_elements
        for element in unique_in_hits:
            suggestions.append({
                "element": element,
                "suggestion_type": "visual_differentiation",
                "description": f"站内爆品独有元素 '{element}'，可作为视觉差异化亮点",
            })

        return suggestions

    def _calculate_gross_margin(self, product):
        cost = product.get("cost", 0)
        price = product.get("price", 0)
        if price <= 0:
            return 0.0
        margin = (price - cost) / price
        return round(margin, 4)

    def _apply_margin_penalty(self, element, margin):
        if margin < self.MARGIN_THRESHOLD:
            current_weight = element.get("recommendation_weight", 1.0)
            element["recommendation_weight"] = round(current_weight * 0.7, 2)
            element["margin_penalty_applied"] = True
        else:
            element["margin_penalty_applied"] = False
        return element

    def _extract_product_elements(self, product):
        elements = []
        features = product.get("standardized_features", {})
        if not features or not isinstance(features, dict):
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

    def _estimate_element_margin(self, element, freq):
        return 0.35
