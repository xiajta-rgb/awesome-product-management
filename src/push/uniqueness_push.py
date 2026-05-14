from src.algorithm.uniqueness_calculator import UniquenessCalculator


class UniquenessPushBuilder:

    def __init__(self):
        self.calculator = UniquenessCalculator()

    def build_uniqueness_recommendations(
        self,
        products: list,
        user_products: list,
        threshold: float = 0.7,
    ) -> dict:
        sorted_products = self._sort_by_uniqueness(products, user_products)
        recommendations = []
        for product in sorted_products:
            uniqueness = self._calculate_product_uniqueness(product, user_products)
            if uniqueness >= (1.0 - threshold):
                recommendations.append(
                    {
                        "title": product.get("title", ""),
                        "url": product.get("url", ""),
                        "uniqueness_coefficient": uniqueness,
                        "category_main": product.get("category_main", ""),
                        "category_sub": product.get("category_sub", ""),
                        "price": product.get("price", 0.0),
                        "data_source": product.get("data_source", ""),
                    }
                )
        return {
            "push_type": "uniqueness_recommendations",
            "title": "独特性系数筛选推送",
            "threshold": threshold,
            "recommendations": recommendations,
        }

    def _calculate_product_uniqueness(
        self, product: dict, user_products: list
    ) -> float:
        similarity = self.calculator.calculate(product, user_products)
        return round(1.0 - similarity, 4)

    def _sort_by_uniqueness(self, products: list, user_products: list) -> list:
        products_with_score = []
        for product in products:
            uniqueness = self._calculate_product_uniqueness(product, user_products)
            product_copy = dict(product)
            product_copy["uniqueness_score"] = uniqueness
            products_with_score.append(product_copy)
        return sorted(
            products_with_score,
            key=lambda x: x.get("uniqueness_score", 0.0),
            reverse=True,
        )
