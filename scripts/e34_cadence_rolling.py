"""E34-C cadence question, dated instead of averaged: rolling 3-year
monthly-vs-quarterly relative on the five-member desk ladder.

E33 answered Q2 CADENCE with three windows (full / 2016+ / 2018+) and got a
wash with a sign flip. A three-window read cannot say *when* the flip happened
or whether it is one episode or a regime. This runner replays the same two
cadence curves once and then reads every trailing 36-month window, so the
flips are dated.

Accounting is imported from E33 (which itself imports E24/E27) -- nothing is
re-implemented here:
  * e33.cadence_indices / e27.simulate -> the two curves
  * e33._delta_bp / base.metrics / base.monthly_relative -> the stats

Honest notes:
  * overlapping 36-month windows: neighbouring samples share 35 months, so the
    "number of positive windows" is not an independent sample count.
  * the ETF population is today's surviving listing set (listing survivorship).
  * descriptive census only: no gate, no verdict, no prereg, no trial count.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e24_ladder_weighting as base  # noqa: E402
import e27_universe_expansion as e27  # noqa: E402
import e33_ladder_baseline as e33  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "e34_cadence_rolling")
WINDOW_MONTHS = 36


def cadence_curves(cal, closes, amounts, cash, cost_mult=1.0,
                   cadences=("monthly", "quarterly")):
    prices = {s: [closes[s].get(d) for d in cal] for s in closes}
    ams = {s: [amounts[s].get(d) for d in cal] for s in closes}
    curves, auxes = {}, {}
    for cad in cadences:
        rebal = e33.cadence_indices(cal, cad)
        curve, aux, _ = e27.simulate(cal, prices, ams, base.LADDER, cash, None,
                                     cost_mult, {}, rebal=rebal)
        curves[cad] = curve
        auxes[cad] = dict(aux, rebalance_days=len(rebal))
    return curves, auxes


def month_end_samples(curve):
    """map date -> (bar index, value) at every month end present in the curve."""
    dates = [d for d, _ in curve]
    out = {}
    for i, d in enumerate(dates):
        nxt = dates[i + 1] if i + 1 < len(dates) else None
        if nxt is None or nxt[:7] != d[:7]:
            out[d] = (i, curve[i][1])
    return out


def rolling_relative(curve_a, curve_b, window_months=WINDOW_MONTHS):
    """trailing window_months relative annualised (bp/yr) of a vs b."""
    sa, sb = month_end_samples(curve_a), month_end_samples(curve_b)
    common = [d for d in sa if d in sb]
    rows = []
    for i in range(window_months, len(common)):
        d0, d1 = common[i - window_months], common[i]
        i0, v0a = sa[d0]
        i1, v1a = sa[d1]
        v0b, v1b = sb[d0][1], sb[d1][1]
        if v0a <= 0 or v0b <= 0:
            continue
        rel = (v1a / v0a) / (v1b / v0b) - 1.0
        # annualise on the realised bar span (geometric, not linear): a
        # 36-month-end window spans up to ~3.1 calendar years.
        years = (i1 - i0) / 252.0
        rel_ann = (1.0 + rel) ** (1.0 / years) - 1.0
        rows.append({"asof": d1, "window_start": d0,
                     "rel_cum_pct": round(rel * 100.0, 3),
                     "rel_bp_annualised": round(rel_ann * 1e4, 1)})
    return rows


def flips(rows):
    out = []
    for prev, cur in zip(rows, rows[1:]):
        if prev["rel_bp_annualised"] * cur["rel_bp_annualised"] < 0:
            out.append({"between": [prev["asof"], cur["asof"]],
                        "from_bp": prev["rel_bp_annualised"],
                        "to_bp": cur["rel_bp_annualised"]})
    return out


def era_of(asof):
    y = int(asof[:4])
    if y <= 2015:
        return "pre-2016"
    if y <= 2017:
        return "2016-2017"
    if y <= 2020:
        return "2018-2020"
    if y <= 2023:
        return "2021-2023"
    return "2024+"


def era_table(rows):
    buckets = {}
    for r in rows:
        buckets.setdefault(era_of(r["asof"]), []).append(r["rel_bp_annualised"])
    out = {}
    for k in ("pre-2016", "2016-2017", "2018-2020", "2021-2023", "2024+"):
        v = buckets.get(k) or []
        if not v:
            out[k] = {"n": 0}
            continue
        out[k] = {"n": len(v), "mean_bp": round(sum(v) / len(v), 1),
                  "min_bp": min(v), "max_bp": max(v),
                  "positive_n": sum(1 for x in v if x > 0)}
    return out


def run(cost_mult=1.0):
    cal, closes, amounts = base.load_panel()
    cash = base.load_cash_series(cal)
    if not cal:
        raise SystemExit("empty calendar")
    curves, auxes = cadence_curves(cal, closes, amounts, cash, cost_mult)
    rows = rolling_relative(curves["monthly"], curves["quarterly"])
    years = len(cal) / 252.0
    face = {
        "study": "e34_cadence_rolling",
        "evidence_cutoff": cal[-1],
        "start": cal[0],
        "bars": len(cal),
        "years": round(years, 2),
        "members": base.LADDER,
        "window_months": WINDOW_MONTHS,
        "cost_mult": cost_mult,
        "cost_bp_per_side": base.COST_BP_SIDE,
        "cadence_aux": {k: {"rebalances": v["rebalances"],
                            "rebalance_days": v["rebalance_days"],
                            "turnover_total": round(v["turnover_total"], 3),
                            "cost_paid_frac": round(v["cost_paid_frac"], 6)}
                        for k, v in auxes.items()},
        "full_sample": {
            "monthly_metrics": base.metrics(curves["monthly"], years),
            "quarterly_metrics": base.metrics(curves["quarterly"], years),
            "quarterly_minus_monthly_bp_annualised": e33._delta_bp(
                curves["quarterly"], curves["monthly"], years),
            "quarterly_vs_monthly": base.monthly_relative(curves["quarterly"],
                                                          curves["monthly"]),
        },
        "rolling": rows,
        "flips": flips(rows),
        "era_table": era_table(rows),
        "honest": [
            "descriptive census only: no gate, no verdict, no prereg, no trial count consumed",
            "overlapping 36-month windows: adjacent samples share 35 months, so window counts are not independent samples",
            "ETF population is today's surviving listing set (listing survivorship)",
            "13.041bp/side charged on turnover; idle share accrues at the GC001 repo close",
            "quarterly rebalances on the last trading day of Mar/Jun/Sep/Dec",
        ],
    }
    return face


def write_face(face, tag):
    os.makedirs(OUTDIR, exist_ok=True)
    p = os.path.join(OUTDIR, "CADENCE-ROLLING-3Y-%s.json" % tag)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    return os.path.basename(p)


def selftest():
    from datetime import timedelta
    ok = 0
    tot = 0

    # 1. identical curves -> zero relative in every window
    cal = []
    d = datetime(2015, 1, 1)
    while len(cal) < 900:
        if d.weekday() < 5:
            cal.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)
    c = [(dt, 1.0 + 0.001 * i) for i, dt in enumerate(cal)]
    rows = rolling_relative(c, c)
    assert rows and all(abs(r["rel_bp_annualised"]) < 1e-9 for r in rows)
    ok += 1; tot += 1

    # 2. constant annual alpha reproduces itself: a = b * 1.02^years
    a = [(dt, v * (1.02 ** (i / 252.0))) for i, (dt, v) in enumerate(c)]
    rows2 = rolling_relative(a, c)
    assert all(abs(r["rel_bp_annualised"] - 200.0) < 1.0 for r in rows2), rows2[:2]
    ok += 1; tot += 1

    # 3. no window before the first full 36 months
    assert rows and rows[0]["window_start"] < rows[0]["asof"]
    total_months = len(month_end_samples(c))
    assert len(rows) == total_months - WINDOW_MONTHS
    ok += 1; tot += 1

    # 4. flip detection fires exactly on a constructed crossing
    fake = [{"asof": "2020-01", "rel_bp_annualised": 100.0},
            {"asof": "2020-02", "rel_bp_annualised": 50.0},
            {"asof": "2020-03", "rel_bp_annualised": -10.0},
            {"asof": "2020-04", "rel_bp_annualised": -20.0},
            {"asof": "2020-05", "rel_bp_annualised": 5.0}]
    fl = flips(fake)
    assert len(fl) == 2
    assert fl[0]["between"] == ["2020-02", "2020-03"]
    ok += 1; tot += 1

    # 5. era buckets are exhaustive and ordered on the samples
    et = era_table(rows)
    assert sum(v["n"] for v in et.values()) == len(rows)
    assert et["2018-2020"]["n"] > 0
    ok += 1; tot += 1

    # 6. month_end_samples keeps exactly the last bar of each calendar month
    ms = month_end_samples([("2020-01-30", 1.0), ("2020-01-31", 2.0),
                            ("2020-02-28", 3.0)])
    assert ms["2020-01-31"] == (1, 2.0) and ms["2020-02-28"] == (2, 3.0)
    assert "2020-01-30" not in ms
    ok += 1; tot += 1

    print("selftest %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--cost-mult", type=float, default=1.0)
    ap.add_argument("--tag", default=None)
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    face = run(cost_mult=args.cost_mult)
    tag = args.tag or face["evidence_cutoff"].replace("-", "")
    name = write_face(face, tag)
    print(json.dumps({"face": name,
                      "full_sample_bp": face["full_sample"]["quarterly_minus_monthly_bp_annualised"],
                      "windows": len(face["rolling"]),
                      "flips": len(face["flips"])}, ensure_ascii=False))
    for k, v in face["era_table"].items():
        print("era %-10s n=%s mean %s bp/yr (positive %s)" % (
            k, v.get("n"), v.get("mean_bp"), v.get("positive_n")))
    for f in face["flips"]:
        print("flip %s -> %s: %s -> %s bp/yr" % (f["between"][0], f["between"][1],
                                                 f["from_bp"], f["to_bp"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))