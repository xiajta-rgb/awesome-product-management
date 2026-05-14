from datetime import datetime


class AlgorithmOptimizer:
    DEFAULT_WEIGHTS = {
        "sales": 0.3,
        "trend": 0.25,
        "review": 0.25,
        "competition": 0.1,
        "compliance": 0.1,
    }

    def optimize_weights(self, current_results, market_data):
        weights = dict(self.DEFAULT_WEIGHTS)
        season = self._detect_season()
        weights = self._adjust_for_season(weights, season)
        trend_data = market_data.get("trend_data", {})
        if trend_data:
            weights = self._adjust_for_trend_shift(weights, trend_data)
        total = sum(weights.values())
        if total > 0:
            weights = {k: round(v / total, 4) for k, v in weights.items()}
        return weights

    def _detect_season(self):
        month = datetime.now().month
        if month in (3, 4, 5):
            return "spring"
        elif month in (6, 7, 8):
            return "summer"
        elif month in (9, 10, 11):
            return "autumn"
        else:
            return "winter"

    def _adjust_for_season(self, weights, season):
        season_adjustments = {
            "spring": {"trend": 0.03, "sales": -0.02},
            "summer": {"sales": 0.03, "trend": -0.01},
            "autumn": {"trend": 0.02, "review": -0.01},
            "winter": {"sales": 0.05, "trend": 0.02, "competition": -0.03},
        }
        adjustments = season_adjustments.get(season, {})
        for key, delta in adjustments.items():
            if key in weights:
                weights[key] = weights[key] + delta
        return weights

    def _adjust_for_trend_shift(self, weights, trend_data):
        shift_intensity = trend_data.get("shift_intensity", "low")
        if shift_intensity == "high":
            weights["trend"] = weights.get("trend", 0.25) + 0.05
            weights["sales"] = weights.get("sales", 0.3) - 0.03
        elif shift_intensity == "medium":
            weights["trend"] = weights.get("trend", 0.25) + 0.03
            weights["sales"] = weights.get("sales", 0.3) - 0.02
        else:
            pass
        return weights
