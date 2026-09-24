# -*- coding: utf-8 -*-
"""T33_ROUTER_VALIDATION (T-2026-09-24-33 deliverable-4) -- corps router d4.

Consumes the FROZEN spec research/T33_ROUTER_SPEC.md (d3, sha da78f746 in
ticket note) and derives, deterministically, with ZERO new signal families:
  state source  : REGIME_GUARD v3 import-replay (T-21 same primitives,
                   no cache, per-run recompute) -> 4-state daily series
  member source : scripts/ew6_portfolio.member_run (anchor pipeline reused
                   verbatim; cost faces via CostPatch)
  passive       : EW-48 daily-rebalanced (o1600 caliber: close pct_change
                   mean axis=1)
Judgments (frozen s4, J18 -- implementation may fix itself, criteria never):
  V-R1 per-corps segment survival vs passive EW-48 (x2 face):
      target-segment mean daily excess > 0 AND corps segment maxDD not
      worse than passive segment maxDD by more than 5pp. defense corps
      empty => honest zero-accept row (RED covered by cash floor in V-R2).
  V-R2 routed vs constant-chop vs passive, three cost faces
      (x1/x2/x3), descriptive: ann/sharpe/maxDD; HARD claim = RED-segment
      routed maxDD must beat constant-chop RED-segment maxDD.
  V-R3 x3-face annualized switching-cost drag <= 1.5%.
Tenure grid {5,10,20} frozen; selection = smallest grid with annualized
switch count <= 12 (ties -> more conservative larger grid); none satisfy ->
grid 20 + review flag.
Causality: state at T close -> position effective T+1 (shift-by-one).
Analysis window = v3 win dates trimmed to the member-run common coverage
(full-window v3 counts gate stays on the UNTRIMMED series, bit-match).
Zero registration / zero wiring / zero ledger N increment (aggregation
precedent r68/r69). Audit section mandatory (s0).
"""
import argparse
import datetime as dt
import hashlib
import io
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pandas as pd

from engine.metrics import annual_return, max_drawdown, sharpe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_DOC = os.path.join(ROOT, "research", "T33_ROUTER_SPEC.md")
ROSTER = os.path.join(ROOT, "results", "corps_roster.json")
OUT_JSON = os.path.join(ROOT, "results", "t33_router_validation.json")
OUT_CSV = os.path.join(ROOT, "research", "t33_router_validation_results.csv")

# frozen data gate: v3 calibration batch recorded counts (bm-b r98-99 canon)
V3_STATE_COUNTS = {"GREEN": 664, "YELLOW": 772, "ORANGE": 35, "RED": 161}
GRIDS = (5, 10, 20)
MAX_SWITCHES_PER_YR = 12
VR1_DD_TOL = 0.05          # 5pp segment maxDD deterioration line (frozen)
VR3_DRAG_MAX = 0.015       # x3-face annualized switching drag <= 1.5% (frozen)
COVERAGE_MIN = 0.98        # analysis-window calendar coverage gate
COST_X1_RATE = 0.0013041    # G2-recorded baseline single-side cost (live.paper)
STATE_CORPS = {"GREEN": "attack", "YELLOW": "chop", "ORANGE": "chop",
               "RED": "defense"}
CORPS_FALLBACK = {"attack": ["chop", "defense", "cash"],
                  "chop": ["defense", "cash"],
                  "defense": ["cash"], "cash": []}


# ------------------------------------------------------------- pure logic
def map_corps(state: str, roster_corps: dict) -> str:
    """s3.1 mapping + s3.2 empty-corps fallback (finite order, no recursion)."""
    want = STATE_CORPS[state]
    if roster_corps.get(want):
        return want
    for nxt in CORPS_FALLBACK[want]:
        if nxt == "cash" or roster_corps.get(nxt):
            return nxt
    return "cash"


def simulate_tenure(corps_seq, tenure: int):
    """Hysteresis: pending corps must persist >= tenure consecutive days.

    Applied on the MAPPED-corps sequence (the frozen object is corps
    switching -- s3.3 'simulate corps switch counts'; state micro-churn
    inside one corps, e.g. YELLOW<->ORANGE, has zero portfolio effect and
    is not a switch; interpretation disclosed in s7 backfill).
    Returns (effective_seq, n_switches).
    """
    if not corps_seq:
        return [], 0
    held = corps_seq[0]
    eff = [held]
    pending, cnt = None, 0
    n_sw = 0
    for c in corps_seq[1:]:
        if c == held:
            pending, cnt = None, 0
        else:
            if c == pending:
                cnt += 1
            else:
                pending, cnt = c, 1
            if cnt >= tenure:
                held = c
                pending, cnt = None, 0
                n_sw += 1
        eff.append(held)
    return eff, n_sw


