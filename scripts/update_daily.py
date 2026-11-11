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
  - laggard catch-up (R54): per-symbol publication lag breaks the
    "one probe == whole calendar" assumption (2026-09-23: 12 SZ 159xxx
    ETFs published hours after the sh names, then stayed frozen behind
    the probe fast-path). When the probe yields 0 new rows, core files
    whose last bar date is BEHIND the probe's are fetched anyway (heal),
    with a per-symbol 60-min retry backoff (catchup_attempts in the
    status file) and a 15-day staleness exit (dead/suspended symbols
    stop being fetched, mirroring the pool F1 freshness rule).
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

  - dual-leg fallback (T-08, additive NEW fields only -- sina default path
    byte-identical): on primary fetch failure the run falls back to the
    TENCENT VALIDATION LEG (scripts/daily_validate.py) for diagnosis -- bars
    are NEVER written from tencent (no amount column, R34 probe evidence);
    it answers "is the bar upstream at all?" per failed symbol and "is the
    zero-row run a sina lag or a legit no-op?" via a 1-request probe-freshness
    check after 15:30. On sweep success a post-sweep parity audit re-checks
    the symbols that just received bars (level parity 1e-3, ex-div dates
    false-red -> flagged, never auto-corrected). Status gains: source_used,
    fallback_events, parity_audit (new keys only; readers of existing keys
    unaffected). --simulate-primary-failure forces the primary fetcher to
    fail for acceptance evidence (writes results/update_status_sim.json --
    production status file untouched, zero data writes).

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
import re
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS
from config.lane_io import write_lane

COLUMNS = ["date", "open", "high", "low", "close", "volume", "amount"]
CLOSE_ACCEPT_TIME = dt.time(15, 30)      # today's bar only after market close
PROBE_SYMBOL = "510300"                  # liquid SSE ETF, calendar proxy
FETCH_SLEEP = 0.3                        # rate limit, mirrors download_etf.py
CATCHUP_RETRY_MIN = 60          # laggard retry backoff window (minutes)
CATCHUP_STALE_DAYS = 15        # lag beyond this -> dead symbol, stop fetching
STATUS_PATH = os.path.join(PATHS.results_dir, "update_status.json")
# r1512: the status file is overwritten every run, so the evening after a top-up
# nothing on disk says WHICH bars came from the quote face. Append-only, one line
# per session that was topped up; readers (the CEO page) ask this instead of
# re-reading a status payload that has since rolled forward.
QUOTE_LEDGER = os.path.join(PATHS.results_dir, "quote_topup_ledger.jsonl")
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
    if path == STATUS_PATH:
        # Lane dual-track (D-20260928-03 batch-2): mirror this machine's
        # own snapshot to its lane file; fail-soft, never breaks the run.
        write_lane("update_status", summary)


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


def parity_verdict(hist, mine, tol_rel: float = 1e-6) -> dict:
    """Compare the local panel tail against one source history frame.

    The newest local bar can be absent from the source for two opposite
    reasons, and the old check could not tell them apart: the source
    rewrote history (loud) or the panel is legitimately AHEAD because the
    same-evening quote face (E138) wrote tonight's finished session before
    the history face publishes it (expected). Parity is therefore asserted
    on the newest date BOTH sides carry; the unverifiable tail is returned
    in ``ahead`` for disclosure instead of being failed.
    """
    out = {"status": "no_overlap", "compared_date": None,
           "ahead": [], "mismatch_col": None}
    if hist is None or mine is None or len(hist) == 0 or len(mine) == 0:
        return out
    h = hist.copy()
    m = mine.copy()
    h["date"] = h["date"].astype(str)
    m["date"] = m["date"].astype(str)
    src_last = str(h["date"].iloc[-1])
    out["ahead"] = [d for d in m["date"] if d > src_last]
    shared = h[h["date"].isin(set(m["date"]))]
    if len(shared) == 0:
        return out
    last = str(shared["date"].iloc[-1])
    out["compared_date"] = last
    src_row = shared[shared["date"] == last]
    loc_row = m[m["date"] == last]
    if len(src_row) != 1 or len(loc_row) != 1:
        out["status"] = "ambiguous"     # duplicate dates: refuse to guess
        return out
    for c in COLUMNS[1:]:
        a = float(src_row.iloc[0][c])
        b = float(loc_row.iloc[0][c])
        if abs(a - b) > max(1e-9, abs(b) * tol_rel):
            out["status"] = "mismatch"
            out["mismatch_col"] = c
            return out
    out["status"] = "match"
    return out


def _panel_decimals(path: str, default: int = 4) -> int:
    """Decimal places the panel already prints, read off its last data line."""
    try:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            lines = [ln for ln in fh.read().splitlines() if ln.strip()]
        last = lines[-1].split(",")
        if len(last) >= len(COLUMNS) and "." in last[-3]:
            return len(last[-3].split(".")[1])
    except Exception:  # noqa: BLE001 -- style probe only, never fatal
        pass
    return default


