"""Individual-stock money-flow forward collector (R63 bm-a, claim MSG-20260924-0920).

Spec: research/shortline/MF_COLLECTOR.md (frozen before implementation).
Lane: data dept, O-1620 GM-approved money-flow domain; R58 source-audit follow-up.

v2 (T-2026-09-25-39, R109): daykline face proven dead (endpoint-level hard
block, frozen digest DIGEST-20260925-moneyflow-daykline-dead). Primary face =
push2 clist rank cross-section (fid=f62, ~60 req/day full market, forward
collect one row per symbol per completed trading day, date consumer-stamped
from the local ETF calendar 15:30 convention). Legacy daykline refresh stays
as opportunistic backfill lane (120td window = natural gap repairer).

Core design (from R58 finding: push2his returns a rolling 120-trading-day window
per stock): periodic FULL-universe refresh (5222 symbols, 2.5s throttle,
detached background process) keeps the daily panel gapless as long as the
refresh interval stays < 120 trading days. Gate trigger = panel cutoff older
than 20 trading days OR panel not complete; first pull starts the clock.

Storage (gitignored, regenerable):
  data/moneyflow/per/<code>.csv        append-only per-symbol daily rows
  data/moneyflow/_progress.json        checkpoint {done:[], attempts:{}}
  data/moneyflow/_refresh.lock         {pid, ts} while refresh runs
Status (tracked): results/moneyflow_update_status.json

Semantics (update_futures family):
- append-only; overlap verified on primary field zhu_li (yuan, tol 1.0);
  mismatch -> that symbol's local file NOT touched, counted, final exit 3
- completeness guard: a row dated today only persists after 15:30 local
  (intraday live partial values must not enter the panel)
- throttle 2.5s/request; fuse = 5 consecutive fetch failures -> stop with
  checkpoint preserved (exit 2, complete=false); gate relaunches after the
  30-min spawn throttle, resuming from checkpoint
- a symbol failing >= 3 cumulative refreshes is quarantined (honest, so the
  universe can complete without lying about permanently dead endpoints)
- lane ownership guard (R31 watchdog precedent): the auto-gate only acts on
  bm-a (fleet/machine.json machine_id); other machines no-op honestly, so the
  shared S6 prompt never triggers duplicate pulls on bm-b/bm-c

Exit codes (gate):  0 = ok/no-op/spawned/in-progress; 2 = machinery failure
Exit codes (refresh): 0 = universe complete, mismatch-free;
                      2 = not complete (fuse-stopped / source-blocked / failures remain -- checkpoint preserved, gate self-heals);
                      3 = complete but overlap mismatches occurred (panel updated)
"""
from __future__ import annotations

import csv as _csv
import datetime as dt
import glob as _glob
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "moneyflow")
PER_DIR = os.path.join(DATA_DIR, "per")
PROGRESS = os.path.join(DATA_DIR, "_progress.json")
LOCK = os.path.join(DATA_DIR, "_refresh.lock")
STATUS = os.path.join(ROOT, "results", "moneyflow_update_status.json")
LOG = os.path.join(ROOT, "logs", "moneyflow_refresh.log")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")

LANE_OWNER = "bm-a"          # R31 lane-ownership precedent
SLEEP_S = 2.5                # EM citizenship throttle (daykline lane)
FUSE_LIMIT = 5               # consecutive fetch failures (any kind) -> stop
CONN_STOP = 3                # consecutive connection-level failures -> source-block stop
CONN_MARKERS = ("ConnectionError", "Timeout", "RemoteDisconnected",
                "ChunkedEncodingError", "ProtocolError", "MaxRetryError")
QUARANTINE_AT = 3            # cumulative refresh failures -> skip forever
MAX_ROWS = 130               # 120td window + source slack
MIN_SPAWN_S = 30 * 60        # spawn throttle (shared by both lanes' gates)
STALE_TD = 20                # daykline backfill trigger: panel age in trading days

# --- v2 rank lane (T-2026-09-25-39; daykline face proven dead, frozen digest
# DIGEST-20260925-moneyflow-daykline-dead: push2his fflow/daykline = endpoint-
# level hard block >=25h both hosts; same-domain clist rank face ALIVE,
# total=5920. Primary face = one forward row per symbol per completed day.) ---
RANK_URL = "https://push2.eastmoney.com/api/qt/clist/get"
RANK_PARAMS = {
    "pn": 1, "pz": 100, "po": 1, "np": 1, "fltt": 2, "invt": 2,
    "fid": "f62",
    # R108 probe face: 沪深A + 北交 (frozen digest table row 4)
    "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048",
    "fields": "f12,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87",
}
RANK_SLEEP_S = 2.5           # citizenship pace (akshare/daykline-lane precedent;
                             # 0.5s draft pace tripped intermittent RemoteDisconnected
                             # at bulk -- R109 live-fire, frozen in round report)
RANK_PAGE_RETRIES = 2         # per-page retry for intermittent conn drops
RANK_RETRY_SLEEP_S = 5.0
RANK_MAX_PAGES = 80          # 5920/100 + slack
RANK_FIELD_MAP = {           # 12 value cols -> FROZEN panel schema, zero drift
    "f2": "收盘价", "f3": "涨跌幅", "f62": "主力净流入-净额",
    "f184": "主力净流入-净占比", "f66": "超大单净流入-净额",
    "f69": "超大单净流入-净占比", "f72": "大单净流入-净额",
    "f75": "大单净流入-净占比", "f78": "中单净流入-净额",
    "f81": "中单净流入-净占比", "f84": "小单净流入-净额",
    "f87": "小单净流入-净占比",
}

# frozen schema: 12 value columns (R58 probe A, source Chinese names kept)
FLOW_COLS = ["收盘价", "涨跌幅", "主力净流入-净额", "主力净流入-净占比",
             "超大单净流入-净额", "超大单净流入-净占比",
             "大单净流入-净额", "大单净流入-净占比",
             "中单净流入-净额", "中单净流入-净占比",
             "小单净流入-净额", "小单净流入-净占比"]
PRIMARY = "主力净流入-净额"   # overlap verification field (yuan)
PRIMARY_TOL = 1.0             # cent-level stability tolerance


def _clear_proxy_env():
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)


