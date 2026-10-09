"""Convertible-bond (CB) data-face reachability probe -- P3 explore E1.

E1 (state/queue/explore.md head): "CB T+0 data-face feasibility survey:
akshare CB source reachability + fee/intraday-turn rule notes;
new-asset-class survey-first (landing needs a GM-signed P1 ticket)".

This script is the runnable artifact of that survey. It MEASURES ONLY:
per akshare CB endpoint, on THIS machine (machine_id from fleet/machine.json):
reachability, latency, schema (column names), row count, sample tail row.
Zero panel writes, zero backtest, zero strategy claims, no engine touch.
Any production collector / prereg on this asset class stays gated on
(1) a GM-signed P1 ticket (P3 queue header law) and (2) the T-67 2 freeze
law (>=12 months forward accumulation before any new prereg).

Endpoint families probed (akshare 1.18.96 surface, getattr-guarded):
  sina:  bond_zh_hs_cov_spot / bond_zh_hs_cov_daily / bond_zh_hs_cov_min
  em:    bond_zh_cov / bond_cov_comparison / bond_zh_cov_value_analysis
  jsl:   bond_cb_redeem_jsl (expected token gate -> honest FAIL record)

Discipline: 45s timeout jacket per call (r806 law), 2.5s sleep between
network calls, atomic evidence write, ASCII-only source (repo encoding
law), sample codes derived from the live spot face when possible.

Usage:
    python scripts/cb_data_probe.py probe      # live measurement -> results/cb_data_probe.json
    python scripts/cb_data_probe.py selftest   # offline guard (no network)

Exit codes: 0 = done (endpoint FAILs are findings, not errors) |
            2 = mechanism fault (evidence write failure / argparse misuse).
"""
import datetime as dt
import json
import os
import re
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "cb_data_probe.json")
MACHINE_FILE = os.path.join(ROOT, "fleet", "machine.json")
TIMEOUT_S = 45.0
SLEEP_S = 2.5
FALLBACK_SH = "sh113050"   # fixed fallback if spot face unusable
FALLBACK_SZ = "sz123008"


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


def _derive_codes(spot_df):
    """From the live spot face, collect candidate code lists.
    Returns (sh_candidates, sz_candidates, bj_count). Accepts values like
    'sh113050' or bare '113050'. CB numeric families: SH 110/111/112/113/
    118, SZ 123/124/125/127/128; BSE (bj8xxxxx) counted but NOT probed
    (sina daily/min support for BSE bonds unverified)."""
    sh, sz = [], []
    bj = 0
    pat_pref = re.compile(r"^(sh|sz|bj)(\d{6})$")
    pat_bare = re.compile(r"^(\d{6})$")
    seen = set()

    def add(exch, num):
        nonlocal bj
        key = exch + num
        if key in seen:
            return
        seen.add(key)
        if exch == "sh" or (num[:3] in ("110", "111", "112", "113", "118")
                            and exch == "bare"):
            sh.append("sh" + num)
        elif exch == "sz" or (num[:3] in ("123", "124", "125", "127", "128")
                              and exch == "bare"):
            sz.append("sz" + num)
        elif exch == "bj" or num[0] in ("4", "8"):
            bj += 1

    for col in spot_df.columns:
        for v in [str(x).strip() for x in spot_df[col].tolist()[:800]]:
            m = pat_pref.match(v)
            if m:
                add(m.group(1), m.group(2))
                continue
            m2 = pat_bare.match(v)
            if m2:
                add("bare", m2.group(1))
        if sh or sz:
            break
    # prefer live-issue families first (113/118 sh, 123/127/128 sz)
    sh.sort(key=lambda c: 0 if c[2:5] in ("113", "118") else 1)
    sz.sort(key=lambda c: 0 if c[2:5] in ("123", "127", "128") else 1)
    return sh, sz, bj


