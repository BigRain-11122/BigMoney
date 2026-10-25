"""Pull CSI300 + CSI500 constituents' daily bars via akshare into data/astock_daily/per.

Resumable: existing files with a recent tail date are skipped. Columns are normalised
to date,open,high,low,close,volume,amount (qfq adjusted) so the quant scripts can read
them without knowing akshare's Chinese headers.

Usage: python scripts/pull_astock_panel.py [--indexes 000300,000905] [--workers 8]
"""
import argparse
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import akshare as ak
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "astock_daily", "per")
START = "20200101"
COLS = {"日期": "date", "开盘": "open", "收盘": "close", "最高": "high",
        "最低": "low", "成交量": "volume", "成交额": "amount"}


def sina_symbol(code):
    if code.startswith(("6", "9")):
        return "sh" + code
    if code.startswith(("4", "8")):
        return "bj" + code
    return "sz" + code


def constituents(indexes):
    syms = {}
    for idx in indexes:
        df = ak.index_stock_cons_csindex(symbol=idx)
        code_col = [c for c in df.columns if c.startswith("成分券代")][0]
        name_col = [c for c in df.columns if c.startswith("成分券名")][0]
        for c, n in zip(df[code_col].astype(str), df[name_col].astype(str)):
            syms[c] = n
    return syms


def fetch(sym, end, today):
    path = os.path.join(OUT, sym + ".csv")
    if os.path.exists(path):
        try:
            tail = pd.read_csv(path, usecols=["date"]).iloc[-1, 0]
            if str(tail) >= today:
                return sym, "skip"
        except Exception:
            pass
    for attempt in range(3):
        try:
            df = ak.stock_zh_a_daily(symbol=sina_symbol(sym), adjust="qfq")
            if df is None or df.empty:
                return sym, "empty"
            df = df.rename(columns=COLS)
            keep = [c for c in ["date", "open", "high", "low", "close", "volume", "amount"]
                    if c in df.columns]
            df = df[keep].sort_values("date")
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df = df[df["date"] >= "2020-01-01"]
            df.to_csv(path, index=False, encoding="utf-8")
            return sym, "ok rows=%d" % len(df)
        except Exception as e:
            if attempt == 2:
                return sym, "ERR %s %s" % (type(e).__name__, str(e)[:80])
            time.sleep(2.0 * (attempt + 1))
    return sym, "ERR"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--indexes", default="000300,000905")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--shard", default="0/1", help="i/n slice of the symbol list")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    end = time.strftime("%Y%m%d")
    syms = constituents(a.indexes.split(","))
    todo = sorted(syms)
    si, sn = [int(x) for x in a.shard.split("/")]
    todo = [s for i, s in enumerate(todo) if i % sn == si]
    if a.limit:
        todo = todo[:a.limit]
    print("universe", len(syms), "todo", len(todo), "workers", a.workers, flush=True)
    ok = skip = err = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(fetch, s, end, end): s for s in todo}
        for i, fu in enumerate(as_completed(futs), 1):
            sym, st = fu.result()
            if st.startswith("ok"):
                ok += 1
            elif st == "skip":
                skip += 1
            else:
                err += 1
                if err <= 10:
                    print("  FAIL", sym, st, flush=True)
            if i % 100 == 0:
                print("  %d/%d ok=%d skip=%d err=%d %.0fs"
                      % (i, len(todo), ok, skip, err, time.time() - t0), flush=True)
    print("done ok=%d skip=%d err=%d in %.0fs" % (ok, skip, err, time.time() - t0))


if __name__ == "__main__":
    main()