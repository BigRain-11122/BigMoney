#!/usr/bin/env python3
"""E12: repo month-end rate pulse probe (descriptive face, zero prereg).

Queue row: state/queue/explore.md E12 (repo GC001 month-end pulse -> cash-leg
timing gate CANDIDATE). Consumes the existing REPO_PANEL ladder (collected by
scripts/update_repo.py, spec research/shortline/REPO_PANEL.md). Zero network,
zero panel write, zero judged claim: any judged face needs its own prereg
ticket (PREREG_TEMPLATE front door + forward window >= 12 months per T-67 s2
+ family-exception three questions vs r947/r938 sentiment-timing closures;
this is a NEW data-source channel, same-lane skin-change still forbidden).

Measures:
  1. month-end window pulse: last N trading days of month, close-rate dist
     vs all-day baseline (N in 1..3; primary window = last 1 day).
  2. quarter-end split: Mar/Jun/Sep/Dec month-ends vs other month-ends.
  3. pre-long-holiday pulse: day before a market gap (gap>=3 = weekend+short
     holiday diluted label; gap>=5 = true long holiday: CNY / National Day).
  4. term-ladder slope at month-ends: GC007 close - GC001 close (pp).
  5. spike persistence: day close >= p90(all) -> next-day close distribution.
  6. yearly pulse magnitude: median month-end-window close per year vs that
     year's all-day median (decay/growth check).
  7. 53.44 anchor verification (2015-02-10 pre-Spring-Festival).
  8. top-10 spike days labeled by (month-end, quarter-end, pre-holiday).
Selftest: hermetic fixture ladder, no network, no panel write.
"""
import csv
import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL_DIR = os.path.join(ROOT, "data", "repo_daily")
OUT_PATH = os.path.join(ROOT, "results", "repo_monthend_pulse_probe.json")
ANCHOR_DATE = "2015-02-10"
ANCHOR_CLOSE = 53.44


def load_series(name):
    """Load one ladder member CSV -> list of dicts sorted by date."""
    path = os.path.join(PANEL_DIR, name + ".csv")
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "date": r["date"],
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "volume": float(r["volume"]),
            })
    rows.sort(key=lambda x: x["date"])
    return rows


def quantile(sorted_vals, q):
    if not sorted_vals:
        return None
    idx = min(len(sorted_vals) - 1, max(0, int(round(q * (len(sorted_vals) - 1)))))
    return sorted_vals[idx]


