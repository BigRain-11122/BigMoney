"""Incremental daily-bar updater for the core-48 pool + paper accrual hook.

Why (J17 pointer): data/daily freshness depended on an external manual
action. Paper tracking only accrues on new closed bars; without this
updater months_tracked never grows and the 2026-10-31 first-month
promotion check dies.

Contract:
  - scope: core-48 bare-code CSVs in data/daily (same universe as
    live.paper.load_core / backtests). sh/sz-prefixed expansion-pool
    files are NOT touched (BACKTEST_PLAN: no 1676 expansion).
  - source parity: ak.fund_etf_hist_sina -- the same source the pool
    was built with (download_etf.py); columns date,open,high,low,
    close,volume,amount only.
  - append-only: rows with date strictly greater than the file's last
    date are appended; existing rows are NEVER rewritten. If the source
    re-adjusts history (ETF dividend), the overlap check flags it in
    the status log AND live.paper's anchor gate aborts loudly --
    never auto-rewrite history here.
  - closed-bars-only (no look-ahead): a bar dated TODAY is accepted
    only after 15:30 Asia/Shanghai. Sina daily klines are completed
    bars intraday (verified 2026-09-23 11:07), this guard is
    defense-in-depth. Weekends/holidays -> 0 new rows = normal no-op.
  - probe fast-path: one liquid symbol (510300) is updated first; if it
    yields 0 new rows the whole market calendar is unchanged and the
    remaining fetches are skipped (10-min polling stays cheap).
  - atomic write: staged to <path>.tmp then os.replace.
  - idempotent: re-running the same day yields 0 new rows.
  - hook: if ANY new bar landed, run `python -m live.paper` once
    (anchor gate first; drift -> abort, trader JSONs untouched).
    --no-paper skips the hook.
  - status log: results/update_status.json (per-symbol rows appended,
    overlap mismatches, failures, totals) for ops/dashboard reads.

Exit codes: 0 ok | 1 selftest fail | 2 symbol fetch failure |
3 paper hook failed (anchor drift or crash -- NEVER silenced).

Usage:
    python scripts/update_daily.py             # update + paper hook
    python scripts/update_daily.py --no-paper  # update only
    python scripts/update_daily.py --selftest  # offline logic tests
"""
import datetime as dt
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS

COLUMNS = ["date", "open", "high", "low", "close", "volume", "amount"]
CLOSE_ACCEPT_TIME = dt.time(15, 30)      # today's bar only after market close
PROBE_SYMBOL = "510300"                  # liquid SSE ETF, calendar proxy
FETCH_SLEEP = 0.3                        # rate limit, mirrors download_etf.py
STATUS_PATH = os.path.join(PATHS.results_dir, "update_status.json")


def to_sina_symbol(code: str) -> str:
    """Bare 6-digit code -> sina sh/sz prefix (same split as the pool)."""
    if not (len(code) == 6 and code.isdigit()):
        raise ValueError(f"bad bare code: {code!r}")
    return ("sh" if code.startswith("5") else "sz") + code


def fetch_history(code: str):
    """Full sina history for one bare code, canonical columns only."""
    import akshare as ak
    df = ak.fund_etf_hist_sina(symbol=to_sina_symbol(code))
    if df is None or df.empty:
        return None
    df = df.rename(columns={"date": "date"})
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"sina source lost columns {missing}")
    df = df[COLUMNS].copy()
    df["date"] = df["date"].astype(str)
    return df


def closed_bar_ok(date_str: str, now: dt.datetime) -> bool:
    """Accept only completed bars: past dates always; today only after
    15:30 local (Asia/Shanghai machine clock); future dates never."""
    d = dt.date.fromisoformat(date_str)
    if d < now.date():
        return True
    if d == now.date():
        return now.time() >= CLOSE_ACCEPT_TIME
    return False


def load_existing(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"date": str})
    return df


