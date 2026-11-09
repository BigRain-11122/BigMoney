"""The rung is not the problem; the RULE is.

r1486 swept the vol target (none, 8, 10, 12, 15, 20, 25%) and found the two things the
desk wants are mutually exclusive ON THAT PATH: every rung that clears Y4 (top-2 year
share <= 70%) sizes down by nothing (maxdd identical to "none" at -16.04%), and the only
rung that really buys drawdown (vt08, -10.56%) is the one the gate refuses (70.67%).

The mechanism is visible in the per-year scale: a vol target trims in LOW-VOL years,
and low-vol years are also the low-return years, so the denominator shrinks faster than
the numerator (29.23pp vs 18.31pp -- r1486's own readings). Trimming the small years is
exactly what concentrates the book into its top two.

So this face changes the RULE instead of the rung. Three de-risking rules that all use
only information available at the decision bar, each frozen BEFORE the run (no knob was
searched -- if the family fails, the answer is the family, not a missing rung):

  dd_brake       de-lever in proportion to the book's OWN drawdown from its own peak
                 (>=8% -> 0.50, >=15% -> 0.25). De-risks only after money is lost.
  loss_cond_vt   the r1486 vol target, applied ONLY while the book's own trailing 60-bar
                 return is negative (full size in calm up-markets, which is where the
                 good years come from).
  trend_brake    half size while the book's own equity sits below its own 200-bar mean.

Each one is benchmarked against the same two published rungs on the same panel, the same
score, the same 20-bar rebalance, the same 10bp/edge: `none` (ADMIT, top2 68.55%) and
`vt08` (CONDITIONAL, top2 70.67%, mdd -10.56%). The CONTROL GATE is hard: `none` and
`vt08` must reproduce the published VT-LADDER.json to 1e-6 on CAGR and top-2 share, or
this script refuses to write a face at all -- a rule receipt that cannot re-derive the
ladder it is compared against is not a comparison.

A rule that passes the gate is then path-tested (E188): five decision phases (start
offset 0/5/10/15/20 days), and it must pass on 5/5 phases against each phase's OWN
control, because a single-phase win may be one decision sequence.

Usage:
    python scripts/etf_book_derisk_rule.py run
    python scripts/etf_book_derisk_rule.py check
    python scripts/etf_book_derisk_rule.py selftest
"""
import argparse
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402
import etf_book_vt_ladder as L  # noqa: E402

OUT_DIR = os.path.join(ROOT, "results", "etf_book_derisk_rule")
OUT = os.path.join(OUT_DIR, "DERISK-RULE.json")
LADDER = os.path.join(ROOT, "results", "etf_book_vt_ladder", "VT-LADDER.json")
CELL = {"rebalance_days": 20, "top_n": 5, "cost": 0.0010}
VOL_TARGET = 0.08          # the r1486 rung this face is compared against
DD_SOFT, DD_HARD = 0.08, 0.15
DD_SOFT_SCALE, DD_HARD_SCALE = 0.50, 0.25
TREND_WINDOW = 200
TREND_SCALE = 0.50
LOSS_WINDOW = 60
PHASE_OFFSETS_DAYS = [0, 5, 10, 15, 20]


# ---------------------------------------------------------------- the rules
def _dd(path: pd.Series) -> float:
    """Drawdown of the book's own realised equity path (causal: path ends at this bar)."""
    p = path.dropna().astype(float)
    if len(p) < 2:
        return 0.0
    peak = float(p.cummax().iloc[-1])
    last = float(p.iloc[-1])
    if peak <= 0:
        return 0.0
    return last / peak - 1.0


def rule_dd_brake(book, date, path, est_vol):
    d = _dd(path)
    if d <= -DD_HARD:
        return DD_HARD_SCALE
    if d <= -DD_SOFT:
        return DD_SOFT_SCALE
    return 1.0


def rule_loss_cond_vt(book, date, path, est_vol):
    p = path.dropna().astype(float)
    if len(p) < LOSS_WINDOW + 1:
        return 1.0                      # not enough history: take no de-risk claim
    trailing = float(p.iloc[-1]) / float(p.iloc[-1 - LOSS_WINDOW]) - 1.0
    if trailing >= 0.0:
        return 1.0
    if est_vol is None or not np.isfinite(est_vol) or est_vol <= 0:
        return 1.0
    return float(min(1.0, VOL_TARGET / est_vol))


def rule_trend_brake(book, date, path, est_vol):
    p = path.dropna().astype(float)
    if len(p) < TREND_WINDOW:
        return 1.0                      # censored window: no claim, never a fabricated 0
    ma = float(p.tail(TREND_WINDOW).mean())
    return TREND_SCALE if float(p.iloc[-1]) < ma else 1.0


