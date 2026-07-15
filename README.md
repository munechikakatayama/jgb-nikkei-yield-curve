# 動的利回り曲線 (JGB Yield Curve × Nikkei 225)

An interactive tool comparing Japan's full JGB yield curve (1–10Y annually, plus 15/20/25/30/40Y) against the Nikkei 225 index over time (1985–present), inspired by [stockcharts.com's Dynamic Yield Curve](https://stockcharts.com/freecharts/yieldcurve.php).

- `index.html` / `full.html` — the tool (identical content)
- `data/jgb_nikkei_data.json` — canonical merged dataset
- `templates/template_full.html` — HTML template used to regenerate `index.html` / `full.html`
- `scripts/update_data.py` — fetches the latest JGB yields (Ministry of Finance Japan) and Nikkei 225 close (Yahoo Finance), merges new trading days, and regenerates the HTML
- `.github/workflows/update.yml` — runs `update_data.py` daily (7:00 AM JST) and commits any new data

## Features

- Full 15-maturity JGB curve; longer maturities show gaps before they existed (e.g. 40Y JGBs weren't issued until Nov 2007)
- Fixed y-axis with an explicit 0% baseline, so scale doesn't jump while scrubbing/animating
- Selectable start date for the displayed window (defaults to the earliest available data, Jan 1985)
- Optional overlay of the Bank of Japan's historical Yield Curve Control (YCC) target bands for the 10-year yield (Sept 2016 – Mar 2024)

## Data sources

- JGB yields: [Ministry of Finance Japan — Interest Rate](https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/index.htm)
- Nikkei 225: Yahoo Finance (`^N225`)

## Running the updater manually

```bash
python scripts/update_data.py  # only needs the standard library, no extra deps
```
