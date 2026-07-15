#!/usr/bin/env python3
"""
Fetches the latest JGB yield curve data (Ministry of Finance Japan) and
Nikkei 225 daily close data (Yahoo Finance), merges any new trading days
into data/jgb_nikkei_data.json, and regenerates index.html (== full.html)
from templates/template_full.html.

Designed to run daily via .github/workflows/update.yml on GitHub Actions,
which has normal outbound internet access (no special workarounds needed).
"""
import csv
import io
import json
import sys
import time
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "jgb_nikkei_data.json"
TEMPLATE_FULL = ROOT / "templates" / "template_full.html"
OUT_FULL = ROOT / "full.html"
OUT_INDEX = ROOT / "index.html"

MOF_HISTORICAL_CSV = "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv"
UA = "Mozilla/5.0 (compatible; jgb-nikkei-yield-curve-updater/1.0)"

MATURITY_COLS = ["1Y","2Y","3Y","4Y","5Y","6Y","7Y","8Y","9Y","10Y","15Y","20Y","25Y","30Y","40Y"]
FLOOR_DATE = "1974-09-24"


def http_get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_jgb():
    """Returns {iso_date: [15 floats, None for any maturity not yet issued]}."""
    text = http_get(MOF_HISTORICAL_CSV)
    reader = csv.reader(io.StringIO(text))
    next(reader)  # title row
    next(reader)  # header row
    out = {}
    for row in reader:
        if not row or not row[0]:
            continue
        y, m, d = row[0].split("/")
        iso = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        if iso < FLOOR_DATE:
            continue
        vals = row[1:16]
        parsed = [float(v) if v.strip() not in ("", "-") else None for v in vals]
        out[iso] = parsed
    return out


def fetch_nikkei(period1_epoch, period2_epoch):
    """Returns {iso_date: close_float}."""
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/%5EN225"
        f"?period1={period1_epoch}&period2={period2_epoch}&interval=1d"
    )
    text = http_get(url, headers={"User-Agent": UA, "Accept": "application/json"})
    data = json.loads(text)
    result = data["chart"]["result"][0]
    ts = result["timestamp"]
    closes = result["indicators"]["quote"][0]["close"]
    gmtoffset = result.get("meta", {}).get("gmtoffset", 0) or 0
    out = {}
    for t, c in zip(ts, closes):
        if c is None:
            continue
        dt = datetime.fromtimestamp(t + gmtoffset, tz=timezone.utc)
        iso = dt.strftime("%Y-%m-%d")
        out[iso] = round(float(c), 2)
    return out


def load_existing():
    if not DATA_PATH.exists():
        return []
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def main():
    existing = load_existing()
    existing_by_date = {row[0]: row for row in existing}
    last_date = existing[-1][0] if existing else FLOOR_DATE
    print(f"Existing rows: {len(existing)}, last date: {last_date}")

    last_dt = date.fromisoformat(last_date)
    period1 = int(datetime(last_dt.year, last_dt.month, last_dt.day, tzinfo=timezone.utc).timestamp())
    period2 = int(time.time()) + 86400

    print("Fetching JGB historical CSV...")
    jgb = fetch_jgb()
    print(f"  {len(jgb)} JGB rows total (>= {FLOOR_DATE})")

    print("Fetching Nikkei 225 from Yahoo Finance...")
    nikkei = fetch_nikkei(period1, period2)
    print(f"  {len(nikkei)} Nikkei rows in requested window")

    common_new = sorted(d for d in (set(jgb) & set(nikkei)) if d > last_date)
    print(f"New common trading days after {last_date}: {len(common_new)}")

    if not common_new:
        print("No new data available (market holiday/weekend, or sources not yet updated). Nothing to do.")
        return 0

    for d in common_new:
        existing_by_date[d] = [d] + jgb[d] + [nikkei[d]]

    merged = [existing_by_date[d] for d in sorted(existing_by_date.keys())]
    DATA_PATH.write_text(json.dumps(merged, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(merged)} total rows to {DATA_PATH}")

    today_iso = date.today().isoformat()
    full_tpl = TEMPLATE_FULL.read_text(encoding="utf-8")
    full_out = full_tpl.replace("__DATA__", json.dumps(merged, separators=(",", ":"))).replace("__UPDATED__", today_iso)
    OUT_FULL.write_text(full_out, encoding="utf-8")
    OUT_INDEX.write_text(full_out, encoding="utf-8")

    print(f"Regenerated {OUT_FULL.name} and {OUT_INDEX.name}")
    print(f"Latest date now: {merged[-1][0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