def _no_proxy_opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


# ------------------------------------------------------- calendar gates (pure)

_DATES_CACHE = None
COMPLETE_HOUR = dt.time(15, 30)


def _load_trading_dates():
    """Local ETF trading-day calendar (update_lhb/update_futures pattern:
    data/daily 510300.csv primary, glob fallback, None -> weekday approx)."""
    global _DATES_CACHE
    if _DATES_CACHE is not None:
        return _DATES_CACHE
    cands = [os.path.join(ROOT, "data", "daily", "510300.csv")]
    cands += [p for p in sorted(_glob.glob(os.path.join(ROOT, "data", "daily", "*.csv")))
              if p != cands[0]]
    dates = None
    for p in dict.fromkeys(cands):
        try:
            with io.open(p, "r", encoding="utf-8") as f:
                ds = {str(r.get("date") or "") for r in _csv.DictReader(f)}
            ds = sorted(d for d in ds if re.match(r"^\d{4}-\d{2}-\d{2}$", d))
            if len(ds) >= 100:
                dates = ds
                break
        except Exception:
            continue
    _DATES_CACHE = dates
    return dates


def expected_latest_bar_date(now, dates=None):
    """Latest date a COMPLETE daily row can exist at `now` (15:30 convention,
    evening source lag self-heals -- expected_disclosure_date precedent)."""
    if dates is None:
        dates = _load_trading_dates()
    today = now.date().isoformat()
    if now.time() >= COMPLETE_HOUR:
        if dates is None:
            if now.weekday() < 5:
                return today
        elif today in dates:
            return today
    if dates is not None:
        prior = [d for d in dates if d < today]
        if prior:
            return prior[-1]
    d = now.date() - dt.timedelta(days=1) if now.time() < COMPLETE_HOUR else now.date()
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d.isoformat()


def trading_days_back(anchor, dates, n):
    """Trading date `n` trading days strictly before `anchor`; None if the
    calendar is too short or absent."""
    if not dates:
        return None
    prior = [d for d in dates if d < str(anchor)]
    if len(prior) >= n:
        return prior[-n]
    return prior[0] if prior else None


def stale_gate(panel_cutoff, now, dates=None, max_age_td=STALE_TD):
    """(needs_refresh, reason). Zero-network freshness verdict for the panel."""
    if panel_cutoff is None:
        return True, "no local panel (first run)"
    expected = expected_latest_bar_date(now, dates)
    if str(panel_cutoff) >= expected:
        return False, (f"panel cutoff {panel_cutoff} covers complete-bar date {expected}")
    required = trading_days_back(expected, dates, max_age_td)
    if required is None:
        required = (dt.date.fromisoformat(expected)
                    - dt.timedelta(days=28)).isoformat()  # degenerate approx
    if str(panel_cutoff) >= required:
        return False, (f"panel cutoff {panel_cutoff} within {max_age_td} trading "
                       f"days of {expected} (rolling 120td window keeps it gapless)")
    return True, f"panel cutoff {panel_cutoff} older than {required} (stale)"


def completeness_filter(rows, now=None):
    """Drop trailing rows dated today when now < 15:30 (live intraday partial)."""
    now = now or dt.datetime.now()
    if now.time() >= COMPLETE_HOUR or not rows:
        return rows, 0
    today = now.date().isoformat()
    kept, dropped = list(rows), 0
    while kept and str(kept[-1].get("date", "")) == today:
        kept.pop()
        dropped += 1
    return kept, dropped


# ------------------------------------------------------------ validate + merge


def validate_rows(rows):
    """Dates ISO/strictly-increasing/unique; primary present & finite;
    row cap. Returns error str or None."""
    prev = None
    saw_primary = False
    for r in rows:
        d = str(r.get("date", ""))
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            return f"bad_date_format:{d}"
        if prev is not None and d <= prev:
            return f"non_monotonic_at:{d}"
        prev = d
        v = r.get(PRIMARY)
        if v is not None and v == v:
            saw_primary = True
    if rows and not saw_primary:
        return f"primary_{PRIMARY}_all_nan"
    if len(rows) > MAX_ROWS:
        return f"row_cap_exceeded:{len(rows)}>{MAX_ROWS}"
    return None


def merge_incremental(local_rows, source_rows, primary=PRIMARY, tol=PRIMARY_TOL):
    """Append-only merge; overlap compared on `primary` only (price cols are
    provenance, source may re-adjust them). Mismatch -> merged=False."""
    local_by_date = {str(r["date"]): r for r in local_rows}
    mismatch, overlap = None, 0
    for r in source_rows:
        d = str(r["date"])
        loc = local_by_date.get(d)
        if loc is None:
            continue
        overlap += 1
        lv, sv = loc.get(primary), r.get(primary)
        if lv is None and sv is None:
            continue
        if lv is None or sv is None or abs(float(lv) - float(sv)) > tol:
            mismatch = d
            break
    if mismatch:
        return {"appended": 0, "overlap": overlap, "mismatch": mismatch,
                "merged": False, "merged_rows": None}
    new_rows = [r for r in source_rows if str(r["date"]) not in local_by_date]
    merged = list(local_rows) + new_rows
    merged.sort(key=lambda r: str(r["date"]))
    return {"appended": len(new_rows), "overlap": overlap, "mismatch": None,
            "merged": True, "merged_rows": merged}


# --------------------------------------------------------------- csv + status


def rows_to_csv_text(rows):
    buf = io.StringIO()
    w = _csv.writer(buf, lineterminator="\n")
    w.writerow(["date"] + FLOW_COLS)
    for r in rows:
        out = [str(r["date"])]
        for col in FLOW_COLS:
            v = r.get(col)
            if v is None or v != v:
                out.append("")
            else:
                out.append(f"{float(v):.10g}")
        w.writerow(out)
    return buf.getvalue()


def read_local_csv(path):
    if not os.path.exists(path):
        return []
    with io.open(path, "r", encoding="utf-8") as f:
        rd = _csv.DictReader(f)
        rows = []
        for x in rd:
            r = {"date": x["date"]}
            for col in FLOW_COLS:
                v = x.get(col, "")
                try:
                    r[col] = float(v) if v not in ("", None) else None
                except (TypeError, ValueError):
                    r[col] = None
            rows.append(r)
    return rows


def atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, path)


def load_status():
    if os.path.exists(STATUS):
        try:
            with io.open(STATUS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def write_status(payload):
    atomic_write(STATUS, json.dumps(payload, ensure_ascii=False, indent=2))


def load_progress():
    if os.path.exists(PROGRESS):
        try:
            with io.open(PROGRESS, "r", encoding="utf-8") as f:
                p = json.load(f)
            return {"done": set(p.get("done", [])),
                    "attempts": dict(p.get("attempts", {}))}
        except Exception:
            pass
    return {"done": set(), "attempts": {}}


def save_progress(prog):
    atomic_write(PROGRESS, json.dumps(
        {"done": sorted(prog["done"]),
         "attempts": {k: int(v) for k, v in prog["attempts"].items()}},
        ensure_ascii=False))


# ------------------------------------------------------------------ universe


def universe_codes(bars_dir=None):
    """(codes, skipped) from Money02 bars glob; market deriv: 6->sh, 0/3->sz."""
    bars_dir = bars_dir or BARS_DIR
    codes, skipped = [], []
    for p in sorted(_glob.glob(os.path.join(bars_dir, "*.parquet"))):
        stem = os.path.splitext(os.path.basename(p))[0]
        code = re.sub(r"^(sh|sz|SH|SZ)", "", stem)
        if not re.match(r"^\d{6}$", code):
            skipped.append(stem)
            continue
        codes.append(code)
    # dedupe bare/sh-prefixed twins (J6 lesson): bare wins, prefix twin same code
    return sorted(set(codes)), skipped


def market_of(code):
    if code.startswith("6"):
        return "sh"
    if code.startswith("0") or code.startswith("3"):
        return "sz"
    return None  # bj/unknown -> honest skip


# --------------------------------------------------------------------- fetch


def _is_conn_error(ename, emsg=""):
    """Source-level (connection) failure classifier -- quarantine-storm guard."""
    return any(m in ename or m in str(emsg)[:200] for m in CONN_MARKERS)


def fetch_one(code, market):
    """Rolling-120d daily rows for one stock via akshare (direct connection)."""
    import akshare as ak
    df = ak.stock_individual_fund_flow(stock=code, market=market)
    if df is None or len(df) == 0:
        return []
    rows = []
    for _, x in df.iterrows():
        d = str(x.get("日期"))[:10]
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            continue
        r = {"date": d}
        for col in FLOW_COLS:
            v = x.get(col)
            try:
                r[col] = None if v is None or v != v else float(v)
            except (TypeError, ValueError):
                r[col] = None
        rows.append(r)
    rows.sort(key=lambda r: r["date"])
    # dedupe by date (source safety)
    seen, out = set(), []
    for r in rows:
        if r["date"] in seen:
            continue
        seen.add(r["date"])
        out.append(r)
    return out


# ------------------------------------------------------------------ refresh


def _write_lock():
    os.makedirs(DATA_DIR, exist_ok=True)
    atomic_write(LOCK, json.dumps({"pid": os.getpid(),
                                  "ts": dt.datetime.now().isoformat(timespec="seconds")}))


def _clear_lock():
    try:
        os.remove(LOCK)
    except FileNotFoundError:
        pass


def _pid_alive(pid):
    try:
        out = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
            capture_output=True, timeout=15)
        txt = out.stdout.decode("utf-8", errors="replace")
        return f'"{pid}"' in txt
    except Exception:
        return False


def _lock_alive():
    """True only if lock exists AND its pid is running (stale lock -> False)."""
    if not os.path.exists(LOCK):
        return False
    try:
        with io.open(LOCK, "r", encoding="utf-8") as f:
            pid = int(json.load(f).get("pid", 0))
        if pid and _pid_alive(pid):
            return True
    except Exception:
        pass
    return False


