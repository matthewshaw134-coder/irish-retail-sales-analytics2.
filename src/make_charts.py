"""
make_charts.py
--------------
Static PNG charts (matplotlib) for the README / reports.

Usage:  python src/make_charts.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

BLUE, GREY, RED, INK, MUTED = "#2a78d6", "#a9a79f", "#c9302c", "#0b0b0b", "#52514e"
plt.rcParams.update({
    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#cfcdc6", "axes.labelcolor": MUTED, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.grid": True, "grid.color": "#ebe9e3", "axes.axisbelow": True,
    "figure.dpi": 150,
})
euro_k = mtick.FuncFormatter(lambda v, _: f"€{v / 1000:,.0f}k")


def monthly_trend():
    df = pd.read_csv(OUT / "02_monthly_trend.csv")
    fig, ax = plt.subplots(figsize=(9, 4))
    for yr, c, lw in [(2024, GREY, 2), (2025, BLUE, 2.2)]:
        d = df[df.year == yr]
        ax.plot(d.month_name, d.net_sales, color=c, lw=lw, label=str(yr), marker="o", ms=4)
    ax.yaxis.set_major_formatter(euro_k)
    ax.set_title("Monthly net sales, 2025 vs 2024", loc="left", color=INK, fontweight="bold")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(CHARTS / "monthly_trend.png")
    plt.close(fig)


def store_league():
    df = pd.read_csv(OUT / "03_store_performance.csv").iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [RED if v < 0 else BLUE for v in df.yoy_pct]
    ax.barh(df.store, df.sales_2025, color=colors, height=0.65)
    for y, (v, g) in enumerate(zip(df.sales_2025, df.yoy_pct)):
        ax.text(v + 5000, y, f"€{v / 1000:,.0f}k  ({g:+.1f}%)", va="center", fontsize=8.5, color=MUTED)
    ax.xaxis.set_major_formatter(euro_k)
    ax.set_xlim(0, df.sales_2025.max() * 1.25)
    ax.grid(axis="y", visible=False)
    ax.set_title("Store net sales 2025 (change vs 2024)", loc="left", color=INK, fontweight="bold")
    fig.tight_layout()
    fig.savefig(CHARTS / "store_league.png")
    plt.close(fig)


def category_mix():
    df = pd.read_csv(OUT / "04_category_mix.csv").iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.barh(df.category, df.share_pct, color=BLUE, height=0.6)
    for y, (s, m) in enumerate(zip(df.share_pct, df.gross_margin_pct)):
        ax.text(s + 0.4, y, f"{s}% of sales · {m}% margin", va="center", fontsize=8.5, color=MUTED)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.set_xlim(0, df.share_pct.max() * 1.45)
    ax.grid(axis="y", visible=False)
    ax.set_title("Category share of net sales, 2025", loc="left", color=INK, fontweight="bold")
    fig.tight_layout()
    fig.savefig(CHARTS / "category_mix.png")
    plt.close(fig)


def heatmap():
    df = pd.read_csv(OUT / "07_weekday_hour.csv")
    order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    pv = df.pivot(index="weekday", columns="hour", values="avg_orders_per_day").reindex(order)
    fig, ax = plt.subplots(figsize=(9, 3.4))
    im = ax.imshow(pv.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(pv.columns)), [f"{h}:00" for h in pv.columns], fontsize=8)
    ax.set_yticks(range(len(order)), order)
    ax.grid(False)
    fig.colorbar(im, ax=ax, label="avg orders / day")
    ax.set_title("In-store orders by weekday and hour, 2025", loc="left", color=INK, fontweight="bold")
    fig.tight_layout()
    fig.savefig(CHARTS / "footfall_heatmap.png")
    plt.close(fig)


if __name__ == "__main__":
    monthly_trend()
    store_league()
    category_mix()
    heatmap()
    print(f"Charts saved -> {CHARTS.relative_to(ROOT)}")
