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
  - single assembly (T-04 F1): the status file is written ONCE, after
    the paper hook, by main() -- it always carries exit_code + hook_ok
    (+ hook_exit, cutoff_error). Staged .tmp + os.replace, atomic.
  - single-instance lock (T-04 F1): logs/update_daily.lock PID lockfile;
    a second live instance exits 0 without touching data. Stale PID is
    reclaimed (dead-PID check; age > LOCK_STALE_AGE fallback).

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
LOCK_PATH = os.path.join(PATHS.root, "logs", "update_daily.lock")
LOCK_STALE_AGE = 30 * 60        # belt-and-braces reclaim behind the PID check


def _pid_alive(pid: int) -> bool:
    """True if `pid` names a live process. Windows: kernel32 OpenProcess +
    WaitForSingleObject (WAIT_TIMEOUT == still running); a re-openable but
    terminated process reports WAIT_OBJECT_0 -> dead. POSIX: os.kill(pid, 0).
    ACCESS_DENIED on Windows means the process exists (elevated) -> alive."""
    if not pid or pid < 1:
        return False
    if os.name == "nt":
        try:
            import ctypes
            k32 = ctypes.WinDLL("kernel32", use_last_error=True)
            h = k32.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
            if not h:
                # 5 == ACCESS_DENIED: exists but elevated -> alive
                return ctypes.get_last_error() == 5
            try:
                rc = k32.WaitForSingleObject(h, 0)
                return rc == 258  # WAIT_TIMEOUT
            finally:
                k32.CloseHandle(h)
        except Exception:  # noqa: BLE001 -- never fatal
            return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False


