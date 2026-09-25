# -*- coding: utf-8 -*-
"""AH premium panel collector (T-2026-09-24-17 deliverable-2 main body).

Spec: research/shortline/AH_PANEL.md (frozen before implementation).
Lane: dept:数据, bm-a only (R31 precedent); family = update_moneyflow /
update_ths_panel (checkpoint + fuse + detached spawn; dimensional isolation).

Evidence chain (faces probe-validated, results/shortline/ah_face_probes.json
cutoff 2026-09-24 + ah_synth_validate_02318.json slice-1):
  A-leg  ak.stock_zh_a_daily('sh/sz'+code)   sina family, english cols
  H-leg  ak.stock_zh_ah_daily(h_code, start_year, end_year)  -- EXPLICIT YEAR
         WINDOW MANDATORY (full-window call truncates at 2019-12-31)
  FX     ak.currency_boc_sina('港币')         BOC official central parity,
         iloc4 per-100 HKD -> /100; ffill within panel (disclosed)
  HSAHP  ak.stock_hk_index_daily_sina('HSAHP') short recent window only
  map    EM push2 clist fs=b:DLMK0101 direct urllib (ProxyHandler({}) recipe,
         moneyflow T4) -- authoritative A<->H dual-code table; EM domain is
         intermittent on this host -> conn-fuse 3 = mapping unavailable this
         run = honest exit 2, gate self-heals on next spawn
  census tencent hk_rank.php board=A_H (akshare stock_zh_ah_spot same source)
         -- row field 13 = spot premium % = per-pair mapping cross-check

Frozen premium formula (slice-1 L7): premium = close_A / (close_H * fx) - 1.

Storage (gitignored, regenerable):
  data/ah_panel/per/<h_code>.csv        append-only, overlap boundary verified
  data/ah_panel/_universe_em.json      frozen A<->H mapping (fetched_at)
  data/ah_panel/_universe_tx.json      tencent census (cross-check face)
  data/ah_panel/fx_series.csv / hsahp_index.csv
  data/ah_panel/ah_premium_panel.parquet   consolidated long panel (finalize)
  data/ah_panel/_progress.json         checkpoint {run_target, done, attempts}
  data/ah_panel/_refresh.lock          {pid, ts} pid-liveness (D-03 family)
Status (tracked): results/ah_panel_status.json

Exit codes (gate):    0 = ok/no-op/spawned/in-progress; 2 = machinery fault
Exit codes (refresh): 0 = complete; 2 = incomplete (fuse / mapping unavailable
                      / failures remain -- checkpoint preserved, gate heals);
                      3 = complete but overlap mismatches occurred
"""
from __future__ import annotations

import csv as _csv
import datetime as dt
import io
import json
import os
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "ah_panel")
PER_DIR = os.path.join(DATA_DIR, "per")
PROGRESS = os.path.join(DATA_DIR, "_progress.json")
LOCK = os.path.join(DATA_DIR, "_refresh.lock")
UNIVERSE_EM = os.path.join(DATA_DIR, "_universe_em.json")
UNIVERSE_TX = os.path.join(DATA_DIR, "_universe_tx.json")
FX_CSV = os.path.join(DATA_DIR, "fx_series.csv")
HSAHP_CSV = os.path.join(DATA_DIR, "hsahp_index.csv")
PANEL_PARQUET = os.path.join(DATA_DIR, "ah_premium_panel.parquet")
STATUS = os.path.join(ROOT, "results", "ah_panel_status.json")
LOG = os.path.join(ROOT, "logs", "ah_refresh.log")

LANE_OWNER = "bm-a"            # R31 lane-ownership precedent
WINDOW_START = "2015-01-01"
WINDOW_START_YEAR = "2015"
PAIR_SLEEP_S = 2.5             # citizen pace (R109 live-fire precedent)
PAGE_RETRIES = 2
RETRY_SLEEP_S = 5.0
FUSE_LIMIT = 5                # consecutive pair failures -> stop this run
CONN_STOP = 3                 # consecutive connection-level fails -> source stop
QUARANTINE_AT = 3             # cumulative pair failures -> quarantine
MIN_SPAWN_S = 30 * 60          # spawn throttle (family precedent)
HK_SAFE_HOUR = dt.time(16, 30)  # H-leg 16:00 close + source lag; before this,
                                # today's target is not required (churn guard)
FX_RANGE = (0.70, 1.00)        # CNY per 1 HKD sanity band (history 2015->now)
PREMIUM_GROSS_CAP = 5.0       # |premium| beyond = leg failure (wrong mapping /
                              # bad price guard; real AH premium stays well under)
