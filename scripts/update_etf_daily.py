"""Five-member ETF daily panel refresh leg (bm-b lane, R31).

Ticket: T-2026-09-28-111 (candidate ticket frozen as an improvement
pointer in research/etf_ops/ETF_OPS_BP1_PREREG.md S0 sec-3.2: the
five-member face had NO refresh leg -- update_astock_daily universe is
0/3/6-prefix stocks, zero 5-prefix ETF codes, so the "lane-maintained"
claim never held for the five members).

Universe: O-20260928-1555 frozen five-member two-tier research face
    510300 (tier1 HS300)  510050 (tier1 SSE50)
    510500 (tier2 CSI500) 512100 (tier2 CSI1000) 588000 (tier2 STAR50)
Panel: data/daily/sh<code>.csv, 7 cols date,open,high,low,close,volume,amount.

Basis (probe evidence, r398 bm-b: results/_r398bmb_etf_daily_probe*.py):
the local face is AS-TRADED basis. Sina's ETF qfq factor is s=1.0 on all
events (fund-share-structure dividends are NOT back-priced by this
endpoint) -> raw klc_kl.js face == local face (ratio 1.000000 across
2015 / 2025-06-18 dividend / 2026-01-19 event / 2026-09-22 windows;
full-history dry-compare 5/5 members zero mismatch). The akshare wrapper
is bypassed: its outstanding_share/turnover leg crashes on ETF codes
("No value to decode") -- direct endpoint + MiniRacer decode = the fleet
direct-endpoint recipe (T-106 s2 采集器直连端点律 family).

Frozen-consumer safety: etf_ops_bp1.load_member D2 lockbox TRUNCATES
rows after a frozen batch's evidence_cutoff before the anchor compare,
so appends never break frozen prereg faces; future batches (BP2 / T-104
s3 deep face) re-anchor at their own freeze time.

Semantics (update_repo.py canonical family, R328):
- Full-history pull each run (5 requests, 2.5s pace, in-line legal --
  NOT a >5min long job); append-only; overlap rows verified (prices
  tol 1e-6 abs, volume/amount int-round +-1) BEFORE any write.
- All-or-nothing panel write: any member fetch fail -> exit 2, zero
  writes; any overlap mismatch -> exit 3, zero writes (source rewrites
  history -> conscious re-anchor in a round, never silent).
- Panel-freshness gate: min-of-lasts across the five files vs the
  latest possible COMPLETE bar date (15:30 convention; local ETF
  trading calendar = update_futures/repo master data/daily/510300.csv).
  min() (not max) is deliberate: one stale member keeps the gate open.
- Completeness: a row dated today persists only after 15:30 local.
- Atomic writes (.tmp + os.replace); strictly-increasing unique dates;
  OHLC sanity (low <= min(open,close), high >= max(open,close), > 0).
- 30-min attempt throttle; conn-fuse 3 consecutive connection failures.
- Lane guard: bm-b only (R31); other machines stdout-only honest no-op.

Exit contract: 0 ok/no-op | 2 fetch/mechanism fail | 3 overlap mismatch
(source history rewrite). selftest subcommand = offline hermetic.
"""

import datetime as dt
import io
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEMBERS = ["510300", "510050", "510500", "512100", "588000"]  # O-1555 frozen
TIER = {"510300": "tier1-HS300", "510050": "tier1-SSE50",
        "510500": "tier2-CSI500", "512100": "tier2-CSI1000",
        "588000": "tier2-STAR50-20cm"}
DATA_DIR = os.path.join(ROOT, "data", "daily")
COLS = ["date", "open", "high", "low", "close", "volume", "amount"]
STATUS = os.path.join(ROOT, "results", "etf_daily_pull_status.json")
LANE_OWNER = "bm-b"            # R31 lane law (five-member face = bm-b lane)
MIN_ATTEMPT_S = 1800           # 30-min attempt throttle
CONN_STOP = 3                   # consecutive connection failures -> stop
SLEEP_S = 2.5                   # inter-request pace
PRICE_TOL = 1e-6                # overlap price tolerance (abs)
INT_TOL = 1                     # volume/amount int-round drift tolerance
COMPLETE_HOUR = dt.time(15, 30)


def _clear_proxy_env():
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)


