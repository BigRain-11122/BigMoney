"""sina per-stock four-tier moneyflow backfill collector (T-2026-09-26-72, R217 bm-a).

Spec (FROZEN at ticket claim commit 5a14ff38): research/shortline/SINA_MF_PREREG.md
Lane: data dept, moneyflow-family R31 lane extension (bm-a only), T-43 collector
precedent flow. Probe bloodline: R215/R216 (T-71 closed) -- endpoint ALIVE 6/6,
four-tier decomposition self-consistency law exact (worst 4.77e-07), freshness
FRESH through 2026-09-24 via date-sorted unmasked dual-stock reads.

Positioning (prereg section-3): BACKFILL / gap-repair face for cross-source
redundancy -- NOT a daily forward face. Rolling <=100td source window per stock;
the refresh gate fires when the panel cutoff lags the latest complete bar date
by more than STALE_TD (20) trading days or the first pull never completed.
Monthly-level full-universe re-pull 5222 x 2.5s ~= 3.6h (not daily).

Storage (gitignored, regenerable inside the source window):
  data/sina_mf/per/<code>.csv     append-only per-symbol daily rows
  data/sina_mf/_progress.json    checkpoint {done:[], attempts:{}}
  data/sina_mf/_refresh.lock     {pid, ts} while refresh runs
Status (tracked): results/sina_mf_update_status.json

Semantics (update_futures / update_moneyflow family):
- frozen schema = 14 raw-ASCII source fields, opendate is the date key (no
  renaming, no EM-semantics mapping -- R118 law: sina tiers are an independent
  dimension, stored independently, never mapped onto EM main-force semantics)
- self-collapse law per row: netamount == r0_net+r1_net+r2_net+r3_net within
  COLLAPSE_TOL; violating rows are REJECTED (not booked) and counted honestly;
  rows with netamount but any missing tier_net cannot verify -> conservative
  rejection (no fabrication), counted separately as unverifiable
- append-only; overlap verified on PRIMARY (netamount, tol 1.0 yuan); mismatch
  -> that symbol's local file NOT touched, counted (final refresh exit 3 face)
- completeness guard: rows dated today only persist after 15:30 local
  (local ETF trading calendar primary via data/daily/510300.csv, weekday
  fallback -- update_lhb/update_futures precedent)
- universe = data/fundamental/eligibility.csv 6-digit codes, market derived
  6->sh / 0|3->sz; other prefixes (83/87/43/92 bj-nt family) honestly skipped
  with per-bucket counts; zero-network universe source
- throttle 2.5s/request; fuse = 5 consecutive fetch failures -> stop with
  checkpoint preserved; conn-level 3 consecutive connection failures ->
  source-block stop (checkpoint preserved, gate self-heals after the 30-min
  spawn throttle); a symbol failing >= 3 cumulative refreshes is quarantined
- lane ownership guard (R31 precedent): the auto-gate only acts on bm-a
  (fleet/machine.json machine_id); other machines no-op honestly

Exit codes (gate):     0 = ok/no-op/spawned/in-progress; 2 = machinery failure
Exit codes (refresh):  0 = universe complete, mismatch-free;
                       2 = not complete (fuse/source-block/failures remain --
                           checkpoint preserved, gate self-heals);
                       3 = complete but overlap mismatches occurred
"""
from __future__ import annotations

import ast
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
DATA_DIR = os.path.join(ROOT, "data", "sina_mf")
PER_DIR = os.path.join(DATA_DIR, "per")
PROGRESS = os.path.join(DATA_DIR, "_progress.json")
LOCK = os.path.join(DATA_DIR, "_refresh.lock")
STATUS = os.path.join(ROOT, "results", "sina_mf_update_status.json")
LOG = os.path.join(ROOT, "logs", "sina_mf_refresh.log")
ELIG = os.path.join(ROOT, "data", "fundamental", "eligibility.csv")

LANE_OWNER = "bm-a"          # R31 lane-ownership precedent
BASE_URL = ("https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
            "MoneyFlow.ssl_qsfx_lscjfb")
QUERY = "page=1&num=100&sort=opendate&asc=0&fenlei=1&daima={daima}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
           "Referer": "https://finance.sina.com.cn/"}