def acquire_lock(path: str) -> bool:
    """PID lockfile with stale-PID reclaim (round.lock precedent). True if
    we hold the lock; False if another live instance holds it. A confirmed
    dead PID is reclaimed at any age; an unparseable lock is only reclaimed
    once older than LOCK_STALE_AGE (conservative stand-down while fresh)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                other = int(fh.read().strip() or 0)
        except (OSError, ValueError):
            other = 0
        age = dt.datetime.now().timestamp() - os.path.getmtime(path)
        if other and _pid_alive(other):
            return False
        if not other and age < LOCK_STALE_AGE:
            return False  # unparseable + fresh: be conservative, stand down
        # dead pid -> reclaim below
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(str(os.getpid()))
    return True


def release_lock(path: str) -> None:
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def _write_status_atomic(summary: dict, path: str | None = None) -> None:
    """Status log write: staged .tmp + os.replace (crash never leaves a
    half-written JSON behind). Optional `path` for selftest isolation."""
    path = path or STATUS_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def _pool_cutoff(files: list) -> tuple:
    """Post-update max last date across the pool. Returns (cutoff, error);
    error is recorded, NEVER silently swallowed (T-04 F8)."""
    try:
        lasts = []
        for p in files:
            old = load_existing(p)
            lasts.append(str(old["date"].iloc[-1]))
        return max(lasts), None
    except Exception as e:  # noqa: BLE001 -- field, not silence
        return None, f"{type(e).__name__}: {e}"


def _finalize_summary(summary: dict, exit_code: int,
                       hook_ok, hook_exit) -> dict:
    """Single status assembly (T-04 F1): everything the ops reader needs is
    merged here, once, right before the atomic write. hook_ok is None when
    the hook did not run (--no-paper or 0 new rows)."""
    summary["exit_code"] = exit_code
    summary["hook_ok"] = hook_ok
    summary["hook_exit"] = hook_exit
    return summary


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
    # data cutoff = max last date across the pool (post-update read);
    # read failure is recorded in the status, never swallowed (F8)
    summary["data_cutoff"], summary["cutoff_error"] = _pool_cutoff(files)
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

        # E: _pool_cutoff -- read failure recorded, never swallowed (F8)
        e = _pool_cutoff([os.path.join(td, "nope.csv")])
        e_ok = (e[0] is None and isinstance(e[1], str) and bool(e[1]))
        e = _pool_cutoff([p, p2])   # both end 2026-09-23 in sandbox
        e_ok &= (e[0] == "2026-09-23" and e[1] is None)
        ok &= e_ok
        print("  [updater] pool cutoff error field... "
              + ("PASS" if e_ok else "FAIL"))

        # F: single assembly + atomic status write (F1)
        sm = {"updated": "x", "total_new_rows": 3}
        _finalize_summary(sm, exit_code=3, hook_ok=False, hook_exit=1)
        st_path = os.path.join(td, "update_status.json")
        _write_status_atomic(sm, st_path)
        back = json.load(open(st_path, encoding="utf-8"))
        f_ok = (back["exit_code"] == 3 and back["hook_ok"] is False
                and back["hook_exit"] == 1
                and not os.path.exists(st_path + ".tmp"))
        _finalize_summary(sm, 0, None, None)
        f_ok &= sm["hook_ok"] is None and sm["exit_code"] == 0
        ok &= f_ok
        print("  [updater] single assembly + atomic status write... "
              + ("PASS" if f_ok else "FAIL"))

        # G: PID lockfile -- mutual exclusion + stale-PID reclaim (F1)
        lk = os.path.join(td, "update_daily.lock")
        g_ok = acquire_lock(lk) is True
        g_ok &= acquire_lock(lk) is False      # our own pid is alive -> busy
        release_lock(lk)
        g_ok &= not os.path.exists(lk)
        g_ok &= acquire_lock(lk) is True
        with open(lk, "w", encoding="utf-8") as fh:   # stale holder: bogus pid
            fh.write("4000000")
        g_ok &= acquire_lock(lk) is True      # dead pid -> reclaimed
        g_ok &= _pid_alive(os.getpid()) is True
        g_ok &= _pid_alive(0) is False and _pid_alive(-1) is False
        release_lock(lk)
        ok &= g_ok
        print("  [updater] PID lock + stale reclaim... "
              + ("PASS" if g_ok else "FAIL"))

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
    if not acquire_lock(LOCK_PATH):
        print("another live update_daily instance holds the lock -> stand down")
        return 0
    try:
        summary = run_update(now)
        print(f"new rows: {summary['total_new_rows']} | "
              f"failures: {len(summary['failures'])} | "
              f"overlap_mismatch: {summary['overlap_mismatches']} | "
              f"data cutoff: {summary['data_cutoff']}")
        if summary["overlap_mismatches"]:
            print(f"WARNING: source history changed for "
                  f"{summary['overlap_mismatches']} -- history NOT rewritten; "
                  f"live.paper anchor gate will abort if evidence drifted")
        exit_code = 0
        if summary["failures"]:
            exit_code = 2
        hook_ok, hook_exit = None, None
        if summary["total_new_rows"] > 0 and "--no-paper" not in argv:
            hook_exit = paper_hook()
            hook_ok = hook_exit == 0
            if hook_exit != 0:
                print("paper hook FAILED -- anchor drift or crash "
                      "(never silenced)")
                exit_code = 3
        # single assembly, single atomic write (T-04 F1): the on-disk
        # status ALWAYS carries the exit code + hook verdict
        _finalize_summary(summary, exit_code, hook_ok, hook_exit)
        _write_status_atomic(summary)
        print(f"status -> {STATUS_PATH}")
        return exit_code
    except Exception as e:  # noqa: BLE001 -- status log must never crash the run
        emergency = {"updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                     "now": str(now), "run_error": f"{type(e).__name__}: {e}",
                     "exit_code": 1, "hook_ok": None, "hook_exit": None}
        try:
            _write_status_atomic(emergency)
        except Exception:  # noqa: BLE001 -- best effort
            pass
        raise
    finally:
        release_lock(LOCK_PATH)


if __name__ == "__main__":
    sys.exit(main())
