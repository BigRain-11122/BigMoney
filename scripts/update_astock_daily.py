"""A-share per-stock daily-bar forward collector (T-2026-09-26-87 supply lane, bm-b).

Ticket/lane: fleet/tasks/T-2026-09-26-87.json progress_r279_bmb (bm-b supply
claim, opens r280); consumption = T-87 REV_OSC_STOCK_P1 stock sleeve forward
leg + O-20260926-2335 refine-furnace stock mirror. Lane owner = bm-b (R31
family); data dept supply lane.

Step-0 probe (r280, THIS machine): results/_r280bmb_probe_akshare_daily.py ->
results/_r280bmb_probe_akshare_daily.json -- ak.stock_zh_a_daily (sina, qfq)
ALIVE 4/4 incl bj face, schema = date,open,high,low,close,volume,amount,
outstanding_share,turnover; ak.stock_zh_a_hist (EM) 0/4 ConnectionError from
this machine = channel decision sina-only, EM face honest-disclosed dead.

Storage (gitignored, regenerable):
  data/astock_daily/per/<code>.csv   per-symbol daily rows (qfq face)
  data/astock_daily/_progress.json  checkpoint {attempts:{}} + bookkeeping
  data/astock_daily/_refresh.lock   {pid, ts} while refresh runs
Status (tracked): results/astock_daily_update_status.json

Semantics (update_sina_mf / update_futures family):
- frozen schema = 9 raw source fields verbatim, no renaming, no derived faces
  (R258 law: outstanding_share is a current-section ffilled proxy -- source
  stored as-is, consumers own its semantics)
- continuation todo is FILE-DERIVED (per-symbol tail date < expected latest
  complete bar date), never a done-set churn face -- the R235 defect-1/2
  family lessons taken at design time: zero-symbol rounds cannot stall,
  universe growth self-heals (missing file -> todo)
- qfq continuity law (deviation from family not-touched law, disclosed):
  overlap mismatch on close within the continuation window = corporate-action
  qfq rewrite signal -> that symbol gets a full re-pull + atomic replace
  (counted `readjusted`); a qfq panel must track the source's adjusted truth,
  freezing pre-dividend bytes would poison every downstream mark/backtest
- sanity: OHLC order (high >= max(o,c), low <= min(o,c), high >= low),
  volume/amount >= 0; rows dated today persist only after 15:30 local
  (family completeness guard, local ETF calendar primary)
- unit anchor (r262 lore-vs-cache law): amount/volume ~= close vwap face is
  MEASURED and recorded in status as a diagnostic (probe 000001:
  1186736896/104381872 = 11.36 vs close 11.3); volume = true-share face
- universe = data/fundamental/eligibility.csv 6-digit codes; market 6->sh,
  0/3->sz; B-shares (2xxxxx sz, 9xxxxx sh) + bj-nt (4/8xxxxx, 920xxx)
  honestly skipped with per-bucket counts (update_sina_mf precedent; bj
  probe-alive evidence recorded -- extension = future signed decision)
- throttle 2.5s/request; fuse = 5 consecutive fetch failures -> stop,
  checkpoint preserved; conn-level 3 consecutive -> source-block stop;
  symbol failing >= 3 cumulative refreshes quarantined
- gate (daily-forward face): panel complete AND cutoff >= expected latest
  complete bar date -> zero-network no-op; incomplete/first-pull -> spawn
  detached full-universe refresh; complete but cutoff lagging > 20td ->
  refresh-repull (all symbols); 30-min spawn throttle; lock-alive no-op
- lane guard: gate acts only on bm-b (R31); other machines stdout-only no-op

Exit codes (gate):    0 = ok/no-op/spawned/in-progress; 2 = machinery failure
Exit codes (refresh): 0 = todo exhausted (universe complete, readjustments
                          resolved); 2 = not complete (fuse/source-block/
                          failures remain -- checkpoint preserved, gate
                          self-heals after the 30-min throttle)
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

import akshare as ak

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "astock_daily")
PER_DIR = os.path.join(DATA_DIR, "per")
PROGRESS = os.path.join(DATA_DIR, "_progress.json")
LOCK = os.path.join(DATA_DIR, "_refresh.lock")
STATUS = os.path.join(ROOT, "results", "astock_daily_update_status.json")
LOG = os.path.join(ROOT, "logs", "astock_daily_refresh.log")
ELIG = os.path.join(ROOT, "data", "fundamental", "eligibility.csv")
PROBE_REF = "results/_r280bmb_probe_akshare_daily.json"

LANE_OWNER = "bm-b"          # T-87 progress_r279_bmb lane claim (R31 family)

DATE_KEY = "date"
BAR_COLS = ["open", "high", "low", "close", "volume", "amount",
            "outstanding_share", "turnover"]
PRIMARY = "close"
PRIMARY_TOL = 1e-6           # qfq prices: exact-decimal source face
WRITTEN_LAW_TOL = 1e-8        # %.10g written-face relative bound (family law)
OVERLAP_BUFFER_D = 40         # calendar days of tail overlap canary window

SLEEP_S = 2.5
FUSE_LIMIT = 5
CONN_STOP = 3
QUARANTINE_AT = 3
MIN_SPAWN_S = 30 * 60
STALE_TD = 20                 # structural-repull trigger (collector down long)
MIN_UNIVERSE = 100
COMPLETE_HOUR = dt.time(15, 30)

CONN_MARKERS = ("ConnectionError", "Timeout", "RemoteDisconnected",
                "ChunkedEncodingError", "ProtocolError", "MaxRetryError",
                "URLError", "HTTPError", "SSLError")


# ------------------------------------------------------------- calendar gates

_DATES_CACHE = None


def _load_trading_dates():
    """Local ETF trading-day calendar (update_lhb/update_futures family:
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
                rd = _csv.reader(f)
                head = next(rd, None)
                if not head:
                    continue
                di = 0
                for i, h in enumerate(head):
                    if "date" in h.lower() or "日期" in h:
                        di = i
                        break
                ds = set()
                for row in rd:
                    if len(row) > di and re.match(r"^\d{4}-\d{2}-\d{2}$", row[di].strip()[:10]):
                        ds.add(row[di].strip()[:10])
                if len(ds) >= 200:
                    dates = sorted(ds)
                    break
        except Exception:
            continue
    _DATES_CACHE = dates
    return dates


def expected_latest_bar_date(now, dates=None):
    """Latest date whose daily bar is expected COMPLETE on the local panel:
    today >= 15:30 -> today if a trading day else last trading day before;
    today < 15:30 -> last trading day strictly before today (family law)."""
    dates = dates if dates is not None else _load_trading_dates()
    t = now.date().isoformat()
    if dates:
        if now.time() >= COMPLETE_HOUR:
            return t if t in dates else max((d for d in dates if d <= t), default=None)
        return max((d for d in dates if d < t), default=None)
    # weekday approximation (no calendar file)
    d = now.date()
    if now.time() < COMPLETE_HOUR:
        d -= dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d.isoformat()


def stale_gate(panel_cutoff, now, dates=None, max_age_td=STALE_TD):
    """(needs, reason) -- panel lags the expected complete bar date."""
    dates = dates if dates is not None else _load_trading_dates()
    exp = expected_latest_bar_date(now, dates)
    if exp is None:
        return False, "no calendar anchor"
    if panel_cutoff is None:
        return True, "no panel cutoff (first pull / empty panel)"
    if panel_cutoff >= exp:
        return False, f"panel fresh (cutoff {panel_cutoff} >= expected {exp})"
    # structural-staleness check: how many trading days behind
    if dates:
        behind = [d for d in dates if panel_cutoff < d <= exp]
        if len(behind) > max_age_td:
            return True, (f"structural stale: cutoff {panel_cutoff} lags "
                          f"{len(behind)}td > {max_age_td} -> repull")
    return True, f"panel lags expected bar date ({panel_cutoff} < {exp})"


# ------------------------------------------------------- universe + markets

def market_of(code):
    """6-digit eligibility code -> sina symbol prefix. None = skipped face."""
    if re.match(r"^6\d{5}$", code):
        return "sh"
    if re.match(r"^[03]\d{5}$", code):
        return "sz"
    return None


def universe_codes(elig_path=None):
    """Pull universe + honest per-bucket skip counts (family face)."""
    elig_path = elig_path or ELIG
    codes, seen = [], set()
    buckets = {}
    with io.open(elig_path, "r", encoding="utf-8-sig") as f:
        rd = _csv.DictReader(f)
        for row in rd:
            c = str(row.get("code", "")).strip()
            if not c:
                continue
            b = c[0]
            buckets[b] = buckets.get(b, 0) + 1
            if market_of(c) and c not in seen:
                seen.add(c)
                codes.append(c)
    codes.sort()
    return codes, buckets


# ------------------------------------------------------------ fetch + parse

def fetch_one(code, market):
    """One request: full-history qfq daily bars (akshare filters client-side)."""
    df = ak.stock_zh_a_daily(symbol=f"{market}{code}", adjust="qfq")
    rows = []
    for _, r in df.iterrows():
        row = {DATE_KEY: str(r["date"])[:10]}
        for col in BAR_COLS:
            v = r.get(col)
            try:
                row[col] = None if v is None or v != v else float(v)
            except (TypeError, ValueError):
                row[col] = None
        rows.append(row)
    return rows


def completeness_filter(rows, now=None):
    """Family guard: rows dated today persist only after 15:30 local."""
    now = now or dt.datetime.now()
    if now.time() >= COMPLETE_HOUR:
        return rows, 0
    today = now.date().isoformat()
    kept = [r for r in rows if str(r[DATE_KEY]) < today]
    return kept, len(rows) - len(kept)


def validate_rows(rows):
    """OHLC sanity; return None if clean else a short defect string."""
    bad = 0
    for r in rows:
        o, h, l, c = (r.get(k) for k in ("open", "high", "low", "close"))
        v, a = r.get("volume"), r.get("amount")
        if None in (o, h, l, c):
            bad += 1
            continue
        if not (h >= max(o, c) - 1e-9 and l <= min(o, c) + 1e-9 and h >= l - 1e-9):
            bad += 1
            continue
        if (v is not None and v < 0) or (a is not None and a < 0):
            bad += 1
    if bad:
        return f"sanity_defects={bad}/{len(rows)}"
    return None


def vwap_anchor(rows, tail_n=5):
    """r262 unit anchor: |amount/volume - close|/close on the tail rows
    (suspension rows volume=0 are skipped). Diagnostic only, never a gate."""
    face = []
    for r in rows[-tail_n:]:
        v, a, c = r.get("volume"), r.get("amount"), r.get("close")
        if v and a and c:
            face.append(abs(a / v - c) / c)
    if not face:
        return None
    return round(max(face), 6)


def _overlap_tol(lv, sv, tol=PRIMARY_TOL):
    return max(tol, WRITTEN_LAW_TOL * max(abs(float(lv)), abs(float(sv))))


def merge_incremental(local_rows, source_rows, primary=PRIMARY, tol=PRIMARY_TOL):
    """Append-only merge with tail-overlap canary. Mismatch -> (merged=False,
    mismatch=date, rewrite=True hint): caller runs the qfq readjust path."""
    local_by_date = {str(r[DATE_KEY]): r for r in local_rows}
    mismatch, overlap = None, 0
    for r in source_rows:
        d = str(r[DATE_KEY])
        loc = local_by_date.get(d)
        if loc is None:
            continue
        overlap += 1
        lv, sv = loc.get(primary), r.get(primary)
        if lv is None and sv is None:
            continue
        if lv is None or sv is None or \
                abs(float(lv) - float(sv)) > _overlap_tol(lv, sv, tol):
            mismatch = d
            break
    if mismatch:
        return {"appended": 0, "overlap": overlap, "mismatch": mismatch,
                "merged": False, "merged_rows": None}
    new_rows = [r for r in source_rows if str(r[DATE_KEY]) not in local_by_date]
    merged = list(local_rows) + new_rows
    merged.sort(key=lambda r: str(r[DATE_KEY]))
    return {"appended": len(new_rows), "overlap": overlap, "mismatch": None,
            "merged": True, "merged_rows": merged}


# --------------------------------------------------------------- csv + state

def rows_to_csv_text(rows):
    buf = io.StringIO()
    w = _csv.writer(buf, lineterminator="\n")
    w.writerow([DATE_KEY] + BAR_COLS)
    for r in rows:
        out = [str(r[DATE_KEY])]
        for col in BAR_COLS:
            v = r.get(col)
            out.append("" if v is None or v != v else f"{float(v):.10g}")
        w.writerow(out)
    return buf.getvalue()


def read_local_csv(path):
    if not os.path.exists(path):
        return []
    with io.open(path, "r", encoding="utf-8") as f:
        rd = _csv.DictReader(f)
        rows = []
        for x in rd:
            r = {DATE_KEY: x[DATE_KEY]}
            for col in BAR_COLS:
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
            return {"attempts": {k: int(v) for k, v in p.get("attempts", {}).items()}}
        except Exception:
            pass
    return {"attempts": {}}


def save_progress(prog):
    atomic_write(PROGRESS, json.dumps(prog, ensure_ascii=False))


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
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                             capture_output=True, timeout=15)
        return f'"{pid}"' in out.stdout.decode("utf-8", errors="replace")
    except Exception:
        return False


