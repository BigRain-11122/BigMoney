"""W22 ETF holiday feasibility census (bm-b r1089).

Question (descriptive, exploratory): the frozen W22 confirm family
(hol_pre1 x h{3,4}) was measured on the daily equal-weight stock face.
Does the same pre-holiday lift exist in the ETF universe we actually
trade (5-member frozen ladder: 510300/510050/510500/512100/588000)?

No prereg edit, no judgment, no pool entry: this is a feasibility census
so that a 2-year forward accrual is not spent blind. Honest limits:
ETF listing histories are short, ETF cross-section is small, and the
holiday definition is imported verbatim from seasonal_calendar_census
(gap >= 4 calendar days) so window counting cannot drift from E23/W22.

Verdict vocabulary: FEASIBLE / WEAK / ABSENT, and it is *not* a judgment.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
from datetime import datetime, timezone, timedelta

import numpy as np

_ROOTH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOTH not in sys.path:
    sys.path.insert(0, _ROOTH)

from scripts.seasonal_calendar_census import (  # noqa: E402  single-source
    annotate_calendar, era_of, HOLIDAY_GAP_DAYS, now_iso,
)

DATA_DIR = os.path.join(_ROOTH, "data", "daily")
OUT_DIR = os.path.join(_ROOTH, "results", "w22_etf_holiday_census")
CAL_SYMBOL = "sh510300.csv"
TRADED = ("sh510300", "sh510050", "sh510500", "sh512100", "sh588000")
HORIZONS = (3, 4)
MAX_ABS_R = 0.75


def read_etf(path: str):
    """-> (dates[list[str]], closes[np.ndarray]) ; skips malformed rows."""
    dates, closes = [], []
    with open(path, "r", encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        for row in rd:
            try:
                c = float(row["close"])
            except (KeyError, TypeError, ValueError):
                continue
            if not math.isfinite(c) or c <= 0:
                continue
            dates.append(row["date"][:10])
            closes.append(c)
    return dates, np.asarray(closes, dtype="float64")


def forward_grid(pos, closes, n_cal, h: int):
    """Close-to-close h-bar forward return on the calendar grid."""
    full = np.full(n_cal, np.nan)
    full[pos] = closes
    fwd = np.full(n_cal, np.nan)
    if n_cal > h:
        fwd[:-h] = full[h:] / full[:-h] - 1.0
    return fwd


def _stats(vals) -> dict:
    a = np.asarray([v for v in vals if v is not None and math.isfinite(v)],
                   dtype="float64")
    n = int(a.size)
    if n == 0:
        return {"n": 0}
    m = float(a.mean())
    sd = float(a.std(ddof=1)) if n > 1 else float("nan")
    se = sd / math.sqrt(n) if n > 1 else float("nan")
    return {"n": n, "mean": m, "sd": sd if n > 1 else None,
            "se": se if n > 1 else None,
            "t": (m / se) if (n > 1 and se > 0) else None,
            "win": float((a > 0).mean())}


def census() -> dict:
    cal_dates, cal_close = read_etf(os.path.join(DATA_DIR, CAL_SYMBOL))
    cal = [datetime.strptime(d, "%Y-%m-%d").date() for d in cal_dates]
    variants, breaks = annotate_calendar(cal)
    n_cal = len(cal)
    cal_pos = {d.strftime("%Y-%m-%d"): i for i, d in enumerate(cal)}

    pre_days = [i for i, d in enumerate(cal) if "hol_pre1" in variants[d]]
    pre2_days = [i for i, d in enumerate(cal) if "hol_pre2" in variants[d]]

    files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".csv"))
    per_etf = {}
    # window-level accumulation: value per (window, horizon) = mean across ETFs
    win_vals = {h: {} for h in HORIZONS}          # (h, window_idx) -> [vals]
    win_vals_2 = {h: {} for h in HORIZONS}
    base_vals = {h: [] for h in HORIZONS}
    coverage = {"files": 0, "files_used": 0, "bad_files": 0}

    for fn in files:
        sym = fn[:-4]
        coverage["files"] += 1
        try:
            dates, closes = read_etf(os.path.join(DATA_DIR, fn))
        except Exception:
            coverage["bad_files"] += 1
            continue
        if len(closes) < 120:
            continue
        pos = np.array([cal_pos[d] for d in dates if d in cal_pos],
                       dtype="int64")
        if pos.size != len(closes):
            keep = np.array([d in cal_pos for d in dates])
            closes = closes[keep]
            pos = np.array([cal_pos[d] for d in dates if d in cal_pos],
                           dtype="int64")
        if pos.size < 120:
            continue
        coverage["files_used"] += 1
        rec = {}
        for h in HORIZONS:
            fwd = forward_grid(pos, closes, n_cal, h)
            ok_fin = np.isfinite(fwd) & (np.abs(fwd) < MAX_ABS_R)
            wvals = []
            for wi, t in enumerate(pre_days):
                if t < n_cal and ok_fin[t]:
                    v = float(fwd[t])
                    wvals.append(v)
                    win_vals[h].setdefault(wi, []).append(v)
            w2vals = []
            for wi, t in enumerate(pre2_days):
                if t < n_cal and ok_fin[t]:
                    w2vals.append(float(fwd[t]))
                    win_vals_2[h].setdefault(wi, []).append(float(fwd[t]))
            bsample = fwd[np.isfinite(fwd) & (np.abs(fwd) < MAX_ABS_R)]
            if h == 4 and bsample.size:
                step = max(1, bsample.size // 400)
                base_vals[h].extend(bsample[::step].tolist())
            rec["h%d" % h] = _stats(wvals)
            rec["h2pre%d" % h] = _stats(w2vals)
        per_etf[sym] = rec

    out = {"generated": now_iso(), "evidence_cutoff": cal_dates[-1],
           "calendar_days": n_cal, "calendar_start": cal_dates[0],
           "holiday_gap_days": HOLIDAY_GAP_DAYS,
           "n_breaks": len(breaks), "n_pre1_windows": len(pre_days),
           "n_pre2_windows": len(pre2_days),
           "coverage": coverage, "horizons": list(HORIZONS)}

    def _window_stats(bucket):
        # honest day-clustered stats: one observation per window
        series = [float(np.mean(v)) for v in bucket.values() if v]
        return _stats(series)

    out["window_level"] = {"hol_pre1": {("h%d" % h): _window_stats(win_vals[h])
                                        for h in HORIZONS},
                           "hol_pre2": {("h%d" % h): _window_stats(win_vals_2[h])
                                        for h in HORIZONS}}
    out["baseline_all_days"] = {"h4": _stats(base_vals[4])}

    # per-era on the pre1 window level
    eras = {}
    for wi, t in enumerate(pre_days):
        yr = cal[t].year
        eras.setdefault(era_of(yr), {h: [] for h in HORIZONS})
    for h in HORIZONS:
        for wi, vals in win_vals[h].items():
            if not vals:
                continue
            yr = cal[pre_days[wi]].year
            eras.setdefault(era_of(yr), {hh: [] for hh in HORIZONS})
            eras[era_of(yr)][h].append(float(np.mean(vals)))
    out["by_era_pre1"] = {e: {("h%d" % h): _stats(v)
                              for h, v in sorted(d.items())}
                          for e, d in sorted(eras.items())}

    # traded ladder detail + cross-ETF breadth
    out["traded"] = {s: per_etf.get(s) for s in TRADED}
    breadth = {}
    for h in HORIZONS:
        pos_share = [1 if (rec.get("h%d" % h, {}) or {}).get("mean", 0) > 0
                     else 0 for rec in per_etf.values()]
        breadth["h%d" % h] = {"etfs": len(pos_share),
                             "positive_share": (sum(pos_share) / len(pos_share))
                             if pos_share else None}
    out["breadth"] = breadth
    out["per_etf_n"] = len(per_etf)

    # verdict (descriptive only)
    wl = out["window_level"]["hol_pre1"]
    t4 = wl["h4"].get("t") or 0.0
    m4 = wl["h4"].get("mean") or 0.0
    b4 = out["baseline_all_days"]["h4"].get("mean") or 0.0
    tr = [out["traded"][s]["h4"] for s in TRADED
          if out["traded"].get(s) and out["traded"][s].get("h4", {}).get("n")]
    tr_pos = sum(1 for r in tr if (r.get("mean") or 0) > 0)
    if t4 >= 2.0 and tr_pos >= 3:
        verdict = "FEASIBLE"
    elif t4 >= 1.0 or tr_pos >= 3:
        verdict = "WEAK"
    else:
        verdict = "ABSENT"
    out["verdict"] = verdict
    out["verdict_inputs"] = {"window_h4_mean": m4, "window_h4_t": t4,
                             "baseline_h4_mean": b4,
                             "traded_positive": tr_pos,
                             "traded_measured": len(tr)}
    out["honest_notes"] = [
        "descriptive feasibility census; NOT a judgment and no pool entry",
        "ETF histories are short and the traded ladder is 5 members: low power",
        "windows overlap in calendar time; window-level t is day-clustered but "
        "still autocorrelated across neighbouring breaks",
        "extreme moves |r|>=0.75 dropped (split/typo guard), disclosed counts "
        "not tracked per file",
    ]
    return out


def selftest() -> int:
    # synthetic: 10 calendar days, break before day 5 -> hol_pre1 == day 4
    cal = [datetime(2020, 1, d) for d in (1, 2, 3, 6, 7, 13, 14, 15, 16, 17)]
    variants, breaks = annotate_calendar(cal)
    assert len(breaks) == 1, breaks
    pre = [d for d in cal if "hol_pre1" in variants[d]]
    assert pre == [datetime(2020, 1, 7)], pre          # last day before the break
    closes = np.array([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9])
    pos = np.arange(len(cal))
    f4 = forward_grid(pos, closes, len(cal), 4)
    assert abs(f4[4] - (1.8 / 1.4 - 1)) < 1e-12, f4[4]   # h bars == index+4
    assert np.isnan(f4[7]), "tail must be NaN, not fabricated"
    s = _stats([0.01, 0.02, -0.01])
    assert s["n"] == 3 and abs(s["mean"] - 0.0066666667) < 1e-6, s
    assert _stats([]) == {"n": 0}
    # read_etf round-trip on a temp file
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                     encoding="utf-8", newline="") as fh:
        fh.write("date,open,high,low,close,volume,amount\n")
        fh.write("2020-01-01,1,1,1,1.0,0,0\n")
        fh.write("2020-01-02,1,1,1,bad,0,0\n")
        fh.write("2020-01-03,1,1,1,1.5,0,0\n")
        tmp = fh.name
    try:
        d, c = read_etf(tmp)
        assert d == ["2020-01-01", "2020-01-03"], d
        assert list(c) == [1.0, 1.5], c
    finally:
        os.unlink(tmp)
    print("selftest 8/8 PASS")
    return 0


def main(argv) -> int:
    if "--selftest" in argv:
        return selftest()
    face = census()
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "face.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"verdict": face["verdict"],
                      "window_level": face["window_level"]["hol_pre1"],
                      "baseline": face["baseline_all_days"],
                      "traded": face["verdict_inputs"],
                      "out": path}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))