def select_tenure(ann_switches: dict):
    """Smallest satisfying grid (<=12/yr); among grids TIED on that same ann
    switch count -> more conservative larger grid; none -> 20 + review flag."""
    ok = [g for g in GRIDS if ann_switches.get(g, 1e9) <= MAX_SWITCHES_PER_YR]
    if not ok:
        return 20, True
    g_min = min(ok)
    tied = [g for g in ok if ann_switches[g] == ann_switches[g_min]]
    return max(tied), False


def routed_daily(corps_rets: dict, eff_prev, side_rate: float):
    """Routed portfolio daily returns with causality (position = eff[t-1])
    and two-side full-turnover switching cost on position-change days."""
    out = []
    prev_pos = eff_prev[0]
    cost_total = 0.0
    for i in range(len(eff_prev)):
        pos = eff_prev[i]          # position effective on day i (t-1 close)
        r = 0.0 if pos == "cash" else corps_rets[pos][i]
        if i > 0 and pos != prev_pos:
            cost = 2.0 * side_rate   # sell leg + buy leg, full turnover
            r -= cost
            cost_total += cost
        out.append(r)
        prev_pos = pos
    return out, cost_total


def seg_metrics(rets):
    """ann / sharpe / maxDD over a daily-return list (engine.metrics caliber
    on the rebuilt equity curve)."""
    if len(rets) < 2:
        return {"ann": 0.0, "sharpe": 0.0, "maxdd": 0.0, "n": len(rets)}
    eq = (1.0 + pd.Series(rets)).cumprod()
    return {"ann": round(float(annual_return(eq)), 6),
            "sharpe": round(float(sharpe(eq)), 4),
            "maxdd": round(float(max_drawdown(eq)), 6),
            "n": len(rets)}


def vr1_face(corps_ret: list, passive_ret: list):
    """V-R1 per-corps: mean daily excess > 0 and segment maxDD not worse
    than passive by more than 5pp (frozen s4)."""
    n = min(len(corps_ret), len(passive_ret))
    if n == 0:
        return {"n_days": 0, "mean_excess": None, "pass": None}
    excess = [corps_ret[i] - passive_ret[i] for i in range(n)]
    mean_ex = sum(excess) / n
    dd_c = seg_metrics(corps_ret[:n])["maxdd"]
    dd_p = seg_metrics(passive_ret[:n])["maxdd"]
    ok_ex = mean_ex > 0
    ok_dd = dd_c >= dd_p - VR1_DD_TOL
    return {"n_days": n, "mean_excess": round(mean_ex, 8),
            "corps_seg_maxdd": dd_c, "passive_seg_maxdd": dd_p,
            "pass": bool(ok_ex and ok_dd),
            "pass_mean_excess": bool(ok_ex), "pass_dd": bool(ok_dd)}


# ------------------------------------------------------------- data layer
def load_state_series():
    """v3 import-replay (no cache, per-run recompute -- T-21 same primitives)."""
    from scripts.regime_calibration import (WINDOW_END_CAP, WINDOW_START,
                                            bench_dim_series, breadth_series,
                                            build_bench, raw_series,
                                            state_replay)
    from scripts.market_regime import raw_level_v3, resolve_state_v3
    bench = build_bench()
    bench = bench[bench.index <= pd.Timestamp(WINDOW_END_CAP)]
    ds = bench_dim_series(bench)
    br = breadth_series(bench)
    raw = raw_series(bench, ds, br, level_fn=raw_level_v3)
    states, streaks, init_day = state_replay(bench, raw,
                                             resolver=resolve_state_v3)
    win = [d for d in bench.index if str(d.date()) >= WINDOW_START]
    return pd.Series({d: states[d] for d in win})


