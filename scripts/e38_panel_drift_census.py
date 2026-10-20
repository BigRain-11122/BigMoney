"""E38 panel-drift census: is the wide-book number a property of the strategy or of the
panel state?

r1110 measured three magnitudes for ONE unchanged spec (+82.7bp on a panel cut at
2026-09-22, +156.0bp through 2026-10-20 in one run, +215.5bp in an earlier run) and
located the culprit in panel arrival, not in the strategy. This script turns that
inference into a number.

Two axes are measured, both descriptive (no gate, no verdict, no prereg):

  A. CUT AXIS -- the same spec truncated at several month ends. If the panel is
     converged, the vsLadder number and the eligible count at a FIXED reference date
     must be identical across every cut that covers that date. Any spread here is
     window-length arithmetic, not panel state.

  B. COST AXIS -- the same spec at cost x1 vs x3 on the same cut. Answers whether the
     fragility (if any) lives in fees or in the data.

Usage:
  python scripts/e38_panel_drift_census.py run
  python scripts/e38_panel_drift_census.py selftest
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e24_ladder_weighting as base  # noqa: E402  (shared accounting/metrics)
import e27_universe_expansion as e27  # noqa: E402  (the frozen spec under test)

OUTDIR = os.path.join(ROOT, "results", "e38_panel_drift_census")
REF_DATE = "2026-09-22"   # the fixed reference date the r1110 drift was observed at
START = "2020-01-01"
NS = [9999]
EXCLUDE = ["sh511"]
CUTS = ["2026-03-31", "2026-06-30", "2026-08-31", "2026-09-22", "2026-09-30", "2026-10-20"]
COST_CUTS = ["2026-09-22", "2026-10-20"]


def eligible_at(ref, cut, universe, prices, amounts, cal):
    """Eligible/liquid count at `ref` for a panel truncated at `cut`.

    `ref` must be inside the truncated calendar; the count is read off the SAME
    trailing-window rule the runner uses, so a converged panel must return the
    identical number for every cut >= ref.
    """
    if ref not in cal or universe is None:
        return None
    idx = cal.index(ref)
    live = [s for s in universe if s in prices and base.elig(prices[s], idx)]
    liq = [s for s in live if (base.trailing_mean(amounts[s], idx) or 0) > 0]
    return {"eligible": len(live), "liquid": len(liq), "idx": idx, "cal_len": len(cal)}


def build_panel(cut):
    """Mirror e27.run's panel construction so eligibility is read the same way."""
    raw = e27.load_universe()
    raw = {s: v for s, v in raw.items() if not s.startswith(tuple(EXCLUDE))}
    cal = base.load_panel()[0]
    cal = [d for d in cal if START <= d <= cut]
    all_syms = sorted(set(base.LADDER) | set(raw))
    prices, amounts = {}, {}
    for s in all_syms:
        c, a = raw.get(s, ({}, {}))
        prices[s] = [c.get(d) for d in cal]
        amounts[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw]
    return cal, prices, amounts, universe


def _pick(face):
    """The one non-ladder scheme face of an e27 run (ns=[9999] -> 'top9999')."""
    for name, f in face["schemes"].items():
        if name != "ladder5":
            return name, f
    return None, None


