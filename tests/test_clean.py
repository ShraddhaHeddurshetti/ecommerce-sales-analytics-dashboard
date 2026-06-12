import pandas as pd
import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.clean import clean_orders, clean_items, clean_products


# ── Fixtures ──────────────────────────────────────────────────
@pytest.fixture
def sample_orders():
    return pd.DataFrame({
        "order_id": ["o1", "o2", "o3", "o1"],   # o1 is duplicate
        "customer_id": ["c1", "c2", "c3", "c1"],
        "order_status": ["delivered", "shipped", "canceled", "delivered"],
        "order_purchase_timestamp": pd.to_datetime(["2018-01-01", "2018-02-01", "2018-03-01", "2018-01-01"]),
        "order_delivered_customer_date": pd.to_datetime(["2018-01-10", "NaT", "NaT", "2018-01-10"]),
        "order_estimated_delivery_date": pd.to_datetime(["2018-01-15", "2018-02-20", "NaT", "2018-01-15"]),
        "order_delivered_carrier_date": pd.to_datetime(["2018-01-05", "NaT", "NaT", "2018-01-05"]),
        "order_approved_at": pd.to_datetime(["2018-01-01", "2018-02-01", "2018-03-01", "2018-01-01"]),
    })


@pytest.fixture
def sample_items():
    return pd.DataFrame({
        "order_id": ["o1", "o2", "o3"],
        "order_item_id": [1, 1, 1],
        "product_id": ["p1", "p2", "p3"],
        "seller_id": ["s1", "s2", "s3"],
        "price": [100.0, -5.0, 5000.0],   # -5 is invalid, 5000 is outlier
        "freight_value": [10.0, 5.0, 50.0],
        "shipping_limit_date": pd.to_datetime(["2018-01-05", "2018-02-05", "2018-03-05"]),
    })


@pytest.fixture
def sample_products():
    return pd.DataFrame({
        "product_id": ["p1", "p2"],
        "product_category_name": ["cama_mesa_banho", "informatica_acessorios"],
        "product_weight_g": [300.0, np.nan],
        "product_length_cm": [20.0, np.nan],
        "product_height_cm": [10.0, np.nan],
        "product_width_cm": [15.0, np.nan],
    })


@pytest.fixture
def sample_cat_names():
    return pd.DataFrame({
        "product_category_name": ["cama_mesa_banho", "informatica_acessorios"],
        "product_category_name_english": ["bed_bath_table", "computers_accessories"],
    })


# ── Tests ─────────────────────────────────────────────────────
def test_clean_orders_removes_duplicates(sample_orders):
    cleaned = clean_orders(sample_orders)
    assert cleaned["order_id"].duplicated().sum() == 0


def test_clean_orders_row_count_after_dedup(sample_orders):
    cleaned = clean_orders(sample_orders)
    assert len(cleaned) == 3  # o1 deduped from 4 rows


def test_clean_orders_adds_delivery_days(sample_orders):
    cleaned = clean_orders(sample_orders)
    assert "delivery_days" in cleaned.columns


def test_clean_orders_is_delivered_flag(sample_orders):
    cleaned = clean_orders(sample_orders)
    assert cleaned[cleaned["order_status"] == "delivered"]["is_delivered"].all()


def test_clean_orders_adds_order_month(sample_orders):
    cleaned = clean_orders(sample_orders)
    assert "order_month" in cleaned.columns


def test_clean_items_removes_negative_prices(sample_items):
    cleaned = clean_items(sample_items)
    assert (cleaned["price"] > 0).all()


def test_clean_items_correct_row_count(sample_items):
    cleaned = clean_items(sample_items)
    assert len(cleaned) == 2  # -5 row removed


def test_clean_items_adds_item_total(sample_items):
    cleaned = clean_items(sample_items)
    assert "item_total" in cleaned.columns
    assert cleaned[cleaned["price"] == 100.0]["item_total"].iloc[0] == 110.0  # 100 + 10


def test_clean_items_flags_outliers(sample_items):
    cleaned = clean_items(sample_items)
    assert "is_price_outlier" in cleaned.columns
    assert cleaned[cleaned["price"] == 5000.0]["is_price_outlier"].iloc[0] is True


def test_clean_products_adds_category_en(sample_products, sample_cat_names):
    cleaned = clean_products(sample_products, sample_cat_names)
    assert "category_en" in cleaned.columns


def test_clean_products_fills_missing_dims(sample_products, sample_cat_names):
    cleaned = clean_products(sample_products, sample_cat_names)
    assert cleaned["product_weight_g"].isnull().sum() == 0
    assert cleaned["product_length_cm"].isnull().sum() == 0
