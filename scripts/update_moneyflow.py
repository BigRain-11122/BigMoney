"""Individual-stock money-flow forward collector (R63 bm-a, claim MSG-20260924-0920).

Spec: research/shortline/MF_COLLECTOR.md (frozen before implementation).
Lane: data dept, O-1620 GM-approved money-flow domain; R58 source-audit follow-up.

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
SLEEP_S = 2.5                # EM citizenship throttle
FUSE_LIMIT = 5               # consecutive fetch failures (any kind) -> stop
CONN_STOP = 3                # consecutive connection-level failures -> source-block stop
CONN_MARKERS = ("ConnectionError", "Timeout", "RemoteDisconnected",
                "ChunkedEncodingError", "ProtocolError", "MaxRetryError")
QUARANTINE_AT = 3            # cumulative refresh failures -> skip forever
MAX_ROWS = 130               # 120td window + source slack
MIN_SPAWN_S = 30 * 60        # spawn throttle
STALE_TD = 20                # refresh trigger: panel age in trading days

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


# ---------------------------------------------------------------------- gate


def _lane_owner_id():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"),
                     "r", encoding="utf-8-sig") as f:
            return str(json.load(f).get("machine_id", ""))
    except Exception:
        return ""


def spawn_detached_refresh():
    """Silent detached refresh (zero popups); log appended, lock self-managed."""
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    with io.open(LOG, "a", encoding="utf-8") as lf:
        subprocess.Popen(
            [sys.executable, os.path.abspath(__file__), "refresh"],
            stdout=lf, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, creationflags=flags, close_fds=False)
    # child inherits lf; parent keeps running (R20 backfill precedent)


def gate():
    """S6 step: zero-network no-op when fresh; spawns detached refresh when stale."""
    st = load_status()
    now = dt.datetime.now()
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        st["ts"] = now.isoformat(timespec="seconds")
        st["mode"] = f"no-op: lane owned by {LANE_OWNER} (R31 guard, this={owner or 'unknown'})"
        write_status(st)
        print(f"no-op: moneyflow lane owned by {LANE_OWNER}, not this machine ({owner or '?'})")
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
    print("selftest: 13/13 PASS")
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
    if argv and argv[0] == "status":
        return status()
    return gate()


if __name__ == "__main__":
    sys.exit(main())