RULES = [
    ("none", None, "control: the bond-free book, no de-risking"),
    ("vt08", VOL_TARGET, "control: the r1486 8% vol target (the rung the gate refuses)"),
    ("dd_brake", rule_dd_brake,
     "de-lever with the book's own drawdown (>=8% -> 0.50, >=15% -> 0.25)"),
    ("loss_cond_vt", rule_loss_cond_vt,
     "8% vol target only while the book's own 60-bar return is negative"),
    ("trend_brake", rule_trend_brake,
     "half size while the book's own equity is below its own 200-bar mean"),
]


# ---------------------------------------------------------------- measurement
def rule_row(label: str, rule, ser: pd.Series, turn: float, diag: list) -> dict:
    years = L.yearly_returns(ser)
    st = A.stats2(ser, label)
    cagr = st.get("cagr")
    blk = G.admission_block(years, None, None, cagr)
    return {
        "rule": label,
        "verdict": blk["verdict"],
        "checks": blk["checks"],
        "year_metrics": blk["year_metrics"],
        "years": blk["years"],
        "partial_years": blk["partial_years"],
        "cagr_pct": cagr,
        "sharpe": st.get("sharpe"),
        "maxdd_pct": st.get("maxdd"),
        "vol_realised_pct": (None if L.realised_vol(ser) is None
                             else round(L.realised_vol(ser) * 100.0, 3)),
        "turnover_per_side": round(float(turn), 3),
        "annual_sum_pp": blk["year_metrics"].get("annual_sum"),
        "top2_sum_pp": (None if blk["year_metrics"].get("annual_sum") is None
                        else round(blk["year_metrics"]["annual_sum"]
                                   * (blk["year_metrics"]["top2_share"] or 0.0), 4)),
        "scale_by_year": L.sizing_by_year(diag, ser),
        "de_risk_share": (None if not diag else
                          round(float(np.mean([r["scale"] < 1.0 for r in diag])), 4)),
        "mean_scale": (None if not diag else round(float(np.mean([r["scale"] for r in diag])), 4)),
    }


def prepare() -> dict:
    """Load the panel ONCE (61s of the round's budget) and hand it to every run."""
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    sc = E.build_score(close[cols], amt[cols], feats)
    return {"close": close[cols], "openp": openp[cols], "amt": amt[cols], "score": sc,
            "n_flip": int(n_flip), "cols": cols, "bars": int(len(close)),
            "first": str(close.index[0].date()), "last": str(close.index[-1].date())}


def _phase_start(phase_days: int) -> str:
    if not phase_days:
        return R.START
    return str((pd.Timestamp(R.START) + pd.Timedelta(days=phase_days)).date())


def build_runs(bundle: dict, phase_days: int = 0, only=None) -> tuple[list, dict]:
    start = _phase_start(phase_days)
    rows = []
    for label, knob, _desc in RULES:
        if only is not None and label not in only:
            continue
        diag: list = []
        kw = {}
        if label == "vt08":
            kw["vol_target"] = VOL_TARGET
        elif knob is not None:
            kw["scale_hook"] = knob
        ser, turn = R.open_to_open_equity(
            bundle["close"], bundle["openp"], bundle["amt"], bundle["score"],
            CELL["rebalance_days"], CELL["top_n"], CELL["cost"],
            start=start, diag=diag, **kw)
        rows.append(rule_row(label, knob, ser, turn, diag))
        print("%-13s top2=%s cagr=%s mdd=%s de_risk=%.2f verdict=%s"
              % (label, rows[-1]["year_metrics"]["top2_share"], rows[-1]["cagr_pct"],
                 rows[-1]["maxdd_pct"], rows[-1]["de_risk_share"] or 0.0,
                 rows[-1]["verdict"]), flush=True)
    meta = {"bars": bundle["bars"], "first": bundle["first"], "last": bundle["last"],
            "flips_repaired": bundle["n_flip"], "bond_free_universe": len(bundle["cols"]),
            "cell": dict(CELL), "start": start, "phase_offset_days": int(phase_days)}
    return rows, meta


def control_gate(rows: list) -> dict:
    """`none` and `vt08` must reproduce the published ladder, or nothing is published."""
    if not os.path.exists(LADDER):
        return {"ok": False, "detail": "published VT-LADDER.json missing -- nothing to "
                                       "reproduce, so no comparison is possible"}
    with io.open(LADDER, encoding="utf-8") as f:
        pub = {r["rung"]: r for r in json.load(f)["rungs"]}
    out, ok = {}, True
    for label in ("none", "vt08"):
        mine = next((r for r in rows if r["rule"] == label), None)
        their = pub.get(label)
        if mine is None or their is None:
            out[label] = {"note": "not priced on both sides"}
            ok = False
            continue
        gaps = {
            "cagr_pp": round(abs((mine["cagr_pct"] or 0.0) - (their["cagr_pct"] or 0.0)) * 100, 9),
            "top2": round(abs((mine["year_metrics"]["top2_share"] or 0.0)
                              - (their["year_metrics"]["top2_share"] or 0.0)), 12),
            "mdd_pp": round(abs((mine["maxdd_pct"] or 0.0) - (their["maxdd_pct"] or 0.0)) * 100, 9),
        }
        good = gaps["cagr_pp"] <= 1e-6 and gaps["top2"] <= 1e-9 and gaps["mdd_pp"] <= 1e-6
        ok = ok and good
        out[label] = {"published": {"cagr_pct": their["cagr_pct"],
                                    "top2_share": their["year_metrics"]["top2_share"],
                                    "maxdd_pct": their["maxdd_pct"]},
                      "measured": {"cagr_pct": mine["cagr_pct"],
                                   "top2_share": mine["year_metrics"]["top2_share"],
                                   "maxdd_pct": mine["maxdd_pct"]},
                      "gaps": gaps, "reproduces": good}
    out["ok"] = ok
    out["detail"] = ("both published rungs reproduce to 1e-6 on CAGR/drawdown and 1e-9 on "
                     "top-2 share" if ok else
                     "CONTROL GATE FAILED -- the comparison base does not re-derive")
    return out