def _lock_alive():
    if not os.path.exists(LOCK):
        return False
    try:
        with io.open(LOCK, "r", encoding="utf-8") as f:
            pid = int(json.load(f).get("pid", 0))
        return _pid_alive(pid)
    except Exception:
        return False


def _local_last_date(code, per_dir=None):
    """Per-symbol tail date (bytes tail-read, family pattern). None=no file."""
    p = os.path.join(per_dir or PER_DIR, code + ".csv")
    if not os.path.exists(p):
        return None
    try:
        with io.open(p, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 256))
            tail = f.read().decode("utf-8", errors="replace")
        lines = [ln for ln in tail.strip().splitlines() if ln.strip()]
        if not lines:
            return None
        d = lines[-1].split(",", 1)[0]
        return d if re.match(r"^\d{4}-\d{2}-\d{2}$", d) else None
    except Exception:
        return None


def _panel_cutoff_from_bytes(per_dir=None):
    per_dir = per_dir or PER_DIR
    best = None
    for p in _glob.glob(os.path.join(per_dir, "*.csv")):
        d = _local_last_date(os.path.splitext(os.path.basename(p))[0], per_dir)
        if d and (best is None or d > best):
            best = d
    return best


def _is_conn_error(ename, emsg=""):
    return any(m in ename or m in str(emsg)[:200] for m in CONN_MARKERS)


