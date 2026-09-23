"""Crypto daily backfill via Gate.io (CN-reachable, verified 2026-09-22 00:47).

User scope: 全球主流市场都可以尝试 - crypto as the first non-equity market
(7x24 data accrues fastest; simplest rule profile: no limits, T+0).

Universe: top-30 USDT spot pairs by 24h volume.
History: /api/v4/spot/candlesticks (interval=1d, limit=1000, paginated via
from/to). Output: data/mkt_crypto/bars/<PAIR>.parquet with
date/open/high/low/close/volume/amount columns.
Idempotent: per-pair parquet, re-run refreshes (recent window only later;
full refetch when file absent).
"""
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(r"E:\Money")
OUT = ROOT / "data" / "mkt_crypto" / "bars"
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
BASE = "https://api.gateio.ws/api/v4"


def _get(url, params=None, tries=3):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=15)
            if r.ok:
                return r.json()
        except Exception:  # noqa: BLE001
            pass
        time.sleep(2 + 2 * i)
    return None


def top_pairs(n=30):
    j = _get(f"{BASE}/spot/tickers")
    if not j:
        return []
    rows = []
    for t in j:
        p = t.get("currency_pair", "")
        if not p.endswith("_USDT"):
            continue
        try:
            rows.append((p, float(t.get("quote_volume", 0) or 0)))
        except Exception:  # noqa: BLE001
            pass
    rows.sort(key=lambda x: -x[1])
    return [p for p, _ in rows[:n]]


def fetch_pair_history(pair):
    """Paginate daily candles back to pair inception (or 2017)."""
    end = int(time.time())
    start = int(time.mktime(time.strptime("2017-01-01", "%Y-%m-%d")))
    all_rows = []
    to = end
    while True:
        j = _get(f"{BASE}/spot/candlesticks",
                 {"currency_pair": pair, "interval": "1d", "limit": 1000,
                  "to": to})
        if not j:
            break
        all_rows = j + all_rows
        oldest = int(j[0][0])
        if oldest <= start or len(j) < 1000:
            break
        to = oldest - 1
    if not all_rows:
        return None
    # Gate row: [ts, volume(base), close, high, low, open, window_closed?...]
    recs = []
    seen = set()
    for row in all_rows:
        ts = int(row[0])
        d = time.strftime("%Y-%m-%d", time.gmtime(ts))
        if d in seen:
            continue
        seen.add(d)
        try:
            o, h, l, c = float(row[5]), float(row[3]), float(row[4]), float(row[2])
            vol = float(row[1])
            if not (h >= l and h >= max(o, c) - 1e-9 and l <= min(o, c) + 1e-9):
                continue  # sanity: drop malformed
            amount = c * vol  # USDT notional
            recs.append({"date": d, "open": o, "high": h, "low": l,
                         "close": c, "volume": vol, "amount": amount})
        except Exception:  # noqa: BLE001
            continue
    return pd.DataFrame(recs).sort_values("date").reset_index(drop=True)


def main():
    t0 = time.time()
    pairs = top_pairs(30)
    print(f"universe: {len(pairs)} pairs: {pairs[:10]} ...", flush=True)
    n_ok = 0
    for i, p in enumerate(pairs, 1):
        df = fetch_pair_history(p)
        if df is None or df.empty:
            print(f"  [{i}/{len(pairs)}] {p}: EMPTY", flush=True)
            continue
        df.to_parquet(OUT / f"{p}.parquet", index=False)
        n_ok += 1
        print(f"  [{i}/{len(pairs)}] {p}: {len(df)}天 {df['date'].min()}~"
              f"{df['date'].max()} close={df['close'].iloc[-1]:.4f}",
              flush=True)
        time.sleep(0.6)
    print(f"DONE {n_ok}/{len(pairs)} pairs | {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
