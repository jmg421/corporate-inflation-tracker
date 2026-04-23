#!/usr/bin/env python3
"""
One chart. One message.
Since 2019, corporate profits grew 85%. The economy grew 49%.
Where did the extra 36% come from? You.
"""

import csv
import io
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import requests

OUTPUT = Path(__file__).resolve().parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)


def fetch_fred(series_id, start="2014-01-01", end="2026-04-01"):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={start}&coed={end}"
    r = requests.get(url)
    rows = []
    reader = csv.reader(io.StringIO(r.text))
    next(reader)
    for row in reader:
        try:
            rows.append((datetime.strptime(row[0], "%Y-%m-%d"), float(row[1])))
        except (ValueError, IndexError):
            continue
    return rows


def main():
    cp = fetch_fred("CP")    # Corporate Profits ($B quarterly)
    gdp = fetch_fred("GDP")  # GDP ($B quarterly)

    # Align by date
    gdp_map = {d.strftime("%Y-%m"): v for d, v in gdp}
    aligned = [(d, v, gdp_map[d.strftime("%Y-%m")]) for d, v in cp if d.strftime("%Y-%m") in gdp_map]

    # Index to 2019 Q1 = 100
    base = next(i for i, (d, _, _) in enumerate(aligned) if d.year == 2019 and d.month == 1)
    dates = [a[0] for a in aligned]
    cp_idx = [a[1] / aligned[base][1] * 100 for a in aligned]
    gdp_idx = [a[2] / aligned[base][2] * 100 for a in aligned]

    # The chart
    fig, ax = plt.subplots(figsize=(11, 6))

    ax.plot(dates, gdp_idx, color="#2196F3", linewidth=3, label="The Economy (GDP)")
    ax.plot(dates, cp_idx, color="#F44336", linewidth=3, label="Corporate Profits")

    # Shade the gap after COVID
    covid_idx = next(i for i, d in enumerate(dates) if d.year == 2020 and d.month == 4)
    ax.fill_between(dates[covid_idx:], cp_idx[covid_idx:], gdp_idx[covid_idx:],
                     alpha=0.2, color="#F44336", label="The gap (what's coming out of your pocket)")

    # Annotate the endpoints
    ax.annotate(f"Profits: +{cp_idx[-1]-100:.0f}%", xy=(dates[-1], cp_idx[-1]),
                xytext=(15, 5), textcoords="offset points", fontsize=12,
                fontweight="bold", color="#B71C1C")
    ax.annotate(f"Economy: +{gdp_idx[-1]-100:.0f}%", xy=(dates[-1], gdp_idx[-1]),
                xytext=(15, -15), textcoords="offset points", fontsize=12,
                fontweight="bold", color="#1565C0")

    # COVID marker
    ax.axvline(x=datetime(2020, 3, 1), color="gray", linestyle=":", alpha=0.4)
    ax.text(datetime(2020, 5, 1), max(cp_idx) * 0.95, "COVID", fontsize=9, color="gray")

    # Baseline
    ax.axhline(y=100, color="gray", linestyle="--", alpha=0.3)

    ax.set_title("Corporate Profits Are Growing Almost Twice as Fast as the Economy\nSince 2019, the gap keeps widening", fontsize=14)
    ax.set_ylabel("Growth Since 2019 (2019 = 100)")
    ax.legend(loc="upper left", fontsize=11)
    ax.grid(axis="y", alpha=0.2)

    plt.tight_layout()
    out = OUTPUT / "profit_vs_gdp.png"
    plt.savefig(out, dpi=150)
    print(f"📊 Saved to {out}")


if __name__ == "__main__":
    main()
