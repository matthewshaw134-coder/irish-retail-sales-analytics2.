"""
generate_data.py
----------------
Generates a realistic *synthetic* sales dataset for a fictional Irish
multi-store retailer ("Clover & Co.") covering Jan 2024 - Dec 2025.

The data deliberately includes seasonality (Christmas, Black Friday,
January sales, back-to-school, St Patrick's weekend), regional
differences, an online channel, returns, and a handful of realistic
data-quality problems (duplicates, missing values, inconsistent text)
so that the cleaning step in clean_load.py has real work to do.

Output: data/raw/stores.csv, products.csv, customers.csv,
        orders.csv, order_items.csv

Usage:  python src/generate_data.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

START, END = "2024-01-01", "2025-12-31"

# ---------------------------------------------------------------------------
# Stores: (id, name, town, county, region, size_factor, opened)
# ---------------------------------------------------------------------------
STORES = [
    ("S01", "Grafton Street", "Dublin", "Dublin", "Dublin", 1.60, "2015-03-01"),
    ("S02", "Dundrum", "Dublin", "Dublin", "Dublin", 1.35, "2016-09-01"),
    ("S03", "Blanchardstown", "Dublin", "Dublin", "Dublin", 1.25, "2017-04-01"),
    ("S04", "Liffey Valley", "Dublin", "Dublin", "Dublin", 1.15, "2018-06-01"),
    ("S05", "Patrick Street", "Cork", "Cork", "Munster", 1.20, "2016-02-01"),
    ("S06", "Shop Street", "Galway", "Galway", "Connacht", 0.95, "2017-11-01"),
    ("S07", "O'Connell Street", "Limerick", "Limerick", "Munster", 0.85, "2018-03-01"),
    ("S08", "John Roberts Square", "Waterford", "Waterford", "Munster", 0.70, "2019-05-01"),
    ("S09", "High Street", "Kilkenny", "Kilkenny", "Leinster", 0.60, "2019-08-01"),
    ("S10", "Golden Island", "Athlone", "Westmeath", "Leinster", 0.62, "2020-10-01"),
    ("S11", "O'Connell Street", "Sligo", "Sligo", "Connacht", 0.50, "2021-04-01"),
    ("S12", "Marshes", "Dundalk", "Louth", "Leinster", 0.65, "2021-09-01"),
    ("WEB", "Online Store", "Online", "N/A", "Online", 1.40, "2015-03-01"),
]

# ---------------------------------------------------------------------------
# Products: category -> list of (name, price_incl_vat, margin_pct)
# ---------------------------------------------------------------------------
CATALOGUE = {
    "Womenswear": [
        ("Wool Blend Coat", 129.0, 0.58), ("Knit Jumper", 49.0, 0.62),
        ("Midi Dress", 59.0, 0.60), ("Slim Jeans", 45.0, 0.55),
        ("Linen Shirt", 35.0, 0.60), ("Puffer Jacket", 89.0, 0.55),
    ],
    "Menswear": [
        ("Waxed Jacket", 139.0, 0.55), ("Aran Jumper", 69.0, 0.60),
        ("Oxford Shirt", 39.0, 0.60), ("Chinos", 45.0, 0.55),
        ("Rain Jacket", 79.0, 0.52), ("Crew Neck T-Shirt", 15.0, 0.65),
    ],
    "Kidswear": [
        ("School Uniform Set", 30.0, 0.40), ("Kids Raincoat", 32.0, 0.50),
        ("Kids Hoodie", 22.0, 0.55), ("Pyjama Set", 18.0, 0.58),
    ],
    "Footwear": [
        ("Leather Boots", 110.0, 0.50), ("Running Trainers", 85.0, 0.45),
        ("Wellington Boots", 35.0, 0.50), ("School Shoes", 45.0, 0.42),
        ("Slippers", 20.0, 0.60),
    ],
    "Homeware": [
        ("Merino Throw", 75.0, 0.62), ("Scented Candle", 18.0, 0.70),
        ("Cotton Bed Set", 65.0, 0.58), ("Ceramic Mug Set", 24.0, 0.65),
        ("Christmas Decoration Set", 28.0, 0.68),
    ],
    "Beauty": [
        ("Hand Cream Gift Set", 25.0, 0.62), ("Perfume 50ml", 65.0, 0.45),
        ("Skincare Starter Kit", 39.0, 0.55), ("Lip Balm Trio", 12.0, 0.68),
    ],
    "Accessories": [
        ("Tweed Cap", 35.0, 0.62), ("Wool Scarf", 29.0, 0.66),
        ("Leather Wallet", 45.0, 0.60), ("Umbrella", 19.0, 0.62),
        ("Gloves", 22.0, 0.64),
    ],
}

# Category seasonality by month (1..12): multipliers around 1.0
CATEGORY_SEASON = {
    "Womenswear":  [0.9, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 0.9, 1.0, 1.1, 1.3, 1.5],
    "Menswear":    [0.9, 0.8, 0.9, 1.0, 1.0, 1.0, 0.9, 0.9, 1.0, 1.1, 1.3, 1.5],
    "Kidswear":    [0.7, 0.7, 0.8, 0.9, 0.9, 1.0, 1.4, 2.2, 1.2, 0.9, 1.0, 1.3],
    "Footwear":    [0.9, 0.8, 0.9, 1.0, 1.0, 1.0, 1.2, 1.8, 1.1, 1.1, 1.2, 1.3],
    "Homeware":    [0.8, 0.7, 0.8, 0.8, 0.9, 0.8, 0.8, 0.8, 0.9, 1.1, 1.6, 2.4],
    "Beauty":      [0.7, 1.1, 1.2, 0.9, 1.0, 0.9, 0.9, 0.9, 0.9, 1.0, 1.6, 2.6],
    "Accessories": [0.9, 0.8, 0.8, 0.8, 0.8, 0.7, 0.7, 0.8, 1.0, 1.2, 1.5, 2.0],
}

# Overall monthly traffic (orders per day multiplier)
MONTH_TRAFFIC = [0.95, 0.80, 0.90, 0.92, 0.95, 0.95, 1.00, 1.05, 0.95, 1.00, 1.25, 1.55]
WEEKDAY_TRAFFIC = [0.80, 0.80, 0.85, 0.95, 1.10, 1.40, 1.10]  # Mon..Sun

BASE_ORDERS_PER_STORE_DAY = 11.0
YEAR_GROWTH = {2024: 1.00, 2025: 1.07}  # ~7% like-for-like growth in 2025

PAYMENT_STORE = (["Contactless", "Chip & PIN", "Cash", "Apple/Google Pay"],
                 [0.48, 0.22, 0.12, 0.18])
PAYMENT_WEB = (["Card", "PayPal", "Apple/Google Pay", "Klarna"],
               [0.52, 0.20, 0.20, 0.08])

COUNTY_WEIGHTS = {
    "Dublin": 0.30, "Cork": 0.12, "Galway": 0.06, "Limerick": 0.05,
    "Kildare": 0.05, "Meath": 0.04, "Wicklow": 0.03, "Waterford": 0.03,
    "Kilkenny": 0.03, "Louth": 0.03, "Westmeath": 0.02, "Sligo": 0.02,
    "Tipperary": 0.03, "Wexford": 0.03, "Kerry": 0.03, "Clare": 0.02,
    "Donegal": 0.03, "Mayo": 0.02, "Laois": 0.02, "Offaly": 0.02,
}


def black_friday_date(year: int) -> pd.Timestamp:
    """Day after the 4th Thursday of November (US Thanksgiving)."""
    nov = pd.Timestamp(year=year, month=11, day=1)
    first_thu = nov + pd.Timedelta(days=(3 - nov.weekday()) % 7)
    return first_thu + pd.Timedelta(weeks=3, days=1)


def special_day_boost(d: pd.Timestamp) -> float:
    """Extra traffic on Irish retail calendar moments."""
    boost = 1.0
    # Black Friday weekend (Fri-Sun) and Cyber Monday
    black_friday = black_friday_date(d.year)
    if black_friday <= d <= black_friday + pd.Timedelta(days=3):
        boost *= 2.1
    # Final Christmas shopping week
    if d.month == 12 and 15 <= d.day <= 23:
        boost *= 1.6
    if d.month == 12 and d.day == 24:
        boost *= 1.2
    if d.month == 12 and d.day in (25, 26):
        boost *= 0.0          # shops closed Christmas Day / St Stephen's Day
    # St Stephen's Day online + January sales
    if (d.month == 12 and d.day >= 27) or (d.month == 1 and d.day <= 10):
        boost *= 1.35
    # St Patrick's weekend (tourism bump)
    if d.month == 3 and 15 <= d.day <= 18:
        boost *= 1.25
    return boost


def discount_rate(d: pd.Timestamp) -> float:
    """Average promotional discount by period."""
    black_friday = black_friday_date(d.year)
    if black_friday <= d <= black_friday + pd.Timedelta(days=3):
        return 0.25
    if (d.month == 12 and d.day >= 27) or (d.month == 1 and d.day <= 31):
        return 0.30
    if d.month == 7:
        return 0.20                       # summer sale
    return 0.0


def build_products() -> pd.DataFrame:
    rows, i = [], 1
    for cat, items in CATALOGUE.items():
        for name, price, margin in items:
            rows.append({
                "product_id": f"P{i:03d}",
                "product_name": name,
                "category": cat,
                "unit_price": price,                       # incl. 23% VAT
                "unit_cost": round(price / 1.23 * (1 - margin), 2),  # ex VAT
            })
            i += 1
    return pd.DataFrame(rows)


def build_customers(n: int = 18000) -> pd.DataFrame:
    counties = list(COUNTY_WEIGHTS)
    w = np.array(list(COUNTY_WEIGHTS.values()))
    w = w / w.sum()
    signup = pd.to_datetime("2019-01-01") + pd.to_timedelta(
        rng.integers(0, (pd.Timestamp(END) - pd.Timestamp("2019-01-01")).days, n), "D")
    df = pd.DataFrame({
        "customer_id": [f"C{i:05d}" for i in range(1, n + 1)],
        "county": rng.choice(counties, n, p=w),
        "age_band": rng.choice(["18-24", "25-34", "35-44", "45-54", "55-64", "65+"], n,
                               p=[0.14, 0.24, 0.22, 0.18, 0.13, 0.09]),
        "loyalty_tier": rng.choice(["Bronze", "Silver", "Gold"], n, p=[0.62, 0.28, 0.10]),
        "signup_date": signup.date,
    })
    return df


def main() -> None:
    stores = pd.DataFrame(STORES, columns=[
        "store_id", "store_name", "town", "county", "region", "size_factor", "opened_date"])
    products = build_products()
    customers = build_customers()

    cat_names = list(CATALOGUE)
    prods_by_cat = {c: products[products.category == c] for c in cat_names}
    # Category mix (base share of picks)
    cat_base = np.array([0.22, 0.17, 0.09, 0.14, 0.15, 0.10, 0.13])

    # Gold members shop more often -> weight customer selection by tier
    tier_w = customers.loyalty_tier.map({"Bronze": 1.0, "Silver": 1.8, "Gold": 3.2}).to_numpy()
    tier_w = tier_w / tier_w.sum()
    cust_ids = customers.customer_id.to_numpy()
    # Pre-sample a large pool of customer picks (much faster than per-order sampling)
    cust_pool = rng.choice(cust_ids, 400_000, p=tier_w)
    cust_ptr = 0
    prod_arrays = {c: (df.product_id.to_numpy(), df.unit_price.to_numpy())
                   for c, df in prods_by_cat.items()}

    dates = pd.date_range(START, END, freq="D")
    orders, items = [], []
    order_no, line_no = 100000, 1

    for d in dates:
        day_mult = (MONTH_TRAFFIC[d.month - 1] * WEEKDAY_TRAFFIC[d.weekday()]
                    * special_day_boost(d) * YEAR_GROWTH[d.year])
        disc = discount_rate(d)
        season = np.array([CATEGORY_SEASON[c][d.month - 1] for c in cat_names])
        cat_p = cat_base * season
        cat_p = cat_p / cat_p.sum()

        for s in STORES:
            sid, size = s[0], s[5]
            is_web = sid == "WEB"
            mult = day_mult
            if is_web:
                # Online keeps trading over Christmas; grows faster in 2025
                if d.month == 12 and d.day in (25, 26):
                    mult = MONTH_TRAFFIC[11] * 1.8 * YEAR_GROWTH[d.year]
                if d.year == 2025:
                    mult *= 1.10
            elif sid == "S04" and d.year == 2025 and 3 <= d.month <= 5:
                mult *= 0.55        # Liffey Valley refurbishment (partial closure)
            n_orders = rng.poisson(BASE_ORDERS_PER_STORE_DAY * size * mult)
            if n_orders == 0:
                continue

            pay_opts, pay_p = PAYMENT_WEB if is_web else PAYMENT_STORE
            for _ in range(n_orders):
                order_no += 1
                # ~55% of in-store / 95% online orders linked to a loyalty customer
                has_cust = rng.random() < (0.95 if is_web else 0.55)
                cust = None
                if has_cust:
                    cust = cust_pool[cust_ptr % len(cust_pool)]
                    cust_ptr += 1
                hour = int(rng.choice(range(9, 21), p=np.array(
                    [3, 5, 7, 9, 10, 10, 10, 10, 11, 10, 9, 6]) / 100)) if not is_web \
                    else int(rng.integers(0, 24))
                ts = d + pd.Timedelta(hours=hour, minutes=int(rng.integers(0, 60)))
                orders.append({
                    "order_id": f"ORD{order_no}",
                    "order_datetime": ts.strftime("%Y-%m-%d %H:%M"),
                    "store_id": sid,
                    "customer_id": cust,
                    "channel": "Online" if is_web else "In-store",
                    "payment_method": rng.choice(pay_opts, p=pay_p),
                })
                n_lines = 1 + rng.poisson(0.8 if not is_web else 1.1)
                for cat in rng.choice(cat_names, n_lines, p=cat_p):
                    ids, prices = prod_arrays[cat]
                    k = rng.integers(0, len(ids))
                    qty = 1 + int(rng.random() < 0.15) + int(rng.random() < 0.04)
                    line_disc = disc if (disc and rng.random() < 0.7) else 0.0
                    return_p = 0.09 if is_web else 0.025
                    if cat in ("Womenswear", "Footwear"):
                        return_p *= 1.6
                    items.append({
                        "line_id": line_no,
                        "order_id": f"ORD{order_no}",
                        "product_id": ids[k],
                        "quantity": qty,
                        "unit_price": prices[k],
                        "discount_pct": line_disc,
                        "returned": int(rng.random() < return_p),
                    })
                    line_no += 1

    orders = pd.DataFrame(orders)
    items = pd.DataFrame(items)

    # ---------------- Inject realistic data-quality issues ----------------
    # 1) Duplicate order rows (double-exported from POS)
    dup = orders.sample(frac=0.004, random_state=SEED)
    orders = pd.concat([orders, dup]).sort_values("order_datetime").reset_index(drop=True)
    # 2) Inconsistent payment method text
    idx = orders.sample(frac=0.02, random_state=SEED + 1).index
    orders.loc[idx, "payment_method"] = orders.loc[idx, "payment_method"].str.upper() + " "
    # 3) Missing quantities on a few lines
    idx = items.sample(frac=0.003, random_state=SEED + 2).index
    items.loc[idx, "quantity"] = np.nan
    # 4) A few negative quantities (POS keying errors)
    idx = items.sample(frac=0.001, random_state=SEED + 3).index
    items.loc[idx, "quantity"] = -items.loc[idx, "quantity"].abs()
    # 5) Messy county text in customer master
    idx = customers.sample(frac=0.03, random_state=SEED + 4).index
    customers.loc[idx, "county"] = "Co. " + customers.loc[idx, "county"].str.lower()

    stores.to_csv(RAW / "stores.csv", index=False)
    products.to_csv(RAW / "products.csv", index=False)
    customers.to_csv(RAW / "customers.csv", index=False)
    orders.to_csv(RAW / "orders.csv", index=False)
    items.to_csv(RAW / "order_items.csv", index=False)

    print(f"stores={len(stores)} products={len(products)} customers={len(customers)} "
          f"orders={len(orders):,} order_items={len(items):,}")


if __name__ == "__main__":
    main()
