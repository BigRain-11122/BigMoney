"""E24 breadth-h20 monthly entry test (descriptive, cost-aware; NO gate, NO trial count).

Question left open by r1093: the breadth census at h=20 showed the top quintile
of "share of ETFs above their 20d MA" carrying +245.2bp per 20-day stride
(t 4.90) on the five-member traded ladder, the strongest cell of the 15-cell
E24 grid.  That t is inflated by overlapping 20-day windows read every day.
This face asks the economic question on a NON-OVERLAPPING monthly grid:

  at each month's decision day, read breadth-h20 (causal, expanding 0.80
  cutoff with a 250-day burn-in); if the read is in the top tail, hold the
  equal-weight ladder for the next 20 trading days and pay two sides of the
  frozen 13.041bp cost; otherwise stay in cash (0%, no cash yield credited).

Windows never overlap: the next decision day must fall after the previous
exit.  Monthly returns are therefore independent reads, so a plain t is
legitimate (this is the point of the face).

Pre-declared decision rule (frozen here BEFORE the numbers were seen; the
same constants are re-emitted in the face as `decision_rule`):

    DRAFT a prereg candidate  iff ALL of
      (a) net edge vs always-on ladder >= +200 bp/yr   (EDGE_MIN_BP_YR)
      (b) paired t of (gated net - always-on gross) >= 2.0  (T_MIN)
      (c) edge sign positive in >= 2 of 3 era buckets  (ERA_MIN)
      (d) same sign at >= 2 of 3 cutoff levels {0.67,0.80,0.90}  (CUT_MIN)
    otherwise                        HONEST_CLOSE_NEGATIVE (binding failure named)

Honest labels baked in:
  * the cell was picked post hoc out of a 15-cell grid -> multiplicity is real
    and is NOT corrected here; the decision rule is deliberately demanding.
  * expansion cutoffs are causal; signal at day i is computed from closes <= i.
  * T+1 entry: decision at close of day i, exposure returns accrue i+1..i+20.
  * cost = 2 * 13.041bp per active window (entry + exit), the frozen engine
    constant; cash windows pay nothing and earn nothing.
  * sensitivity legs (cutoff 0.67/0.90, mid-month grid offset 10) exist to
    catch grid luck, not to rescue the primary cell.
  * DESCRIPTIVE ONLY: no gate, no prereg, no verdict on admission, no
    trial-count consumption.

Modes
  run       : write results/e24_breadth_h20_entry/ENTRY-<cutoff>.json + latest.json
  selftest  : hermetic checks (exit 0/1)
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from bisect import insort
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from e24_regime_census import BURN, breadth_at, load_panel, tstat  # noqa: E402
from e24_overlay_feasibility import COST_BP, ladder_returns  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "e24_breadth_h20_entry")
H = 20
PRIMARY_Q = 0.80
CUT_LEVELS = (0.67, 0.80, 0.90)
GRID_OFFSET = 10

# --- frozen decision rule (declared before the numbers, do not tune) --------
EDGE_MIN_BP_YR = 200.0
T_MIN = 2.0
ERA_MIN = 2


# ---------------------------------------------------------------- grid pieces
def monthly_indices(cal, offset=0):
    """Indices of the (offset+1)-th trading day of every calendar month."""
    buckets = {}
    for i, d in enumerate(cal):
        buckets.setdefault(d[:7], []).append(i)
    out = []
    for ym in sorted(buckets):
        idxs = buckets[ym]
        if offset < len(idxs):
            out.append(idxs[offset])
    return out


def non_overlapping(cands, h):
    """Keep decision days whose holding window does not overlap the previous one."""
    kept, last_exit = [], -1
    for i in cands:
        # exposure of the previous window is i_prev+1 .. i_prev+h, so a decision
        # ON the exit close (i == i_prev+h) still opens a fresh, disjoint window
        if i < last_exit:
            continue
        kept.append(i)
        last_exit = i + h
    return kept


def window_return(rets, i, h):
    """Compounded ladder return over bars i+1..i+h (None if any bar missing)."""
    acc = 1.0
    for k in range(i + 1, i + h + 1):
        if k >= len(rets) or rets[k] is None:
            return None
        acc *= 1.0 + rets[k]
    return acc - 1.0


def era_of(d):
    y = int(d[:4])
    if y < 2017:
        return "pre2017"
    if y <= 2020:
        return "2017-2020"
    if y <= 2023:
        return "2021-2023"
    return "2024-now"


def expanding_cut(hist, q):
    """Quantile of the signal history seen strictly before the decision day."""
    srt = sorted(hist)
    return srt[min(len(srt) - 1, int(len(srt) * q))]


# ------------------------------------------------------------------ strategy
def run_grid(cal, rets, sig, h=H, q=PRIMARY_Q, offset=0, burn=BURN,
             cost_bp=COST_BP):
    picks = non_overlapping([i for i in monthly_indices(cal, offset) if i >= burn], h)
    hist, ptr, windows = [], 0, []
    for i in picks:
        while ptr < i:
            v = sig[ptr]
            if v is not None:
                insort(hist, v)
            ptr += 1
        v = sig[i]
        on, cut = False, None
        if v is not None and len(hist) >= burn:
            cut = expanding_cut(hist, q)
            on = v > cut
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


def summarize(windows):
    if not windows:
        return {"status": "empty", "reason": "no usable monthly windows"}
    gross_all = [w["gross"] for w in windows]
    net_all = [w["net"] for w in windows]
    active = [w for w in windows if w["on"]]
    n = len(windows)
    n_years = n / 12.0

    mean_net = statistics.fmean(net_all)
    t_net = tstat(net_all)
    # always-on comparison: same windows, ladder held throughout, one entry+exit
    always_gross = statistics.fmean(gross_all)
    always_net = always_gross - 2.0 * COST_BP / 1e4 / n
    diffs = [w["net"] - w["gross"] for w in windows]
    t_paired = tstat(diffs)

    era_net, era_n = {}, {}
    for w in windows:
        e = era_of(w["decision_date"])
        era_net.setdefault(e, []).append(w["net"])
        era_n[e] = era_n.get(e, 0) + (1 if w["on"] else 0)
    era = {}
    for e, vals in sorted(era_net.items()):
        era[e] = {
            "windows": len(vals),
            "active_windows": era_n.get(e, 0),
            "net_bp_per_window": round(statistics.fmean(vals) * 1e4, 1),
            "edge_vs_always_bp_per_yr": round(
                (statistics.fmean(vals) - always_net) * 12 * 1e4, 1),
        }
    return {
        "windows": n,
        "years": round(n_years, 2),
        "active_windows": len(active),
        "exposure_share": round(len(active) / n, 4),
        "gated": {
            "mean_gross_bp_active": round(statistics.fmean([w["gross"] for w in active]) * 1e4, 1) if active else None,
            "mean_net_bp_per_window": round(mean_net * 1e4, 2),
            "net_bp_per_year": round(mean_net * 12 * 1e4, 1),
            "t_net": round(t_net, 2) if t_net is not None else None,
            "cost_bp_total": round(sum(w["cost"] for w in windows) * 1e4, 1),
            "cost_bp_per_year": round(sum(w["cost"] for w in windows) / n_years * 1e4, 1),
        },
        "always_on_ladder": {
            "mean_gross_bp_per_window": round(always_gross * 1e4, 2),
            "mean_net_bp_per_window": round(always_net * 1e4, 2),
            "net_bp_per_year": round(always_net * 12 * 1e4, 1),
            "t_gross": round(tstat(gross_all), 2) if tstat(gross_all) is not None else None,
        },
        "edge_vs_always_on_bp_per_year": round((mean_net - always_net) * 12 * 1e4, 1),
        "paired_t": round(t_paired, 2) if t_paired is not None else None,
        "era": era,
    }


def decide(primary, sens):
    """Apply the frozen rule; return verdict + named binding failures."""
    fails = []
    edge = primary["edge_vs_always_on_bp_per_year"]
    if edge < EDGE_MIN_BP_YR:
        fails.append("edge %.1f < %.1f bp/yr" % (edge, EDGE_MIN_BP_YR))
    pt = primary["paired_t"]
    if pt is None or pt < T_MIN:
        fails.append("paired_t %s < %.1f" % (pt, T_MIN))
    pos_eras = sum(1 for v in primary["era"].values()
                   if v["active_windows"] > 0
                   and v["edge_vs_always_bp_per_yr"] > 0)
    if pos_eras < ERA_MIN:
        fails.append("positive eras %d < %d" % (pos_eras, ERA_MIN))
    pos_cuts = sum(1 for k, v in sens.items()
                   if k.startswith("q") and v.get("edge_vs_always_on_bp_per_year", 0) > 0)
    if pos_cuts < ERA_MIN:
        fails.append("positive cutoffs %d < %d" % (pos_cuts, ERA_MIN))
    return {
        "verdict": "HONEST_CLOSE_NEGATIVE" if fails else "DRAFT_PREREG_CANDIDATE",
        "binding_failures": fails,
        "positive_eras": pos_eras,
        "positive_cutoffs": pos_cuts,
    }


def build_face(cal, rets, sig):
    primary = summarize(run_grid(cal, rets, sig))
    sens = {}
    for q in CUT_LEVELS:
        if q == PRIMARY_Q:
            continue
        s = summarize(run_grid(cal, rets, sig, q=q))
        sens["q%02d" % round(q * 100)] = s
    s = summarize(run_grid(cal, rets, sig, offset=GRID_OFFSET))
    sens["offset%d" % GRID_OFFSET] = s
    sens["q%02d" % round(PRIMARY_Q * 100)] = primary
    return {
        "face": "breadth20-top-quintile monthly entry on the five-member ladder",
        "evidence_cutoff": cal[-1] if cal else None,
        "window_start": cal[0] if cal else None,
        "horizon_bars": H,
        "primary": primary,
        "sensitivity": {k: {kk: v.get(kk) for kk in
                            ("windows", "active_windows", "exposure_share",
                             "edge_vs_always_on_bp_per_year", "paired_t")}
                        for k, v in sens.items()},
        "decision": decide(primary, sens),
        "decision_rule": {
            "edge_min_bp_per_year": EDGE_MIN_BP_YR,
            "paired_t_min": T_MIN,
            "era_min": ERA_MIN,
            "cut_levels": list(CUT_LEVELS),
        },
        "labels": {
            "descriptive": True,
            "prereg": None,
            "trial_count": 0,
            "verdict": "none (feasibility face; admission needs a frozen prereg)",
            "multiplicity": "cell chosen post hoc from the 15-cell E24 grid; no correction applied",
            "execution": "T+1 (decision at close i, exposure i+1..i+20, non-overlapping windows)",
            "cost": "2 * 13.041bp per active window; cash windows earn 0%",
        },
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


# -------------------------------------------------------------------- selftest
def selftest():
    fails = []
    count = {"n": 0}

    def chk(name, cond):
        count["n"] += 1
        print(("  PASS " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    # calendar: 60 trading days spanning 3 months
    cal = ["2026-%02d-%02d" % (1 + i // 20, 1 + i % 20) for i in range(60)]
    rets = [None] + [0.001] * 59          # flat +10bp/day ladder
    sig = [0.5] * 60

    chk("monthly grid picks one day per month", len(monthly_indices(cal)) == 3)
    chk("offset grid picks a later day in each month",
         monthly_indices(cal, 5)[0] == 5)

    picks = non_overlapping(monthly_indices(cal), 20)
    chk("non-overlap keeps decision days >= previous exit", len(picks) == 3)
    picks2 = non_overlapping([0, 1, 2, 21, 22], 20)
    chk("overlapping candidates are dropped", picks2 == [0, 21])

    wr = window_return(rets, 0, 20)
    chk("window return compounds h bars", abs(wr - (1.001 ** 20 - 1)) < 1e-12)
    chk("window return None when a bar is missing",
         window_return([None] + [None] * 5, 0, 2) is None)

    chk("expanding cut is the q quantile of history",
         expanding_cut(list(range(100)), 0.80) == 80)

    # gated windows: sig above cut -> on; below -> cash (h=10 for the fixture)
    sig_on = [0.1] * 20 + [0.9] * 40
    w_on = run_grid(cal, rets, sig_on, h=10, burn=10)
    chk("windows after burn-in exist", len(w_on) == 2)
    chk("both gate states exercised in the fixture",
         sorted(w["on"] for w in w_on) == [False, True])
    chk("cost charged only on active windows",
         all(abs(w["cost"] - (2 * COST_BP / 1e4 if w["on"] else 0.0)) < 1e-15 for w in w_on))
    chk("cash windows return exactly zero",
         all(w["net"] == 0.0 for w in w_on if not w["on"]))
    chk("active windows net == gross - cost",
         all(abs(w["net"] - (w["gross"] - w["cost"])) < 1e-12
             for w in w_on if w["on"]))

    # causality: a shock on day 30 cannot change the decision taken on day 20
    sig2 = list(sig_on)
    sig2[30] = 0.999
    a = [w["on"] for w in run_grid(cal, rets, sig_on, h=10, burn=10)]
    b = [w["on"] for w in run_grid(cal, rets, sig2, h=10, burn=10)]
    chk("decision is invariant to a shock after its own day", a[0] == b[0])

    # summarize + decide: construct a clear positive and a clear negative case
    def mk(gross, on):
        return {"decision_date": "2026-01-02", "exit_date": "2026-01-30",
                "signal": 0.9, "cutoff": 0.5, "on": on, "gross": gross,
                "cost": 2 * COST_BP / 1e4 if on else 0.0,
                "net": (gross if on else 0.0) - (2 * COST_BP / 1e4 if on else 0.0)}

    good = [mk(0.03 if i % 2 == 0 else -0.01, i % 2 == 0) for i in range(36)]
    s_good = summarize(good)
    chk("summarize counts windows", s_good["windows"] == 36)
    chk("summarize edge is positive for a winning gate",
         s_good["edge_vs_always_on_bp_per_year"] > 0)

    bad = [mk(0.01, False) for _ in range(36)]
    s_bad = summarize(bad)
    chk("cash-only gate has zero net and negative edge",
         s_bad["gated"]["net_bp_per_year"] == 0.0
         and s_bad["edge_vs_always_on_bp_per_year"] < 0)

    sens = {"q67": {"edge_vs_always_on_bp_per_year": -10.0},
            "q80": {"edge_vs_always_on_bp_per_year": 500.0},
            "q90": {"edge_vs_always_on_bp_per_year": 50.0}}

    def fake_primary(edge, t, era_edges):
        return {"edge_vs_always_on_bp_per_year": edge, "paired_t": t,
                "era": {e: {"active_windows": 4, "edge_vs_always_bp_per_yr": v}
                        for e, v in era_edges.items()}}

    pos = fake_primary(500.0, 3.0, {"a": 100.0, "b": 200.0, "c": -50.0})
    chk("rule drafts when every criterion clears",
         decide(pos, sens)["verdict"] == "DRAFT_PREREG_CANDIDATE")
    neg = fake_primary(50.0, 0.5, {"a": 10.0, "b": -20.0, "c": -5.0})
    d_neg = decide(neg, sens)
    chk("rule closes negative when criteria fail",
         d_neg["verdict"] == "HONEST_CLOSE_NEGATIVE" and len(d_neg["binding_failures"]) >= 2)

    print("selftest: %d/%d PASS" % (count["n"] - len(fails), count["n"]))
    return 0 if not fails else 1


# ------------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("run", help="compute the monthly entry face")
    sub.add_parser("selftest", help="hermetic self checks")
    args = ap.parse_args(argv)
    cmd = args.cmd or "run"
    if cmd == "selftest":
        return selftest()

    cal, symbols, rows = load_panel()
    rets = ladder_returns(cal, symbols, rows)
    sig = [breadth_at(rows, i, 20) for i in range(len(rows))]
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
                                   "edge_vs_always_on_bp_per_year", "paired_t")},
                      "sensitivity": face["sensitivity"],
                      "decision": face["decision"]},
                     ensure_ascii=False, indent=1))
    print("face: %s" % os.path.relpath(path, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())