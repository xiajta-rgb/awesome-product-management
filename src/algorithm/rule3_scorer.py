class ProductScorer:
    WEIGHTS = {
        "sales": 0.3,
        "trend": 0.25,
        "review": 0.25,
        "competition": 0.1,
        "compliance": 0.1,
    }

    MAX_WEIGHTED_SCORE = (
        30.0 * 0.3 + 25.0 * 0.25 + 25.0 * 0.25 + 10.0 * 0.1 + 10.0 * 0.1
    )

    def score(self, product):
        s_sales = self._score_sales(product)
        s_trend = self._score_trend(product)
        s_review = self._score_review(product)
        s_comp = self._score_competition(product)
        s_compliance = self._score_compliance(product)

        is_new_product = self._is_new_product(product)
        velocity_bonus = self._calculate_velocity_bonus(product)

        raw_score = (
            s_sales * self.WEIGHTS["sales"]
            + s_trend * self.WEIGHTS["trend"]
            + s_review * self.WEIGHTS["review"]
            + s_comp * self.WEIGHTS["competition"]
            + s_compliance * self.WEIGHTS["compliance"]
        )
        total_score = round((raw_score / self.MAX_WEIGHTED_SCORE) * 100, 2)

        return {
            "total_score": total_score,
            "s_sales": s_sales,
            "s_trend": s_trend,
            "s_review": s_review,
            "s_comp": s_comp,
            "s_compliance": s_compliance,
            "is_new_product": is_new_product,
            "velocity_bonus": velocity_bonus,
        }

    def _score_sales(self, product):
        monthly_sales = product.get("monthly_sales", 0)
        if monthly_sales >= 1000:
            return 30.0
        elif monthly_sales >= 500:
            return 25.0
        elif monthly_sales >= 300:
            return 20.0
        else:
            return round((monthly_sales / 300) * 20, 2)

    def _score_review(self, product):
        is_new = self._is_new_product(product)
        review_count = product.get("review_count", 0)
        rating = product.get("rating", 0)
        positive_rate = product.get("positive_rate", 0)

        if review_count == 0:
            if is_new:
                base_score = 15.0
            else:
                base_score = 25.0
        else:
            if positive_rate >= 0.9:
                base_score = 25.0
            elif positive_rate >= 0.8:
                base_score = 20.0
            elif positive_rate >= 0.7:
                base_score = 15.0
            else:
                base_score = 10.0

        velocity_bonus = self._calculate_velocity_bonus(product)
        bonus = min(velocity_bonus, 5.0)
        return min(base_score + bonus, 25.0)

    def _score_trend(self, product):
        trend_match_score = product.get("trend_match_score", 0)
        score = (trend_match_score / 100) * 25
        return round(score, 2)

    def _score_competition(self, product):
        sales_rank = product.get("sales_rank")
        category_competitor_count = product.get("category_competitor_count", 0)

        rank_score = 0.0
        if sales_rank is not None:
            if sales_rank <= 10:
                rank_score = 5.0
            elif sales_rank <= 50:
                rank_score = 4.0
            elif sales_rank <= 100:
                rank_score = 3.0
            elif sales_rank <= 500:
                rank_score = 2.0
            else:
                rank_score = 1.0
        else:
            rank_score = 2.0

        competitor_score = 0.0
        if category_competitor_count == 0:
            competitor_score = 5.0
        elif category_competitor_count <= 50:
            competitor_score = 4.0
        elif category_competitor_count <= 200:
            competitor_score = 3.0
        elif category_competitor_count <= 500:
            competitor_score = 2.0
        else:
            competitor_score = 1.0

        return min(rank_score + competitor_score, 10.0)

    def _score_compliance(self, product):
        compliance_status = product.get("compliance_status", "")
        if compliance_status == "compliant":
            return 10.0
        elif compliance_status in ("minor_risk", "轻微风险"):
            return 5.0
        else:
            return 0.0

    def _is_new_product(self, product):
        listing_date = product.get("listing_date")
        review_count = product.get("review_count", 0)
        if listing_date is not None:
            from datetime import datetime, timezone
            if isinstance(listing_date, datetime):
                days_since_listing = (datetime.now(timezone.utc) - listing_date).days
                return days_since_listing <= 30
        if review_count == 0:
            return True
        return False

    def _calculate_velocity_bonus(self, product):
        velocity = product.get("ranking_velocity", 0)
        if velocity >= 50:
            return 5.0
        elif velocity >= 30:
            return 4.0
        elif velocity >= 20:
            return 3.0
        elif velocity >= 10:
            return 2.0
        elif velocity > 0:
            return 1.0
        return 0.0
