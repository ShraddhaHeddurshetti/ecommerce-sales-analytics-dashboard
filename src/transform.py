import pandas as pd
import numpy as np


def get_master_df(orders, items, customers, products) -> pd.DataFrame:
    """Join all tables into one analysis-ready DataFrame."""
    df = (
        orders
        .merge(items, on="order_id", how="inner")
        .merge(customers, on="customer_id", how="left")
        .merge(products[["product_id", "category_en"]], on="product_id", how="left")
    )
    return df


def monthly_revenue(master: pd.DataFrame) -> pd.DataFrame:
    """Returns monthly revenue with MoM growth %."""
    result = (
        master[master["is_delivered"]]
        .groupby("order_month")
        .agg(
            revenue=("item_total", "sum"),
            order_count=("order_id", "nunique"),
        )
        .reset_index()
    )
    result["order_month"] = result["order_month"].astype(str)
    result["mom_growth"] = result["revenue"].pct_change() * 100
    result["aov"] = result["revenue"] / result["order_count"]
    return result


def top_categories(master: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top N categories by revenue."""
    return (
        master[master["is_delivered"]]
        .groupby("category_en")
        .agg(revenue=("item_total", "sum"), orders=("order_id", "nunique"))
        .reset_index()
        .sort_values("revenue", ascending=False)
        .head(n)
    )


def revenue_by_state(master: pd.DataFrame) -> pd.DataFrame:
    return (
        master[master["is_delivered"]]
        .groupby("customer_state")
        .agg(revenue=("item_total", "sum"), customers=("customer_id", "nunique"))
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


def headline_kpis(master: pd.DataFrame, orders: pd.DataFrame) -> dict:
    delivered = master[master["is_delivered"]]
    total_revenue = delivered["item_total"].sum()
    total_orders = delivered["order_id"].nunique()
    aov = total_revenue / total_orders if total_orders else 0

    customer_counts = (
        delivered.groupby("customer_id")["order_id"].nunique()
    )
    repeat_rate = (customer_counts > 1).mean() * 100

    avg_delivery = orders[orders["is_delivered"]]["delivery_days"].mean()
    on_time_rate = (~orders[orders["is_delivered"]]["is_late"]).mean() * 100

    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "aov": round(aov, 2),
        "repeat_rate": round(repeat_rate, 2),
        "avg_delivery_days": round(avg_delivery, 1),
        "on_time_rate": round(on_time_rate, 1),
    }
