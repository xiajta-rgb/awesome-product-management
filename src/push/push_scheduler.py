from apscheduler.schedulers.background import BackgroundScheduler

from src.push.channels import PushChannelManager
from src.push.content_builder import ContentBuilder
from src.push.element_push import ElementPushBuilder
from src.push.pitfall_push import PitfallPushBuilder
from src.push.product_push import ProductPushBuilder
from src.push.uniqueness_push import UniquenessPushBuilder


class PushScheduler:

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.content_builder = ContentBuilder()
        self.product_push_builder = ProductPushBuilder()
        self.element_push_builder = ElementPushBuilder()
        self.pitfall_push_builder = PitfallPushBuilder()
        self.uniqueness_push_builder = UniquenessPushBuilder()
        self.channel_manager = PushChannelManager()

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()

    def add_daily_push(self, hour: int = 8):
        self.scheduler.add_job(
            self._execute_daily_push,
            "cron",
            hour=hour,
            minute=0,
            id="daily_push",
            replace_existing=True,
        )

    def add_weekly_push(self, day_of_week: str = "mon"):
        self.scheduler.add_job(
            self._execute_weekly_push,
            "cron",
            day_of_week=day_of_week,
            hour=9,
            minute=0,
            id="weekly_push",
            replace_existing=True,
        )

    def trigger_manual_push(self, push_type: str, user_id: str):
        push_builders = {
            "daily_digest": self._execute_daily_push,
            "weekly_push": self._execute_weekly_push,
        }
        builder = push_builders.get(push_type)
        if builder:
            content = builder()
            channels = self.channel_manager._get_user_channel_preference(user_id)
            for channel in channels:
                self.channel_manager.push(channel, content, user_id)

    def _execute_daily_push(self):
        market_trends = self.content_builder.build_market_trends([])
        compliance_alerts = self.content_builder.build_compliance_alerts([])
        external_trends = self.content_builder.build_external_trends_summary([])
        supply_alerts = self.content_builder.build_supply_chain_alerts([])
        daily_digest = self.content_builder.build_daily_digest(
            market_trends, compliance_alerts, external_trends, supply_alerts
        )
        return daily_digest

    def _execute_weekly_push(self):
        hit_products = self.product_push_builder.build_hit_product_list([])
        potential_products = self.product_push_builder.build_potential_product_list([])
        pitfall_reminders = self.pitfall_push_builder.build_pitfall_reminders([])
        uniqueness_recs = self.uniqueness_push_builder.build_uniqueness_recommendations(
            [], []
        )
        weekly_elements = self.element_push_builder.build_weekly_element_report(
            [], [], []
        )
        return {
            "push_type": "weekly_push",
            "hit_products": hit_products,
            "potential_products": potential_products,
            "pitfall_reminders": pitfall_reminders,
            "uniqueness_recommendations": uniqueness_recs,
            "weekly_elements": weekly_elements,
        }
