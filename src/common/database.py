from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RawProductData(Base):
    __tablename__ = "raw_product_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    features = Column(Text)
    sales_rank = Column(Integer)
    price_range = Column(String(100))
    stock_status = Column(String(50))
    seller_type = Column(String(50))
    promotions = Column(Text)
    related_products = Column(Text)
    listing_date = Column(DateTime)
    data_source = Column(String(100))
    main_image_url = Column(String(1000))
    detail_image_urls = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class CleanedProductData(Base):
    __tablename__ = "cleaned_product_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    standardized_features = Column(JSON)
    monthly_sales = Column(Integer)
    sales_rank = Column(Integer)
    price = Column(Float)
    stock_status = Column(String(50))
    seller_type = Column(String(50))
    category_main = Column(String(100))
    category_sub = Column(String(100))
    sales_tier = Column(String(50))
    pain_points = Column(Text)
    compliance_status = Column(String(50))
    data_source = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)


class TrendData(Base):
    __tablename__ = "trend_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    element_type = Column(String(100), nullable=False)
    element_value = Column(String(200), nullable=False)
    standardized_tag = Column(String(200))
    category = Column(String(100))
    trend_cycle = Column(String(50))
    heat_level = Column(String(50))
    data_source = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class RuleFile(Base):
    __tablename__ = "rule_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(200), nullable=False)
    rule_content_json = Column(JSON)
    version = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class UserPreference(Base):
    __tablename__ = "user_preference"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False)
    gender_focus = Column(String(50))
    category_focus = Column(String(200))
    heat_preference = Column(String(50))
    uniqueness_threshold = Column(Float)
    push_channels = Column(String(200))
    push_frequency = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class PushRecord(Base):
    __tablename__ = "push_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False)
    push_type = Column(String(50))
    push_content = Column(Text)
    push_channel = Column(String(50))
    push_status = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)


class SystemLog(Base):
    __tablename__ = "system_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_type = Column(String(50), nullable=False)
    log_content = Column(Text)
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)


from src.common.config import DATABASE_URL

from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL, echo=False)
