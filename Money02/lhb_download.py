"""LHB (龙虎榜 / Dragon-Tiger board) smart-money event data downloader.

User order 2026-09-21: beyond technical analysis - event/smart-money data.
Downloads the full publicly available history of exchange disclosure lists
(stocks that hit daily price/volume disclosure thresholds, with net buy
amounts) into data/lhb/lhb_detail.parquet. Chunked quarterly, idempotent
(skips existing chunks), gentle on the source (sequential + throttle).

This is raw DATA - panel integration (lhb_buy flag per stock-day) happens in
build_cache once this file exists.
"""
import os
import sys
import time
from pathlib import Path

import pandas as pd

import config as C

OUT = C.ROOT / "data" / "lhb"
CHUNKS = OUT / "chunks"
OUT.mkdir(parents=True, exist_ok=True)
CHUNKS.mkdir(parents=True, exist_ok=True)


def _fetch_chunk(q_start, q_end):
    import akshare as ak
    # correct name on this akshare build (stock_lhb_detail_daily does not
    # exist here): eastmoney LHB detail for [start,end]
    df = ak.stock_lhb_detail_em(start_date=q_start, end_date=q_end)
    return df


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t0 = time.time()
    frames = []
    n_new = 0
    # 2007Q1..2026Q3: LHB disclosures became systematic in 2007
    quarters = pd.period_range("2007Q1", "2026Q3", freq="Q")
    for q in quarters:
        p = CHUNKS / f"{q}.parquet"
        if p.exists():
            frames.append(pd.read_parquet(p))
            continue
        qs = q.start_time.strftime("%Y%m%d")
        qe = q.end_time.strftime("%Y%m%d")
        try:
            df = _fetch_chunk(qs, qe)
        except Exception as e:  # noqa: BLE001
            print(f"  {q}: FAIL {type(e).__name__}: {str(e)[:80]}", flush=True)
            time.sleep(2)
            continue
        if df is None or df.empty:
            print(f"  {q}: empty", flush=True)
            p.write_bytes(b"")  # negative cache marker
            continue
        df.to_parquet(p, index=False)
        frames.append(df)
        n_new += 1
        print(f"  {q}: {len(df)} rows", flush=True)
        time.sleep(1.0)
    full = pd.concat([f for f in frames if len(f)], ignore_index=True) \
        if any(len(f) for f in frames) else pd.DataFrame()
    if len(full):
        full.to_parquet(OUT / "lhb_detail.parquet", index=False)
        print(f"TOTAL {len(full)} rows | new chunks {n_new} | "
              f"{full['代码'].nunique() if '代码' in full.columns else '?'} stocks | "
              f"{time.time() - t0:.0f}s", flush=True)
        print("columns:", list(full.columns)[:12], flush=True)
    else:
        print("no data fetched", flush=True)


if __name__ == "__main__":
    main()
