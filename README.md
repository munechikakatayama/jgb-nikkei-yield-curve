# 動的利回り曲線 (JGB Yield Curve × Nikkei 225)

An interactive tool comparing Japan's JGB yield curve against the Nikkei 225 index over time (2007–present), inspired by [stockcharts.com's Dynamic Yield Curve](https://stockcharts.com/freecharts/yieldcurve.php).

- `index.html` — landing page
- `simple.html` — 6-maturity version (1, 2, 5, 10, 20, 30Y)
- `full.html` — 15-maturity version (1–10Y annually, plus 15, 20, 25, 30, 40Y)
- `data/jgb_nikkei_data.json` — canonical merged dataset
- `templates/` — HTML templates used to regenerate `simple.html` / `full.html`
- `scripts/update_data.py` — fetches the latest JGB yields (Ministry of Finance Japan) and Nikkei 225 close (Yahoo Finance), merges new trading days, and regenerates the two HTML files
- `.github/workflows/update.yml` — runs `update_data.py` daily (7:00 AM JST) and commits any new data

## Data sources

- JGB yields: [Ministry of Finance Japan — Interest Rate](https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/index.htm)
- Nikkei 225: Yahoo Finance (`^N225`)

## Running the updater manually

```bash
pip install -r requirements.txt  # only needs the standard library, no extra deps
python scripts/update_data.py
```