def update_one(path: str, fetcher, now: dt.datetime) -> dict:
    """Append strictly-new closed bars to one CSV. Never rewrites rows."""
    status = {"symbol": os.path.basename(path)[:-4], "appended": 0,
              "overlap_mismatch": False, "error": None}
    try:
        old = load_existing(path)
        hist = fetcher(status["symbol"])
        if hist is None or hist.empty:
            status["error"] = "empty source"
            return status
        last_date = str(old["date"].iloc[-1])
        # overlap sanity: source's row at our last date must match ours
        # (source history re-adjustment -> flag loudly, never rewrite)
        ov = hist[hist["date"] == last_date]
        if len(ov) == 1:
            row = ov.iloc[0]
            mine = old.iloc[-1]
            for c in COLUMNS[1:]:
                a, b = float(row[c]), float(mine[c])
                if abs(a - b) > max(1e-9, abs(b) * 1e-6):
                    status["overlap_mismatch"] = True
                    status["mismatch_col"] = c
                    break
        new = hist[hist["date"] > last_date].copy()
        new = new[[closed_bar_ok(d, now) for d in new["date"]]]
        if len(new) == 0:
            return status
        merged = pd.concat([old[COLUMNS], new[COLUMNS]], ignore_index=True)
        tmp = path + ".tmp"
        merged.to_csv(tmp, index=False)
        os.replace(tmp, path)
        status["appended"] = int(len(new))
        status["first_new"] = str(new["date"].iloc[0])
        status["last_new"] = str(new["date"].iloc[-1])
    except Exception as e:  # noqa: BLE001 -- per-symbol isolation
        status["error"] = f"{type(e).__name__}: {e}"
    return status


def core_files() -> list:
    """Core-48 bare-code CSVs (mirror of live.paper.load_core listing)."""
    daily = PATHS.daily_dir
    return sorted(os.path.join(daily, f) for f in os.listdir(daily)
                  if f.endswith(".csv") and f[:-4].isdigit())


