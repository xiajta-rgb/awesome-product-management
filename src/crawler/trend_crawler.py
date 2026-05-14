import logging
import re

import requests
from bs4 import BeautifulSoup

from src.crawler.anti_detect import AntiDetect
from src.crawler.retry_handler import RetryHandler

logger = logging.getLogger(__name__)


class TrendCrawler:

    GOOGLE_TRENDS_URL = "https://trends.google.com/trends/api/widgetdata/multiline"
    PINTEREST_URL = "https://www.pinterest.com"
    STATISTA_URL = "https://www.statista.com"
    INSTAGRAM_URL = "https://www.instagram.com"
    TIKTOK_URL = "https://www.tiktok.com"
    WGSN_URL = "https://www.wgsn.com"

    def __init__(self):
        self.session = requests.Session()
        self.anti_detect = AntiDetect()
        self.retry_handler = RetryHandler(max_retries=2, retry_delay=5.0)
        self._channel_config = {
            "google_trends": {"enabled": True, "interval": 86400},
            "pinterest": {"enabled": True, "interval": 86400},
            "statista": {"enabled": True, "interval": 604800},
            "instagram": {"enabled": True, "interval": 43200},
            "tiktok": {"enabled": True, "interval": 43200},
            "wgsn": {"enabled": True, "interval": 604800},
        }

    def _request(self, url, params=None):
        headers = self.anti_detect.get_random_headers()
        proxy = self.anti_detect.get_proxy()
        self.anti_detect.random_delay()
        response = self.session.get(
            url, headers=headers, proxies=proxy, params=params, timeout=30
        )
        return response

    def crawl_google_trends(self, keyword):
        try:
            result = self.retry_handler.execute_with_retry(
                self._crawl_google_trends_impl, keyword
            )
            return result
        except Exception as e:
            logger.error("Failed to crawl Google Trends for '%s': %s", keyword, str(e))
            return {"keyword": keyword, "data_source": "google_trends", "error": str(e)}

    def _crawl_google_trends_impl(self, keyword):
        explore_url = "https://trends.google.com/trends/api/explore"
        params = {
            "hl": "en-US",
            "tz": "-480",
            "req": '{"comparisonItem":[{"keyword":"' + keyword + '","geo":"US","time":"today 3-m"}],"category":0,"property":""}',
        }
        headers = self.anti_detect.get_random_headers()
        proxy = self.anti_detect.get_proxy()
        self.anti_detect.random_delay()
        response = self.session.get(
            explore_url, headers=headers, proxies=proxy, params=params, timeout=30
        )

        timeline_data = []
        interest_over_time = []

        if response.status_code == 200:
            text = response.text
            if text.startswith(")]}'"):
                text = text[4:]
            try:
                import json

                data = json.loads(text)
                widgets = data.get("widgets", [])
                for widget in widgets:
                    if widget.get("id") == "TIMESERIES":
                        token = widget.get("token", "")
                        timeline_data = self._fetch_timeline_data(keyword, token)
            except Exception:
                pass

        result = {
            "keyword": keyword,
            "search_heat": 0,
            "trend_change": "stable",
            "timeline_data": timeline_data,
            "interest_over_time": interest_over_time,
            "data_source": "google_trends",
        }
        return result

    def _fetch_timeline_data(self, keyword, token):
        return []

    def crawl_pinterest(self, keyword):
        try:
            result = self.retry_handler.execute_with_retry(
                self._crawl_pinterest_impl, keyword
            )
            return result
        except Exception as e:
            logger.error("Failed to crawl Pinterest for '%s': %s", keyword, str(e))
            return []

    def _crawl_pinterest_impl(self, keyword):
        search_url = f"{self.PINTEREST_URL}/search/pins/"
        params = {"q": keyword, "rs": "typed"}
        response = self._request(search_url, params=params)

        trends = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            pin_items = soup.select("div[data-test-id='pinWrapper']")
            for pin in pin_items:
                title_elem = pin.select_one("div[data-test-id='pinTitle']")
                desc_elem = pin.select_one("div[data-test-id='pinDescription']")
                img_elem = pin.select_one("img")

                trend_item = {
                    "title": title_elem.get_text(strip=True) if title_elem else "",
                    "description": desc_elem.get_text(strip=True) if desc_elem else "",
                    "image_url": img_elem.get("src", "") if img_elem else "",
                    "keyword": keyword,
                    "data_source": "pinterest",
                }
                trends.append(trend_item)

        return trends

    def crawl_statista(self, report_url):
        try:
            result = self.retry_handler.execute_with_retry(
                self._crawl_statista_impl, report_url
            )
            return result
        except Exception as e:
            logger.error("Failed to crawl Statista for '%s': %s", report_url, str(e))
            return {"url": report_url, "data_source": "statista", "error": str(e)}

    def _crawl_statista_impl(self, report_url):
        response = self._request(report_url)

        result = {
            "url": report_url,
            "title": "",
            "key_findings": [],
            "statistics": [],
            "data_source": "statista",
        }

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            title_elem = soup.select_one("h1.header__title")
            result["title"] = title_elem.get_text(strip=True) if title_elem else ""

            finding_elems = soup.select("div.keyFigures div.keyFigure__text")
            result["key_findings"] = [f.get_text(strip=True) for f in finding_elems]

            stat_elems = soup.select("div.statisticItem span.statisticItem__title")
            result["statistics"] = [s.get_text(strip=True) for s in stat_elems]

        return result

    def crawl_social_media(self, platform, keyword):
        try:
            result = self.retry_handler.execute_with_retry(
                self._crawl_social_media_impl, platform, keyword
            )
            return result
        except Exception as e:
            logger.error(
                "Failed to crawl %s for '%s': %s", platform, keyword, str(e)
            )
            return []

    def _crawl_social_media_impl(self, platform, keyword):
        platform = platform.lower()
        if platform == "instagram":
            return self._crawl_instagram(keyword)
        elif platform == "tiktok":
            return self._crawl_tiktok(keyword)
        else:
            logger.warning("Unsupported platform: %s", platform)
            return []

    def _crawl_instagram(self, keyword):
        search_url = f"{self.INSTAGRAM_URL}/explore/tags/{keyword}/"
        response = self._request(search_url)

        topics = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            post_elems = soup.select("article div.v1Nh3")
            for post in post_elems:
                img_elem = post.select_one("img")
                topic = {
                    "platform": "instagram",
                    "keyword": keyword,
                    "image_url": img_elem.get("src", "") if img_elem else "",
                    "description": img_elem.get("alt", "") if img_elem else "",
                    "data_source": "instagram",
                }
                topics.append(topic)

        return topics

    def _crawl_tiktok(self, keyword):
        search_url = f"{self.TIKTOK_URL}/search?q={keyword}"
        response = self._request(search_url)

        topics = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            video_elems = soup.select("div.tiktok-x6y88p-DivItemContainerV2")
            for video in video_elems:
                desc_elem = video.select_one("div.tiktok-1itcwxg-ImgPoster")
                topic = {
                    "platform": "tiktok",
                    "keyword": keyword,
                    "description": desc_elem.get_text(strip=True) if desc_elem else "",
                    "data_source": "tiktok",
                }
                topics.append(topic)

        return topics

    def crawl_wgsn(self, category):
        try:
            result = self.retry_handler.execute_with_retry(
                self._crawl_wgsn_impl, category
            )
            return result
        except Exception as e:
            logger.error("Failed to crawl WGSN for '%s': %s", category, str(e))
            return {"category": category, "data_source": "wgsn", "error": str(e)}

    def _crawl_wgsn_impl(self, category):
        search_url = f"{self.WGSN_URL}/en/fashion-insight/{category}"
        response = self._request(search_url)

        result = {
            "category": category,
            "trend_themes": [],
            "color_palettes": [],
            "key_items": [],
            "materials": [],
            "data_source": "wgsn",
        }

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            theme_elems = soup.select("div.trend-theme h3")
            result["trend_themes"] = [t.get_text(strip=True) for t in theme_elems]

            color_elems = soup.select("div.color-palette span.color-name")
            result["color_palettes"] = [c.get_text(strip=True) for c in color_elems]

            item_elems = soup.select("div.key-item span.item-name")
            result["key_items"] = [i.get_text(strip=True) for i in item_elems]

            material_elems = soup.select("div.material-info span.material-name")
            result["materials"] = [m.get_text(strip=True) for m in material_elems]

        return result
