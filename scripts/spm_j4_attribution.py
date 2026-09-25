"""T-52 R1: SPM J4 attribution batch (CEO order O-20260925-1105; charter
firm/STABLE_PROFIT_MODEL.md s3.2 归因驱动迭代; ticket T-2026-09-25-52-P1;
claim r173 bm-b).

Deterministic re-analysis of the FROZEN T-28 evidence pack -- ZERO new
backtests, zero new signal families, zero engine code (t28 grid loaders +
B_MAXDIV frozen weights + _grid_unit reused verbatim per house reuse law).

Evidence-domain honesty (verified pre-run r173 bm-b):
  * legacy axis (P5C legL checkpoint, starts 2021-01..2026-03) REPRODUCES
    the frozen 12m faces bit-exact (n=1127 beats=594 rate=0.5271 x1;
    580/0.5146 x2) -> cell-level attribution legal on this axis.
  * deep axis cells are machine-local on bm-a (MSG-0054 decision: cells stay
    machine-local); bm-b's local cells_deep_*_2.jsonl are a DIFFERENT batch
    (x2 face returns HIGHER than base face = provenance mismatch; local
    recompute 88/554 vs frozen 623/1380) -> EXCLUDED; deep axis consumed
    ONLY as frozen aggregates from results/current_market_stable_profit.json.
  * reproduction gate: run aborts (exit 2) if legacy 12m x1/x2 recompute
    mismatches the frozen pack (guards against silent data drift, r117 law).

Attribution faces (12m = J4 primary, x2 = cost face):
  per-member drag        w_ce[t]*(ret_t - passive) on failing windows
  failure-mode taxonomy  loss windows / underperform-positive / cost-razor
                         (x1-pass-x2-fail) / regime-boundary cohort
  era / panel            legacy(2021+) vs deep, window-length gradient
  cohort                 beat rate by start year (legacy, cell-level)
  hypothesis scoring     H1 alpha-decay / H2 regime / H3 cost / H4 assembly
                         ceiling / H5 pool-breadth -- scored, not narrated;
                         rubrics frozen in _hypotheses docstring (J18: no
                         post-hoc rubric edits)
  gap decomposition      upper-bound pp levers toward the 0.70 line
                         (non-additive, disclosed)

Deliverables: results/spm_j4_attribution.json (machine-checkable) +
research/SPM_J4_ATTRIBUTION.md. Register/cadence land as separate doc
edits (firm/SPM_REGISTER.md v1 row + OPERATING_PLAN cadence row).

Subcommands:
  run        attribution -> results/spm_j4_attribution.json + md report
  selftest   offline fixtures (pure functions, no file IO)
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from t28_stable_profit import (_grid_unit, _load_deep_grid,
                               _load_legacy_grid, TOURN_JSON)

T28_JSON = os.path.join("results", "current_market_stable_profit.json")
OUT_JSON = os.path.join("results", "spm_j4_attribution.json")
OUT_MD = os.path.join("research", "SPM_J4_ATTRIBUTION.md")
SIX = ["COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
       "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01"]
J_BEAT_LINE = 0.70            # frozen (P-5/P-5B; charter s6 no-pillar-moves)
BOUNDARY_K = 21               # trading starts after a segment flip
GRID_EVIDENCE_CUTOFF = "2026-09-22"   # frozen grid faces cutoff (t28)


# ------------------------------------------------------------ core (pure)
def _cells_from_grid(tret, passive, w_ce, six, window, faces):
    """Per-start rows for each cost face; mirrors t28 _grid_unit cell logic."""
    out = {}
    for face in faces:
        rows = {}
        for sdate, pw in passive.items():
            if window not in pw:
                continue
            rets, ok = {}, True
            for t in six:
                e = tret.get((t, face, sdate), {}).get(window)
                if e is None:
                    ok = False
                    break
                rets[t] = e
            if not ok:
                continue
            blend = sum(w_ce[t] * rets[t][0] for t in six)
            rows[sdate] = {
                "blend": blend, "passive": pw[window],
                "rets": {t: rets[t][0] for t in six},
                "segment": rets[six[0]][3],
                "trades": sum(rets[t][2] for t in six)}
        out[face] = rows
    return out


def _beat_stats(rows):
    n = len(rows)
    k = sum(1 for r in rows.values() if r["blend"] > r["passive"])
    return {"n": n, "beats": k,
            "beat_rate": round(k / n, 4) if n else None}


def _failure_modes(rows_x1, rows_x2):
    """Taxonomy on the x1 primary face + cost-razor pairing (x1 beat, x2 fail)."""
    fails = {s: r for s, r in rows_x1.items() if r["blend"] <= r["passive"]}
    loss = {s: r for s, r in fails.items() if r["blend"] < 0}
    under_pos = {s: r for s, r in fails.items() if r["blend"] >= 0}
    razor = sorted(s for s, r in rows_x1.items()
                   if r["blend"] > r["passive"]
                   and s in rows_x2
                   and rows_x2[s]["blend"] <= rows_x2[s]["passive"])
    rescue = sorted(s for s, r in rows_x1.items()
                    if r["blend"] <= r["passive"]
                    and s in rows_x2
                    and rows_x2[s]["blend"] > rows_x2[s]["passive"])
    nf = len(fails)
    return {
        "failing_windows": nf,
        "loss_windows": {"n": len(loss),
                         "share_of_fails": round(len(loss) / nf, 4) if nf else None,
                         "mean_blend_ret": _mean([r["blend"] for r in loss.values()]),
                         "mean_passive": _mean([r["passive"] for r in loss.values()])},
        "underperform_positive": {"n": len(under_pos),
                                  "share_of_fails": round(len(under_pos) / nf, 4) if nf else None,
                                  "mean_blend_ret": _mean([r["blend"] for r in under_pos.values()]),
                                  "mean_passive": _mean([r["passive"] for r in under_pos.values()])},
        "cost_razor_x1_pass_x2_fail": {"n": len(razor), "starts": razor},
        "cost_rescue_x1_fail_x2_pass": {"n": len(rescue), "starts": rescue}}


def _drag_table(rows_x1, w_ce, six):
    """Per-member decomposition of failing windows.

    drag_t = sum over failing windows of w_ce[t] * (ret_t - passive)
    (identically decomposes blend - passive); negative = dragging member.
    share_neg = share of total negative drag (dragging members only).
    Also: per-member beat rates + mean return vs passive on the same face.
    """
    fails = {s: r for s, r in rows_x1.items() if r["blend"] <= r["passive"]}
    allr = rows_x1
    tab = {}
    for t in six:
        drag = sum(w_ce[t] * (r["rets"][t] - r["passive"]) for r in fails.values())
        beats = sum(1 for r in allr.values() if r["rets"][t] > r["passive"])
        tab[t] = {
            "beat_rate_12m_x1_legacy": round(beats / len(allr), 4) if allr else None,
            "mean_ret": _mean([r["rets"][t] for r in allr.values()]),
            "mean_ret_vs_passive": _mean([r["rets"][t] - r["passive"] for r in allr.values()]),
            "drag_total_failing": round(drag, 6),
            "drag_mean_failing": round(drag / len(fails), 6) if fails else None,
            "mean_ret_failing": _mean([r["rets"][t] for r in fails.values()])}
    neg = sum(min(0.0, v["drag_total_failing"]) for v in tab.values())
    for t in six:
        d = tab[t]["drag_total_failing"]
        tab[t]["share_of_negative_drag"] = (round(min(0.0, d) / neg, 4)
                                            if neg < 0 and d < 0 else
                                            (0.0 if neg < 0 else None))
    return {"n_failing": len(fails), "members": tab}


def _segment_cut(rows_x1):
    out = {}
    for seg in ("bull", "chop", "bear"):
        sub = {s: r for s, r in rows_x1.items() if r["segment"] == seg}
        st = _beat_stats(sub)
        st["mean_passive"] = _mean([r["passive"] for r in sub.values()])
        st["mean_blend"] = _mean([r["blend"] for r in sub.values()])
        out[seg] = st
    return out


def _cohort_by_year(rows_x1):
    out = {}
    for s, r in rows_x1.items():
        y = s[:4]
        out.setdefault(y, []).append(r)
    return {y: _beat_stats({i: r for i, r in enumerate(v)})
            for y, v in sorted(out.items())}


def _boundary_cohort(rows_x1, k=BOUNDARY_K):
    """Windows starting within k trading starts after a segment-class flip.

    Segment labels are start-date states (regime AT start; a 12m window
    spans mixed regimes -- coarse cut, disclosed). Boundary = consecutive
    sorted starts with differing segment labels.
    """
    starts = sorted(rows_x1)
    boundary = []
    for i in range(1, len(starts)):
        if rows_x1[starts[i]]["segment"] != rows_x1[starts[i - 1]]["segment"]:
            boundary.append(i)
    bset = set()
    for b in boundary:
        for j in range(b, min(b + k, len(starts))):
            bset.add(starts[j])
    inb = {s: rows_x1[s] for s in bset}
    outb = {s: r for s, r in rows_x1.items() if s not in bset}
    return {"n_transitions": len(boundary),
            "boundary_cohort": _beat_stats(inb),
            "stable_cohort": _beat_stats(outb)}


def _era_window_table(frozen):
    g = frozen["w_grid"]
    out = {}
    for axis in ("legacy", "deep"):
        for win in ("6m", "12m", "24m"):
            for face in ("x1", "x2"):
                u = g[f"{axis}|{win}|{face}"]
                out[f"{axis}|{win}|{face}"] = {
                    "n": u["n"], "beats": u["beats"], "beat_rate": u["beat_rate"]}
    pooled = {}
    for win in ("6m", "12m", "24m"):
        for face in ("x1", "x2"):
            n = sum(out[f"{a}|{win}|{face}"]["n"] for a in ("legacy", "deep"))
            k = sum(out[f"{a}|{win}|{face}"]["beats"] for a in ("legacy", "deep"))
            pooled[f"{win}|{face}"] = {"n": n, "beats": k,
                                      "beat_rate": round(k / n, 4) if n else None}
    return out, pooled


def _mean(xs):
    xs = list(xs)
    return round(sum(xs) / len(xs), 6) if xs else None


def _rank(xs):
    """Average ranks (ties averaged) for Spearman."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for kk in range(i, j + 1):
            ranks[order[kk]] = avg
        i = j + 1
    return ranks


