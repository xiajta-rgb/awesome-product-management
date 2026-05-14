import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from src.common.config import DAILY_CRAWL_HOUR, WEEKLY_CRAWL_DAY
from src.crawler.amazon_crawler import AmazonCrawler
from src.crawler.trend_crawler import TrendCrawler
from src.crawler.anti_detect import AntiDetect
from src.crawler.retry_handler import RetryHandler

logger = logging.getLogger(__name__)


class CrawlScheduler:

    CATEGORY_URLS = {
        "business_casual": "https://www.amazon.com/s?k=business+casual+mens+clothing",
        "casual_sport": "https://www.amazon.com/s?k=casual+sport+clothing",
        "workwear_outdoor": "https://www.amazon.com/s?k=workwear+outdoor+clothing",
    }

    TREND_KEYWORDS = [
        "fashion trend 2025",
        "business casual outfit",
        "outdoor workwear",
        "athleisure men",
        "casual sportswear",
    ]

    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.amazon_crawler = AmazonCrawler()
        self.trend_crawler = TrendCrawler()
        self.anti_detect = AntiDetect()
        self.retry_handler = RetryHandler()

    def start(self):
        logger.info("Starting crawl scheduler")
        self.scheduler.start()

    def stop(self):
        logger.info("Stopping crawl scheduler")
        self.scheduler.shutdown(wait=False)

    def add_daily_job(self, hour=2):
        self.scheduler.add_job(
            self._execute_daily_crawl,
            "cron",
            hour=hour,
            minute=0,
            id="daily_crawl",
            replace_existing=True,
        )
        logger.info("Daily crawl job scheduled at hour %d", hour)

    def add_weekly_job(self, day_of_week="mon"):
        self.scheduler.add_job(
            self._execute_weekly_crawl,
            "cron",
            day_of_week=day_of_week,
            hour=3,
            minute=0,
            id="weekly_crawl",
            replace_existing=True,
        )
        logger.info("Weekly crawl job scheduled on %s", day_of_week)

    def trigger_manual_crawl(self, crawl_type):
        if crawl_type == "daily":
            self._execute_daily_crawl()
        elif crawl_type == "weekly":
            self._execute_weekly_crawl()
        else:
            logger.warning("Unknown crawl type: %s", crawl_type)

    def _execute_daily_crawl(self):
        logger.info("Executing daily crawl")
        all_products = []
        for category, url in self.CATEGORY_URLS.items():
            try:
                products = self.amazon_crawler.crawl_category(url)
                all_products.extend(products)
                logger.info("Daily crawl: %d products from %s", len(products), category)
            except Exception as e:
                logger.error("Daily crawl failed for %s: %s", category, str(e))

        for keyword in self.TREND_KEYWORDS[:2]:
            try:
                trend_data = self.trend_crawler.crawl_google_trends(keyword)
                logger.info("Daily crawl: Google Trends data for '%s'", keyword)
            except Exception as e:
                logger.error("Daily crawl Google Trends failed for '%s': %s", keyword, str(e))

        reliable_products = self.retry_handler.filter_unreliable_data(all_products)
        logger.info("Daily crawl complete: %d reliable products", len(reliable_products))

    def _execute_weekly_crawl(self):
        logger.info("Executing weekly full crawl")
        all_products = []
        for category, url in self.CATEGORY_URLS.items():
            try:
                products = self.amazon_crawler.crawl_category(url)
                all_products.extend(products)
                logger.info("Weekly crawl: %d products from %s", len(products), category)
            except Exception as e:
                logger.error("Weekly crawl failed for %s: %s", category, str(e))

        for keyword in self.TREND_KEYWORDS:
            try:
                trend_data = self.trend_crawler.crawl_google_trends(keyword)
                logger.info("Weekly crawl: Google Trends for '%s'", keyword)
            except Exception as e:
                logger.error("Weekly crawl Google Trends failed for '%s': %s", keyword, str(e))

        for keyword in self.TREND_KEYWORDS:
            try:
                pinterest_data = self.trend_crawler.crawl_pinterest(keyword)
                logger.info("Weekly crawl: Pinterest for '%s'", keyword)
            except Exception as e:
                logger.error("Weekly crawl Pinterest failed for '%s': %s", keyword, str(e))

        for platform in ["instagram", "tiktok"]:
            for keyword in self.TREND_KEYWORDS[:3]:
                try:
                    social_data = self.trend_crawler.crawl_social_media(platform, keyword)
                    logger.info("Weekly crawl: %s for '%s'", platform, keyword)
                except Exception as e:
                    logger.error("Weekly crawl %s failed for '%s': %s", platform, keyword, str(e))

        for category in ["business_casual", "casual_sport", "workwear_outdoor"]:
            try:
                wgsn_data = self.trend_crawler.crawl_wgsn(category)
                logger.info("Weekly crawl: WGSN for '%s'", category)
            except Exception as e:
                logger.error("Weekly crawl WGSN failed for '%s': %s", category, str(e))

        reliable_products = self.retry_handler.filter_unreliable_data(all_products)
        logger.info("Weekly crawl complete: %d reliable products", len(reliable_products))