OVERLAP_TOL = 1e-6
CROSSCHECK_TOL = 0.05
MIN_PAIR_ROWS = 60            # ~1 quarter of common trading days; fewer = the
                              # pair is too young / broken to feed the panel
PER_HEADER = ["date", "close_A", "close_H", "fx_HKD_CNY", "premium"]

EM_URL = "https://push2.eastmoney.com/api/qt/clist/get"
EM_FIELDS = "f193,f191,f192,f12,f13,f14,f1,f2,f4,f3,f152,f186,f190,f187,f189,f188"
EM_MAX_PAGES = 10             # universe ~150-220 at pz=100
EM_TIMEOUT = 15
TX_URL = "http://stock.gtimg.cn/data/hk_rank.php"
TX_HEADERS = {"Referer": "http://stockapp.finance.qq.com/mstats/",
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/77.0.3865.120 Safari/537.36"}
TX_TIMEOUT = 15

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------- lane identity

def _lane_owner_id():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"),
                      encoding="utf-8-sig") as f:
            return json.load(f).get("machine_id")
    except Exception:
        return None


# ---------------------------------------------------------------- local calendar

def _load_trading_dates():
    """Local ETF trading-day calendar (family: update_lhb/update_futures)."""
    import glob as _glob
    import re as _re
    cands = [os.path.join(ROOT, "data", "daily", "510300.csv")]
    cands += [p for p in sorted(_glob.glob(os.path.join(ROOT, "data",
                    "daily", "*.csv"))) if p != cands[0]]
    for p in dict.fromkeys(cands):
        try:
            with io.open(p, "r", encoding="utf-8") as f:
                ds = {str(r.get("date") or "") for r in _csv.DictReader(f)}
            ds = sorted(d for d in ds if _re.match(r"^\d{4}-\d{2}-\d{2}$", d))
            if len(ds) >= 100:
                return ds
        except Exception:
            continue
    return None


def expected_latest_bar_date(now, dates):
    """Latest date a COMPLETE A-share daily row can exist (15:30 convention)."""
    today = now.date().isoformat()
    if now.time() >= dt.time(15, 30):
        if dates is None:
            if now.weekday() < 5:
                return today
        elif today in dates:
            return today
    if dates is not None:
        prior = [d for d in dates if d < today]
        if prior:
            return prior[-1]
    d = now.date() - dt.timedelta(days=1) if now.time() < dt.time(15, 30) \
        else now.date()
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d.isoformat()


def gate_target(now, dates):
    """Freshness target for the AH panel (pure).
    Before HK_SAFE_HOUR today's H row is not required -> target = previous
    A trading day; after it -> expected latest bar date (usually today)."""
    if now.time() < HK_SAFE_HOUR:
        today = now.date().isoformat()
        if dates:
            prior = [d for d in dates if d < today]
            if prior:
                return prior[-1]
        d = now.date() - dt.timedelta(days=1)
        while d.weekday() >= 5:
            d -= dt.timedelta(days=1)
        return d.isoformat()
    return expected_latest_bar_date(now, dates)


def gate_needs_refresh(status, target):
    """(bool, reason). Zero-network freshness verdict (pure)."""
    if not status.get("complete"):
        return True, "panel not complete (first run or prior fuse-stop)"
    cutoff = str(status.get("cutoff") or "")
    if not cutoff or cutoff < target:
        return True, f"panel cutoff {cutoff or 'none'} < target {target}"
    return False, f"panel cutoff {cutoff} covers target {target}"


# ---------------------------------------------------------------- pure helpers

def a_leg_symbol(a_code):
    """Exchange prefix for the sina A-leg face; None = unsupported board."""
    if not a_code or len(a_code) != 6 or not a_code.isdigit():
        return None
    if a_code.startswith("6"):
        return "sh" + a_code
    if a_code.startswith("0") or a_code.startswith("3"):
        return "sz" + a_code
    return None


def norm_date(v):
    s = str(v)
    return s[:10]


def fx_ffill_map(fx_rows, dates):
    """Forward-fill FX lookup for `dates` from sorted fx_rows [(date, rate)].
    Returns {date: rate}; dates before the first fx row are omitted (dropped,
    disclosed in spec S1). Pure."""
    out = {}
    i = 0
    n = len(fx_rows)
    for d in sorted(dates):
        while i < n and fx_rows[i][0] <= d:
            i += 1
        if i > 0:
            out[d] = fx_rows[i - 1][1]
    return out


