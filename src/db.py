import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = "data/ecommerce.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def write_table(df: pd.DataFrame, table_name: str, if_exists: str = "replace") -> None:
    with get_conn() as conn:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    print(f"Written {len(df):,} rows → {table_name}")


def create_views() -> None:
    views = {
        "vw_monthly_revenue": """
            SELECT
                strftime('%Y-%m', order_purchase_timestamp) AS month,
                COUNT(DISTINCT o.order_id) AS order_count,
                ROUND(SUM(i.price + i.freight_value), 2) AS revenue
            FROM orders o
            JOIN items i ON o.order_id = i.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY 1
            ORDER BY 1
        """,
        "vw_top_categories": """
            SELECT
                p.category_en,
                COUNT(DISTINCT i.order_id) AS order_count,
                ROUND(SUM(i.price + i.freight_value), 2) AS revenue
            FROM items i
            JOIN products p ON i.product_id = p.product_id
            JOIN orders o ON i.order_id = o.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY 1
            ORDER BY revenue DESC
            LIMIT 10
        """,
    }
    with get_conn() as conn:
        for name, sql in views.items():
            conn.execute(f"DROP VIEW IF EXISTS {name}")
            conn.execute(f"CREATE VIEW {name} AS {sql}")
    print("Views created.")


def query(sql: str) -> pd.DataFrame:
    with get_conn() as conn:
        return pd.read_sql_query(sql, conn)


def populate_db(cleaned: dict) -> None:
    """Write cleaned DataFrames to SQLite and create SQL views."""
    table_map = {
        "orders":    cleaned["orders"],
        "items":     cleaned["items"],
        "customers": cleaned["customers"],
        "products":  cleaned["products"],
    }
    for name, df in table_map.items():
        # SQLite can't store Period dtype — convert to string first
        df_copy = df.copy()
        for col in df_copy.select_dtypes(include="period").columns:
            df_copy[col] = df_copy[col].astype(str)
        write_table(df_copy, name)
    create_views()


if __name__ == "__main__":
    # Quick test — query the monthly revenue view
    df = query("SELECT * FROM vw_monthly_revenue LIMIT 5")
    print(df)
