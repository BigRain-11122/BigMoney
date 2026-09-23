#!/usr/bin/env python
# -*- coding: ascii -*-
"""backfill_ext_slots.py -- P-1d extension-slot raw pulls (one-shot backfill).

Slots (research/shortline/P1D_EXT_SLOTS_IC.md, frozen prereg):
  dzjy   block-trade details per month range (stock_dzjy_mrmx, A-share,
         5000-row page cap -> recursive bisection on cap hit)
  gdhs   holder-number quarterly snapshots (stock_zh_a_gdhs, 2015Q3..2026Q2)
  margin daily margin details per trading day, per-month parquet buffers
         (stock_margin_detail_sse + stock_margin_detail_szse, 2010-03-31+;
         trading calendar derived from Money02 bars 600000.parquet)

Discipline (P-1d prereg sec5): >=2.5s throttle between requests, retry w/
backoff, consecutive-5-failure fuse (abort leg, keep checkpoints for resume),
sequential legs only (EM datacenter-web citizen duty), checkpoint = chunk
file existence, status ledger results/ext_slots_pull_status.json.

Exit codes: 0 = done or all-chunks-already-complete; 2 = source failure
(fuse hit or leg aborted) -- report as-is, never mask; selftest subcommand
runs offline with zero network.

Usage:
  python scripts/backfill_ext_slots.py dzjy|gdhs|margin|all|status|selftest
"""
import json
import os
import sys
import time

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "ext_slots")
STATUS_PATH = os.path.join(ROOT, "results", "ext_slots_pull_status.json")
BARS_CALENDAR = os.path.join(ROOT, "Money02", "data", "bars", "600000.parquet")

THROTTLE_SEC = 2.5
MAX_CONSEC_FAIL = 5
RETRY_BACKOFF = [2.0, 8.0, 20.0]
DZJY_PAGE_CAP = 5000

_LAST_REQ = [0.0]


def _now_iso():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _throttle():
    wait = THROTTLE_SEC - (time.time() - _LAST_REQ[0])
    if wait > 0 and _LAST_REQ[0] > 0:
        time.sleep(wait)
    _LAST_REQ[0] = time.time()


def _load_status():
    if os.path.exists(STATUS_PATH):
        with open(STATUS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"legs": {}, "updated": None}


def _save_status(st):
    st["updated"] = _now_iso()
    tmp = STATUS_PATH + ".tmp"
    os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATUS_PATH)


def _fetch(ak, fn_name, *args, **kwargs):
    """Fetch with throttle + retry/backoff. Returns (df, err_str)."""
    fn = getattr(ak, fn_name)
    last_err = None
    for attempt, backoff in enumerate([0.0] + RETRY_BACKOFF):
        if backoff:
            time.sleep(backoff)
        _throttle()
        try:
            df = fn(*args, **kwargs)
            if df is None:
                return None, "returned None"
            return df, None
        except Exception as e:
            last_err = "%s: %s" % (type(e).__name__, str(e)[:160])
    return None, last_err


