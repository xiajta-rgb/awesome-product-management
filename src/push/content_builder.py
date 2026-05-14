from datetime import datetime


class ContentBuilder:

    def build_market_trends(self, trend_data: list) -> dict:
        items = []
        for trend in trend_data:
            item = {
                "category": trend.get("category", ""),
                "sales_growth": trend.get("sales_growth", ""),
                "pricing_trend": trend.get("pricing_trend", ""),
                "data_source": trend.get("data_source", ""),
            }
            items.append(item)
        return {
            "push_type": "market_trends",
            "title": "细分赛道趋势推送",
            "content": items,
            "generated_at": datetime.now().isoformat(),
        }

    def build_compliance_alerts(self, compliance_issues: list) -> dict:
        items = []
        for issue in compliance_issues:
            item = {
                "issue_type": issue.get("issue_type", ""),
                "description": issue.get("description", ""),
                "severity": issue.get("severity", ""),
                "affected_categories": issue.get("affected_categories", []),
                "data_source": issue.get("data_source", ""),
            }
            items.append(item)
        return {
            "push_type": "compliance_alerts",
            "title": "违规预警推送",
            "content": items,
            "generated_at": datetime.now().isoformat(),
        }

    def build_external_trends_summary(self, trends: list) -> dict:
        items = []
        for trend in trends:
            item = {
                "trend_name": trend.get("trend_name", ""),
                "platform": trend.get("platform", ""),
                "heat_level": trend.get("heat_level", ""),
                "description": trend.get("description", ""),
                "data_source": trend.get("data_source", ""),
            }
            items.append(item)
        return {
            "push_type": "external_trends_summary",
            "title": "站外热门趋势汇总推送",
            "content": items,
            "generated_at": datetime.now().isoformat(),
        }

    def build_supply_chain_alerts(self, supply_data: list) -> dict:
        items = []
        for data in supply_data:
            item = {
                "alert_type": data.get("alert_type", ""),
                "material": data.get("material", ""),
                "cost_change": data.get("cost_change", ""),
                "moq_status": data.get("moq_status", ""),
                "data_source": data.get("data_source", ""),
            }
            items.append(item)
        return {
            "push_type": "supply_chain_alerts",
            "title": "供应链预警推送",
            "content": items,
            "generated_at": datetime.now().isoformat(),
        }

    def build_daily_digest(
        self,
        market_trends: dict,
        compliance_alerts: dict,
        external_trends: dict,
        supply_alerts: dict,
    ) -> dict:
        return {
            "push_type": "daily_digest",
            "title": "每日核心资讯推送",
            "market_trends": market_trends,
            "compliance_alerts": compliance_alerts,
            "external_trends": external_trends,
            "supply_alerts": supply_alerts,
            "generated_at": datetime.now().isoformat(),
        }
