"""Northbound-funds (HSGT) data-face reachability probe -- P3 explore E3.

E3 (state/queue/explore.md head): "northbound funds data-source reachability
scan (akshare/EM source; sentiment-factor candidate)".

This script is the runnable artifact of that survey. It MEASURES ONLY:
per akshare northbound endpoint, on THIS machine (machine_id from
fleet/machine.json): reachability, latency, schema (column names), row
count, sample tail row, plus a generic disclosure-regime measurement on
the daily-history faces (NaN-rate split analysis around the candidate
2024-08-19 real-time-disclosure discontinuity -- measured, not assumed;
the split is a CANDIDATE anchor, the empirical last-nonnull dates are the
findings). Zero panel writes, zero backtest, zero strategy claims, no
engine touch. Any production collector / prereg on this factor stays
gated on (1) survey findings + a GM-signed ticket for lane landing and
(2) the T-67 s2 freeze law (>=12 months forward accumulation before any
new prereg).

Endpoint families probed (akshare 1.18.96 surface, getattr-guarded,
ALL EM-sourced -- single-source concentration is itself a finding):
  summary: stock_hsgt_fund_flow_summary_em
  hist:    stock_hsgt_hist_em[north|sh|sz]
  min:     stock_hsgt_fund_min_em[north]
  hold:    stock_hsgt_hold_stock_em[north, today-rank]
  indiv:   stock_hsgt_individual_em[600519] /
           stock_hsgt_individual_detail_em[600519]
  stats:   stock_hsgt_stock_statistics_em[north-hold] /
           stock_hsgt_institution_statistics_em[north-hold]
  board:   stock_hsgt_board_rank_em[north-industry, today]
  spot:    stock_hsgt_sh_hk_spot_em

CJK argument values are written as \\uXXXX escapes (ASCII-source law,
precedent scripts/backfill_ext_slots.py L170).

Discipline: 45s timeout jacket per call (r806 law), 2.5s sleep between
network calls, atomic evidence write, honest FAIL/MISSING records.

Usage:
    python scripts/northbound_probe.py probe      # live -> results/northbound_probe.json
    python scripts/northbound_probe.py selftest   # offline guard (no network)

Exit codes: 0 = done (endpoint FAILs are findings, not errors) |
            2 = mechanism fault (evidence write failure / argparse misuse).
"""
import datetime as dt
import json
import os
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "northbound_probe.json")
MACHINE_FILE = os.path.join(ROOT, "fleet", "machine.json")
TIMEOUT_S = 45.0
SLEEP_S = 2.5
REGIME_SPLIT = "2024-08-19"   # candidate real-time-disclosure discontinuity
NORTH = "\u5317\u5411"                                  # north
NORTH_FUND = "\u5317\u5411\u8d44\u91d1"                # north funds
SH_CONNECT = "\u6caa\u80a1\u901a"                      # SH connect
SZ_CONNECT = "\u6df1\u80a1\u901a"                      # SZ connect
NORTH_HOLD = "\u5317\u5411\u6301\u80a1"                # north holdings
TODAY_RANK = "\u4eca\u65e5\u6392\u884c"               # today rank
TODAY = "\u4eca\u65e5"                                 # today
NORTH_BOARD = ("\u5317\u5411\u8d44\u91d1\u589e\u6301"
               "\u884c\u4e1a\u677f\u5757\u6392\u884c")  # north industry rank
ANCHOR_STOCK = "600519"   # heavily northbound-held universe anchor
WIN_START = "20260901"
WIN_END = "20261010"


def _machine_id():
    try:
        with open(MACHINE_FILE, encoding="utf-8") as f:
            return str(json.load(f).get("machine_id", "unknown"))
    except Exception:
        return "unknown"


def _call_with_timeout(fn, timeout_s=TIMEOUT_S):
    """Run fn in a daemon thread; join with timeout. Returns
    (ok, value_or_error, elapsed_s). A timed-out call is abandoned
    (daemon thread left to die) -- honest timeout record, probe moves on."""
    box = {}

    def run():
        try:
            box["value"] = fn()
        except Exception as e:
            box["error"] = "%s: %s" % (type(e).__name__, str(e)[:300])

    t0 = time.time()
    th = threading.Thread(target=run, daemon=True)
    th.start()
    th.join(timeout_s)
    elapsed = round(time.time() - t0, 2)
    if th.is_alive():
        return False, "TIMEOUT after %ss" % timeout_s, elapsed
    if "error" in box:
        return False, box["error"], elapsed
    return True, box.get("value"), elapsed


