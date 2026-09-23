"""Global market data source probe (user scope corrected 2026-09-21:
全球主流市场都可以尝试 - stocks + crypto + FX + commodities, anything
legally tradable).

Read-only feasibility probe, one endpoint per asset class:
  crypto : Binance / OKX / CoinGecko public klines
  us eq  : Yahoo chart API (yfinance's backend) direct
  global : Stooq CSV (works for indices, FX, commodities, global stocks)
  hk/jp  : TX fqkline (hk verified earlier; jp probe here)
No heavy downloads - just depth/samples. Results decide the per-market
source matrix for the backfill.
"""
import json
import sys
import time

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
T = 12


def show(tag, ok, msg):
    print(f"  {tag:28s} {'OK ' if ok else 'FAIL'} {msg}"[:150])


def p_binance():
    try:
        r = requests.get("https://api.binance.com/api/v3/klines",
                         params={"symbol": "BTCUSDT", "interval": "1d",
                                 "limit": 5}, headers=UA, timeout=T)
        j = r.json()
        show("Binance BTCUSDT 1d", r.ok and len(j) == 5,
             f"{j[0][0]}~{j[-1][0] if isinstance(j[-1], list) else '?'} "
             f"close={j[-1][4] if isinstance(j[-1], list) else '?'}")
    except Exception as e:  # noqa: BLE001
        show("Binance", False, f"{type(e).__name__}: {str(e)[:60]}")


def p_okx():
    try:
        r = requests.get("https://www.okx.com/api/v5/market/candles",
                         params={"instId": "BTC-USDT", "bar": "1D",
                                 "limit": 5}, headers=UA, timeout=T)
        j = r.json()
        n = len(j.get("data", []))
        show("OKX BTC-USDT 1D", r.ok and n > 0, f"{n}根 最早{str(j['data'][-1][0])[:10]}")
    except Exception as e:  # noqa: BLE001
        show("OKX", False, f"{type(e).__name__}: {str(e)[:60]}")


def p_coingecko():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/coins/bitcoin/"
                         "market_chart",
                         params={"vs_currency": "usd", "days": "max",
                                 "interval": "daily"}, headers=UA, timeout=20)
        j = r.json()
        pr = j.get("prices", [])
        show("CoinGecko BTC max-daily", r.ok and len(pr) > 1000,
             f"{len(pr)}天 自{time.strftime('%Y-%m-%d', time.gmtime(pr[0][0]/1000))}")
    except Exception as e:  # noqa: BLE001
        show("CoinGecko", False, f"{type(e).__name__}: {str(e)[:60]}")


def p_yahoo(sym):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/"
                         f"chart/{sym}",
                         params={"range": "3mo", "interval": "1d"},
                         headers=UA, timeout=T)
        j = r.json()["chart"]["result"][0]
        ts = j["timestamp"]
        show(f"Yahoo {sym} 1d", r.ok and len(ts) > 40,
             f"{len(ts)}根 自{time.strftime('%Y-%m-%d', time.gmtime(ts[0]))}")
    except Exception as e:  # noqa: BLE001
        show(f"Yahoo {sym}", False, f"{type(e).__name__}: {str(e)[:60]}")


def p_stooq(sym):
    try:
        r = requests.get("https://stooq.com/q/d/l/", params={"s": sym, "i": "d"},
                         headers=UA, timeout=T)
        lines = r.text.strip().splitlines()
        first = lines[1].split(",")[0] if len(lines) > 1 else "-"
        show(f"Stooq {sym}", r.ok and len(lines) > 10,
             f"{len(lines)}行 自{first}")
    except Exception as e:  # noqa: BLE001
        show(f"Stooq {sym}", False, f"{type(e).__name__}: {str(e)[:60]}")


def p_tx(sym):
    try:
        r = requests.get("https://proxy.finance.qq.com/ifzqgtimg/appstock/"
                         f"app/fqkline/get?param={sym},day,,,5,qfq",
                         headers={**UA, "Referer": "https://gu.qq.com/"},
                         timeout=T)
        data = r.json()["data"][sym]
        bars = data.get("qfqday") or data.get("day")
        show(f"TX {sym}", bool(bars), f"{len(bars)}根 {bars[0][0]}~{bars[-1][0]}")
    except Exception as e:  # noqa: BLE001
        show(f"TX {sym}", False, f"{type(e).__name__}: {str(e)[:60]}")


def main():
    print("== 加密货币 ==")
    p_binance()
    p_okx()
    p_coingecko()
    print("== 美股/全球股 (Yahoo chart) ==")
    for s in ("AAPL", "7203.T", "ASML.AS", "005930.KS", "2330.TW"):
        p_yahoo(s)
    print("== 全球ETF/外汇/商品 (Stooq) ==")
    for s in ("spy.us", "qqq.us", "eurusd", "xauusd", "cl.f", "^nkx"):
        p_stooq(s)
    print("== 港/日股 (TX) ==")
    for s in ("hk00700",):
        p_tx(s)
    print("PROBE-DONE", time.strftime("%H:%M:%S"))


if __name__ == "__main__":
    main()