def synthesize_pair(a_rows, h_rows, fx_map, start=WINDOW_START,
                    gross_cap=PREMIUM_GROSS_CAP):
    """a_rows/h_rows: [(date, close)] -> premium rows on common dates >= start.
    Returns (rows, stats); rows = [(date, close_A, close_H, fx, premium)].
    Raises ValueError on gross premium violation (wrong mapping / bad price).
    Pure."""
    ad = {norm_date(d): float(c) for d, c in a_rows}
    hd = {norm_date(d): float(c) for d, c in h_rows}
    common = sorted(d for d in (set(ad) & set(hd)) if d >= start)
    rows = []
    for d in common:
        fx = fx_map.get(d)
        if fx is None:
            continue
        p = ad[d] / (hd[d] * fx) - 1.0
        if abs(p) > gross_cap:
            raise ValueError(f"gross premium {p:.4g} at {d} exceeds cap "
                             f"{gross_cap} (suspect mapping/price)")
        rows.append((d, ad[d], hd[d], fx, p))
    stats = {"rows": len(rows), "skipped_no_fx": len(common) - len(rows),
             "first": rows[0][0] if rows else None,
             "last": rows[-1][0] if rows else None}
    return rows, stats


def overlap_verify(local_rows, new_rows, tol=OVERLAP_TOL):
    """Deterministic re-derivation check on shared dates (append-only law).
    (ok, mismatch_dates). Compares premium (and components) within tol."""
    loc = {r[0]: r for r in local_rows}
    bad = []
    for r in new_rows:
        old = loc.get(r[0])
        if old is None:
            continue
        if (abs(float(old[1]) - r[1]) > tol or abs(float(old[2]) - r[2]) > tol
                or abs(float(old[3]) - r[3]) > tol
                or abs(float(old[4]) - r[4]) > tol):
            bad.append(r[0])
    return (not bad), bad


def rows_to_append(local_rows, new_rows):
    """Only rows strictly after the local last date (append-only)."""
    if not local_rows:
        return list(new_rows)
    last = local_rows[-1][0]
    return [r for r in new_rows if r[0] > last]


def crosscheck_verdict(premium, tx_premium_pct, tol=CROSSCHECK_TOL):
    """(verdict, detail). verdict in {'pass','fail'}; caller quarantines on
    fail (tencent spot premium ratio vs latest synthesized close premium;
    a wrong A<->H mapping shows up as a huge gap). Pure."""
    if tx_premium_pct is None:
        return "deferred", "no census premium field"
    diff = abs(premium - float(tx_premium_pct) / 100.0)
    if diff <= tol:
        return "pass", f"diff {diff:.4g} within {tol}"
    return "fail", f"diff {diff:.4g} > {tol} (mapping suspect)"


def progress_roll(progress, new_target):
    """New bar-day target -> reset done set, keep attempts + quarantine
    (cumulative lifetime counters). Pure."""
    if progress.get("run_target") == new_target:
        return progress
    out = dict(progress)
    out["run_target"] = new_target
    out["done"] = []
    return out


# ---------------------------------------------------------------- file helpers

def _read_json(path, default=None):
    try:
        with io.open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def pair_path(h_code):
    return os.path.join(PER_DIR, f"{h_code}.csv")


def read_pair_file(h_code):
    """Local per-pair rows [(date, close_A, close_H, fx, premium)]."""
    p = pair_path(h_code)
    if not os.path.exists(p):
        return []
    rows = []
    with io.open(p, encoding="utf-8") as f:
        for r in _csv.DictReader(f):
            rows.append((r["date"], float(r["close_A"]), float(r["close_H"]),
                         float(r["fx_HKD_CNY"]), float(r["premium"])))
    return rows


def append_pair_rows(h_code, rows):
    """Create-with-header or append; caller has already overlap-verified."""
    p = pair_path(h_code)
    os.makedirs(PER_DIR, exist_ok=True)
    new = not os.path.exists(p)
    with io.open(p, "a", encoding="utf-8", newline="\n") as f:
        w = _csv.writer(f)
        if new:
            w.writerow(PER_HEADER)
        for r in rows:
            w.writerow([r[0], repr(r[1]), repr(r[2]), repr(r[3]), repr(r[4])])


def _pid_alive(pid):
    try:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                              capture_output=True, timeout=15)
        return f'"{pid}"' in out.stdout.decode("utf-8", errors="replace")
    except Exception:
        return False


def _lock_alive():
    st = _read_json(LOCK)
    if not st:
        return False
    pid = st.get("pid")
    return bool(pid and _pid_alive(pid))