def _todo_for(codes, expected_cutoff, repull=False, quarantine=None):
    """File-derived todo (design note in header): repull -> all
    non-quarantined; continuation -> symbols whose tail date lags the
    expected complete bar date (missing file counts as lagging)."""
    quarantine = quarantine or set()
    if repull:
        return [c for c in codes if c not in quarantine]
    if expected_cutoff is None:
        return [c for c in codes if c not in quarantine]
    return [c for c in codes
            if c not in quarantine and (_local_last_date(c) or "") < expected_cutoff]


# ------------------------------------------------------------------ refresh

def refresh(limit=None, repull=False):
    """Long-running full-universe pull. Checkpointed + fused; detached-safe."""
    codes, buckets = universe_codes()
    if len(codes) < MIN_UNIVERSE:
        print(f"universe unavailable ({len(codes)} codes from {ELIG}) -- "
              f"refusing honest exit 2")
        return 2
    _write_lock()
    try:
        prog = load_progress()
        quarantine = {c for c, n in prog["attempts"].items() if n >= QUARANTINE_AT}
        expected = expected_latest_bar_date(dt.datetime.now())
        todo = _todo_for(codes, expected, repull=repull, quarantine=quarantine)
        if limit is not None:
            todo = todo[:int(limit)]
        now0 = dt.datetime.now()
        st = load_status()
        st.update({
            "ts": now0.isoformat(timespec="seconds"),
            "mode": (f"refresh in progress (todo={len(todo)}/{len(codes)}, "
                     f"quarantined={len(quarantine)}"
                     + (", repull=all-symbols" if repull else "") + ")"),
            "panel": dict(st.get("panel") or {}, complete=False,
                          universe_n=len(codes)),
            "claim": "T-2026-09-26-87-bm-b-astock-daily-collector",
            "probe_ref": PROBE_REF,
        })
        st.setdefault("universe_skip_buckets", buckets)
        write_status(st)

        consec_fail, consec_conn = 0, 0
        appended_total = readjusted_n = fetched_n = 0
        failures, readjusted = [], []
        conn_stopped = False
        panel_cutoff = None
        vwap_faces = []
        t_start = time.time()
        for i, code in enumerate(todo):
            try:
                rows = fetch_one(code, market_of(code))
                fetched_n += 1
                rows, _dropped_today = completeness_filter(rows)
                err = validate_rows(rows)
                if err:
                    raise RuntimeError(f"validation_fail:{err}")
                face = vwap_anchor(rows)
                if face is not None:
                    vwap_faces.append(face)
                p = os.path.join(PER_DIR, code + ".csv")
                local = read_local_csv(p)
                res = merge_incremental(local, rows)
                if not res["merged"]:
                    # qfq corporate-action rewrite: full re-pull + replace
                    full = fetch_one(code, market_of(code))
                    full, _ = completeness_filter(full)
                    err2 = validate_rows(full)
                    if err2:
                        raise RuntimeError(f"readjust_validation_fail:{err2}")
                    atomic_write(p, rows_to_csv_text(full))
                    readjusted_n += 1
                    readjusted.append(f"{code}@{res['mismatch']}")
                    last = str(full[-1][DATE_KEY]) if full else None
                else:
                    atomic_write(p, rows_to_csv_text(res["merged_rows"]))
                    appended_total += res["appended"]
                    last = (str(res["merged_rows"][-1][DATE_KEY])
                            if res["merged_rows"] else None)
                if last and (panel_cutoff is None or last > panel_cutoff):
                    panel_cutoff = last
                prog["attempts"].pop(code, None)
                consec_fail = 0
                consec_conn = 0
            except Exception as e:
                ename, emsg = type(e).__name__, str(e)
                if _is_conn_error(ename, emsg):
                    consec_conn += 1
                    failures.append(f"{code}:conn:{ename}")
                    if consec_conn >= CONN_STOP:
                        conn_stopped = True
                        print(f"source-level block suspected ({consec_conn} "
                              f"consecutive connection failures) -- stopping, "
                              f"checkpoint intact, gate retries after throttle")
                        break
                else:
                    consec_fail += 1
                    prog["attempts"][code] = prog["attempts"].get(code, 0) + 1
                    failures.append(f"{code}:{ename}:{emsg[:80]}")
                    if consec_fail >= FUSE_LIMIT:
                        print(f"fuse: {consec_fail} consecutive fetch failures "
                              f"-- stopping, checkpoint intact")
                        break
            if (i + 1) % 50 == 0:
                save_progress(prog)
                print(f"  [{i + 1}/{len(todo)}] appended={appended_total} "
                      f"readjusted={readjusted_n} fails={len(failures)} "
                      f"elapsed={(time.time() - t_start) / 60:.1f}min",
                      flush=True)
            time.sleep(SLEEP_S)

        save_progress(prog)
        quarantine = {c for c, n in prog["attempts"].items() if n >= QUARANTINE_AT}
        remaining = _todo_for(codes, expected, repull=False,
                              quarantine=quarantine)
        complete = (not conn_stopped and not remaining
                    and not [f for f in failures if ":conn:" not in f]) \
            if not repull else (not conn_stopped and not remaining)
        cutoff = panel_cutoff or _panel_cutoff_from_bytes()
        st.update({
            "ts": dt.datetime.now().isoformat(timespec="seconds"),
            "mode": ("refresh complete" if complete
                     else "refresh incomplete (checkpoint preserved)"),
            "panel": {"complete": bool(complete), "cutoff": cutoff,
                      "universe_n": len(codes),
                      "per_files": len(_glob.glob(os.path.join(PER_DIR, "*.csv")))},
            "last_refresh": {"todo": len(todo), "fetched": fetched_n,
                             "appended": appended_total,
                             "readjusted": readjusted_n,
                             "readjusted_tail": readjusted[-8:],
                             "failures_tail": failures[-12:],
                             "failures_n": len(failures),
                             "conn_stopped": bool(conn_stopped),
                             "elapsed_min": round((time.time() - t_start) / 60, 1),
                             "vwap_anchor_max": (max(vwap_faces) if vwap_faces
                                                 else None),
                             "repull": bool(repull)},
            "quarantined_n": len(quarantine),
        })
        write_status(st)
        print(f"refresh done: todo={len(todo)} fetched={fetched_n} "
              f"appended={appended_total} readjusted={readjusted_n} "
              f"failures={len(failures)} complete={complete} "
              f"cutoff={cutoff}")
        return 0 if complete else 2
    finally:
        _clear_lock()