def _sanitize(df):
    """Generic honest frame snapshot: rows, columns, first/last row samples."""
    rec = {"rows": int(len(df)), "columns": [str(c) for c in df.columns]}
    if len(df) > 0:
        rec["first_row_sample"] = {str(k): str(v)[:60]
                                   for k, v in df.iloc[0].items()}
        rec["last_row_sample"] = {str(k): str(v)[:60]
                                  for k, v in df.iloc[-1].items()}
    return rec


def _find_date_col(df):
    """Generic date-column detection: exact common names first, then first
    column whose first/last values look like ISO-ish dates."""
    if df is None or len(df) == 0:
        return None
    for c in df.columns:
        if str(c).strip().lower() in ("date", "\u65e5\u671f",
                                       "\u4ea4\u6613\u65e5"):
            return c
    for c in df.columns:
        vals = [str(v).strip() for v in df[c].tolist()[:5]
                if str(v).strip()]
        if vals and all(len(v) == 10 and v[:2] == "20" and v[4] in "-/" and
                        v[7] in "-/" for v in vals):
            return c
    return None


def _regime_nan_profile(df):
    """Disclosure-regime measurement for a daily-history face: per column,
    NaN-rate in the pre/post windows around the CANDIDATE split date, and
    the last date each column carried a non-null value. Generic over
    schema drift -- column names are never assumed."""
    prof = {"candidate_split": REGIME_SPLIT, "columns": {}}
    dcol = _find_date_col(df)
    if dcol is None:
        prof["error"] = "no date column detected"
        return prof
    dates = df[dcol].astype(str).str.strip()
    pre = df[dates < REGIME_SPLIT]
    post = df[dates >= REGIME_SPLIT]
    prof["rows_pre"] = int(len(pre))
    prof["rows_post"] = int(len(post))
    prof["first_date"] = str(dates.iloc[0]) if len(dates) else None
    prof["last_date"] = str(dates.iloc[-1]) if len(dates) else None
    for c in df.columns:
        col = df[c]
        nn_last = None
        try:
            nz_dates = df.loc[col.notna(), dcol].astype(str).str.strip()
            if len(nz_dates) > 0:
                nn_last = str(nz_dates.iloc[-1])
        except Exception:
            nn_last = None
        def rate(frame):
            if len(frame) == 0:
                return None
            try:
                return round(float(frame[c].isna().mean()), 4)
            except Exception:
                return None
        prof["columns"][str(c)] = {
            "nan_rate_pre": rate(pre), "nan_rate_post": rate(post),
            "last_nonnull_date": nn_last}
    return prof


def _atomic_write(path, obj):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=True, indent=1)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def _probe_endpoint(out, family, name, call, sleep_before=SLEEP_S):
    time.sleep(sleep_before)
    ok, value, elapsed = _call_with_timeout(call)
    rec = {"family": family, "name": name, "ok": ok, "elapsed_s": elapsed}
    frame = None
    if ok:
        try:
            rec.update(_sanitize(value))
            frame = value
        except Exception as e:
            rec["ok"] = False
            rec["error"] = "sanitize-fault: %s: %s" % (type(e).__name__,
                                                       str(e)[:200])
    else:
        rec["error"] = value
    out.append(rec)
    return rec, frame


