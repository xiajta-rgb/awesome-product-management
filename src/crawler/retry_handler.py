import logging
import time

logger = logging.getLogger(__name__)


class RetryHandler:

    RELIABLE_SOURCES = {
        "amazon_bestseller",
        "amazon_trending",
        "google_trends",
        "wgsn",
        "pinterest",
        "statista",
        "instagram",
        "tiktok",
        "aafa_report",
        "emarketer",
    }

    def __init__(self, max_retries=2, retry_delay=5.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def execute_with_retry(self, func, *args, **kwargs):
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                last_exception = e
                logger.warning(
                    "Attempt %d/%d failed for %s: %s",
                    attempt,
                    self.max_retries,
                    func.__name__,
                    str(e),
                )
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(
                        "All %d attempts failed for %s. Pushing alert.",
                        self.max_retries,
                        func.__name__,
                    )
                    self._push_alert(func.__name__, str(last_exception))
        raise last_exception

    def _push_alert(self, func_name, error_msg):
        logger.error(
            "ALERT: Function %s failed after all retries. Error: %s",
            func_name,
            error_msg,
        )

    def validate_source(self, data):
        if not isinstance(data, dict):
            return False
        data_source = data.get("data_source", "")
        if not data_source:
            return False
        return data_source in self.RELIABLE_SOURCES

    def filter_unreliable_data(self, data_list):
        reliable = []
        for item in data_list:
            if self.validate_source(item):
                reliable.append(item)
            else:
                logger.warning(
                    "Filtered unreliable data, source: %s",
                    item.get("data_source", "unknown"),
                )
        return reliable