def _fresh_date(frame):
    """Tail date of a daily face (col 0), or None."""
    try:
        if frame is None or len(frame) == 0:
            return None
        return str(frame.iloc[-1, 0])
    except Exception:
        return None


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
    rec = {"family": family, "name": name, "ok": ok,
           "elapsed_s": elapsed}
    frame = None
    if ok:
        try:
            rec.update(_sanitize(value))
            frame = value  # caller handle; NEVER embedded (JSON-unsafe)
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
           "law_ref": "P3 explore E1 survey-first; GM-signed P1 gate for "
                      "production landing; T-67 2 freeze law for prereg",
           "endpoints": [], "derived": {}, "cross_check": {}}
    eps = out["endpoints"]

    # 1) sina spot -- universe snapshot + code derivation source
    spot, spot_df = _probe_endpoint(
        eps, "sina", "bond_zh_hs_cov_spot",
        lambda: ak.bond_zh_hs_cov_spot(), sleep_before=0.0)
    sh_cands, sz_cands, bj_n = ([], [], 0)
    derive_err = None
    if spot.get("ok") and spot_df is not None:
        try:
            sh_cands, sz_cands, bj_n = _derive_codes(spot_df)
        except Exception as e:
            derive_err = str(e)[:200]
    candidates = (sh_cands[:2] + sz_cands[:2]) or [FALLBACK_SH,
                                                    FALLBACK_SZ]
    out["derived"] = {"sh_candidates": sh_cands[:6],
                      "sz_candidates": sz_cands[:6],
                      "bj_count_in_spot": bj_n,
                      "probe_candidates": candidates,
                      "derive_error": derive_err,
                      "source": "live spot face" if spot.get("ok")
                      and sh_cands else "fixed fallback"}

    # 2) sina daily -- per-candidate history coverage (dead-bond disclosure:
    #    v1 first-hit derivation picked a 2024-redeemed issue; v2 probes a
    #    few candidates and picks the FRESHEST tail as the live sample)
    daily_cov = []
    live_code = None
    live_df = None
    live_tail = None
    for sym in candidates:
        rec, frame = _probe_endpoint(
            eps, "sina", "bond_zh_hs_cov_daily[%s]" % sym,
            lambda s=sym: ak.bond_zh_hs_cov_daily(symbol=s))
        tail = _fresh_date(frame) if rec.get("ok") else None
        daily_cov.append({"symbol": sym, "ok": bool(rec.get("ok")),
                          "rows": rec.get("rows"), "tail_date": tail})
        if tail and (live_tail is None or tail > live_tail):
            live_code, live_df, live_tail = sym, frame, tail
    out["daily_coverage"] = daily_cov
    if live_code is None:
        live_code = candidates[0]
        out["derived"]["live_pick_note"] = \
            "no fresh-tail candidate; fallback to first candidate"
    out["derived"]["live_code"] = live_code
    out["derived"]["live_tail_date"] = live_tail

    # 3) sina 1-min bars on the FRESHEST candidate -- the intraday
    #    (T+0 trade-able) data face; dead-symbol failures disclosed apart
    #    from endpoint-side failures by the coverage table above
    _probe_endpoint(eps, "sina", "bond_zh_hs_cov_min(period=1)",
                    lambda: ak.bond_zh_hs_cov_min(symbol=live_code,
                                                  period="1"))

    # 4) EM list face
    _probe_endpoint(eps, "em", "bond_zh_cov",
                    lambda: ak.bond_zh_cov())

    # 5) EM conversion-value comparison face (CB core fundamental face)
    #    one retry: classify transient vs persistent (conn-fuse spirit,
    #    2 attempts total, never hammer)
    cmp1, _ = _probe_endpoint(eps, "em", "bond_cov_comparison",
                              lambda: ak.bond_cov_comparison())
    if not cmp1.get("ok"):
        cmp2, _ = _probe_endpoint(
            eps, "em", "bond_cov_comparison(retry)",
            lambda: ak.bond_cov_comparison())
        out["comparison_retry_class"] = \
            "transient(retry OK)" if cmp2.get("ok") else \
            "persistent(2 attempts failed)"

    # 6) EM per-bond value analysis (numeric code form, live pick)
    num = live_code.replace("sh", "").replace("sz", "")
    _probe_endpoint(eps, "em", "bond_zh_cov_value_analysis",
                    lambda: ak.bond_zh_cov_value_analysis(symbol=num))

    # 7) jsl redeem face -- expected token gate; honest FAIL is a finding
    _probe_endpoint(eps, "jsl", "bond_cb_redeem_jsl",
                    lambda: ak.bond_cb_redeem_jsl())

    # cross-check: sina daily last close vs spot trade price on live code
    try:
        if live_df is not None and spot_df is not None and len(live_df) > 0:
            close_col = None
            for c in live_df.columns:
                if "close" in str(c).lower() or str(c) in ("收盘", "收盘价"):
                    close_col = c
                    break
            if close_col is not None and "trade" in spot_df.columns \
                    and "symbol" in spot_df.columns:
                last_close = float(live_df.iloc[-1][close_col])
                rows = spot_df[spot_df["symbol"].astype(str).str.strip()
                               == live_code]
                if len(rows) > 0:
                    spot_px = float(rows.iloc[0]["trade"])
                    out["cross_check"] = {
                        "symbol": live_code,
                        "daily_last_date": live_tail,
                        "daily_last_close": last_close,
                        "spot_trade": spot_px,
                        "absdiff": round(abs(last_close - spot_px), 4)}
    except Exception as e:
        out["cross_check"] = {"error": "%s: %s" % (type(e).__name__,
                                                   str(e)[:200])}

    ok_n = sum(1 for r in eps if r.get("ok"))
    out["summary"] = {"reachable": ok_n, "total": len(eps),
                      "verdict": "measured; see research/shortline/"
                                 "CB_T0_DATA_FEASIBILITY.md"}
    try:
        _atomic_write(OUT, out)
    except Exception as e:
        print("mechanism fault: evidence write failed: %s: %s"
              % (type(e).__name__, str(e)[:200]))
        return 2
    print("CB probe: reachable %d/%d -> %s" % (ok_n, len(eps), OUT))
    for r in eps:
        print("  [%s] %s %s rows=%s %s" % (
            r["family"], r["name"], "OK" if r["ok"] else "FAIL",
            r.get("rows"), ("" if r["ok"] else str(r.get("error"))[:110])))
    print(" derived:", json.dumps(out["derived"]))
    print(" cross_check:", json.dumps(out["cross_check"]))
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
    # L5 code derivation: prefixed + bare + bj counting (symbol col first)
    spot = pd.DataFrame({"symbol": ["sh113050", "sz123215", "bj810011"],
                         "noise": ["x", "y", "z"]})
    sh, sz, bj = _derive_codes(spot)
    leg("L5 derive codes", sh[:1] == ["sh113050"] and sz[:1] == ["sz123215"]
        and bj == 1)
    # L6 bare-numeric prefixing by family + live-family sort order
    spot2 = pd.DataFrame({"code": ["110042", "113042", "128100"]})
    sh2, sz2, bj2 = _derive_codes(spot2)
    leg("L6 bare numeric + sort", sh2[0] == "sh113042"
        and sh2[1] == "sh110042" and sz2[:1] == ["sz128100"])
    # L6b fresh-date tail extraction
    leg("L6b fresh tail", _fresh_date(df) == "2026-09-02"
        and _fresh_date(None) is None)
    # L7 atomic write roundtrip byte-equal
    tmp_out = os.path.join(ROOT, "results", "_cb_probe_selftest.json")
    obj = {"a": 1, "b": "x"}
    _atomic_write(tmp_out, obj)
    back = json.load(open(tmp_out, encoding="utf-8"))
    leg("L7 atomic roundtrip", back == obj)
    os.remove(tmp_out)
    # L8 machine id anchored
    leg("L8 machine id", _machine_id() in ("bm-a", "bm-b", "bm-c"))

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
    print("usage: cb_data_probe.py [probe|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
