import random
import time
import logging

logger = logging.getLogger(__name__)


class AntiDetect:

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/105.0.0.0",
    ]

    PROXY_POOL = [
        {"http": "", "https": ""},
    ]

    def __init__(self):
        self._current_ua_index = 0
        self._proxies = list(self.PROXY_POOL)

    def get_random_headers(self):
        headers = {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }
        return headers

    def get_proxy(self):
        if not self._proxies:
            return {}
        proxy = random.choice(self._proxies)
        return proxy

    def random_delay(self, min_sec=1.0, max_sec=3.0):
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def rotate_user_agent(self):
        self._current_ua_index = (self._current_ua_index + 1) % len(self.USER_AGENTS)
        return self.USER_AGENTS[self._current_ua_index]

    def handle_captcha(self, response):
        captcha_indicators = [
            "captcha",
            "robot",
            "enter the characters",
            "Type the characters",
            "api-services-support@amazon.com",
        ]
        if response and hasattr(response, "text"):
            text_lower = response.text.lower()
            for indicator in captcha_indicators:
                if indicator.lower() in text_lower:
                    logger.warning("Captcha detected: %s", indicator)
                    return True
        return False
