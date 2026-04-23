#!/usr/bin/env python3
"""
GoPro pricing: launch price vs current price. That's it.
Older tech should get cheaper. Is it?
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "output"
OUTPUT.mkdir(exist_ok=True)

# Real data: Smartprix Apr 23 2026, CamelCamelCamel
models = [
    ("Hero 5\n(2016)", 399.99, 389.00),
    ("Hero 9\n(2020)", 349.99, 299.00),
    ("Hero 10\n(2021)", 399.99, 449.24),
    ("Hero 11\n(2022)", 399.99, 589.95),
    ("Hero 12\n(2023)", 399.99, 319.99),
    ("Hero 13\n(2024)", 399.99, 379.00),
]

names = [m[0] for m in models]
launch = [m[1] for m in models]
current = [m[2] for m in models]
diff = [c - l for l, c in zip(launch, current)]

fig, ax = plt.subplots(figsize=(10, 6))
x = range(len(names))
width = 0.35

bars_launch = ax.bar([i - width/2 for i in x], launch, width, label="Launch Price", color="#2196F3")
bars_current = ax.bar([i + width/2 for i in x], current, width, label="Price Today (Apr 2026)", color="#F44336")

# Add labels
for bar in bars_launch:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
            f"${bar.get_height():.0f}", ha="center", fontsize=9, color="#2196F3")
for i, bar in enumerate(bars_current):
    color = "#B71C1C" if diff[i] > 0 else "#2E7D32"
    sign = "+" if diff[i] > 0 else ""
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
            f"${bar.get_height():.0f}\n({sign}${diff[i]:.0f})", ha="center", fontsize=9,
            color=color, fontweight="bold")

ax.set_ylabel("Price ($)")
ax.set_title("GoPro: What You Paid at Launch vs. What It Costs Today\nOlder tech should get cheaper. It's not.", fontsize=13)
ax.set_xticks(x)
ax.set_xticklabels(names)
ax.legend(loc="upper left")
ax.set_ylim(0, 700)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%.0f"))
ax.grid(axis="y", alpha=0.2)

plt.tight_layout()
out = OUTPUT / "gopro_pricing.png"
plt.savefig(out, dpi=150)
print(f"📊 Saved to {out}")
