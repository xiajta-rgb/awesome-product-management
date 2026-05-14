class ProductPushBuilder:

    def build_hit_product_list(self, hit_products: list) -> dict:
        formatted_products = []
        for product in hit_products:
            formatted_products.append(self._format_product(product))
        return {
            "push_type": "hit_product_list",
            "title": "高潜力爆品列表推送",
            "products": formatted_products,
        }

    def build_potential_product_list(self, potential_products: list) -> dict:
        formatted_products = []
        for product in potential_products:
            formatted = self._format_product(product)
            formatted["growth_potential"] = product.get("growth_potential", "")
            formatted["data_source"] = product.get("data_source", "")
            formatted["supply_chain_feasibility"] = product.get(
                "supply_chain_feasibility", ""
            )
            formatted_products.append(formatted)
        return {
            "push_type": "potential_product_list",
            "title": "潜力爆品列表推送",
            "products": formatted_products,
        }

    def _format_product(self, product: dict) -> dict:
        formatted = {
            "title": product.get("title", ""),
            "url": product.get("url", ""),
            "features": product.get("features", {}),
            "price": product.get("price", 0.0),
            "selling_points": product.get("selling_points", []),
            "trend_match_points": product.get("trend_match_points", []),
            "data_source": product.get("data_source", ""),
            "expected_margin": product.get("expected_margin", 0.0),
            "uniqueness_coefficient": product.get("uniqueness_coefficient", 0.0),
            "review_status": self._check_review_status(product),
            "margin_alert": self._check_margin_alert(product),
        }
        return formatted

    def _check_review_status(self, product: dict) -> str:
        reviews = product.get("reviews", [])
        if not reviews or len(reviews) == 0:
            return "无有效评论"
        return "有有效评论"

    def _check_margin_alert(self, product: dict) -> str:
        margin = product.get("expected_margin", 0.0)
        if isinstance(margin, (int, float)) and margin < 0.3:
            return "低毛利预警"
        return ""