def _acquire_lock():
    _write_json(LOCK, {"pid": os.getpid(),
                       "ts": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})


def _release_lock():
    try:
        os.remove(LOCK)
    except Exception:
        pass


def load_status():
    return _read_json(STATUS, {}) or {}


def write_status(**patch):
    st = load_status()
    st.update(patch)
    _write_json(STATUS, st)
    return st


# ---------------------------------------------------------------- network legs

def _opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _fetch_em_page(pn, timeout=EM_TIMEOUT):
    params = {"np": "1", "fltt": "1", "invt": "2", "fs": "b:DLMK0101",
              "fields": EM_FIELDS, "fid": "f3", "pn": str(pn), "pz": "100",
              "po": "1", "dect": "1", "wbp2u": "|0|0|0|web"}
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(
        EM_URL + "?" + qs,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                 "Referer": "https://quote.eastmoney.com/"})
    with _opener().open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def fetch_em_ah_table(fetch_page=None):
    """Authoritative A<->H mapping. Returns (rows, total).
    rows: {h_code, a_code, name, a_price, premium_pct, parity}.
    Raises ConnectionError-ish after per-page retries (caller fuses)."""
    fetch_page = fetch_page or _fetch_em_page
    out, total = [], None
    for pn in range(1, EM_MAX_PAGES + 1):
        js = None
        err = None
        for attempt in range(PAGE_RETRIES + 1):
            try:
                js = fetch_page(pn)
                err = None
                break
            except Exception as e:
                err = f"em page {pn}: {type(e).__name__}: {str(e)[:160]}"
                if attempt < PAGE_RETRIES:
                    time.sleep(RETRY_SLEEP_S)
        if err:
            raise RuntimeError(err)
        data = (js or {}).get("data") or {}
        diff = data.get("diff") or []
        total = data.get("total", total)
        for it in diff:
            h = str(it.get("f12") or "").strip()
            a = str(it.get("f191") or "").strip()
            if not h or not a or a in ("-", ""):
                continue
            out.append({
                "h_code": h.zfill(5), "a_code": a.zfill(6),
                "name": str(it.get("f193") or ""),
                "a_price": it.get("f186"), "premium_pct": it.get("f188"),
                "parity": it.get("f189"),
            })
        if total is not None and len(out) >= int(total):
            break
        if len(diff) < 100:
            break
    return out, total


def fetch_tx_census(fetch=None):
    """Tencent AH census (akshare stock_zh_ah_spot same source, raw rows
    kept: field 13 = spot premium %). Returns (rows, page_count)."""
    import requests
    from akshare.utils import demjson

    def _page(req_page):
        params = {"board": "A_H", "metric": "price", "pageSize": "20",
                  "reqPage": str(req_page), "order": "decs",
                  "var_name": "list_data"}
        r = requests.get(TX_URL, params=params, headers=TX_HEADERS,
                         timeout=TX_TIMEOUT)
        t = r.text
        return demjson.decode(t[t.find("{"):t.rfind("}") + 1])["data"]

    d = None
    for attempt in range(PAGE_RETRIES + 1):
        try:
            d = _page(0)
            break
        except Exception:
            if attempt < PAGE_RETRIES:
                time.sleep(RETRY_SLEEP_S)
            else:
                raise
    page_count = int(d.get("page_count") or 0)
    rows = []
    raw = d.get("page_data") or []
    for req_page in range(0, page_count):
        pd_ = raw if req_page == 0 else _page(req_page)["page_data"]
        for line in pd_:
            f = str(line).split("~")
            if len(f) < 14 or not f[0].strip():
                continue
            prem = None
            try:
                prem = float(f[13])
            except Exception:
                pass
            rows.append({"h_code": f[0].strip().zfill(5),
                         "name": f[1], "premium_pct": prem})
    return rows, page_count


def fetch_fx_series(end_date=None):
    """BOC official central parity, per-100 HKD -> unit rate.
    Returns sorted [(date, rate)] with NaN rows dropped."""
    import akshare as ak
    end = end_date or dt.date.today().strftime("%Y%m%d")
    df = ak.currency_boc_sina(symbol="港币", start_date="20150101",
                              end_date=end)
    rows = []
    for _, r in df.iterrows():
        d = norm_date(r.iloc[0])
        v = r.iloc[4]
        try:
            v = float(v)
        except Exception:
            continue
        if v != v:  # NaN on source holidays
            continue
        rows.append((d, v / 100.0))
    rows.sort(key=lambda x: x[0])
    return rows


