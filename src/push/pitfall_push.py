from datetime import datetime


class PitfallPushBuilder:

    def build_pitfall_reminders(self, products_with_reviews: list) -> dict:
        filtered_products = self._filter_no_review_products(products_with_reviews)
        pitfalls = []
        for product in filtered_products:
            reviews = product.get("reviews", [])
            pain_points = self._extract_pain_points(reviews)
            if not pain_points:
                continue
            pitfalls.append({
                "title": product.get("title", "未知产品"),
                "description": f"该产品存在 {len(pain_points)} 个常见问题，选品时需注意规避",
                "pain_points": pain_points,
                "data_source": product.get("data_source", ""),
            })
        ranked_pitfalls = self._rank_pitfalls(pitfalls)
        return {
            "push_type": "pitfall_reminders",
            "title": "避坑提醒推送",
            "pitfalls": ranked_pitfalls,
            "generated_at": datetime.now().isoformat(),
        }

    def _extract_pain_points(self, reviews: list) -> list:
        pain_points = []
        seen = set()
        for review in reviews:
            points = review.get("pain_points", [])
            for point in points:
                point_text = point if isinstance(point, str) else str(point)
                if point_text not in seen:
                    seen.add(point_text)
                    pain_points.append(point_text)
        return pain_points

    def _rank_pitfalls(self, pitfalls: list) -> list:
        return sorted(pitfalls, key=lambda x: len(x.get("pain_points", [])), reverse=True)

    def _filter_no_review_products(self, products: list) -> list:
        filtered = []
        for product in products:
            reviews = product.get("reviews", [])
            if reviews and len(reviews) > 0:
                filtered.append(product)
        return filtered