def refresh(limit=None):
    """Long-running full-universe pull. Checkpointed + fused; detached-safe."""
    codes, skipped_glob = universe_codes()
    if len(codes) < 100:
        print(f"universe unavailable ({len(codes)} codes) -- refusing honest exit 2")
        return 2
    _clear_proxy_env()
    _write_lock()
    try:
        prog = load_progress()
        quarantined = {c for c, n in prog["attempts"].items() if n >= QUARANTINE_AT}
        todo = [c for c in codes
                if c not in prog["done"] and c not in quarantined]
        if limit is not None:
            todo = todo[:int(limit)]
        now0 = dt.datetime.now()
        st = load_status()
        st.update({
            "ts": now0.isoformat(timespec="seconds"),
            "mode": f"refresh in progress (todo={len(todo)}/{len(codes)}, "
                    f"done={len(prog['done'])}, quarantined={len(quarantined)})",
            "panel": dict(st.get("panel") or {},
                          complete=False, universe_n=len(codes)),
            "claim": "MSG-20260924-0920-bm-a-moneyflow-collector",
        })
        write_status(st)

        consec_fail, consec_conn, appended_total = 0, 0, 0
        failures, mismatches = [], []
        conn_stopped = False
        panel_cutoff, n_rows_total = None, 0
        t_start = time.time()
        for i, code in enumerate(todo):
            mkt = market_of(code)
            if mkt is None:
                prog["attempts"][code] = prog["attempts"].get(code, 0) + 1
                failures.append(f"{code}:unmapped_market")
                save_progress(prog)
                continue
            try:
                rows = fetch_one(code, mkt)
                rows, dropped_today = completeness_filter(rows)
                err = validate_rows(rows)
                if err:
                    raise RuntimeError(f"validation_fail:{err}")
                p = os.path.join(PER_DIR, code + ".csv")
                local = read_local_csv(p)
                res = merge_incremental(local, rows)
                if not res["merged"]:
                    mismatches.append(f"{code}@{res['mismatch']}")
                    last = str(local[-1]["date"]) if local else None
                else:
                    atomic_write(p, rows_to_csv_text(res["merged_rows"]))
                    appended_total += res["appended"]
                    last = str(res["merged_rows"][-1]["date"]) if res["merged_rows"] else None
                if last and (panel_cutoff is None or last > panel_cutoff):
                    panel_cutoff = last
                prog["done"].add(code)
                prog["attempts"].pop(code, None)
                consec_fail = 0
                consec_conn = 0
            except Exception as e:
                ename, emsg = type(e).__name__, str(e)
                is_conn = _is_conn_error(ename, emsg)
                if is_conn:
                    # source-level block (per-IP, fluctuating -- r40/r46 precedent):
                    # do NOT bump per-symbol attempts (quarantine-storm guard),
                    # stop fast so the 30-min gate retry costs only 3 requests.
                    consec_conn += 1
                    failures.append(f"{code}:conn:{ename}")
                    if consec_conn >= CONN_STOP:
                        conn_stopped = True
                        print(f"source-level block suspected ({consec_conn} consecutive "
                              f"connection failures) -- stopping, checkpoint intact, "
                              f"gate retries after throttle window")
                        break
                else:
                    prog["attempts"][code] = prog["attempts"].get(code, 0) + 1
                    failures.append(f"{code}:{ename}:{emsg[:120]}")
                consec_fail += 1
            save_progress(prog)
            if consec_fail >= FUSE_LIMIT:
                print(f"FUSE tripped after {i + 1} symbols ({FUSE_LIMIT} consecutive "
                      f"failures) -- checkpoint preserved, gate will resume")
                break
            if i < len(todo) - 1:
                time.sleep(SLEEP_S)

        # panel row/symbol census from directory (cheap one-shot at end)
        n_symbols = len(_glob.glob(os.path.join(PER_DIR, "*.csv")))
        fuse_stopped = consec_fail >= FUSE_LIMIT
        stopped_early = fuse_stopped or conn_stopped
        complete = (not stopped_early) and (len(prog["done"]) + len(
            {c for c, n in prog["attempts"].items() if n >= QUARANTINE_AT}
        ) >= len(codes)) and (limit is None)
        now1 = dt.datetime.now()
        st.update({
            "ts": now1.isoformat(timespec="seconds"),
            "mode": ("refresh source-blocked (connection-level)" if conn_stopped
                     else "refresh fuse-stopped" if fuse_stopped
                     else "refresh finished"),
            "panel": {
                "cutoff": panel_cutoff,
                "complete": bool(complete),
                "n_symbols": n_symbols,
                "universe_n": len(codes),
            },
            "last_refresh": {
                "started": now0.isoformat(timespec="seconds"),
                "elapsed_min": round((time.time() - t_start) / 60, 1),
                "appended": appended_total,
                "failures": len(failures),
                "failure_head": failures[:5],
                "mismatches": mismatches[:10],
                "n_mismatches": len(mismatches),
                "quarantined": sorted(
                    c for c, n in prog["attempts"].items() if n >= QUARANTINE_AT)[:20],
                "skipped_glob": skipped_glob[:5],
                "fuse_stopped": fuse_stopped,
                "conn_stopped": conn_stopped,
            },
        })
        write_status(st)
        print(f"refresh done: +{appended_total} rows, {len(failures)} failures, "
              f"{len(mismatches)} mismatches, complete={complete}, "
              f"panel cutoff={panel_cutoff}")
        if mismatches and complete:
            return 3
        if fuse_stopped or conn_stopped or not complete:
            return 2          # honest: not complete (failures/block remain)
        return 0
    finally:
        _clear_lock()


# ---------------------------------------------------------------- v2 rank lane


def rank_pull_allowed(now=None, dates=None):
    """(allowed, reason). Rank face = live snapshot with NO date field:
    block the ticket's intraday mutation window (09:15-15:05) AND the
    15:05-15:30 band where values are already today's finals but the 15:30
    stamp convention would still date them to the prior trading day
    (stamp/value-day mismatch hazard). Net: no pull on trading days
    09:15-15:30; pre-open, night, non-trading days fine."""
    now = now or dt.datetime.now()
    t = now.time()
    if not (dt.time(9, 15) <= t < dt.time(15, 30)):
        return True, ""
    today = now.date().isoformat()
    ds = dates if dates is not None else _load_trading_dates()
    if ds is None:
        if now.weekday() < 5:
            return False, (f"weekday {today} inside 09:15-15:30 "
                          f"(calendar absent, conservative block)")
        return True, "weekend (calendar absent, weekday approx)"
    if today in ds:
        return False, (f"trading day {today} inside 09:15-15:30 "
                       f"(snapshot mutating / stamp-hazard band)")
    return True, f"{today} not a trading day (snapshot static)"


def rank_row_from_item(item):
    """One clist item -> FLOW_COLS row (values yuan/percent as served).
    '-' = suspended/absent -> None (honest, no fabrication)."""
    row = {}
    for f, col in RANK_FIELD_MAP.items():
        v = item.get(f)
        try:
            row[col] = None if v in (None, "", "-") else float(v)
        except (TypeError, ValueError):
            row[col] = None
    return row


def rank_merge_one(local_rows, stamp, mapped_row, primary=PRIMARY, tol=PRIMARY_TOL):
    """(action, payload) for one symbol. Idempotent same-day skip / honest
    mismatch / clean append; never rewrites existing rows."""
    stamp = str(stamp)
    for r in local_rows:
        if str(r.get("date")) == stamp:
            lv, sv = r.get(primary), mapped_row.get(primary)
            if lv is None and sv is None:
                return "skip_same_day", "both_none"
            if lv is None or sv is None or abs(float(lv) - float(sv)) > tol:
                return "mismatch", f"{stamp}:{lv}!={sv}"
            return "skip_same_day", "overlap_match"
    if any(str(r.get("date")) > stamp for r in local_rows):
        return "mismatch", "stamp_behind_local"   # clock/calendar anomaly: don't touch
    return "append", list(local_rows) + [dict(mapped_row, date=stamp)]


def rank_universe_join(items, codes):
    """(in_universe, not_in_universe): rank-face x bars-universe code join."""
    cs = set(codes)
    in_u = [c for c in codes if c in items]
    not_u = [c for c in items if c not in cs]
    return in_u, not_u


