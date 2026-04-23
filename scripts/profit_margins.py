#!/usr/bin/env python3
"""
S&P 500 / Corporate profit margin expansion analysis.

Tests: Are corporate profits growing faster than the economy?
If yes, the gap = how much companies are extracting via pricing power vs real growth.

Data: FRED (Federal Reserve Economic Data) — no API key needed for CSV export.
"""

import csv
import io
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import requests

OUTPUT = Path(__file__).resolve().parent.parent / "output"
DATA = Path(__file__).resolve().parent.parent / "data"
OUTPUT.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)


def fetch_fred(series_id, start="2000-01-01", end="2026-04-01"):
    """Fetch a FRED series as CSV, return list of (date, value) tuples."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={start}&coed={end}"
    r = requests.get(url)
    r.raise_for_status()
    rows = []
    reader = csv.reader(io.StringIO(r.text))
    next(reader)  # skip header
    for row in reader:
        try:
            dt = datetime.strptime(row[0], "%Y-%m-%d")
            val = float(row[1])
            rows.append((dt, val))
        except (ValueError, IndexError):
            continue
    return rows


def align_quarterly(series_a, series_b):
    """Align two series by quarter (use date as key)."""
    b_map = {d.strftime("%Y-%m"): v for d, v in series_b}
    aligned = []
    for d, a_val in series_a:
        key = d.strftime("%Y-%m")
        if key in b_map:
            aligned.append((d, a_val, b_map[key]))
    return aligned


def main():
    print("📥 Fetching FRED data...")
    cp = fetch_fred("CP")          # Corporate Profits After Tax ($B, quarterly, SAAR)
    gdp = fetch_fred("GDP")        # GDP ($B, quarterly, SAAR)
    cpi = fetch_fred("CPIAUCSL")   # CPI (monthly)

    print(f"   Corporate Profits: {len(cp)} quarters")
    print(f"   GDP: {len(gdp)} quarters")
    print(f"   CPI: {len(cpi)} months")

    # Compute profit share of GDP
    aligned = align_quarterly(cp, gdp)
    dates = [a[0] for a in aligned]
    profit_share = [a[1] / a[2] * 100 for a in aligned]  # as percentage

    # Compute indexed growth (2019 Q1 = 100)
    base_idx = next(i for i, a in enumerate(aligned) if a[0].year == 2019 and a[0].month == 1)
    cp_indexed = [a[1] / aligned[base_idx][1] * 100 for a in aligned]
    gdp_indexed = [a[2] / aligned[base_idx][2] * 100 for a in aligned]

    # CPI indexed to Jan 2019
    cpi_base_idx = next(i for i, (d, v) in enumerate(cpi) if d.year == 2019 and d.month == 1)
    cpi_dates = [d for d, v in cpi]
    cpi_indexed = [v / cpi[cpi_base_idx][1] * 100 for d, v in cpi]

    # Print key stats
    print(f"\n{'='*60}")
    print("Corporate Profits as % of GDP")
    print(f"{'='*60}")
    print(f"2000 Q1: {profit_share[0]:.1f}%")
    pre_covid = next(ps for d, ps in zip(dates, profit_share) if d.year == 2019 and d.month == 10)
    print(f"2019 Q4 (pre-COVID): {pre_covid:.1f}%")
    print(f"Latest ({dates[-1].strftime('%Y Q%q').replace('Q%q', 'Q'+str((dates[-1].month-1)//3+1))}): {profit_share[-1]:.1f}%")
    print(f"Change since 2019: {profit_share[-1] - pre_covid:+.1f} percentage points")

    # Growth comparison
    print(f"\nGrowth since 2019 Q1 (indexed):")
    print(f"  Corporate Profits: {cp_indexed[-1]:.0f} ({cp_indexed[-1]-100:+.0f}%)")
    print(f"  GDP:               {gdp_indexed[-1]:.0f} ({gdp_indexed[-1]-100:+.0f}%)")
    print(f"  CPI:               {cpi_indexed[-1]:.0f} ({cpi_indexed[-1]-100:+.0f}%)")
    print(f"  Profit growth MINUS GDP growth: {(cp_indexed[-1]-100)-(gdp_indexed[-1]-100):+.0f} pp")
    print(f"  Profit growth MINUS inflation:  {(cp_indexed[-1]-100)-(cpi_indexed[-1]-100):+.0f} pp")

    # --- Chart 1: Profit share of GDP ---
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    ax1 = axes[0]
    ax1.fill_between(dates, profit_share, alpha=0.3, color="#F44336")
    ax1.plot(dates, profit_share, color="#F44336", linewidth=2)
    ax1.set_ylabel("Corporate Profits as % of GDP")
    ax1.set_title("Corporate Profit Share of GDP (2000–2025)\nHigher = companies capturing more of the economy")
    ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax1.axhline(y=pre_covid, color="gray", linestyle="--", alpha=0.5, label=f"Pre-COVID ({pre_covid:.1f}%)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # --- Chart 2: Indexed growth comparison ---
    ax2 = axes[1]
    ax2.plot(dates, cp_indexed, color="#F44336", linewidth=2.5, label="Corporate Profits")
    ax2.plot(dates, gdp_indexed, color="#2196F3", linewidth=2.5, label="GDP")
    ax2.plot(cpi_dates, cpi_indexed, color="#FF9800", linewidth=1.5, alpha=0.7, label="CPI (Inflation)")
    ax2.axhline(y=100, color="gray", linestyle="--", alpha=0.3)
    ax2.axvline(x=datetime(2020, 3, 1), color="gray", linestyle=":", alpha=0.5, label="COVID")
    ax2.set_ylabel("Index (2019 Q1 = 100)")
    ax2.set_title("Profits vs. GDP vs. Inflation — Indexed to 2019\n\"If profits grow faster than GDP, the difference is extraction\"")
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    out_path = OUTPUT / "profit_vs_gdp.png"
    plt.savefig(out_path, dpi=150)
    print(f"\n📊 Chart saved to {out_path}")

    # Save raw data
    csv_path = DATA / "fred_profit_gdp.csv"
    with open(csv_path, "w") as f:
        f.write("date,corporate_profits_B,gdp_B,profit_share_pct\n")
        for d, cp_val, gdp_val in aligned:
            f.write(f"{d.strftime('%Y-%m-%d')},{cp_val},{gdp_val},{cp_val/gdp_val*100:.2f}\n")
    print(f"💾 Data saved to {csv_path}")


if __name__ == "__main__":
    main()
