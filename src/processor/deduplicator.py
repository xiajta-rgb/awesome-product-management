import hashlib

from src.common.ontology import CLOTHING_ONTOLOGY


class DataDeduplicator:

    def deduplicate_products(self, product_list):
        seen = set()
        result = []
        for product in product_list:
            key = self._generate_product_key(product)
            if key not in seen:
                seen.add(key)
                result.append(product)
        return result

    def deduplicate_trends(self, trend_list):
        seen = set()
        result = []
        for trend in trend_list:
            key = self._generate_trend_key(trend)
            if key not in seen:
                seen.add(key)
                result.append(trend)
        return result

    def _generate_product_key(self, product):
        title = product.get("title", "") or ""
        url = product.get("url", "") or ""
        raw = f"{title}|{url}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def _generate_trend_key(self, trend):
        element = ""
        if isinstance(trend.get("element_value"), str):
            element = trend["element_value"]
        elif isinstance(trend.get("keyword"), str):
            element = trend["keyword"]
        elif isinstance(trend.get("title"), str):
            element = trend["title"]
        source = trend.get("data_source", "") or ""
        raw = f"{element}|{source}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()
