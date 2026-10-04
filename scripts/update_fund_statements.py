"""Fund statement faces collector -- EM datacenter bulk-by-period DATA LEG
(T-2026-10-04-166-P1, dept:数据+研究, O-20261002-2115 family-line lineage).

Ticket (GM-signed P1, claim r663): three statement faces per report period
via akshare EM datacenter bulk interfaces -- cashflow stock_xjll_em, balance
stock_zcfz_em, income/performance stock_yjbb_em. Unlocks FUND piece-4
(accrual CFO-NI wedge, Sloan lineage), piece-5 reserve legs (FFScore partial
dROA/d_leverage) and the census gross_profitability flip candidate.
Probe evidence (r663, 6/6 OK): results/_r663bma_cfo_source_probe_facts.json.

Spec: research/shortline/FUND_STATEMENT_PANEL.md.
Lane: bm-a only (R31; fundamental data lane host = update_fundamental.py
family sibling; bulk EM source is network-generic, zero conflict with the
bm-c machine-local fund_history per-symbol family).

Bulk economics (ticket): ~86 periods (2005Q1..latest statutory-complete)
x 3 interfaces ~= 260 calls ~= 30-45 min ONE background pass -- preferred
over the per-symbol 5224-pull pattern (no data-locality constraint).

PIT face: every interface row carries a declare-date column (公告日期 /
最新公告日期) -> stored as avail_date. Consumer availability anchors at
max(actual declare, statutory deadline) per T-145 leg(a) receipt
(statutory-anchor gate inheritance).

Revision limitation DISCLOSED (ticket, r595 leg(b) precedent): EM by-date
returns as-currently-revised values with the latest declare date --
future-rewrite face; quarterly re-pull diff = follow-up slice. Forward
refresh in THIS slice = missing-periods only (statutory-deadline-passed
gate); history frozen as-collected (done-key never re-pulled here).

Storage (gitignored data face + committed status face):
  data/fund_statement_export/_staging/<key>_<period>.parquet   per-period
      snapshot-replace units (atomic tmp+os.replace, (code,period_end) dedupe)
  data/fund_statement_export/{cashflow,balance,income}_faces.parquet
      assembled full faces (sort by (code,period_end), dedupe, atomic)
  data/fund_statement_export/_progress.json   checkpoint done-keys
  data/fund_statement_export/status.json      runtime status (gitignored)
  data/fund_statement_export/_refresh.lock    pid-liveness lock
  results/fund_statement_update_status.json   committed status face

Contract (data-gate-wiring 10 laws):
  1 zero-network no-op gate -- panel complete iff each face parquet covers
    exactly the expected period set 20050331..latest statutory-complete
    (coverage derived from PANEL BYTES, law: cutoff from panel bytes);
  2 separated background refresh -- gate spawns detached `refresh`, returns
    exit 0 immediately; refresh resumes per (interface,period) done-key,
    2.5s citizen pace, conn-fuse 3 consecutive failures -> stop (checkpoint
    preserved), 30-min spawn throttle, pid-liveness lock;
  3 (n/a overlap law) -- quarterly snapshot-replace face, not daily append;
    idempotent done-keys + (code,period_end) dedupe instead; source revision
    rewrite = disclosed limitation, never silently re-pulled;
  4 exit codes gate:     0 ok/no-op/spawned/in-progress | 2 machinery | 3 shape
                         drift (column-set deviation vs probe-frozen = blocked
                         honest, manual ruling, no self-heal -- THS precedent)
                refresh: 0 all-periods complete | 2 incomplete (fuse/window) |
                         3 shape drift;
  5 lane guard -- host=bm-a only, others stdout-only honest no-op zero write;
  6 atomic writes tmp+os.replace; no-NaN keys; cutoff from panel bytes;
  7 conn-fuse 3; all pulls checkpoint-resumable, never restart from zero;
  8 window guard -- trading day 09:15-15:30 EM-pressure band = pull ban
    (statement face is disclosure-coupled, NOT bar-coupled: no bar-landed
     requirement; mid-run band entry = clean abort exit 2);
  9 selftest = offline zero-network, temp-dir-only disk;
 10 S6 chain + smoke_test registered.

TTM derive = consumer-side pure helper `ttm_from_cumulative` importable from
this module (selftested); collector stores raw cumulative values AS
DISCLOSED (zero derive-side judgment).

NO backtest NO engine NO admission NO marks/SEED/ledger touch (pure
acquisition lane; T-67 sec.2 freeze law: forward history >= 12 months
before any new prereg on these faces).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import time
import io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "fund_statement_export")
STAGING_DIR = os.path.join(DATA_DIR, "_staging")
PROGRESS = os.path.join(DATA_DIR, "_progress.json")
STATUS = os.path.join(DATA_DIR, "status.json")
LOCK = os.path.join(DATA_DIR, "_refresh.lock")
LOG = os.path.join(ROOT, "logs", "fund_statements_refresh.log")
COMMITTED_STATUS = os.path.join(ROOT, "results", "fund_statement_update_status.json")

LANE_OWNER = "bm-a"                     # R31 lane-ownership precedent
FIRST_PERIOD = "20050331"                # ticket: 2005Q1 .. latest
INTRADAY_START = dt.time(9, 15)
INTRADAY_END = dt.time(15, 30)           # EM-pressure band (family law)
CALL_SLEEP_S = 2.5                       # citizen pace (R109 precedent)
CALL_RETRIES = 2                         # per-call retry (THS page precedent)
RETRY_SLEEP_S = 5.0
CONN_STOP = 3                            # consecutive failed calls -> fuse
MIN_SPAWN_S = 30 * 60                    # spawn throttle (family precedent)
CALL_TIMEOUT_S = 120                      # single akshare call watchdog

# statutory disclosure deadlines (A-share): period -> deadline
#   Q1 (03-31) -> 04-30 same year      H1 (06-30) -> 08-31
#   Q3 (09-30) -> 10-31                Annual (12-31) -> 04-30 next year
STATUTORY_DEADLINE = {
    "03-31": lambda y: dt.date(y, 4, 30),
    "06-30": lambda y: dt.date(y, 8, 31),
    "09-30": lambda y: dt.date(y, 10, 31),
    "12-31": lambda y: dt.date(y + 1, 4, 30),
}

# frozen schemas: byte-identical to probe raw
# (results/_r663bma_cfo_source_probe_facts.json columns; shape-drift gate)
FROZEN_COLS = {
    "cashflow": ["序号", "股票代码", "股票简称", "净现金流-净现金流",
                 "净现金流-同比增长", "经营性现金流-现金流量净额",
                 "经营性现金流-净现金流占比", "投资性现金流-现金流量净额",
                 "投资性现金流-净现金流占比", "融资性现金流-现金流量净额",
                 "融资性现金流-净现金流占比", "公告日期"],
    "balance": ["序号", "股票代码", "股票简称", "资产-货币资金", "资产-应收账款",
                "资产-存货", "资产-总资产", "资产-总资产同比", "负债-应付账款",
                "负债-预收账款", "负债-总负债", "负债-总负债同比", "资产负债率",
                "股东权益合计", "公告日期"],
    "income": ["序号", "股票代码", "股票简称", "每股收益", "营业总收入-营业总收入",
               "营业总收入-同比增长", "营业总收入-季度环比增长", "净利润-净利润",
               "净利润-同比增长", "净利润-季度环比增长", "每股净资产", "净资产收益率",
               "每股经营现金流量", "销售毛利率", "所处行业", "最新公告日期"],
}
KEY_COLS = {"cashflow": ["股票代码", "股票简称", "公告日期"],
            "balance": ["股票代码", "股票简称", "公告日期"],
            "income": ["股票代码", "股票简称", "最新公告日期"]}
AK_FN = {"cashflow": "stock_xjll_em",
         "balance": "stock_zcfz_em",
         "income": "stock_yjbb_em"}
FACE_PATH = {k: os.path.join(DATA_DIR, f"{k}_faces.parquet") for k in FROZEN_COLS}


class ShapeDrift(Exception):
    """Column set deviates from probe-frozen schema -> stop, manual ruling."""


# ------------------------------------------------------------ periods (pure)
def statutory_deadline(period: str) -> dt.date:
    y = int(period[:4])
    md = f"{period[4:6]}-{period[6:]}"           # '0331' -> '03-31'
    return STATUTORY_DEADLINE[md](y)


def enumerate_periods(first: str, last: str):
    """All quarter-end periods YYYYMMDD in [first, last], ascending."""
    out = []
    y, q = int(first[:4]), (int(first[4:6]) - 1) // 3 + 1
    ly, lq = int(last[:4]), (int(last[4:6]) - 1) // 3 + 1
    while (y, q) <= (ly, lq):
        mm = q * 3
        day = {3: "31", 6: "30", 9: "30", 12: "31"}[mm]
        out.append(f"{y}{mm:02d}{day}")
        q += 1
        if q > 4:
            y, q = y + 1, 1
    return out


def expected_latest_period(now: dt.datetime) -> str:
    """Latest report period whose STATUTORY disclosure deadline has passed
    (ticket: forward refresh = statutory-deadline-passed gate only)."""
    best = FIRST_PERIOD
    for y in (now.year, now.year - 1):
        for md in STATUTORY_DEADLINE:
            p = f"{y}{md.replace('-', '')}"
            if statutory_deadline(p) <= now.date():
                if p > best:
                    best = p
    return best


def expected_period_set(now: dt.datetime):
    return enumerate_periods(FIRST_PERIOD, expected_latest_period(now))


# --------------------------------------------------------- window guard (pure)
def pull_allowed(now=None):
    """(allowed, reason). Trading-day 09:15-15:30 EM-pressure band = ban.
    Statement face is disclosure-coupled, not bar-coupled: no bar-landed
    requirement; nights/pre-open/weekends/holidays = allowed."""
    now = now or dt.datetime.now()
    t = now.time()
    if INTRADAY_START <= t < INTRADAY_END and now.weekday() < 5:
        return False, (f"trading day {now.date().isoformat()} inside "
                       f"09:15-15:30 EM-pressure band")
    return True, "outside EM-pressure band (statement face, no bar coupling)"


# ------------------------------------------------------------- io helpers
def atomic_write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(payload, ensure_ascii=False, indent=1))
    os.replace(tmp, path)


def _read_json(path, default):
    try:
        with io.open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except Exception:
        return default


def load_status():
    st = _read_json(STATUS, {})
    return st if isinstance(st, dict) else {}


def write_status(payload):
    atomic_write_json(STATUS, payload)
    # committed face twin (family precedent: futures_update_status.json)
    face = {k: payload.get(k) for k in (
        "ts", "mode", "verdict", "complete", "blocked", "block_reason",
        "cutoff", "n_periods_expected", "n_periods_present", "rows_total",
        "last_refresh_exit", "requests_used", "zero_row_periods",
        "last_spawn_attempt")}
    face["host"] = LANE_OWNER
    face["evidence_cutoff"] = payload.get("cutoff")
    atomic_write_json(COMMITTED_STATUS, face)


def load_progress():
    prog = _read_json(PROGRESS, {})
    return prog if isinstance(prog, dict) else {}


def save_progress(prog):
    atomic_write_json(PROGRESS, prog)


# ------------------------------------------------------------- lock (pid live)
def _write_lock():
    os.makedirs(DATA_DIR, exist_ok=True)
    atomic_write_json(LOCK, {"pid": os.getpid(),
                             "ts": dt.datetime.now().isoformat(timespec="seconds")})


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
        if pid and _pid_alive(pid):
            return True
    except Exception:
        pass
    return False


# ------------------------------------------------------------- lane id
def _lane_owner_id():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"),
                     "r", encoding="utf-8-sig") as f:
            return str(json.load(f).get("machine_id", ""))
    except Exception:
        return ""


# ------------------------------------------------------------ normalization
def norm_code(v):
    """6-digit A/B/BJ code normalization: digits-only shorter than 6 =
    zero-strip artifact -> zfill(6) (bijective, idempotent; non-digit pass)."""
    s = "" if v is None else str(v)
    if s.endswith(".0"):
        s = s[:-2]
    if s and s.isdigit() and len(s) < 6:
        return s.zfill(6)
    return s


def norm_avail_date(v):
    """Declare date -> 'YYYY-MM-DD' string or None. Handles EM string dates,
    pandas Timestamp, datetime, and empty/-- forms (raw honesty: absent
    availability = None, never fabricated)."""
    if v is None:
        return None
    if isinstance(v, (dt.datetime, dt.date)):
        try:
            return v.strftime("%Y-%m-%d")
        except ValueError:             # pd.NaT is a datetime subclass; strftime raises
            return None
    s = str(v).strip()
    if not s or s in ("--", "-", "nan", "None", "NaT"):
        return None
    s = s.split(" ")[0].split("T")[0]
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return dt.datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def normalize_rows(iface, df, period):
    """Frozen-shape check + normalized key columns + raw values verbatim.
    Returns list[dict] with schema [code, period_end, avail_date, name] +
    value columns (Chinese names, byte-identical to frozen minus keys/序号)."""
    cols = [str(c) for c in df.columns]
    if cols != FROZEN_COLS[iface]:
        raise ShapeDrift(f"{iface}: column drift {cols!r} != frozen "
                        f"{FROZEN_COLS[iface]!r}")
    code_c, name_c, dec_c = KEY_COLS[iface]
    val_cols = [c for c in FROZEN_COLS[iface]
                if c not in ("序号", code_c, name_c, dec_c)]
    rows = []
    for rec in df.to_dict("records"):
        code = norm_code(rec.get(code_c))
        if not code or len(code) != 6 or not code.isdigit():
            continue                      # row-shell defense (R58)
        out = {"code": code,
               "period_end": f"{period[:4]}-{period[4:6]}-{period[6:]}",
               "avail_date": norm_avail_date(rec.get(dec_c)),
               "name": "" if rec.get(name_c) is None else str(rec.get(name_c))}
        for c in val_cols:
            out[c] = rec.get(c)           # raw cumulative value AS DISCLOSED
        rows.append(out)
    # (code, period_end) dedupe: first occurrence wins (snapshot-replace law)
    seen = set()
    deduped = []
    for r in rows:
        k = (r["code"], r["period_end"])
        if k in seen:
            continue
        seen.add(k)
        deduped.append(r)
    return deduped


def staging_path(iface, period):
    return os.path.join(STAGING_DIR, f"{iface}_{period}.parquet")


def write_parquet_atomic(path, rows):
    import pandas as pd
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    pd.DataFrame(rows).to_parquet(tmp, index=False)
    os.replace(tmp, path)


# ------------------------------------------------------------- panel bytes
def panel_coverage():
    """(per-face period sets, rows_total) derived from PANEL BYTES (law:
    cutoff from panel bytes, never from memory/symbols)."""
    import pandas as pd
    cov = {}
    rows_total = 0
    for iface, path in FACE_PATH.items():
        if not os.path.exists(path):
            cov[iface] = set()
            continue
        try:
            df = pd.read_parquet(path, columns=["period_end"])
            # gate coverage must match expected_period_set compact form:
            # assembled faces store EM-native dashed period_end (F6), while
            # expected enumeration is 'YYYYMMDD' -- normalize here or every
            # gate call misreads a complete panel as 100% missing (r671 live
            # catch: 258/258 face-periods phantom-missing -> wasteful spawn).
            cov[iface] = set(df["period_end"].astype(str)
                             .str.replace("-", "", regex=False))
            rows_total += len(df)
        except Exception:
            cov[iface] = set()
    return cov, rows_total


def panel_cutoff(cov):
    """Latest period_end present across ALL faces (panel-bytes cutoff).
    Any face empty/absent -> no honest cross-face cutoff (None)."""
    if not cov:
        return None
    inter = set.intersection(*cov.values())
    return max(inter).replace("-", "") if inter else None


# --------------------------------------------------------------- fetch
def _call_with_timeout(fn, kwargs, timeout_s):
    """Single akshare call with watchdog thread (no infinite hang)."""
    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(fn, **kwargs)
        try:
            return fut.result(timeout=timeout_s)
        except cf.TimeoutError:
            raise RuntimeError(f"call timeout after {timeout_s}s")


def fetch_period(iface, period):
    """One (interface, period) bulk pull. Raises ShapeDrift on drift.
    Returns list[dict] normalized rows (may be 0 = honest zero-rows period)."""
    import akshare as ak
    fn = getattr(ak, AK_FN[iface])
    df = _call_with_timeout(fn, {"date": period}, CALL_TIMEOUT_S)
    if df is None or len(df) == 0:
        return []
    return normalize_rows(iface, df, period)


# --------------------------------------------------------------- assembly
def assemble_faces():
    """Local-only assembly: staging parquets -> face parquets (sort by
    (code, period_end), dedupe safety net, atomic replace)."""
    import pandas as pd
    summary = {}
    for iface, face_path in FACE_PATH.items():
        frames = []
        for p in sorted(os.listdir(STAGING_DIR)) if os.path.isdir(STAGING_DIR) else []:
            if p.startswith(f"{iface}_") and p.endswith(".parquet"):
                try:
                    frames.append(pd.read_parquet(os.path.join(STAGING_DIR, p)))
                except Exception:
                    continue
        if not frames:
            summary[iface] = 0
            continue
        df = pd.concat(frames, ignore_index=True)
        df = df.drop_duplicates(subset=["code", "period_end"], keep="first")
        df = df.sort_values(["code", "period_end"], kind="mergesort").reset_index(drop=True)
        tmp = face_path + ".tmp"
        df.to_parquet(tmp, index=False)
        os.replace(tmp, face_path)
        summary[iface] = len(df)
    return summary


# --------------------------------------------------------------- gate
def gate_verdict(now, done_blocked, cov, expected):
    """Pure decision core (hermetic selftest face).
    -> ("no_op"|"spawn"|"blocked", reason)"""
    if done_blocked:
        return "blocked", "source shape drift awaiting manual ruling"
    missing = {k: sorted(expected - cov[k]) for k in cov}
    n_missing = sum(len(v) for v in missing.values())
    if n_missing == 0:
        return "no_op", (f"panel complete: {len(expected)} periods x "
                         f"{len(cov)} faces cover latest statutory-complete "
                         f"{max(expected)}")
    return "spawn", f"panel incomplete: {n_missing} face-periods missing " \
                    f"(latest expected {max(expected)})"


def spawn_detached_refresh():
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW | 0x00004000)  # BELOW_NORMAL (CEO 10% CPU margin law)
    with io.open(LOG, "a", encoding="utf-8") as lf:
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "refresh"],
                         stdout=lf, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, creationflags=flags, close_fds=False)


def gate(now_fn=None, spawn_fn=None):
    now = (now_fn or dt.datetime.now)()
    spawn_fn = spawn_fn or spawn_detached_refresh
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        print(f"no-op: fund statements lane owned by {LANE_OWNER}, "
              f"not this machine ({owner or '?'})")
        return 0
    st = load_status()
    cov, rows_total = panel_coverage()
    expected = set(expected_period_set(now))
    action, reason = gate_verdict(now, bool(st.get("blocked")), cov, expected)
    common = dict(ts=now.isoformat(timespec="seconds"), verdict=action,
                  n_periods_expected=len(expected),
                  n_periods_present=min((len(s & expected) for s in cov.values()),
                                        default=0),
                  rows_total=rows_total,
                  cutoff=panel_cutoff(cov))
    if action == "blocked":
        st.update(common, mode=f"blocked: {st.get('block_reason', 'shape drift')}")
        write_status(st)
        print(f"blocked: {st.get('block_reason', 'shape drift')} "
              f"(exit 3, awaiting manual ruling)")
        return 3
    if action == "no_op":
        st.update(common, mode=f"no-op: {reason}", complete=True,
                  last_refresh_exit=st.get("last_refresh_exit", 0))
        write_status(st)
        print(f"no-op: {reason} -> zero network")
        return 0
    # spawn path: 30-min throttle + lock liveness (mirror BEFORE acting, r18)
    last = st.get("last_spawn_attempt")
    if last:
        try:
            age = (now - dt.datetime.fromisoformat(last)).total_seconds()
            if age < MIN_SPAWN_S:
                print(f"throttle: spawn {last} ({age / 60:.1f}min ago) "
                      f"< 30min -> no-op (refresh in flight/self-heals)")
                return 0
        except Exception:
            pass
    if _lock_alive():
        print("refresh in progress (lock alive) -> no-op")
        return 0
    st.update(common, last_spawn_attempt=now.isoformat(timespec="seconds"),
              mode="spawn: detached refresh", spawn_reason=reason,
              complete=False)
    write_status(st)
    spawn_fn()
    print(f"spawned detached refresh: {reason}")
    return 0


# --------------------------------------------------------------- refresh
def refresh(now_fn=None, fetch=None, sleep_fn=None):
    """Detached child: collect missing (interface, period) units to staging,
    checkpoint each done-key, assemble faces at end. Injectable for selftest."""
    now_fn = now_fn or dt.datetime.now
    fetch = fetch or fetch_period
    sleep_fn = sleep_fn or time.sleep
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        print(f"no-op: fund statements lane owned by {LANE_OWNER}, "
              f"not this machine ({owner or '?'})")
        return 0
    now = now_fn()
    expected = expected_period_set(now)
    st = load_status()
    if st.get("blocked"):
        print(f"blocked: {st.get('block_reason')} -> refresh refuses (manual ruling)")
        return 3
    allowed, why = pull_allowed(now)
    if not allowed:
        print(f"window closed at start: {why}")
        return 2
    prog = load_progress()
    done = prog.get("done") if isinstance(prog.get("done"), dict) else {}
    # stage rows already written + checkpoint done -> skip (frozen history)
    todo = [(iface, p) for iface in FROZEN_COLS for p in expected
            if f"{iface}:{p}" not in done]
    if not todo:
        summary = assemble_faces()
        st.update(ts=now_fn().isoformat(timespec="seconds"), complete=True,
                  mode=f"no-op: all {len(expected)} periods done "
                       f"(faces re-assembled {summary})",
                  cutoff=panel_cutoff(panel_coverage()[0]),
                  last_refresh_exit=0)
        write_status(st)
        print(f"no-op: all periods done; faces re-assembled {summary}")
        return 0
    # strip proxies for direct EM path (R118 直连铁律, family precedent)
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)
    requests_used = 0
    conn = 0
    zero_rows = []
    _write_lock()
    try:
        for i, (iface, period) in enumerate(todo):
            now = now_fn()
            allowed, why = pull_allowed(now)
            if not allowed:
                save_progress({"done": done})
                st.update(ts=now.isoformat(timespec="seconds"),
                          mode=f"window closed mid-run at {iface}:{period}: {why}",
                          last_refresh_exit=2, requests_used=requests_used,
                          complete=False)
                write_status(st)
                print(f"window closed mid-run at {iface}:{period}: {why} "
                      f"(checkpoint preserved)")
                return 2
            ok, rows, err = False, None, None
            for attempt in range(CALL_RETRIES + 1):
                requests_used += 1
                try:
                    rows = fetch(iface, period)
                    ok, err = True, None
                    break
                except ShapeDrift as e:
                    save_progress({"done": done})
                    st.update(ts=now_fn().isoformat(timespec="seconds"),
                              blocked=True,
                              block_reason=f"shape drift {iface}:{period}: {e}",
                              mode="blocked: shape drift (manual ruling)",
                              last_refresh_exit=3, requests_used=requests_used,
                              complete=False)
                    write_status(st)
                    print(f"SHAPE DRIFT {iface}:{period}: {e} -> blocked, exit 3 "
                          f"(staging/faces untouched by this call)")
                    return 3
                except Exception as e:
                    err = f"{iface}:{period}: {type(e).__name__}: {str(e)[:160]}"
                    if attempt < CALL_RETRIES:
                        sleep_fn(RETRY_SLEEP_S)
            if not ok:
                conn += 1
                print(f"fetch failed ({err}) [{conn}/{CONN_STOP}]")
                if conn >= CONN_STOP:
                    save_progress({"done": done})
                    st.update(ts=now_fn().isoformat(timespec="seconds"),
                              mode=f"conn-fuse stop at {iface}:{period}: {err}",
                              last_refresh_exit=2, requests_used=requests_used,
                              complete=False)
                    write_status(st)
                    print(f"conn-fuse {CONN_STOP} consecutive failures -> stop "
                          f"(checkpoint preserved, gate self-heals)")
                    return 2
                continue
            conn = 0
            if rows:
                write_parquet_atomic(staging_path(iface, period), rows)
            else:
                zero_rows.append(f"{iface}:{period}")
            done[f"{iface}:{period}"] = {"n_rows": len(rows),
                                          "ts": now_fn().isoformat(timespec="seconds")}
            save_progress({"done": done})
            if i < len(todo) - 1:
                sleep_fn(CALL_SLEEP_S)
        # all todo units processed -> assemble + complete check
        summary = assemble_faces()
        cov, rows_total = panel_coverage()
        n_missing = sum(len(set(expected) - cov[k]) for k in cov)
        complete = n_missing == 0
        st.update(ts=now_fn().isoformat(timespec="seconds"),
                  complete=complete,
                  mode=(f"complete: {len(expected)} periods x 3 faces, "
                        f"rows={rows_total} {summary}" if complete
                        else f"partial: {n_missing} face-periods still missing"),
                  cutoff=panel_cutoff(cov),
                  n_periods_expected=len(expected),
                  rows_total=rows_total,
                  zero_row_periods=zero_rows,
                  last_refresh_exit=(0 if complete else 2),
                  requests_used=requests_used)
        write_status(st)
        save_progress({"done": done})
        print(("complete" if complete else f"incomplete ({n_missing} missing)")
              + f": requests={requests_used} zero_row_periods={len(zero_rows)}")
        return 0 if complete else 2
    finally:
        _clear_lock()


# ------------------------------------------------------- TTM consumer helper
def ttm_from_cumulative(pairs):
    """Consumer-side TTM derive from cumulative within-fiscal-year values.

    pairs: iterable of (period_end 'YYYY-MM-DD', cumulative_value) for ONE
    code and ONE statement value column, ascending or any order.
    Returns float TTM (trailing four quarters) or None when insufficient
    structure (missing intermediate quarter -> honest None, no fabrication).

    Two equivalent calibres both honored:
      - delta chain: TTM = sum of last 4 quarterly deltas
        (Q1; H1-Q1; Q3-H1; ANN-Q3, each within the trailing 4 quarters)
      - annual twin formula (update_fundamental.py precedent):
        TTM = ANN_prev + INTERIM - INTERIM_prev_year_twin
    """
    def qnum(pe):
        return (int(pe[5:7]) - 1) // 3 + 1
    by = {}
    for pe, v in pairs:
        if pe is None or v is None:
            continue
        try:
            v = float(v)
        except (TypeError, ValueError):
            continue
        if v != v:                      # NaN
            continue
        by[(int(pe[:4]), qnum(pe))] = v
    if not by:
        return None
    latest = max(by)
    y, q = latest
    deltas = {}
    # quarterly deltas within year y
    if (y, 1) in by:
        deltas[1] = by[(y, 1)]
    if (y, 1) in by and (y, 2) in by:
        deltas[2] = by[(y, 2)] - by[(y, 1)]
    if (y, 2) in by and (y, 3) in by:
        deltas[3] = by[(y, 3)] - by[(y, 2)]
    if (y, 3) in by and (y, 4) in by:
        deltas[4] = by[(y, 4)] - by[(y, 3)]
    if q == 4 and all(k in deltas for k in (1, 2, 3, 4)):
        return deltas[1] + deltas[2] + deltas[3] + deltas[4]   # = annual value
    if q == 4:
        return None                     # incomplete annual chain -> honest None
    # interim latest: TTM = prev annual + interim - prev-year twin
    prev_ann = by.get((y - 1, 4))
    twin = by.get((y - 1, q))
    if prev_ann is not None and twin is not None:
        return prev_ann + by[(y, q)] - twin
    return None


# --------------------------------------------------------------- selftest
def _selftest():
    import tempfile

    # F1 window guard: EM-pressure band only (no bar coupling)
    a, why = pull_allowed(dt.datetime(2026, 10, 5, 10, 0))   # Monday mid-band
    assert not a and "09:15-15:30" in why
    a, _ = pull_allowed(dt.datetime(2026, 10, 5, 9, 14, 59))
    assert a                                                # pre-open
    a, _ = pull_allowed(dt.datetime(2026, 10, 4, 12, 0))    # Sunday
    assert a
    a, _ = pull_allowed(dt.datetime(2026, 10, 5, 15, 30))  # band end boundary
    assert a

    # F2 statutory-deadline period gate
    assert expected_latest_period(dt.datetime(2026, 10, 4, 7, 0)) == "20260630"
    assert expected_latest_period(dt.datetime(2026, 10, 30, 23, 0)) == "20260630"
    assert expected_latest_period(dt.datetime(2026, 10, 31, 9, 0)) == "20260930"
    assert expected_latest_period(dt.datetime(2026, 4, 29, 23, 0)) == "20250930"
    assert expected_latest_period(dt.datetime(2026, 4, 30, 9, 0)) == "20260331"
    assert expected_latest_period(dt.datetime(2026, 9, 1, 9, 0)) == "20260630"
    ps = expected_period_set(dt.datetime(2026, 10, 4, 7, 0))
    assert ps[0] == "20050331" and ps[-1] == "20260630" and len(ps) == 86
    assert enumerate_periods("20250331", "20251231") == \
        ["20250331", "20250630", "20250930", "20251231"]
    assert enumerate_periods("20251231", "20260331") == \
        ["20251231", "20260331"]
    assert statutory_deadline("20260630") == dt.date(2026, 8, 31)
    assert statutory_deadline("20251231") == dt.date(2026, 4, 30)

    # F3 shape drift (column identity, byte level, all three interfaces)
    import pandas as pd
    for iface in FROZEN_COLS:
        cols_bad = FROZEN_COLS[iface][:-1]         # dropped last col = drift
        df_bad = pd.DataFrame([dict(zip(cols_bad, ["x"] * len(cols_bad)))])
        try:
            normalize_rows(iface, df_bad, "20250630")
            raise AssertionError(f"{iface}: shape drift not caught")
        except ShapeDrift:
            pass

    # F4 code normalization (zero-strip artifacts + BJ 6-digit passthrough)
    assert norm_code(790) == "000790" and norm_code("790") == "000790"
    assert norm_code("300666") == "300666" and norm_code("875029") == "875029"
    assert norm_code("000790.0") == "000790"       # floatified code column
    assert norm_code("") == "" and norm_code(None) == ""

    # F5 avail_date normalization (PIT face honesty)
    assert norm_avail_date("2025-08-29") == "2025-08-29"
    assert norm_avail_date(dt.datetime(2025, 8, 29)) == "2025-08-29"
    assert norm_avail_date("2025/08/29 00:00:00") == "2025-08-29"
    assert norm_avail_date("--") is None and norm_avail_date("") is None
    assert norm_avail_date(None) is None and norm_avail_date(float("nan")) is None
    # r663 regression leg: pd.NaT is a datetime subclass -> strftime raised
    # (live crash at cashflow:20080630); must yield None (absent avail, never crash)
    import pandas as _pd
    assert norm_avail_date(_pd.NaT) is None

    # F6 normalize_rows full path: keys + dedupe + raw verbatim + row-shell
    cols = FROZEN_COLS["cashflow"]
    rec_ok = dict(zip(cols, [1, "000790", "测试A", 1.0, 2.0, 3.0, 4.0, 5.0,
                              6.0, 7.0, 8.0, "2025-08-29"]))
    rec_dup = dict(zip(cols, [2, 790, "测试A", 9.0, 9.0, 9.0, 9.0, 9.0,
                              9.0, 9.0, 9.0, "2025-08-29"]))
    rec_shell = dict(zip(cols, [3, None, "壳", None, None, None, None, None,
                                None, None, None, None]))
    df = pd.DataFrame([rec_ok, rec_dup, rec_shell])
    rows = normalize_rows("cashflow", df, "20250630")
    assert len(rows) == 1                          # dup + shell dropped
    r = rows[0]
    assert r["code"] == "000790" and r["period_end"] == "2025-06-30"
    assert r["avail_date"] == "2025-08-29"
    assert r["经营性现金流-现金流量净额"] == 3.0   # raw value verbatim
    assert "序号" not in r and "股票代码" not in r  # keys folded into code/name

    # F7 staging + assembly determinism (sort/dedupe/atomic, temp-dir only)
    with tempfile.TemporaryDirectory() as td:
        global STAGING_DIR, FACE_PATH, DATA_DIR, PROGRESS, STATUS
        keep = (STAGING_DIR, dict(FACE_PATH), DATA_DIR, PROGRESS, STATUS)
        try:
            STAGING_DIR = os.path.join(td, "_staging")
            DATA_DIR = td
            FACE_PATH = {k: os.path.join(td, f"{k}_faces.parquet")
                         for k in FROZEN_COLS}
            PROGRESS = os.path.join(td, "_progress.json")
            STATUS = os.path.join(td, "status.json")
            r1 = [{"code": "000001", "period_end": "2025-06-30",
                   "avail_date": "2025-08-29", "name": "A",
                   "经营性现金流-现金流量净额": 10.0}]
            r2 = [{"code": "000001", "period_end": "2025-09-30",
                   "avail_date": "2025-10-28", "name": "A",
                   "经营性现金流-现金流量净额": 12.0},
                  {"code": "000001", "period_end": "2025-09-30",
                   "avail_date": "2025-10-28", "name": "A",
                   "经营性现金流-现金流量净额": 99.0}]   # assembly dedupe net
            write_parquet_atomic(os.path.join(STAGING_DIR, "cashflow_20250630.parquet"), r1)
            write_parquet_atomic(os.path.join(STAGING_DIR, "cashflow_20250930.parquet"), r2)
            summary = assemble_faces()
            assert summary["cashflow"] == 2
            df = pd.read_parquet(FACE_PATH["cashflow"])
            assert list(df["period_end"]) == ["2025-06-30", "2025-09-30"]  # sorted
            assert list(df["经营性现金流-现金流量净额"]) == [10.0, 12.0]    # dedupe kept first
            # panel coverage derived from bytes
            cov, rows_total = panel_coverage()
            # r671 regression leg: assembled faces store EM-native dashed
            # period_end, but gate expected set is compact 'YYYYMMDD' --
            # panel_coverage must normalize, else a complete panel reads as
            # 100% missing and every gate call spawns a phantom re-fetch.
            assert cov["cashflow"] == {"20250630", "20250930"}
            assert cov["cashflow"] & {"20250630"} == {"20250630"}
            assert cov["balance"] == set() and rows_total == 2
            assert panel_cutoff(cov) is None          # balance face empty -> no common cutoff
        finally:
            STAGING_DIR, FACE_PATH, DATA_DIR, PROGRESS, STATUS = keep

    # F8 gate verdict (pure decision core)
    expected = {"20250331", "20250630"}
    cov_full = {k: set(expected) for k in FROZEN_COLS}
    cov_hole = {k: ({"20250331"} if k != "balance" else set(expected))
                for k in FROZEN_COLS}
    assert gate_verdict(None, False, cov_full, expected)[0] == "no_op"
    assert gate_verdict(None, False, cov_hole, expected)[0] == "spawn"
    assert gate_verdict(None, True, cov_full, expected)[0] == "blocked"

    # F9 TTM derive (delta chain == annual-twin formula; honest None)
    ann_prev = [("2025-03-31", 100.0), ("2025-06-30", 220.0),
                ("2025-09-30", 330.0), ("2025-12-31", 400.0)]
    assert ttm_from_cumulative(ann_prev) == 400.0    # annual complete chain
    interim = [("2025-03-31", 100.0), ("2025-06-30", 220.0),
               ("2025-09-30", 330.0), ("2025-12-31", 400.0),
               ("2026-03-31", 110.0), ("2026-06-30", 240.0)]
    # TTM at 2026-06-30 = 400 + 240 - 220 = 420
    assert abs(ttm_from_cumulative(interim) - 420.0) < 1e-9
    assert ttm_from_cumulative([("2026-06-30", 240.0)]) is None  # no prev structure
    assert ttm_from_cumulative([("2026-03-31", None)]) is None    # NaN/None rows skipped
    assert ttm_from_cumulative([]) is None
    # incomplete annual chain (missing Q3) -> honest None
    assert ttm_from_cumulative([("2025-03-31", 100.0), ("2025-06-30", 220.0),
                                ("2025-12-31", 400.0)]) is None

    print("selftest: all fund statement panel guard cases PASS")
    return 0


# ---------------------------------------------------------------------- main
def status():
    print(json.dumps(load_status(), ensure_ascii=False, indent=1))
    return 0


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "gate"
    if arg == "gate":
        return gate()
    if arg == "refresh":
        return refresh()
    if arg == "status":
        return status()
    if arg == "selftest":
        return _selftest()
    print(f"unknown subcommand: {arg} (gate/refresh/status/selftest)")
    return 2


if __name__ == "__main__":
    sys.exit(main())
