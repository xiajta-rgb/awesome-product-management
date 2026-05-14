from src.common.ontology_engine import OntologyEngine


class TrendClassifier:

    ELEMENT_TYPE_MAP = {
        "color": "color",
        "颜色": "color",
        "colour": "color",
        "material": "material",
        "材质": "material",
        "fabric": "material",
        "面料": "material",
        "design": "design",
        "设计": "design",
        "fit": "fit",
        "版型": "fit",
        "silhouette": "fit",
    }

    def __init__(self):
        self.ontology_engine = OntologyEngine()

    def classify_by_element(self, trend):
        element_type_raw = (trend.get("element_type", "") or "").strip()
        element_value = (
            trend.get("element_value", "")
            or trend.get("keyword", "")
            or trend.get("title", "")
            or ""
        ).strip()
        element_type = self.ELEMENT_TYPE_MAP.get(element_type_raw.lower(), element_type_raw.lower())
        standardized_tag = element_value
        if element_type in ("color", "material", "design", "fit") and element_value:
            standardized_tag = self.ontology_engine.standardize_tag(element_value, element_type)
        return {
            "element_type": element_type,
            "standardized_tag": standardized_tag,
        }

    def classify_by_cycle(self, trend):
        duration = trend.get("duration_months")
        if duration is None:
            cycle = trend.get("trend_cycle", "") or ""
            cycle_lower = cycle.lower()
            if "short" in cycle_lower or "短期" in cycle:
                return "短期"
            elif "long" in cycle_lower or "长期" in cycle:
                return "长期"
            elif "medium" in cycle_lower or "中期" in cycle:
                return "中期"
            return "中期"
        try:
            d = float(duration)
        except (ValueError, TypeError):
            return "中期"
        if d <= 3:
            return "短期"
        elif d <= 6:
            return "中期"
        else:
            return "长期"

    def classify_by_heat(self, trend):
        heat = trend.get("heat_score")
        rank = trend.get("rank")
        if heat is not None:
            try:
                h = float(heat)
            except (ValueError, TypeError):
                return "低热度"
            if h >= 90:
                return "高热度"
            elif h >= 70:
                return "中热度"
            else:
                return "低热度"
        if rank is not None:
            try:
                r = int(rank)
            except (ValueError, TypeError):
                return "低热度"
            if r <= 10:
                return "高热度"
            elif r <= 30:
                return "中热度"
            else:
                return "低热度"
        return "低热度"

    def classify_trend(self, trend):
        element_info = self.classify_by_element(trend)
        trend_cycle = self.classify_by_cycle(trend)
        heat_level = self.classify_by_heat(trend)
        return {
            "element_type": element_info["element_type"],
            "standardized_tag": element_info["standardized_tag"],
            "trend_cycle": trend_cycle,
            "heat_level": heat_level,
        }