def fetch_hsahp():
    """HSAHP index close series (short recent window, disclosed)."""
    import akshare as ak
    df = ak.stock_hk_index_daily_sina(symbol="HSAHP")
    cols = [str(c) for c in df.columns]
    if "close" not in cols:
        raise RuntimeError(f"hsahp shape drift: cols {cols}")
    rows = [(norm_date(r["date"]), float(r["close"]))
            for _, r in df.iterrows()]
    rows.sort(key=lambda x: x[0])
    return rows


def fetch_a_leg(a_code, symbol=None):
    """A-leg sina daily closes [(date, close)]; full history one call."""
    import akshare as ak
    sym = symbol or a_leg_symbol(a_code)
    if not sym:
        raise RuntimeError(f"unsupported A board for {a_code}")
    df = ak.stock_zh_a_daily(symbol=sym, adjust="")
    cols = [str(c) for c in df.columns]
    if "close" not in cols or "date" not in cols:
        raise RuntimeError(f"A-leg shape drift: cols {cols}")
    return [(norm_date(r["date"]), float(r["close"])) for _, r in df.iterrows()]


def fetch_h_leg(h_code, end_year=None):
    """H-leg tencent AH daily closes; EXPLICIT YEAR WINDOW mandatory
    (full-window call truncates at 2019-12-31 -- slice-1 L1/L3c evidence)."""
    import akshare as ak
    ey = end_year or str(dt.date.today().year)
    df = ak.stock_zh_ah_daily(symbol=h_code, start_year=WINDOW_START_YEAR,
                              end_year=ey)
    if len(df.columns) != 6:
        raise RuntimeError(f"H-leg shape drift: {len(df.columns)} cols")
    return [(norm_date(r.iloc[0]), float(r.iloc[2])) for _, r in df.iterrows()]


# ---------------------------------------------------------------- refresh

def _write_series_csv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        w = _csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(list(r))
    os.replace(tmp, path)


def run_refresh():
    os.makedirs(DATA_DIR, exist_ok=True)
    if _lock_alive():
        print("refresh in progress (lock alive) -- nothing to do")
        return 0
    _acquire_lock()
    try:
        return _refresh_inner()
    finally:
        _release_lock()