def _fetch_rank_page_impl(pn, timeout=10):
    """One clist page, direct urllib + ProxyHandler({}) (digest T4 recipe:
    registry proxies defeat _clear_proxy_env alone). Query string built
    manually to keep EM's literal '+' separators intact."""
    params = dict(RANK_PARAMS, pn=pn)
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(
        RANK_URL + "?" + qs,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                 "Referer": "https://quote.eastmoney.com/"})
    with _no_proxy_opener().open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def fetch_rank_all_pages(fetch_page=None, page_size=100,
                         max_pages=RANK_MAX_PAGES, sleep_s=RANK_SLEEP_S,
                         retry_sleep_s=RANK_RETRY_SLEEP_S, retries=RANK_PAGE_RETRIES):
    """({code: item}, total, pages, error). All-or-nothing: caller aborts on
    any page error after in-place retries -- same-day idempotency makes the
    redo cheap. Intermittent RemoteDisconnected drops are retried per page
    (EM conn-level flakiness, R109 live-fire evidence)."""
    fetch_page = fetch_page or _fetch_rank_page_impl
    out, total, pn = {}, None, 1
    while pn <= max_pages:
        js, err = None, None
        for attempt in range(retries + 1):
            try:
                js = fetch_page(pn)
                err = None
                break
            except Exception as e:
                err = f"page {pn}: {type(e).__name__}: {str(e)[:160]}"
                if attempt < retries:
                    time.sleep(retry_sleep_s)
        if err:
            return out, total, pn, err
        data = (js or {}).get("data") or {}
        if total is None:
            try:
                total = int(data.get("total") or 0)
            except (TypeError, ValueError):
                total = 0
        diff = data.get("diff") or []
        if not diff:
            break
        for item in diff:
            code = str(item.get("f12", ""))
            if re.match(r"^\d{6}$", code):
                out[code] = item
        if (total and len(out) >= total) or len(diff) < page_size:
            break
        pn += 1
        if pn <= max_pages:
            time.sleep(sleep_s)
    return out, total, pn, None


def rank_stale(status=None, now=None, dates=None):
    """(needs, reason). v2 gate cadence for the rank lane only: daily-forward
    -- cutoff lags 1td -> trigger (replaces the 20td logic; daykline backfill
    lane keeps its own stale_gate untouched)."""
    st = status if status is not None else load_status()
    rank = st.get("rank") or {}
    stamp = rank.get("last_stamp")
    expected = expected_latest_bar_date(now or dt.datetime.now(), dates)
    if stamp is None:
        return True, "rank lane never fired"
    if str(stamp) < str(expected):
        return True, f"rank stamp {stamp} lags expected {expected}"
    return False, f"rank stamp {stamp} covers {expected}"


def rank_pass(fetch_page=None):
    """v2 primary face: one forward pass (child of gate(), or manual for the
    live-fire acceptance). Exit 0 = full pass clean / no-op / deferred;
    2 = fetch/machinery failure (nothing written); 3 = full pass, honest
    mismatches counted (appended rows stand, mismatched locals untouched)."""
    now = dt.datetime.now()
    st = load_status()
    allowed, why = rank_pull_allowed(now)
    if not allowed:
        st["rank"] = dict(st.get("rank") or {},
                          ts=now.isoformat(timespec="seconds"), mode="no-op: " + why)
        write_status(st)
        print("no-op:", why)
        return 0
    if _lock_alive():
        st["rank"] = dict(st.get("rank") or {}, ts=now.isoformat(timespec="seconds"),
                          mode="deferred: daykline refresh holds the panel lock")
        write_status(st)
        print("deferred: daykline refresh in progress")
        return 0
    stamp = expected_latest_bar_date(now)
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(stamp)):
        print("calendar unavailable (stamp undeterminable) -> honest exit 2")
        return 2
    codes, _ = universe_codes()
    if len(codes) < 100:
        print(f"universe unavailable ({len(codes)} codes) -- refusing honest exit 2")
        return 2
    _clear_proxy_env()
    _write_lock()
    try:
        t0 = time.time()
        items, total, pages, err = fetch_rank_all_pages(fetch_page=fetch_page)
        if err or not items:
            st["rank"] = dict(st.get("rank") or {},
                              ts=dt.datetime.now().isoformat(timespec="seconds"),
                              mode=f"fetch_failed: {err or 'empty rank face'}")
            write_status(st)
            print(f"rank pass failed: {err or 'empty rank face'} -> exit 2 (nothing written)")
            return 2
        in_u, not_u = rank_universe_join(items, codes)
        appended = skipped_same = mismatches = 0
        mismatch_head = []
        for code in in_u:
            row = rank_row_from_item(items[code])
            p = os.path.join(PER_DIR, code + ".csv")
            local = read_local_csv(p)
            action, payload = rank_merge_one(local, stamp, row)
            if action == "skip_same_day":
                skipped_same += 1
            elif action == "mismatch":
                mismatches += 1
                if len(mismatch_head) < 10:
                    mismatch_head.append(f"{code}:{payload}")
            else:
                atomic_write(p, rows_to_csv_text(payload))
                appended += 1
        st["rank"] = dict(st.get("rank") or {},
                          ts=dt.datetime.now().isoformat(timespec="seconds"),
                          mode="ok" if not mismatches else "ok_with_mismatches",
                          last_stamp=stamp,
                          rank_face_n=len(items), total=total, pages=pages,
                          universe_n=len(codes),
                          appended=appended, skipped_same_day=skipped_same,
                          not_in_rank_face=len(codes) - len(in_u),
                          skipped_not_in_universe=len(not_u),
                          mismatches_n=mismatches, mismatch_head=mismatch_head,
                          last_run_elapsed_s=round(time.time() - t0, 1))
        write_status(st)
        print(f"rank pass {stamp}: +{appended} rows, {skipped_same} same-day skips, "
              f"{len(codes) - len(in_u)} not in rank face, {len(not_u)} not in universe, "
              f"{mismatches} mismatches")
        return 3 if mismatches else 0
    finally:
        _clear_lock()


# ---------------------------------------------------------------------- gate


def _lane_owner_id():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"),
                     "r", encoding="utf-8-sig") as f:
            return str(json.load(f).get("machine_id", ""))
    except Exception:
        return ""


def spawn_detached(arg):
    """Silent detached child (zero popups); log appended, lock self-managed."""
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    with io.open(LOG, "a", encoding="utf-8") as lf:
        subprocess.Popen(
            [sys.executable, os.path.abspath(__file__), arg],
            stdout=lf, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, creationflags=flags, close_fds=False)
    # child inherits lf; parent keeps running (R20 backfill precedent)