# ---------------------------------------------------------------- calendars
def month_ranges(start_y, start_m, end_y, end_m):
    """List of (ym_int, start_str, end_str) covering [start, end] inclusive."""
    out = []
    y, m = start_y, start_m
    while (y, m) <= (end_y, end_m):
        ym = y * 100 + m
        if m == 12:
            nxt = (y + 1) * 100 + 1
        else:
            nxt = y * 100 + m + 1
        # last day of month = day before next month's 1st
        import datetime as _dt
        last = _dt.date(nxt // 100, nxt % 100, 1) - _dt.timedelta(days=1)
        out.append((ym, "%04d%02d01" % (y, m), "%04d%02d%02d" % (y, m, last.day)))
        m += 1
        if m == 13:
            m, y = 1, y + 1
    return out


def quarter_ends(start_y, start_q, end_y, end_q):
    out = []
    y, q = start_y, start_q
    month_of = {1: 3, 2: 6, 3: 9, 4: 12}
    day_of = {1: 31, 2: 30, 3: 30, 4: 31}
    while (y, q) <= (end_y, end_q):
        out.append("%04d%02d%02d" % (y, month_of[q], day_of[q]))
        q += 1
        if q == 5:
            q, y = 1, y + 1
    return out


def trading_calendar(start_date, end_date):
    """SSE trading days from Money02 bars 600000.parquet date axis."""
    df = pd.read_parquet(BARS_CALENDAR, columns=["date"])
    dates = pd.to_datetime(df["date"]).dt.strftime("%Y%m%d")
    return [d for d in dates if start_date <= d <= end_date]


# ------------------------------------------------------------------- dzjy
def pull_dzjy(ak, st, log):
    """Pull A-share block-trade details month by month; bisect on page cap."""
    leg = st["legs"].setdefault("dzjy", {"chunks": 0, "rows": 0, "failures": [], "done": True})
    outdir = os.path.join(DATA_DIR, "dzjy")
    os.makedirs(outdir, exist_ok=True)
    months = month_ranges(2013, 1, 2026, 9)
    consec_fail = 0
    for ym, s, e in months:
        path = os.path.join(outdir, "mrmx_%06d.parquet" % ym)
        marker = os.path.join(outdir, "mrmx_%06d.done.json" % ym)
        if os.path.exists(path) or os.path.exists(marker):
            continue
        rows = _dzjy_pull_range(ak, ym, s, e, outdir, log)
        if rows < 0:
            leg["failures"].append({"month": ym, "error": "range-failed"})
            consec_fail += 1
            if consec_fail >= MAX_CONSEC_FAIL:
                leg["done"] = False
                _save_status(st)
                log("FUSE: %d consecutive failures, aborting dzjy leg" % consec_fail)
                return 2
            continue
        consec_fail = 0
        with open(marker, "w", encoding="utf-8") as f:
            json.dump({"month": ym, "rows": rows, "ts": _now_iso()}, f)
        leg["chunks"] += 1
        leg["rows"] += rows
        _save_status(st)
    log("dzjy leg complete: %d chunks, %d rows" % (leg["chunks"], leg["rows"]))
    return 0


def _dzjy_pull_range(ak, ym, s, e, outdir, log):
    """Pull [s, e] recursively; on 5000-cap hit split in half. Returns rows or -1."""
    df, err = _fetch(ak, "stock_dzjy_mrmx", symbol="A\u80a1", start_date=s, end_date=e)
    if df is None:
        log("dzjy %d [%s..%s] fetch error: %s" % (ym, s, e, err))
        return -1
    if len(df) == DZJY_PAGE_CAP:
        import datetime as _dt
        d1 = _dt.datetime.strptime(s, "%Y%m%d")
        d2 = _dt.datetime.strptime(e, "%Y%m%d")
        if (d2 - d1).days >= 1:
            mid = d1 + (d2 - d1) / 2
            r1 = _dzjy_pull_range(ak, ym, s, mid.strftime("%Y%m%d"), outdir, log)
            r2 = _dzjy_pull_range(ak, ym, _next_day(mid), e, outdir, log)
            if r1 < 0 or r2 < 0:
                return -1
            return r1 + r2
        # single day hitting the cap: source hard-truncates, record honestly
        log("dzjy %d single-day cap hit (%s), truncated record kept" % (ym, s))
    tag = "%06d" % ym if s == "%04d%02d01" % (ym // 100, ym % 100) else "%s_%s" % (s, e)
    path = os.path.join(outdir, "mrmx_%s.parquet" % tag)
    df.to_parquet(path)
    return len(df)


def _next_day(d):
    import datetime as _dt
    return (d + _dt.timedelta(days=1)).strftime("%Y%m%d")


# ------------------------------------------------------------------- gdhs
def pull_gdhs(ak, st, log):
    leg = st["legs"].setdefault("gdhs", {"chunks": 0, "rows": 0, "failures": [], "done": True})
    outdir = os.path.join(DATA_DIR, "gdhs")
    os.makedirs(outdir, exist_ok=True)
    quarters = quarter_ends(2015, 3, 2026, 2)
    consec_fail = 0
    for q in quarters:
        path = os.path.join(outdir, "gdhs_%s.parquet" % q)
        if os.path.exists(path):
            continue
        df, err = _fetch(ak, "stock_zh_a_gdhs", symbol=q)
        if df is None:
            leg["failures"].append({"quarter": q, "error": err})
            consec_fail += 1
            if consec_fail >= MAX_CONSEC_FAIL:
                leg["done"] = False
                _save_status(st)
                log("FUSE: aborting gdhs leg at %s" % q)
                return 2
            continue
        consec_fail = 0
        df.to_parquet(path)
        leg["chunks"] += 1
        leg["rows"] += len(df)
        _save_status(st)
    log("gdhs leg complete: %d quarters, %d rows" % (leg["chunks"], leg["rows"]))
    return 0


# ------------------------------------------------------------------ margin
def pull_margin(ak, st, log):
    leg = st["legs"].setdefault("margin", {"chunks": 0, "rows": 0, "failures": [], "done": True,
                                           "empty_days": 0, "empty_days_list": []})
    outdir = os.path.join(DATA_DIR, "margin")
    os.makedirs(outdir, exist_ok=True)
    cal = trading_calendar("20100331", "20260922")
    by_month = {}
    for d in cal:
        by_month.setdefault(d[:6], []).append(d)
    consec_fail = 0
    for ym, days in sorted(by_month.items()):
        path_sse = os.path.join(outdir, "sse_%s.parquet" % ym)
        path_szse = os.path.join(outdir, "szse_%s.parquet" % ym)
        buf_sse, buf_szse = [], []
        need = not (os.path.exists(path_sse) and os.path.exists(path_szse))
        if not need:
            continue
        month_ok = True
        for d in days:
            if not os.path.exists(path_sse):
                df, err = _fetch(ak, "stock_margin_detail_sse", date=d)
                if df is None:
                    leg["failures"].append({"date": d, "ex": "sse", "error": err})
                    consec_fail += 1
                    if consec_fail >= MAX_CONSEC_FAIL:
                        leg["done"] = False
                        _save_status(st)
                        log("FUSE: aborting margin leg at %s (sse)" % d)
                        return 2
                    month_ok = False
                    break
                consec_fail = 0
                if len(df) == 0:
                    leg["empty_days"] += 1
                    if len(leg["empty_days_list"]) < 400:
                        leg["empty_days_list"].append(d)
                else:
                    df = df.copy()
                    df["trade_date"] = d
                    buf_sse.append(df)
            if not os.path.exists(path_szse):
                df, err = _fetch(ak, "stock_margin_detail_szse", date=d)
                if df is None:
                    leg["failures"].append({"date": d, "ex": "szse", "error": err})
                    consec_fail += 1
                    if consec_fail >= MAX_CONSEC_FAIL:
                        leg["done"] = False
                        _save_status(st)
                        log("FUSE: aborting margin leg at %s (szse)" % d)
                        return 2
                    month_ok = False
                    break
                consec_fail = 0
                if len(df) > 0:
                    df = df.copy()
                    df["trade_date"] = d
                    buf_szse.append(df)
        if not month_ok:
            continue  # month retried next resume
        if buf_sse:
            pd.concat(buf_sse, ignore_index=True).to_parquet(path_sse)
        elif not os.path.exists(path_sse):
            pd.DataFrame({"trade_date": days}).to_parquet(path_sse)  # honest empty month
        if buf_szse:
            pd.concat(buf_szse, ignore_index=True).to_parquet(path_szse)
        elif not os.path.exists(path_szse):
            pd.DataFrame({"trade_date": days}).to_parquet(path_szse)
        leg["chunks"] += 1
        leg["rows"] += sum(len(x) for x in buf_sse) + sum(len(x) for x in buf_szse)
        _save_status(st)
    log("margin leg complete: %d months, %d rows" % (leg["chunks"], leg["rows"]))
    return 0


# ------------------------------------------------------------------ misc
def cmd_status():
    st = _load_status()
    print(json.dumps(st, ensure_ascii=False, indent=1))
    counts = {}
    for slot in ("dzjy", "gdhs", "margin"):
        d = os.path.join(DATA_DIR, slot)
        counts[slot] = len(os.listdir(d)) if os.path.isdir(d) else 0
    print("files:", counts)


def cmd_selftest():
    ok = True

    def check(name, cond):
        res = bool(cond)
        print("[%s] %s" % ("PASS" if res else "FAIL", name))
        return res

    m = month_ranges(2013, 1, 2013, 3)
    ok &= check("month_ranges head", m[0] == (201301, "20130101", "20130131") and m[-1] == (201303, "20130301", "20130331"))
    m2 = month_ranges(2025, 11, 2026, 2)
    ok &= check("month_ranges year wrap", len(m2) == 4 and m2[2][0] == 202601 and m2[2][1] == "20260101" and m2[0][2] == "20251130" and m2[1][2] == "20251231")
    q = quarter_ends(2015, 3, 2016, 2)
    ok &= check("quarter_ends", q == ["20150930", "20151231", "20160331", "20160630"])
    q2 = quarter_ends(2025, 4, 2026, 2)
    ok &= check("quarter_ends wrap", q2 == ["20251231", "20260331", "20260630"])
    # status roundtrip on a TEMP path (never clobber the real status ledger)
    global STATUS_PATH
    real_status = STATUS_PATH
    tmp_status = os.path.join(DATA_DIR, "_selftest_status.json")
    STATUS_PATH = tmp_status
    _save_status({"legs": {"t": {"chunks": 1}}})
    st2 = _load_status()
    ok &= check("status roundtrip", st2["legs"]["t"]["chunks"] == 1 and st2["updated"])
    os.remove(tmp_status)
    STATUS_PATH = real_status
    # calendar derivation (local, no network)
    cal = trading_calendar("20100331", "20100430")
    ok &= check("calendar 2010-03 window nonempty", len(cal) >= 15 and cal[0] >= "20100331")
    ok &= check("calendar excludes weekend", "20100403" not in cal and "20100404" not in cal and "20100401" in cal and "20100430" in cal)
    print("selftest: %s" % ("ALL PASS" if ok else "FAIL"))
    return 0 if ok else 3


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "selftest":
        sys.exit(cmd_selftest())
    if cmd == "status":
        cmd_status()
        sys.exit(0)
    if cmd not in ("dzjy", "gdhs", "margin", "all"):
        print(__doc__)
        sys.exit(1)

    def log(msg):
        print("[%s] %s" % (_now_iso(), msg), flush=True)

    import akshare as ak  # import deferred: selftest stays offline/zero-net

    st = _load_status()
    rc = 0
    if cmd in ("dzjy", "all"):
        rc = pull_dzjy(ak, st, log) or rc
    if cmd in ("gdhs", "all"):
        rc = pull_gdhs(ak, st, log) or rc
    if cmd in ("margin", "all"):
        rc = pull_margin(ak, st, log) or rc
    _save_status(st)
    sys.exit(rc if rc else 0)


if __name__ == "__main__":
    main()
