from datetime import datetime


class PitfallPushBuilder:

    def build_pitfall_reminders(self, products_with_reviews: list) -> dict:
        filtered_products = self._filter_no_review_products(products_with_reviews)
        pitfalls = []
        for product in filtered_products:
            reviews = product.get("reviews", [])
            product_pitfalls = self._extract_pain_points(reviews)
            for pitfall in product_pitfalls:
                pitfall["product_title"] = product.get("title", "")
                pitfall["data_source"] = product.get("data_source", "")
                pitfalls.append(pitfall)
        ranked_pitfalls = self._rank_pitfalls(pitfalls)
        return {
            "push_type": "pitfall_reminders",
            "title": "避坑提醒推送",
            "pitfalls": ranked_pitfalls,
            "generated_at": datetime.now().isoformat(),
        }

    def _extract_pain_points(self, reviews: list) -> list:
        pain_point_map = {}
        for review in reviews:
            points = review.get("pain_points", [])
            for point in points:
                point_text = point if isinstance(point, str) else str(point)
                if point_text in pain_point_map:
                    pain_point_map[point_text] += 1
                else:
                    pain_point_map[point_text] = 1
        result = []
        for text, count in pain_point_map.items():
            result.append({"pain_point": text, "frequency": count})
        return result

    def _rank_pitfalls(self, pitfalls: list) -> list:
        return sorted(pitfalls, key=lambda x: x.get("frequency", 0), reverse=True)

    def _filter_no_review_products(self, products: list) -> list:
        filtered = []
        for product in products:
            reviews = product.get("reviews", [])
            if reviews and len(reviews) > 0:
                filtered.append(product)
        return filtered
