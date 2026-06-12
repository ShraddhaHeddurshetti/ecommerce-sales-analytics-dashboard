import pandas as pd
import os

RAW = "data/raw"

DATE_COLS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
}


def load_orders() -> pd.DataFrame:
    df = pd.read_csv(
        f"{RAW}/olist_orders_dataset.csv",
        parse_dates=DATE_COLS["orders"],
    )
    return df


def load_items() -> pd.DataFrame:
    return pd.read_csv(
        f"{RAW}/olist_order_items_dataset.csv",
        parse_dates=["shipping_limit_date"],
    )


def load_customers() -> pd.DataFrame:
    return pd.read_csv(f"{RAW}/olist_customers_dataset.csv")


def load_products() -> pd.DataFrame:
    return pd.read_csv(f"{RAW}/olist_products_dataset.csv")


def load_category_names() -> pd.DataFrame:
    return pd.read_csv(f"{RAW}/product_category_name_translation.csv")


def load_reviews() -> pd.DataFrame:
    return pd.read_csv(f"{RAW}/olist_order_reviews_dataset.csv")


def load_all() -> dict:
    """Returns dict of all raw DataFrames."""
    return {
        "orders":    load_orders(),
        "items":     load_items(),
        "customers": load_customers(),
        "products":  load_products(),
        "cat_names": load_category_names(),
        "reviews":   load_reviews(),
    }


if __name__ == "__main__":
    dfs = load_all()
    for name, df in dfs.items():
        print(f"{name}: {df.shape} | nulls: {df.isnull().sum().sum()}")