# frozen schema (prereg section-1): date key + 13 value cols, raw ASCII
DATE_KEY = "opendate"
FLOW_COLS = ["trade", "changeratio", "turnover", "netamount", "ratioamount",
             "r0", "r1", "r2", "r3", "r0_net", "r1_net", "r2_net", "r3_net"]
TIER_NETS = ["r0_net", "r1_net", "r2_net", "r3_net"]
PRIMARY = "netamount"
PRIMARY_TOL = 1.0             # yuan-level stability tolerance (family precedent)
COLLAPSE_TOL = 1e-3            # self-collapse law tolerance (probe worst 4.77e-07)

SLEEP_S = 2.5                  # polite pace (family citizenship precedent)
FUSE_LIMIT = 5                 # consecutive fetch failures -> stop
CONN_STOP = 3                   # consecutive connection-level failures -> stop
CONN_MARKERS = ("ConnectionError", "Timeout", "RemoteDisconnected",
                "ChunkedEncodingError", "ProtocolError", "MaxRetryError",
                "URLError", "HTTPError")
QUARANTINE_AT = 3               # cumulative refresh failures -> skip forever
MAX_ROWS = 110                  # num=100 source window + slack
MIN_SPAWN_S = 30 * 60           # spawn throttle (gate self-heal window)
STALE_TD = 20                   # backfill trigger: panel age in trading days
BODY_CAP = 400_000              # bytes read cap (100 rows ~ 20KB, generous)


def _clear_proxy_env():
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)


def _no_proxy_opener():
    # registry proxies defeat env clearing alone (digest T4 recipe) --
    # ProxyHandler({}) is the only reliable direct-connection face
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
        return False, f"panel cutoff {panel_cutoff} covers complete-bar date {expected}"
    required = trading_days_back(expected, dates, max_age_td)
    if required is None:
        required = (dt.date.fromisoformat(expected)
                    - dt.timedelta(days=28)).isoformat()  # degenerate approx
    if str(panel_cutoff) >= required:
        return False, (f"panel cutoff {panel_cutoff} within {max_age_td} trading "
                       f"days of {expected} (rolling 100td window keeps it gapless)")
    return True, f"panel cutoff {panel_cutoff} older than {required} (stale)"


def completeness_filter(rows, now=None):
    """Drop trailing rows dated today when now < 15:30 (live intraday partial)."""
    now = now or dt.datetime.now()
    if now.time() >= COMPLETE_HOUR or not rows:
        return rows, 0
    today = now.date().isoformat()
    kept, dropped = list(rows), 0
    while kept and str(kept[-1].get(DATE_KEY, "")) == today:
        kept.pop()
        dropped += 1
    return kept, dropped


# ---------------------------------------------------------- universe (pure)


def market_of(code):
    if code.startswith("6"):
        return "sh"
    if code.startswith("0") or code.startswith("3"):
        return "sz"
    return None  # bj/nt/b-share family -> honest skip


def universe_codes(elig_path=None):
    """(codes, skipped, skipped_buckets) from the eligibility snapshot;
    market derivation 6->sh, 0/3->sz, everything else honestly skipped."""
    elig_path = elig_path or ELIG
    codes, buckets = [], {}
    try:
        with io.open(elig_path, "r", encoding="utf-8") as f:
            for x in _csv.DictReader(f):
                code = str(x.get("code") or "").strip()
                if not re.match(r"^\d{6}$", code):
                    continue
                if market_of(code) is None:
                    k = code[:2]
                    buckets[k] = buckets.get(k, 0) + 1
                    continue
                codes.append(code)
    except FileNotFoundError:
        return [], [], {}
    return sorted(set(codes)), sorted(buckets), buckets


# ------------------------------------------------------------------- parse


def _parse_body(text):
    """Source body -> list of dicts (json_v2.php serves python-literal JSON).
    Pure function (selftest feeds canned probe payloads)."""
    text = (text or "").strip()
    if not text.startswith("["):
        # {"__ERROR":1,"__ERRORMSG":"Input error"} face and friends
        return None
    try:
        rows = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return None
    return rows if isinstance(rows, list) else None


def _num(v):
    try:
        return None if v in (None, "", "-") else float(v)
    except (TypeError, ValueError):
        return None