def reads(rows: list, control_row: dict, phases: dict | None = None) -> dict:
    """Read the family's answer off its own rows: which rules clear the gate, and of
    those which also buy drawdown against the same control. When the phase table is
    present, a rule that passes in some phases but not all is named as phase-dependent
    -- that is a decision sequence, not a rule, and it must not be read as an ADMIT."""
    if not rows or control_row is None:
        return {"answer": "UNKNOWN", "detail": "nothing was priced"}
    base = control_row
    passing = [r for r in rows if r["verdict"] == "ADMIT"]
    buys = [r for r in rows
            if r["rule"] not in ("none",)
            and (r["maxdd_pct"] or 0.0) > (base["maxdd_pct"] or 0.0) + 0.005]
    both = [r for r in passing if r in buys and r["rule"] != "none"]
    mechanism = []
    for r in rows:
        if r["rule"] == "none":
            continue
        mechanism.append({
            "rule": r["rule"],
            "de_risk_share": r.get("de_risk_share"),
            "annual_sum_pp": r.get("annual_sum_pp"),
            "delta_annual_sum_pp": (None if r.get("annual_sum_pp") is None
                                    or base.get("annual_sum_pp") is None
                                    else round(r["annual_sum_pp"] - base["annual_sum_pp"], 4)),
            "top2_share": r["year_metrics"]["top2_share"],
            "delta_top2": round((r["year_metrics"]["top2_share"] or 0.0)
                                - (base["year_metrics"]["top2_share"] or 0.0), 4),
            "delta_maxdd_pp": round(((r["maxdd_pct"] or 0.0) - (base["maxdd_pct"] or 0.0)) * 100, 4),
        })
    detail = ("rules passing the gate: %s | of those buying >=0.5pp drawdown vs control "
              "(%s): %s"
              % (",".join(r["rule"] for r in passing) or "none",
                 "%.4f" % (base["maxdd_pct"] or 0.0),
                 ",".join(r["rule"] for r in both) or "none"))
    out = {"mechanism": mechanism}
    if phases:
        dep = [lab for lab, ph in phases.items()
               if isinstance(ph, dict) and "phases" in ph
               and 0 < sum(1 for c in ph["phases"] if c["passes"]) < len(ph["phases"])]
        stable = [lab for lab, ph in phases.items()
                  if isinstance(ph, dict) and "phases" in ph and ph.get("passes_all_phases")]
        out["phase_dependent_rules"] = dep
        out["phase_stable_pass_rules"] = stable
        if dep:
            detail += (" | PHASE-DEPENDENT (passes in some phases only, not a rule): %s"
                       % ",".join(dep))
        if stable:
            detail += " | passes in every phase: %s" % ",".join(stable)
        # a rule that only wins in some phases is a decision sequence, not a member
        keep = []
        for r in both:
            ph = phases.get(r["rule"])
            if isinstance(ph, dict) and "phases" in ph and not ph.get("passes_all_phases"):
                continue
            keep.append(r)
        both = keep
    if both:
        pick = max(both, key=lambda r: r["sharpe"] or -9)
        out.update({"answer": "RULE_FAMILY_HAS_MEMBER", "rule": pick["rule"], "detail": detail})
        return out
    cand = [r for r in rows if r["rule"] not in ("none",)]
    if not cand:
        out.update({"answer": "UNKNOWN", "detail": "no candidate rule was priced"})
        return out
    best = min(cand, key=lambda r: (abs((r["year_metrics"]["top2_share"] or 9.9)
                                       - G.TOP2_SHARE_MAX),
                                   -(r["maxdd_pct"] or -9)))
    fails = [k for k, v in best["checks"].items() if v is False]
    out.update({"answer": "NO_RULE_CLEARS_BOTH",
                "closest_rule": best["rule"],
                "closest_fails": fails,
                "detail": (detail + " | closest %s: top2 %.4f vs %.2f, mdd %.4f vs control "
                           "%.4f, fails %s"
                           % (best["rule"], best["year_metrics"]["top2_share"] or float("nan"),
                              G.TOP2_SHARE_MAX, best["maxdd_pct"] or float("nan"),
                              base["maxdd_pct"] or float("nan"),
                              ",".join(fails) or "none"))})
    return out