def spawn_detached_refresh():
    spawn_detached("refresh")


def gate():
    """S6 step: v2 rank lane first (daily-forward, T-39), then the legacy
    daykline opportunistic-backfill gate (stale_gate + spawn, unchanged)."""
    st = load_status()
    now = dt.datetime.now()
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        # R31 lane guard, hardened per bm-c MSG-20260924-0955: non-owner machines
        # must NEVER touch the shared status mirror (mode/ts falsification +
        # throttle-clock refresh on the owner's status). stdout-only early exit.
        print(f"no-op: moneyflow lane owned by {LANE_OWNER}, not this machine ({owner or '?'})")
        return 0
    # v2 rank lane: cutoff lags 1td -> one forward pass (60 req/day budget)
    rank = st.get("rank") or {}
    needs, reason = rank_stale(st, now)
    if needs:
        allowed, why = rank_pull_allowed(now)
        if not allowed:
            print(f"rank lane needs pass ({reason}) but window guard blocks: {why}")
            # fall through to the legacy lane (its own guards unchanged)
        else:
            last = rank.get("last_spawn_attempt")
            try:
                age = None if not last else (now - dt.datetime.fromisoformat(last)).total_seconds()
            except Exception:
                age = None
            if age is not None and age < MIN_SPAWN_S:
                print(f"throttle: rank spawn {last} ({age / 60:.1f}min ago) < 30min -> no-op")
                return 0
            if _lock_alive():
                print("panel lock alive (daykline refresh or rank pass running) -> no-op")
                return 0
            st["rank"] = dict(rank,
                              last_spawn_attempt=now.isoformat(timespec="seconds"),
                              mode="spawn: detached rank pass", spawn_reason=reason)
            st["ts"] = now.isoformat(timespec="seconds")
            write_status(st)
            spawn_detached("rank")
            print(f"spawned detached rank pass: {reason}")
            return 0
    panel = st.get("panel") or {}
    complete = bool(panel.get("complete"))
    cutoff = panel.get("cutoff") if complete else None
    needs, reason = stale_gate(cutoff, now)
    if not needs:
        st["ts"] = now.isoformat(timespec="seconds")
        st["mode"] = "no-op: panel fresh"
        st["no_op_reason"] = reason
        st["panel"] = panel
        write_status(st)
        print(f"no-op: {reason} -> zero network")
        return 0
    # needs refresh: spawn throttle (mirror written BEFORE acting, r18 lesson)
    last = st.get("last_spawn_attempt")
    if last:
        try:
            age = (now - dt.datetime.fromisoformat(last)).total_seconds()
            if age < MIN_SPAWN_S:
                print(f"throttle: last spawn {last} ({age / 60:.1f}min ago) < 30min -> no-op")
                return 0
        except Exception:
            pass
    if _lock_alive():
        st["ts"] = now.isoformat(timespec="seconds")
        st["mode"] = "refresh in progress (lock alive)"
        write_status(st)
        print("refresh already in progress (lock alive) -> no-op")
        return 0
    _clear_lock()  # stale lock from a dead run
    st["last_spawn_attempt"] = now.isoformat(timespec="seconds")
    st["mode"] = "spawn: detached refresh"
    st["spawn_reason"] = reason
    write_status(st)
    spawn_detached_refresh()
    print(f"spawned detached refresh: {reason}")
    return 0


def status():
    st = load_status()
    print(json.dumps(st, ensure_ascii=False, indent=2)[:3000])
    return 0


# ------------------------------------------------------------------- selftest


