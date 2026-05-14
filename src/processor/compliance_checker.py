INFRINGEMENT_KEYWORDS = [
    "nike",
    "adidas",
    "gucci",
    "louis vuitton",
    "lv",
    "chanel",
    "prada",
    "hermes",
    "dior",
    "versace",
    "balenciaga",
    "yeezy",
    "jordan",
    "supreme",
    "off-white",
    "puma",
    "new balance",
    "under armour",
    "the north face",
    "patagonia",
    "耐克",
    "阿迪达斯",
    "古驰",
    "路易威登",
    "香奈儿",
    "普拉达",
    "爱马仕",
    "迪奥",
    "范思哲",
    "巴黎世家",
]


class ComplianceChecker:

    COMPLIANCE_RULES = [
        {
            "rule_id": "missing_size_label",
            "description": "No size label found",
            "severity": "violation",
        },
        {
            "rule_id": "material_mismatch",
            "description": "Material label inconsistency",
            "severity": "violation",
        },
        {
            "rule_id": "infringement_risk",
            "description": "Potential trademark infringement",
            "severity": "violation",
        },
    ]

    def check_compliance(self, product):
        issues = []
        if not self._check_size_label(product):
            issues.append("missing_size_label")
        if not self._check_material_label(product):
            issues.append("material_mismatch")
        if not self._check_infringement(product):
            issues.append("infringement_risk")
        is_compliant = len(issues) == 0
        if len(issues) >= 2:
            risk_level = "high"
        elif len(issues) == 1:
            risk_level = "medium"
        else:
            risk_level = "low"
        return {
            "is_compliant": is_compliant,
            "issues": issues,
            "risk_level": risk_level,
        }

    def filter_non_compliant(self, product_list):
        result = []
        for product in product_list:
            compliance = self.check_compliance(product)
            if compliance["is_compliant"]:
                result.append(product)
        return result

    def _check_size_label(self, product):
        features = product.get("standardized_features", {})
        if isinstance(features, dict):
            size_info = features.get("size", [])
            if size_info:
                return True
        title = product.get("title", "") or ""
        size_keywords = [
            "size",
            "尺码",
            "码",
            "S",
            "M",
            "L",
            "XL",
            "XXL",
            "small",
            "medium",
            "large",
        ]
        title_upper = title.upper()
        for kw in size_keywords:
            if kw.upper() in title_upper:
                return True
        features_str = product.get("features", "") or ""
        for kw in size_keywords:
            if kw.upper() in features_str.upper():
                return True
        return False

    def _check_material_label(self, product):
        features = product.get("standardized_features", {})
        if not isinstance(features, dict):
            return True
        material_tags = features.get("material", [])
        title = product.get("title", "") or ""
        features_str = product.get("features", "") or ""
        if not material_tags and not title and not features_str:
            return True
        if not material_tags:
            return True
        return True

    def _check_infringement(self, product):
        title = (product.get("title", "") or "").lower()
        features = (product.get("features", "") or "").lower()
        text = f"{title} {features}"
        for keyword in INFRINGEMENT_KEYWORDS:
            if keyword.lower() in text:
                return False
        return True
