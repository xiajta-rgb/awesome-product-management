from sqlalchemy.orm import sessionmaker

from src.common.database import (
    engine,
    RawProductData,
    CleanedProductData,
    SystemLog,
)


class DataManager:
    MAIN_CATEGORIES = ["business_casual", "casual_sport", "workwear_outdoor"]

    def __init__(self):
        self.Session = sessionmaker(bind=engine)

    def view_raw_data(self, category_main=None, category_sub=None, limit=100):
        session = self.Session()
        try:
            query = session.query(RawProductData)
            if category_main:
                query = query.filter(RawProductData.title.contains(category_main))
            if category_sub:
                query = query.filter(RawProductData.title.contains(category_sub))
            query = query.order_by(RawProductData.created_at.desc())
            query = query.limit(limit)
            results = query.all()
            data = []
            for row in results:
                data.append({
                    "id": row.id,
                    "title": row.title,
                    "url": row.url,
                    "features": row.features,
                    "sales_rank": row.sales_rank,
                    "price_range": row.price_range,
                    "stock_status": row.stock_status,
                    "seller_type": row.seller_type,
                    "data_source": row.data_source,
                    "listing_date": row.listing_date.isoformat() if row.listing_date else None,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                })
            return data
        finally:
            session.close()

    def view_cleaned_data(self, category_main=None, category_sub=None, limit=100):
        session = self.Session()
        try:
            query = session.query(CleanedProductData)
            if category_main:
                query = query.filter(CleanedProductData.category_main == category_main)
            if category_sub:
                query = query.filter(CleanedProductData.category_sub == category_sub)
            query = query.order_by(CleanedProductData.created_at.desc())
            query = query.limit(limit)
            results = query.all()
            data = []
            for row in results:
                data.append({
                    "id": row.id,
                    "title": row.title,
                    "url": row.url,
                    "standardized_features": row.standardized_features,
                    "monthly_sales": row.monthly_sales,
                    "sales_rank": row.sales_rank,
                    "price": row.price,
                    "stock_status": row.stock_status,
                    "seller_type": row.seller_type,
                    "category_main": row.category_main,
                    "category_sub": row.category_sub,
                    "sales_tier": row.sales_tier,
                    "pain_points": row.pain_points,
                    "compliance_status": row.compliance_status,
                    "data_source": row.data_source,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                })
            return data
        finally:
            session.close()

    def export_to_excel(self, data_type, output_path, category_main=None, category_sub=None):
        if data_type == "raw":
            data = self.view_raw_data(
                category_main=category_main,
                category_sub=category_sub,
                limit=100000,
            )
            headers = [
                "id", "title", "url", "features", "sales_rank",
                "price_range", "stock_status", "seller_type",
                "data_source", "listing_date", "created_at",
            ]
        elif data_type == "cleaned":
            data = self.view_cleaned_data(
                category_main=category_main,
                category_sub=category_sub,
                limit=100000,
            )
            headers = [
                "id", "title", "url", "standardized_features", "monthly_sales",
                "sales_rank", "price", "stock_status", "seller_type",
                "category_main", "category_sub", "sales_tier", "pain_points",
                "compliance_status", "data_source", "created_at",
            ]
        else:
            return None
        try:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = data_type
            ws.append(headers)
            for row_data in data:
                row_values = [row_data.get(h, "") for h in headers]
                ws.append(row_values)
            wb.save(output_path)
            return output_path
        except ImportError:
            import csv
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for row_data in data:
                    writer.writerow({h: row_data.get(h, "") for h in headers})
            return output_path

    def view_crawl_logs(self, status=None, limit=100):
        session = self.Session()
        try:
            query = session.query(SystemLog).filter(
                SystemLog.log_type.in_(["crawl", "daily_crawl", "weekly_crawl"])
            )
            if status:
                query = query.filter(SystemLog.status == status)
            query = query.order_by(SystemLog.created_at.desc())
            query = query.limit(limit)
            results = query.all()
            logs = []
            for row in results:
                logs.append({
                    "id": row.id,
                    "log_type": row.log_type,
                    "log_content": row.log_content,
                    "status": row.status,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                })
            return logs
        finally:
            session.close()

    def filter_by_category(self, data, category_main=None, category_sub=None):
        filtered = data
        if category_main:
            filtered = [
                d for d in filtered
                if d.get("category_main") == category_main
            ]
        if category_sub:
            filtered = [
                d for d in filtered
                if d.get("category_sub") == category_sub
            ]
        return filtered