def load_roster_corps():
    d = json.load(io.open(ROSTER, encoding="utf-8"))
    corps = {"attack": [], "chop": [], "defense": []}
    for r in d.get("registered", []):
        c = r.get("corps") or r.get("assigned_corps")
        if c in corps and r.get("member"):
            corps[c].append(r["member"])
    return corps, d.get("summary", {})


def member_equity(tid: str, cost_mult):
    """member_run reuse (anchor pipeline). cost_mult None -> x1 base face."""
    import scripts.ew6_portfolio as ew6
    if ew6.PRICES_FULL is None:
        ew6.PRICES_FULL = ew6.load_core()
    r = ew6.member_run(tid, cost_mult=cost_mult)
    eq = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
    return eq, r.get("cutoff")


def build() -> int:
    t0 = time.time()
    spec_sha = hashlib.sha256(io.open(SPEC_DOC, "rb").read()).hexdigest()
    state_full = load_state_series()
    counts = {k: int((state_full == k).sum()) for k in V3_STATE_COUNTS}
    gate_counts = counts == V3_STATE_COUNTS
    corps, roster_summary = load_roster_corps()
    gate_roster = (len(corps["attack"]) >= 1 and len(corps["chop"]) >= 1
                   and os.path.exists(ROSTER))

    import live.paper as LP
    prices_full = LP.load_core()
    P = LP.build_panels(prices_full)
    close = P["close"]
    panel_cutoff = str(close.index[-1].date())
    gate_panel = panel_cutoff >= "2026-09-23"
    passive_all = close.pct_change(fill_method=None).mean(axis=1)

    faces = {"x1": None, "x2": 2.0, "x3": 3.0}
    corps_rets = {f: {} for f in faces}
    member_runs = 0
    member_cutoffs = {}
    member_last = None
    for cname, members in corps.items():
        if not members:
            continue
        for fname, mult in faces.items():
            rets = {}
            for m in members:
                eq, mcut = member_equity(m, mult)
                member_runs += 1
                member_cutoffs[m] = mcut
                member_last = (eq.index[-1] if member_last is None
                               else min(member_last, eq.index[-1]))
                rets[m] = eq.pct_change().fillna(0.0)
            corps_rets[fname][cname] = pd.DataFrame(rets).mean(axis=1)

    dates = state_full.index.intersection(passive_all.index)
    if member_last is not None:
        dates = dates[dates <= member_last]
    coverage = round(len(dates) / max(len(state_full), 1), 4)
    gate_calendar = coverage >= COVERAGE_MIN
    state = state_full.reindex(dates)
    passive = passive_all.reindex(dates).fillna(0.0)
    years = len(dates) / 252.0

    out = {
        "batch": "T33_ROUTER_VALIDATION",
        "ticket": "T-2026-09-24-33 deliverable-4",
        "spec_doc": "research/T33_ROUTER_SPEC.md",
        "prereg_sha256_at_run": spec_sha,
        "spec_sha_frozen_ref": "da78f746 (d3 freeze, ticket note)",
        "evidence_cutoff": panel_cutoff,
        "science_gates": {"cutoff_meta": {"evidence_cutoff": panel_cutoff}},
        "data_gates": {
            "g1_v3_counts_bit_match": gate_counts,
            "v3_state_counts": counts,
            "g2_roster": gate_roster,
            "roster_counts": {k: len(v) for k, v in corps.items()},
            "g3_panel_cutoff": gate_panel,
            "g4_calendar_coverage": gate_calendar,
            "calendar_coverage": coverage,
            "analysis_window": {"start": str(dates[0].date()),
                                "end": str(dates[-1].date()),
                                "n_days": len(dates),
                                "trim_note": "trimmed to member-run common "
                                             "coverage (evidence_cutoff side)"},
            "member_cutoffs": member_cutoffs,
        },
        "defense_empty_disclosure": len(corps["defense"]) == 0,
        "years": round(years, 4),
    }
    if not (gate_counts and gate_roster and gate_panel and gate_calendar):
        out["verdict"] = "GATES_FAILED"
        out["audit"] = {"elapsed_sec": round(time.time() - t0, 1),
                        "n_member_runs": member_runs}
        io.open(OUT_JSON, "w", encoding="utf-8", newline="\n").write(
            json.dumps(out, ensure_ascii=False, indent=1))
        print("GATES_FAILED:", {k: v for k, v in out["data_gates"].items()
                                if k.startswith("g")})
        return 2

    corps_seq = [map_corps(s, corps) for s in state.values]
    ann_sw, eff_by_grid = {}, {}
    for g in GRIDS:
        eff, n_sw = simulate_tenure(corps_seq, g)
        eff_by_grid[g] = eff
        ann_sw[g] = round(n_sw / years, 4)
    tenure, review_flag = select_tenure(ann_sw)
    eff = eff_by_grid[tenure]
    eff_prev = [eff[0]] + eff[:-1]        # causality: T close -> T+1 effective
    n_switches = sum(1 for i in range(1, len(eff)) if eff[i] != eff[i - 1])
    out["tenure_grid_ann_switches"] = ann_sw
    out["tenure_selected"] = tenure
    out["tenure_review_flag"] = review_flag
    out["n_switches_selected"] = n_switches

    # ---------------- V-R1 (x2 face, frozen judgment) ----------------
    vr1 = {}
    seg_map = {"attack": state.isin(["GREEN"]).values,
               "chop": state.isin(["YELLOW", "ORANGE"]).values,
               "defense": state.isin(["RED"]).values}
    for cname, mask in seg_map.items():
        if not corps.get(cname):
            vr1[cname] = {"n_members": 0, "pass": None,
                          "note": "corps empty -- honest zero-accept "
                                  "(RED cash floor covers in V-R2)"}
            continue
        c_ret = corps_rets["x2"][cname].reindex(dates).fillna(0.0)
        vr1[cname] = {"n_members": len(corps[cname]),
                     "n_days": int(mask.sum())}
        vr1[cname].update(vr1_face(list(c_ret.values[mask]),
                                   list(passive.values[mask])))
    out["vr1"] = vr1
    out["vr1_verdict"] = all((v.get("pass") is not False) for v in vr1.values())

    # ---------------- V-R2 (3 faces x routed/chop/passive) -------------
    vr2 = {}
    for fname in faces:
        mult = {"x1": 1, "x2": 2, "x3": 3}[fname]
        side = COST_X1_RATE * mult
        cr = {c: list(s.reindex(dates).fillna(0.0).values)
              for c, s in corps_rets[fname].items()}
        cr["cash"] = [0.0] * len(dates)
        rr, cost_total = routed_daily(cr, eff_prev, side)
        chop_ret = list(corps_rets[fname]["chop"].reindex(dates)
                        .fillna(0.0).values)
        red_mask = (state == "RED").values
        red_routed = [rr[i] for i in range(len(rr)) if red_mask[i]]
        red_chop = [chop_ret[i] for i in range(len(chop_ret)) if red_mask[i]]
        vr2[fname] = {
            "routed": seg_metrics(rr),
            "constant_chop": seg_metrics(chop_ret),
            "passive": seg_metrics(list(passive.values)),
            "red_seg_routed_maxdd": seg_metrics(red_routed)["maxdd"],
            "red_seg_chop_maxdd": seg_metrics(red_chop)["maxdd"],
            "switch_cost_total": round(cost_total, 6),
            "switch_cost_drag_ann": round(cost_total / years, 6),
        }
        vr2[fname]["red_dd_claim_pass"] = bool(
            vr2[fname]["red_seg_routed_maxdd"] > vr2[fname]["red_seg_chop_maxdd"])
    out["vr2"] = vr2
    out["vr2_red_claim_pass"] = all(v["red_dd_claim_pass"] for v in vr2.values())

    # ---------------- V-R3 (x3 switching drag, frozen line) ------------
    drag = vr2["x3"]["switch_cost_drag_ann"]
    out["vr3"] = {"x3_drag_ann": drag, "pass": bool(drag <= VR3_DRAG_MAX),
                 "line": VR3_DRAG_MAX, "n_switches": n_switches}
    out["audit"] = {"elapsed_sec": round(time.time() - t0, 1),
                    "n_member_runs": member_runs,
                    "core_workers": os.cpu_count(),
                    "deterministic": "no RNG, pure replay"}
    out["verdict"] = "GATES_OK"

    io.open(OUT_JSON, "w", encoding="utf-8", newline="\n").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    rows = []
    for cname, v in vr1.items():
        rows.append({"section": "V-R1", "key": cname,
                     "pass": v.get("pass"), "n_days": v.get("n_days"),
                     "mean_excess": v.get("mean_excess"),
                     "corps_seg_maxdd": v.get("corps_seg_maxdd"),
                     "passive_seg_maxdd": v.get("passive_seg_maxdd")})
    for fname, v in vr2.items():
        rows.append({"section": "V-R2", "key": f"routed/{fname}",
                     "pass": v["red_dd_claim_pass"], "n_days": v["routed"]["n"],
                     "ann": v["routed"]["ann"], "sharpe": v["routed"]["sharpe"],
                     "maxdd": v["routed"]["maxdd"]})
        rows.append({"section": "V-R2", "key": f"constant_chop/{fname}",
                     "pass": "", "n_days": v["constant_chop"]["n"],
                     "ann": v["constant_chop"]["ann"],
                     "sharpe": v["constant_chop"]["sharpe"],
                     "maxdd": v["constant_chop"]["maxdd"]})
        rows.append({"section": "V-R2", "key": f"passive/{fname}",
                     "pass": "", "n_days": v["passive"]["n"],
                     "ann": v["passive"]["ann"], "sharpe": v["passive"]["sharpe"],
                     "maxdd": v["passive"]["maxdd"]})
    rows.append({"section": "V-R3", "key": "x3_drag_ann",
                 "pass": out["vr3"]["pass"], "n_days": n_switches,
                 "ann": "", "sharpe": "", "maxdd": drag})
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding="utf-8")
    print("verdict:", out["verdict"], "| tenure:", tenure,
          "| ann_sw:", ann_sw, "| vr1:", out["vr1_verdict"],
          "| vr2_red:", out["vr2_red_claim_pass"],
          "| vr3:", out["vr3"]["pass"], "| member_runs:", member_runs)
    print("out ->", OUT_JSON)
    return 0