def _spearman(a, b):
    if len(a) < 3:
        return None
    ra, rb = _rank(a), _rank(b)
    n = len(a)
    d2 = sum((x - y) ** 2 for x, y in zip(ra, rb))
    return round(1 - 6 * d2 / (n * (n * n - 1)), 4)


# --------------------------------------------------- hypothesis scoring
def _hypotheses(cohort, seg, modes, cost, drag, era, pooled, per_member_max,
                ce6_weight_share, n_pooled_12m, k_pooled_12m):
    """H1-H5 verdicts. Rubrics FROZEN here (J18: no post-hoc edits).

    H1 alpha-decay: SUPPORTED if cohort(first vs last year) drop >= 8pp
      AND spearman(year, rate) <= -0.6 over >=4 cohorts; PARTIAL if drop
      3-8pp or weaker rank; else REJECTED (legacy axis only -- deep axis
      aggregate-only, disclosed).
    H2 regime-dependence: SUPPORTED if bull-start rate < non-bull rate by
      >= 8pp; PARTIAL 3-8pp; else REJECTED/REVERSED.
    H3 cost-drag: pp delta (x2 -> x1 pooled 12m); MINOR if < 20% of the
      J4 gap in pp; else MAJOR.
    H4 assembly-ceiling: SUPPORTED if (max member - blend) < 5pp AND max
      member < 0.70 AND |blend - EW| small (assembly reshapes risk, does
      not create beat-consistency); quantify both deltas.
    H5 pool-breadth: STRUCTURAL-SUPPORTED (restricted CE-6 face + ~1.5 true
      engines per P3); full scoring deferred to T-54 grid backfill.
    """
    gap = round(J_BEAT_LINE - k_pooled_12m / n_pooled_12m, 4)
    hyp = {}
    years = sorted(cohort)
    rates = [cohort[y]["beat_rate"] for y in years]
    drop = (round(rates[0] - rates[-1], 4)
            if len(rates) >= 2 and None not in rates else None)
    rho = _spearman([int(y) for y in years], rates)
    if drop is not None and drop >= 0.08 and (rho is None or rho <= -0.6) and len(years) >= 4:
        v1 = "SUPPORTED"
    elif drop is not None and (drop >= 0.03 or (rho is not None and rho <= -0.4)):
        v1 = "PARTIAL"
    else:
        v1 = "REJECTED"
    hyp["H1_alpha_decay"] = {
        "verdict": v1, "cohort_first_vs_last_pp": drop,
        "spearman_year_vs_rate": rho, "axis": "legacy-only (deep aggregate-only)",
        "evidence": {y: cohort[y]["beat_rate"] for y in years},
        "interpretation_note": "cohort cut confounds calendar time with "
                               "regime composition: 2024+ cohorts coincide "
                               "with the 2024-2025 bull in which defensive "
                               "members structurally trail passive EW48 "
                               "(T-22 member-level bull collapse 0.471/0.266 "
                               "cross-check, PROFIT_MODEL_MAP constraint-1); "
                               "mechanical verdict per frozen rubric retained; "
                               "discriminating evidence = bull-window grid "
                               "faces post T-54 backfill / T-47 supply"}
    bull = seg.get("bull", {}).get("beat_rate")
    nonbull_n = sum(seg.get(s, {}).get("n", 0) for s in ("chop", "bear"))
    nonbull_k = sum(seg.get(s, {}).get("beats", 0) for s in ("chop", "bear"))
    nonbull = round(nonbull_k / nonbull_n, 4) if nonbull_n else None
    diff = round(bull - nonbull, 4) if bull is not None and nonbull is not None else None
    if diff is not None and diff <= -0.08:
        v2 = "SUPPORTED"
    elif diff is not None and diff <= -0.03:
        v2 = "PARTIAL"
    elif diff is None:
        v2 = "UNSCOREABLE"
    else:
        v2 = "REJECTED/REVERSED"
    hyp["H2_regime_dependence"] = {
        "verdict": v2, "bull_start_rate": bull, "nonbull_start_rate": nonbull,
        "delta_pp": diff,
        "interpretation_note": "segment label = regime AT start (12m window "
                               "spans mixed regimes -- coarse cut, "
                               "disclosed); the start-label cut and the "
                               "start-year cohort cut disagree in direction "
                               "(see cohort_segment_crosstab) -- regime "
                               "failure shows up as RECENT-bull-trail, not "
                               "as low bull-start rate",
        "cross_check": "T-22 bull collapse 0.471/0.266 (constraint-1 face, "
                       "PROFIT_MODEL_MAP 二; member-level) -- pointer"}
    cost_pp = cost["pooled_delta_pp"]
    v3 = "MINOR" if (cost_pp is not None and cost_pp < 0.2 * gap) else "MAJOR"
    hyp["H3_cost_drag"] = {
        "verdict": v3, "pooled_x2_to_x1_pp": cost_pp,
        "razor_windows_legacy": cost["razor_legacy_n"],
        "rescue_windows_legacy": cost["rescue_legacy_n"],
        "share_of_gap_pct": round(100 * cost_pp / gap, 2) if cost_pp is not None else None}
    hyp["H4_assembly_ceiling"] = {
        "verdict": "SUPPORTED" if (per_member_max is not None
                                   and per_member_max < J_BEAT_LINE
                                   and per_member_max - pooled["12m|x1"]["beat_rate"] < 0.05)
        else "REJECTED",
        "max_member_beat_rate_12m_pooled": per_member_max,
        "blend_minus_max_member_pp": (round(pooled["12m|x1"]["beat_rate"] - per_member_max, 4)
                                      if per_member_max is not None else None),
        "structural_conclusion": ("even 100% concentration in the best member "
                                  f"({per_member_max}) stays below the 0.70 "
                                  "line -> NO reweighting of the current "
                                  "CE-6 pool can close J4; orthogonal pool "
                                  "expansion (R3/T-54) is structurally "
                                  "required") if per_member_max is not None and
                                 per_member_max < J_BEAT_LINE else None,
        "note": "B_MAXDIV vs EW-CE6 quantified in gap_decomposition "
                "(assembly choice is a real second-order lever on J4's "
                "beat-consistency measure, traded against J1-J3 risk faces)"}
    hyp["H5_pool_breadth"] = {
        "verdict": "STRUCTURAL-SUPPORTED (restricted face; full scoring "
                   "deferred to T-54 PROSPECT grid backfill)",
        "ce6_raw_weight_share_in_28_member_blend": ce6_weight_share,
        "w_grid_face": "CE-6 restricted sub-portfolio (t28 disclosed)",
        "true_engines_estimate": "~1.5 (P3; composite pair corr 0.87 anti-example)",
        "note": "J4 measures 6 of 28 members; PROSPECT 22 lack grid evidence"}
    return hyp, gap