def stats(vals):
    sv = sorted(vals)
    n = len(sv)
    if n == 0:
        return {"n": 0}
    med = sv[n // 2] if n % 2 else (sv[n // 2 - 1] + sv[n // 2]) / 2.0
    return {
        "n": n,
        "mean": round(sum(sv) / n, 3),
        "median": round(med, 3),
        "p75": round(quantile(sv, 0.75), 3),
        "p90": round(quantile(sv, 0.90), 3),
        "p95": round(quantile(sv, 0.95), 3),
        "max": round(sv[-1], 3),
    }


def month_end_mask(dates, n):
    """Boolean list: True for the last n trading days of each month."""
    if not dates:
        return []
    key = [(d[:4], d[5:7]) for d in dates]
    last_idx_of_month = {}
    for i, k in enumerate(key):
        last_idx_of_month[k] = i
    out = [False] * len(dates)
    for k, last in last_idx_of_month.items():
        for j in range(max(0, last - n + 1), last + 1):
            if key[j] == k:
                out[j] = True
    return out


def quarter_end_mask(dates):
    """True for the last trading day of Mar/Jun/Sep/Dec."""
    out = [False] * len(dates)
    key = [(d[:4], d[5:7]) for d in dates]
    last_idx = {}
    for i, k in enumerate(key):
        last_idx[k] = i
    for k, i in last_idx.items():
        if k[1] in ("03", "06", "09", "12"):
            out[i] = True
    return out


def pre_long_holiday_mask(dates, min_gap=3):
    """True when the NEXT trading day is >= min_gap calendar days later.

    min_gap=3 catches weekends+short holidays (diluted label);
    min_gap=5 isolates true long holidays (CNY / National Day).
    """
    out = [False] * len(dates)
    for i in range(len(dates) - 1):
        d0 = date.fromisoformat(dates[i])
        d1 = date.fromisoformat(dates[i + 1])
        if (d1 - d0).days >= min_gap:
            out[i] = True
    return out


def run():
    gc001 = load_series("GC001")
    gc007 = load_series("GC007")
    dates = [r["date"] for r in gc001]
    closes = [r["close"] for r in gc001]
    ranges = [r["high"] - r["low"] for r in gc001]
    vols = [r["volume"] for r in gc001]
    cutoff = dates[-1]

    me1 = month_end_mask(dates, 1)
    me3 = month_end_mask(dates, 3)
    qe = quarter_end_mask(dates)
    pre_hol = pre_long_holiday_mask(dates, 3)
    pre_hol5 = pre_long_holiday_mask(dates, 5)

    base = stats(closes)
    base_med = base["median"]
    me1_closes = [c for c, m in zip(closes, me1) if m]
    me3_closes = [c for c, m in zip(closes, me3) if m]
    qe_closes = [c for c, m in zip(closes, qe) if m]
    non_qe_me = [c for c, m, q in zip(closes, me1, qe) if m and not q]
    hol_closes = [c for c, m in zip(closes, pre_hol) if m]
    hol5_closes = [c for c, m in zip(closes, pre_hol5) if m]
    me1_hol = [c for c, m, h in zip(closes, me1, pre_hol) if m and h]
    me1_nothol = [c for c, m, h in zip(closes, me1, pre_hol) if m and not h]

    # term-ladder slope (pp) on common dates
    gc007_map = {r["date"]: r["close"] for r in gc007}
    slope_all, slope_me1 = [], []
    for r in gc001:
        v = gc007_map.get(r["date"])
        if v is not None:
            s = v - r["close"]
            i = dates.index(r["date"]) if False else None  # noqa: F841
            slope_all.append(s)
    for i, r in enumerate(gc001):
        v = gc007_map.get(r["date"])
        if v is not None and me1[i]:
            slope_me1.append(v - r["close"])

    # spike persistence: close >= p90(all) -> next-day close
    p90 = base["p90"]
    spikes = [(i, closes[i]) for i in range(len(closes) - 1) if closes[i] >= p90]
    nxt = [closes[i + 1] for i, _ in spikes]
    nxt_med = sorted(nxt)[len(nxt) // 2] if nxt else None
    still_p75 = sum(1 for v in nxt if v >= base["p75"])

    # yearly pulse: median of month-end closes per year vs year all-day median
    yearly = {}
    for i, d in enumerate(dates):
        y = d[:4]
        yearly.setdefault(y, {"all": [], "me": []})
        yearly[y]["all"].append(closes[i])
        if me1[i]:
            yearly[y]["me"].append(closes[i])
    yearly_pulse = {}
    for y in sorted(yearly):
        a = sorted(yearly[y]["all"])
        m = sorted(yearly[y]["me"])
        if not m or not a:
            continue
        am = a[len(a) // 2]
        mm = m[len(m) // 2]
        yearly_pulse[y] = {
            "all_median": round(am, 3),
            "monthend_median": round(mm, 3),
            "ratio": round(mm / am, 3) if am else None,
        }

    # anchor verification
    anchor_row = next((r for r in gc001 if r["date"] == ANCHOR_DATE), None)
    anchor = None
    if anchor_row is not None:
        i = dates.index(ANCHOR_DATE)
        anchor = {
            "date": ANCHOR_DATE,
            "close": anchor_row["close"],
            "high": anchor_row["high"],
            "is_pre_long_holiday": bool(pre_hol[i]),
            "close_matches_53_44": abs(anchor_row["close"] - ANCHOR_CLOSE) < 1e-9,
        }

    # top-10 spike days labeled
    order = sorted(range(len(closes)), key=lambda i: -closes[i])[:10]
    top = [{
        "date": dates[i],
        "close": closes[i],
        "month_end": bool(me1[i]),
        "quarter_end": bool(qe[i]),
        "pre_long_holiday": bool(pre_hol[i]),
    } for i in order]

    excess = lambda s: round(s["median"] - base_med, 3) if s.get("n") else None
    result = {
        "probe": "E12 repo month-end rate pulse (descriptive face)",
        "status": "OK",
        "evidence_cutoff": cutoff,
        "panel_members": sorted(
            os.path.splitext(f)[0] for f in os.listdir(PANEL_DIR) if f.endswith(".csv")
        ),
        "baseline_all_days": base,
        "month_end_last1": stats(me1_closes),
        "month_end_last1_excess_pp": excess(stats(me1_closes)),
        "month_end_last3": stats(me3_closes),
        "month_end_last3_excess_pp": excess(stats(me3_closes)),
        "quarter_end_last1": stats(qe_closes),
        "quarter_end_last1_excess_pp": excess(stats(qe_closes)),
        "month_end_non_quarter": stats(non_qe_me),
        "month_end_non_quarter_excess_pp": excess(stats(non_qe_me)),
        "pre_long_holiday_gap3": stats(hol_closes),
        "pre_long_holiday_gap3_excess_pp": excess(stats(hol_closes)),
        "pre_long_holiday_gap5": stats(hol5_closes),
        "pre_long_holiday_gap5_excess_pp": excess(stats(hol5_closes)),
        "month_end_and_pre_holiday": stats(me1_hol),
        "month_end_not_pre_holiday": stats(me1_nothol),
        "intraday_range_baseline": stats(ranges),
        "intraday_range_month_end": stats([r for r, m in zip(ranges, me1) if m]),
        "volume_median_baseline": round(sorted(vols)[len(vols) // 2]),
        "volume_median_month_end": round(
            sorted([v for v, m in zip(vols, me1) if m])[max(0, sum(me1) // 2)]
        ) if sum(me1) else None,
        "ladder_slope_gc007_minus_gc001_all": stats(slope_all),
        "ladder_slope_gc007_minus_gc001_month_end": stats(slope_me1),
        "spike_p90_persistence": {
            "spike_days_n": len(spikes),
            "next_day_median": round(nxt_med, 3) if nxt_med is not None else None,
            "next_day_still_ge_p75": still_p75,
            "next_day_still_ge_p75_frac": round(still_p75 / len(spikes), 3) if spikes else None,
        },
        "yearly_pulse": yearly_pulse,
        "anchor_2015_02_10": anchor,
        "top10_spike_days": top,
        "zero_prereg_zero_judged": True,
        "family_law_note": (
            "new cash-leg rate channel; any judged face needs its own prereg + "
            "T-67 s2 forward window + family-exception three questions vs "
            "r947/r938 market-sentiment timing closures"
        ),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("probe OK -> %s (cutoff=%s, n=%d days)" % (OUT_PATH, cutoff, len(dates)))
    return 0


def selftest():
    """Hermetic legs: masks, stats, gap detection, anchor logic. No network."""
    ok = 0
    # L1: month_end_mask last-1 (fixture spanning 3 months)
    d = ["2024-01-26", "2024-01-29", "2024-01-30", "2024-01-31",
         "2024-02-01", "2024-02-02", "2024-02-28", "2024-03-01", "2024-03-29"]
    m = month_end_mask(d, 1)
    assert m == [False, False, False, True, False, False, True, False, True], m
    ok += 1
    # L2: month_end_mask last-3 same fixture
    m3 = month_end_mask(d, 3)
    # Jan has 4 days -> idx0 out; Feb has 3 -> all in; Mar has 2 -> both in
    assert m3 == [False, True, True, True, True, True, True, True, True], m3
    ok += 1
    # L3: quarter_end_mask
    q = quarter_end_mask(d)
    assert q == [False] * 8 + [True], q
    ok += 1
    # L4: pre_long_holiday_mask gap>=3 (weekend + holiday)
    d2 = ["2024-02-07", "2024-02-08", "2024-02-19", "2024-02-20"]
    h = pre_long_holiday_mask(d2, 3)
    assert h == [False, True, False, False], h
    ok += 1
    # L4b: gap>=5 isolates true long holidays (Fri->Mon=3 excluded)
    h5 = pre_long_holiday_mask(d2, 5)
    assert h5 == [False, True, False, False] and pre_long_holiday_mask(
        ["2024-02-08", "2024-02-11"], 5) == [False, False], h5
    ok += 1
    # L5: stats quantile sanity
    s = stats([1.0, 2.0, 3.0, 4.0, 10.0])
    assert s["n"] == 5 and s["median"] == 3.0 and s["max"] == 10.0, s
    ok += 1
    # L6: stats empty
    assert stats([]) == {"n": 0}
    ok += 1
    # L7: month-end mask on single-month singleton
    m1s = month_end_mask(["2024-05-10"], 1)
    assert m1s == [True], m1s
    ok += 1
    # L8: pre_long_holiday last day has no next-day info -> False
    h2 = pre_long_holiday_mask(["2024-02-08"])
    assert h2 == [False], h2
    ok += 1
    print("selftest: %d/9 OK" % ok)
    return 0 if ok == 9 else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())