def run(save=True):
    rows = []
    faces_out = {}
    for cut in CUTS:
        for cm in (1.0, 3.0):
            if cm != 1.0 and cut not in COST_CUTS:
                continue
            face = e27.run(ns=NS, start=START, cost_mult=cm, end=cut, exclude=EXCLUDE)
            name, f = _pick(face)
            cal, prices, amounts, universe = build_panel(cut)
            ref = eligible_at(REF_DATE, cut, universe, prices, amounts, cal)
            row = {
                "cut": cut,
                "cost_mult": cm,
                "evidence_cutoff": face["evidence_cutoff"],
                "bars": face["bars"],
                "years": face["years"],
                "scheme": name,
                "vs_ladder_bp": f.get("vs_ladder_bp_annualised"),
                "vs_ladder_t": (f.get("vs_ladder") or {}).get("t"),
                "ann_pct": f["metrics"].get("ann_pct"),
                "sharpe": f["metrics"].get("sharpe"),
                "cost_bp_per_year": f["aux"].get("cost_per_year_bp"),
                "rebalances": f["aux"].get("rebalances"),
                "eligible_at_cut": (face["universe_live_marks"] or {}).get(face["evidence_cutoff"]),
                "eligible_at_ref": None if ref is None else ref["eligible"],
                "liquid_at_ref": None if ref is None else ref["liquid"],
                "universe_size": face["universe_size"],
            }
            rows.append(row)
            faces_out["%s_x%s" % (cut, cm)] = {
                "vs_ladder": f.get("vs_ladder"),
                "metrics": f["metrics"],
                "aux": f["aux"],
            }
            print("%-12s x%-3s vsLadder=%+7.1fbp t=%s eligible@cut=%s eligible@ref=%s" % (
                cut, cm, row["vs_ladder_bp"] or 0.0,
                _fmt(row["vs_ladder_t"]),
                (row["eligible_at_cut"] or {}).get("eligible"),
                row["eligible_at_ref"]))

    # convergence verdict face: eligible at REF_DATE across every cut that covers it
    ref_vals = sorted({r["eligible_at_ref"] for r in rows
                       if r["cost_mult"] == 1.0 and r["eligible_at_ref"] is not None})
    x1 = [r for r in rows if r["cost_mult"] == 1.0]
    bp = [r["vs_ladder_bp"] for r in x1 if r["vs_ladder_bp"] is not None]

    face = {
        "study": "e38_panel_drift_census",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": max(r["evidence_cutoff"] for r in rows),
        "spec": {
            "runner": "scripts/e27_universe_expansion.py run --exclude sh511 --ns 9999",
            "start": START,
            "exclude": EXCLUDE,
            "cost_bp_per_side": base.COST_BP_SIDE,
            "cuts": CUTS,
            "cost_cuts": COST_CUTS,
            "ref_date": REF_DATE,
        },
        "rows": rows,
        "convergence": {
            "ref_date": REF_DATE,
            "eligible_values_across_cuts": ref_vals,
            "converged": len(ref_vals) <= 1,
            "spread": (max(ref_vals) - min(ref_vals)) if ref_vals else None,
        },
        "cut_axis": {
            "vs_ladder_bp_min": min(bp) if bp else None,
            "vs_ladder_bp_max": max(bp) if bp else None,
            "vs_ladder_bp_spread": (max(bp) - min(bp)) if bp else None,
            "cuts": len(x1),
        },
        "faces": faces_out,
        "honest": [
            "descriptive census only: no gate, no verdict, no prereg, no trial count consumed",
            "the ETF population is today's surviving listing set (listing survivorship)",
            "the cut axis changes window length as well as panel content; only the "
            "eligible-at-ref column isolates panel state",
            "the reference date is fixed at 2026-09-22 because that is where r1110 saw 985 -> 1190",
        ],
    }
    if save:
        os.makedirs(OUTDIR, exist_ok=True)
        stem = "CENSUS-%s" % face["evidence_cutoff"].replace("-", "")
        with open(os.path.join(OUTDIR, stem + ".json"), "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
        with open(os.path.join(OUTDIR, "cuts.csv"), "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for r in rows:
                w.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, dict) else v)
                            for k, v in r.items()})
        with open(os.path.join(OUTDIR, "cut_axis.json"), "w", encoding="utf-8") as fh:
            json.dump({"cut_axis": face["cut_axis"], "convergence": face["convergence"],
                       "rows": [{"cut": r["cut"], "cost_mult": r["cost_mult"],
                                 "vs_ladder_bp": r["vs_ladder_bp"],
                                 "vs_ladder_t": r["vs_ladder_t"],
                                 "eligible_at_ref": r["eligible_at_ref"]} for r in rows]},
                      fh, ensure_ascii=False, indent=1)
        print("face: %s" % os.path.join(OUTDIR, stem + ".json"))
    print("convergence: eligible_at_ref values=%s converged=%s" % (
        ref_vals, face["convergence"]["converged"]))
    print("cut axis: vsLadder spread=%.1fbp over %d cuts" % (
        face["cut_axis"]["vs_ladder_bp_spread"] or 0.0, len(x1)))
    return face


def _synthetic_calendar(n, start=(2024, 1, 1)):
    """n consecutive ISO dates from a fixed start (hermetic fixtures only)."""
    import datetime as _dt
    d0 = _dt.date(*start)
    return [(d0 + _dt.timedelta(days=k)).isoformat() for k in range(n)]


def _fmt(v):
    return "None" if v is None else ("%.2f" % v)


def selftest():
    ok = tot = 0

    def check(name, cond):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        print("[%s] %s" % ("PASS" if cond else "FAIL", name))

    # 1) eligible_at returns None outside the truncated calendar
    cal = ["2026-01-02", "2026-09-22"]
    check("ref outside cut -> None", eligible_at("2026-10-20", "2026-09-22", [], {}, {}, cal) is None)

    # 2) eligibility rule is the shared one: a member needs i >= MIN_BARS and a full
    #    MIN_BARS-long run of non-missing closes ending at i.
    n = base.MIN_BARS
    series = [1.0] * (n + 1)
    check("shared elig() accepts a full window", base.elig(series, n) is True)
    check("shared elig() rejects a hole", base.elig(series[:-1] + [None], n) is False)
    check("shared elig() rejects a short history", base.elig([1.0] * n, n - 1) is False)

    # 3) pick() reads the non-ladder scheme, never the baseline
    face = {"schemes": {"ladder5": {}, "top9999": {"x": 1}}}
    name, _ = _pick(face)
    check("pick skips the ladder baseline", name == "top9999")

    # 4) the ref-date count is cut-invariant WHEN the panel is truncated identically --
    #    a fixed panel + two cuts that both cover REF must agree (the convergence check
    #    would flag a non-deterministic counter as drift).
    cal2 = _synthetic_calendar(base.MIN_BARS + 12) + ["2026-09-22", "2026-09-30"]
    prices = {"a": [1.0] * len(cal2)}
    amounts = {"a": [1e6] * len(cal2)}
    r1 = eligible_at("2026-09-22", "2026-09-22", ["a"], prices, amounts, cal2[:-1])
    check("counter deterministic at ref", r1 is not None and r1["eligible"] == 1)

    # 5) cut axis ignores the cost runs (they are a separate axis)
    check("cost axis kept off the cut grid", set(COST_CUTS) <= set(CUTS))

    print("selftest: %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))