# ------------------------------------------------------------- selftest
def selftest() -> int:
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print("t33_router_validation selftest:")
    seq = ["A", "A", "B", "B", "A", "B", "B", "B", "B", "A", "A", "A"]
    eff, n_sw = simulate_tenure(seq, 3)
    ok("S1 short B burst suppressed (no flip)",
       eff[0:5] == ["A"] * 5 and eff[6] == "A")
    ok("S2 persistent B flips on 3rd consecutive day",
       eff[7] == "B" and n_sw >= 1)
    ok("S3 flip-back to A only after 3-day persistence",
       eff[-1] == "A" and n_sw == 2)
    sel, flag = select_tenure({5: 14.0, 10: 9.0, 20: 9.0})
    ok("S4 tie -> larger (more conservative) grid", sel == 20 and not flag)
    sel2, flag2 = select_tenure({5: 8.0, 10: 4.0, 20: 3.0})
    ok("S5 smallest satisfying grid wins", sel2 == 5 and not flag2)
    sel3, flag3 = select_tenure({5: 20.0, 10: 15.0, 20: 13.0})
    ok("S6 none satisfy -> grid 20 + review flag", sel3 == 20 and flag3)
    cr = {"attack": [0.01, 0.01, 0.01, 0.01], "cash": [0.0] * 4}
    eff_prev = ["attack", "attack", "cash", "cash"]
    rr, cost = routed_daily(cr, eff_prev, 0.0013041)
    ok("S7 switch cost exact (two-side, charged on effective day)",
       abs(cost - 2 * 0.0013041) < 1e-12 and abs(rr[2] + 2 * 0.0013041) < 1e-12)
    ok("S8 cash floor zero return, no double charge",
       rr[3] == 0.0 and cost == 2 * 0.0013041)
    f = vr1_face([0.010, 0.012], [0.004, 0.010])
    ok("S9 V-R1 mean excess arithmetic",
       abs(f["mean_excess"] - 0.004) < 1e-9 and f["pass"] is True)
    f2 = vr1_face([0.004, 0.004], [0.010, 0.012])
    ok("S10 V-R1 negative excess fails honestly",
       f2["pass_mean_excess"] is False and f2["pass"] is False)
    ok("S11 fallback order (empty attack->chop, empty defense->cash)",
       map_corps("GREEN", {"chop": ["x"]}) == "chop"
       and map_corps("RED", {}) == "cash"
       and map_corps("RED", {"defense": ["y"]}) == "defense")
    print("SELFTEST", "ALL PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    return build()


if __name__ == "__main__":
    sys.exit(main())