def collapse_ok(row):
    """(ok, why). Self-collapse law: netamount == sum(r0_net..r3_net).
    Missing tier while netamount present -> unverifiable -> conservative
    reject (anti-fabrication; probe evidence: full values always served)."""
    net = row.get(PRIMARY)
    if net is None:
        return False, "netamount_missing"
    tiers = [row.get(k) for k in TIER_NETS]
    if any(t is None for t in tiers):
        return False, "tier_missing_unverifiable"
    s = sum(tiers)
    if abs(net - s) > COLLAPSE_TOL:
        return False, f"law_violation:{net - s:.6g}"
    return True, ""


def rows_from_source(rows_raw):
    """Raw dicts -> (clean rows asc-by-date, n_rejected). Date-format gate +
    self-collapse law row-level rejection (prereg section-2/4: violating rows
    are NOT booked, counted honestly)."""
    clean, rejected = [], 0
    for x in rows_raw or []:
        d = str(x.get(DATE_KEY, ""))[:10]
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            rejected += 1
            continue
        r = {DATE_KEY: d}
        for col in FLOW_COLS:
            r[col] = _num(x.get(col))
        ok, _why = collapse_ok(r)
        if not ok:
            rejected += 1
            continue
        clean.append(r)
    clean.sort(key=lambda r: r[DATE_KEY])
    seen, out = set(), []
    for r in clean:                      # dedupe by date (source safety)
        if r[DATE_KEY] in seen:
            continue
        seen.add(r[DATE_KEY])
        out.append(r)
    return out, rejected


def fetch_one(code, market):
    """Rolling-<=100td rows for one stock (direct urllib, probe recipe)."""
    url = BASE_URL + "?" + QUERY.format(daima=market + code)
    req = urllib.request.Request(url, headers=HEADERS)
    with _no_proxy_opener().open(req, timeout=15) as resp:
        body = resp.read(BODY_CAP).decode("utf-8", errors="replace")
    raw = _parse_body(body)
    if raw is None:
        raise RuntimeError(f"parse_fail_head:{body[:80]!r}")
    return rows_from_source(raw)


# ---------------------------------------------------------- validate + merge


def validate_rows(rows):
    """Dates ISO/strictly-increasing/unique; primary present & finite;
    row cap. Returns error str or None."""
    prev = None
    saw_primary = False
    for r in rows:
        d = str(r.get(DATE_KEY, ""))
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
    """Append-only merge; overlap compared on `primary` only (other cols are
    provenance, source may re-adjust them). Mismatch -> merged=False."""
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
        if lv is None or sv is None or abs(float(lv) - float(sv)) > tol:
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


# --------------------------------------------------------------- csv + status


def rows_to_csv_text(rows):
    buf = io.StringIO()
    w = _csv.writer(buf, lineterminator="\n")
    w.writerow([DATE_KEY] + FLOW_COLS)
    for r in rows:
        out = [str(r[DATE_KEY])]
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
            r = {DATE_KEY: x[DATE_KEY]}
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


# -------------------------------------------------------------------- locks


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


# ------------------------------------------------------------------ refresh


def _is_conn_error(ename, emsg=""):
    """Source-level (connection) failure classifier -- quarantine-storm guard."""
    return any(m in ename or m in str(emsg)[:200] for m in CONN_MARKERS)


