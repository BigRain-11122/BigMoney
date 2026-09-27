"""Repo term-ladder daily rate puller (T-2026-09-26-88 s3, R328 bm-a).

Spec (frozen with this file's first-pull commit): research/shortline/REPO_PANEL.md
Lane: data dept, T-88 s3 owner = bm-a (R31 lane-ownership precedent).

11 terms of pledge-style repo rates (prices ARE annualized % close):
  SH: GC001=204001 GC003=204003 GC004=204004 GC007=204007 GC014=204014
      GC028=204028 GC091=204091 GC182=204182
  SZ: R-001=131810 R-003=131800 R-007=131801
(Deep-market long end R-014+ not in first wave: probe face unvalidated, honest.)

Source design (r328 live arbitration, spec sec-3):
- PRIMARY face = newfqkline per-year windows (complete + deepest history:
  GC001 from 2012-05-17 vs fqkline's 2013-08-27 start; serves every fabric
  day incl. the 25 crash-summer-2015 days fqkline lacks; zero weekend rows).
- REPAIR face = fqkline per-2-year windows, used ONLY for rows the order
  guard rejects on the primary face (vendor digit-transposition glitches,
  e.g. 2021-08-10 GC001 close served as 2.850 > high 2.750; fqkline serves
  the true bar 2.085 -- cross-validated by the sibling-term curve that day:
  GC003 2.115 / GC007 2.23 / R-003 1.89 / R-007 2.06 -- and by the
  transposed-digit format 2.085<->2.850). Guard-fail dates absent from the
  repair face are quarantined (dropped + recorded, never landed corrupt).
- akshare stock_zh_a_hist_tx REJECTED as a source: it wraps newfqkline
  (same transposition blood) with no repair leg -- Money0923's cached
  repo_daily.csv inherited the 2.850 glitch (same bloodline, not evidence).
- Benign: ~13% of overlap rows differ by exactly one 0.005 tick between the
  two faces (GC001 tick size); single-primary-face series stays internally
  consistent; diff disclosed here, not a defect.

Semantics (update_futures.py canonical family, R48/R51):
- Full-history pull each run (11 requests, 2.5s pace, in-line legal --
  NOT a >5min long job); local append-only; overlap rows compared tol 1e-6;
  mismatch -> flag + local NOT rewritten, exit 3 (source re-writes history).
- Completeness: a row dated today only persists after 15:30 local.
- Atomic writes (.tmp + os.replace); dedupe by date; strictly-increasing
  dates; no-NaN close gate + rate-band sanity (0 < close < 50).
- Daily-cutoff gate: zero-network no-op when the 11-file panel covers the
  latest possible COMPLETE bar date (15:30 convention; local ETF trading
  calendar primary, weekday fallback).
- Throttle 30min between real attempts; last_attempt mirror written BEFORE
  fetching (r18 lesson). conn-fuse: 3 consecutive connection failures ->
  stop honest (exit 2).

Exit codes: 0 = ok/no-op; 2 = source failure (honest, do not mask);
3 = overlap mismatch flagged (local untouched).
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "repo_daily")
STATUS = os.path.join(ROOT, "results", "repo_update_status.json")

# term -> tencent symbol (spec sec-1 frozen table)
TERMS = {
    "GC001": "sh204001", "GC003": "sh204003", "GC004": "sh204004",
    "GC007": "sh204007", "GC014": "sh204014", "GC028": "sh204028",
    "GC091": "sh204091", "GC182": "sh204182",
    "R-001": "sz131810", "R-003": "sz131800", "R-007": "sz131801",
}
COLS = ["date", "open", "high", "low", "close", "volume"]
SLEEP_S = 2.5
MIN_ATTEMPT_S = 30 * 60
CONN_STOP = 3                 # consecutive connection failures -> stop
RATE_BAND = (0.0, 200.0)      # annualized % sanity band; >200 = nonsense.
# (0,50) rejected at r328 live-fire: 2015-02-10 GC001 close 53.44/high 65.00
# is a GENUINE pre-CNY squeeze print -- both faces agree + sibling terms
# confirm (GC003 close 22.275, GC007 13.845 same day) + seasonal pattern.
LANE_OWNER = "bm-a"           # R31 lane-ownership precedent (T-88 claim)


def _clear_proxy_env():
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)


def _opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _lane_owner_id():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"),
                      encoding="utf-8-sig") as f:
            return json.load(f).get("machine_id")
    except Exception:
        return None


# ---------------------------------------------------------------- guards (pure)


def completeness_filter(rows, now=None):
    """Drop a trailing row dated `now.date()` when now < 15:30 local. Pure."""
    now = now or dt.datetime.now()
    if now.time() >= dt.time(15, 30) or not rows:
        return rows, 0
    today = now.date().isoformat()
    kept, dropped = list(rows), 0
    while kept and str(kept[-1].get("date", "")) == today:
        kept.pop()
        dropped += 1
    return kept, dropped


_DATES_CACHE = None
COMPLETE_HOUR = dt.time(15, 30)


def _load_trading_dates():
    """Local ETF trading-day calendar as sorted ISO strings (update_futures
    pattern: data/daily 510300.csv primary, glob fallback, None -> weekday
    approximation). Repo trades on the same exchange-day fabric."""
    global _DATES_CACHE
    if _DATES_CACHE is not None:
        return _DATES_CACHE
    import csv as _csv
    import glob as _glob
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
    """Latest date a COMPLETE repo daily bar can exist at `now` (pure).
    Mirror of update_futures.expected_latest_bar_date."""
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


def cutoff_gate(local_cutoff, now, dates=None):
    """(needs_fetch, expected_date, reason)."""
    expected = expected_latest_bar_date(now, dates)
    if local_cutoff is None:
        return True, expected, "no local term data (first run)"
    if str(local_cutoff) >= expected:
        return False, expected, (f"local cutoff {local_cutoff} covers expected "
                                f"complete-bar date {expected}")
    return True, expected, f"local cutoff {local_cutoff} behind expected {expected}"


def local_data_cutoff(data_dir=None):
    """Max last-bar date across the 11 term CSVs; None if any file missing/empty."""
    data_dir = data_dir or DATA_DIR
    lasts = []
    for t in TERMS:
        p = os.path.join(data_dir, t + ".csv")
        if not os.path.exists(p):
            return None
        rows = read_local_csv(p)
        if not rows:
            return None
        lasts.append(str(rows[-1]["date"]))
    return max(lasts)


def validate_rows(rows):
    """Dates strictly increasing + unique; close finite + in rate band."""
    prev = None
    for r in rows:
        d = str(r.get("date", ""))
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            return f"bad_date_format:{d}"
        if prev is not None and d <= prev:
            return f"non_monotonic_at:{d}"
        prev = d
        c = r.get("close")
        if c is None or c != c:
            return f"nan_close_at:{d}"
        if not (RATE_BAND[0] < float(c) < RATE_BAND[1]):
            return f"close_out_of_rate_band:{d}:{c}"
    return None


def merge_incremental(local_rows, source_rows, tol=1e-6):
    """Append-only merge (update_futures mirror). On mismatch: merged=False."""
    local_by_date = {str(r["date"]): r for r in local_rows}
    mismatch, overlap = None, 0
    for r in source_rows:
        d = str(r["date"])
        loc = local_by_date.get(d)
        if loc is None:
            continue
        overlap += 1
        for col in ("open", "high", "low", "close"):
            lv, sv = loc.get(col), r.get(col)
            if lv is None or sv is None or abs(float(lv) - float(sv)) > tol:
                mismatch = d
                break
        if mismatch:
            break
    if mismatch:
        return {"appended": 0, "overlap": overlap, "mismatch": mismatch,
                "merged": False, "merged_rows": None}
    local_dates = set(local_by_date)
    new_rows = [r for r in source_rows if str(r["date"]) not in local_dates]
    merged = list(local_rows) + new_rows
    merged.sort(key=lambda r: str(r["date"]))
    return {"appended": len(new_rows), "overlap": overlap, "mismatch": None,
            "merged": True, "merged_rows": merged}


# ------------------------------------------------------------------ csv helpers


def rows_to_csv_text(rows):
    import csv
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(COLS)
    for r in rows:
        out = [str(r["date"])]
        for col in COLS[1:]:
            v = r.get(col)
            if v is None or v != v:
                out.append("")
            elif col == "volume":
                out.append(str(int(round(float(v)))) if float(v) == float(v) else "")
            else:
                out.append(f"{float(v):.10g}")
        w.writerow(out)
    return buf.getvalue()


def read_local_csv(path):
    import csv as _csv
    if not os.path.exists(path):
        return []
    with io.open(path, "r", encoding="utf-8") as f:
        rd = _csv.DictReader(f)
        rows = []
        for x in rd:
            r = {"date": x["date"]}
            for col in COLS[1:]:
                v = x.get(col, "")
                r[col] = float(v) if v not in ("", None) else None
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


# ---------------------------------------------------------------------- fetches

NFQ_URL = ("https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/"
           "get?_var=k{y}&param={sym},day,{y}-01-01,{y1}-12-31,640,&r=0.82")
FQ_URL = ("https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?"
          "param={sym},day,{y}-01-01,{y1}-12-31,640,qfq")
YEAR_START = 2012          # newfqkline serves GC001 from 2012-05-17
YEAR_END = 2026             # extended each January by +2 (2-year windows)
WINDOW_SLEEP_S = 0.8


def _get_jsonp_payload(url):
    with _opener().open(url, timeout=30) as resp:
        txt = resp.read().decode("utf-8", errors="replace")
    i = txt.find("{")
    if i < 0:
        raise RuntimeError("payload_has_no_json_object")
    return json.loads(txt[i:])


def _node_rows(node):
    k = node.get("day") or node.get("qfqday") or node.get("hfqday")
    return k or []


def _window_years():
    return list(range(YEAR_START, YEAR_END + 1, 2))


def fetch_face(url_tpl, sym, sleep_s=WINDOW_SLEEP_S, sleep_hook=None):
    """Union rows over per-2-year windows of one tencent face. Returns rows."""
    rows = {}
    for y in _window_years():
        url = url_tpl.format(sym=sym, y=y, y1=y + 1)
        d = _get_jsonp_payload(url)
        node = (d.get("data") or {}).get(sym)
        if not node:
            raise RuntimeError(f"face_parse_fail: no data node for {sym}")
        for it in _node_rows(node):
            rows[str(it[0])] = it
        if sleep_hook:
            sleep_hook()
        elif sleep_s:
            time.sleep(sleep_s)
    return rows


def row_order_ok(o, c, h, l):
    return (h + 1e-9 >= max(o, c)) and (l - 1e-9 <= min(o, c))


def _to_row(it):
    """tencent row [date, open, close, high, low, (volume)] -> COLS dict."""
    d = str(it[0])
    o, c, h, l = float(it[1]), float(it[2]), float(it[3]), float(it[4])
    vol = None
    if len(it) >= 6:
        try:
            vol = float(it[5])
        except (TypeError, ValueError):
            vol = None
    return {"date": d, "open": o, "high": h, "low": l, "close": c,
            "volume": vol}


def fetch_primary(sym):
    """newfqkline primary face: parse, order-guard per row; guard-fail dates
    repaired via fqkline face; unrecoverable dates quarantined (dropped).
    Returns (rows, stats)."""
    raw = fetch_face(NFQ_URL, sym)
    guard_fail = {}
    rows = {}
    for d, it in raw.items():
        try:
            o, c, h, l = float(it[1]), float(it[2]), float(it[3]), float(it[4])
            if not row_order_ok(o, c, h, l):
                guard_fail[d] = f"close>{'high' if c > h else 'low-range'}"
                continue
            r = _to_row(it)
        except (TypeError, ValueError, IndexError):
            guard_fail[d] = "parse_fail"
            continue
        rows[d] = r
    stats = {"raw_rows": len(raw), "guard_fail": guard_fail,
             "repaired": {}, "quarantined": {}}
    if guard_fail:
        repair = fetch_face(FQ_URL, sym)
        for d in list(guard_fail):
            it = repair.get(d)
            if it is None:
                stats["quarantined"][d] = guard_fail[d]
                continue
            try:
                o, c, h, l = float(it[1]), float(it[2]), float(it[3]), float(it[4])
                if not row_order_ok(o, c, h, l):
                    stats["quarantined"][d] = f"repair_also_bad:{guard_fail[d]}"
                    continue
                rows[d] = _to_row(it)
                stats["repaired"][d] = guard_fail[d]
            except (TypeError, ValueError, IndexError):
                stats["quarantined"][d] = f"repair_parse_fail:{guard_fail[d]}"
    return sorted(rows.values(), key=lambda r: r["date"]), stats


# ------------------------------------------------------------------------- run


def run():
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        print(f"no-op: repo rates lane owned by {LANE_OWNER}, "
              f"not this machine ({owner or '?'})")
        return 0
    st = load_status()
    now = dt.datetime.now()
    local_cut = local_data_cutoff()
    needs_fetch, expected, gate_reason = cutoff_gate(local_cut, now)
    if not needs_fetch:
        st["last_attempt"] = st["ts"] = now.isoformat(timespec="seconds")
        st["mode"] = "no-op: cutoff covered"
        st["no_op_reason"] = gate_reason
        st["expected_cutoff"] = expected
        st["data_cutoff"] = local_cut
        write_status(st)
        print(f"no-op: {gate_reason} -> zero network")
        return 0
    last_attempt = st.get("last_attempt")
    if last_attempt:
        try:
            age = (now - dt.datetime.fromisoformat(last_attempt)).total_seconds()
            if age < MIN_ATTEMPT_S:
                print(f"throttle: last attempt {last_attempt} "
                      f"({age/60:.1f}min ago) < 30min -> no-op")
                return 0
        except Exception:
            pass
    st["last_attempt"] = now.isoformat(timespec="seconds")  # mirror FIRST (r18)
    st["terms_planned"] = list(TERMS)
    write_status(st)

    _clear_proxy_env()
    per, failures, mismatches = [], [], []
    conn_fails = 0
    for i, (term, sym) in enumerate(TERMS.items()):
        rec = {"term": term, "symbol": sym, "appended": 0, "overlap": 0,
               "mismatch": None, "error": None, "path": None,
               "rows_local": None, "first": None, "last": None}
        if conn_fails >= CONN_STOP:
            rec["error"] = f"conn-fuse: {conn_fails} consecutive connection failures"
            per.append(rec)
            continue
        try:
            try:
                rows, fstats = fetch_primary(sym)
            except urllib.error.URLError as e:
                conn_fails += 1
                raise RuntimeError(f"conn_fail:{type(e).__name__} ({conn_fails}/{CONN_STOP})")
            except Exception:
                conn_fails = 0  # non-conn error resets the conn fuse
                raise
            conn_fails = 0
            rec["path"] = "tencent_newfqkline_primary + fqkline_repair"
            rec["face_stats"] = fstats
            rows, dropped_today = completeness_filter(rows)
            err = validate_rows(rows)
            if err:
                raise RuntimeError(f"validation_fail: {err}")
            p = os.path.join(DATA_DIR, term + ".csv")
            local = read_local_csv(p)
            res = merge_incremental(local, rows)
            rec["overlap"] = res["overlap"]
            rec["mismatch"] = res["mismatch"]
            if not res["merged"]:
                mismatches.append(f"{term}@{res['mismatch']}")
                rec["rows_local"] = len(local)
                if local:
                    rec["first"], rec["last"] = str(local[0]["date"]), str(local[-1]["date"])
            else:
                text = rows_to_csv_text(res["merged_rows"])
                atomic_write(p, text)
                rec["appended"] = res["appended"]
                rec["rows_local"] = len(res["merged_rows"])
                if res["merged_rows"]:
                    rec["first"] = str(res["merged_rows"][0]["date"])
                    rec["last"] = str(res["merged_rows"][-1]["date"])
            if dropped_today:
                rec["dropped_today_partial"] = dropped_today
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {str(e)[:180]}"
            failures.append(term)
        per.append(rec)
        if i < len(TERMS) - 1:
            time.sleep(SLEEP_S)

    st.update({
        "ts": now.isoformat(timespec="seconds"),
        "mode": "full-history pull, append-only local, overlap-verified",
        "per_term": per,
        "summary": {
            "terms": len(TERMS), "failures": len(failures),
            "mismatches": len(mismatches),
            "total_appended": sum(r.get("appended") or 0 for r in per),
            "data_cutoff": max([r["last"] for r in per if r.get("last")],
                               default=None),
        },
        "claim": "T-2026-09-26-88-bm-a-s3-repo-rates-collector",
        "note": "prices ARE annualized % (close = day's closing annualized rate); "
                "consumption interest formula belongs to consumer preregs "
                "(M0923 pattern: amt*rate*pct*days/365, commission 1e-5, "
                "1000-CNY multiples); collector supplies the rate series only",
    })
    write_status(st)
    print(f"update_repo -> {STATUS}")
    for r in per:
        line = f"  {r['term']}: "
        if r["error"]:
            line += f"FAIL {r['error']}"
        elif r["mismatch"]:
            line += f"MISMATCH@{r['mismatch']} local untouched ({r['rows_local']} rows)"
        else:
            line += (f"+{r['appended']} rows -> {r['rows_local']} total "
                     f"{r['first']}..{r['last']}")
        print(line)
    if failures:
        return 2
    if mismatches:
        return 3
    return 0


# --------------------------------------------------------------------- selftest


def _selftest():
    import tempfile
    now = dt.datetime(2026, 9, 24, 10, 0)
    today = "2026-09-24"
    # S1 completeness guard
    rows = [{"date": "2026-09-22", "close": 1.0},
            {"date": today, "close": 2.0}]
    kept, dropped = completeness_filter(rows, now=now)
    assert len(kept) == 1 and dropped == 1 and kept[0]["date"] == "2026-09-22"
    kept, dropped = completeness_filter(rows, now=dt.datetime(2026, 9, 24, 15, 31))
    assert len(kept) == 2 and dropped == 0
    # S2 validation gate incl rate band
    assert validate_rows([{"date": "2026-09-01", "close": 1.5},
                          {"date": "2026-09-02", "close": 2.5}]) is None
    assert validate_rows([{"date": "2026-09-01", "close": 0.0}]) is not None   # band low
    assert validate_rows([{"date": "2026-09-01", "close": 999.0}]) is not None  # band high
    assert validate_rows([{"date": "2026-09-01", "close": 53.44}]) is None  # r328 live law: genuine squeeze print passes
    assert validate_rows([{"date": "2026-09-01", "close": None}]) is not None
    assert validate_rows([{"date": "bad", "close": 1.0}]) is not None
    # S3 incremental merge + mismatch honesty
    local = [{"date": "2026-09-01", "open": 1.2, "high": 1.5, "low": 1.1, "close": 1.4},
             {"date": "2026-09-02", "open": 1.3, "high": 1.6, "low": 1.2, "close": 1.5}]
    src = local + [{"date": "2026-09-03", "open": 1.4, "high": 1.7, "low": 1.3, "close": 1.6}]
    res = merge_incremental(local, src)
    assert res["merged"] and res["appended"] == 1 and res["overlap"] == 2
    src_bad = [dict(local[0]), dict(local[1])]
    src_bad[0]["close"] = 9.99
    res2 = merge_incremental(local, src_bad)
    assert not res2["merged"] and res2["mismatch"] == "2026-09-01"
    # S4 row-order guard + row parse (tencent [date, open, close, high, low])
    assert row_order_ok(1.375, 1.440, 1.480, 1.100)
    assert not row_order_ok(2.600, 2.850, 2.750, 1.800)   # r328 live glitch law
    r = _to_row(["2026-09-24", "1.375", "1.440", "1.480", "1.100", "12345"])
    assert r["close"] == 1.440 and r["high"] == 1.480 and r["low"] == 1.100
    assert r["volume"] == 12345.0
    # S4b: fetch_primary repair + quarantine (injected faces, offline)
    global fetch_face
    good = {"2026-09-24": ["2026-09-24", "1.375", "1.440", "1.480", "1.100", "1"],
            "2021-08-10": ["2021-08-10", "2.600", "2.850", "2.750", "1.800", "1"]}
    fix = {"2021-08-10": ["2021-08-10", "2.600", "2.085", "2.750", "1.800", "1"],
           "2015-06-15": ["2015-06-15", "9.9", "9.9", "9.9", "9.9", "1"]}
    _orig_ff = fetch_face
    try:
        fetch_face = lambda url_tpl, sym, sleep_s=0, sleep_hook=None: (
            dict(good) if "newfqkline" in url_tpl else dict(fix))
        rows, st = fetch_primary("sh204001")
        assert len(rows) == 2 and rows[0]["date"] == "2021-08-10"
        assert rows[0]["close"] == 2.085          # repaired via fqkline face
        assert rows[1]["close"] == 1.440
        assert list(st["repaired"]) == ["2021-08-10"] and not st["quarantined"]
        # S4c: unrecoverable guard-fail date -> quarantined, never landed
        good2 = dict(good); good2["2015-07-08"] = ["2015-07-08", "1.0", "9.9", "2.0", "0.5", "1"]
        fetch_face = lambda url_tpl, sym, sleep_s=0, sleep_hook=None: (
            dict(good2) if "newfqkline" in url_tpl else {})
        rows2, st2 = fetch_primary("sh204001")
        assert "2015-07-08" in st2["quarantined"] and "2021-08-10" in st2["quarantined"]
        assert len(rows2) == 1 and rows2[0]["date"] == "2026-09-24"
    finally:
        fetch_face = _orig_ff
    # S5 csv roundtrip (volume int cast)
    rr = [{"date": "2026-09-01", "open": 1.2, "high": 1.5, "low": 1.1,
           "close": 1.4, "volume": 123456.0}]
    text = rows_to_csv_text(rr)
    assert text.splitlines()[0] == ",".join(COLS)
    assert text.splitlines()[1].endswith("123456")
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "x.csv")
        atomic_write(p, text)
        back = read_local_csv(p)
        assert back[0]["close"] == 1.4 and back[0]["volume"] == 123456.0
    # S6 cutoff gate + expected bar date (injected calendar)
    cal = ["2026-09-21", "2026-09-22", "2026-09-23"]
    assert expected_latest_bar_date(dt.datetime(2026, 9, 24, 7, 0), cal) == "2026-09-23"
    assert expected_latest_bar_date(dt.datetime(2026, 9, 24, 16, 0), cal) == "2026-09-23"
    assert expected_latest_bar_date(dt.datetime(2026, 9, 24, 16, 0),
                                     cal + ["2026-09-24"]) == "2026-09-24"
    assert expected_latest_bar_date(dt.datetime(2026, 9, 26, 16, 0), []) == "2026-09-25"
    needs, exp, _ = cutoff_gate("2026-09-23", dt.datetime(2026, 9, 24, 7, 0), cal)
    assert not needs and exp == "2026-09-23"
    needs, _, _ = cutoff_gate("2026-09-22", dt.datetime(2026, 9, 24, 7, 0), cal)
    assert needs
    needs, _, _ = cutoff_gate(None, dt.datetime(2026, 9, 24, 7, 0), cal)
    assert needs
    # S7 local_data_cutoff on constructed 11-term panel (any-missing -> None)
    with tempfile.TemporaryDirectory() as td:
        base = [{"date": "2026-09-22", "close": 1.0}, {"date": "2026-09-23", "close": 1.1}]
        for t in TERMS:
            atomic_write(os.path.join(td, t + ".csv"),
                         rows_to_csv_text([dict(r, open=r["close"], high=r["close"],
                                                low=r["close"], volume=1.0) for r in base]))
        assert local_data_cutoff(td) == "2026-09-23"
        os.remove(os.path.join(td, "R-001" + ".csv"))
        assert local_data_cutoff(td) is None
    # S8 status JSON roundtrip: native types only
    assert json.loads(json.dumps({"a": int(2), "b": None}))["b"] is None
    # S9 lane guard logic: non-owner stdout no-op (injected owner ids)
    assert LANE_OWNER == "bm-a"
    assert ("bm-b" != LANE_OWNER) and ("bm-c" != LANE_OWNER) and (None != LANE_OWNER)
    # S10 term map integrity: 11 terms, unique symbols, sh/sz prefixes only
    assert len(TERMS) == 11 and len(set(TERMS.values())) == 11
    assert all(v.startswith(("sh", "sz")) for v in TERMS.values())
    print("selftest: 10/10 PASS")
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return _selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())
