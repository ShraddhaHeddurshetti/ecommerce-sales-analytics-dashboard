import pandas as pd
import numpy as np
import os

PROCESSED = "data/processed"
os.makedirs(PROCESSED, exist_ok=True)


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Drop duplicate order_ids (keep first)
    df = df.drop_duplicates(subset=["order_id"], keep="first")

    # 2. Keep only delivered & approved orders for revenue analysis
    #    but keep all statuses for the status breakdown chart
    df["is_delivered"] = df["order_status"] == "delivered"

    # 3. Delivery days (only for delivered orders)
    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.days

    # 4. Flag late deliveries
    df["is_late"] = (
        df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]
    )

    # 5. Month period column for time series
    df["order_month"] = df["order_purchase_timestamp"].dt.to_period("M")

    # 6. Assert no nulls in critical columns
    critical = ["order_id", "customer_id", "order_status", "order_purchase_timestamp"]
    for col in critical:
        null_count = df[col].isnull().sum()
        assert null_count == 0, f"Null found in {col}: {null_count} rows"

    return df


def clean_items(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Remove negative prices (data error)
    before = len(df)
    df = df[df["price"] > 0].copy()
    print(f"Removed {before - len(df)} rows with price <= 0")

    # 2. Total value per item
    df["item_total"] = df["price"] + df["freight_value"]

    # 3. Flag price outliers (> 3 std devs) — keep but mark
    mean_p = df["price"].mean()
    std_p = df["price"].std()
    df["is_price_outlier"] = df["price"] > (mean_p + 3 * std_p)
    n_outliers = df["is_price_outlier"].sum()
    print(f"Price outliers flagged: {n_outliers}")

    return df


def clean_products(df: pd.DataFrame, cat_names: pd.DataFrame) -> pd.DataFrame:
    # 1. Join English category names
    df = df.merge(cat_names, on="product_category_name", how="left")

    # 2. Fill missing English names with original Portuguese
    df["category_en"] = df["product_category_name_english"].fillna(
        df["product_category_name"]
    )

    # 3. Fill missing numeric product dimensions with median
    dim_cols = [
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
    for col in dim_cols:
        df[col] = df[col].fillna(df[col].median())

    return df


def save_processed(df: pd.DataFrame, name: str) -> None:
    path = f"{PROCESSED}/{name}.parquet"
    df.to_parquet(path, index=False)
    print(f"Saved {name} → {path} ({len(df):,} rows)")


def run_cleaning(dfs: dict) -> dict:
    cleaned = {}
    cleaned["orders"]    = clean_orders(dfs["orders"])
    cleaned["items"]     = clean_items(dfs["items"])
    cleaned["products"]  = clean_products(dfs["products"], dfs["cat_names"])
    cleaned["customers"] = dfs["customers"].copy()  # already clean
    cleaned["reviews"]   = dfs["reviews"].drop_duplicates(subset=["review_id"])

    for name, df in cleaned.items():
        save_processed(df, name)

    return cleaned
