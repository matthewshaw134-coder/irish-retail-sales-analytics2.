"""
clean_load.py
-------------
Cleans the raw CSV exports and loads them into a SQLite database
(data/retail.db) using the schema in sql/schema.sql.

Cleaning steps (each one is logged so the data-quality story is visible):
  1. Standardise payment-method text (case / trailing spaces)
  2. Remove duplicate orders exported twice from the POS (by order_id)
  3. Standardise county names in the customer master ("Co. cork" -> "Cork")
  4. Drop order lines with missing quantities
  5. Fix negative quantities (POS keying errors) by taking the absolute value
  6. Remove order lines that no longer have a parent order
  7. Build an Irish calendar dimension, including public holidays

Usage:  python src/clean_load.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "retail.db"
SCHEMA = ROOT / "sql" / "schema.sql"
LOG_PATH = ROOT / "outputs" / "data_quality_log.csv"

log = []


def note(step: str, rows_affected: int) -> None:
    log.append({"step": step, "rows_affected": int(rows_affected)})
    print(f"  - {step}: {rows_affected:,}")


def irish_bank_holidays(years) -> set:
    """Irish public holidays (fixed dates + 'first Monday' rules + Easter Monday)."""
    hol = set()
    easter = {2024: "2024-03-31", 2025: "2025-04-20"}

    def first_monday(y, m):
        d = pd.Timestamp(y, m, 1)
        return d + pd.Timedelta(days=(7 - d.weekday()) % 7)

    def last_monday(y, m):
        d = pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0)
        return d - pd.Timedelta(days=d.weekday())

    for y in years:
        hol |= {pd.Timestamp(y, 1, 1), pd.Timestamp(y, 3, 17),
                pd.Timestamp(y, 12, 25), pd.Timestamp(y, 12, 26)}
        # St Brigid's Day: first Monday in Feb, or 1 Feb if it falls on a Friday
        feb1 = pd.Timestamp(y, 2, 1)
        hol.add(feb1 if feb1.weekday() == 4 else first_monday(y, 2))
        hol.add(pd.Timestamp(easter[y]) + pd.Timedelta(days=1))  # Easter Monday
        hol |= {first_monday(y, 5), first_monday(y, 6), first_monday(y, 8),
                last_monday(y, 10)}
    return {d.date() for d in hol}


def build_calendar(start: str, end: str) -> pd.DataFrame:
    d = pd.date_range(start, end, freq="D")
    hols = irish_bank_holidays(sorted(set(d.year)))
    return pd.DataFrame({
        "date": d.date,
        "year": d.year,
        "quarter": d.quarter,
        "month": d.month,
        "month_name": d.strftime("%b"),
        "iso_week": d.isocalendar().week.to_numpy(),
        "weekday": d.strftime("%a"),
        "is_weekend": (d.weekday >= 5).astype(int),
        "is_bank_holiday": [int(x in hols) for x in d.date],
    })


def main() -> None:
    print("Loading raw files...")
    stores = pd.read_csv(RAW / "stores.csv", keep_default_na=False)
    products = pd.read_csv(RAW / "products.csv")
    customers = pd.read_csv(RAW / "customers.csv")
    orders = pd.read_csv(RAW / "orders.csv")
    items = pd.read_csv(RAW / "order_items.csv")
    note("raw orders loaded", len(orders))
    note("raw order lines loaded", len(items))

    print("Cleaning...")
    bad_pay = orders.payment_method.str.strip().ne(orders.payment_method) | \
        orders.payment_method.str.isupper()
    canonical = {m.upper(): m for m in orders.loc[~bad_pay, "payment_method"].unique()}
    orders["payment_method"] = orders.payment_method.str.strip().str.upper().map(canonical)
    note("payment methods standardised", bad_pay.sum())

    # De-duplicate AFTER standardising text, keyed on the business key
    before = len(orders)
    orders = orders.drop_duplicates(subset="order_id", keep="first")
    note("duplicate orders removed", before - len(orders))

    messy = customers.county.str.startswith("Co. ")
    customers["county"] = customers.county.str.replace(r"^Co\.\s*", "", regex=True).str.title()
    note("county names standardised", messy.sum())

    missing_qty = items.quantity.isna()
    items = items[~missing_qty].copy()
    note("order lines with missing quantity dropped", missing_qty.sum())

    neg = items.quantity < 0
    items.loc[neg, "quantity"] = items.loc[neg, "quantity"].abs()
    items["quantity"] = items.quantity.astype(int)
    note("negative quantities corrected", neg.sum())

    orphan = ~items.order_id.isin(orders.order_id)
    items = items[~orphan]
    note("orphan order lines removed", orphan.sum())

    orders["order_date"] = orders.order_datetime.str[:10]
    calendar = build_calendar(orders.order_date.min(), orders.order_date.max())

    print("Writing SQLite database...")
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA.read_text())
    stores.to_sql("stores", con, if_exists="append", index=False)
    products.to_sql("products", con, if_exists="append", index=False)
    customers.to_sql("customers", con, if_exists="append", index=False)
    calendar.to_sql("calendar", con, if_exists="append", index=False)
    orders[["order_id", "order_datetime", "order_date", "store_id", "customer_id",
            "channel", "payment_method"]].to_sql("orders", con, if_exists="append", index=False)
    items.to_sql("order_items", con, if_exists="append", index=False)
    con.commit()

    n = con.execute("SELECT COUNT(*) FROM v_sales_lines").fetchone()[0]
    con.close()
    note("clean order lines in database", n)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(log).to_csv(LOG_PATH, index=False)
    print(f"Done -> {DB_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