def _refresh_inner():
    now = dt.datetime.now()
    dates = _load_trading_dates()
    target = gate_target(now, dates)
    prog = progress_roll(_read_json(PROGRESS, {}) or {}, target)
    status = load_status()

    # -- leg 1: EM mapping (authoritative; fuse -> honest exit 2)
    try:
        em_rows, em_total = fetch_em_ah_table()
    except Exception as e:
        write_status(mode="refresh", last_refresh_exit=2, ts=now.strftime(
            "%Y-%m-%d %H:%M:%S"), mapping_error=str(e)[:300], run_target=target)
        print(f"EM mapping unavailable: {str(e)[:200]}")
        return 2
    _write_json(UNIVERSE_EM, {"fetched_at": now.strftime(
        "%Y-%m-%d %H:%M:%S"), "total": em_total, "rows": em_rows})
    pairs = [r for r in em_rows if a_leg_symbol(r["a_code"])]
    print(f"EM mapping: total={em_total} mapped_pairs={len(pairs)}")

    # -- leg 2: tencent census (cross-check face; non-fatal)
    tx_map = {}
    tx_rows_n = 0
    try:
        tx_rows, tx_pages = fetch_tx_census()
        tx_rows_n = len(tx_rows)
        _write_json(UNIVERSE_TX, {"fetched_at": now.strftime(
            "%Y-%m-%d %H:%M:%S"), "rows": tx_rows, "pages": tx_pages})
        tx_map = {r["h_code"]: r.get("premium_pct") for r in tx_rows}
    except Exception as e:
        print(f"tx census unavailable (non-fatal): {str(e)[:160]}")

    # -- leg 3: FX series (fatal)
    fx_rows = fetch_fx_series()
    if len(fx_rows) < 100:
        write_status(mode="refresh", last_refresh_exit=2, ts=now.strftime(
            "%Y-%m-%d %H:%M:%S"), fx_error=f"only {len(fx_rows)} fx rows")
        return 2
    fx_bad = sum(1 for _, v in fx_rows if not (FX_RANGE[0] <= v <= FX_RANGE[1]))
    _write_series_csv(FX_CSV, ["date", "fx_HKD_CNY"], fx_rows)

    # -- leg 4: HSAHP index (non-fatal)
    hsahp_rows_n = 0
    try:
        hs = fetch_hsahp()
        hsahp_rows_n = len(hs)
        _write_series_csv(HSAHP_CSV, ["date", "close"], hs)
    except Exception as e:
        print(f"hsahp unavailable (non-fatal): {str(e)[:160]}")

    # -- leg 5: per-pair pulls
    quarantined = dict(prog.get("quarantined") or {})
    attempts = dict(prog.get("attempts") or {})
    done = list(prog.get("done") or [])
    mismatches, crosschecks = [], {}
    fuse = 0
    pulled = 0
    for pair in pairs:
        h = pair["h_code"]
        if h in quarantined:
            continue
        if h in done:
            continue
        if fuse >= FUSE_LIMIT:
            print(f"fuse stop at {fuse} consecutive failures "
                  "(checkpoint preserved)")
            break
        try:
            a_rows = fetch_a_leg(pair["a_code"])
            h_rows = fetch_h_leg(h)
            common_dates = [d for d in
                            ({r[0] for r in a_rows} & {r[0] for r in h_rows})
                            if d >= WINDOW_START]
            fx_map = fx_ffill_map(fx_rows, common_dates)
            rows, stats = synthesize_pair(a_rows, h_rows, fx_map)
            if len(rows) < MIN_PAIR_ROWS:
                raise RuntimeError(f"only {len(rows)} common rows "
                                    f"(too young/broken for panel)")
            local = read_pair_file(h)
            ok, bad = overlap_verify(local, rows)
            if not ok:
                mismatches.append(h)
                print(f"overlap mismatch on {h}: {bad[:3]} -- local untouched")
                fuse += 1
                continue
            new = rows_to_append(local, rows)
            if new:
                append_pair_rows(h, new)
                pulled += len(new)
            # mapping cross-check: only meaningful when the latest synthesized
            # row is the current bar day (census = live spot snapshot)
            verdict, detail = "deferred", "no census or stale last row"
            if tx_map.get(h) is not None and rows[-1][0] == target:
                verdict, detail = crosscheck_verdict(rows[-1][4], tx_map[h])
            crosschecks[h] = verdict
            if verdict == "fail":
                quarantined[h] = f"crosscheck {detail} @ {now:%Y-%m-%d}"
                print(f"crosscheck FAIL {h}: {detail} -> quarantined")
                continue
            done.append(h)
            fuse = 0
            _write_json(PROGRESS, {"run_target": target, "done": done,
                                   "attempts": attempts,
                                   "quarantined": quarantined,
                                   "last_update": now.strftime(
                                       "%Y-%m-%d %H:%M:%S")})
        except Exception as e:
            attempts[h] = int(attempts.get(h, 0)) + 1
            fuse += 1
            print(f"pair {h} fail: {str(e)[:160]} "
                  f"(attempt {attempts[h]})")
            if attempts[h] >= QUARANTINE_AT:
                quarantined[h] = f"{QUARANTINE_AT} cumulative failures " \
                                 f"@ {now:%Y-%m-%d}"
            _write_json(PROGRESS, {"run_target": target, "done": done,
                                   "attempts": attempts,
                                   "quarantined": quarantined,
                                   "last_update": now.strftime(
                                       "%Y-%m-%d %H:%M:%S")})
        time.sleep(PAIR_SLEEP_S)

    _write_json(PROGRESS, {"run_target": target, "done": done,
                           "attempts": attempts, "quarantined": quarantined,
                           "last_update": now.strftime("%Y-%m-%d %H:%M:%S")})

    # -- finalize: consolidated panel + status
    cutoff, panel_rows = None, 0
    try:
        import pandas as pd
        frames = []
        em_by_h = {r["h_code"]: r for r in pairs}
        for h in done:
            f = pair_path(h)
            if not os.path.exists(f):
                continue
            dfp = pd.read_csv(f)
            dfp["h_code"] = h
            dfp["a_code"] = em_by_h[h]["a_code"]
            frames.append(dfp)
            panel_rows += len(dfp)
            if cutoff is None or str(dfp["date"].max()) > cutoff:
                cutoff = str(dfp["date"].max())
        if frames:
            panel = pd.concat(frames, ignore_index=True)[
                ["date", "h_code", "a_code", "close_A", "close_H",
                 "fx_HKD_CNY", "premium"]]
            panel.sort_values(["date", "h_code"], inplace=True)
            panel.to_parquet(PANEL_PARQUET, index=False)
    except Exception as e:
        print(f"panel assembly error: {str(e)[:200]}")

    complete = (len(done) + len(quarantined)) >= len(pairs) and fuse < FUSE_LIMIT
    fresh = [h for h in done]
    exit_code = 2 if not complete else (3 if mismatches else 0)
    write_status(
        mode="refresh", ts=now.strftime("%Y-%m-%d %H:%M:%S"),
        complete=complete, cutoff=cutoff, run_target=target,
        universe_em_total=em_total, mapped_pairs=len(pairs),
        fresh_pairs=len(fresh), pulled_rows=pulled,
        quarantined=quarantined, quarantine_count=len(quarantined),
        mismatch_pairs=mismatches,
        crosscheck_pass=sum(1 for v in crosschecks.values() if v == "pass"),
        crosscheck_deferred=sum(1 for v in crosschecks.values()
                                if v == "deferred"),
        fx_rows=len(fx_rows), fx_range_flag=fx_bad,
        hsahp_rows=hsahp_rows_n, tx_census_rows=tx_rows_n,
        panel_rows=panel_rows, last_refresh_exit=exit_code,
        evidence_cutoff=expected_latest_bar_date(now, dates),
    )
    print(f"refresh done: pairs={len(pairs)} done={len(done)} "
          f"quarantined={len(quarantined)} pulled_rows={pulled} "
          f"cutoff={cutoff} complete={complete} exit={exit_code}")
    return exit_code


