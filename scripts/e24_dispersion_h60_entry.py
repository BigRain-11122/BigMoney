"""E24 dispersion-h60 monthly entry test (descriptive, cost-aware; NO gate, NO trial count).

Question left open by r1095 (the h=60 census burn closing the E24 mode x horizon
grid): at h=60 the signal ordering INVERTS for dispersion -- lowest quintile
+355.9bp per 60-bar stride (t 3.44), highest quintile +136.4bp (t 1.55).  Every
earlier E24 read (breadth, ladder momentum) was a top-tail, short-horizon story;
this is the only long-horizon cell whose best bucket sits at the BOTTOM of the
signal.  Overlapping 60-day windows read every day inflate t, so this face asks
the economic question on a NON-OVERLAPPING grid:

  at each month's decision day, read dispersion (cross-sectional stdev of the
  panel's 5-day trailing returns, causal); if it sits in the BOTTOM tail
  (<= expanding q cutoff with a 250-day burn-in), hold the equal-weight ladder
  for the next H bars and pay two sides of the frozen 13.041bp cost; otherwise
  stay in cash (0%, no cash yield credited).

H = 60 bars (the horizon whose census cell raised the question).  Windows never
overlap -- with a 60-bar hold only about every third month can fire, so the
monthly t is a legitimate independent read.

Pre-declared decision rule (frozen BEFORE the numbers were seen; re-emitted in
the face as `decision_rule`; identical constants to the r1094 breadth face):

    DRAFT a prereg candidate  iff ALL of
      (a) net edge vs always-on ladder >= +200 bp/yr   (EDGE_MIN_BP_YR)
      (b) paired t of (gated net - always-on gross) >= 2.0  (T_MIN)
      (c) edge sign positive in >= 2 of 3 era buckets  (ERA_MIN)
      (d) same sign at >= 2 of 3 cutoff levels {0.20, 0.33, 0.50}  (CUT_MIN)
    otherwise                        HONEST_CLOSE_NEGATIVE (binding failure named)

Honest labels baked in:
  * cell picked post hoc out of a 15-cell grid -> multiplicity real, uncorrected.
  * expanding cutoffs are causal; signal at day i uses closes <= i only.
  * T+1 entry: decision at close i, exposure accrues i+1..i+H.
  * cost = 2 * 13.041bp per active window (entry + exit), the frozen engine
    constant; cash windows pay nothing and earn nothing.
  * 60-bar holds overlap heavily in calendar time; non-overlap is enforced.
  * DESCRIPTIVE ONLY: no gate, no prereg, no admission verdict, no trial count.

Modes
  run       : write results/e24_dispersion_h60_entry/ENTRY-<date>.json + latest.json
  selftest  : hermetic checks (exit 0/1)
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from e24_breadth_h20_entry import (  # noqa: E402
    CUT_LEVELS as _BREADTH_CUTS,
    decide,
    monthly_indices,
    non_overlapping,
    summarize,
)
from e24_overlay_feasibility import COST_BP, ladder_returns  # noqa: E402
from e24_regime_census import BURN, load_panel, trailing  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "e24_dispersion_h60_entry")
H = 60
PRIMARY_Q = 0.20
CUT_LEVELS = (0.20, 0.33, 0.50)
GRID_OFFSET = 10
# the bottom-tail read is the cell under test; keep decide()'s cutoff scan honest
assert len(CUT_LEVELS) == len(_BREADTH_CUTS)


def dispersion_at(closes, i, n=5, min_names=20):
    """Cross-sectional stdev of n-day trailing returns at i (causal, None if thin)."""
    t = trailing(closes, i, n)
    if len(t) < min_names:
        return None
    return statistics.pstdev(t)


def window_return(rets, i, h):
    acc = 1.0
    for k in range(i + 1, i + h + 1):
        if k >= len(rets) or rets[k] is None:
            return None
        acc *= 1.0 + rets[k]
    return acc - 1.0


def expanding_cut(hist, q):
    srt = sorted(hist)
    return srt[min(len(srt) - 1, int(len(srt) * q))]


def run_grid(cal, rets, sig, h=H, q=PRIMARY_Q, offset=0, burn=BURN,
             cost_bp=COST_BP):
    """Bottom-tail gate: long the ladder when the signal is at/below the q cutoff."""
    picks = non_overlapping([i for i in monthly_indices(cal, offset) if i >= burn], h)
    hist, ptr, windows = [], 0, []
    for i in picks:
        while ptr < i:
            v = sig[ptr]
            if v is not None:
                hist.append(v)
            ptr += 1
        v = sig[i]
        on, cut = False, None
        if v is not None and len(hist) >= burn:
            cut = expanding_cut(hist, q)
            on = v <= cut
        wr = window_return(rets, i, h)
        if wr is None:
            continue
        cost = 2.0 * cost_bp / 1e4 if on else 0.0
        windows.append({
            "decision_date": cal[i],
            "exit_date": cal[min(i + h, len(cal) - 1)],
            "signal": None if v is None else round(v, 6),
            "cutoff": None if cut is None else round(cut, 6),
            "on": on,
            "gross": wr,
            "cost": cost,
            "net": (wr if on else 0.0) - cost,
        })
    return windows


def diagnostics(windows):
    """Why the exposure share is what it is (structural read, not a threshold knob)."""
    fires = [w for w in windows if w["on"]]
    by_year = {}
    for w in fires:
        y = w["decision_date"][:4]
        by_year[y] = by_year.get(y, 0) + 1
    sig = [w["signal"] for w in windows if w["signal"] is not None]
    cuts = [w["cutoff"] for w in windows if w["cutoff"] is not None]
    return {
        "fires": len(fires),
        "fire_years": dict(sorted(by_year.items())),
        "signal_on_decision_days": {
            "n": len(sig),
            "min": round(min(sig), 6) if sig else None,
            "median": round(statistics.median(sig), 6) if sig else None,
            "max": round(max(sig), 6) if sig else None,
        },
        "expanding_cut_range": {
            "min": round(min(cuts), 6) if cuts else None,
            "max": round(max(cuts), 6) if cuts else None,
        },
        "reading": ("an expanding bottom-tail cutoff on a trending signal can only fire in "
                    "the era where the signal was still low; a small exposure share is "
                    "structural, not a threshold choice"),
    }


def build_face(cal, rets, sig):
    primary = summarize(run_grid(cal, rets, sig))
    sens = {}
    for q in CUT_LEVELS:
        if q == PRIMARY_Q:
            continue
        sens["q%02d" % round(q * 100)] = summarize(run_grid(cal, rets, sig, q=q))
    sens["offset%d" % GRID_OFFSET] = summarize(
        run_grid(cal, rets, sig, offset=GRID_OFFSET))
    sens["q%02d" % round(PRIMARY_Q * 100)] = primary
    return {
        "face": "dispersion60-bottom-tail monthly entry on the five-member ladder",
        "evidence_cutoff": cal[-1] if cal else None,
        "window_start": cal[0] if cal else None,
        "horizon_bars": H,
        "primary": primary,
        "sensitivity": {k: {kk: v.get(kk) for kk in
                            ("windows", "active_windows", "exposure_share",
                             "edge_vs_always_on_bp_per_year", "paired_t")}
                        for k, v in sens.items()},
        "decision": decide(primary, sens),
        "diagnostics": diagnostics(run_grid(cal, rets, sig)),
        "decision_rule": {
            "edge_min_bp_per_year": 200.0,
            "paired_t_min": 2.0,
            "era_min": 2,
            "cut_levels": list(CUT_LEVELS),
            "side": "low (signal <= expanding q cutoff)",
        },
        "labels": {
            "descriptive": True,
            "prereg": None,
            "trial_count": 0,
            "verdict": "none (feasibility face; admission needs a frozen prereg)",
            "multiplicity": "cell chosen post hoc from the 15-cell E24 grid; no correction applied",
            "execution": "T+1 (decision at close i, exposure i+1..i+%d, non-overlapping windows)" % H,
            "cost": "2 * 13.041bp per active window; cash windows earn 0%",
        },
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def selftest():
    fails = []
    count = {"n": 0}

    def chk(name, cond):
        count["n"] += 1
        print(("  PASS " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    # fixture: 200 trading days, 3 calendar slices
    cal = ["2026-%02d-%02d" % (1 + i // 28, 1 + i % 28) for i in range(200)]
    rets = [None] + [0.0005] * 199
    sig = [i * 0.001 for i in range(200)]      # strictly rising dispersion

    chk("dispersion_at needs enough names",
         dispersion_at([[1.0], [1.1]], 1, 5, min_names=20) is None)
    chk("dispersion_at returns a stdev",
         dispersion_at([[1.0, 2.0] * 10 for _ in range(10)],
                       9, 5, min_names=20) is not None)

    # a collapsing signal must eventually fall under its own expanding cut
    sig_drop = [1.0 + 0.001 * i for i in range(100)] + [0.0] * 100
    w = run_grid(cal, rets, sig_drop, h=30, burn=30)
    chk("grid produces windows", len(w) > 0)
    chk("bottom-tail gate stays off while the signal is high, fires after it drops",
         w[0]["on"] is False and any(x["on"] for x in w))
    chk("cash windows net exactly zero",
         all(x["net"] == 0.0 for x in w if not x["on"]))
    chk("active windows net == gross - 2 sides",
         all(abs(x["net"] - (x["gross"] - 2 * COST_BP / 1e4)) < 1e-12
             for x in w if x["on"]))

    picks = non_overlapping(monthly_indices(cal), 60)
    chk("60-bar windows never overlap",
         all(b - a >= 60 for a, b in zip(picks, picks[1:])))
    chk("window_return compounds h bars",
         abs(window_return(rets, 0, 60) - (1.0005 ** 60 - 1)) < 1e-12)
    chk("expanding_cut is the q quantile", expanding_cut(list(range(100)), 0.20) == 20)

    # causality: shock after a decision day cannot move that decision
    sig2 = list(sig)
    sig2[60] = 99.0
    a = [x["on"] for x in run_grid(cal, rets, sig, h=60, burn=30)]
    b = [x["on"] for x in run_grid(cal, rets, sig2, h=60, burn=30)]
    chk("decision invariant to a later shock", a[0] == b[0])

    diag = diagnostics(run_grid(cal, rets, sig_drop, h=30, burn=30))
    chk("diagnostics fire count matches active windows",
         diag["fires"] == sum(diag["fire_years"].values()))

    # summarize/decide wiring on a synthetic winning gate
    def mk(gross, on):
        return {"decision_date": "2026-01-02", "exit_date": "2026-03-31",
                "signal": 0.001, "cutoff": 0.01, "on": on, "gross": gross,
                "cost": 2 * COST_BP / 1e4 if on else 0.0,
                "net": (gross if on else 0.0) - (2 * COST_BP / 1e4 if on else 0.0)}

    good = [mk(0.04 if x % 2 == 0 else -0.005, x % 2 == 0) for x in range(36)]
    s_good = summarize(good)
    chk("summarize counts windows", s_good["windows"] == 36)
    chk("winning gate shows positive edge",
         s_good["edge_vs_always_on_bp_per_year"] > 0)

    sens = {"q20": {"edge_vs_always_on_bp_per_year": 500.0},
            "q33": {"edge_vs_always_on_bp_per_year": 300.0},
            "q50": {"edge_vs_always_on_bp_per_year": -10.0}}
    primary = {"edge_vs_always_on_bp_per_year": 400.0, "paired_t": 2.5,
               "era": {e: {"active_windows": 3, "edge_vs_always_bp_per_yr": v}
                       for e, v in {"a": 100.0, "b": 200.0, "c": -30.0}.items()}}
    chk("rule drafts when criteria clear",
         decide(primary, sens)["verdict"] == "DRAFT_PREREG_CANDIDATE")
    weak = dict(primary, edge_vs_always_on_bp_per_year=50.0, paired_t=0.4)
    chk("rule closes negative when criteria fail",
         decide(weak, sens)["verdict"] == "HONEST_CLOSE_NEGATIVE")

    print("selftest: %d/%d PASS" % (count["n"] - len(fails), count["n"]))
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("run", help="compute the dispersion-h60 entry face")
    sub.add_parser("selftest", help="hermetic self checks")
    args = ap.parse_args(argv)
    cmd = args.cmd or "run"
    if cmd == "selftest":
        return selftest()

    cal, symbols, rows = load_panel()
    rets = ladder_returns(cal, symbols, rows)
    sig = [dispersion_at(rows, i, 5) for i in range(len(rows))]
    face = build_face(cal, rets, sig)
    os.makedirs(OUTDIR, exist_ok=True)
    stamp = (face["evidence_cutoff"] or "").replace("-", "")
    path = os.path.join(OUTDIR, "ENTRY-%s.json" % stamp)
    for p in (path, os.path.join(OUTDIR, "latest.json")):
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({"primary": {k: face["primary"].get(k) for k in
                                  ("windows", "active_windows", "exposure_share",
                                   "gated", "always_on_ladder",
                                   "edge_vs_always_on_bp_per_year", "paired_t", "era")},
                      "sensitivity": face["sensitivity"],
                      "decision": face["decision"]},
                     ensure_ascii=False, indent=1))
    print("face: %s" % os.path.relpath(path, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())