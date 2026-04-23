#!/usr/bin/env python3
"""
GoPro pricing analysis — test case for the corporate inflation hypothesis.

Compares launch MSRP vs current/recent pricing across GoPro generations.
In a normal tech market, older models get cheaper. If they get more expensive, something's wrong.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)

# GoPro Hero pricing data — launch MSRP and observed recent prices
# Sources: GoPro press releases, Smartprix/Amazon Apr 23 2026, CamelCamelCamel
GOPRO_DATA = {
    "Hero 5 Black": {
        "launch_date": "Oct 2016",
        "launch_msrp": 399.99,
        "current_price": 389.00,  # Smartprix Apr 2026
        "generation": 5,
        "note": "10 years old, still selling near launch price",
    },
    "Hero 9 Black": {
        "launch_date": "Sep 2020",
        "launch_msrp": 349.99,
        "current_price": 299.00,  # Smartprix Apr 2026
        "generation": 9,
    },
    "Hero 10 Black": {
        "launch_date": "Sep 2021",
        "launch_msrp": 399.99,
        "current_price": 449.24,  # CamelCamelCamel avg Amazon price (out of stock now)
        "generation": 10,
        "note": "John Finizio's original observation: $50 more than 18 months ago despite being 3-4 gens old. CCC avg Amazon price used (currently out of stock).",
    },
    "Hero 11 Black": {
        "launch_date": "Sep 2022",
        "launch_msrp": 399.99,
        "current_price": 589.95,  # Smartprix Apr 2026
        "generation": 11,
        "note": "47% ABOVE launch price despite being 4 generations old",
    },
    "Hero 12 Black": {
        "launch_date": "Sep 2023",
        "launch_msrp": 399.99,
        "current_price": 319.99,  # Smartprix Apr 2026
        "generation": 12,
    },
    "Hero 13 Black": {
        "launch_date": "Sep 2024",
        "launch_msrp": 399.99,
        "current_price": 379.00,  # Smartprix Apr 2026
        "generation": 13,
    },
}

# What SHOULD happen: older tech depreciates ~20-30% per generation
# What IS happening: prices stay flat or increase on older models

def expected_depreciation(launch_price, gens_old, rate=0.20):
    """Normal tech depreciation: ~20% per generation."""
    return launch_price * ((1 - rate) ** gens_old)


def main():
    current_gen = 13
    
    print("=" * 70)
    print("GoPro Pricing Analysis — Corporate Inflation Test Case")
    print("=" * 70)
    print()
    print(f"{'Model':<20} {'Launch':<10} {'Expected':<12} {'Actual':<12} {'Delta':<10} {'Gens Old'}")
    print("-" * 74)
    
    models = []
    launch_prices = []
    expected_prices = []
    actual_prices = []
    
    for name, d in GOPRO_DATA.items():
        gens_old = current_gen - d["generation"]
        expected = expected_depreciation(d["launch_msrp"], gens_old)
        
        # Use best available actual price
        actual = d.get("current_price") or d.get("camel_avg_amazon") or d.get("camel_avg_3p_new")
        if actual is None:
            continue
            
        delta = actual - expected
        delta_pct = (delta / expected) * 100
        
        print(f"{name:<20} ${d['launch_msrp']:<8.2f} ${expected:<10.2f} ${actual:<10.2f} +${delta:<7.2f} {gens_old}")
        
        models.append(f"Hero {d['generation']}\n({gens_old}gen old)")
        launch_prices.append(d["launch_msrp"])
        expected_prices.append(expected)
        actual_prices.append(actual)
    
    print()
    print("Expected = launch MSRP depreciated 20% per generation (normal tech curve)")
    print("Actual = current/recent observed price")
    print("Delta = how much MORE you're paying than you should be")
    
    # Build chart
    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(models))
    width = 0.25
    
    bars1 = ax.bar([i - width for i in x], launch_prices, width, label="Launch MSRP", color="#2196F3", alpha=0.8)
    bars2 = ax.bar(x, expected_prices, width, label="Expected (20%/gen depreciation)", color="#4CAF50", alpha=0.8)
    bars3 = ax.bar([i + width for i in x], actual_prices, width, label="Actual Recent Price", color="#F44336", alpha=0.8)
    
    ax.set_ylabel("Price ($)")
    ax.set_title("GoPro Pricing: Expected Depreciation vs. Reality\n\"Why is a 4-year-old camera more expensive than when it launched?\"")
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%.0f"))
    ax.set_ylim(0, 550)
    
    # Add value labels on bars
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"${height:.0f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)
    
    plt.tight_layout()
    out_path = OUTPUT / "gopro_pricing.png"
    plt.savefig(out_path, dpi=150)
    print(f"\n📊 Chart saved to {out_path}")
    
    # Save data
    data_path = OUTPUT / "gopro_pricing.json"
    with open(data_path, "w") as f:
        json.dump(GOPRO_DATA, f, indent=2)
    print(f"💾 Data saved to {data_path}")


if __name__ == "__main__":
    main()
