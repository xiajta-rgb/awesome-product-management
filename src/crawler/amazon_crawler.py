import logging
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from src.crawler.anti_detect import AntiDetect
from src.crawler.retry_handler import RetryHandler

logger = logging.getLogger(__name__)

VALID_CATEGORIES = {
    "business_casual",
    "casual_sport",
    "workwear_outdoor",
}

EXCLUDE_KEYWORDS = [
    "kids",
    "child",
    "boys",
    "girls",
    "toddler",
    "infant",
    "baby",
    "children",
    "accessory",
    "accessories",
    "hat",
    "belt",
    "scarf",
    "jewelry",
    "watch",
    "sunglasses",
    "sock",
    "tie",
    "glove",
]


class AmazonCrawler:

    BASE_URL = "https://www.amazon.com"

    def __init__(self):
        self.session = requests.Session()
        self.anti_detect = AntiDetect()
        self.retry_handler = RetryHandler(max_retries=2, retry_delay=5.0)

    def _request(self, url):
        headers = self.anti_detect.get_random_headers()
        proxy = self.anti_detect.get_proxy()
        self.anti_detect.random_delay()
        response = self.session.get(url, headers=headers, proxies=proxy, timeout=30)
        if self.anti_detect.handle_captcha(response):
            logger.warning("Captcha encountered for URL: %s", url)
            raise Exception("Captcha detected, cannot proceed")
        return response

    def crawl_category(self, category_url):
        try:
            products = self.retry_handler.execute_with_retry(
                self._crawl_category_impl, category_url
            )
            return products
        except Exception as e:
            logger.error("Failed to crawl category %s: %s", category_url, str(e))
            return []

    def _crawl_category_impl(self, category_url):
        response = self._request(category_url)
        products = self._parse_product_list(response.text)
        filtered = []
        for product in products:
            if self._is_valid_product(product):
                filtered.append(product)
        return filtered

    def _is_valid_product(self, product):
        title = product.get("title", "").lower()
        for keyword in EXCLUDE_KEYWORDS:
            if keyword in title:
                return False
        return True

    def crawl_product_detail(self, product_url):
        try:
            detail = self.retry_handler.execute_with_retry(
                self._crawl_product_detail_impl, product_url
            )
            return detail
        except Exception as e:
            logger.error("Failed to crawl product detail %s: %s", product_url, str(e))
            return {}

    def _crawl_product_detail_impl(self, product_url):
        response = self._request(product_url)
        detail = self._parse_product_detail(response.text)
        detail["url"] = product_url
        return detail

    def _parse_product_list(self, html):
        soup = BeautifulSoup(html, "html.parser")
        products = []
        items = soup.select("div[data-component-type='s-search-result']")
        if not items:
            items = soup.select("div.s-result-item")

        for item in items:
            try:
                product = self._extract_list_item(item)
                if product:
                    products.append(product)
            except Exception as e:
                logger.warning("Error parsing list item: %s", str(e))
                continue
        return products

    def _extract_list_item(self, item):
        title_elem = item.select_one("h2 a span")
        if not title_elem:
            return None
        title = title_elem.get_text(strip=True)

        link_elem = item.select_one("h2 a")
        url = ""
        if link_elem and link_elem.get("href"):
            url = self.BASE_URL + link_elem["href"]
            if link_elem["href"].startswith("http"):
                url = link_elem["href"]

        price_elem = item.select_one("span.a-price span.a-offscreen")
        price_range = ""
        if price_elem:
            price_range = price_elem.get_text(strip=True)

        image_elem = item.select_one("img.s-image")
        main_image_url = ""
        if image_elem:
            main_image_url = image_elem.get("src", "")

        rating_elem = item.select_one("span.a-icon-alt")
        sales_rank = None

        product = {
            "title": title,
            "url": url,
            "features": "",
            "sales_rank": sales_rank,
            "price_range": price_range,
            "stock_status": "",
            "seller_type": "",
            "promotions": "",
            "related_products": "",
            "listing_date": None,
            "data_source": "amazon_bestseller",
            "main_image_url": main_image_url,
            "detail_image_urls": "",
        }
        return product

    def _parse_product_detail(self, html):
        soup = BeautifulSoup(html, "html.parser")
        detail = {}

        title_elem = soup.select_one("span#productTitle")
        detail["title"] = title_elem.get_text(strip=True) if title_elem else ""

        feature_bullets = soup.select("div#feature-bullets li span.a-list-item")
        features_list = []
        for bullet in feature_bullets:
            text = bullet.get_text(strip=True)
            if text and "make sure this fits" not in text.lower():
                features_list.append(text)
        detail["features"] = "; ".join(features_list)

        sales_rank_elem = soup.select_one("div#detailBullets_feature_div span.a-list-item")
        sales_rank = None
        if sales_rank_elem:
            rank_text = sales_rank_elem.get_text()
            rank_match = re.search(r"#(\d[\d,]*)", rank_text)
            if rank_match:
                sales_rank = int(rank_match.group(1).replace(",", ""))
        detail["sales_rank"] = sales_rank

        price_elem = soup.select_one("span.a-price span.a-offscreen")
        if not price_elem:
            price_elem = soup.select_one("span#priceblock_ourprice")
        detail["price_range"] = price_elem.get_text(strip=True) if price_elem else ""

        availability_elem = soup.select_one("div#availability span")
        detail["stock_status"] = availability_elem.get_text(strip=True) if availability_elem else ""

        seller_elem = soup.select_one("a#sellerProfileTriggerId")
        detail["seller_type"] = seller_elem.get_text(strip=True) if seller_elem else ""

        promo_elems = soup.select("div#dealsAccordionRow span.a-color-success")
        promotions_list = [p.get_text(strip=True) for p in promo_elems]
        detail["promotions"] = "; ".join(promotions_list)

        related_elems = soup.select("div#sims-fbt-carousel div.a-section span.a-text-normal")
        related_list = [r.get_text(strip=True) for r in related_elems[:5]]
        detail["related_products"] = "; ".join(related_list)

        date_elem = soup.select_one("th:contains('Date First Available') + td")
        listing_date = None
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            try:
                listing_date = datetime.strptime(date_text, "%B %d, %Y")
            except ValueError:
                listing_date = None
        detail["listing_date"] = listing_date

        main_img_elem = soup.select_one("img#landingImage")
        detail["main_image_url"] = main_img_elem.get("src", "") if main_img_elem else ""

        detail_imgs = soup.select("div#imageBlock img")
        detail_image_urls = []
        for img in detail_imgs:
            src = img.get("src", "")
            if src and "grey-pixel" not in src:
                detail_image_urls.append(src)
        detail["detail_image_urls"] = "; ".join(detail_image_urls)

        detail["data_source"] = "amazon_bestseller"

        return detail