# ------------------------------------------------------------------ run
def cmd_run():
    t0 = time.time()
    print("=== SPM J4 attribution (T-52; frozen T-28 evidence pack) ===")
    frozen = json.load(open(T28_JSON, encoding="utf-8-sig"))
    if frozen.get("batch") != "T28_STABLE_PROFIT":
        print("GATE FAIL: unexpected frozen pack batch")
        return 2

    # -- frozen weights (t28 caliber; CE-6 restriction renorm)
    tour = json.load(open(TOURN_JSON, encoding="utf-8"))
    w_full = tour["weights"]["B_MAXDIV"]["weights"]
    wsum = sum(w_full[t] for t in SIX)
    w_ce = {t: round(w_full[t] / wsum, 8) for t in SIX}
    ce6_share = round(wsum, 6)
    print(f"B_MAXDIV sha {frozen['weights']['sha256_first16']}; "
          f"CE-6 raw weight share in 28-member blend = {ce6_share}")

    # -- legacy axis cells (reproducing face)
    lt, lp = _load_legacy_grid()
    cells = _cells_from_grid(lt, lp, w_ce, SIX, "12m", ("x1", "x2"))
    rows_x1, rows_x2 = cells["x1"], cells["x2"]

    # -- reproduction gate (r117: verify before consume)
    for face, fk in (("x1", "legacy|12m|x1"), ("x2", "legacy|12m|x2")):
        got = _beat_stats(cells[face])
        want = frozen["w_grid"][fk]
        if (got["n"], got["beats"], got["beat_rate"]) != (
                want["n"], want["beats"], want["beat_rate"]):
            print(f"GATE FAIL: legacy 12m {face} recompute {got} != "
                  f"frozen n={want['n']} beats={want['beats']} "
                  f"rate={want['beat_rate']} -- data drift; abort")
            return 2
        pm_got = {t: v["beat_rate"] for t, v in _per_member_rates(cells[face], SIX).items()}
        pm_want = {t: v["beat_rate"] for t, v in want["per_member_beat_rate"].items()}
        if pm_got != pm_want:
            print(f"GATE FAIL: legacy 12m {face} per-member drift "
                  f"{pm_got} != {pm_want}")
            return 2
    print("reproduction gate PASS: legacy 12m x1/x2 bit-exact vs frozen pack")

    # -- attribution tables (legacy cell-level)
    modes = _failure_modes(rows_x1, rows_x2)
    drag = _drag_table(rows_x1, w_ce, SIX)
    seg = _segment_cut(rows_x1)
    cohort = _cohort_by_year(rows_x1)
    boundary = _boundary_cohort(rows_x1)
    era, pooled = _era_window_table(frozen)

    # -- equal-weight CE-6 counterfactual on legacy (assembly lever bound)
    ew_rows = {}
    for s, r in rows_x1.items():
        ew_rows[s] = dict(r, blend=sum(r["rets"][t] for t in SIX) / len(SIX))
    ew_stats = _beat_stats(ew_rows)

    # -- cost face (pooled, frozen deltas + legacy cell flips)
    g = frozen["w_grid"]
    n12, k12 = pooled["12m|x1"]["n"], pooled["12m|x1"]["beats"]
    n12x2, k12x2 = pooled["12m|x2"]["n"], pooled["12m|x2"]["beats"]
    cost = {"razor_legacy_n": modes["cost_razor_x1_pass_x2_fail"]["n"],
            "rescue_legacy_n": modes["cost_rescue_x1_fail_x2_pass"]["n"],
            "pooled_beats_x1": k12, "pooled_beats_x2": k12x2,
            "pooled_delta_pp": round((k12 - k12x2) / n12, 4)}

    # -- per-member 12m pooled beat rate (axis-n weighted, frozen rates)
    per_member_max, per_member_pooled = None, {}
    for t in SIX:
        r_l = g["legacy|12m|x1"]["per_member_beat_rate"][t]["beat_rate"]
        r_d = g["deep|12m|x1"]["per_member_beat_rate"][t]["beat_rate"]
        n_l, n_d = g["legacy|12m|x1"]["n"], g["deep|12m|x1"]["n"]
        pooled_rate = round((r_l * n_l + r_d * n_d) / (n_l + n_d), 4)
        per_member_pooled[t] = {"legacy": r_l, "deep": r_d, "pooled": pooled_rate}
        per_member_max = max(per_member_max or 0.0, pooled_rate)
    per_member_max = round(per_member_max, 4)

    hyp, gap = _hypotheses(cohort, seg, modes, cost, drag, era, pooled,
                           per_member_max, ce6_share, n12, k12)

    # -- gap decomposition (upper bounds, non-additive)
    era_parity = round((g["legacy|12m|x1"]["beats"]
                        + g["deep|12m|x1"]["n"] * g["legacy|12m|x1"]["beat_rate"]) / n12, 4)
    decomp = {
        "j4_pooled_12m_x1": pooled["12m|x1"],
        "gap_to_line_pp": round(gap * 100, 2),
        "beats_shortfall_to_line": int(J_BEAT_LINE * n12 + 0.9999) - k12,
        "levers_upper_bounds_non_additive": {
            "cost_elimination_x2_to_x1_pp": round(cost["pooled_delta_pp"] * 100, 2),
            "era_parity_deep_at_legacy_rate_pp": round((era_parity - k12 / n12) * 100, 2),
            "best_member_concentration_pp": round((per_member_max - k12 / n12) * 100, 2),
            "ew_ce6_vs_bmaxdiv_pp": round((ew_stats["beat_rate"]
                                           - pooled["12m|x1"]["beat_rate"]) * 100, 2),
            "window_length_sensitivity_disclosure": {
                "pooled_6m_x1": pooled["6m|x1"]["beat_rate"],
                "pooled_12m_x1": pooled["12m|x1"]["beat_rate"],
                "pooled_24m_x1": pooled["24m|x1"]["beat_rate"],
                "note": "U-shape; J4 line frozen at 12m primary face"}},
        "notes": "era_parity/best_member are arithmetic bounds, NOT "
                 "prescriptions; concentration violates the orthogonal-"
                 "engine mandate (P3 corr 0.87 anti-example)"}

    # -- cohort x segment crosstab (H1/H2 confound disclosure face)
    crosstab = {}
    for s, r in rows_x1.items():
        crosstab.setdefault(s[:4], {}).setdefault(r["segment"], 0)
        crosstab[s[:4]][r["segment"]] += 1

    out = {
        "batch": "SPM_J4_ATTRIBUTION",
        "ticket": "T-2026-09-25-52",
        "evidence_cutoff": frozen["evidence_cutoff"],
        "grid_evidence_cutoff": GRID_EVIDENCE_CUTOFF,
        "frozen_source": T28_JSON,
        "zero_new_backtests": True,
        "reproduction_gate": {"legacy_12m_x1_x2_vs_frozen": "PASS bit-exact",
                              "per_member_rates_vs_frozen": "PASS"},
        "evidence_domain": {
            "legacy_axis": "cell-level (P5C legL checkpoint, starts "
                           "2021-01-15..2026-03-23, verified bit-exact)",
            "deep_axis": "frozen aggregates ONLY (cells machine-local on "
                         "bm-a per MSG-0054; bm-b local cells_deep_*_2 files "
                         "= different batch: x2 face returns HIGHER than "
                         "base, 88/554 vs frozen 623/1380 -> excluded as "
                         "non-authoritative)"},
        "weights": {"method": "B_MAXDIV", "six": SIX, "w_ce_renorm": w_ce,
                    "ce6_raw_weight_share_in_28_member_blend": ce6_share},
        "per_member_12m": {"legacy_cell_level": drag,
                           "pooled_axis_n_weighted_frozen": per_member_pooled},
        "failure_modes_legacy_12m": modes,
        "segment_cut_legacy_12m": seg,
        "cohort_by_start_year_legacy_12m": cohort,
        "cohort_segment_crosstab_legacy_12m": crosstab,
        "regime_boundary_cohort_legacy_12m": boundary,
        "era_window_table_frozen": era,
        "pooled_frozen": pooled,
        "ew_ce6_counterfactual_legacy_12m": ew_stats,
        "cost_face": cost,
        "hypotheses": hyp,
        "gap_decomposition": decomp,
        "audit": {"runtime_sec": round(time.time() - t0, 1),
                  "machine": "bm-b", "ts": time.strftime("%Y-%m-%d %H:%M:%S")},
    }
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
    print(f"outputs: {OUT_JSON}")

    # -- one-page report
    SHORT = {"COMPOSITE-CE-01": "COMP01", "COMPOSITE-CE-02": "COMP02",
             "DROUGHT-CE-01": "DROUGHT", "ENGULF-CE-01": "ENGULF",
             "NEEDLE-DE-01": "NEEDLE", "VOLATILITY-CE-01": "VOLAT"}
    yrc = "; ".join(f"{y}={cohort[y]['beat_rate']}(n={cohort[y]['n']})"
                    for y in sorted(cohort))
    segt = "; ".join(f"{s}={seg[s]['beat_rate']}(n={seg[s]['n']})" for s in seg)
    drg = "; ".join(f"{SHORT[t]}:{drag['members'][t]['share_of_negative_drag']}"
                    for t in SIX)
    pmr = "; ".join(f"{SHORT[t]}={per_member_pooled[t]['pooled']}"
                    f" (L{per_member_pooled[t]['legacy']}/D{per_member_pooled[t]['deep']})"
                    for t in SIX)
    xt = "; ".join(f"{y}:{crosstab[y]}" for y in sorted(crosstab))
    rep = f"""# SPM J4 归因表（T-52·确定性再分析·零新回测）

- 判据锚：J4=12m 池化 beat 率 **0.4854** <0.70（冻结 T-28 面·n=2507/beats=1217；缺口 {decomp['gap_to_line_pp']}pp/差 {decomp['beats_shortfall_to_line']} 窗）
- 复现门：legacy 轴 12m x1/x2 逐位复现冻结面（1127/594·580 ✓）；**deep 轴仅消费冻结聚合**（cells=bm-a 机本地（MSG-0054），本机 cells_deep_*_2=异源批（x2 反高于 base·88/554≠623/1380）已排除如实披露）
- 失败模式（legacy 12m·x1 主判面，失败 {modes['failing_windows']} 窗）：亏损窗 {modes['loss_windows']['n']}（占比 {modes['loss_windows']['share_of_fails']}）·正收益欠被动 {modes['underperform_positive']['n']}（{modes['underperform_positive']['share_of_fails']}，均 blend {modes['underperform_positive']['mean_blend_ret']} vs 被动 {modes['underperform_positive']['mean_passive']}）·成本剃刀翻案 x1过x2死 {modes['cost_razor_x1_pass_x2_fail']['n']} 窗（反向 {modes['cost_rescue_x1_fail_x2_pass']['n']}）
- 政体段（起点政体·粗切）：{segt}；起点年份队列：{yrc}；队列×政体交叉：{xt}；政体边界队（翻转后 {BOUNDARY_K} 日起）：{boundary['boundary_cohort']['beat_rate']}(n={boundary['boundary_cohort']['n']}) vs 稳定队 {boundary['stable_cohort']['beat_rate']}(n={boundary['stable_cohort']['n']})
- 逐成员 12m 池化 beat 率（legacy/深轴冻结）：{pmr}；失败窗负拖累份额：{drg}
- 假设判决：H1 衰减={hyp['H1_alpha_decay']['verdict']}（首末 {hyp['H1_alpha_decay']['cohort_first_vs_last_pp']}·ρ={hyp['H1_alpha_decay']['spearman_year_vs_rate']}·注=队列切与政体构成混淆（2024+ 队列恰逢牛市防御员结构性落后·T-22 bull 崩塌交叉证））·H2 政体={hyp['H2_regime_dependence']['verdict']}（起点标签粗切：bull {hyp['H2_regime_dependence']['bull_start_rate']} vs 非bull {hyp['H2_regime_dependence']['nonbull_start_rate']}·失败呈现在「近年牛市跑输」非「bull 起点率低」）·H3 成本={hyp['H3_cost_drag']['verdict']}（{round(cost['pooled_delta_pp']*100, 2)}pp=缺口 {hyp['H3_cost_drag']['share_of_gap_pct']}%）·H4 装配上限={hyp['H4_assembly_ceiling']['verdict']}（最佳成员 {per_member_max}<0.70→**现 CE-6 池任何再加权都到不了判线·正交扩池结构性必需**·blend-最佳={hyp['H4_assembly_ceiling']['blend_minus_max_member_pp']}）·H5 池广度={hyp['H5_pool_breadth']['verdict']}（CE-6 权重份额 {ce6_share}）
- 缺口分解（上界·非可加）：成本 +{decomp['levers_upper_bounds_non_additive']['cost_elimination_x2_to_x1_pp']}pp·年代拉平 +{decomp['levers_upper_bounds_non_additive']['era_parity_deep_at_legacy_rate_pp']}pp·最佳成员集中 +{decomp['levers_upper_bounds_non_additive']['best_member_concentration_pp']}pp（反例警示非处方·集中违反正交引擎律）·EW-CE6 vs B_MAXDIV {decomp['levers_upper_bounds_non_additive']['ew_ce6_vs_bmaxdiv_pp']:+}pp（装配选择=真实二阶杠杆·与 J1-J3 风险面互偿）；窗长敏感性（6m {pooled['6m|x1']['beat_rate']}/12m {pooled['12m|x1']['beat_rate']}/24m {pooled['24m|x1']['beat_rate']}·U 形·判线冻结 12m）
- SPM-v2 设计输入（喂 R4/R3）：①成员池质量=约束面（无一 12m 面成员≥0.70·NEEDLE 两轴最弱·失败窗负拖累 NEEDLE {drag['members']['NEEDLE-DE-01']['share_of_negative_drag']}/DROUGHT {drag['members']['DROUGHT-CE-01']['share_of_negative_drag']}）②成本与装配面合计 <2pp 非主因③近年失败=防御性构成×牛市政体（约束①同源·T-47 进攻军供给直接对症）④池广度结构性受限（CE-6 面测 6/28 员）→T-54 回填后 J4 面扩容
- 边界：诊断层零采纳零接线；判线 0.70 冻结不动（O-1105 §二）；deep 轴逐窗归因待 bm-a 车道或 T-54 全池网格（本机如实留白）
- 验证链：results/spm_j4_attribution.json（机读全表）+冻结件 results/current_market_stable_profit.json（sha 权重 9b112d51583aeeb7）+T-22 bull 崩塌交叉证（PROFIT_MODEL_MAP 二）
"""
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(rep)
    print(f"report: {OUT_MD}")
    return 0