def phase_test(bundle: dict, labels: list, base_rows: list) -> dict:
    """E188: a verdict is only a rule if it survives every decision phase, measured
    against that phase's OWN control. A single-phase win may be one decision sequence.

    Every candidate is path-tested, not only the ones that passed at phase 0: a rule
    that misses by a hair in one phase can clear the line in another, and that
    "some phases pass" reading is exactly what a single-phase receipt would hide."""
    out = {}
    if not labels:
        return {"skipped": "no candidate rule was priced -- nothing to path-test"}
    base0 = next(r for r in base_rows if r["rule"] == "none")
    for label in labels:
        cells = []
        for off in PHASE_OFFSETS_DAYS:
            if off == 0:
                base, mine = base0, next(r for r in base_rows if r["rule"] == label)
            else:
                rows, _ = build_runs(bundle, phase_days=off, only=["none", label])
                base = next(r for r in rows if r["rule"] == "none")
                mine = next(r for r in rows if r["rule"] == label)
            cells.append({
                "phase_offset_days": off,
                "verdict": mine["verdict"],
                "passes": mine["verdict"] == "ADMIT",
                "top2_share": mine["year_metrics"]["top2_share"],
                "control_top2_share": base["year_metrics"]["top2_share"],
                "maxdd_pct": mine["maxdd_pct"],
                "control_maxdd_pct": base["maxdd_pct"],
                "drawdown_gain_pp": round(((mine["maxdd_pct"] or 0.0)
                                           - (base["maxdd_pct"] or 0.0)) * 100, 4),
                "cagr_gain_pp": round(((mine["cagr_pct"] or 0.0)
                                       - (base["cagr_pct"] or 0.0)) * 100, 4),
            })
            print("phase %-13s +%02dd verdict=%s top2=%s gain_dd=%+.4fpp"
                  % (label, off, cells[-1]["verdict"], cells[-1]["top2_share"],
                     cells[-1]["drawdown_gain_pp"]), flush=True)
        n_pass = sum(1 for c in cells if c["passes"])
        gains = [c["drawdown_gain_pp"] for c in cells]
        out[label] = {
            "phases": cells,
            "passes_all_phases": n_pass == len(cells),
            "passes_n_of": "%d/%d" % (n_pass, len(cells)),
            "drawdown_gain_pp_min": min(gains),
            "drawdown_gain_pp_median": round(float(np.median(gains)), 4),
            "verdict_stable": all(c["passes"] == cells[0]["passes"] for c in cells),
        }
    return out


def instrument_read(phases: dict, ctrl: dict, rows: list) -> dict:
    """Can THIS gate judge THIS book at all? (E433 lineage: a ruler that cannot judge
    itself reads the decision phase, not the book.)

    Each rule\'s top-2 share is measured on five decision phases. If a configuration\'s
    own spread across phases straddles the 70% line, then "passes Y4" / "fails Y4" is a
    statement about the phase, not about the book, and the verdict cannot be read as a
    property of the strategy."""
    line = G.TOP2_SHARE_MAX
    per = {}
    if not phases:
        return {"available": False, "detail": "no phase table -- resolvability unknown"}
    for lab, ph in phases.items():
        if not isinstance(ph, dict) or "phases" not in ph:
            continue
        vals = sorted({round(c["top2_share"], 12) for c in ph["phases"]
                       if c.get("top2_share") is not None})
        if not vals:
            continue
        per[lab] = {
            "top2_min": vals[0], "top2_max": vals[-1],
            "spread_pp": round((vals[-1] - vals[0]) * 100, 4),
            "straddles_line": vals[0] <= line <= vals[-1],
            "distance_to_line_pp": round(abs((vals[0] if abs(vals[0] - line) < abs(vals[-1] - line)
                                              else vals[-1]) - line) * 100, 4),
        }
    ctrl_vals = sorted({round(c["control_top2_share"], 12)
                        for ph in phases.values()
                        if isinstance(ph, dict) and "phases" in ph
                        for c in ph["phases"] if c.get("control_top2_share") is not None}
                       | {round(ctrl["year_metrics"]["top2_share"], 12)})
    ctrl_block = {
        "top2_min": ctrl_vals[0], "top2_max": ctrl_vals[-1],
        "spread_pp": round((ctrl_vals[-1] - ctrl_vals[0]) * 100, 4),
        "straddles_line": ctrl_vals[0] <= line <= ctrl_vals[-1],
    }
    unresolvable = [lab for lab, b in per.items() if b["straddles_line"]]
    resolvable_fail = [lab for lab, b in per.items()
                       if not b["straddles_line"] and b["top2_min"] > line]
    return {
        "available": True,
        "control": ctrl_block,
        "rules": per,
        "unresolvable": sorted(unresolvable),
        "resolvably_above_line": sorted(resolvable_fail),
        "detail": ("the unde-risked control itself reads %.4f..%.4f across five decision "
                   "phases (spread %.2fpp, line %.2f) -- %s"
                   % (ctrl_vals[0], ctrl_vals[-1], (ctrl_vals[-1] - ctrl_vals[0]) * 100,
                      line,
                      "so the gate's reading moves across its own line for the SAME book"
                      if ctrl_block["straddles_line"] else
                      "the control stays on one side of the line")),
    }


