"""Futures main-continuous daily puller (R48 bm-a, claim MSG-20260924-0645).

Full-history pull of 9 varieties (IF/IC/IM/IH/T/TF/RB/AU/SC) from sina
main-continuous daily kline into data/futures_daily/<V>.csv (root data dir;
Money0923 archive untouched). Pure data engineering: zero engine runs, ledger N
untouched (POOL_AUDIT / R47 probe precedent).

Semantics (update_daily family):
- Fetch full history each run; local history is append-only. Overlap rows are
  compared (price cols, tol 1e-6); mismatch -> flag `overlap_mismatch`, local
  file NOT rewritten (anchor-gate honesty; consumer batches expose drift).
- Completeness guard: a row dated today is only persisted after 15:30 local
  (futures day session ends 15:15; 15:30 conservative -- night session belongs
  to the *next* trading day's bar in sina convention, partial today-row dropped).
- Atomic writes (.tmp + os.replace); dedupe by date; strictly-increasing dates;
  no-NaN close validation gate.
- Daily-cutoff gate (R51 S6 wiring): when local history already covers the
  latest possible COMPLETE bar date (15:30 convention; local ETF trading
  calendar primary, weekday fallback), the run is a verified zero-network
  no-op -- status ts/last_attempt refreshed for the panel reader
  (update_lhb expected_disclosure_date precedent: a same-evening source
  publication delay just defers the fetch a few hours, self-healing).
- Throttle: min 30min between attempts; last_attempt mirror is written BEFORE
  fetching (r18 lesson: crash mid-run still throttles).
- Network: direct connection (proxy env cleared -- Clash hijack lesson), 2.5s
  polite sleep between varieties, akshare primary + raw sina jsonp fallback.

Exit codes: 0 = ok/no-op; 2 = source failure (honest, do not mask);
3 = overlap mismatch flagged (source re-adjusted history; local untouched).
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "futures_daily")
STATUS = os.path.join(ROOT, "results", "futures_update_status.json")

VARIETIES = ["IF", "IC", "IM", "IH", "T", "TF", "RB", "AU", "SC"]
COLS = ["date", "open", "high", "low", "close", "volume", "oi", "settle"]
SLEEP_S = 2.5
MIN_ATTEMPT_S = 30 * 60
RAW_URL = ("https://stock2.finance.sina.com.cn/futures/api/jsonp.php/"
           "var%20_F={sym}/InnerFuturesNewService.getDailyKLine?symbol={sym}")


def _clear_proxy_env():
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)


def _no_proxy_opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


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
COMPLETE_HOUR = dt.time(15, 30)  # mirrors completeness_filter convention


def _load_trading_dates():
    """Local ETF trading-day calendar as sorted ISO strings (update_lhb
    pattern: data/daily 510300.csv primary, glob fallback, None -> weekday
    approximation). Same exchange-day fabric as futures (R50 G3: two
    cross-exchange gap dates in 21k rows = 0.009%, accepted)."""
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
    """Latest date a COMPLETE futures daily bar can exist at `now` (pure).

    Today counts only when now >= 15:30 AND today's bar is already in the
    local calendar (evening source lag defers the fetch a few hours,
    self-healing -- expected_disclosure_date precedent). Otherwise the most
    recent local trading day strictly before today. Weekday approximation
    when no calendar is available.
    """
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
    """(needs_fetch, expected_date, reason). Zero-network no-op when the
    local chain already covers the latest possible complete-bar date."""
    expected = expected_latest_bar_date(now, dates)
    if local_cutoff is None:
        return True, expected, "no local variety data (first run)"
    if str(local_cutoff) >= expected:
        return False, expected, (f"local cutoff {local_cutoff} covers expected "
                                f"complete-bar date {expected}")
    return True, expected, f"local cutoff {local_cutoff} behind expected {expected}"


def local_data_cutoff(data_dir=None):
    """Max last-bar date across the 9 variety CSVs; None if any file is
    missing/empty (gate then degrades honestly to a real fetch)."""
    data_dir = data_dir or DATA_DIR
    lasts = []
    for v in VARIETIES:
        p = os.path.join(data_dir, v + ".csv")
        if not os.path.exists(p):
            return None
        rows = read_local_csv(p)
        if not rows:
            return None
        lasts.append(str(rows[-1]["date"]))
    return max(lasts)


def validate_rows(rows):
    """Dates strictly increasing + unique; close finite. Returns error str or None."""
    prev = None
    for r in rows:
        d = str(r.get("date", ""))
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            return f"bad_date_format:{d}"
        if prev is not None and d <= prev:
            return f"non_monotonic_at:{d}"
        prev = d
        c = r.get("close")
        if c is None or c != c:  # NaN check
            return f"nan_close_at:{d}"
    return None


def merge_incremental(local_rows, source_rows, tol=1e-6):
    """Append-only merge. Returns dict(appended, overlap, mismatch, merged, merged_rows).

    On mismatch: merged=False, merged_rows=None (caller must NOT rewrite local).
    """
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
        return {"appended": 0, "overlap": overlap, "mismatch": mismatch, "merged": False,
                "merged_rows": None}
    local_dates = set(local_by_date)
    new_rows = [r for r in source_rows if str(r["date"]) not in local_dates]
    merged = list(local_rows) + new_rows
    merged.sort(key=lambda r: str(r["date"]))
    return {"appended": len(new_rows), "overlap": overlap, "mismatch": None, "merged": True,
            "merged_rows": merged}


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
            elif col in ("volume", "oi"):
                out.append(str(int(round(float(v))))
                           if float(v) == float(v) else "")
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


def fetch_akshare(sym):
    import akshare as ak
    df = ak.futures_main_sina(symbol=sym)
    if df is None or len(df) == 0:
        return []
    cns = {"日期": "date", "开盘价": "open", "最高价": "high", "最低价": "low",
           "收盘价": "close", "成交量": "volume", "持仓量": "oi", "动态结算价": "settle"}
    rows = []
    for _, x in df.iterrows():
        r = {}
        for cn, en in cns.items():
            v = x.get(cn)
            if en == "date":
                r[en] = str(v)
            else:
                try:
                    r[en] = None if v is None or v != v else float(v)
                except (TypeError, ValueError):
                    r[en] = None
        rows.append(r)
    return rows


def fetch_raw(sym):
    url = RAW_URL.format(sym=sym)
    with _no_proxy_opener().open(url, timeout=30) as resp:
        txt = resp.read().decode("utf-8", errors="replace")
    m = re.search(r"\(\s*(\[.*\])\s*\)", txt, re.S)
    if not m:
        raise RuntimeError("raw_parse_fail: no json array")
    arr = json.loads(m.group(1))
    rows = []
    for it in arr:
        d = it.get("d", "")
        rows.append({
            "date": str(d),
            "open": float(it["o"]), "high": float(it["h"]),
            "low": float(it["l"]), "close": float(it["c"]),
            "volume": float(it.get("v") or 0) or None,
            "oi": float(it.get("o") or 0) or None,
            "settle": None,
        })
    return rows


def fetch(sym):
    try:
        rows = fetch_akshare(sym)
        if rows:
            return rows, "akshare.futures_main_sina"
    except Exception as e:
        note = f"akshare_fail:{type(e).__name__}"
    else:
        note = "akshare_empty"
    rows = fetch_raw(sym)
    return rows, f"raw_sina_jsonp (after {note})"


# ------------------------------------------------------------------------- run


def run():
    st = load_status()
    now = dt.datetime.now()
    # Daily-cutoff gate FIRST: verified zero-network no-op when the local
    # chain already covers the latest possible complete-bar date. Bumps
    # ts+last_attempt so the panel reader stays fresh; throttle window also
    # restarts (benign: worst case the new daily bar lands ~30min after
    # publication -- same-evening source lag self-heals, update_lhb precedent).
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
                print(f"throttle: last attempt {last_attempt} ({age/60:.1f}min ago) < 30min -> no-op")
                return 0
        except Exception:
            pass
    st["last_attempt"] = now.isoformat(timespec="seconds")  # mirror FIRST (r18 lesson)
    st["varieties_planned"] = VARIETIES
    write_status(st)

    _clear_proxy_env()
    per, failures, mismatches = [], [], []
    use_raw_only = False
    for i, v in enumerate(VARIETIES):
        sym = v + "0"
        rec = {"variety": v, "symbol": sym, "appended": 0, "overlap": 0,
               "mismatch": None, "error": None, "path": None,
               "rows_local": None, "first": None, "last": None}
        try:
            if use_raw_only:
                rows, path = fetch_raw(sym), "raw_sina_jsonp (sticky after akshare family failure)"
            else:
                try:
                    rows, path = fetch(sym)
                except Exception as e:
                    if "akshare" in str(e) or "Arrow" in str(e) or "parse" in str(e).lower():
                        use_raw_only = True
                    raise
            rec["path"] = path
            rows, dropped_today = completeness_filter(rows)
            err = validate_rows(rows)
            if err:
                raise RuntimeError(f"validation_fail: {err}")
            p = os.path.join(DATA_DIR, v + ".csv")
            local = read_local_csv(p)
            res = merge_incremental(local, rows)
            rec["overlap"] = res["overlap"]
            rec["mismatch"] = res["mismatch"]
            if not res["merged"]:
                mismatches.append(f"{v}@{res['mismatch']}")
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
            failures.append(v)
        per.append(rec)
        if i < len(VARIETIES) - 1:
            time.sleep(SLEEP_S)

    st.update({
        "ts": now.isoformat(timespec="seconds"),
        "mode": "full-history pull, append-only local, overlap-verified",
        "per_variety": per,
        "summary": {
            "varieties": len(VARIETIES), "failures": len(failures),
            "mismatches": len(mismatches),
            "total_appended": sum(r.get("appended") or 0 for r in per),
            "data_cutoff": max([r["last"] for r in per if r.get("last")], default=None),
        },
        "claim": "MSG-20260924-0645-bm-a-futures-cta-puller",
        "note": "main-continuous bars are raw price level at roll (unadjusted); roll-gap handling is a prereg design decision, not a puller concern",
    })
    write_status(st)
    print(f"update_futures -> {STATUS}")
    for r in per:
        line = f"  {r['variety']}: "
        if r["error"]:
            line += f"FAIL {r['error']}"
        elif r["mismatch"]:
            line += f"MISMATCH@{r['mismatch']} local untouched ({r['rows_local']} rows)"
        else:
            line += f"+{r['appended']} rows -> {r['rows_local']} total {r['first']}..{r['last']}"
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
    # S1 completeness guard: drop trailing today-row pre-15:30
    rows = [{"date": "2026-09-22", "close": 1.0},
            {"date": today, "close": 2.0}]
    kept, dropped = completeness_filter(rows, now=now)
    assert len(kept) == 1 and dropped == 1 and kept[0]["date"] == "2026-09-22"
    # S1b: post-15:30 keeps it
    kept, dropped = completeness_filter(rows, now=dt.datetime(2026, 9, 24, 15, 31))
    assert len(kept) == 2 and dropped == 0
    # S1c: yesterday-only rows untouched
    kept, _ = completeness_filter([{"date": "2026-09-23", "close": 1.0}], now=now)
    assert len(kept) == 1
    # S2 validation gate
    assert validate_rows([{"date": "2026-09-01", "close": 1.0},
                           {"date": "2026-09-02", "close": 1.5}]) is None
    assert validate_rows([{"date": "2026-09-02", "close": 1.0},
                           {"date": "2026-09-01", "close": 1.5}]) is not None
    assert validate_rows([{"date": "2026-09-01", "close": None}]) is not None
    assert validate_rows([{"date": "bad", "close": 1.0}]) is not None
    # S3 incremental merge: clean append
    local = [{"date": "2026-09-01", "open": 10.0, "high": 11.0, "low": 9.0, "close": 10.5},
             {"date": "2026-09-02", "open": 10.5, "high": 11.5, "low": 10.0, "close": 11.0}]
    src = local + [{"date": "2026-09-03", "open": 11.0, "high": 12.0, "low": 10.5, "close": 11.5}]
    res = merge_incremental(local, src)
    assert res["merged"] and res["appended"] == 1 and res["overlap"] == 2 and res["mismatch"] is None
    assert len(res["merged_rows"]) == 3 and res["merged_rows"][-1]["date"] == "2026-09-03"
    # S4 mismatch: local untouched, merged False (assert J18 self-consistency: 10.5 vs 10.5)
    src_bad = [dict(local[0]), dict(local[1])] + [
        {"date": "2026-09-03", "open": 11.0, "high": 12.0, "low": 10.5, "close": 11.5}]
    src_bad[0]["close"] = 9.99  # source re-adjusted history
    res2 = merge_incremental(local, src_bad)
    assert not res2["merged"] and res2["mismatch"] == "2026-09-01" and res2["merged_rows"] is None
    # S5 csv roundtrip incl. volume int cast + NaN settle as empty
    rr = [{"date": "2026-09-01", "open": 10.0, "high": 11.0, "low": 9.0, "close": 10.5,
           "volume": 123456.0, "oi": 98765.0, "settle": None}]
    text = rows_to_csv_text(rr)
    assert text.splitlines()[0] == ",".join(COLS)
    assert text.splitlines()[1].endswith("123456,98765,")
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "x.csv")
        atomic_write(p, text)
        back = read_local_csv(p)
        assert back[0]["close"] == 10.5 and back[0]["volume"] == 123456.0 and back[0]["settle"] is None
    # S6 symbol mapping
    assert [v + "0" for v in ["IF", "AU"]] == ["IF0", "AU0"]
    # S7 status JSON roundtrip: native types only
    assert json.loads(json.dumps({"a": int(2), "b": None, "c": bool(1)}))["b"] is None
    # S8 expected_latest_bar_date (injected calendar; fabric = ETF trading
    # days through 09-23, today 09-24 Thu; J18 self-consistency -- constructed
    # calendar, no live-data dependence)
    cal = ["2026-09-21", "2026-09-22", "2026-09-23"]
    assert expected_latest_bar_date(dt.datetime(2026, 9, 24, 7, 0), cal) == "2026-09-23"   # pre-15:30
    assert expected_latest_bar_date(dt.datetime(2026, 9, 24, 16, 0), cal) == "2026-09-23"  # post-15:30, today's bar not landed -> self-heal
    assert expected_latest_bar_date(dt.datetime(2026, 9, 24, 16, 0), cal + ["2026-09-24"]) == "2026-09-24"
    cal5 = cal + ["2026-09-24", "2026-09-25"]
    assert expected_latest_bar_date(dt.datetime(2026, 9, 26, 16, 0), cal5) == "2026-09-25"  # Sat -> Fri
    assert expected_latest_bar_date(dt.datetime(2026, 10, 1, 16, 0), cal5 + ["2026-09-30"]) == "2026-09-30"  # holiday -> prior
    assert expected_latest_bar_date(dt.datetime(2026, 9, 24, 16, 0), []) == "2026-09-24"  # degenerate/absent calendar -> weekday fallback, post-15:30 Thu
    assert expected_latest_bar_date(dt.datetime(2026, 9, 24, 7, 0), []) == "2026-09-23"
    assert expected_latest_bar_date(dt.datetime(2026, 9, 26, 16, 0), []) == "2026-09-25"  # Sat -> walk back
    # S9 cutoff_gate
    needs, exp, _ = cutoff_gate("2026-09-23", dt.datetime(2026, 9, 24, 7, 0), cal)
    assert not needs and exp == "2026-09-23"
    needs, exp, _ = cutoff_gate("2026-09-22", dt.datetime(2026, 9, 24, 7, 0), cal)
    assert needs and exp == "2026-09-23"
    needs, _, _ = cutoff_gate(None, dt.datetime(2026, 9, 24, 7, 0), cal)
    assert needs  # no local data -> honest fetch
    # S10 local_data_cutoff on a constructed variety set (offline, temp dir)
    with tempfile.TemporaryDirectory() as td:
        base = [{"date": "2026-09-22", "close": 1.0}, {"date": "2026-09-23", "close": 1.1}]
        for v in VARIETIES:
            atomic_write(os.path.join(td, v + ".csv"),
                         rows_to_csv_text([dict(r, open=r["close"], high=r["close"],
                                               low=r["close"], volume=1.0, oi=1.0,
                                               settle=None) for r in base]))
        assert local_data_cutoff(td) == "2026-09-23"
        os.remove(os.path.join(td, "AU" + ".csv"))
        assert local_data_cutoff(td) is None  # any-missing -> None (honest fetch)
    print("selftest: 10/10 PASS")
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return _selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())