def run_update(now: dt.datetime | None = None, fetcher=None) -> dict:
    """Probe fast-path + full sweep. Returns the status dict."""
    now = now or dt.datetime.now()
    fetcher = fetcher or fetch_history
    files = core_files()
    probe_path = os.path.join(PATHS.daily_dir, f"{PROBE_SYMBOL}.csv")
    results = []

    probe = update_one(probe_path, fetcher, now)
    results.append(probe)
    if probe.get("error") or probe["appended"] > 0 or probe.get("overlap_mismatch"):
        # probe error -> calendar unknown, sweep anyway; new/mismatch -> sweep
        for path in files:
            if path == probe_path:
                continue
            results.append(update_one(path, fetcher, now))
            time.sleep(FETCH_SLEEP)
    else:
        results.extend([{"symbol": os.path.basename(p)[:-4], "appended": 0,
                         "overlap_mismatch": False, "error": None,
                         "skipped": "probe_no_new"}
                        for p in files if p != probe_path])

    summary = {
        "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "now": str(now), "close_accept_time": str(CLOSE_ACCEPT_TIME),
        "symbols": len(results),
        "total_new_rows": int(sum(r["appended"] for r in results)),
        "failures": [r["symbol"] for r in results if r.get("error")],
        "overlap_mismatches": [r["symbol"] for r in results
                               if r.get("overlap_mismatch")],
        "data_cutoff": None, "per_symbol": results,
    }
    # data cutoff = max last date across the pool (post-update read)
    try:
        lasts = []
        for p in files:
            old = load_existing(p)
            lasts.append(str(old["date"].iloc[-1]))
        summary["data_cutoff"] = max(lasts)
    except Exception:  # noqa: BLE001 -- status log must never crash the run
        pass
    with open(STATUS_PATH, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    return summary


def paper_hook() -> int:
    """Post-download hook: accrue paper evidence (anchor gate inside)."""
    root = PATHS.root
    print(f"[hook] new bars landed -> python -m live.paper")
    r = subprocess.run([sys.executable, "-m", "live.paper"], cwd=root)
    return r.returncode


# ---------------------------------------------------------------- selftest

def _fake_fetcher(rows: dict):
    """rows: {code: DataFrame} -- deterministic offline source."""
    def f(code):
        return rows.get(code)
    return f


def selftest() -> bool:
    import tempfile
    ok = True

    # A: closed-bar guard -- past always; today only >=15:30; future never
    now = dt.datetime(2026, 9, 23, 11, 0)
    ok &= closed_bar_ok("2026-09-22", now) is True
    ok &= closed_bar_ok("2026-09-23", now) is False      # intraday today
    ok &= closed_bar_ok("2026-09-23", dt.datetime(2026, 9, 23, 15, 31)) is True
    ok &= closed_bar_ok("2026-09-24", now) is False       # future
    print("  [updater] closed-bar guard unit tests... " + ("PASS" if ok else "FAIL"))

    # B: append-only + idempotency on a sandbox copy (offline fake source)
    with tempfile.TemporaryDirectory() as td:
        cols = ["date", "open", "high", "low", "close", "volume", "amount"]
        old_rows = [(f"2026-09-{d}", 4.0 + d, 4.1 + d, 3.9 + d, 4.0 + d,
                     1000 + d, 4000 + d) for d in (18, 21, 22)]
        src_rows = old_rows + [("2026-09-23", 4.3, 4.4, 4.2, 4.35, 2000, 8700)]
        old = pd.DataFrame(old_rows, columns=cols)
        src = pd.DataFrame(src_rows, columns=cols)
        p = os.path.join(td, "510300.csv")
        old.to_csv(p, index=False)

        s1 = update_one(p, _fake_fetcher({"510300": src}),
                        dt.datetime(2026, 9, 23, 16, 0))
        got = pd.read_csv(p)
        b = (s1["appended"] == 1 and len(got) == 4
             and got["date"].iloc[-1] == "2026-09-23"
             and abs(float(got["close"].iloc[-1]) - 4.35) < 1e-9)
        # history untouched
        b &= [round(float(x), 6) for x in got["close"].iloc[:-1]] == \
             [round(float(x), 6) for x in old["close"]]
        s2 = update_one(p, _fake_fetcher({"510300": src}),
                        dt.datetime(2026, 9, 23, 16, 0))
        b &= s2["appended"] == 0  # idempotent
        # intraday guard: next-day bar is NOT accepted before 15:30
        src2 = pd.concat([src, pd.DataFrame(
            [("2026-09-24", 4.5, 4.6, 4.4, 4.55, 2100, 9500)], columns=cols)],
            ignore_index=True)
        s3 = update_one(p, _fake_fetcher({"510300": src2}),
                        dt.datetime(2026, 9, 24, 10, 0))
        b &= s3["appended"] == 0 and len(pd.read_csv(p)) == 4
        ok &= b
        print("  [updater] append-only + idempotent + intraday guard... "
              + ("PASS" if b else "FAIL"))

        # C: overlap mismatch flagged, history never rewritten
        bad = src.copy()
        bad.loc[bad["date"] == "2026-09-22", "close"] = 9.99
        p2 = os.path.join(td, "510301.csv")
        old.to_csv(p2, index=False)
        s4 = update_one(p2, _fake_fetcher({"510301": bad}),
                        dt.datetime(2026, 9, 23, 16, 0))
        got2 = pd.read_csv(p2)
        # sandbox tail (2026-09-22) close = 4.0+22 = 26.0, must survive
        c = (s4["overlap_mismatch"] is True and s4["appended"] == 1
             and abs(float(got2["close"].iloc[-2]) - 26.0) < 1e-9)
        ok &= c
        print("  [updater] overlap-mismatch flag, no history rewrite... "
              + ("PASS" if c else "FAIL"))

    # D: source parity on real data (network; SKIP if unreachable)
    try:
        hist = fetch_history(PROBE_SYMBOL)
        mine = load_existing(os.path.join(PATHS.daily_dir,
                                          f"{PROBE_SYMBOL}.csv"))
        last = str(mine["date"].iloc[-1])
        ov = hist[hist["date"] == last]
        same = (len(ov) == 1 and all(
            abs(float(ov.iloc[0][c]) - float(mine.iloc[-1][c])) <=
            max(1e-9, abs(float(mine.iloc[-1][c])) * 1e-6)
            for c in COLUMNS[1:]))
        ok &= same
        print(f"  [updater] source parity {PROBE_SYMBOL} @ {last}... "
              + ("PASS" if same else "FAIL (source history changed!)"))
    except Exception as e:  # noqa: BLE001 -- offline selftest stays runnable
        print(f"  [updater] source parity... SKIP (network: {type(e).__name__})")
    return bool(ok)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        print(f"=== update_daily selftest {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        return 0 if selftest() else 1

    now = dt.datetime.now()
    print(f"=== Bigmoney daily update {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"core pool: {len(core_files())} CSVs | "
          f"today-bar guard: >= {CLOSE_ACCEPT_TIME}")
    summary = run_update(now)
    print(f"new rows: {summary['total_new_rows']} | "
          f"failures: {len(summary['failures'])} | "
          f"overlap_mismatch: {summary['overlap_mismatches']} | "
          f"data cutoff: {summary['data_cutoff']}")
    if summary['overlap_mismatches']:
        print(f"WARNING: source history changed for "
              f"{summary['overlap_mismatches']} -- history NOT rewritten; "
              f"live.paper anchor gate will abort if evidence drifted")
    exit_code = 0
    if summary["failures"]:
        exit_code = 2
    if summary["total_new_rows"] > 0 and "--no-paper" not in argv:
        if paper_hook() != 0:
            print("paper hook FAILED -- anchor drift or crash (never silenced)")
            exit_code = 3
    with open(STATUS_PATH, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    print(f"status -> {STATUS_PATH}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