def refresh(limit=None):
    """Long-running full-universe pull. Checkpointed + fused; detached-safe."""
    codes, skipped, buckets = universe_codes()
    if len(codes) < 100:
        print(f"universe unavailable ({len(codes)} codes from {ELIG}) -- "
              f"refusing honest exit 2")
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
            "mode": (f"refresh in progress (todo={len(todo)}/{len(codes)}, "
                     f"done={len(prog['done'])}, quarantined={len(quarantined)})"),
            "panel": dict(st.get("panel") or {},
                          complete=False, universe_n=len(codes)),
            "claim": "T-2026-09-26-72-bm-a-sina-mf-collector",
        })
        write_status(st)

        consec_fail, consec_conn = 0, 0
        appended_total = rejected_total = 0
        failures, mismatches = [], []
        conn_stopped = False
        panel_cutoff = None
        t_start = time.time()
        for i, code in enumerate(todo):
            try:
                rows, rejected = fetch_one(code, market_of(code))
                rejected_total += rejected
                rows, _dropped_today = completeness_filter(rows)
                err = validate_rows(rows)
                if err:
                    raise RuntimeError(f"validation_fail:{err}")
                p = os.path.join(PER_DIR, code + ".csv")
                local = read_local_csv(p)
                res = merge_incremental(local, rows)
                if not res["merged"]:
                    mismatches.append(f"{code}@{res['mismatch']}")
                    last = str(local[-1][DATE_KEY]) if local else None
                else:
                    atomic_write(p, rows_to_csv_text(res["merged_rows"]))
                    appended_total += res["appended"]
                    last = (str(res["merged_rows"][-1][DATE_KEY])
                            if res["merged_rows"] else None)
                if last and (panel_cutoff is None or last > panel_cutoff):
                    panel_cutoff = last
                prog["done"].add(code)
                prog["attempts"].pop(code, None)
                consec_fail = 0
                consec_conn = 0
            except Exception as e:
                ename, emsg = type(e).__name__, str(e)
                if _is_conn_error(ename, emsg):
                    # source-level block: do NOT bump per-symbol attempts
                    # (quarantine-storm guard); stop fast so the 30-min gate
                    # retry costs only CONN_STOP requests.
                    consec_conn += 1
                    failures.append(f"{code}:conn:{ename}")
                    if consec_conn >= CONN_STOP:
                        conn_stopped = True
                        print(f"source-level block suspected ({consec_conn} "
                              f"consecutive connection failures) -- stopping, "
                              f"checkpoint intact, gate retries after throttle")
                        break
                else:
                    prog["attempts"][code] = prog["attempts"].get(code, 0) + 1
                    failures.append(f"{code}:{ename}:{emsg[:120]}")
                consec_fail += 1
            save_progress(prog)
            if consec_fail >= FUSE_LIMIT:
                print(f"FUSE tripped after {i + 1} symbols ({FUSE_LIMIT} "
                      f"consecutive failures) -- checkpoint preserved, gate resumes")
                break
            if i % 250 == 0 and i:
                print(f"progress {i}/{len(todo)} (+{appended_total} rows, "
                      f"{rejected_total} law-rejected)")
            if i < len(todo) - 1:
                time.sleep(SLEEP_S)

        n_symbols = len(_glob.glob(os.path.join(PER_DIR, "*.csv")))
        fuse_stopped = consec_fail >= FUSE_LIMIT
        stopped_early = fuse_stopped or conn_stopped
        complete = ((not stopped_early)
                    and (len(prog["done"]) + len(
                        {c for c, n in prog["attempts"].items()
                         if n >= QUARANTINE_AT}) >= len(codes))
                    and (limit is None))
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
                "law_rejected_rows": rejected_total,
                "failures": len(failures),
                "failure_head": failures[:5],
                "mismatches": mismatches[:10],
                "n_mismatches": len(mismatches),
                "quarantined": sorted(
                    c for c, n in prog["attempts"].items()
                    if n >= QUARANTINE_AT)[:20],
                "universe_skipped": len(skipped),
                "universe_skipped_buckets": dict(buckets),
                "fuse_stopped": fuse_stopped,
                "conn_stopped": conn_stopped,
            },
        })
        write_status(st)
        print(f"refresh done: +{appended_total} rows, {rejected_total} law-rejected, "
              f"{len(failures)} failures, {len(mismatches)} mismatches, "
              f"complete={complete}, panel cutoff={panel_cutoff}")
        if mismatches and complete:
            return 3
        if fuse_stopped or conn_stopped or not complete:
            return 2          # honest: not complete (failures/block remain)
        return 0
    finally:
        _clear_lock()


# ----------------------------------------------------------------- gate


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


