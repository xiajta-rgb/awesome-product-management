import re

RELIABLE_SOURCES = {
    "amazon_bestseller",
    "amazon",
    "google_trends",
    "pinterest",
    "statista",
    "instagram",
    "tiktok",
    "wgsn",
}

SPAM_KEYWORDS = [
    "free money",
    "click here",
    "buy now",
    "limited offer",
    "act now",
    "100% free",
    "no risk",
    "guaranteed",
    "winner",
    "congratulations",
    "click below",
    "subscribe now",
    "exclusive deal",
    "限时免费",
    "点击领取",
    "免费领取",
    "中奖",
    "恭喜",
]


class DataDenoiser:

    def denoise_products(self, product_list):
        result = []
        for product in product_list:
            title = product.get("title", "") or ""
            if not self._is_valid_title(title):
                continue
            price_raw = product.get("price_range", "") or product.get("price", "")
            if price_raw and not self._is_valid_price(price_raw):
                product["price_range"] = ""
                product["price"] = None
            rank = product.get("sales_rank")
            if rank is not None and not self._is_valid_rank(rank):
                product["sales_rank"] = None
            if self._is_spam(product):
                continue
            source = product.get("data_source", "") or ""
            if source and source.lower() not in {s.lower() for s in RELIABLE_SOURCES}:
                continue
            sales = product.get("monthly_sales")
            if sales is not None and sales == 0:
                continue
            result.append(product)
        return result

    def denoise_trends(self, trend_list):
        result = []
        for trend in trend_list:
            source = trend.get("data_source", "") or ""
            if source and source.lower() not in {s.lower() for s in RELIABLE_SOURCES}:
                continue
            result.append(trend)
        return result

    def _is_valid_title(self, title):
        if not title or not title.strip():
            return False
        if len(title.strip()) < 3:
            return False
        return True

    def _is_valid_price(self, price):
        try:
            if isinstance(price, (int, float)):
                num = float(price)
            else:
                cleaned = re.sub(r"[^\d.]", "", str(price))
                if not cleaned:
                    return False
                num = float(cleaned)
            if num < 0 or num > 10000:
                return False
            return True
        except (ValueError, TypeError):
            return False

    def _is_valid_rank(self, rank):
        try:
            r = int(rank)
            return r >= 0
        except (ValueError, TypeError):
            return False

    def _is_spam(self, product):
        title = (product.get("title", "") or "").lower()
        features = (product.get("features", "") or "").lower()
        text = f"{title} {features}"
        for keyword in SPAM_KEYWORDS:
            if keyword.lower() in text:
                return True
        return False
