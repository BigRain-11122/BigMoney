"""Crypto market runner (per-market tick, mirrors run_tick.py design).

User scope 2026-09-21: 全球主流市场海选. Crypto = market #2, fully state-
isolated from A-share via MONEY_CACHE_DIR / MONEY_RESULTS_DIR env switches:
its own league, live genome, paper account (100万), signals and archives.

Cadence (MoneyQuantCryptoTick, hourly, pythonw = silent):
  - new UTC day completed -> incremental bar refresh -> panel rebuild ->
    paper_step executes yesterday's signals at the new day's open ->
    state update
  - otherwise -> league round(s) on the frozen panel (pure evolution)
  - always -> write signals for the next session + log to ticks.jsonl

Panel hygiene: only COMPLETED UTC days enter the panel (crypto_cache drops
the running candle), so paper marks and blind tests use closed bars only.
"""
import json
import os
import sys
import time
import datetime as dt

MKT = r"E:\Money\data\mkt_crypto"
os.environ["MONEY_CACHE_DIR"] = os.path.join(MKT, "cache")
os.environ["MONEY_RESULTS_DIR"] = r"E:\Money\results_crypto"
sys.path.insert(0, r"E:\Money")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import config as C  # noqa: E402  (env must be set before import)
import data as D  # noqa: E402
import evolve as EV  # noqa: E402
import report as RP  # noqa: E402
import regime as RG  # noqa: E402

LOCK = C.LOGS_DIR / "crypto_tick.lock"
TICKS = C.RESULTS_DIR / "ticks.jsonl"
BARS = os.path.join(MKT, "bars")


def _log(row):
    with open(TICKS, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _try_lock():
    if LOCK.exists():
        try:
            age = time.time() - LOCK.stat().st_mtime
        except OSError:
            age = 999
        if age < 90 * 60:  # crypto round is fast; police at 90min
            return False
        LOCK.unlink(missing_ok=True)
    LOCK.write_text(str(os.getpid()))
    return True


def refresh_bars(days=12):
    """Incremental refresh: last N days per pair, merged into parquets."""
    import pandas as pd
    import requests
    ua = {"User-Agent": "Mozilla/5.0"}
    n_ok = n_err = 0
    for fn in os.listdir(BARS):
        if not fn.endswith(".parquet"):
            continue
        pair = fn[:-8]
        try:
            r = requests.get("https://api.gateio.ws/api/v4/spot/candlesticks",
                            params={"currency_pair": pair, "interval": "1d",
                                    "limit": days}, headers=ua, timeout=15)
            rows = r.json()
        except Exception:  # noqa: BLE001
            n_err += 1
            continue
        if not rows:
            n_err += 1
            continue
        recs = {}
        for row in rows:
            d = time.strftime("%Y-%m-%d", time.gmtime(int(row[0])))
            o, h, l, c = float(row[5]), float(row[3]), float(row[4]), float(row[2])
            v = float(row[1])
            recs[d] = {"date": d, "open": o, "high": h, "low": l, "close": c,
                       "volume": v, "amount": c * v}
        p = os.path.join(BARS, fn)
        old = pd.read_parquet(p)
        merged = pd.concat([old[~old["date"].isin(recs)],
                            pd.DataFrame(list(recs.values()))])
        merged = merged.sort_values("date").drop_duplicates("date")
        merged.to_parquet(p, index=False)
        n_ok += 1
        time.sleep(0.3)
    return n_ok, n_err


def main():
    if not _try_lock():
        print("crypto tick skipped: previous tick running")
        return
    try:
        cache = D.load_cache(mmap=True)
        panel_last = str(cache["dates"][-1])[:10]
        utc_today = dt.datetime.utcnow().strftime("%Y-%m-%d")
        fresh = panel_last < utc_today and \
            dt.datetime.utcnow().hour >= 1  # UTC day closed + a margin
        if fresh:
            n_ok, n_err = refresh_bars(12)
            print(f"refresh: ok={n_ok} err={n_err}")
            import crypto_cache
            crypto_cache.main()
            cache = D.load_cache(mmap=True)
            # paper: execute yesterday's signals at the new day's open
            from run_daily import paper_step
            if RP.signals_path().exists():
                sig = json.loads(RP.signals_path().read_text(encoding="utf-8"))
                paper = paper_step(cache, sig)
                print(f"paper[{str(cache['dates'][-1])[:10]}]: "
                      f"equity={paper['history'][-1]['equity']:,.0f} "
                      f"pos={len(paper['positions'])}")
        # league round(s) on the frozen panel
        res = EV.league_round()
        if not res.get("valid"):
            print("league budget skip")
            _log({"time": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
                  "mode": "league-skip"})
            return
        sig = RP.write_signals(res["cache"], res["live"], res["regime"],
                               res["out_dir"])
        lg = {n: s["pts"] for n, s in res["league"].items()}
        leader = max(lg.items(), key=lambda kv: kv[1])[0]
        _log({"time": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
              "mode": "league", "round": res["round"],
              "win_regime": res["regime_name"], "winner": res["winner"],
              "leader": EV.CLAN_CN[leader], "leader_pts": lg[leader],
              "seat_change": res["took_seat"],
              "n_buys": len(sig.get("buys", [])), "fresh_data": fresh})
        print(f"crypto round={res['round']} winner={EV.CLAN_CN[res['winner']]} "
              f"leader={EV.CLAN_CN[leader]}({lg[leader]}) "
              f"buys={len(sig.get('buys', []))} fresh={fresh}")
    finally:
        try:
            LOCK.unlink()
        except OSError:
            pass


ROOT_FILE = r"E:\Money\crypto_cache.py"

if __name__ == "__main__":
    main()
