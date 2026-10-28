"""
run_analysis.py
---------------
Runs every query in sql/analysis/ against data/retail.db and saves each
result to outputs/<query_name>.csv. Prints a preview of each result.

Usage:  python src/run_analysis.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "retail.db"
SQL_DIR = ROOT / "sql" / "analysis"
OUT = ROOT / "outputs"


def run_all() -> dict:
    OUT.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    results = {}
    for f in sorted(SQL_DIR.glob("*.sql")):
        df = pd.read_sql_query(f.read_text(), con)
        name = f.stem
        df.to_csv(OUT / f"{name}.csv", index=False)
        results[name] = df
        print(f"\n=== {name} ({len(df)} rows) ===")
        print(df.head(8).to_string(index=False))
    con.close()
    return results


if __name__ == "__main__":
    pd.set_option("display.width", 160)
    run_all()
