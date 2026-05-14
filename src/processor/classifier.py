from src.common.ontology_engine import OntologyEngine
from src.common.ontology import CLOTHING_ONTOLOGY


class DataClassifier:

    PAIN_POINT_KEYWORDS = {
        "尺码偏小": "Size Too Small",
        "尺码偏大": "Size Too Large",
        "尺码不准": "Size Inaccurate",
        "偏小": "Size Too Small",
        "偏大": "Size Too Large",
        "材质粗糙": "Rough Material",
        "材质差": "Poor Material",
        "面料差": "Poor Material",
        "质量差": "Poor Quality",
        "做工差": "Poor Craftsmanship",
        "掉色": "Color Fading",
        "褪色": "Color Fading",
        "染色": "Color Fading",
        "起球": "Pilling",
        "起毛": "Pilling",
        "毛球": "Pilling",
        "线头多": "Loose Threads",
        "脱线": "Loose Threads",
        "开线": "Loose Threads",
        "不透气": "Not Breathable",
        "闷热": "Not Breathable",
        "不舒适": "Uncomfortable",
        "不舒服": "Uncomfortable",
        "扎人": "Scratchy",
        "刺痒": "Scratchy",
        "色差": "Color Mismatch",
        "颜色不符": "Color Mismatch",
        "与图片不符": "Not As Pictured",
        "与描述不符": "Not As Described",
        "薄": "Too Thin",
        "太薄": "Too Thin",
        "薄透": "Too Thin",
        "缩水": "Shrinks",
        "变形": "Deforms",
        "走形": "Deforms",
        "有异味": "Bad Odor",
        "异味": "Bad Odor",
        "臭味": "Bad Odor",
        "拉链坏": "Broken Zipper",
        "扣子掉": "Button Falls Off",
        "容易破": "Easily Torn",
        "不耐磨": "Not Durable",
    }

    VALID_GENDERS = {"Menswear", "Womenswear"}
    VALID_CATEGORIES = {"Business Casual", "Casual Sport", "Workwear Outdoor"}

    def __init__(self):
        self.ontology_engine = OntologyEngine()

    def classify_by_sales(self, product):
        sales = product.get("monthly_sales")
        if sales is None:
            try:
                sales = int(product.get("sales", 0))
            except (ValueError, TypeError):
                sales = 0
        if sales >= 1000:
            return "爆品"
        elif sales >= 300:
            return "潜力品"
        elif sales >= 100:
            return "常规品"
        else:
            return "滞销品"

    def classify_by_category(self, product):
        title = product.get("title", "") or ""
        features = product.get("standardized_features", {})
        if not isinstance(features, dict):
            features = {}
        result = self.ontology_engine.match_category(title, features)
        gender = result.get("gender")
        category_main = result.get("category_main")
        category_sub = result.get("category_sub")
        if gender not in self.VALID_GENDERS:
            gender = None
        if category_main not in self.VALID_CATEGORIES:
            category_main = None
        if gender and category_main:
            ontology_subs = CLOTHING_ONTOLOGY.get(gender, {}).get(category_main, [])
            if category_sub not in ontology_subs:
                category_sub = None
        return {
            "gender": gender,
            "category_main": category_main,
            "category_sub": category_sub,
        }

    def classify_by_pain_points(self, product):
        reviews = product.get("negative_reviews", []) or product.get("reviews", [])
        if not reviews:
            return []
        pain_points = []
        seen = set()
        for review in reviews:
            text = ""
            if isinstance(review, dict):
                text = review.get("content", "") or review.get("text", "") or ""
            elif isinstance(review, str):
                text = review
            if not text:
                continue
            for keyword, pain_label in self.PAIN_POINT_KEYWORDS.items():
                if keyword in text and pain_label not in seen:
                    pain_points.append(pain_label)
                    seen.add(pain_label)
        return pain_points

    def classify_product(self, product):
        sales_tier = self.classify_by_sales(product)
        category = self.classify_by_category(product)
        pain_points = self.classify_by_pain_points(product)
        return {
            "sales_tier": sales_tier,
            "gender": category["gender"],
            "category_main": category["category_main"],
            "category_sub": category["category_sub"],
            "pain_points": pain_points,
        }
