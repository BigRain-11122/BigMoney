"""THS 全单聚合资金流辅助面板 collector (T-2026-09-25-43 slice-2, dept:数据).

Prereg (frozen a30d2ee5, R120): research/shortline/THS_AGG_P1.md (two-phase
batch, this = A-phase forward-collect face).
Spec: research/shortline/THS_PANEL.md (slice-4).
Lane: bm-a only (R31 precedent); family = update_moneyflow (T-39 EM face,
zero touch -- dimensional isolation law, R118).

Source: data.10jqka.com.cn/funds/ggzjl cross-section, ALL-SIZE AGGREGATE
measure. Column names/ordre byte-identical to probe raw
results/shortline/t41_ths_probe_raw.json; mapping aggregate values onto
主力/超大单/大单 semantics = dimensional fabrication, forbidden.

Face epoch consistency law (THS_PANEL §2, core honesty invariant): the
snapshot always shows the LAST COMPLETED session; a pull is legal iff
face-day == date-stamp (last completed bar day, 15:30 convention, local ETF
calendar). Blocked windows: trading-day 09:15-15:30 (intraday mutation +
stamp-hazard band) and post-15:30 while today's bar has not landed (face
flipped but stamp lags). Resume across a face flip = mixed-day file =
fabrication, structurally impossible (resume_valid gate).

Forward lockbox: no backfill API -> one cross-section per completed bar day;
a day whose pull never completes before the face rolls = honest permanent
gap (recorded, never fabricated).

Storage (gitignored): data/ths_ggzjl/daily/<bar-day>.csv + _progress.json
(checkpoint page set) + status.json + _refresh.lock (pid-liveness).

Contract (frozen prereg §6): 105 req/day nominal, 2.5s/page citizen pace,
page retry x2 (5s backoff), conn-fuse 3 consecutive failed pages -> stop
(checkpoint preserved; 30-min gate spawn throttle self-heals), per-page
window re-check (mid-run close = clean abort exit 2), shape drift -> blocked
flag awaiting manual ruling (exit 3, no self-heal per frozen §2(c)).

Exit codes (gate):   0 = ok/no-op/spawned/in-progress; 2 = machinery fault;
                     3 = source shape drift (blocked, manual ruling)
Exit codes (refresh): 0 = day complete; 2 = incomplete (fuse/window/cap);
                     3 = shape drift
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

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "ths_ggzjl")
DAILY_DIR = os.path.join(DATA_DIR, "daily")
PROGRESS = os.path.join(DATA_DIR, "_progress.json")
STATUS = os.path.join(DATA_DIR, "status.json")
LOCK = os.path.join(DATA_DIR, "_refresh.lock")
LOG = os.path.join(ROOT, "logs", "ths_refresh.log")

LANE_OWNER = "bm-a"          # R31 lane-ownership precedent
COMPLETE_HOUR = dt.time(15, 30)
INTRADAY_START = dt.time(9, 15)

PAGE_URL = ("http://data.10jqka.com.cn/funds/ggzjl/field/zdf/"
            "order/desc/page/{pn}/ajax/1/free/1/")
PAGE_SLEEP_S = 2.5            # citizen pace (R109 EM live-fire precedent)
PAGE_RETRIES = 2              # per-page retry (frozen §6)
RETRY_SLEEP_S = 5.0
CONN_STOP = 3                 # consecutive failed pages -> fuse stop
MAX_PAGES = 120               # probe said 105; sanity cap
NOMINAL_PAGES = 105           # declared daily budget (frozen §0)
CRISIS_ROWS = 4800            # frozen §2(b) crisis-candidate line
MIN_SPAWN_S = 30 * 60         # spawn throttle (family precedent)
REQUEST_TIMEOUT = 15

# frozen schema: byte-identical to probe raw (t41_ths_probe_raw.json columns)
FROZEN_COLS = ["序号", "股票代码", "股票简称", "最新价", "涨跌幅", "换手率",
               "流入资金(元)", "流出资金(元)", "净额(元)", "成交额(元)"]

_DATES_CACHE = None


class ShapeDrift(Exception):
    """Column names/ordre deviate from probe raw -> stop, manual ruling."""


# ------------------------------------------------------- calendar gates (pure)
def _load_trading_dates():
    """Local ETF trading-day calendar (update_moneyflow pattern:
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
    evening source lag self-heals -- update_moneyflow exact copy)."""
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


def calendar_face_consistent(stamp, now, dates):
    """True iff no UNACCOUNTED weekday lies strictly between stamp and today.
    The local ETF calendar is the only session oracle: a weekday after the
    stamp with no landed bar is either a holiday (face unchanged, fill legal)
    or a missed update_daily (session ran, face moved ahead of stamp). The
    two are indistinguishable -> conservative block (no fabrication ever)."""
    ds = set(dates) if dates else set()
    d = dt.date.fromisoformat(str(stamp)) + dt.timedelta(days=1)
    today = now.date()
    while d < today:
        if d.weekday() < 5 and d.isoformat() not in ds:
            return False
        d += dt.timedelta(days=1)
    return True


def pull_allowed(now=None, dates=None):
    """(allowed, reason). Face-epoch consistency window guard (THS_PANEL §2):
    trading day 09:15-15:30 = mutating/stamp-hazard band (frozen intraday ban
    09:15-15:05 inclusive); trading day >=15:30 with today's bar NOT yet in
    the local calendar = face flipped but stamp lags -> block until the bar
    lands (calendar advance = consistency oracle); pre-open trading days,
    nights and non-trading days = static face == stamp -> allowed (legitimate
    gap-fill windows), gated by calendar_face_consistent (calendar-lag hole:
    unaccounted weekday between stamp and today = face may be ahead = block)."""
    now = now or dt.datetime.now()
    t = now.time()
    today = now.date().isoformat()
    ds = dates if dates is not None else _load_trading_dates()
    stamp = expected_latest_bar_date(now, ds)
    if INTRADAY_START <= t < COMPLETE_HOUR:
        if ds is not None and today in ds:
            return False, (f"trading day {today} inside 09:15-15:30 "
                           f"(intraday mutation / stamp-hazard band)")
        if now.weekday() < 5:
            # weekday possibly a running session whose bar is not yet in the
            # local calendar -> conservative block (holiday cost = narrower
            # window only, night/pre-open pulls still allowed)
            return False, (f"weekday {today} inside 09:15-15:30 "
                           f"(calendar lag -> conservative block)")
        if not calendar_face_consistent(stamp, now, ds):
            return False, (f"weekend but unaccounted weekday before today "
                           f"(stamp {stamp} calendar lag -> face may be ahead)")
        return True, f"{today} weekend (static face)"
    if t >= COMPLETE_HOUR and now.weekday() < 5:
        # post-close weekday: face = today's finals; consistent only once
        # today's bar has landed (today in calendar)
        if ds is not None:
            if today in ds:
                return True, f"trading day {today} post-close, bar landed (face==stamp)"
            return False, (f"post-close {today} but bar not landed "
                           f"(face flipped, stamp lags) -> wait for calendar")
        return False, f"post-close weekday {today}, calendar absent -> conservative block"
    # pre-open or night or non-trading day: face = last completed session;
    # stamp == calendar last date; consistency still needs the lag check
    if not calendar_face_consistent(stamp, now, ds):
        return False, (f"unaccounted weekday(s) between stamp {stamp} and today "
                       f"(calendar lag -> face may be ahead, no fabrication)")
    return True, "pre-open/night/static face (face==stamp)"


def resume_valid(prog, now, dates):
    """True iff the live face still serves prog's bar_day (no completed
    session between bar_day and now) -- resume across a face flip would mix
    two days into one file = fabrication, structurally blocked here."""
    bar_day = str(prog.get("bar_day") or "")
    if not bar_day:
        return False
    today = now.date().isoformat()
    if today == bar_day:
        # same calendar day: a prog with bar_day==today can only have been
        # created post-15:30 with the bar landed; same-evening resume is fine
        return now.time() >= COMPLETE_HOUR
    if not calendar_face_consistent(bar_day, now, dates):
        return False        # unaccounted weekday -> face may have moved on
    ds = set(dates) if dates else set()
    for d in ds:
        if bar_day < d <= today:
            return False    # a landed-bar session ran after bar_day
    if now.weekday() < 5 and now.time() >= INTRADAY_START:
        # today is a weekday at/after session open: today's session has run
        # (post-close) or is running -> face != bar_day
        return False
    return True             # only weekends/holidays in between -> static


# ------------------------------------------------------------- status/progress
def atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
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
    atomic_write(STATUS, json.dumps(payload, ensure_ascii=False, indent=1))


def load_progress():
    prog = _read_json(PROGRESS, {})
    return prog if isinstance(prog, dict) else {}


def save_progress(prog):
    atomic_write(PROGRESS, json.dumps(prog, ensure_ascii=False))


# ------------------------------------------------------------------ csv face
def _cell(v):
    if v is None:
        return ""
    try:
        if v != v:             # NaN (read_html float cells)
            return ""
    except Exception:
        pass
    return str(v)


def rows_to_csv_text(rows):
    buf = io.StringIO()
    w = _csv.writer(buf, lineterminator="\n")
    w.writerow(FROZEN_COLS)
    for r in rows:
        w.writerow([_cell(r.get(c)) for c in FROZEN_COLS])
    return buf.getvalue()


def day_path(stamp):
    return os.path.join(DAILY_DIR, f"{stamp}.csv")


# --------------------------------------------------------------------- fetch
def _ths_token():
    """hexin-v token via akshare's bundled ths.js (lazy import: gate on
    non-owner machines must not pay the akshare import cost)."""
    from py_mini_racer import MiniRacer                     # R118 import face
    from akshare.stock_feature.stock_fund_flow import _get_file_content_ths
    js = MiniRacer()
    js.eval(_get_file_content_ths("ths.js"))
    return js.call("v")


def _page_headers(token):
    return {
        "Accept": "text/html, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "hexin-v": token,
        "Host": "data.10jqka.com.cn",
        "Pragma": "no-cache",
        "Referer": "http://data.10jqka.com.cn/funds/hyzjl/",
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/90.0.4430.85 Safari/537.36"),
        "X-Requested-With": "XMLHttpRequest",
    }


def _fix_code(v):
    """Restore zero-stripped A-share codes: pd.read_html's TextParser infers
    the all-numeric 股票代码 column to int ('000790' -> 790). All A-share
    codes are exactly 6 digits -> digits-only values shorter than 6 are
    zero-strip artifacts; zfill(6) restores them bijectively (idempotent for
    already-correct 6-digit codes; non-digit values pass through untouched).
    Probe evidence flagged this: t41_ths_probe_raw.json numeric_cols."""
    s = _cell(v)
    if s and s.isdigit() and len(s) < 6:
        return s.zfill(6)
    return s


def _parse_page(text):
    """(rows, page_info_or_None). Raises ShapeDrift on column drift."""
    import pandas as pd
    m = re.search(r'class="page_info"[^>]*>\s*(\d+)\s*/\s*(\d+)', text)
    page_info = (int(m.group(1)), int(m.group(2))) if m else None
    tables = pd.read_html(io.StringIO(text))
    if not tables:
        raise ShapeDrift("no table in page")
    df = tables[0]
    cols = [str(c) for c in df.columns]
    if cols != FROZEN_COLS:
        raise ShapeDrift(f"column drift: {cols!r} != frozen {FROZEN_COLS!r}")
    df["股票代码"] = df["股票代码"].map(_fix_code)
    rows = [{c: v for c, v in zip(FROZEN_COLS, rec.values())}
            for rec in df.to_dict("records")]
    return rows, page_info


def _fetch_page_impl(pn):
    """One ggzjl page: direct connection (proxy strip, R118 直连铁律), fresh
    token per page (akshare precedent). Returns (rows, page_info)."""
    sess = requests.Session()
    sess.trust_env = False
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)
    r = sess.get(PAGE_URL.format(pn=pn), headers=_page_headers(_ths_token()),
                 timeout=REQUEST_TIMEOUT)
    if r.status_code != 200:
        raise RuntimeError(f"page {pn}: HTTP {r.status_code}")
    if not r.encoding or r.encoding.lower() in ("iso-8859-1", "ascii"):
        r.encoding = r.apparent_encoding or "gbk"
    rows, page_info = _parse_page(r.text)
    if not rows:
        raise RuntimeError(f"page {pn}: 0 rows")
    return rows, page_info


# ------------------------------------------------------------------- locking
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
        if pid and _pid_alive(pid):
            return True
    except Exception:
        pass
    return False


# -------------------------------------------------------------------- lane id
def _lane_owner_id():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"),
                     "r", encoding="utf-8-sig") as f:
            return str(json.load(f).get("machine_id", ""))
    except Exception:
        return ""


# ------------------------------------------------------------------- gate
def gate_verdict(now, dates, day_exists, blocked):
    """Pure decision core (hermetic selftest face).

    -> ("no_op", reason) / ("wait", reason) / ("blocked", reason) / ("spawn", reason)
    """
    if blocked:
        return "blocked", "source shape drift awaiting manual ruling"
    stamp = expected_latest_bar_date(now, dates)
    if day_exists:
        return "no_op", f"daily {stamp}.csv already collected (same-day idempotent)"
    allowed, why = pull_allowed(now, dates)
    if not allowed:
        return "wait", f"day file missing but window blocks: {why}"
    return "spawn", f"day file {stamp}.csv missing, window open"


def spawn_detached_refresh():
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    with io.open(LOG, "a", encoding="utf-8") as lf:
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "refresh"],
                         stdout=lf, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, creationflags=flags, close_fds=False)


def gate(now_fn=None, spawn_fn=None):
    """S6 step: zero-network verdict; spawn detached refresh when needed."""
    now = (now_fn or dt.datetime.now)()
    spawn_fn = spawn_fn or spawn_detached_refresh
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        # R31 lane guard + R65 zero-shared-state law: stdout-only, no writes
        print(f"no-op: ths panel lane owned by {LANE_OWNER}, not this machine ({owner or '?'})")
        return 0
    st = load_status()
    action, reason = gate_verdict(now, _load_trading_dates(),
                                  os.path.exists(day_path(expected_latest_bar_date(
                                      now, _load_trading_dates()))),
                                  bool(st.get("blocked")))
    if action == "blocked":
        print(f"blocked: {st.get('block_reason', 'shape drift')} (exit 3, awaiting manual ruling)")
        return 3
    if action == "no_op":
        st.update(ts=now.isoformat(timespec="seconds"), mode=f"no-op: {reason}",
                  cutoff=expected_latest_bar_date(now, _load_trading_dates()))
        write_status(st)
        print(f"no-op: {reason} -> zero network")
        return 0
    if action == "wait":
        st.update(ts=now.isoformat(timespec="seconds"), mode=f"wait: {reason}")
        write_status(st)
        print(f"wait: {reason}")
        return 0
    # spawn path: 30-min throttle + lock liveness, mirror BEFORE acting (r18)
    last = st.get("last_spawn_attempt")
    if last:
        try:
            age = (now - dt.datetime.fromisoformat(last)).total_seconds()
            if age < MIN_SPAWN_S:
                print(f"throttle: spawn {last} ({age / 60:.1f}min ago) < 30min -> no-op")
                return 0
        except Exception:
            pass
    if _lock_alive():
        print("refresh in progress (lock alive) -> no-op")
        return 0
    st.update(last_spawn_attempt=now.isoformat(timespec="seconds"),
              mode="spawn: detached refresh", spawn_reason=reason,
              ts=now.isoformat(timespec="seconds"))
    write_status(st)
    spawn_fn()
    print(f"spawned detached refresh: {reason}")
    return 0


# ------------------------------------------------------------------ refresh
def assemble_rows(pages_data, pages_total):
    rows = []
    for pn in range(1, pages_total + 1):
        rows.extend(pages_data[str(pn)])
    return rows


def refresh(now_fn=None, fetch_page=None, sleep_fn=None):
    """Detached child: collect today's cross-section into daily/<stamp>.csv.
    Injectables (now_fn/fetch_page/sleep_fn) exist for hermetic selftest."""
    now_fn = now_fn or dt.datetime.now
    fetch_page = fetch_page or _fetch_page_impl
    sleep_fn = sleep_fn or time.sleep
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        print(f"no-op: ths panel lane owned by {LANE_OWNER}, not this machine ({owner or '?'})")
        return 0
    dates = _load_trading_dates()
    now = now_fn()
    stamp = expected_latest_bar_date(now, dates)
    target = day_path(stamp)
    if os.path.exists(target):
        st = load_status()
        st.update(ts=now.isoformat(timespec="seconds"), cutoff=stamp,
                  complete=True, mode="no-op: day file exists")
        write_status(st)
        print(f"no-op: {target} exists (same-day idempotent)")
        return 0
    allowed, why = pull_allowed(now, dates)
    if not allowed:
        print(f"window closed at start: {why}")
        return 2
    prog = load_progress()
    if not resume_valid(prog, now, dates):
        old = str(prog.get("bar_day") or "")
        if old and prog.get("pages_total") and not os.path.exists(day_path(old)):
            st = load_status()
            st.setdefault("abandoned_days", [])
            if old not in st["abandoned_days"]:
                st["abandoned_days"].append(old)
            st.update(ts=now.isoformat(timespec="seconds"),
                      mode=f"gap recorded: {old} (face rolled before completion)")
            write_status(st)
            print(f"honest gap: {old} incomplete and face rolled -> abandoned (no fabrication)")
        prog = {"bar_day": stamp, "pages_total": None, "pages_data": {}}
    if prog.get("bar_day") != stamp:
        prog = {"bar_day": stamp, "pages_total": None, "pages_data": {}}
    pages_total = prog.get("pages_total")
    pages_data = prog.get("pages_data") or {}
    if not isinstance(pages_data, dict):
        pages_data = {}
    requests_used = 0
    conn = 0
    _write_lock()
    try:
        pn = 1
        while pages_total is None or pn <= pages_total:
            if str(pn) in pages_data:
                pn += 1
                continue
            now = now_fn()
            allowed, why = pull_allowed(now, dates)
            if not allowed:
                prog.update(bar_day=stamp, pages_total=pages_total, pages_data=pages_data)
                save_progress(prog)
                st = load_status()
                st.update(ts=now.isoformat(timespec="seconds"),
                          mode=f"window closed mid-run at page {pn}: {why}",
                          last_refresh_exit=2)
                write_status(st)
                print(f"window closed mid-run at page {pn}: {why} (checkpoint preserved)")
                return 2
            ok, rows, page_info, err = False, None, None, None
            for attempt in range(PAGE_RETRIES + 1):
                requests_used += 1
                try:
                    rows, page_info = fetch_page(pn)
                    ok = True
                    err = None
                    break
                except ShapeDrift as e:
                    prog.update(bar_day=stamp, pages_total=pages_total, pages_data=pages_data)
                    save_progress(prog)
                    st = load_status()
                    st.update(ts=now.isoformat(timespec="seconds"), blocked=True,
                              block_reason=f"shape drift page {pn}: {e}",
                              mode="blocked: shape drift (manual ruling)", last_refresh_exit=3)
                    write_status(st)
                    print(f"SHAPE DRIFT page {pn}: {e} -> blocked, exit 3 (local daily untouched)")
                    return 3
                except Exception as e:
                    err = f"page {pn}: {type(e).__name__}: {str(e)[:160]}"
                    if attempt < PAGE_RETRIES:
                        sleep_fn(RETRY_SLEEP_S)
            if not ok:
                conn += 1
                print(f"fetch failed ({err}) [{conn}/{CONN_STOP}]")
                if conn >= CONN_STOP:
                    prog.update(bar_day=stamp, pages_total=pages_total, pages_data=pages_data)
                    save_progress(prog)
                    st = load_status()
                    st.update(ts=now.isoformat(timespec="seconds"),
                              mode=f"conn-fuse stop at page {pn}: {err}",
                              last_refresh_exit=2, requests_used=requests_used)
                    write_status(st)
                    print(f"conn-fuse {CONN_STOP} consecutive page failures -> stop "
                          f"(checkpoint preserved, gate self-heals)")
                    return 2
                continue
            conn = 0
            if page_info and (pages_total is None or pn == 1):
                pages_total = page_info[1]
                if not (1 <= pages_total <= MAX_PAGES):
                    st = load_status()
                    st.update(ts=now.isoformat(timespec="seconds"),
                              mode=f"pages_total {pages_total} out of sane range",
                              last_refresh_exit=2)
                    write_status(st)
                    print(f"pages_total {pages_total} outside [1,{MAX_PAGES}] -> honest stop")
                    return 2
            pages_data[str(pn)] = rows
            prog.update(bar_day=stamp, pages_total=pages_total, pages_data=pages_data)
            save_progress(prog)
            pn += 1
            if pages_total is not None and pn <= pages_total:
                sleep_fn(PAGE_SLEEP_S)
        # completeness
        if pages_total is None or len(pages_data) < pages_total:
            st = load_status()
            st.update(ts=now.isoformat(timespec="seconds"),
                      mode=f"incomplete: {len(pages_data)}/{pages_total} pages",
                      last_refresh_exit=2, requests_used=requests_used)
            write_status(st)
            print(f"incomplete: {len(pages_data)}/{pages_total} pages -> exit 2")
            return 2
        rows = assemble_rows(pages_data, pages_total)
        codes = [str(r.get("股票代码", "")) for r in rows]
        dup = len(codes) - len(set(codes))
        crisis = len(rows) < CRISIS_ROWS
        atomic_write(target, rows_to_csv_text(rows))
        st = load_status()
        st.update(ts=now.isoformat(timespec="seconds"), cutoff=stamp, complete=True,
                  rows=len(rows), pages_total=pages_total, requests_used=requests_used,
                  dup_count=dup, crisis_flag=(f"{stamp}:{len(rows)}" if crisis else None),
                  mode=f"complete: {stamp} rows={len(rows)} pages={pages_total}",
                  last_refresh_exit=0,
                  budget_note=(None if requests_used <= NOMINAL_PAGES + 10
                              else f"requests {requests_used} > nominal {NOMINAL_PAGES} (retries)"))
        write_status(st)
        save_progress({"bar_day": stamp, "pages_total": pages_total, "pages_data": {}})
        print(f"complete: {target} rows={len(rows)} pages={pages_total} "
              f"requests={requests_used} dup={dup} crisis_flag={crisis}")
        return 0
    finally:
        _clear_lock()


# ------------------------------------------------------------------- selftest
def _selftest():
    import tempfile
    now = dt.datetime(2026, 9, 25, 4, 30)          # Friday pre-open
    cal = [f"2026-09-{d:02d}" for d in range(1, 25)]   # bar landed through 09-24

    # F1 window guard (窗卫): frozen intraday ban inclusive + stamp-hazard band
    allowed, why = pull_allowed(dt.datetime(2026, 9, 25, 10, 0), cal)
    assert not allowed and "09:15-15:30" in why          # trading day mid-band
    allowed, _ = pull_allowed(dt.datetime(2026, 9, 25, 4, 30), cal)
    assert allowed                                         # pre-open gap-fill
    allowed, _ = pull_allowed(dt.datetime(2026, 9, 25, 8, 0), cal)
    assert allowed                                         # pre-open
    allowed, _ = pull_allowed(dt.datetime(2026, 9, 25, 9, 14, 59), cal)
    assert allowed                                         # boundary: one second before
    allowed, _ = pull_allowed(dt.datetime(2026, 9, 25, 9, 15, 0), cal)
    assert not allowed                                     # boundary: band opens
    allowed, _ = pull_allowed(dt.datetime(2026, 9, 25, 15, 29), cal)
    assert not allowed                                     # boundary: still in band
    allowed, why = pull_allowed(dt.datetime(2026, 9, 25, 15, 40), cal)
    assert not allowed and "bar not landed" in why         # face flipped, stamp lags
    allowed, _ = pull_allowed(dt.datetime(2026, 9, 25, 10, 0), None)
    assert not allowed                                     # calendar absent, weekday -> conservative
    # calendar-lag hole: Friday session ran but bar never landed -> weekend /
    # next-week pulls for the Thursday stamp would mislabel Friday's face
    allowed, why = pull_allowed(dt.datetime(2026, 9, 26, 10, 0), cal)
    assert not allowed and "unaccounted weekday" in why
    allowed, why = pull_allowed(dt.datetime(2026, 9, 28, 8, 0), cal)
    assert not allowed and "unaccounted weekday" in why
    cal_fri = cal + ["2026-09-25"]                         # Friday bar landed
    allowed, _ = pull_allowed(dt.datetime(2026, 9, 25, 20, 0), cal_fri)
    assert allowed                                         # post-close, bar landed
    allowed, _ = pull_allowed(dt.datetime(2026, 9, 26, 10, 0), cal_fri)
    assert allowed                                         # Saturday static (stamp=Fri)
    allowed, _ = pull_allowed(dt.datetime(2026, 9, 27, 12, 0), cal_fri)
    assert allowed                                         # Sunday static
    allowed, _ = pull_allowed(dt.datetime(2026, 9, 28, 8, 0), cal_fri)
    assert allowed                                         # Monday pre-open gap-fill
    allowed, why = pull_allowed(dt.datetime(2026, 9, 28, 15, 31), cal_fri)
    assert not allowed and "bar not landed" in why         # Mon post-close, bar not landed

    # F2 date-stamp (15:30 convention, ETF calendar)
    assert expected_latest_bar_date(dt.datetime(2026, 9, 25, 4, 30), cal) == "2026-09-24"
    assert expected_latest_bar_date(dt.datetime(2026, 9, 25, 20, 0), cal) == "2026-09-24"  # bar not landed
    assert expected_latest_bar_date(dt.datetime(2026, 9, 25, 20, 0),
                                    cal_fri) == "2026-09-25"
    assert expected_latest_bar_date(dt.datetime(2026, 9, 26, 10, 0), cal_fri) == "2026-09-25"
    assert expected_latest_bar_date(dt.datetime(2026, 9, 26, 10, 0), cal) == "2026-09-24"

    # F3 face-epoch resume validity: mixed-day fabrication structurally blocked
    prog = {"bar_day": "2026-09-24", "pages_total": 105, "pages_data": {"1": []}}
    assert resume_valid(prog, dt.datetime(2026, 9, 25, 4, 35), cal) is True    # pre-open same face
    assert resume_valid(prog, dt.datetime(2026, 9, 25, 15, 31), cal) is False  # Fri session ran -> face flipped
    assert resume_valid(prog, dt.datetime(2026, 9, 26, 10, 0), cal) is False  # Sat, Fri unaccounted
    assert resume_valid(prog, dt.datetime(2026, 9, 28, 8, 0), cal) is False   # Mon pre-open, Fri unaccounted
    prog_fri = {"bar_day": "2026-09-25", "pages_total": 105, "pages_data": {"1": []}}
    assert resume_valid(prog_fri, dt.datetime(2026, 9, 25, 20, 0), cal_fri) is True   # same-evening
    assert resume_valid(prog_fri, dt.datetime(2026, 9, 26, 10, 0), cal_fri) is True   # Saturday static
    assert resume_valid(prog_fri, dt.datetime(2026, 9, 28, 8, 0), cal_fri) is True    # Mon pre-open (face=Fri)
    assert resume_valid(prog_fri, dt.datetime(2026, 9, 28, 15, 31), cal_fri) is False # Mon session ran
    cal_mon = cal_fri + ["2026-09-28"]
    assert resume_valid(prog_fri, dt.datetime(2026, 9, 28, 20, 0), cal_mon) is False  # landed session after bar_day

    # F4 raw value preservation (万/亿后缀原样, collector zero parsing)
    raw_row = {c: "" for c in FROZEN_COLS}
    raw_row.update({"序号": "1", "股票代码": "301311", "股票简称": "旗天科技",
                    "最新价": 17.98, "涨跌幅": "20.03%", "换手率": "14.10%",
                    "流入资金(元)": "2.99亿", "流出资金(元)": "2.71亿",
                    "净额(元)": "2753.86万", "成交额(元)": "5.70亿"})
    text = rows_to_csv_text([raw_row])
    assert text.splitlines()[0] == ",".join(FROZEN_COLS)     # header byte-identity
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "2026-09-24.csv")
        atomic_write(p, text)
        raw = io.open(p, "rb").read()
        assert not raw.startswith(b"\xef\xbb\xbf")           # utf-8 no BOM
        back = list(_csv.DictReader(io.open(p, encoding="utf-8")))
        for c in ("流入资金(元)", "净额(元)", "涨跌幅"):
            assert back[0][c] == raw_row[c]                  # strings verbatim
        assert back[0]["股票代码"] == "301311"
        assert float(back[0]["最新价"]) == 17.98
    # NaN cell -> empty string, never "nan"
    nan_row = dict(raw_row, 最新价=float("nan"))
    assert rows_to_csv_text([nan_row]).splitlines()[1].split(",")[3] == ""

    # F5 gate verdict (幂等跳过 zero-network core)
    v = gate_verdict(dt.datetime(2026, 9, 25, 4, 30), cal, day_exists=True, blocked=False)
    assert v[0] == "no_op"                                   # same-day idempotent
    v = gate_verdict(dt.datetime(2026, 9, 25, 4, 30), cal, day_exists=False, blocked=False)
    assert v[0] == "spawn"                                   # missing + window open
    v = gate_verdict(dt.datetime(2026, 9, 25, 10, 0), cal, day_exists=False, blocked=False)
    assert v[0] == "wait"                                    # missing + window closed
    v = gate_verdict(dt.datetime(2026, 9, 25, 4, 30), cal, day_exists=False, blocked=True)
    assert v[0] == "blocked"                                 # drift -> manual ruling

    # F6 shape drift detection (column identity, byte level)
    probe_cols = json.load(io.open(os.path.join(ROOT, "results", "shortline",
                                                "t41_ths_probe_raw.json"),
                                   encoding="utf-8"))["columns"]
    assert probe_cols == FROZEN_COLS                          # frozen face == probe evidence
    import pandas as pd
    df_bad = pd.DataFrame([{c: "x" for c in FROZEN_COLS[:-1]}])  # 9 cols = drift
    try:
        _parse_page(df_bad.to_html(index=False))
        raise AssertionError("shape drift not caught")
    except ShapeDrift:
        pass

    # F7 assemble + page order
    pd_pages = {"1": [{"股票代码": "1"}], "2": [{"股票代码": "2"}], "3": [{"股票代码": "3"}]}
    assert [r["股票代码"] for r in assemble_rows(pd_pages, 3)] == ["1", "2", "3"]

    # F8 code-column zero-strip restore (read_html int inference, live-fire
    # evidence: 1491/5210 rows collected with stripped 000xxx codes before
    # the fix; probe numeric_cols was the advance warning)
    assert _fix_code(790) == "000790" and _fix_code("790") == "000790"
    assert _fix_code("301311") == "301311" and _fix_code("832566") == "832566"
    assert _fix_code("") == "" and _fix_code("A1") == "A1"
    import pandas as pd
    html = pd.DataFrame([{c: "x" for c in FROZEN_COLS}]).to_html(index=False)
    df_zero = pd.DataFrame([dict(zip(FROZEN_COLS, ["1", "000790", "测试", "1.5",
                                                  "1%", "1%", "1亿", "1亿",
                                                  "1万", "1亿"]))])
    rows_z, info_z = _parse_page(df_zero.to_html(index=False) + '<span class="page_info">1/1</span>')
    assert rows_z[0]["股票代码"] == "000790", rows_z[0]      # restored through full parse
    assert info_z == (1, 1)
    # csv round-trip keeps the restored code
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "z.csv")
        atomic_write(p, rows_to_csv_text(rows_z))
        back = list(_csv.DictReader(io.open(p, encoding="utf-8")))
        assert back[0]["股票代码"] == "000790"

    print("selftest: all THS panel guard cases PASS")
    return 0


# ---------------------------------------------------------------------- main
def status():
    st = load_status()
    print(json.dumps(st, ensure_ascii=False, indent=1))
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
