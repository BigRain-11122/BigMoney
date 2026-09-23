"""HK / US market data source probe (user scope: 沪深/港股/美股 three markets).

Probes free sources for market #2/#3 feasibility BEFORE any big download:
  1. Tencent fqkline for HK stocks (hk00700 etc.) and US (usAAPL etc.)
  2. Index klines: hkHSI (恒生), usDJI / usIXIC (道指/纳指)
  3. akshare spot lists with market caps for universe sizing
Prints a feasibility report. READ-ONLY - downloads nothing heavy.
"""
import json
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"E:\Money")

import requests


UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Referer": "https://gu.qq.com/"}


def tx_kline(sym, n=10):
    url = ("https://proxy.finance.qq.com/ifzqgtimg/appstock/app"
           f"/fqkline/get?param={sym},day,,,{n},qfq")
    r = requests.get(url, headers=UA, timeout=10)
    j = r.json()
    data = j["data"][sym]
    bars = data.get("qfqday") or data.get("day")
    return bars


def probe(sym):
    try:
        bars = tx_kline(sym)
        if not bars:
            print(f"  {sym}: EMPTY")
            return
        first, last = bars[0][0], bars[-1][0]
        c0, c1 = bars[0][2], bars[-1][2]
        print(f"  {sym}: {len(bars)}bars {first}~{last} close {c0}->{c1}")
    except Exception as e:  # noqa: BLE001
        print(f"  {sym}: FAIL {type(e).__name__}: {str(e)[:60]}")


def deep(sym):
    """Check how deep the history goes (request big n)."""
    try:
        bars = tx_kline(sym, 800)
        print(f"  {sym} 深度: 一次800条 {bars[0][0] if bars else '-'} ~"
              f"{bars[-1][0] if bars else '-'}")
    except Exception as e:  # noqa: BLE001
        print(f"  {sym} 深度: FAIL {type(e).__name__}")


def main():
    print("== 港股 kline (TX fqkline) ==")
    for s in ("hk00700", "hk09988", "hk03690"):
        probe(s)
    deep("hk00700")
    print("== 美股 kline (TX) ==")
    for s in ("usAAPL", "usAAPL.OQ", "usBABA", "usBABA.N", "usMSFT"):
        probe(s)
    print("== 指数 (TX) ==")
    for s in ("hkHSI", "usDJI", "usIXIC", "usINX"):
        probe(s)
    print("== 港股宇宙 (akshare spot) ==")
    try:
        import akshare as ak
        hk = ak.stock_hk_spot_em()
        print(f"  港股spot: {len(hk)} 只 | 列: {list(hk.columns)[:8]}")
    except Exception as e:  # noqa: BLE001
        print(f"  港股spot FAIL: {type(e).__name__}: {str(e)[:60]}")
    print("== 美股宇宙 (akshare spot) ==")
    try:
        import akshare as ak
        us = ak.stock_us_spot_em()
        print(f"  美股spot: {len(us)} 只 | 列: {list(us.columns)[:8]}")
    except Exception as e:  # noqa: BLE001
        print(f"  美股spot FAIL: {type(e).__name__}: {str(e)[:60]}")
    print("PROBE-DONE", time.strftime("%H:%M:%S"))


if __name__ == "__main__":
    main()