def gate():
    """S6 step: freshness verdict -> detached spawn (backfill face, 20td)."""
    st = load_status()
    now = dt.datetime.now()
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        # R31 lane guard, hardened per bm-c MSG-20260924-0955: non-owner
        # machines must NEVER touch the shared status mirror. stdout-only.
        print(f"no-op: sina_mf lane owned by {LANE_OWNER}, "
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
    # needs refresh: spawn throttle (mirror written BEFORE acting, r18 lesson)
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
    st["last_spawn_attempt"] = now.isoformat(timespec="seconds")
    st["mode"] = "spawn: detached refresh"
    st["spawn_reason"] = reason
    write_status(st)
    spawn_detached("refresh")
    print(f"spawned detached refresh: {reason}")
    return 0


def status_cmd():
    st = load_status()
    print(json.dumps(st, ensure_ascii=False, indent=2)[:3000])
    return 0


# ---------------------------------------------------------------- selftest


def _selftest():
    import tempfile
    now = dt.datetime(2026, 9, 24, 10, 0)
    today = "2026-09-24"
    # S1 completeness guard (family S1)
    rows = [{DATE_KEY: "2026-09-22", PRIMARY: 1.0}, {DATE_KEY: today, PRIMARY: 2.0}]
    kept, dropped = completeness_filter(rows, now=now)
    assert len(kept) == 1 and dropped == 1 and kept[0][DATE_KEY] == "2026-09-22"
    kept, dropped = completeness_filter(rows, now=dt.datetime(2026, 9, 24, 15, 31))
    assert len(kept) == 2 and dropped == 0
    # S2 parse: canned probe payload (R216 recipe output face; law-consistent)
    canned = ("[{'opendate':'2026-09-24','trade':'1437.8000','changeratio':'0.086206',"
              "'turnover':'149.673','netamount':'6300406547.3600','ratioamount':'0.242293',"
              "'r0':'25744545280.1600','r1':'254844431.6200','r2':'3975146.0000',"
              "'r3':'0.0000','r0_net':'6333174648.9000','r1_net':'-32905597.5400',"
              "'r2_net':'137496.0000','r3_net':'0.0000'},"
              "{'opendate':'2026-09-23','trade':'1400.1000','changeratio':'0.010000',"
              "'turnover':'120.500','netamount':'1000.0000','ratioamount':'0.100000',"
              "'r0':'2000.0','r1':'500.0','r2':'100.0','r3':'0.0',"
              "'r0_net':'800.0','r1_net':'150.0','r2_net':'50.0','r3_net':'0.0'}]")
    raw = _parse_body(canned)
    assert raw is not None and len(raw) == 2
    clean, rejected = rows_from_source(raw)
    assert rejected == 0 and len(clean) == 2
    assert clean[0][DATE_KEY] == "2026-09-23" and clean[1][DATE_KEY] == today
    # error face (list/rank absent daima) is NOT parseable as rows
    assert _parse_body('{"__ERROR":1,"__ERRORMSG":"Input error"}') is None
    # S3 self-collapse law: violation row rejected, clean rows kept
    bad = [dict(raw[0]),
           {"opendate": "2026-09-22", "trade": "1", "changeratio": "0",
            "turnover": "1", "netamount": "999.0", "ratioamount": "0",
            "r0": "1", "r1": "1", "r2": "1", "r3": "1",
            "r0_net": "1.0", "r1_net": "1.0", "r2_net": "1.0", "r3_net": "1.0"}]
    clean2, rejected2 = rows_from_source(bad)
    assert rejected2 == 1 and len(clean2) == 1      # only the law-violator dropped
    # missing-tier conservative reject (unverifiable -> not booked)
    miss = [{"opendate": "2026-09-22", "trade": "1", "changeratio": "0",
             "turnover": "1", "netamount": "10.0", "ratioamount": "0",
             "r0": "1", "r1": "1", "r2": "1", "r3": "1",
             "r0_net": "1.0", "r1_net": "1.0", "r2_net": "1.0", "r3_net": ""}]
    clean3, rejected3 = rows_from_source(miss)
    assert rejected3 == 1 and clean3 == []
    # S4 validation gate
    good = [{DATE_KEY: "2026-09-01", PRIMARY: -1.0e8},
            {DATE_KEY: "2026-09-02", PRIMARY: 2.5e8}]
    assert validate_rows(good) is None
    assert validate_rows([{DATE_KEY: "2026-09-02", PRIMARY: 1.0},
                          {DATE_KEY: "2026-09-01", PRIMARY: 1.0}]) is not None
    assert validate_rows([{DATE_KEY: "bad", PRIMARY: 1.0}]) is not None
    assert validate_rows([{DATE_KEY: "2026-09-01", PRIMARY: None}]) is not None
    assert validate_rows([{DATE_KEY: f"2026-09-{d:02d}", PRIMARY: float(d)}
                          for d in range(1, 29)]) is None           # 28 rows ok
    assert validate_rows([{DATE_KEY: f"2026-{m:02d}-{d:02d}", PRIMARY: 1.0}
                          for m in range(1, 6) for d in range(1, 29)]
                         ) is not None                               # >110 -> cap
    # S5 merge: clean append (overlap compared on PRIMARY only)
    local = [{DATE_KEY: "2026-09-01", PRIMARY: -123456.78, "trade": 10.0},
             {DATE_KEY: "2026-09-02", PRIMARY: 987654.32, "trade": 10.5}]
    src = local + [{DATE_KEY: "2026-09-03", PRIMARY: -555.0, "trade": 11.0}]
    res = merge_incremental(local, src)
    assert res["merged"] and res["appended"] == 1 and res["overlap"] == 2
    assert res["merged_rows"][-1][DATE_KEY] == "2026-09-03"
    # S6 mismatch on PRIMARY -> local untouched (tol 1.0 yuan)
    src_ok = [dict(local[0]), dict(local[1])]
    src_ok[1][PRIMARY] = 987654.33
    assert merge_incremental(local, src_ok)["merged"]              # cent stable
    src_bad = [dict(local[0]), dict(local[1])]
    src_bad[1][PRIMARY] = 999999.99
    res2 = merge_incremental(local, src_bad)
    assert not res2["merged"] and res2["mismatch"] == "2026-09-02"
    # provenance col drift alone does NOT trip mismatch (source may re-adjust)
    src_px = [dict(local[0]), dict(local[1])]
    src_px[0]["trade"] = 12.34
    assert merge_incremental(local, src_px)["merged"]
    # S7 merge idempotency: rerun on merged output -> zero appended
    res3 = merge_incremental(res["merged_rows"], src)
    assert res3["merged"] and res3["appended"] == 0
    # S8 csv roundtrip (raw-ASCII schema, utf-8 no BOM)
    text = rows_to_csv_text(local)
    assert text.splitlines()[0] == DATE_KEY + "," + ",".join(FLOW_COLS)
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "x.csv")
        atomic_write(p, text)
        back = read_local_csv(p)
        assert len(back) == 2
        assert abs(back[1][PRIMARY] - 987654.32) < 1e-6
        # progress roundtrip
        os.makedirs(os.path.join(td, "d"), exist_ok=True)
        global PROGRESS
        save_backup = PROGRESS
        try:
            PROGRESS = os.path.join(td, "d", "_progress.json")
            prog = {"done": {"000001", "600519"}, "attempts": {"300001": 2}}
            save_progress(prog)
            back_prog = load_progress()
            assert back_prog["done"] == {"000001", "600519"}
            assert back_prog["attempts"]["300001"] == 2
        finally:
            PROGRESS = save_backup
    # S9 market derivation + universe prefix honesty (bj/nt skipped)
    assert market_of("600519") == "sh" and market_of("689009") == "sh"
    assert market_of("000001") == "sz" and market_of("300750") == "sz"
    assert market_of("870357") is None and market_of("430047") is None
    with tempfile.TemporaryDirectory() as td:
        ep = os.path.join(td, "elig.csv")
        with io.open(ep, "w", encoding="utf-8") as f:
            f.write("code,name\n600519,A\n000001,B\n870357,C\n430047,D\n300750,E\n")
        codes, skipped, buckets = universe_codes(elig_path=ep)
        assert codes == ["000001", "300750", "600519"] and len(skipped) == 2
        assert buckets.get("87") == 1 and buckets.get("43") == 1
    # S10 stale gate boundary (fresh vs 20td-stale)
    dcal = [f"2026-09-{d:02d}" for d in range(1, 26)]   # synthetic calendar
    dnow = dt.datetime(2026, 9, 26, 4, 0)                # Saturday pre-open
    needs, why = stale_gate("2026-09-24", dnow, dates=dcal)
    assert not needs, why    # expected=09-25, cutoff within 20td -> fresh
    needs, why = stale_gate("2026-09-04", dnow, dates=dcal)
    assert needs              # older than the 20td boundary (09-05) -> stale
    needs, _ = stale_gate(None, dnow, dates=dcal)
    assert needs              # no panel -> first run
    print("selftest: all guard cases PASS")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "gate"
    if cmd == "gate":
        return gate()
    if cmd == "refresh":
        limit = argv[2] if len(argv) > 2 else None
        return refresh(limit=limit)
    if cmd == "status":
        return status_cmd()
    if cmd == "selftest":
        return _selftest()
    print(f"unknown subcommand: {cmd} (gate|refresh|status|selftest)")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
