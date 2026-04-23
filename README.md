# Corporate Inflation Tracker

**Hypothesis:** Short-term corporate profits are inflated by smoke-and-mirrors tactics — price increases on aging products, shrinkflation, quality degradation, and service cuts — rather than genuine growth or innovation.

## The GoPro Test

A GoPro Hero 10 costs $50 more today than it did 18 months ago, despite being 3-4 generations old. In a healthy market, older tech gets cheaper. When it gets more expensive, something else is going on.

This repo tests whether that pattern is widespread.

## What We're Measuring

| Signal | Data Source | What It Shows |
|--------|------------|---------------|
| Old-gen product price increases | CamelCamelCamel, Wayback Machine | Products getting more expensive instead of depreciating |
| Shrinkflation | BLS CPI microdata, unit sizes | Same price, less product |
| Margin expansion vs. revenue growth | SEC EDGAR, FRED | Profits growing faster than sales = squeezing customers |
| Quality degradation | Amazon review trends, NHTSA complaints, Consumer Reports | Cutting corners to protect margins |
| Real vs. nominal earnings | FRED, S&P data | How much "growth" is just price passthrough |

## Project Structure

```
data/           # Raw and processed datasets
scripts/        # Data collection and analysis scripts
notebooks/      # Jupyter notebooks for exploration
output/         # Charts, tables, findings
```

## Getting Started

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Contributors

- John Muirhead-Gould ([@JonIsGold](https://x.com/JonIsGold))
- John Finizio

## License

MIT
