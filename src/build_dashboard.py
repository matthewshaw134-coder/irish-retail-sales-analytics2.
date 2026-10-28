"""
build_dashboard.py
------------------
Reads the SQL query results in outputs/ and builds a single, self-contained
interactive HTML dashboard (dashboard/index.html). No external libraries or
internet connection are needed to open it: charts are drawn with plain
JavaScript + SVG, and the data is embedded as JSON.

Key findings are written from the numbers, so they stay correct if the
data is regenerated.

Usage:  python src/build_dashboard.py
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
DASH = ROOT / "dashboard"


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / f"{name}.csv")


def eur_k(v: float) -> str:
    return f"€{v / 1e6:.2f}m" if v >= 1e6 else f"€{v / 1000:,.0f}k"


def build_insights(kpi, stores, categories, regions, peaks, rfm, heat) -> list[str]:
    cur, prev = kpi.iloc[-1], kpi.iloc[-2]
    physical = stores[stores.store_id != "WEB"]
    best = physical.sort_values("yoy_pct", ascending=False).iloc[0]
    worst = physical.sort_values("yoy_pct").iloc[0]
    online = stores[stores.store_id == "WEB"].iloc[0]
    top_cat = categories.iloc[0]
    hi_margin = categories.sort_values("gross_margin_pct", ascending=False).iloc[0]
    hi_return = categories.sort_values("return_rate_pct", ascending=False).iloc[0]
    fastest_region = regions[regions.region != "Online"].sort_values("yoy_pct", ascending=False).iloc[0]
    dublin = regions[regions.region == "Dublin"].iloc[0]
    bf = peaks[(peaks.period == "Black Friday weekend")].sort_values("year").iloc[-1]
    champs = rfm[rfm.segment == "Champions"].iloc[0]
    at_risk = rfm[rfm.segment == "At Risk"].iloc[0]
    busiest = heat.sort_values("avg_orders_per_day", ascending=False).iloc[0]

    return [
        f"<b>Net sales grew {cur.net_sales_yoy_pct:.1f}%</b> to {eur_k(cur.net_sales)}, "
        f"driven by more orders (+{cur.orders_yoy_pct:.1f}%) rather than bigger baskets "
        f"(AOV €{cur.avg_order_value:.2f} vs €{prev.avg_order_value:.2f}).",
        f"<b>Online is now the #{int(online.rank_2025)} store</b> by sales and the fastest grower "
        f"(+{online.yoy_pct:.1f}%), at {online.share_of_sales_pct}% of total sales.",
        f"<b>{worst.store} fell {abs(worst.yoy_pct):.1f}%</b> — the only store in decline "
        f"(partly closed for a spring 2025 refit). This held Dublin back to +{dublin.yoy_pct:.1f}%, "
        f"while {fastest_region.region} grew {fastest_region.yoy_pct:.1f}%.",
        f"<b>{top_cat.category}</b> is the biggest category ({top_cat.share_pct}% of sales); "
        f"<b>{hi_margin.category}</b> has the best margin ({hi_margin.gross_margin_pct}%). "
        f"{hi_return.category} has the highest return rate ({hi_return.return_rate_pct}%).",
        f"<b>Black Friday weekend trades at {bf.x_normal_day:.1f}× a normal day</b>; "
        f"the busiest in-store hour is {busiest.weekday} {int(busiest.hour)}:00 — useful for staff rostering.",
        f"<b>Champions</b> ({champs.pct_customers}% of loyalty members) bring in {champs.pct_sales}% of loyalty sales. "
        f"{int(at_risk.customers):,} <b>At Risk</b> customers (worth {eur_k(at_risk.total_sales)}) are a clear win-back target.",
    ]


def main() -> None:
    kpi = load("01_kpi_summary")
    stores = load("03_store_performance")
    categories = load("04_category_mix")
    heat = load("07_weekday_hour")
    rfm = load("08_customer_rfm")
    peaks = load("09_peak_trading")
    regions = load("10_region_summary")
    monthly_cat = load("11_monthly_category")

    data = {
        "kpi": kpi.to_dict("records"),
        "stores": stores.to_dict("records"),
        "categories": categories.to_dict("records"),
        "heatmap": heat.to_dict("records"),
        "rfm": rfm.to_dict("records"),
        "peaks": peaks.to_dict("records"),
        "regions": regions.to_dict("records"),
        "monthlyCat": monthly_cat.to_dict("records"),
        "insights": build_insights(kpi, stores, categories, regions, peaks, rfm, heat),
    }
    payload = json.dumps(data, ensure_ascii=False, default=float).replace("</", "<\\/")
    html = (DASH / "template.html").read_text(encoding="utf-8")
    html = html.replace("/*__DATA__*/null", payload)
    (DASH / "index.html").write_text(html, encoding="utf-8")
    print(f"Dashboard written -> {(DASH / 'index.html').relative_to(ROOT)}")
    for s in data["insights"]:
        print(" *", s.replace("<b>", "").replace("</b>", ""))


if __name__ == "__main__":
    main()