def run(quick: bool = False) -> dict:
    t0 = time.time()
    bundle = prepare()
    rows, meta = build_runs(bundle)
    ctrl = next(r for r in rows if r["rule"] == "none")
    gate = control_gate(rows)
    phases = {}
    if gate["ok"] and not quick:
        cands = [r["rule"] for r in rows if r["rule"] != "none"]
        phases = phase_test(bundle, cands, rows)
    readings = reads(rows, ctrl, phases)
    instrument = instrument_read(phases, ctrl, rows)
    out = {
        "face": "etf_book_derisk_rule",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": meta["last"],
        "cell": "N5_R20_10bp",
        "question": ("r1486 showed no vol-target rung both clears Y4 and buys drawdown; "
                     "does a de-risking RULE that only acts in bad states (own drawdown, "
                     "own trend, vol target conditioned on a loss regime) clear both"),
        "frozen_parameters": {
            "dd_soft_pct": DD_SOFT * 100, "dd_soft_scale": DD_SOFT_SCALE,
            "dd_hard_pct": DD_HARD * 100, "dd_hard_scale": DD_HARD_SCALE,
            "trend_window_bars": TREND_WINDOW, "trend_scale": TREND_SCALE,
            "loss_window_bars": LOSS_WINDOW, "loss_regime_vol_target": VOL_TARGET,
            "note": "chosen before the run; no threshold was searched. If the family "
                    "fails, the answer is the family, not a missing rung",
        },
        "gate_rules": {
            "source": "scripts/candidate_year_gate.py (imported, not copied)",
            "top2_share_max": G.TOP2_SHARE_MAX,
            "worst_year_floor_pp": G.WORST_YEAR_FLOOR_PP,
            "positive_years_share_min": G.POSITIVE_YEARS_SHARE,
        },
        "data": meta,
        "control_gate": gate,
        "rules": rows,
        "phase_test": phases,
        "instrument": instrument,
        "answer": readings,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    if not gate["ok"]:
        print("REFUSED: control gate failed -- face not written")
        return out
    os.makedirs(OUT_DIR, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return out


def load() -> dict | None:
    if not os.path.exists(OUT):
        return None
    with io.open(OUT, encoding="utf-8") as f:
        return json.load(f)


def check() -> int:
    """Re-derive every decision from the published face itself (no engine re-run)."""
    d = load()
    if d is None:
        print("MISSING %s -- nothing to re-derive" % OUT)
        return 1
    errs = []
    rows = d.get("rules") or []
    if not rows:
        errs.append("face publishes no rules")
    ctrl = next((r for r in rows if r["rule"] == "none"), None)
    if ctrl is None:
        errs.append("no control row -- comparisons cannot be read")
    for r in rows:
        yrs = {str(v["year"]): {"net_pct": v["net_pct"], "cohorts": v["cohorts"]}
               for v in (r.get("years") or [])}
        again = G.admission_block(yrs, None, None, r.get("cagr_pct"))
        if again["verdict"] != r["verdict"]:
            errs.append("%s verdict re-derives: %s != %s"
                        % (r["rule"], again["verdict"], r["verdict"]))
        m = again["year_metrics"]
        if (m["top2_share"] is not None and r["year_metrics"]["top2_share"] is not None
                and abs(m["top2_share"] - r["year_metrics"]["top2_share"]) > 1e-9):
            errs.append("%s top2_share re-derives" % r["rule"])
        if r["checks"].get("Y4_top2_share") != (m["top2_share"] <= G.TOP2_SHARE_MAX):
            errs.append("%s Y4 flag disagrees with its own top2_share" % r["rule"])
        for y, s in (r.get("scale_by_year") or {}).items():
            if not (0.0 <= s <= 1.0 + 1e-9):
                errs.append("%s scale %s=%s outside [0,1]" % (r["rule"], y, s))
        if r["de_risk_share"] is not None and not (0.0 <= r["de_risk_share"] <= 1.0):
            errs.append("%s de_risk_share outside [0,1]" % r["rule"])
        # the arithmetic the mechanism block quotes must re-derive from the row itself
        if r.get("annual_sum_pp") is not None and r.get("top2_sum_pp") is not None:
            if abs(r["top2_sum_pp"] - round(r["annual_sum_pp"]
                                            * (r["year_metrics"]["top2_share"] or 0.0), 4)) > 1e-9:
                errs.append("%s top2_sum_pp is not annual_sum x top2_share" % r["rule"])
    # a rule that never de-risks must be identical to the control (identity leg)
    if ctrl is not None:
        for r in rows:
            if r["rule"] == "none":
                continue
            if r["de_risk_share"] == 0.0:
                if abs((r["cagr_pct"] or 0.0) - (ctrl["cagr_pct"] or 0.0)) > 1e-9:
                    errs.append("%s never de-risked but its CAGR differs from the control"
                                % r["rule"])
    # the answer word must follow from the rows, and phase claims must follow from phases
    again = (reads(rows, ctrl, d.get("phase_test") or {}) if ctrl is not None
             else {"answer": "UNKNOWN"})
    if again["answer"] != (d.get("answer") or {}).get("answer"):
        errs.append("answer re-derives: %s != %s"
                    % (again["answer"], (d.get("answer") or {}).get("answer")))
    for label, ph in (d.get("phase_test") or {}).items():
        if not isinstance(ph, dict) or "phases" not in ph:
            continue
        n = sum(1 for c in ph["phases"] if c["passes"])
        if ph["passes_all_phases"] != (n == len(ph["phases"])):
            errs.append("%s passes_all_phases disagrees with its phases" % label)
        if ph["passes_n_of"] != "%d/%d" % (n, len(ph["phases"])):
            errs.append("%s passes_n_of disagrees with its phases" % label)
        if ph["verdict_stable"] != all(c["passes"] == ph["phases"][0]["passes"]
                                       for c in ph["phases"]):
            errs.append("%s verdict_stable disagrees with its phases" % label)
        for c in ph["phases"]:
            if abs(c["drawdown_gain_pp"]
                   - round(((c["maxdd_pct"] or 0.0) - (c["control_maxdd_pct"] or 0.0)) * 100, 4)) > 1e-9:
                errs.append("%s phase +%d drawdown gain does not re-derive"
                            % (label, c["phase_offset_days"]))
    # the mechanism block must quote its own rows, and the phase labels must follow
    for m in (d.get("answer") or {}).get("mechanism") or []:
        row = next((r for r in rows if r["rule"] == m["rule"]), None)
        if row is None:
            errs.append("mechanism names %s, which is not a priced rule" % m["rule"])
            continue
        if m.get("annual_sum_pp") != row.get("annual_sum_pp"):
            errs.append("%s mechanism annual sum differs from its row" % m["rule"])
        d_top2 = round((row["year_metrics"]["top2_share"] or 0.0)
                       - (ctrl["year_metrics"]["top2_share"] or 0.0), 4)
        if abs((m.get("delta_top2") or 0.0) - d_top2) > 1e-9:
            errs.append("%s mechanism top2 delta does not re-derive" % m["rule"])
    phs = d.get("phase_test") or {}
    dep_again = sorted(lab for lab, ph in phs.items()
                       if isinstance(ph, dict) and "phases" in ph
                       and 0 < sum(1 for c in ph["phases"] if c["passes"]) < len(ph["phases"]))
    if sorted((d.get("answer") or {}).get("phase_dependent_rules") or []) != dep_again:
        errs.append("phase_dependent_rules does not re-derive from the phase table")
    # the resolvability block must re-derive from the same phase cells (E433 lineage)
    inst = d.get("instrument") or {}
    if inst.get("available") and ctrl is not None:
        again_inst = instrument_read(phs, ctrl, rows)
        if sorted(inst.get("unresolvable") or []) != again_inst["unresolvable"]:
            errs.append("instrument unresolvable list does not re-derive")
        if abs((inst["control"]["spread_pp"]
                - again_inst["control"]["spread_pp"])) > 1e-9:
            errs.append("instrument control spread does not re-derive")
        if inst["control"]["straddles_line"] != again_inst["control"]["straddles_line"]:
            errs.append("instrument control straddle flag does not re-derive")
        for lab, b in (inst.get("rules") or {}).items():
            if lab not in again_inst["rules"]:
                errs.append("instrument names %s, which has no phase cells" % lab)
            elif abs(b["spread_pp"] - again_inst["rules"][lab]["spread_pp"]) > 1e-9:
                errs.append("instrument spread for %s does not re-derive" % lab)
    if errs:
        print("CHECK_FAIL")
        for e in errs:
            print("  -", e)
        return 1
    print("CHECK_OK rules=%d answer=%s" % (len(rows), (d.get("answer") or {}).get("answer")))
    return 0


# ---------------------------------------------------------------- offline legs
def selftest() -> int:
    ok = tot = 0
    errs = []

    def chk(cond, msg):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        else:
            errs.append(msg)

    idx = pd.bdate_range("2020-01-01", periods=400)
    flat = pd.Series(1.0, index=idx)
    dd8 = pd.Series([1.0] * 300 + list(np.linspace(1.0, 0.90, 20)) + [0.90] * 80, index=idx[:400])
    dd20 = pd.Series([1.0] * 300 + list(np.linspace(1.0, 0.78, 20)) + [0.78] * 80, index=idx[:400])

    # L1 dd_brake: no drawdown = full size, 10% = half, 22% = quarter
    chk(rule_dd_brake({}, idx[-1], flat, None) == 1.0, "dd_brake at no drawdown is 1.0")
    chk(rule_dd_brake({}, idx[-1], dd8, None) == DD_SOFT_SCALE, "dd_brake at -10% is 0.50")
    chk(rule_dd_brake({}, idx[-1], dd20, None) == DD_HARD_SCALE, "dd_brake at -22% is 0.25")

    # L2 loss_cond_vt: full size when the book is up, target-sized when it is down
    up = pd.Series(np.linspace(1.0, 1.5, 400), index=idx)
    down = pd.Series(np.linspace(1.5, 1.1, 400), index=idx)
    chk(rule_loss_cond_vt({}, idx[-1], up, 0.16) == 1.0,
        "loss-conditional target does not trim an up book")
    got = rule_loss_cond_vt({}, idx[-1], down, 0.16)
    chk(abs(got - VOL_TARGET / 0.16) < 1e-12,
        "loss-conditional target trims a down book to 8%/16%")

    # L3 trend_brake: below its own mean halves, above stays full
    chk(rule_trend_brake({}, idx[-1], dd20, None) == TREND_SCALE,
        "trend brake halves a book under its own mean")
    chk(rule_trend_brake({}, idx[-1], up, None) == 1.0,
        "trend brake keeps full size on a book above its own mean")

    # L4 censored history is no claim, not a fabricated de-risk (r1261 lineage)
    short = pd.Series(np.linspace(1.0, 0.8, 30), index=idx[:30])
    chk(rule_trend_brake({}, idx[29], short, 0.2) == 1.0,
        "a book shorter than the trend window is not de-risked on a guess")
    chk(rule_loss_cond_vt({}, idx[29], short, 0.2) == 1.0,
        "a book shorter than the loss window is not de-risked on a guess")
    chk(rule_dd_brake({}, idx[0], pd.Series([1.0], index=idx[:1]), None) == 1.0,
        "a one-bar path has no drawdown to read")

    # L5 every rule speaks one language: a scale strictly inside [0, 1]
    for nm, fn in (("dd_brake", rule_dd_brake), ("loss_cond_vt", rule_loss_cond_vt),
                   ("trend_brake", rule_trend_brake)):
        for path in (flat, up, down, dd8, dd20, short):
            s = fn({}, path.index[-1], path, 0.11)
            chk(np.isfinite(s) and 0.0 <= s <= 1.0, "%s returns a legal scale" % nm)

    # L6 the engine refuses a rule that tries to lever up or returns nonsense
    close = pd.DataFrame({"a": np.linspace(10, 20, 300), "b": np.linspace(10, 15, 300)},
                         index=pd.bdate_range("2020-01-01", periods=300))
    op = close.copy()
    amt = pd.DataFrame(1e9, index=close.index, columns=close.columns)
    sc = pd.DataFrame({"a": 1.0, "b": 0.5}, index=close.index)

    def bad(_b, _d, _p, _v):
        return 1.5

    raised = False
    try:
        R.open_to_open_equity(close, op, amt, sc, 20, 1, 0.001, scale_hook=bad)
    except ValueError:
        raised = True
    chk(raised, "the engine raises on a scale above 1 instead of clamping silently")

    both = False
    try:
        R.open_to_open_equity(close, op, amt, sc, 20, 1, 0.001, vol_target=0.08,
                              scale_hook=rule_trend_brake)
    except ValueError:
        both = True
    chk(both, "vol_target and scale_hook are refused together")

    # L7 a hook returning 1.0 everywhere is bit-identical to no hook at all
    s_ref, _ = R.open_to_open_equity(close, op, amt, sc, 20, 1, 0.001)
    s_one, _ = R.open_to_open_equity(close, op, amt, sc, 20, 1, 0.001,
                                     scale_hook=lambda b, d, p, v: 1.0)
    chk(float(np.max(np.abs(s_ref.to_numpy() - s_one.to_numpy()))) < 1e-12,
        "a hook that de-risks by nothing reproduces the plain engine exactly")

    # L8 a hook that halves the book really halves it (not a silent no-op)
    s_half, _ = R.open_to_open_equity(close, op, amt, sc, 20, 1, 0.001,
                                      scale_hook=lambda b, d, p, v: 0.5)
    chk(float(s_half.iloc[-1]) < float(s_ref.iloc[-1]),
        "halving the book reduces the terminal equity on a rising panel")

    # L9 the gate is imported, and both directions still work
    chk(G.TOP2_SHARE_MAX == 0.70 and G.WORST_YEAR_FLOOR_PP == -15.0,
        "gate lines come from the frozen module")
    carried = {"2020": 1.0, "2021": 2.0, "2022": 2.0, "2023": 3.0, "2024": 25.0}
    blk = G.admission_block({str(y): {"net_pct": v, "cohorts": 4}
                             for y, v in carried.items()}, None, None, 0.08)
    chk(blk["checks"]["Y4_top2_share"] is False, "a two-year book still fails Y4")
    even = {str(y): 8.0 for y in range(2020, 2026)}
    blk2 = G.admission_block({str(y): {"net_pct": v, "cohorts": 4}
                              for y, v in even.items()}, None, None, 0.08)
    chk(blk2["verdict"] == "ADMIT", "an even ladder still passes (so failures are the books)")

    # L10 the answer word follows from the rows in both directions
    ctrl = {"rule": "none", "verdict": "ADMIT", "maxdd_pct": -0.16, "sharpe": 1.0,
            "checks": {"Y4_top2_share": True}, "year_metrics": {"top2_share": 0.68}}
    good = {"rule": "r", "verdict": "ADMIT", "maxdd_pct": -0.12, "sharpe": 1.1,
            "checks": {"Y4_top2_share": True}, "year_metrics": {"top2_share": 0.69}}
    small = {"rule": "s", "verdict": "ADMIT", "maxdd_pct": -0.159, "sharpe": 1.0,
             "checks": {"Y4_top2_share": True}, "year_metrics": {"top2_share": 0.69}}
    badg = {"rule": "b", "verdict": "CONDITIONAL", "maxdd_pct": -0.10, "sharpe": 1.2,
            "checks": {"Y4_top2_share": False}, "year_metrics": {"top2_share": 0.71}}
    chk(reads([ctrl, good], ctrl)["answer"] == "RULE_FAMILY_HAS_MEMBER",
        "a rule that passes and buys drawdown is reported by name")
    chk(reads([ctrl, small], ctrl)["answer"] == "NO_RULE_CLEARS_BOTH",
        "a rule that passes but does not buy drawdown does not settle the question")
    chk(reads([ctrl, badg], ctrl)["answer"] == "NO_RULE_CLEARS_BOTH",
        "a rule that buys drawdown but fails the gate does not settle it either")
    chk(reads([], None)["answer"] == "UNKNOWN", "an empty family is UNKNOWN")

    # L11 phase dependence is named, and cannot be read as an acceptance
    ph_mixed = {"r": {"phases": [{"passes": True}, {"passes": False}],
                      "passes_all_phases": False}}
    r11 = reads([ctrl, good], ctrl, ph_mixed)
    chk(r11["answer"] == "NO_RULE_CLEARS_BOTH" and "r" in r11["phase_dependent_rules"],
        "a rule passing in some phases only is named phase-dependent, not accepted")
    ph_all = {"r": {"phases": [{"passes": True}, {"passes": True}],
                    "passes_all_phases": True}}
    chk(reads([ctrl, good], ctrl, ph_all)["answer"] == "RULE_FAMILY_HAS_MEMBER",
        "a rule passing every phase is accepted")
    # L12 the mechanism block quotes its own rows
    mrow = dict(good)
    mrow.update({"de_risk_share": 0.4, "annual_sum_pp": 100.0})
    c2 = dict(ctrl)
    c2.update({"annual_sum_pp": 110.0})
    m = reads([c2, mrow], c2)["mechanism"][0]
    chk(abs(m["delta_annual_sum_pp"] + 10.0) < 1e-12,
        "the mechanism delta is measured against the control, not typed")

    # L13 the ruler test: a spread that crosses the line is unresolvable, one that does
    # not is read as a FAIL (never as a pass by luck)
    def ph(vals, ctrl_vals):
        return {"x": {"phases": [{"top2_share": v, "control_top2_share": cv,
                                  "passes": v <= 0.70}
                                 for v, cv in zip(vals, ctrl_vals)]}}
    inst_a = instrument_read(ph([0.6568, 0.7067, 0.7698], [0.6855, 0.6855, 0.6855]),
                             ctrl, [ctrl])
    chk(inst_a["available"] and "x" in inst_a["unresolvable"],
        "a spread that crosses the 70% line is reported unresolvable")
    inst_b = instrument_read(ph([0.7451, 0.9144], [0.6855, 0.7629]), ctrl, [ctrl])
    chk("x" in inst_b["resolvably_above_line"] and "x" not in inst_b["unresolvable"],
        "a spread that stays above the line is a resolvable fail")
    chk(instrument_read({}, ctrl, [ctrl])["available"] is False,
        "no phase table means resolvability is unknown, not green")

    print("selftest %d/%d" % (ok, tot))
    for e in errs:
        print("  FAIL:", e)
    return 0 if not errs else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "check", "selftest"])
    ap.add_argument("--quick", action="store_true", help="skip the phase test")
    a = ap.parse_args()
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check()
    out = run(quick=a.quick)
    print(json.dumps({"answer": out["answer"],
                      "control_gate_ok": out["control_gate"]["ok"],
                      "rules": {r["rule"]: [r["verdict"], r["cagr_pct"], r["maxdd_pct"],
                                            r["year_metrics"]["top2_share"],
                                            r["de_risk_share"]]
                                for r in out["rules"]},
                      "elapsed_sec": out["elapsed_sec"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())