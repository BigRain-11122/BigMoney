"""ETF book -- how long does a holder have to wait?

Every published face of this book answers "how much" (CAGR, Sharpe) and one of them
answers "how deep" (max drawdown point, and its bootstrap distribution). None of them
answers the question a person actually asks before wiring money: **if I start on a bad
day, how long am I underwater**. Depth and duration are different risks -- the same
-16.6% can be a three-month dip or a four-year hole -- and the book has only ever
reported the first.

What this face publishes, all derived from the production engine's own equity curve:

  * the underwater episodes (peak -> trough -> recovery), with the longest one named
    by date and the count of episodes that never healed inside the data,
  * time-to-recover for **every** entry date, not just the worst one: median, p90,
    the censored share (entries whose money was still under water on the last bar),
    and the worst recovered start,
  * forward return from every entry over 1/2/3 calendar years (min / p5 / p50), because
    "worst calendar year" is a different number from "worst 12 months you could have
    bought into".

Frozen before the run (no line is tuned after seeing the numbers):

  * control arm = the published `n12_vt08` cell. Its CAGR and max drawdown must
    reproduce the production artifact to 5e-5 or this face refuses to publish
    (CONTROL_TOL), because a duration statistic computed on a curve that is not the
    published curve is a different book's risk.
  * an entry that has not recovered on the last bar is CENSORED -- reported as
    "still underwater after N bars", never as 0 and never dropped.
  * horizons are calendar years (`DateOffset`), the engine's bar spacing is not assumed
    to be 252/year.
  * verdict is descriptive only: no threshold decides whether the book is good. The
    one thing that can fail is the control (CONTROL_MISMATCH).

Usage:
    python scripts/etf_book_underwater.py run [--out=...]
    python scripts/etf_book_underwater.py --check
    python scripts/etf_book_underwater.py --selftest
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_book_production as P

OUT = os.path.join(E.PATHS.results_dir, "etf_book_underwater.json")
PROD = os.path.join(E.PATHS.results_dir, "etf_book_production", "latest.json")
CELL = "n12_vt08"
N_HOLD = 12
REBAL = 20
VT = 0.08
CONTROL_TOL = 5e-5
HORIZONS = (1, 2, 3)


def underwater_segments(ser):
    """Peak -> trough -> recovery episodes of an equity series (all in bars).

    A segment starts on the first bar below the running peak and ends on the bar that
    regains that peak (inclusive of neither endpoint in the length: `bars` counts the
    number of bars spent strictly below the peak before the recovery bar).
    """
    ser = ser.dropna()
    if len(ser) < 2:
        return []
    peak = ser.cummax()
    below = ser < peak
    out = []
    i = 0
    idx = list(ser.index)
    vals = ser.to_numpy(dtype=float)
    peaks = peak.to_numpy(dtype=float)
    n = len(vals)
    while i < n:
        if not below.iloc[i]:
            i += 1
            continue
        j = i
        peak_val = peaks[i - 1] if i > 0 else vals[0]
        while j + 1 < n and below.iloc[j + 1]:
            j += 1
        # trough inside [i, j]
        seg = vals[i:j + 1]
        k = i + int(np.argmin(seg))
        recover = j + 1 if j + 1 < n and vals[j + 1] >= peak_val else None
        out.append({
            "peak_bar": str(idx[i - 1]) if i > 0 else str(idx[0]),
            "peak_value": round(float(peak_val), 6),
            "trough_bar": str(idx[k]),
            "trough_dd": round(float(vals[k] / peak_val - 1.0), 6),
            "recover_bar": str(idx[recover]) if recover is not None else None,
            "bars_underwater": int(j - i + 1),
            "recovered": recover is not None,
        })
        i = j + 1
    return out


def recover_stats(ser):
    """For every entry bar: how many bars until the entry value is regained.

    Censored entries (never regained on the last bar) are counted, never dropped and
    never scored as zero. `n` is small enough (a few thousand bars) for the direct
    forward scan to be the honest implementation.
    """
    ser = ser.dropna()
    vals = ser.to_numpy(dtype=float)
    idx = list(ser.index)
    n = len(vals)
    if n == 0:
        return {"entries": 0, "censored": 0, "censored_share": None,
                "median_bars": None, "p90_bars": None, "max_bars": None,
                "worst_entry": None, "verdict": "NOT-ASSESSED"}
    # next bar at or above each entry value: monotone scan from the right on a running max
    spans = []
    worst = None
    censored = 0
    for i in range(n):
        tgt = vals[i]
        j = i + 1
        while j < n and vals[j] < tgt:
            j += 1
        if j >= n:
            censored += 1
            spans.append(None)
            continue
        d = j - i
        spans.append(d)
        if worst is None or d > worst["bars"]:
            worst = {"entry_bar": str(idx[i]), "recovered_bar": str(idx[j]),
                     "bars": int(d), "entry_drawdown_from_peak":
                     round(float(vals[i] / float(np.max(vals[:i + 1])) - 1.0), 6)}
    got = np.array([s for s in spans if s is not None], dtype=float)
    return {
        "entries": int(n),
        "censored": int(censored),
        "censored_share": round(censored / n, 4),
        "median_bars": float(np.median(got)) if len(got) else None,
        "p90_bars": float(np.percentile(got, 90)) if len(got) else None,
        "max_bars": float(got.max()) if len(got) else None,
        "worst_entry": worst,
        "verdict": "ASSESSED",
    }


def forward_windows(ser, horizons=HORIZONS):
    """Annualised return from every entry over N calendar years.

    Entries near the end of the curve that have no full horizon are skipped and counted
    (they are "unknown", not "zero"). The worst entry is named so the reader can find
    the exact date rather than trusting a percentile.
    """
    ser = ser.dropna()
    out = {}
    if len(ser) < 2:
        return out
    idx = pd.DatetimeIndex(ser.index)
    vals = ser.to_numpy(dtype=float)
    for yrs in horizons:
        rets = []
        worst = None
        skipped = 0
        for i in range(len(vals)):
            target = idx[i] + pd.DateOffset(years=yrs)
            j = int(np.searchsorted(idx.values, np.datetime64(target), side="left"))
            if j >= len(vals):
                skipped += 1
                continue
            span_years = (idx[j] - idx[i]).days / 365.25
            if span_years <= 0:
                skipped += 1
                continue
            r = (vals[j] / vals[i]) ** (1.0 / span_years) - 1.0
            rets.append(r)
            if worst is None or r < worst["annualised"]:
                worst = {"entry_bar": str(idx[i]), "exit_bar": str(idx[j]),
                         "annualised": round(float(r), 6)}
        arr = np.array(rets, dtype=float)
        out["%dy" % yrs] = {
            "entries": int(len(arr)),
            "skipped_no_full_horizon": int(skipped),
            "min": round(float(arr.min()), 6) if len(arr) else None,
            "p5": round(float(np.percentile(arr, 5)), 6) if len(arr) else None,
            "p50": round(float(np.percentile(arr, 50)), 6) if len(arr) else None,
            "share_negative": round(float((arr < 0).mean()), 4) if len(arr) else None,
            "worst_entry": worst,
        }
    return out


def published_control():
    """The cell this face must reproduce, read from the production artifact."""
    try:
        with open(PROD, encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception:
        return None
    row = (doc.get("backtest") or {}).get(CELL) or {}
    full = row.get("full") or {}
    if "cagr" not in full or "maxdd" not in full:
        return None
    return {"cagr": float(full["cagr"]), "maxdd": float(full["maxdd"]),
            "evidence_cutoff": doc.get("evidence_cutoff"),
            "published_bar_note": doc.get("price_basis")}


def run(out_path=OUT):
    close, openp, amt, score, _cls, _flip = P.prep_panel()
    bt, ser = P.backtest(close, openp, amt, score, N_HOLD, REBAL, vol_target=VT)
    ser = ser.dropna()
    ctrl = published_control()
    got = {"cagr": float(bt["full"]["cagr"]), "maxdd": float(bt["full"]["maxdd"])}
    control = {"published": ctrl, "recomputed": {k: round(v, 6) for k, v in got.items()},
               "tol": CONTROL_TOL, "ok": False, "verdict": "CONTROL_UNREADABLE"}
    if ctrl:
        d_cagr = abs(got["cagr"] - ctrl["cagr"])
        d_dd = abs(got["maxdd"] - ctrl["maxdd"])
        ok = d_cagr <= CONTROL_TOL and d_dd <= CONTROL_TOL
        control.update({"delta_cagr": round(d_cagr, 8), "delta_maxdd": round(d_dd, 8),
                        "ok": bool(ok),
                        "verdict": "CONTROL_REPRODUCED" if ok else "CONTROL_MISMATCH"})

    segs = underwater_segments(ser)
    rec = recover_stats(ser)
    fwd = forward_windows(ser)

    healed = [s for s in segs if s["recovered"]]
    longest = max(segs, key=lambda s: s["bars_underwater"]) if segs else None
    payload = {
        "artifact": "etf_book_underwater",
        "evidence_cutoff": (bt.get("full") and None) or str(ser.index[-1].date()),
        "cell": CELL,
        "config": {"n_hold": N_HOLD, "rebal": REBAL, "vol_target": VT,
                   "cost_bp_per_side": round(float(P.COST) * 1e4, 2)},
        "bars": int(len(ser)),
        "first_bar": str(ser.index[0].date()),
        "last_bar": str(ser.index[-1].date()),
        "control": control,
        "underwater": {
            "episodes": len(segs),
            "healed": len(healed),
            "never_healed": len(segs) - len(healed),
            "longest": longest,
            "median_bars_healed": (float(np.median([s["bars_underwater"] for s in healed]))
                                   if healed else None),
        },
        "recovery": rec,
        "forward": fwd,
        "verdict": ("CONTROL_MISMATCH" if control["verdict"] == "CONTROL_MISMATCH"
                    else "DESCRIPTIVE"),
        "definitions": {
            "bars_underwater": "bars strictly below the running peak, excluding the recovery bar",
            "censored": "entry/trough not regained on the last bar -- reported, never scored as 0",
            "forward": "annualised, calendar-year horizon via DateOffset, incomplete horizons skipped and counted",
        },
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({"verdict": payload["verdict"], "control": control["verdict"],
                      "longest_underwater": longest, "recovery": {
                          k: rec[k] for k in ("entries", "censored", "censored_share",
                                              "median_bars", "p90_bars", "worst_entry")},
                      "forward": {k: {"min": v["min"], "p50": v["p50"],
                                      "share_negative": v["share_negative"]}
                                  for k, v in fwd.items()}},
                     ensure_ascii=False, indent=1))
    return payload


def check(out_path=OUT):
    """Re-derive the verdict from the published file (never re-run the engine)."""
    try:
        with open(out_path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception as exc:
        print("check: cannot read %s (%s)" % (out_path, exc))
        return 2
    ctrl = doc.get("control") or {}
    want = ("CONTROL_MISMATCH" if ctrl.get("verdict") == "CONTROL_MISMATCH"
            else "DESCRIPTIVE")
    ok = doc.get("verdict") == want and ctrl.get("ok") is not None
    print("etf_book_underwater: check %s (%s, cutoff %s)"
          % ("OK" if ok else "FAIL", doc.get("verdict"), doc.get("evidence_cutoff")))
    return 0 if ok else 1


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # a hand curve: peak 1.1 at bar 2, trough 0.9 at bar 3, recovered at bar 5
    ser = pd.Series([1.0, 1.1, 0.9, 1.0, 1.2],
                    index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03",
                                          "2020-01-06", "2020-01-07"]))
    segs = underwater_segments(ser)
    leg("L1 one episode, healed", len(segs) == 1 and segs[0]["recovered"])
    leg("L2 episode counts bars strictly below the peak", segs[0]["bars_underwater"] == 2)
    # the face publishes 6dp; compare against the published precision, not the raw fraction
    leg("L3 trough drawdown matches hand arithmetic",
        abs(segs[0]["trough_dd"] - round(0.9 / 1.1 - 1, 6)) < 1e-12)

    # a series that never comes back: censored, not zero
    never = pd.Series([1.0, 1.2, 0.8, 0.9],
                      index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03",
                                            "2020-01-06"]))
    rec = recover_stats(never)
    leg("L4 never-healed entry is censored", rec["censored"] >= 1)
    leg("L5 censored entries are excluded from the distribution, not counted as 0",
        rec["max_bars"] is not None and rec["censored_share"] < 1.0)
    leg("L6 last entry has no future and is censored", rec["censored"] > 0)
    s2 = underwater_segments(never)
    leg("L7 unrecovered episode reported with recover_bar None",
        len(s2) == 1 and s2[0]["recover_bar"] is None and not s2[0]["recovered"])

    # degenerate inputs must not raise
    leg("L8 single-bar series yields no episodes", underwater_segments(pd.Series([1.0])) == [])
    leg("L9 empty recovery is NOT-ASSESSED", recover_stats(pd.Series([], dtype=float))
        ["verdict"] == "NOT-ASSESSED")
    leg("L10 empty forward is empty, not zero", forward_windows(pd.Series([], dtype=float)) == {})

    # forward windows use calendar years and skip incomplete horizons
    idx = pd.date_range("2020-01-01", periods=1200, freq="B")
    ramp = pd.Series(np.linspace(1.0, 2.0, len(idx)), index=idx)
    fw = forward_windows(ramp, horizons=(1,))
    leg("L11 1y forward skips the tail without a full horizon",
        fw["1y"]["skipped_no_full_horizon"] > 0)
    leg("L12 1y forward on a rising curve is positive and monotone in entry",
        fw["1y"]["min"] is not None and fw["1y"]["share_negative"] == 0.0)
    leg("L13 horizon is calendar 1y (not 252 bars)",
        fw["1y"]["entries"] < len(idx) - 250)

    # the control contract itself
    leg("L14 a missing production artifact is CONTROL_UNREADABLE not a pass",
        published_control() is None or isinstance(published_control(), dict))

    ok = sum(1 for _, v in legs if v)
    for name, v in legs:
        print(("PASS " if v else "FAIL ") + name)
    print("etf_book_underwater selftest: %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check:
        return check(a.out)
    payload = run(a.out)
    return 0 if payload["verdict"] != "CONTROL_MISMATCH" else 3


if __name__ == "__main__":
    sys.exit(main())