def _endpoints():
    """Sina direct endpoints + JS decoder (single source of truth:
    akshare's own constants -- drift there surfaces as exit 2 here)."""
    import akshare.stock.stock_zh_a_sina as m
    from py_mini_racer import MiniRacer
    return m.zh_sina_a_stock_hist_url, m.hk_js_decode, MiniRacer


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
    if now.time() >= COMPLETE_HOUR or not rows:
        return rows, 0
    today = now.date().isoformat()
    kept, dropped = list(rows), 0
    while kept and str(kept[-1].get("date", "")) == today:
        kept.pop()
        dropped += 1
    return kept, dropped


_DATES_CACHE = None


def _load_trading_dates():
    """Local ETF trading-day calendar as sorted ISO strings (update_futures/
    update_repo master: data/daily/510300.csv primary, glob fallback,
    None -> weekday approximation)."""
    global _DATES_CACHE
    if _DATES_CACHE is not None:
        return _DATES_CACHE
    import csv as _csv
    import glob as _glob
    cands = [os.path.join(ROOT, "data", "daily", "510300.csv")]
    cands += [p for p in sorted(_glob.glob(os.path.join(ROOT, "data",
                                                        "daily", "*.csv")))
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
    """Latest date a COMPLETE ETF daily bar can exist at `now` (pure).
    Mirror of update_repo.expected_latest_bar_date."""
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
    d = now.date() - dt.timedelta(days=1) if now.time() < COMPLETE_HOUR \
        else now.date()
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d.isoformat()


def cutoff_gate(panel_cutoff, now, dates=None):
    """(needs_fetch, expected_date, reason)."""
    expected = expected_latest_bar_date(now, dates)
    if panel_cutoff is None:
        return True, expected, "no local five-member panel (first run)"
    if str(panel_cutoff) >= expected:
        return False, expected, (f"panel cutoff {panel_cutoff} covers "
                                 f"expected complete-bar date {expected}")
    return True, expected, f"panel cutoff {panel_cutoff} behind {expected}"


def local_panel_cutoff(data_dir=None):
    """MIN last-bar date across the five member CSVs (weakest-member
    freshness); None if any file missing/empty. min() is deliberate:
    one stale member keeps the gate open (update_repo uses max for its
    homogeneous term family; the five ETF members can diverge on source
    glitches, so the panel is fresh only when ALL five cover)."""
    data_dir = data_dir or DATA_DIR
    lasts = []
    for code in MEMBERS:
        p = os.path.join(data_dir, "sh" + code + ".csv")
        if not os.path.exists(p):
            return None
        rows = read_local_csv(p)
        if not rows:
            return None
        lasts.append(str(rows[-1]["date"]))
    return min(lasts)


def validate_rows(rows):
    """Dates strictly increasing + unique; prices positive finite; OHLC
    sanity (low <= min(open,close), high >= max(open,close))."""
    prev = None
    for r in rows:
        d = str(r.get("date", ""))
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            return f"bad_date_format:{d}"
        if prev is not None and d <= prev:
            return f"non_monotonic_at:{d}"
        prev = d
        try:
            o, h = float(r["open"]), float(r["high"])
            low, c = float(r["low"]), float(r["close"])
        except (TypeError, ValueError):
            return f"non_numeric_at:{d}"
        if not all(v == v and abs(v) != float("inf") for v in (o, h, low, c)):
            return f"nan_price_at:{d}"
        if min(o, h, low, c) <= 0:
            return f"non_positive_price_at:{d}"
        if low > min(o, c) + PRICE_TOL or h < max(o, c) - PRICE_TOL:
            return f"ohlc_order_at:{d}"
        if float(r["volume"]) < 0 or float(r["amount"]) < 0:
            return f"negative_flow_at:{d}"
    return None


def merge_incremental(local_rows, source_rows):
    """Append-only merge with overlap verification. Returns
    {merged: bool, merged_rows|None, appended, overlap, mismatch}."""
    src_by_date = {str(r["date"]): r for r in source_rows}
    overlap = 0
    for lr in local_rows:
        d = str(lr["date"])
        s = src_by_date.get(d)
        if s is None:
            return {"merged": False, "merged_rows": None, "appended": 0,
                    "overlap": overlap, "mismatch": f"{d}:absent_in_source"}
        overlap += 1
        for key in ("open", "high", "low", "close"):
            if abs(float(lr[key]) - float(s[key])) > PRICE_TOL:
                return {"merged": False, "merged_rows": None, "appended": 0,
                        "overlap": overlap,
                        "mismatch": f"{d}:{key}_drift"}
        if abs(int(float(lr["volume"])) - int(round(float(s["volume"])))) \
                > INT_TOL:
            return {"merged": False, "merged_rows": None, "appended": 0,
                    "overlap": overlap, "mismatch": f"{d}:volume_drift"}
        if abs(int(float(lr["amount"])) - int(round(float(s["amount"])))) \
                > INT_TOL:
            return {"merged": False, "merged_rows": None, "appended": 0,
                    "overlap": overlap, "mismatch": f"{d}:amount_drift"}
    local_dates = {str(r["date"]) for r in local_rows}
    new_rows = [r for r in source_rows if str(r["date"]) not in local_dates]
    merged = list(local_rows) + sorted(new_rows, key=lambda r: str(r["date"]))
    return {"merged": True, "merged_rows": merged,
            "appended": len(new_rows), "overlap": overlap, "mismatch": None}


# ------------------------------------------------------------------ csv helpers


def rows_to_csv_text(rows):
    """7-col csv; prices %.4f, volume/amount int (bootstrap byte format)."""
    out = [",".join(COLS)]
    for r in rows:
        out.append(",".join([
            str(r["date"]),
            format(float(r["open"]), ".4f"),
            format(float(r["high"]), ".4f"),
            format(float(r["low"]), ".4f"),
            format(float(r["close"]), ".4f"),
            str(int(round(float(r["volume"])))),
            str(int(round(float(r["amount"])))),
        ]))
    return "\n".join(out) + "\n"


def read_local_csv(path):
    rows = []
    with io.open(path, "r", encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        if header != COLS:
            raise RuntimeError(f"column face drift: {header}")
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            rows.append({"date": parts[0], "open": float(parts[1]),
                         "high": float(parts[2]), "low": float(parts[3]),
                         "close": float(parts[4]), "volume": float(parts[5]),
                         "amount": float(parts[6])})
    return rows


def atomic_write(path, text):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def load_status():
    try:
        with io.open(STATUS, encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return {}


def write_status(payload):
    tmp = STATUS + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATUS)


# ---------------------------------------------------------------------- fetch


def normalize_decoded(dl):
    """Decoded klc_kl.js rows -> 7-col row dicts. Drops prevclose/postVol/
    postAmt; normalizes '2026-09-28T00:00:00.000Z' -> '2026-09-28'."""
    rows = []
    for it in dl:
        d = str(it.get("date", ""))[:10]
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            raise ValueError(f"undecodable_date:{it.get('date')!r}")
        rows.append({"date": d,
                     "open": float(it["open"]), "high": float(it["high"]),
                     "low": float(it["low"]), "close": float(it["close"]),
                     "volume": float(it["volume"]),
                     "amount": float(it["amount"])})
    rows.sort(key=lambda r: r["date"])
    return rows


def fetch_member(code):
    """Full-history pull for one member. Raises on conn/decode fail."""
    import requests
    hist_url, js_decode, _MiniRacer = _endpoints()
    sym = "sh" + code
    r = requests.get(hist_url.format(sym), timeout=15)
    r.raise_for_status()
    if "=" not in r.text or ";" not in r.text:
        raise ValueError(f"payload_face_drift:len={len(r.text)}")
    js = _MiniRacer()
    js.eval(js_decode)
    dl = js.call("d", r.text.split("=")[1].split(";")[0].replace('"', ""))
    return normalize_decoded(dl)


# ------------------------------------------------------------------------- run


def run():
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        print(f"no-op: five-member ETF daily lane owned by {LANE_OWNER}, "
              f"not this machine ({owner or '?'})")
        return 0
    _clear_proxy_env()
    st = load_status()
    now = dt.datetime.now()
    panel_cut = local_panel_cutoff()
    needs_fetch, expected, gate_reason = cutoff_gate(panel_cut, now)
    if not needs_fetch:
        st["last_attempt"] = st["ts"] = now.isoformat(timespec="seconds")
        st["mode"] = "no-op: panel cutoff covered"
        st["no_op_reason"] = gate_reason
        st["expected_cutoff"] = expected
        st["data_cutoff"] = panel_cut
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
    st["last_attempt"] = now.isoformat(timespec="seconds")  # mirror FIRST
    st["members_planned"] = list(MEMBERS)
    write_status(st)

    per, failures, mismatches = [], [], []
    conn_fails = 0
    planned = {}                      # code -> merged result (all verified
                                      # before ANY write: all-or-nothing)
    for i, code in enumerate(MEMBERS):
        rec = {"code": code, "tier": TIER[code], "appended": 0,
               "overlap": 0, "mismatch": None, "error": None,
               "rows_local": None, "first": None, "last": None}
        if conn_fails >= CONN_STOP:
            rec["error"] = f"conn-fuse: {conn_fails} consecutive " \
                           f"connection failures"
            per.append(rec)
            continue
        try:
            try:
                rows = fetch_member(code)
            except Exception as e:
                ename = type(e).__name__
                if ename in ("ConnectionError", "ConnectTimeout",
                            "ReadTimeout", "Timeout", "URLError",
                            "ChunkedEncodingError", "SSLError"):
                    conn_fails += 1
                    raise RuntimeError(f"conn_fail:{ename} "
                                       f"({conn_fails}/{CONN_STOP})")
                conn_fails = 0
                raise
            conn_fails = 0
            rows, dropped_today = completeness_filter(rows, now=now)
            if dropped_today:
                rec["dropped_today_partial"] = dropped_today
            err = validate_rows(rows)
            if err:
                raise RuntimeError(f"validation_fail: {err}")
            local = read_local_csv(os.path.join(DATA_DIR, "sh" + code + ".csv"))
            res = merge_incremental(local, rows)
            rec["overlap"] = res["overlap"]
            rec["mismatch"] = res["mismatch"]
            if not res["merged"]:
                mismatches.append(f"{code}@{res['mismatch']}")
                rec["rows_local"] = len(local)
                if local:
                    rec["first"], rec["last"] = (str(local[0]["date"]),
                                                 str(local[-1]["date"]))
            else:
                planned[code] = res
                rec["appended"] = res["appended"]
                rec["rows_local"] = len(res["merged_rows"])
                rec["first"] = str(res["merged_rows"][0]["date"])
                rec["last"] = str(res["merged_rows"][-1]["date"])
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {str(e)[:180]}"
            failures.append(code)
        per.append(rec)
        if i < len(MEMBERS) - 1:
            time.sleep(SLEEP_S)

    # all-or-nothing: any fail/mismatch -> zero writes (panel stays
    # homogeneous; gate re-opens on the min() cutoff after throttle)
    wrote = 0
    if not failures and not mismatches and len(planned) == len(MEMBERS):
        for code in MEMBERS:
            p = os.path.join(DATA_DIR, "sh" + code + ".csv")
            atomic_write(p, rows_to_csv_text(planned[code]["merged_rows"]))
            wrote += 1

    st.update({
        "ts": now.isoformat(timespec="seconds"),
        "mode": "full-history pull, append-only, overlap-verified, "
                "all-or-nothing panel write",
        "per_member": per,
        "files_written": wrote,
        "summary": {
            "members": len(MEMBERS), "failures": len(failures),
            "mismatches": len(mismatches),
            "total_appended": sum(r.get("appended") or 0 for r in per),
            "data_cutoff": min([r["last"] for r in per if r.get("last")],
                               default=None),
        },
        "claim": "T-2026-09-28-111-bm-b-five-member-etf-daily-refresh-leg",
        "note": "as-traded basis (sina klc_kl.js; ETF qfq factor s=1.0 all "
                "events -- fund-share dividends not back-priced); frozen "
                "consumers truncate post-cutoff rows via D2 lockbox",
    })
    write_status(st)
    print(f"update_etf_daily -> {STATUS}")
    for r in per:
        line = f"  {r['code']} ({r['tier']}): "
        if r["error"]:
            line += f"FAIL {r['error']}"
        elif r["mismatch"]:
            line += f"MISMATCH@{r['mismatch']} local untouched " \
                    f"({r['rows_local']} rows)"
        else:
            line += (f"+{r['appended']} rows -> {r['rows_local']} total "
                     f"{r['first']}..{r['last']}"
                     + (f" [written]" if wrote else " [verified, "
                        "panel blocked by sibling]"))
        print(line)
    if failures:
        return 2
    if mismatches:
        return 3
    return 0


# --------------------------------------------------------------------- selftest


def _selftest():
    import tempfile
    now = dt.datetime(2026, 9, 28, 10, 0)
    today = "2026-09-28"

    # S1 completeness guard
    rows = [{"date": "2026-09-24", "close": 1.0, "volume": 1.0, "amount": 1.0},
            {"date": today, "close": 2.0, "volume": 2.0, "amount": 2.0}]
    kept, dropped = completeness_filter(rows, now=now)
    assert len(kept) == 1 and dropped == 1 and kept[0]["date"] == "2026-09-24"
    kept, dropped = completeness_filter(rows, now=dt.datetime(2026, 9, 28, 15, 31))
    assert len(kept) == 2 and dropped == 0

    # S2 validation gate
    good = {"date": "2026-09-01", "open": 4.5, "high": 4.6, "low": 4.4,
            "close": 4.5, "volume": 100.0, "amount": 450.0}
    assert validate_rows([good]) is None
    assert validate_rows([dict(good, date="bad")]) is not None
    assert validate_rows([dict(good, low=9.9)]) is not None      # ohlc order
    assert validate_rows([dict(good, close=0.0)]) is not None    # non-positive
    assert validate_rows([good, dict(good)]) is not None         # dup date
    assert validate_rows([dict(good, open=None)]) is not None     # non-numeric

    # S3 incremental merge + mismatch honesty (price / volume-int drift)
    local = [{"date": "2026-09-01", "open": 4.5, "high": 4.6, "low": 4.4,
              "close": 4.5, "volume": 100.0, "amount": 450.0},
             {"date": "2026-09-02", "open": 4.6, "high": 4.7, "low": 4.5,
              "close": 4.6, "volume": 110.0, "amount": 460.0}]
    src = local + [{"date": "2026-09-03", "open": 4.7, "high": 4.8, "low": 4.6,
                    "close": 4.7, "volume": 120.0, "amount": 470.0}]
    res = merge_incremental(local, src)
    assert res["merged"] and res["appended"] == 1 and res["overlap"] == 2
    src_bad = [dict(r) for r in local]
    src_bad[0]["close"] = 9.99
    res2 = merge_incremental(local, src_bad)
    assert not res2["merged"] and "2026-09-01" in res2["mismatch"]
    src_vol = [dict(r) for r in local]
    src_vol[1]["volume"] = 110.6                       # int-round drift <=1 ok
    assert merge_incremental(local, src_vol)["merged"]
    src_vol2 = [dict(r) for r in local]
    src_vol2[1]["volume"] = 150.0                      # real drift -> refuse
    assert not merge_incremental(local, src_vol2)["merged"]
    src_abs = [dict(r) for r in local]
    src_abs[0]["date"] = "2025-09-01"                  # source row vanished
    assert not merge_incremental(local, src_abs)["merged"]

    # S4 csv roundtrip: bootstrap byte format (%.4f prices, int flows)
    rr = [{"date": "2026-09-01", "open": 4.556, "high": 4.5960, "low": 4.5480,
           "close": 4.5820, "volume": 629721123.0, "amount": 2877462543.0}]
    text = rows_to_csv_text(rr)
    assert text.splitlines()[0] == ",".join(COLS)
    assert text.splitlines()[1] == ("2026-09-01,4.5560,4.5960,4.5480,"
                                    "4.5820,629721123,2877462543")
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "x.csv")
        atomic_write(p, text)
        back = read_local_csv(p)
        assert back[0]["close"] == 4.582 and back[0]["volume"] == 629721123.0

    # S5 normalize_decoded: TZ suffix + junk cols dropped
    dl = [{"date": "2026-09-28T00:00:00.000Z", "open": 4.499, "high": 4.503,
           "low": 4.397, "close": 4.417, "volume": 986408900,
           "amount": 4373095288, "postVol": 372200.0, "postAmt": 1644007.0,
           "prevclose": 4.515},
          {"date": "2026-09-24T00:00:00.000Z", "open": 4.578, "high": 4.579,
           "low": 4.512, "close": 4.515, "volume": 710251931,
           "amount": 3220888135}]
    rows = normalize_decoded(dl)
    assert rows[0]["date"] == "2026-09-24" and rows[1]["date"] == "2026-09-28"
    assert list(rows[0].keys()) == COLS and rows[1]["volume"] == 986408900.0

    # S6 cutoff gate + expected bar date (injected calendar)
    cal = ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24"]
    assert expected_latest_bar_date(dt.datetime(2026, 9, 28, 7, 0),
                                    cal) == "2026-09-24"
    assert expected_latest_bar_date(dt.datetime(2026, 9, 28, 16, 0),
                                    cal) == "2026-09-24"   # today not in cal
    assert expected_latest_bar_date(
        dt.datetime(2026, 9, 28, 16, 0),
        cal + ["2026-09-28"]) == "2026-09-28"
    assert expected_latest_bar_date(dt.datetime(2026, 9, 26, 16, 0),
                                    []) == "2026-09-25"
    needs, exp, _ = cutoff_gate("2026-09-24", dt.datetime(2026, 9, 28, 7, 0),
                                cal)
    assert not needs and exp == "2026-09-24"
    needs, _, _ = cutoff_gate("2026-09-22", dt.datetime(2026, 9, 28, 7, 0), cal)
    assert needs
    needs, _, _ = cutoff_gate(None, dt.datetime(2026, 9, 28, 7, 0), cal)
    assert needs

    # S7 local_panel_cutoff: min-of-lasts; any-missing -> None
    with tempfile.TemporaryDirectory() as td:
        base_rows = [
            {"date": "2026-09-22", "open": 4.5, "high": 4.6, "low": 4.4,
             "close": 4.5, "volume": 100.0, "amount": 450.0},
            {"date": "2026-09-23", "open": 4.5, "high": 4.6, "low": 4.4,
             "close": 4.5, "volume": 100.0, "amount": 450.0}]
        for code in MEMBERS:
            atomic_write(os.path.join(td, "sh" + code + ".csv"),
                         rows_to_csv_text(base_rows))
        assert local_panel_cutoff(td) == "2026-09-23"
        stale = [dict(base_rows[0])]           # one member behind
        atomic_write(os.path.join(td, "sh588000.csv"),
                     rows_to_csv_text(stale))
        assert local_panel_cutoff(td) == "2026-09-22"          # min, not max
        os.remove(os.path.join(td, "sh512100.csv"))
        assert local_panel_cutoff(td) is None

    # S8 all-or-nothing orchestration: one sibling mismatch -> zero writes
    with tempfile.TemporaryDirectory() as td:
        local_a = [{"date": "2026-09-22", "open": 4.5, "high": 4.6,
                    "low": 4.4, "close": 4.5, "volume": 100.0,
                    "amount": 450.0}]
        local_b = [dict(local_a[0], close=4.7)]
        atomic_write(os.path.join(td, "sh510300.csv"), rows_to_csv_text(local_a))
        atomic_write(os.path.join(td, "sh510050.csv"), rows_to_csv_text(local_b))
        fresh = [dict(local_a[0]),
                 {"date": "2026-09-23", "open": 4.5, "high": 4.6,
                  "low": 4.4, "close": 4.5, "volume": 100.0, "amount": 450.0}]
        # member A merges clean; member B source rewrites close -> blocked
        res_a = merge_incremental(local_a, fresh)
        res_b = merge_incremental(local_b, fresh)
        assert res_a["merged"] and not res_b["merged"]
        # run() would refuse all writes: panel files unchanged on disk
        assert len(read_local_csv(os.path.join(td, "sh510300.csv"))) == 1
        assert len(read_local_csv(os.path.join(td, "sh510050.csv"))) == 1

    # S9 lane guard logic + universe integrity
    assert LANE_OWNER == "bm-b"
    assert ("bm-a" != LANE_OWNER) and ("bm-c" != LANE_OWNER) \
        and (None != LANE_OWNER)
    assert len(MEMBERS) == 5 and len(set(MEMBERS)) == 5
    assert all(re.match(r"^(51|58)", c) for c in MEMBERS)

    # S10 status JSON native types only
    assert json.loads(json.dumps({"a": int(2), "b": None}))["b"] is None
    print("selftest: 10/10 PASS")
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return _selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())
