class BaseFilter:
    RELIABLE_SOURCES = {"amazon", "official", "verified_supplier", "brand_direct"}

    def filter(self, products):
        result = []
        for product in products:
            if self._is_slow_seller(product):
                continue
            if self._is_non_compliant(product):
                continue
            if not self._has_reliable_source(product):
                continue
            monthly_sales = product.get("monthly_sales", 0)
            if monthly_sales < 300:
                continue
            stock_status = product.get("stock_status", "")
            if stock_status not in ("in_stock", "available"):
                continue
            result.append(product)
        return result

    def _is_slow_seller(self, product):
        monthly_sales = product.get("monthly_sales", 0)
        return monthly_sales < 100

    def _is_non_compliant(self, product):
        compliance_status = product.get("compliance_status", "")
        return compliance_status != "compliant"

    def _has_reliable_source(self, product):
        data_source = product.get("data_source", "")
        if not data_source:
            return False
        source_lower = data_source.lower()
        for reliable in self.RELIABLE_SOURCES:
            if reliable in source_lower:
                return True
        return False