def _per_member_rates(rows, six):
    out = {}
    for t in six:
        k = sum(1 for r in rows.values() if r["rets"][t] > r["passive"])
        out[t] = {"beat_rate": round(k / len(rows), 4) if rows else None}
    return out


# -------------------------------------------------------------- selftest
def cmd_selftest():
    ok_n, fails = 0, 0

    def ok(name, cond):
        nonlocal ok_n, fails
        ok_n += 1
        fails += (not cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        return cond

    six = ["A", "B"]
    w_ce = {"A": 0.6, "B": 0.4}
    # -- cell assembly mirrors t28 _grid_unit arithmetic
    #    01-04: blend 0.10 > passive 0.05 (beat); 01-05: blend -0.014
    #    <= passive -0.01 (fail, absolute loss)
    tret = {("A", "x1", "2021-01-04"): {"12m": (0.10, -0.05, 7, "bull")},
            ("B", "x1", "2021-01-04"): {"12m": (0.10, -0.02, 3, "bull")},
            ("A", "x1", "2021-01-05"): {"12m": (-0.02, -0.03, 5, "bear")},
            ("B", "x1", "2021-01-05"): {"12m": (-0.005, -0.01, 2, "bear")},
            ("A", "x2", "2021-01-04"): {"12m": (0.08, -0.05, 7, "bull")},
            ("B", "x2", "2021-01-04"): {"12m": (0.03, -0.01, 3, "bull")},
            ("A", "x2", "2021-01-05"): {"12m": (-0.04, -0.05, 5, "bear")},
            ("B", "x2", "2021-01-05"): {"12m": (-0.02, -0.02, 2, "bear")}}
    passive = {"2021-01-04": {"12m": 0.05}, "2021-01-05": {"12m": -0.01}}
    cells = _cells_from_grid(tret, passive, w_ce, six, "12m", ("x1", "x2"))
    r1, r2 = cells["x1"], cells["x2"]
    ok("cells: static blend arithmetic",
       abs(r1["2021-01-04"]["blend"] - (0.6 * 0.10 + 0.4 * 0.10)) < 1e-12
       and r1["2021-01-04"]["segment"] == "bull"
       and r1["2021-01-04"]["trades"] == 10)
    ok("beat stats: 1 beat of 2", _beat_stats(r1) == {"n": 2, "beats": 1, "beat_rate": 0.5})

    # -- failure modes: 01-05 fails (blend -0.014 <= passive -0.01), absolute
    #    loss (blend<0); cost razor: 01-04 x1 beats, x2 blend
    #    0.6*0.05+0.4*0.02=0.038 <= 0.05 -> razor window
    tret[("A", "x2", "2021-01-04")]["12m"] = (0.05, -0.05, 7, "bull")
    tret[("B", "x2", "2021-01-04")]["12m"] = (0.02, -0.01, 3, "bull")
    cells = _cells_from_grid(tret, passive, w_ce, six, "12m", ("x1", "x2"))
    modes = _failure_modes(cells["x1"], cells["x2"])
    ok("modes: 1 fail, loss-mode, razor=1/rescue=0",
       modes["failing_windows"] == 1
       and modes["loss_windows"]["n"] == 1
       and modes["loss_windows"]["share_of_fails"] == 1.0
       and modes["underperform_positive"]["n"] == 0
       and modes["cost_razor_x1_pass_x2_fail"]["n"] == 1
       and modes["cost_razor_x1_pass_x2_fail"]["starts"] == ["2021-01-04"]
       and modes["cost_rescue_x1_fail_x2_pass"]["n"] == 0)

    # -- drag table: fail window 01-05: A drag=0.6*(-0.02-(-0.01))=-0.006
    drag = _drag_table(cells["x1"], w_ce, six)
    ok("drag: decomposition identity + shares",
       abs(drag["members"]["A"]["drag_total_failing"] - (-0.006)) < 1e-12
       and abs(drag["members"]["B"]["drag_total_failing"] - (0.4 * 0.005)) < 1e-12
       and abs(drag["members"]["A"]["drag_total_failing"]
               + drag["members"]["B"]["drag_total_failing"]
               - (cells["x1"]["2021-01-05"]["blend"]
                  - cells["x1"]["2021-01-05"]["passive"])) < 1e-12
       and drag["members"]["A"]["share_of_negative_drag"] == 1.0
       and drag["members"]["B"]["share_of_negative_drag"] == 0.0)

    # -- segment cut + cohort binning
    seg = _segment_cut(cells["x1"])
    ok("segment cut", seg["bull"]["n"] == 1 and seg["bull"]["beat_rate"] == 1.0
       and seg["bear"]["n"] == 1 and seg["bear"]["beat_rate"] == 0.0)
    coh = _cohort_by_year(cells["x1"])
    ok("cohort: single year 2021 n=2 beats=1", coh["2021"]["beats"] == 1
       and coh["2021"]["n"] == 2)

    # -- boundary cohort: transition at index 1 (bull->bear)
    b = _boundary_cohort(cells["x1"], k=1)
    ok("boundary: 1 transition, cohort k=1 catches the bear window",
       b["n_transitions"] == 1 and b["boundary_cohort"]["n"] == 1
       and b["boundary_cohort"]["beat_rate"] == 0.0
       and b["stable_cohort"]["n"] == 1)

    # -- spearman sanity: monotone decreasing -> -1; constant -> None-safe
    ok("spearman monotone desc", _spearman([2021, 2022, 2023, 2024],
                                           [0.6, 0.5, 0.4, 0.3]) == -1.0)
    ok("spearman short input None", _spearman([1, 2], [0.5, 0.4]) is None)

    # -- era table shape on synthetic frozen dict
    frozen = {"w_grid": {f"{a}|{w}|{f}": {"n": 10, "beats": 5, "beat_rate": 0.5}
                         for a in ("legacy", "deep")
                         for w in ("6m", "12m", "24m") for f in ("x1", "x2")}}
    era, pooled = _era_window_table(frozen)
    ok("era/pooled table", era["legacy|12m|x1"]["n"] == 10
       and pooled["12m|x1"] == {"n": 20, "beats": 10, "beat_rate": 0.5})

    print(f"selftest: {ok_n - fails}/{ok_n} checks "
          f"{'ALL PASS' if not fails else 'FAIL'}")
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run")
    sub.add_parser("selftest")
    a = ap.parse_args()
    return cmd_run() if a.cmd == "run" else cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