def _selftest():
    import tempfile
    now = dt.datetime(2026, 9, 24, 10, 0)
    today = "2026-09-24"
    # S1 completeness guard (futures S1 same family)
    rows = [{"date": "2026-09-22", PRIMARY: 1.0}, {"date": today, PRIMARY: 2.0}]
    kept, dropped = completeness_filter(rows, now=now)
    assert len(kept) == 1 and dropped == 1 and kept[0]["date"] == "2026-09-22"
    kept, dropped = completeness_filter(rows, now=dt.datetime(2026, 9, 24, 15, 31))
    assert len(kept) == 2 and dropped == 0
    kept, _ = completeness_filter([{"date": "2026-09-23", PRIMARY: 1.0}], now=now)
    assert len(kept) == 1
    # S2 validation gate
    good = [{"date": "2026-09-01", PRIMARY: -1.0e8}, {"date": "2026-09-02", PRIMARY: 2.5e8}]
    assert validate_rows(good) is None
    assert validate_rows([{"date": "2026-09-02", PRIMARY: 1.0},
                          {"date": "2026-09-01", PRIMARY: 1.0}]) is not None
    assert validate_rows([{"date": "bad", PRIMARY: 1.0}]) is not None
    assert validate_rows([{"date": "2026-09-01", PRIMARY: None}]) is not None
    assert validate_rows([{"date": f"2026-09-{d:02d}", PRIMARY: float(d)}
                          for d in range(1, 29)]) is None          # 28 rows ok
    assert validate_rows([{"date": f"2026-{m:02d}-{d:02d}", PRIMARY: 1.0}
                          for m in range(1, 6) for d in range(1, 29)]
                         ) is not None                              # >130 rows -> cap
    # S3 merge: clean append (overlap compared on PRIMARY only)
    local = [{"date": "2026-09-01", PRIMARY: -123456.78, "收盘价": 10.0},
             {"date": "2026-09-02", PRIMARY: 987654.32, "收盘价": 10.5}]
    src = local + [{"date": "2026-09-03", PRIMARY: -555.0, "收盘价": 11.0}]
    res = merge_incremental(local, src)
    assert res["merged"] and res["appended"] == 1 and res["overlap"] == 2
    assert res["merged_rows"][-1]["date"] == "2026-09-03"
    # S4 mismatch on PRIMARY -> local untouched (tol 1.0 yuan: 987654.32 vs .33 same, vs 999.0 diff)
    src_ok = [dict(local[0]), dict(local[1])]
    src_ok[1][PRIMARY] = 987654.33
    assert merge_incremental(local, src_ok)["merged"]               # cent-level stable
    src_bad = [dict(local[0]), dict(local[1])]
    src_bad[1][PRIMARY] = 999999.99
    res2 = merge_incremental(local, src_bad)
    assert not res2["merged"] and res2["mismatch"] == "2026-09-02"
    # price col drift alone does NOT trip mismatch (provenance-only, source may re-adjust)
    src_px = [dict(local[0]), dict(local[1])]
    src_px[0]["收盘价"] = 12.34
    assert merge_incremental(local, src_px)["merged"]
    # S5 csv roundtrip with Chinese columns (utf-8 no BOM)
    rr = [{"date": "2026-09-01", PRIMARY: -123456.789, "收盘价": 10.0}]
    text = rows_to_csv_text(rr)
    assert text.splitlines()[0] == "date," + ",".join(FLOW_COLS)
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "x.csv")
        atomic_write(p, text)
        back = read_local_csv(p)
        assert back[0][PRIMARY] == -123456.789 and back[0]["收盘价"] == 10.0
        raw = io.open(p, "rb").read()
        assert not raw.startswith(b"\xef\xbb\xbf")                  # no BOM
    # S6 market derivation
    assert market_of("600519") == "sh" and market_of("688001") == "sh"
    assert market_of("000001") == "sz" and market_of("300750") == "sz"
    assert market_of("920025") is None and market_of("430047") is None
    # S7 stale_gate + trading_days_back on injected calendar
    cal = [f"2026-08-{d:02d}" for d in range(3, 29)] + ["2026-08-31"] + \
          [f"2026-09-{d:02d}" for d in range(1, 24)]
    assert trading_days_back("2026-09-23", cal, 20) == "2026-09-03"  # prior[-20]: Sep 1..22 = 20 synthetic trading days back from anchor
    needs, _ = stale_gate("2026-09-22", dt.datetime(2026, 9, 24, 7, 0), cal)
    assert not needs
    needs, why = stale_gate("2026-08-20", dt.datetime(2026, 9, 24, 7, 0), cal)
    assert needs and "stale" in why
    needs, _ = stale_gate(None, dt.datetime(2026, 9, 24, 7, 0), cal)
    assert needs                                                        # first run
    # S8 fuse + quarantine thresholds
    assert FUSE_LIMIT == 5 and QUARANTINE_AT == 3 and MAX_ROWS == 130
    # S9 progress roundtrip incl quarantine logic
    with tempfile.TemporaryDirectory() as td:
        global PROGRESS
        old = PROGRESS
        PROGRESS = os.path.join(td, "_progress.json")
        try:
            prog = load_progress()
            assert prog["done"] == set() and prog["attempts"] == {}
            prog["done"].add("000001")
            prog["attempts"]["300750"] = 2
            save_progress(prog)
            back = load_progress()
            assert back["done"] == {"000001"} and back["attempts"]["300750"] == 2
            q = {c for c, n in back["attempts"].items() if n >= QUARANTINE_AT}
            assert q == set()
            back["attempts"]["300750"] = 3
            q = {c for c, n in back["attempts"].items() if n >= QUARANTINE_AT}
            assert q == {"300750"}
        finally:
            PROGRESS = old
    # S10 lock: missing lock -> not alive; stale lock (dead pid) -> not alive
    with tempfile.TemporaryDirectory() as td:
        global LOCK
        old_lock = LOCK
        LOCK = os.path.join(td, "_refresh.lock")
        try:
            assert not _lock_alive()                                     # missing
            atomic_write(LOCK, json.dumps({"pid": 99999999, "ts": "x"}))
            assert not _lock_alive()                                    # dead pid -> stale
        finally:
            LOCK = old_lock
    # S11 universe glob on synthetic bars dir (twin dedupe + malformed skip)
    with tempfile.TemporaryDirectory() as td:
        for name in ("000001.parquet", "sh600519.parquet", "600519.parquet",
                     "sz300750.parquet", "920025.parquet", "bad_name.parquet"):
            io.open(os.path.join(td, name), "w").close()
        codes, skipped = universe_codes(td)
        assert set(codes) == {"000001", "600519", "300750", "920025"}
        assert skipped == ["bad_name"]
    # S12 expected_latest_bar_date family (futures S8 same family, injected cal)
    assert expected_latest_bar_date(dt.datetime(2026, 9, 24, 7, 0), cal) == "2026-09-23"
    assert expected_latest_bar_date(dt.datetime(2026, 9, 26, 16, 0), []) == "2026-09-25"
    # S13 conn-level classifier (quarantine-storm guard: blocks never bump attempts)
    assert _is_conn_error("ConnectionError", "('Connection aborted.', RemoteDisconnected('x'))")
    assert _is_conn_error("Exception", "HTTPSConnectionPool: MaxRetryError boom")
    assert _is_conn_error("ReadTimeout", "")
    assert not _is_conn_error("RuntimeError", "validation_fail:bad_date_format:x")
    assert not _is_conn_error("KeyError", "missing column")
    # S14 non-owner gate: stdout-only no-op, shared status mirror untouched
    # (bm-c MSG-20260924-0955: non-owner mirror rewrite = lane stomp)
    with tempfile.TemporaryDirectory() as td:
        global STATUS, _lane_owner_id
        old_status, old_owner_fn = STATUS, _lane_owner_id
        STATUS = os.path.join(td, "mf_status.json")
        _lane_owner_id = lambda: "bm-c"
        try:
            write_status({"ts": "2026-09-24T09:23:55",
                          "mode": "refresh source-blocked (connection-level)",
                          "panel": {"cutoff": None, "complete": False}})
            before = io.open(STATUS, "r", encoding="utf-8").read()
            assert gate() == 0
            after = io.open(STATUS, "r", encoding="utf-8").read()
            assert before == after, "non-owner gate must not rewrite the shared mirror"
        finally:
            STATUS, _lane_owner_id = old_status, old_owner_fn
    # S15 v2 rank window guard (ticket 09:15-15:05 mutation window + the
    # 15:05-15:30 stamp-hazard band -> net block 09:15-15:30 on trading days)
    cal2 = cal + ["2026-09-24"]
    assert not rank_pull_allowed(dt.datetime(2026, 9, 24, 10, 0), cal2)[0]   # intraday
    assert not rank_pull_allowed(dt.datetime(2026, 9, 24, 15, 20), cal2)[0]  # stamp band
    assert rank_pull_allowed(dt.datetime(2026, 9, 24, 15, 31), cal2)[0]      # post-15:30
    assert rank_pull_allowed(dt.datetime(2026, 9, 24, 8, 0), cal2)[0]        # pre-open
    assert rank_pull_allowed(dt.datetime(2026, 9, 26, 10, 0), cal2)[0]       # Saturday
    assert rank_pull_allowed(dt.datetime(2026, 9, 25, 1, 10), cal2)[0]       # night
    # S16 v2 field mapping -> FLOW_COLS zero drift; '-' / absent -> None
    item = {"f12": "600519", "f2": 1500.5, "f3": 1.23, "f62": -123456.78,
            "f184": -0.56, "f66": -100.0, "f69": -1.0, "f72": 200.0, "f75": 2.0,
            "f78": 300.0, "f81": 3.0, "f84": 400.0, "f87": 4.0}
    row = rank_row_from_item(item)
    assert set(row) == set(FLOW_COLS) and row["主力净流入-净额"] == -123456.78
    assert row["收盘价"] == 1500.5 and row["小单净流入-净占比"] == 4.0
    susp = rank_row_from_item({"f12": "000001", "f2": "-", "f62": "-"})
    assert susp["收盘价"] is None and susp["主力净流入-净额"] is None
    assert rank_row_from_item({})["涨跌幅"] is None
    # S17 v2 idempotent same-day merge (skip / mismatch / append / anomalies)
    local = [{"date": "2026-09-23", PRIMARY: -1.0e8, "收盘价": 10.0}]
    a1, _ = rank_merge_one(local, "2026-09-23", {PRIMARY: -1.0e8, "收盘价": 10.1})
    assert a1 == "skip_same_day"                                          # tol match
    a2, _ = rank_merge_one(local, "2026-09-23", {PRIMARY: 5.0e8, "收盘价": 10.2})
    assert a2 == "mismatch"                                              # value drift
    a3, p3 = rank_merge_one(local, "2026-09-24", {PRIMARY: 2.0e8, "收盘价": 10.5})
    assert a3 == "append" and len(p3) == 2 and p3[-1]["date"] == "2026-09-24"
    a4, _ = rank_merge_one([{"date": "2026-09-25", PRIMARY: 1.0}], "2026-09-24",
                          {PRIMARY: 1.0})
    assert a4 == "mismatch"                                              # stamp behind local
    a5, _ = rank_merge_one([{"date": "2026-09-23", PRIMARY: None}], "2026-09-23",
                           {PRIMARY: None})
    assert a5 == "skip_same_day"                                          # both none
    # S18 v2 rank_stale daily-forward trigger (cutoff lags 1td -> fire)
    with tempfile.TemporaryDirectory() as td:
        STATUS = os.path.join(td, "st.json")
        try:
            write_status({"rank": {"last_stamp": "2026-09-23"}})
            n1, _ = rank_stale(now=dt.datetime(2026, 9, 25, 1, 10), dates=cal)
            assert not n1                                                # covers expected
            write_status({"rank": {"last_stamp": "2026-09-22"}})
            n2, w2 = rank_stale(now=dt.datetime(2026, 9, 25, 1, 10), dates=cal)
            assert n2 and "lags" in w2
            write_status({})
            n3, _ = rank_stale(now=dt.datetime(2026, 9, 25, 1, 10), dates=cal)
            assert n3                                                    # never fired
        finally:
            STATUS = old_status
    # S19 v2 pagination (stop conditions + all-or-nothing page error)
    def fake_pages(pn):
        data = {1: [dict(f12=f"{600000 + i}") for i in range(100)],
                2: [dict(f12=f"{600100 + i}") for i in range(100)],
                3: [dict(f12=f"{600200 + i}") for i in range(50)]}
        return {"data": {"total": 250, "diff": data[pn]}}
    items, total, pages, err = fetch_rank_all_pages(fetch_page=fake_pages, sleep_s=0,
                                                    retry_sleep_s=0)
    assert err is None and total == 250 and len(items) == 250 and pages == 3
    def fake_short(pn):
        return {"data": {"total": 100, "diff": [dict(f12=f"{600000 + i}") for i in range(100)]}}
    it2, _, pg2, err2 = fetch_rank_all_pages(fetch_page=fake_short, sleep_s=0,
                                              retry_sleep_s=0)
    assert err2 is None and pg2 == 1 and len(it2) == 100                  # total-reached stop
    def fake_dead(pn):
        raise RuntimeError("RemoteDisconnected")
    _, _, _, err3 = fetch_rank_all_pages(fetch_page=fake_dead, sleep_s=0,
                                          retry_sleep_s=0)
    assert err3 and "RemoteDisconnected" in err3                          # page error -> abort
    flaky_state = {"n": 0}
    def fake_flaky(pn):
        flaky_state["n"] += 1
        if flaky_state["n"] == 1:
            raise RuntimeError("RemoteDisconnected")                        # 1st attempt drops
        return {"data": {"total": 100, "diff": [dict(f12=f"{600000 + i}") for i in range(100)]}}
    it4, _, _, err4 = fetch_rank_all_pages(fetch_page=fake_flaky, sleep_s=0,
                                            retry_sleep_s=0)
    assert err4 is None and len(it4) == 100 and flaky_state["n"] == 2     # retry recovers
    # S20 v2 universe join (rank 5920 x bars 5222 code partition)
    in_u, not_u = rank_universe_join({"600519": 1, "920025": 2}, ["600519", "000001"])
    assert in_u == ["600519"] and not_u == ["920025"]
    print("selftest: 20/20 PASS")
    return 0


def main():
    _clear_proxy_env()
    argv = [a for a in sys.argv[1:]]
    if argv and argv[0] == "selftest":
        return _selftest()
    if argv and argv[0] == "refresh":
        limit = None
        if "--limit" in argv:
            try:
                limit = int(argv[argv.index("--limit") + 1])
            except Exception:
                return 2
        return refresh(limit=limit)
    if argv and argv[0] == "rank":
        return rank_pass()
    if argv and argv[0] == "status":
        return status()
    return gate()


if __name__ == "__main__":
    sys.exit(main())
