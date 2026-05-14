import json
import shutil
import os
from datetime import datetime


class RuleFileManager:
    DEFAULT_RULE = {
        "rule1": {
            "name": "基础筛选规则",
            "slow_seller_threshold": 100,
            "non_compliant_status": ["non_compliant", "严重风险", "banned"],
            "reliable_sources": ["amazon", "official", "verified_supplier", "brand_direct"],
            "min_monthly_sales": 300,
            "valid_stock_status": ["in_stock", "available"],
        },
        "rule2": {
            "name": "趋势匹配规则",
            "match_score_calculation": "matched_element_count / total_trend_element_count * 100",
            "match_threshold": 80,
            "valid_heat_levels": ["high", "中", "medium"],
        },
        "rule3": {
            "name": "权重打分规则",
            "weights": {
                "sales": 0.3,
                "trend": 0.25,
                "review": 0.25,
                "competition": 0.1,
                "compliance": 0.1,
            },
            "formula": "Score = (S_sales × 0.3) + (S_trend × 0.25) + (S_review × 0.25) + (S_comp × 0.1) + (S_compliance × 0.1)",
            "new_product_base_score": 15,
            "new_product_base_max": 25,
            "velocity_bonus_max": 5,
            "high_potential_threshold": 80,
            "potential_threshold": 60,
        },
        "rule4": {
            "name": "元素提取规则",
            "core_frequency_threshold": 20,
            "margin_threshold": 0.3,
            "margin_penalty_factor": 0.7,
        },
        "rule5": {
            "name": "动态优化规则",
            "update_frequency": "weekly",
            "season_weight_adjustments": {
                "spring": {"trend": 0.03, "sales": -0.02},
                "summer": {"sales": 0.03, "trend": -0.01},
                "autumn": {"trend": 0.02, "review": -0.01},
                "winter": {"sales": 0.05, "trend": 0.02, "competition": -0.03},
            },
        },
        "rule6": {
            "name": "更新规则",
            "weight_update_schedule": "weekly_monday",
            "hit_product_update_schedule": "daily",
        },
    }

    def generate_rule_file(self, weights=None):
        rule_data = json.loads(json.dumps(self.DEFAULT_RULE))
        if weights:
            rule_data["rule3"]["weights"] = weights
            total = sum(weights.values())
            if total > 0:
                normalized = {k: round(v / total, 4) for k, v in weights.items()}
                formula_parts = " + ".join(
                    [f"(S_{k} × {normalized[k]})" for k in normalized]
                )
                rule_data["rule3"]["formula"] = f"Score = {formula_parts}"
        rule_data["generated_at"] = datetime.now().isoformat()
        rule_data["version"] = "1.0"
        return rule_data

    def save_rule_file(self, rule_data, filepath):
        dir_path = os.path.dirname(filepath)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(rule_data, f, ensure_ascii=False, indent=2)

    def load_rule_file(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_rule_section(self, section, new_values, filepath):
        rule_data = self.load_rule_file(filepath)
        if section in rule_data:
            rule_data[section].update(new_values)
        else:
            rule_data[section] = new_values
        rule_data["updated_at"] = datetime.now().isoformat()
        self.save_rule_file(rule_data, filepath)
        return rule_data

    def backup_rule_file(self, filepath):
        if not os.path.exists(filepath):
            return None
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{filepath}.backup_{timestamp}"
        shutil.copy2(filepath, backup_path)
        return backup_path