# ---------------------------------------------------------------- gate

def spawn_detached_refresh():
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    with io.open(LOG, "a", encoding="utf-8") as lf:
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "refresh"],
                         stdout=lf, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, creationflags=flags,
                         close_fds=False)


def run_gate(now_fn=None, spawn_fn=None):
    now = (now_fn or dt.datetime.now)()
    spawn_fn = spawn_fn or spawn_detached_refresh
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        print(f"no-op: ah panel lane owned by {LANE_OWNER}, "
              f"not this machine ({owner or '?'})")
        return 0
    dates = _load_trading_dates()
    target = gate_target(now, dates)
    if _lock_alive():
        print(f"refresh in progress, target {target} -- no-op")
        return 0
    st = load_status()
    need, why = gate_needs_refresh(st, target)
    if not need:
        print(f"panel fresh: {why} -- no-op")
        return 0
    last_spawn = st.get("last_spawn_attempt") or ""
    if last_spawn:
        try:
            elapsed = (now - dt.datetime.strptime(
                last_spawn, "%Y-%m-%d %H:%M:%S")).total_seconds()
            if elapsed < MIN_SPAWN_S:
                print(f"spawn throttled ({int(elapsed // 60)}min < "
                      f"{MIN_SPAWN_S // 60}min): {why}")
                return 0
        except Exception:
            pass
    write_status(last_spawn_attempt=now.strftime("%Y-%m-%d %H:%M:%S"),
                 run_target=target)
    spawn_fn()
    print(f"spawned detached refresh: {why}")
    return 0


# ---------------------------------------------------------------- selftest

