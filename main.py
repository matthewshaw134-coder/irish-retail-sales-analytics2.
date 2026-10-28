"""
main.py — runs the whole pipeline end to end.

    python main.py

1. Generate synthetic raw data        (src/generate_data.py)
2. Clean it and load into SQLite      (src/clean_load.py)
3. Run the SQL analysis queries       (src/run_analysis.py)
4. Make static charts for the README  (src/make_charts.py)
5. Build the interactive dashboard    (src/build_dashboard.py)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import build_dashboard  # noqa: E402
import clean_load       # noqa: E402
import generate_data    # noqa: E402
import make_charts      # noqa: E402
import run_analysis     # noqa: E402

if __name__ == "__main__":
    print("\n[1/5] Generating data");        generate_data.main()
    print("\n[2/5] Cleaning + loading");     clean_load.main()
    print("\n[3/5] Running SQL analysis");   run_analysis.run_all()
    print("\n[4/5] Making charts")
    make_charts.monthly_trend(); make_charts.store_league()
    make_charts.category_mix(); make_charts.heatmap()
    print("\n[5/5] Building dashboard");     build_dashboard.main()
    print("\nAll done. Open dashboard/index.html in your browser.")