def run_probe():
    import akshare as ak
    out = {"ts": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
           "machine_id": _machine_id(),
           "akshare_version": ak.__version__,
           "law_ref": "P3 explore E3 survey-first; single-source (EM) "
                      "concentration disclosed; production landing gated on "
                      "GM ticket + T-67 s2 freeze law",
           "endpoints": [], "regime_profiles": {}}
    eps = out["endpoints"]

    def guarded(fname):
        fn = getattr(ak, fname, None)
        return fn if callable(fn) else None

    # 1) summary overview face
    _probe_endpoint(eps, "summary", "stock_hsgt_fund_flow_summary_em",
                    lambda: guarded("stock_hsgt_fund_flow_summary_em")(),
                    sleep_before=0.0)

    # 2-4) daily history faces (sentiment-factor primary face)
    hist_defs = [
        ("hist_north", "stock_hsgt_hist_em[%s]" % NORTH_FUND,
         lambda: ak.stock_hsgt_hist_em(symbol=NORTH_FUND)),
        ("hist_sh", "stock_hsgt_hist_em[%s]" % SH_CONNECT,
         lambda: ak.stock_hsgt_hist_em(symbol=SH_CONNECT)),
        ("hist_sz", "stock_hsgt_hist_em[%s]" % SZ_CONNECT,
         lambda: ak.stock_hsgt_hist_em(symbol=SZ_CONNECT)),
    ]
    for key, name, call in hist_defs:
        rec, frame = _probe_endpoint(eps, "hist", name, call)
        if rec.get("ok") and frame is not None and len(frame) > 0:
            try:
                out["regime_profiles"][key] = _regime_nan_profile(frame)
            except Exception as e:
                out["regime_profiles"][key] = {"error":
                                                "%s: %s" % (type(e).__name__,
                                                            str(e)[:200])}

    # 5) realtime minute face (disclosure-regime sensitive)
    _probe_endpoint(eps, "min", "stock_hsgt_fund_min_em[%s]" % NORTH_FUND,
                    lambda: guarded("stock_hsgt_fund_min_em")(symbol=
                                                              NORTH_FUND))

    # 6) per-stock northbound holdings rank (T+1 disclosure face)
    _probe_endpoint(eps, "hold",
                    "stock_hsgt_hold_stock_em[%s,%s]" % (NORTH, TODAY_RANK),
                    lambda: guarded("stock_hsgt_hold_stock_em")(market=NORTH,
                                                                indicator=
                                                                TODAY_RANK))

    # 7-8) individual-stock faces (universe bridge to A-share panels)
    _probe_endpoint(eps, "indiv",
                    "stock_hsgt_individual_em[%s]" % ANCHOR_STOCK,
                    lambda: guarded("stock_hsgt_individual_em")(symbol=
                                                                ANCHOR_STOCK))
    _probe_endpoint(eps, "indiv",
                    "stock_hsgt_individual_detail_em[%s]" % ANCHOR_STOCK,
                    lambda: guarded("stock_hsgt_individual_detail_em")(
                        symbol=ANCHOR_STOCK, start_date=WIN_START,
                        end_date=WIN_END))

    # 9-10) statistics faces
    _probe_endpoint(eps, "stats",
                    "stock_hsgt_stock_statistics_em[%s]" % NORTH_HOLD,
                    lambda: guarded("stock_hsgt_stock_statistics_em")(
                        symbol=NORTH_HOLD, start_date=WIN_START,
                        end_date=WIN_END))
    _probe_endpoint(eps, "stats",
                    "stock_hsgt_institution_statistics_em[%s]" % NORTH_HOLD,
                    lambda: guarded("stock_hsgt_institution_statistics_em")(
                        market=NORTH_HOLD, start_date=WIN_START,
                        end_date=WIN_END))

    # 11) sector augmentation face
    _probe_endpoint(eps, "board",
                    "stock_hsgt_board_rank_em[north-industry,%s]" % TODAY,
                    lambda: guarded("stock_hsgt_board_rank_em")(
                        symbol=NORTH_BOARD, indicator=TODAY))

    # 12) realtime spot face
    _probe_endpoint(eps, "spot", "stock_hsgt_sh_hk_spot_em",
                    lambda: guarded("stock_hsgt_sh_hk_spot_em")())

    ok_n = sum(1 for r in eps if r.get("ok"))
    out["summary"] = {"reachable": ok_n, "total": len(eps),
                      "source_note": "all faces EM-sourced via akshare; "
                                     "no second independent source "
                                     "available in akshare 1.18.96 "
                                     "(cross-source gate listed in survey)",
                      "verdict": "measured; see research/shortline/"
                                 "NORTHBOUND_DATA_REACHABILITY.md"}
    try:
        _atomic_write(OUT, out)
    except Exception as e:
        print("mechanism fault: evidence write failed: %s: %s"
              % (type(e).__name__, str(e)[:200]))
        return 2
    print("northbound probe: reachable %d/%d -> %s" % (ok_n, len(eps), OUT))
    for r in eps:
        print("  [%s] %s %s rows=%s %s" % (
            r["family"], r["name"], "OK" if r["ok"] else "FAIL",
            r.get("rows"), ("" if r["ok"] else str(r.get("error"))[:110])))
    for k, v in out["regime_profiles"].items():
        tail = {c: (p.get("nan_rate_post"), p.get("last_nonnull_date"))
                for c, p in list(v.get("columns", {}).items())[:6]} \
            if "columns" in v else v
        print("  regime[%s]: %s" % (k, json.dumps(tail)[:400]))
    return 0