# -------------------------------------------------------------------- gate

def _lane_owner_id():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"),
                     "r", encoding="utf-8-sig") as f:
            return str(json.load(f).get("machine_id", ""))
    except Exception:
        return ""


def spawn_detached(arg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    with io.open(LOG, "a", encoding="utf-8") as lf:
        subprocess.Popen([sys.executable, os.path.abspath(__file__), arg],
                         stdout=lf, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, creationflags=flags,
                         close_fds=False)


def gate():
    """S6 step: freshness verdict -> detached spawn (daily-forward face)."""
    st = load_status()
    now = dt.datetime.now()
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        print(f"no-op: astock_daily lane owned by {LANE_OWNER}, "
              f"not this machine ({owner or '?'})")
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
    last = st.get("last_spawn_attempt")
    if last:
        try:
            age = (now - dt.datetime.fromisoformat(last)).total_seconds()
            if age < MIN_SPAWN_S:
                print(f"throttle: last spawn {last} "
                      f"({age / 60:.1f}min ago) < 30min -> no-op")
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
    repull = "structural stale" in reason
    st["last_spawn_attempt"] = now.isoformat(timespec="seconds")
    st["mode"] = "spawn: detached refresh"
    st["spawn_reason"] = reason
    st["spawn_mode"] = "re-pull (all symbols)" if repull else "continuation/first-pull"
    write_status(st)
    spawn_detached("refresh-repull" if repull else "refresh")
    print(f"spawned detached refresh: {reason} "
          f"(mode={'re-pull' if repull else 'continuation/first-pull'})")
    return 0


def status_cmd():
    st = load_status()
    print(json.dumps(st, ensure_ascii=False, indent=2)[:3000])
    return 0


# ----------------------------------------------------------------- selftest

def _selftest():
    import tempfile
    now = dt.datetime(2026, 9, 26, 10, 0)   # Saturday: expected bar 09-24
    # calendar gates
    dates = ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24"]
    assert expected_latest_bar_date(dt.datetime(2026, 9, 25, 9, 0), dates) == "2026-09-24"
    assert expected_latest_bar_date(dt.datetime(2026, 9, 25, 16, 0), dates) == "2026-09-24"
    exp = expected_latest_bar_date(now, dates)
    assert exp == "2026-09-24", exp
    needs, reason = stale_gate("2026-09-24", now, dates)
    assert not needs, reason
    needs, _ = stale_gate("2026-09-22", now, dates)
    assert needs and "lags" in reason or "lags" in _, _
    # structural-stale fixture must span > STALE_TD trading days (r263 law:
    # fixture periods must clear family thresholds)
    long_dates = [(dt.date(2026, 8, 1) + dt.timedelta(days=k)).isoformat()
                  for k in range(0, 40)]
    long_dates = [d for d in long_dates
                  if dt.date.fromisoformat(d).weekday() < 5]
    needs, reason2 = stale_gate("2026-08-01", dt.datetime(2026, 9, 26, 10, 0),
                               long_dates)
    assert needs and "structural stale" in reason2, reason2
    needs, _ = stale_gate(None, now, dates)
    assert needs and "first pull" in _
    # completeness guard (family S1)
    rows = [{DATE_KEY: "2026-09-24", PRIMARY: 1.0},
            {DATE_KEY: "2026-09-25", PRIMARY: 2.0}]
    kept, dropped = completeness_filter(rows, now=dt.datetime(2026, 9, 25, 9, 0))
    assert len(kept) == 1 and dropped == 1
    kept, dropped = completeness_filter(rows, now=dt.datetime(2026, 9, 25, 15, 31))
    assert len(kept) == 2 and dropped == 0
    # market derivation + skip buckets
    assert market_of("600519") == "sh"
    assert market_of("688111") == "sh"
    assert market_of("000001") == "sz"
    assert market_of("300750") == "sz"
    assert market_of("301111") == "sz"
    assert market_of("200002") is None      # sz B-share skipped
    assert market_of("900901") is None       # sh B-share skipped
    assert market_of("920000") is None       # bj-nt skipped
    assert market_of("830001") is None
    assert market_of("430001") is None
    assert market_of("12345") is None       # malformed
    # validate: OHLC sanity
    good = [{DATE_KEY: "2026-09-24", "open": 10.0, "high": 11.0, "low": 9.5,
             "close": 10.5, "volume": 100.0, "amount": 1050.0,
             "outstanding_share": 1e9, "turnover": 1e-7}]
    assert validate_rows(good) is None
    bad = [dict(good[0], high=9.0)]        # high < close
    assert validate_rows(bad) is not None
    bad = [dict(good[0], volume=-1.0)]
    assert validate_rows(bad) is not None
    # vwap anchor (r262 unit-anchor diagnostic)
    assert abs(vwap_anchor(good) - abs(1050.0 / 100.0 - 10.5) / 10.5) < 1e-12
    assert vwap_anchor([dict(good[0], volume=0.0, amount=0.0)]) is None
    # merge: append-only
    local = [{DATE_KEY: "2026-09-23", PRIMARY: 10.0},
             {DATE_KEY: "2026-09-24", PRIMARY: 11.0}]
    src = [{DATE_KEY: "2026-09-24", PRIMARY: 11.0},
           {DATE_KEY: "2026-09-25", PRIMARY: 12.0}]
    res = merge_incremental(local, src)
    assert res["merged"] and res["appended"] == 1 and res["overlap"] == 1
    # merge: qfq rewrite -> mismatch -> caller readjust path
    src2 = [{DATE_KEY: "2026-09-24", PRIMARY: 10.95},   # dividend shift
            {DATE_KEY: "2026-09-25", PRIMARY: 12.0}]
    res2 = merge_incremental(local, src2)
    assert (not res2["merged"]) and res2["mismatch"] == "2026-09-24"
    # csv roundtrip + written-face tolerance
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "000001.csv")
        atomic_write(p, rows_to_csv_text(src))
        back = read_local_csv(p)
        assert [r[DATE_KEY] for r in back] == ["2026-09-24", "2026-09-25"]
        assert abs(back[0][PRIMARY] - 11.0) < 1e-12
    # panel cutoff from bytes (family defect-1 fixture shape, isolated dir:
    # the roundtrip file above carries 09-25 and must not pollute the max)
    with tempfile.TemporaryDirectory() as td:
        atomic_write(os.path.join(td, "600519.csv"),
                     rows_to_csv_text([{DATE_KEY: "2026-09-20", PRIMARY: 1.0},
                                       {DATE_KEY: "2026-09-24", PRIMARY: 2.0}]))
        atomic_write(os.path.join(td, "000002.csv"),
                     rows_to_csv_text([{DATE_KEY: "2026-09-22", PRIMARY: 3.0}]))
        atomic_write(os.path.join(td, "badtail.csv"), "date,close\njunk\n")
        atomic_write(os.path.join(td, "headeronly.csv"), "date,close\n")
        io.open(os.path.join(td, "_progress.json"), "w",
                encoding="utf-8").write("{}")
        assert _panel_cutoff_from_bytes(td) == "2026-09-24"
        assert _local_last_date("nonexistent") is None
    # todo: file-derived continuation
    with tempfile.TemporaryDirectory() as td:
        global PER_DIR
        orig = PER_DIR
        PER_DIR = td
        try:
            atomic_write(os.path.join(td, "600519.csv"),
                         rows_to_csv_text([{DATE_KEY: "2026-09-24", PRIMARY: 1.0}]))
            atomic_write(os.path.join(td, "000001.csv"),
                         rows_to_csv_text([{DATE_KEY: "2026-09-22", PRIMARY: 1.0}]))
            todo = _todo_for(["600519", "000001", "300750"], "2026-09-24")
            assert todo == ["000001", "300750"], todo
            todo = _todo_for(["600519", "000001"], "2026-09-24",
                             quarantine={"000001"})
            assert todo == [], todo
            todo = _todo_for(["600519", "000001"], "2026-09-24", repull=True)
            assert todo == ["600519", "000001"]
            todo = _todo_for(["600519"], None)
            assert todo == ["600519"]
        finally:
            PER_DIR = orig
    # progress roundtrip
    with tempfile.TemporaryDirectory() as td:
        global PROGRESS
        orig = PROGRESS
        PROGRESS = os.path.join(td, "_progress.json")
        try:
            save_progress({"attempts": {"300750": 2}})
            assert load_progress() == {"attempts": {"300750": 2}}
        finally:
            PROGRESS = orig
    print("selftest: all guard cases PASS")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "gate"
    if cmd == "gate":
        return gate()
    if cmd == "refresh":
        limit = argv[2] if len(argv) > 2 else None
        return refresh(limit=limit)
    if cmd == "refresh-repull":
        return refresh(limit=None, repull=True)
    if cmd == "status":
        return status_cmd()
    if cmd == "selftest":
        return _selftest()
    print(f"unknown subcommand: {cmd} (gate|refresh|status|selftest)")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