def _selftest():
    fails = []

    def check(name, cond, detail=""):
        print(f"[{'PASS' if cond else 'FAIL'}] {name}"
              + (f" | {detail}" if detail and not cond else ""))
        if not cond:
            fails.append(name)

    # F1 exchange prefix
    check("F1 a_leg_symbol", a_leg_symbol("601318") == "sh601318"
          and a_leg_symbol("000002") == "sz000002"
          and a_leg_symbol("300750") == "sz300750"
          and a_leg_symbol("830799") is None
          and a_leg_symbol("12345") is None)

    # F2 date normalization (date obj / str / int passthrough form)
    check("F2 norm_date", norm_date(dt.date(2026, 9, 24)) == "2026-09-24"
          and norm_date("2026-09-24 15:00:00") == "2026-09-24"
          and norm_date(1740134400) == "1740134400")

    # F3 fx ffill (gap dates + pre-first drop)
    fx = [("2026-09-18", 0.860), ("2026-09-22", 0.859)]
    m = fx_ffill_map(fx, ["2026-09-17", "2026-09-18", "2026-09-19",
                          "2026-09-22"])
    check("F3 fx_ffill_map",
          m.get("2026-09-18") == 0.860 and m.get("2026-09-19") == 0.860
          and m.get("2026-09-22") == 0.859 and "2026-09-17" not in m)

    # F4 synthesize incl. slice-1 L7 sample numbers (frozen formula)
    a = [("2026-09-24", 53.25)]
    h = [("2026-09-24", 53.25)]
    rows, stats = synthesize_pair(a, h, {"2026-09-24": 0.86054})
    check("F4 synthesize L7 sample",
          abs(rows[0][4] - 0.16206103144537) < 1e-9
          and rows[0][0] == "2026-09-24" and stats["rows"] == 1)
    # gross premium guard fires
    try:
        synthesize_pair([("2026-09-24", 100.0)], [("2026-09-24", 1.0)],
                        {"2026-09-24": 0.86})
        check("F4b gross cap", False, "no exception raised")
    except ValueError:
        check("F4b gross cap", True)

    # F5 overlap verify (match + drift)
    local = [("2026-09-23", 53.87, 53.40, 0.86015, 0.17282043668)]
    new_ok = [("2026-09-23", 53.87, 53.40, 0.86015, 0.17282043668),
              ("2026-09-24", 53.25, 53.25, 0.86054, 0.16206103144)]
    ok, bad = overlap_verify(local, new_ok)
    drift = [("2026-09-23", 53.87, 53.40, 0.86015, 0.3)]
    ok2, bad2 = overlap_verify(local, drift)
    check("F5 overlap_verify", ok and not bad and not ok2 and bad2 == ["2026-09-23"])

    # F6 append-only tail
    tail = rows_to_append(local, new_ok)
    check("F6 rows_to_append", [r[0] for r in tail] == ["2026-09-24"]
          and rows_to_append([], new_ok) == new_ok)

    # F7 gate target (before/after HK safe hour, weekend)
    dates = [f"2026-09-{d:02d}" for d in range(18, 26)
             if d not in (19, 20, 26)]  # 18,21,22,23,24,25 (19/20=weekend)
    check("F7 gate_target",
          gate_target(dt.datetime(2026, 9, 25, 10, 0), dates) == "2026-09-24"
          and gate_target(dt.datetime(2026, 9, 25, 16, 30), dates) == "2026-09-25"
          and gate_target(dt.datetime(2026, 9, 26, 12, 0), dates) == "2026-09-25")

    # F8 gate freshness verdict
    need, _ = gate_needs_refresh({"complete": True, "cutoff": "2026-09-25"},
                                 "2026-09-25")
    need2, _ = gate_needs_refresh({"complete": True, "cutoff": "2026-09-24"},
                                  "2026-09-25")
    need3, _ = gate_needs_refresh({"complete": False, "cutoff": "2026-09-25"},
                                  "2026-09-25")
    check("F8 gate_needs_refresh", not need and need2 and need3)

    # F9 progress roll (target advance resets done, keeps attempts/quarantine)
    p9 = {"run_target": "2026-09-24", "done": ["02318"],
          "attempts": {"00700": 1}, "quarantined": {"03308": "x"}}
    r9 = progress_roll(p9, "2026-09-25")
    check("F9 progress_roll", r9["run_target"] == "2026-09-25"
          and r9["done"] == [] and r9["attempts"] == {"00700": 1}
          and r9["quarantined"] == {"03308": "x"}
          and progress_roll(p9, "2026-09-24") is p9)

    # F10 crosscheck verdict (pass / fail / deferred)
    v1, _ = crosscheck_verdict(0.1621, 16.5)
    v2, _ = crosscheck_verdict(0.1621, 80.0)
    v3, _ = crosscheck_verdict(0.1621, None)
    check("F10 crosscheck_verdict", v1 == "pass" and v2 == "fail"
          and v3 == "deferred")

    # F11 pair file roundtrip (header + append + read)
    test_h = "99999"
    p = pair_path(test_h)
    if os.path.exists(p):
        os.remove(p)
    append_pair_rows(test_h, [("2026-09-24", 1.0, 1.0, 0.86, 0.0)])
    append_pair_rows(test_h, [("2026-09-25", 2.0, 2.0, 0.86, 0.0)])
    back = read_pair_file(test_h)
    check("F11 pair file roundtrip", len(back) == 2
          and back[0][0] == "2026-09-24" and back[1][0] == "2026-09-25")
    os.remove(p)

    # F12 HSAHP shape guard / status json roundtrip via real files
    st = _read_json(STATUS) or {}
    check("F12 status readable", isinstance(st, dict))

    print(f"selftest: {len(fails)} fail" + ("s" if len(fails) != 1 else "")
          + f" / 12 groups")
    return 1 if fails else 0


def main(argv):
    if len(argv) < 2:
        return run_gate()
    cmd = argv[1]
    if cmd == "refresh":
        return run_refresh() or 0
    if cmd == "status":
        print(json.dumps(load_status(), ensure_ascii=False, indent=1))
        return 0
    if cmd == "selftest":
        return _selftest()
    print(f"unknown subcommand: {cmd} (gate default | refresh | status | "
          f"selftest)")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