def run_selftest():
    import pandas as pd
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # L1 timeout jacket: hung call -> honest timeout record
    ok, val, el = _call_with_timeout(lambda: time.sleep(1.5), timeout_s=0.3)
    leg("L1 timeout flagged", (not ok) and str(val).startswith("TIMEOUT")
        and el < 1.0)
    # L2 timeout jacket: fast call returns value
    ok, val, el = _call_with_timeout(lambda: 42, timeout_s=5.0)
    leg("L2 fast call value", ok and val == 42)
    # L3 jacket captures exceptions as error strings
    ok, val, el = _call_with_timeout(lambda: (_ for _ in ()).throw(
        ValueError("boom")), timeout_s=5.0)
    leg("L3 exception captured", (not ok) and "boom" in str(val))
    # L4 sanitizer snapshot on synthetic frame
    df = pd.DataFrame({"date": ["2026-09-01", "2026-09-02"],
                       "close": [100.0, 101.5]})
    rec = _sanitize(df)
    leg("L4 sanitizer fields", rec["rows"] == 2 and
        rec["columns"] == ["date", "close"] and
        rec["last_row_sample"]["close"] == "101.5")
    # L5 atomic write roundtrip byte-equal
    tmp_out = os.path.join(ROOT, "results", "_nb_probe_selftest.json")
    obj = {"a": 1, "b": "x"}
    _atomic_write(tmp_out, obj)
    back = json.load(open(tmp_out, encoding="utf-8"))
    leg("L5 atomic roundtrip", back == obj)
    os.remove(tmp_out)
    # L6 machine id anchored
    leg("L6 machine id", _machine_id() in ("bm-a", "bm-b", "bm-c"))
    # L7 regime NaN profile: pre full / post NaN-only -> post rate 1.0,
    #    last_nonnull pinned at the pre-side tail
    h = pd.DataFrame({"date": ["2024-08-16", "2024-08-19", "2024-08-20"],
                      "net_buy": [10.0, None, None],
                      "turnover": [100.0, None, None]})
    prof = _regime_nan_profile(h)
    leg("L7 regime split profile", prof["rows_pre"] == 1 and
        prof["rows_post"] == 2 and
        prof["columns"]["net_buy"]["nan_rate_pre"] == 0.0 and
        prof["columns"]["net_buy"]["nan_rate_post"] == 1.0 and
        prof["columns"]["net_buy"]["last_nonnull_date"] == "2024-08-16")
    # L8 date-col detection: CJK date column recognized
    h2 = pd.DataFrame({"\u65e5\u671f": ["2026-10-08", "2026-10-09"],
                       "v": [1, 2]})
    leg("L8 CJK date col", _find_date_col(h2) == "\u65e5\u671f")
    # L9 date-col detection: positional ISO fallback
    h3 = pd.DataFrame({"d": ["2026-10-08", "2026-10-09"], "v": [1, 2]})
    leg("L9 positional date col", _find_date_col(h3) == "d")

    npass = sum(1 for _, c in legs if c)
    for name, cond in legs:
        print("  [%s] %s" % ("PASS" if cond else "FAIL", name))
    print("selftest: %d/%d legs PASS" % (npass, len(legs)))
    return 0 if npass == len(legs) else 2


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "probe"
    if mode == "probe":
        return run_probe()
    if mode == "selftest":
        return run_selftest()
    print("usage: northbound_probe.py [probe|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