def _fmt_price(value, dp: int) -> str:
    """A price in the panel's own decimal style, never at the cost of precision.

    Inheriting the style is what keeps a one-row append to one changed line, but
    a panel printed at 1dp must not truncate a 4.35 source bar into 4.3 -- so
    the styled form is used only when it round-trips exactly.
    """
    v = float(value)
    s = ("%." + str(dp) + "f") % v
    if abs(float(s) - v) > 1e-9:
        s = ("%.6f" % v).rstrip("0")
        if s.endswith("."):
            s += "0"
    return s


def _format_row(row, dp: int) -> str:
    """One bar as the panel writes it: fixed-decimal prices, integer sizes."""
    parts = [str(row["date"])]
    for c in COLUMNS[1:5]:
        parts.append(_fmt_price(row[c], dp))
    for c in COLUMNS[5:]:
        parts.append(str(int(round(float(row[c])))))
    return ",".join(parts)


def update_one(path: str, fetcher, now: dt.datetime) -> dict:
    """Append strictly-new closed bars to one CSV. Never rewrites rows.

    The append is BYTE-level, not a pandas round-trip: reading the panel into
    a DataFrame and calling ``to_csv`` re-serialises every float, so three new
    bars rewrote all 1,650 lines of data/daily (2026-10-27 r1190) -- any freeze
    check, blob compare or watermark that looks at that panel then reports a
    whole-panel change for a one-row event. The new rows are therefore formatted
    in the file's own decimal style and appended to the existing text verbatim.
    """
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
        dp = _panel_decimals(path)
        with open(path, "r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        if text and not text.endswith("\n"):
            text += "\n"
        text += "".join(_format_row(r, dp) + "\n" for _i, r in new.iterrows())
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
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


def _last_date(path: str) -> str:
    return str(load_existing(path)["date"].iloc[-1])


def _laggards_of(files: list, probe_last: str) -> list:
    """[(path, last_date)] for core files whose last bar date is behind the
    probe's. Unreadable files are skipped here (they keep their old data;
    the full-sweep branch is where broken files surface as failures)."""
    out = []
    for p in files:
        if os.path.basename(p)[:-4] == PROBE_SYMBOL:
            continue
        try:
            last = _last_date(p)
        except Exception:  # noqa: BLE001 -- probe-0 branch stays cheap
            continue
        if last < probe_last:
            out.append((p, last))
    return out


# ---------------------------------- same-evening quote top-up (r1511 bm-c)
# The history face (klc_kl.js behind ak.fund_etf_hist_sina) publishes a session
# only the NEXT morning, so between 15:30 and then every face built on this
# panel -- ticket, book NAV, CEO page -- is priced on yesterday's close. The
# same vendor's BATCH quote endpoint (hq.sinajs.cn) already carries the finished
# session minutes after the close, and update_etf_wide has used it since
# 2026-10-26 for exactly this gap on the wide universe (verified identical to
# the history face's own later print). This lane therefore IMPORTS that lane's
# quote_tail() instead of writing a second verifier: one definition of "this
# quote really is this instrument's next bar", two panels that cannot disagree.
# Refusals are counted, never guessed: a quote whose session date is not the
# expected one, or whose 昨收 does not reproduce our own last close, is refused.
QUOTE_URL = "https://hq.sinajs.cn/list={syms}"
QUOTE_CHUNK = 60
QUOTE_HEADERS = {"Referer": "https://finance.sina.com.cn",
                 "User-Agent": "Mozilla/5.0"}
QUOTE_LINE = re.compile(r'hq_str_([a-z]{2}\d{6})="([^"]*)"')


def _quote_face():
    """The wide lane's quote verifier -- imported, never re-implemented."""
    try:
        import scripts.update_etf_wide as W
    except ImportError:  # run as `python scripts\update_daily.py`
        import update_etf_wide as W
    return W


def to_sina_symbol(stem: str) -> str:
    return ("sh" if stem[0] == "5" else "sz") + stem


def _quote_fields(sina_syms: list) -> dict:
    """One batched quote request -> {sina_sym: [fields...]}. Pure network I/O."""
    url = QUOTE_URL.format(syms=",".join(sina_syms))
    req = urllib.request.Request(url, headers=QUOTE_HEADERS)
    text = urllib.request.urlopen(req, timeout=20).read().decode("gbk", "replace")
    out = {}
    for sym, body in QUOTE_LINE.findall(text):
        if body:
            out[sym] = body.split(",")
    return out


def _append_bar(path: str, row: dict) -> None:
    """Byte-level tail append in the panel's own decimal style (atomic)."""
    dp = _panel_decimals(path)
    with open(path, "r", encoding="utf-8", newline="") as fh:
        text = fh.read()
    if text and not text.endswith("\n"):
        text += "\n"
    text += _format_row(row, dp) + "\n"
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


def quote_topup(files, now, quote_fields=None, calendar=None,
                appender=None, symbol_of=None) -> dict:
    """Write tonight's completed session into the panel from the quote face.

    Only the tail session, only after 15:30, only for files behind the official
    calendar's expected bar, and only when the quote verifier accepts it.
    Everything else is reported in `refused`. `quote_fields` / `calendar` /
    `appender` are injection points for the offline selftest.
    """
    W = _quote_face()
    out = {"status": "noop", "target": None, "lagging": [], "attempted": 0,
           "appended": 0, "refused": [], "quote_date": None, "rows": [],
           "detail": ""}
    try:
        dates = calendar if calendar is not None else W.official_calendar()
        target = W.U.expected_latest_bar_date(now, dates)
    except Exception as exc:  # noqa: BLE001 -- calendar is a diagnosis, not data
        out["status"] = "unknown_calendar"
        out["detail"] = "%s: %s" % (type(exc).__name__, exc)
        return out
    out["target"] = target
    if target is None:
        out["status"] = "unknown_calendar"
        out["detail"] = "no expected session could be derived"
        return out
    if now.time() < CLOSE_ACCEPT_TIME:
        out["status"] = "gated_before_close"
        out["detail"] = "before %s no completed session can exist" % CLOSE_ACCEPT_TIME
        return out
    lag = []
    for path in files:
        stem = os.path.basename(path)[:-4]
        try:
            last = _last_date(path)
        except Exception as exc:  # noqa: BLE001 -- reported, not fatal
            out["refused"].append({"symbol": stem,
                                   "reason": "unreadable:%s" % type(exc).__name__})
            continue
        if last < target:
            lag.append((path, last))
    out["lagging"] = [os.path.basename(p)[:-4] for p, _ in lag]
    if not lag:
        out["status"] = "noop_current"
        out["detail"] = "every core file already carries %s" % target
        return out

    fetch = quote_fields or _quote_fields
    appender = appender or _append_bar
    # r1556: a caller whose panel files already carry the exchange prefix
    # (`sh510300.csv`, the five-member ETF lane) cannot use the bare-code
    # default -- it would ask the vendor for `szsh510300` and read every
    # answer as `no_quote`. One verifier, the caller names its own stems.
    symbol_of = symbol_of or to_sina_symbol
    syms = [symbol_of(os.path.basename(p)[:-4]) for p, _ in lag]
    fields_by_sym = {}
    try:
        for i in range(0, len(syms), QUOTE_CHUNK):
            fields_by_sym.update(fetch(syms[i:i + QUOTE_CHUNK]))
    except Exception as exc:  # noqa: BLE001 -- network failure is honest output
        out["status"] = "fetch_failed"
        out["detail"] = "%s: %s" % (type(exc).__name__, exc)
        return out

    for path, last in lag:
        stem = os.path.basename(path)[:-4]
        f = fields_by_sym.get(symbol_of(stem))
        out["attempted"] += 1
        if not f:
            out["refused"].append({"symbol": stem, "reason": "no_quote"})
            continue
        try:
            local = [{"date": last,
                      "close": float(load_existing(path)["close"].iloc[-1])}]
        except Exception as exc:  # noqa: BLE001
            out["refused"].append({"symbol": stem,
                                   "reason": "unreadable:%s" % type(exc).__name__})
            continue
        verdict = W.quote_tail(local, f, target)
        if verdict.get("row") is None:
            out["refused"].append({"symbol": stem,
                                   "reason": verdict.get("mismatch")
                                   or "already_current"})
            continue
        try:
            appender(path, verdict["row"])
        except Exception as exc:  # noqa: BLE001
            out["refused"].append({"symbol": stem,
                                   "reason": "write_failed:%s" % type(exc).__name__})
            continue
        out["appended"] += 1
        out["quote_date"] = verdict["row"]["date"]
        out["rows"].append({"symbol": stem, "appended": 1,
                            "overlap_mismatch": False, "error": None,
                            "skipped": "quote_topup"})
    out["status"] = "appended" if out["appended"] else "refused_all"
    out["detail"] = ("%d/%d lagging core files topped up from the batch quote "
                     "face at %s" % (out["appended"], out["attempted"], target))
    return out


def record_quote_topup(topup: dict, path: str = QUOTE_LEDGER,
                       now: dt.datetime | None = None) -> dict | None:
    """Append one line for a session the quote face wrote. Nothing -> no line.

    A run that appended nothing is not an event: writing a line for it would
    turn "the top-up never ran" and "the top-up ran and had nothing to do" into
    the same row of the ledger, which is the disagreement this file exists to
    prevent (a session either came from the quote face or it did not).
    """
    if not topup or int(topup.get("appended") or 0) <= 0:
        return None
    row = {"ts": (now or dt.datetime.now()).isoformat(timespec="seconds"),
           "session": topup.get("quote_date") or topup.get("target"),
           "appended": int(topup.get("appended") or 0),
           "refused": len(topup.get("refused") or []),
           "symbols": sorted(str(r.get("symbol")) for r in (topup.get("rows") or []))}
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read_quote_ledger(path: str = QUOTE_LEDGER) -> list:
    """Ledger rows, oldest first. Missing/unreadable file -> [] (no invention)."""
    if not os.path.exists(path):
        return []
    out = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        return []
    return out


def _backoff_active(ts, now: dt.datetime) -> bool:
    """True while the laggard's last catch-up attempt is younger than
    CATCHUP_RETRY_MIN minutes. Missing/unparseable -> expired (attempt)."""
    if not ts:
        return False
    try:
        t = dt.datetime.fromisoformat(str(ts))
    except ValueError:
        return False
    return (now - t) < dt.timedelta(minutes=CATCHUP_RETRY_MIN)


def run_update(now: dt.datetime | None = None, fetcher=None,
               status_path: str | None = None) -> dict:
    """Probe fast-path + full sweep + laggard catch-up (R54). Returns the
    status dict."""
    now = now or dt.datetime.now()
    fetcher = fetcher or fetch_history
    status_path = status_path or STATUS_PATH
    files = core_files()
    probe_path = os.path.join(PATHS.daily_dir, f"{PROBE_SYMBOL}.csv")
    results = []
    catchup = {"laggards": [], "fetched": [], "backoff": [], "stale_dead": []}

    # prior per-symbol catch-up attempt timestamps -> retry backoff
    try:
        with open(status_path, encoding="utf-8") as fh:
            attempts = dict(json.load(fh).get("catchup_attempts") or {})
    except (OSError, ValueError):
        attempts = {}

    probe = update_one(probe_path, fetcher, now)
    results.append(probe)
    if probe.get("error") or probe["appended"] > 0 or probe.get("overlap_mismatch"):
        # probe error -> calendar unknown, sweep anyway; new/mismatch -> sweep
        for path in files:
            if path == probe_path:
                continue
            results.append(update_one(path, fetcher, now))
            time.sleep(FETCH_SLEEP)
        # post-sweep laggards (source not ready for them yet) count as
        # attempted now, so the 60-min backoff applies to them as well
        probe_last = _last_date(probe_path)
        post = _laggards_of(files, probe_last)
        catchup["laggards"] = [os.path.basename(p)[:-4] for p, _ in post]
        for p, _lag in post:
            attempts[os.path.basename(p)[:-4]] = \
                now.isoformat(timespec="seconds")
    else:
        probe_last = _last_date(probe_path)
        laggards = _laggards_of(files, probe_last)
        catchup["laggards"] = [os.path.basename(p)[:-4] for p, _ in laggards]
        lag_last = dict(laggards)
        for path in files:
            if path == probe_path:
                continue
            sym = os.path.basename(path)[:-4]
            if path not in lag_last:
                results.append({"symbol": sym, "appended": 0,
                                "overlap_mismatch": False, "error": None,
                                "skipped": "probe_no_new"})
                continue
            lag_days = (dt.date.fromisoformat(probe_last)
                        - dt.date.fromisoformat(lag_last[path])).days
            if lag_days > CATCHUP_STALE_DAYS:
                catchup["stale_dead"].append(sym)
                results.append({"symbol": sym, "appended": 0,
                                "overlap_mismatch": False, "error": None,
                                "skipped": "catchup_stale_dead"})
            elif _backoff_active(attempts.get(sym), now):
                catchup["backoff"].append(sym)
                results.append({"symbol": sym, "appended": 0,
                                "overlap_mismatch": False, "error": None,
                                "skipped": "catchup_backoff"})
            else:
                r = update_one(path, fetcher, now)
                r["catchup_fetch"] = True
                results.append(r)
                catchup["fetched"].append(sym)
                attempts[sym] = now.isoformat(timespec="seconds")
                time.sleep(FETCH_SLEEP)
    # prune the backoff bookkeeping to symbols lagging right now
    attempts = {s: t for s, t in attempts.items()
                if s in catchup["laggards"]}

    # same-evening quote top-up: the history face prints tonight's session only
    # tomorrow morning, the batch quote face has it minutes after the close.
    # Rows written here are ordinary append-only bars, so they count as new
    # rows for the status face and for the paper hook below.
    topup = quote_topup(files, now)
    record_quote_topup(topup, now=now)
    results.extend(topup.pop("rows", []))

    summary = {
        "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "now": str(now), "close_accept_time": str(CLOSE_ACCEPT_TIME),
        "symbols": len(results),
        "total_new_rows": int(sum(r["appended"] for r in results)),
        "failures": [r["symbol"] for r in results if r.get("error")],
        "overlap_mismatches": [r["symbol"] for r in results
                               if r.get("overlap_mismatch")],
        "data_cutoff": None, "per_symbol": results,
        "catchup": catchup,
        "catchup_attempts": attempts,
        "quote_topup": topup,
    }
    # data cutoff = max last date across the pool (post-update read);
    # read failure is recorded in the status, never swallowed (F8)
    summary["data_cutoff"], summary["cutoff_error"] = _pool_cutoff(files)
    return summary


def paper_hook() -> int:
    """Post-download hook: accrue paper evidence (anchor gate inside).

    T-21 request channel on the auto path (R94 bm-a integrity fix): the
    hook carries the same BIGMONEY_REGIME_GUARD='enforce' request the OS
    loop's manual paper step makes (R99 bm-b wiring, "三机同请求") -- without
    it, a 2026-10-01 new-bar auto-run would silently miss the env leg of
    the three-gate activation (approval file + date gate + env request).
    setdefault: an explicit caller-set value always wins; pre-10-01 the
    date gate downgrades honestly either way (zero behavior change).
    """
    root = PATHS.root
    print(f"[hook] new bars landed -> python -m live.paper")
    env = dict(os.environ)
    env.setdefault("BIGMONEY_REGIME_GUARD", "enforce")
    r = subprocess.run([sys.executable, "-m", "live.paper"], cwd=root, env=env)
    return r.returncode


# -------------------------------------------------- dual-leg fallback (T-08)
SIM_STATUS_PATH = os.path.join(PATHS.results_dir, "update_status_sim.json")


class _PrimaryDown(Exception):
    """Simulated primary-source outage (--simulate-primary-failure)."""


def _sim_primary_down():
    def f(code):
        raise _PrimaryDown(f"simulated primary outage for {code}")
    return f


def _validation_fallback(summary: dict, fetcher=None) -> dict:
    """T-08 fallback wiring (additive NEW fields only). Never breaks the
    update run -- validation-leg errors are recorded honestly inside
    fallback_events. `fetcher` injects the validation source for offline
    selftest; None = real tencent leg."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    summary["source_used"] = "sina"
    summary.setdefault("fallback_events", [])
    try:
        # import inside the guard: a missing validation-leg module must
        # degrade to a validation_leg_error event per the docstring
        # contract ("never breaks the update run"), never crash the run
        from daily_validate import (audit_new_rows, fallback_diagnose,
                                     freshness, local_last_date,
                                     tencent_daily)
        if summary.get("failures"):
            summary["fallback_events"].extend(
                fallback_diagnose(summary["failures"], fetcher=fetcher))
            summary["source_used"] = \
                "sina(failed)->tencent(validation-only)"
        elif summary.get("total_new_rows", 0) > 0:
            new_syms = [r["symbol"] for r in summary.get("per_symbol", [])
                        if r.get("appended", 0) > 0]
            summary["parity_audit"] = audit_new_rows(new_syms,
                                                      fetcher=fetcher)
        else:
            # zero-row ambiguity (stale cutoff after close): does the bar
            # exist upstream at all? one request, probe symbol only.
            now = dt.datetime.now()
            if now.weekday() < 5 and now.time() >= CLOSE_ACCEPT_TIME:
                pairs, _ = (fetcher or tencent_daily)(PROBE_SYMBOL)
                f = freshness(pairs, local_last_date(PROBE_SYMBOL))
                summary["fallback_events"].append({
                    "symbol": PROBE_SYMBOL, "diagnosis": f["class"],
                    "tencent_latest": f["tencent_latest"],
                    "note": "zero-row ambiguity: upstream bar-existence probe"})
    except BaseException as exc:  # noqa: BLE001 -- never break the update
        summary["fallback_events"].append({
            "diagnosis": "validation_leg_error",
            "error": f"{type(exc).__name__}: {exc}"[:200]})
    return summary



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

        # C2: byte-level append -- existing rows keep their exact text, and the
        # new row inherits the panel's own decimal style. A pandas round-trip
        # passes block B and still rewrites all 1,650 lines (r1190 live case:
        # 3 new bars -> 1,650 changed lines, so every freeze/blob check on the
        # panel reads a whole-panel event).
        p3 = os.path.join(td, "510302.csv")
        styled = ("date,open,high,low,close,volume,amount\n"
                  "2026-09-18,4.1200,4.1740,4.1180,4.1490,1000,4000\n"
                  "2026-09-21,4.1560,4.1620,4.1330,4.1390,1001,4001\n")
        with open(p3, "w", encoding="utf-8", newline="") as fh:
            fh.write(styled)
        s5 = update_one(p3, _fake_fetcher({"510302": src}),
                        dt.datetime(2026, 9, 23, 16, 0))
        with open(p3, "r", encoding="utf-8", newline="") as fh:
            after = fh.read()
        c2 = (s5["appended"] == 2 and after.startswith(styled)
              and after.splitlines()[-2] == "2026-09-22,26.0000,26.1000,25.9000,26.0000,1022,4022"
              and after.splitlines()[-1] == "2026-09-23,4.3000,4.4000,4.2000,4.3500,2000,8700")
        ok &= c2
        print("  [updater] append keeps every existing byte + panel decimal style... "
              + ("PASS" if c2 else "FAIL"))

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

    # H: laggard catch-up in the probe fast-path (R54) -- offline injected
    # source; mirrors the 2026-09-23 incident (12 SZ 159xxx lagging 510300)
    with tempfile.TemporaryDirectory() as td:
        cols = ["date", "open", "high", "low", "close", "volume", "amount"]

        def _rows(d0, d1, base):
            dates = [d for d in ("2026-09-21", "2026-09-22", "2026-09-23")
                     if d0 <= d <= d1]
            return [(d, base, base + 0.1, base - 0.1, base, 1000, 4000)
                    for d in dates]

        def _csv(name, rows):
            p = os.path.join(td, name)
            pd.DataFrame(rows, columns=cols).to_csv(p, index=False)
            return p

        _csv("510300.csv", _rows("2026-09-21", "2026-09-23", 4.0))  # probe
        _csv("510301.csv", _rows("2026-09-21", "2026-09-23", 5.0))  # coherent
        _csv("159934.csv", _rows("2026-09-21", "2026-09-22", 6.0))  # laggard
        _csv("159901.csv", [("2026-08-01", 1.0, 1.1, 0.9, 1.0, 100, 400)])
        st = os.path.join(td, "update_status.json")
        calls = []

        def _mk_src(lag_has_23):
            def f(code):
                calls.append(code)
                table = {
                    "510300": _rows("2026-09-21", "2026-09-23", 4.0),
                    "510301": _rows("2026-09-21", "2026-09-23", 5.0),
                    "159934": _rows("2026-09-21",
                                    "2026-09-23" if lag_has_23
                                    else "2026-09-22", 6.0),
                }
                if code not in table:
                    return None
                return pd.DataFrame(table[code], columns=cols)
            return f

        real_daily = PATHS.daily_dir
        PATHS.daily_dir = td
        try:
            t0 = dt.datetime(2026, 9, 24, 8, 0)
            s1 = run_update(now=t0, fetcher=_mk_src(False), status_path=st)
            h = (s1["total_new_rows"] == 0
                 and sorted(s1["catchup"]["laggards"]) == ["159901", "159934"]
                 and s1["catchup"]["fetched"] == ["159934"]
                 and s1["catchup"]["stale_dead"] == ["159901"]
                 and s1["catchup"]["backoff"] == []
                 and "159901" not in calls)     # dead symbol -> never fetched
            json.dump({"catchup_attempts": s1["catchup_attempts"]},
                      open(st, "w", encoding="utf-8"))
            n_before = len(calls)
            s2 = run_update(now=t0 + dt.timedelta(minutes=30),
                            fetcher=_mk_src(False), status_path=st)
            h &= (s2["catchup"]["fetched"] == []
                  and s2["catchup"]["backoff"] == ["159934"]
                  and calls[n_before:] == [PROBE_SYMBOL])  # probe only
            json.dump({"catchup_attempts": s2["catchup_attempts"]},
                      open(st, "w", encoding="utf-8"))
            s3 = run_update(now=t0 + dt.timedelta(minutes=61),
                            fetcher=_mk_src(True), status_path=st)
            h &= (s3["total_new_rows"] == 1
                  and s3["catchup"]["fetched"] == ["159934"]
                  and _last_date(os.path.join(td, "159934.csv"))
                  == "2026-09-23")
        finally:
            PATHS.daily_dir = real_daily
        ok &= h
        print("  [updater] laggard catch-up + backoff + stale-dead... "
              + ("PASS" if h else "FAIL"))

        # I: dual-leg fallback wiring (T-08) -- offline injected validation
        # source; three branches: failure diagnosis / parity audit /
        # validation-leg error resilience
        with tempfile.TemporaryDirectory() as td:
            PATHS.daily_dir = td
            try:
                cols2 = ["date", "open", "high", "low", "close", "volume",
                         "amount"]
                # sandbox local tail ends 09-22: a primary-failure run means
                # local is BEHIND upstream (tencent has 09-23 in fixture)
                pd.DataFrame([(f"2026-09-{d}", 4.0, 4.1, 3.9, 4.5, 100, 400)
                              for d in ("21", "22")],
                             columns=cols2).to_csv(
                    os.path.join(td, "510300.csv"), index=False)

                def _diag_fetch(code):
                    # validation leg: upstream has the newer bar
                    return ([("2026-09-22", 4.5), ("2026-09-23", 4.6)], False)

                s_fail = {"failures": ["510300"], "total_new_rows": 0,
                          "per_symbol": []}
                _validation_fallback(s_fail, fetcher=_diag_fetch)
                i1 = (s_fail["source_used"]
                       == "sina(failed)->tencent(validation-only)"
                       and s_fail["fallback_events"][0]["diagnosis"]
                       == "upstream_has_newer_bar")

                s_ok = {"failures": [], "total_new_rows": 1, "per_symbol": [
                    {"symbol": "510300", "appended": 1}]}
                _validation_fallback(s_ok, fetcher=_diag_fetch)
                i2 = (s_ok["source_used"] == "sina"
                      and s_ok.get("parity_audit", {}).get("symbols")
                      == ["510300"])

                def _boom(code):
                    raise ConnectionError("validation leg down")

                s_err = {"failures": ["510300"], "total_new_rows": 0,
                         "per_symbol": []}
                _validation_fallback(s_err, fetcher=_boom)
                i3 = (s_err["fallback_events"][0]["diagnosis"]
                      == "validation_leg_unreachable")
            finally:
                PATHS.daily_dir = real_daily
            try:
                from daily_validate import fallback_diagnose  # noqa: F401
                leg_present = True
            except ImportError:
                leg_present = False
            if leg_present:
                i = i1 and i2 and i3
                print("  [updater] dual-leg fallback wiring (T-08)... "
                      + ("PASS" if i else "FAIL"))
            else:
                # module absent on this clone: assert the documented
                # degradation contract instead -- each branch records
                # exactly one validation_leg_error event, run never crashes
                evs = [s.get("fallback_events", [])
                       for s in (s_fail, s_ok, s_err)]
                i = (all(len(e) == 1 and e[0].get("diagnosis")
                         == "validation_leg_error" for e in evs)
                     and s_fail["source_used"] == "sina")
                print("  [updater] dual-leg fallback wiring (T-08)... "
                      + ("PASS" if i else "FAIL")
                      + " [degraded: scripts/daily_validate.py absent on "
                        "this clone -- T-08 owner bm-a untracked-file "
                        "omission, bm-c r58 guard; online-leg cases "
                        "auto-activate when the module lands]")
            ok &= i

    # C2: parity verdict branches (offline) -- a quote-topped tail is not a
    # source rewrite, and a shared-bar disagreement is still loud
    _base = pd.DataFrame([["2026-10-23", 1.0, 1.1, 0.9, 1.05, 100, 1000],
                          ["2026-10-26", 4.155, 4.187, 4.130, 4.179,
                           200, 8000]], columns=COLUMNS)
    _ahead = pd.concat([_base, _base.tail(1).assign(date="2026-10-27")],
                       ignore_index=True)
    _v1 = parity_verdict(_base, _ahead)
    _v2 = parity_verdict(_base, _base.assign(close=[1.05, 4.180]))
    _v3 = parity_verdict(_base, _base.tail(1).assign(date="2026-10-27"))
    i = (_v1["status"] == "match" and _v1["compared_date"] == "2026-10-26"
         and _v1["ahead"] == ["2026-10-27"] and not _v1["mismatch_col"]
         and _v2["status"] == "mismatch" and _v2["mismatch_col"] == "close"
         and _v3["status"] == "no_overlap"
         and parity_verdict(_base, None)["status"] == "no_overlap")
    print("  [updater] parity verdict: quote-tail ahead is not a rewrite... "
          + ("PASS" if i else "FAIL"))
    ok &= i

    # E: same-evening quote top-up -- the tail session the history face has not
    # printed yet is written from the batch quote face, and every way a quote
    # can be the wrong bar is a refusal rather than a guess
    def _qfields(qdate, o, prev, c, h, lo, vol, amt):
        f = [""] * 33
        f[0], f[1], f[2], f[3], f[4], f[5] = ("name", str(o), str(prev),
                                              str(c), str(h), str(lo))
        f[8], f[9], f[30] = str(vol), str(amt), qdate
        return f

    with tempfile.TemporaryDirectory() as td:
        cols = ["date", "open", "high", "low", "close", "volume", "amount"]
        cal = ["2026-10-23", "2026-10-26", "2026-10-27"]
        lag = os.path.join(td, "510300.csv")
        cur = os.path.join(td, "510050.csv")
        pd.DataFrame([["2026-10-23", 4.0, 4.1, 3.9, 4.05, 100, 405],
                      ["2026-10-26", 4.155, 4.187, 4.13, 4.179, 200, 836]],
                     columns=cols).to_csv(lag, index=False)
        pd.DataFrame([["2026-10-26", 3.0, 3.1, 2.9, 3.05, 50, 152],
                      ["2026-10-27", 3.06, 3.09, 3.04, 3.08, 60, 185]],
                     columns=cols).to_csv(cur, index=False)
        q = {"sh510300": _qfields("2026-10-27", 4.18, 4.179, 4.2, 4.22, 4.17,
                                  300, 1254)}
        after = dt.datetime(2026, 10, 27, 16, 0)
        r1 = quote_topup([lag, cur], after, quote_fields=lambda s: q, calendar=cal)
        got = pd.read_csv(lag)
        e = (r1["status"] == "appended" and r1["appended"] == 1
             and r1["lagging"] == ["510300"]
             and got["date"].iloc[-1] == "2026-10-27"
             and abs(float(got["close"].iloc[-1]) - 4.2) < 1e-9
             and abs(float(got["close"].iloc[-2]) - 4.179) < 1e-9)  # history kept
        # idempotent: the same evening run twice adds nothing
        r2 = quote_topup([lag, cur], after, quote_fields=lambda s: q, calendar=cal)
        e &= r2["status"] == "noop_current" and len(pd.read_csv(lag)) == 3
        # before the close there is no completed session to write
        pd.DataFrame([["2026-10-26", 4.155, 4.187, 4.13, 4.179, 200, 836]],
                     columns=cols).to_csv(lag, index=False)
        r3 = quote_topup([lag], dt.datetime(2026, 10, 27, 10, 0),
                         quote_fields=lambda s: q, calendar=cal)
        e &= r3["status"] == "gated_before_close" and len(pd.read_csv(lag)) == 1
        print("  [updater] quote top-up: tail session written, history kept, "
              "idempotent, close-gated... " + ("PASS" if e else "FAIL"))
        ok &= e

        # refusals: wrong session date / prev-close drift / short frame / no quote
        def run_one(fields, sym="sh510300"):
            pd.DataFrame([["2026-10-26", 4.155, 4.187, 4.13, 4.179, 200, 836]],
                         columns=cols).to_csv(lag, index=False)
            fx = {sym: fields} if fields else {}
            return quote_topup([lag], after, quote_fields=lambda s: fx,
                               calendar=cal), len(pd.read_csv(lag))
        r4, n4 = run_one(_qfields("2026-10-28", 4.18, 4.179, 4.2, 4.22, 4.17,
                                  300, 1254))
        r5, n5 = run_one(_qfields("2026-10-27", 4.18, 4.0, 4.2, 4.22, 4.17,
                                  300, 1254))
        r6, n6 = run_one(["name", "4.18", "4.179", "4.2"])
        r7, n7 = run_one(None)
        why = [x["reason"] for x in r4["refused"] + r5["refused"]
               + r6["refused"] + r7["refused"]]
        f = (n4 == 1 and n5 == 1 and n6 == 1 and n7 == 1
             and any(w.startswith("quote_date") for w in why)
             and any(w.startswith("prev_close_drift") for w in why)
             and any(w.startswith("short_quote") for w in why)
             and "no_quote" in why
             and all(x["status"] == "refused_all" for x in (r4, r5, r6, r7)))
        print("  [updater] quote top-up refuses wrong bars (date/drift/short/"
              "missing)... " + ("PASS" if f else "FAIL"))
        ok &= f

    # E2: the provenance ledger. The status payload is overwritten by the next
    # run, so unless the top-up writes a line of its own, "which bars tonight
    # came from the quote face" is unanswerable twenty minutes later.
    with tempfile.TemporaryDirectory() as td:
        lg = os.path.join(td, "ledger.jsonl")
        nothing = record_quote_topup({"status": "noop_current", "appended": 0,
                                      "rows": [], "refused": []}, path=lg)
        # read the file's existence BEFORE the appending call: asking afterwards
        # answers "did the append create it", not "did the no-op leave it alone".
        pre_exists = os.path.exists(lg)
        lag2 = os.path.join(td, "510300.csv")
        lcols = ["date", "open", "high", "low", "close", "volume", "amount"]
        pd.DataFrame([["2026-10-26", 4.155, 4.187, 4.13, 4.179, 200, 836]],
                     columns=lcols).to_csv(lag2, index=False)
        r1 = quote_topup([lag2], after,
                         quote_fields=lambda s: {"sh510300": _qfields(
                             "2026-10-27", 4.18, 4.179, 4.2, 4.22, 4.17, 300, 1254)},
                         calendar=cal, appender=lambda p, row: None)
        one = record_quote_topup(r1, path=lg)
        rows = read_quote_ledger(lg)
        e2 = (nothing is None and pre_exists is False
              and one is not None and one["session"] == "2026-10-27"
              and one["appended"] == 1 and one["symbols"] == ["510300"]
              and len(rows) == 1 and rows[0]["session"] == "2026-10-27"
              and read_quote_ledger(os.path.join(td, "nope.jsonl")) == [])
        print("  [updater] quote top-up leaves a provenance line per session, "
              "and none for a no-op run... " + ("PASS" if e2 else "FAIL"))
        ok &= e2

    # D: source parity on real data (network; SKIP if unreachable)
    try:
        mine = load_existing(os.path.join(PATHS.daily_dir,
                                          f"{PROBE_SYMBOL}.csv"))
        v = parity_verdict(fetch_history(PROBE_SYMBOL), mine)
        ahead = v["ahead"]
        tail = (" [local ahead of source by %d bar(s) %s..%s -- quote-tail "
                "rows written before the history face publishes them, no "
                "source evidence yet]" % (len(ahead), ahead[-1], ahead[0])
                ) if ahead else ""
        if v["status"] == "no_overlap":
            print(f"  [updater] source parity {PROBE_SYMBOL}... SKIP "
                  f"(no overlapping bar){tail}")
        else:
            if v["status"] == "match":
                verdict = "PASS"
            elif v["status"] == "mismatch":
                verdict = (f"FAIL (source history changed: "
                           f"{v['mismatch_col']})")
            else:
                verdict = "FAIL (source history changed!)"
            ok &= v["status"] == "match"
            print(f"  [updater] source parity {PROBE_SYMBOL} "
                  f"@ {v['compared_date']}... {verdict}{tail}")
    except Exception as e:  # noqa: BLE001 -- offline selftest stays runnable
        print(f"  [updater] source parity... SKIP (network: {type(e).__name__})")
    return bool(ok)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        print(f"=== update_daily selftest {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        return 0 if selftest() else 1

    now = dt.datetime.now()
    sim = "--simulate-primary-failure" in argv
    status_out = SIM_STATUS_PATH if sim else STATUS_PATH
    print(f"=== Bigmoney daily update {time.strftime('%Y-%m-%d %H:%M:%S')} ==="
          + ("  [SIMULATED PRIMARY FAILURE -- acceptance evidence only]"
             if sim else ""))
    print(f"core pool: {len(core_files())} CSVs | "
          f"today-bar guard: >= {CLOSE_ACCEPT_TIME}")
    if not acquire_lock(LOCK_PATH):
        print("another live update_daily instance holds the lock -> stand down")
        return 0
    try:
        summary = run_update(now, fetcher=_sim_primary_down() if sim else None)
        # T-08 dual-leg fallback: diagnosis source + post-sweep parity audit
        # (additive fields; validation-leg errors never break the run)
        _validation_fallback(summary)
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
        _write_status_atomic(summary, status_out)
        print(f"status -> {status_out}")
        return exit_code
    except Exception as e:  # noqa: BLE001 -- status log must never crash the run
        emergency = {"updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                     "now": str(now), "run_error": f"{type(e).__name__}: {e}",
                     "exit_code": 1, "hook_ok": None, "hook_exit": None}
        try:
            _write_status_atomic(emergency, status_out)
        except Exception:  # noqa: BLE001 -- best effort
            pass
        raise
    finally:
        release_lock(LOCK_PATH)


if __name__ == "__main__":
    sys.exit(main())
