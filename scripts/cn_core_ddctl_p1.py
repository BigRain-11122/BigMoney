# -*- coding: utf-8 -*-
"""CN-CORE-DDCTL-P1 -- core-leg drawdown-control doctrine batch runner
(T-2026-09-26-73 s3 slice-6, R261 frozen s8 residual pointer 2).

Prereg FROZEN research/CN_CORE_DDCTL_PREREG.md (R263 freeze commit
precedes ANY run). Zero threshold edits post-run; s7/s8 backfill is the
only sanctioned prereg edit (control plane, not here).

Mechanism (prereg s3.1/s3.2): hysteresis gate on the CORE ballast leg
(510880) own trailing-252d drawdown, evaluated on the family quarterly
grid (anchor 62 step 63) from first_active 2013-07-17, state carried
across periods:
    OFF -> ON  when dd_r <  -X/100   (strictly below)
    ON  -> OFF when dd_r >  -X/200   (half-threshold re-entry)
X in {10, 20} (two-caliber frozen axis, no search). dd = core
clean_value / trailing-252 rolling max - 1 on the FULL union calendar
(family signal convention: the timeline floor truncates only the SIM
window, never signal history). Gate states are PRECOMPUTED by a pure
function (no closure mutation = deterministic re-run face).

Cells (prereg s0: judged grid = 4, K=100 nulls NOT in the skill grid):
  CORE_DD10 / CORE_DD20 : gate OFF -> {510880: 1.0}; ON -> {} (all cash;
      de-risk NOT reallocate -- freed weight goes to cash, never to the
      satellite; prereg s3.2 doctrine face)
  SAT40_DD10 / SAT40_DD20 : gate OFF -> {core 0.6 + satellite argmax
      0.4}; ON -> {satellite argmax 0.4} (satellite NEVER gated --
      family s5.3 booked the satellite-gate zero-relief MISS; the gate
      sits on the CORE leg per the R261 doctrine residual).
  Satellite = family law verbatim: trailing-252 strict-full-window clean
  return, MIN_AVAIL=3, argmax, strict-tie equal split, single window.

Nulls (prereg s3.4): K=100 = 2 arms x 50. Each null = random satellite
sleeve (one uniform draw among AVAILABLE legs per rebalance, family rng
face) + SAT40 weight structure + the SAME-ARM core dd gate (gate is the
held-constant mechanism; randomization face = leg selection). Seeds:
DD10 arm = rng(20261130+k) k<50; DD20 arm = rng(20261180+k) k<50.
Registered: science_gates.SEED_REGISTRY['cn_core_ddctl_p1']=20261130 at
the R263 freeze commit (one-step R250 law, band 20261130..20261229
collision-free). Judged-vs-null difference face = satellite selection
only; CORE_DD cells (satellite-free) are judged against the
satellite-bearing null pool = conservative face, prereg note.

Baselines (disclosure only, x2, activation-anchored): core-only buy-hold
510880 + SAT40_bare UNGATED composite (the dd-increment yardstick =
family strongest judged-negative cell re-derived in-batch) + static
80/20 core/EW-available-satellite.

Machinery reuse (anti-repeat law -- zero new judge code): CS =
cn_core_sat_p1 (panel loader + family gates + rebal schedule + hermetic
fixtures + h4 disclosure face), DRV = cn_div_lowvol_rot_p1 engine
(LEGS=8 + five-window crisis list ALREADY injected by the CS import),
SRP = t73_s2_style_rotation (union loader / envelope event detector /
clean_rets / clean_value single sources), science_gates shared criteria
(zero hand-copied lines), cn_rev_tilt_p1 (D6 member faces + regime
column).

Faces (prereg s2, family-verbatim): panel = 8-leg union timeline T=3333
(2013-01-04..2026-09-22), cutoff 2026-09-22 (D2 lockbox), frozen event
set 3 (510500 x2, 512100 x1), CORE zero events, clean_value bridge sim
prices, ADV20 = raw volume x close rolling-20 CNY, V2 ADV20-tiered cost
with 1% ADV day-queued fills, judge face x2 always on, x1/x3 disclosure
tracks. Data gates fail-closed exit 2 on any drift (date-drift refusal
law) INCLUDING the frozen dd-axis probe identity (arm transition counts
/ gated rebalance counts / first-ON dates must equal
results/core_ddctl_probe.json exactly).

Products (prereg s6): results/cn_core_ddctl/p1_results.json (top-level
evidence_cutoff + cutoff_meta + 4 cells x {x1,x2,x3} + nulls100 +
3 baselines + D6 + gate-axis audit) + cells_summary.csv; ledger append
single-shot at finalize (CN_CORE_DDCTL_P1_REFINALIZE=1 = only redo
path); attrition row lands in the ENTRIES list (r248 consumer law).
No mid-batch npz checkpoints (single pass <5min; the finalized results
JSON IS the landed marker; relaunch after landing = idempotent fast
path exit 0).

Usage: run | selftest   (exit 0 ok; 2 = fail-closed gate/mechanism
refusal; 1 = selftest FAIL)
"""
import argparse
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "screening"))

import numpy as np
import pandas as pd

import science_gates as sg
import t73_s2_style_rotation as SRP
import cn_core_sat_p1 as CS          # family single source (frozen batch)
import cn_div_lowvol_rot_p1 as DRV   # engine (CS import injected LEGS=8)
from pbo import cscv_pbo, align_returns
from cn_rev_tilt_p1 import (_corr, d6_block, load_member_rets,
                            regime_v3_column)

TICKET = "T-2026-09-26-73"
PREREG = os.path.join(ROOT, "research", "CN_CORE_DDCTL_PREREG.md")
PROBE_JSON = os.path.join(ROOT, "results", "core_ddctl_probe.json")
OUT_DIR = os.path.join(ROOT, "results", "cn_core_ddctl")
OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")
LOG_PATH = os.path.join(OUT_DIR, "runner.log")

EVIDENCE_CUTOFF = CS.EVIDENCE_CUTOFF       # 2026-09-22 (family D2 lockbox)
OOS_START = CS.OOS_START                   # 2025-01-01 shared split
SEED_BASE = 20_261_130                     # SEED_REGISTRY['cn_core_ddctl_p1']
K_PER_ARM = 50
K_NULLS = 100                              # 2 arms x 50 (prereg s3.4)
BATCH_CELLS = 4
LEDGER_TRIALS = 104                        # 4 cells + 100 nulls (D1 bill)
CORE = CS.CORE                             # 510880
SAT = CS.SAT                               # 7 style ETFs
THRESHOLDS = {"DD10": 10, "DD20": 20}      # percent (frozen two-caliber)
W_DD = 252                                 # trailing window (family W252)
JUDGED_CELLS = ("CORE_DD10", "CORE_DD20",
                "SAT40_DD10", "SAT40_DD20")
JUDGED_FACE = CS.JUDGED_FACE               # "x2"
FACES = CS.FACES                           # x1/x2/x3 single source
MAXDD_LINE = CS.MAXDD_LINE                 # -0.35 descriptive
CRASH_YEAR_LINE = CS.CRASH_YEAR_LINE       # -0.30 descriptive
D6_REJECT = CS.D6_REJECT                   # 0.7 (s1 hard line)
FAM_PREV_JSON = os.path.join(ROOT, "results", "cn_core_satellite",
                             "p1_results.json")


def _log(msg):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    print(f"[cn_core_ddctl] {msg}", flush=True)


# ---------------------------------------------------------------- dd axis


def build_dd_axis(P):
    """Core clean_value trailing-252 dd on the FULL union calendar,
    reindexed to the sim timeline (family signal convention: floor
    truncates only the SIM window, never signal history). Single
    sources = SRP loaders (same calls the family loader makes)."""
    closeU, retU = SRP.load_panels()
    events = SRP.fund_events(retU)
    if events.get(CORE):
        raise RuntimeError("core leg event face drifted (prereg s2: "
                           "CORE zero events)")
    cleanU, _ = SRP.clean_rets(retU, events)
    cv_core = SRP.clean_value(closeU, cleanU, CORE)
    dd = cv_core / cv_core.rolling(W_DD, min_periods=W_DD).max() - 1.0
    return dd.reindex(P["days"])


def active_rebals(P):
    """Family face: rebalance grid from first_active onward (>=3
    satellite signals available)."""
    first_idx = next(r for r in P["rebal_days"]
                     if str(P["days"][r].date())
                     == CS.FIRST_ACTIVE_FROZEN)
    return [r for r in P["rebal_days"] if r >= first_idx]


def gate_states(dd_tl, rebals, x):
    """Pure hysteresis state machine (prereg s3.1): OFF->ON when
    dd < -x/100; ON->OFF when dd > -x/200. Returns {r: bool}."""
    st = False
    out = {}
    for r in rebals:
        d = float(dd_tl.iloc[r])
        if not st:
            st = d < -x / 100.0
        else:
            st = not (d > -x / 200.0)
        out[r] = st
    return out


def gate_axis_probe_identity(dd_tl, rebals):
    """s2 fail-closed: derived gate faces must equal the frozen probe
    (transition counts / gated counts / first-ON dates) exactly."""
    probe = json.load(open(PROBE_JSON, encoding="utf-8"))
    faces = {}
    for arm, x in THRESHOLDS.items():
        st = gate_states(dd_tl, rebals, x)
        on_rs = [r for r in rebals if st[r]]
        trans_on = sum(1 for i, r in enumerate(rebals)
                       if st[r] and (i == 0 or not st[rebals[i - 1]]))
        trans_off = sum(1 for i, r in enumerate(rebals)
                        if not st[r] and i > 0 and st[rebals[i - 1]])
        faces[arm] = {
            "on_transitions": trans_on, "off_transitions": trans_off,
            "gated_rebal_count": len(on_rs),
            "active_rebal_count": len(rebals),
            "first_on_date": (str(P_DAYS[on_rs[0]].date()) if on_rs
                              else None),
        }
    return probe, faces


# ---------------------------------------------------------------- targets


def make_core_dd_target(sig, gate):
    """s3.2 CORE_DD cell: OFF -> {core: 1.0}; ON -> {} (all cash,
    de-risk NOT reallocate). Warmup/<3-avail -> None (family face)."""
    def tgt(r):
        avail = [s for s in SAT if np.isfinite(sig[s][r])]
        if len(avail) < CS.MIN_AVAIL:
            return None
        if gate.get(r, False):
            return {}
        return {CORE: 1.0}
    return tgt


def make_sat40_dd_target(sig, gate):
    """s3.2 SAT40_DD cell: satellite argmax law verbatim, NEVER gated;
    core 0.6 when gate OFF, core to cash when ON."""
    def tgt(r):
        avail = [s for s in SAT if np.isfinite(sig[s][r])]
        if len(avail) < CS.MIN_AVAIL:
            return None
        vals = [sig[s][r] for s in avail]
        mx = max(vals)
        winners = [s for s in avail if sig[s][r] == mx]  # strict tie face
        out = {} if gate.get(r, False) else {CORE: 0.6}
        for s in winners:
            out[s] = 0.4 / len(winners)
        return out
    return tgt


def make_null_target(sig, gate, seed):
    """s3.4: one uniform draw among AVAILABLE satellite legs per
    rebalance (rng consumed in schedule order); SAT40 weight structure;
    same-arm core dd gate (held-constant mechanism face)."""
    rng = np.random.default_rng(seed)
    state = {"draws": []}

    def tgt(r):
        avail = [s for s in SAT if np.isfinite(sig[s][r])]
        if len(avail) < CS.MIN_AVAIL:
            return None
        d = avail[int(rng.integers(0, len(avail)))]
        state["draws"].append(d)
        out = {} if gate.get(r, False) else {CORE: 0.6}
        out[d] = 0.4
        return out
    tgt.draws = state["draws"]
    return tgt


# module-level days face for probe-identity date strings (set in run())
P_DAYS = None


# ---------------------------------------------------------------- h4


def h4_family_faces(judged_series, P):
    """s1 H4-style disclosures (never admission): (1) corr vs 510880 leg
    face = CORE ballast leg (constructional); (2) corr vs family
    judged-negative predecessor CN-CORE-SATELLITE-P1 cells -- the
    predecessor artifact DOES carry judged_x2_returns_6dp_audit, so the
    prereg band 0.85-0.98 is verified with real numbers; (3) vs
    DIV_LOWVOL_P1 C1: no series in artifact -> honest unavailable, band
    0.6-0.9 declared."""
    days = P["days"]
    cl = P["legs"][CORE]["close"]
    leg_core = pd.Series(np.append([np.nan],
                                   cl[1:] / cl[:-1] - 1.0), index=days)
    prev = None
    try:
        with open(FAM_PREV_JSON, encoding="utf-8") as fh:
            prev = json.load(fh).get("judged_x2_returns_6dp_audit")
    except Exception:
        prev = None
    out = {}
    for cell, rets in judged_series.items():
        v510, ov = _corr(rets, leg_core)
        row = {
            "corr_vs_510880_core_leg": {
                "corr": v510, "overlap_days": ov,
                "note": "CORE ballast leg face (60%/100%/0% weights by "
                        "construction) = ALLOC P5 slot leg face "
                        "(disclosure only, judgments never cross-wired)"},
        }
        if prev:
            for pc, pr in prev.items():
                v, o2 = _corr(rets, pd.Series(pr,
                                              index=days).dropna())
                row[f"corr_vs_family_prev_{pc}"] = {
                    "corr": v, "overlap_days": o2,
                    "note": "CN-CORE-SATELLITE-P1 judged-negative x2 "
                            "cell (non-member); prereg s1 declared band "
                            "0.85-0.98 constructional (same legs, gate "
                            "modulates weights only)"}
        row["corr_vs_div_lowvol_p1_c1_x2"] = {
            "status": "unavailable_in_artifact",
            "note": "family artifact carries per-face metrics only, no "
                    "return series; prereg s1 declared band 0.6-0.9 "
                    "(same-instrument domain, judged-negative "
                    "non-member)"}
        out[cell] = row
    return out


# ---------------------------------------------------------------- run


def run() -> int:
    global P_DAYS
    t0 = time.time()
    if os.environ.get("CN_CORE_DDCTL_P1_REFINALIZE") != "1" \
            and os.path.exists(OUT_JSON):
        try:
            j = json.load(open(OUT_JSON, encoding="utf-8"))
            if j.get("trials_ledger"):
                print("idempotent fast path: results/cn_core_ddctl/"
                      "p1_results.json already finalized (ledger block "
                      "present); CN_CORE_DDCTL_P1_REFINALIZE=1 = only "
                      "redo")
                return 0
        except Exception:
            pass
    if sg.SEED_REGISTRY.get("cn_core_ddctl_p1") != SEED_BASE:
        print("VOID: seed base cn_core_ddctl_p1 not registered in "
              "science_gates.SEED_REGISTRY (prereg s3.4: registered AT "
              "the R263 freeze commit)")
        return 2

    P = CS.load_panel()
    if not P["gates"]["all_ok"] or not P["gates"]["first_active_ok"]:
        print("VOID: panel gate FAILED:",
              json.dumps(P["gates"], ensure_ascii=False))
        return 2
    P_DAYS = P["days"]
    _log(f"panel gates OK: T={P['gates']['T']} first_active="
         f"{P['gates']['first_active_rebal']} events="
         f"{P['gates']['events']}")

    dd_tl = build_dd_axis(P)
    rebals = active_rebals(P)
    probe, gate_faces = gate_axis_probe_identity(dd_tl, rebals)
    for arm in THRESHOLDS:
        frozen = probe["arms"][arm]
        got = gate_faces[arm]
        drift = [k for k in ("on_transitions", "off_transitions",
                             "gated_rebal_count", "active_rebal_count")
                 if got[k] != frozen[k]]
        if (drift or got["first_on_date"] != frozen["first_on_date"]):
            print(f"VOID: dd-axis probe identity FAILED for {arm}: "
                  f"got={json.dumps(got)} frozen="
                  f"{json.dumps({k: frozen[k] for k in got})}")
            return 2
    GATES = {arm: gate_states(dd_tl, rebals, x)
             for arm, x in THRESHOLDS.items()}
    _log("dd-axis probe identity OK: "
         + json.dumps({a: {k: gate_faces[a][k] for k in
                           ("on_transitions", "off_transitions",
                            "gated_rebal_count")}
                       for a in THRESHOLDS}))

    SIG = P["sig"]
    days, n = P["days"], P["n"]

    def run_unit(target_fn, cost_fn):
        return DRV.simulate(P, target_fn, cost_fn)

    # -- judged cells x3 faces (s3.5: judge = x2, x1/x3 disclosure)
    # struct prefixes compose with the arm suffix into the frozen
    # JUDGED_CELLS ids: CORE_+DD10 = "CORE_DD10" (R263 crash-1 lesson:
    # the composed id MUST equal JUDGED_CELLS members exactly)
    cell_recs = {}
    for struct in ("CORE", "SAT40"):
        for arm in THRESHOLDS:
            cell = f"{struct}_{arm}"
            tf = (make_core_dd_target(SIG, GATES[arm])
                  if struct == "CORE_DD"
                  else make_sat40_dd_target(SIG, GATES[arm]))
            for face, cost_fn in FACES.items():
                cell_recs[(cell, face)] = run_unit(tf, cost_fn)
            m = DRV.metrics(cell_recs[(cell, JUDGED_FACE)])
            _log(f"cell {cell}: {JUDGED_FACE} sharpe={m['sharpe']} "
                 f"ann={m['ann_ret']} maxdd={m['max_dd']} "
                 f"entries={m['n_entries']} fill_max={m['fill_days_max']} "
                 f"superseded={m['n_superseded']}")

    # -- composed-id contract guard (crash-1 root-cause class, fail-closed
    # with a readable message instead of a downstream KeyError)
    built_ids = {c for (c, _f) in cell_recs}
    if built_ids != set(JUDGED_CELLS):
        print(f"VOID: composed cell ids {sorted(built_ids)} != frozen "
              f"JUDGED_CELLS {list(JUDGED_CELLS)} -- refusing verdict")
        return 2

    # -- R240 zero-rebalance-evaluation refusal (warmup still counts)
    for cell in JUDGED_CELLS:
        rec = cell_recs[(cell, JUDGED_FACE)]
        if rec["n_active_rebal"] == 0 and rec["n_warmup_rebal"] == 0:
            print(f"VOID: {cell} zero rebalance evaluations -- signal "
                  "machinery broken, refusing verdict")
            return 2

    # -- K=100 nulls on the judged x2 face (s3.4, two arms x 50)
    null_recs = []
    null_draws_head = None
    for k in range(K_NULLS):
        arm = "DD10" if k < K_PER_ARM else "DD20"
        seed = SEED_BASE + (k if k < K_PER_ARM
                            else K_PER_ARM + (k - K_PER_ARM))
        tf = make_null_target(SIG, GATES[arm], seed)
        rec = run_unit(tf, FACES[JUDGED_FACE])
        null_recs.append(rec)
        if k == 0:
            null_draws_head = list(tf.draws[:12])
    null_vals = [(DRV._sharpe(r["returns"]) or 0.0) for r in null_recs]
    mu, sigma = float(np.mean(null_vals)), float(np.std(null_vals,
                                                        ddof=1))
    null_pool = {
        "values": [round(v, 6) for v in null_vals],
        "coverage": {"n_values": len(null_vals), "mu": mu, "sigma": sigma,
                     "schemas_parsed": ["cn_core_ddctl_p1: 100 "
                                       "random-satellite quarterly "
                                       "sleeves (2 arms x 50: DD10 "
                                       "seeds 20261130+k, DD20 seeds "
                                       "20261180+k, x2 face, SAT40 "
                                       "structure, same-arm core "
                                       "dd-gate, availability-masked)"],
                     "known_unparsed": []},
    }
    _log(f"nulls: K={K_NULLS} mu={mu:.4f} sigma={sigma:.4f}")

    # -- baselines (s3.4 disclosure only, x2 face, activation-anchored)
    def bh_core_target(r):
        avail = [s for s in SAT if np.isfinite(SIG[s][r])]
        if len(avail) < CS.MIN_AVAIL:
            return None
        return {CORE: 1.0}

    def sat40_bare_target(r):
        avail = [s for s in SAT if np.isfinite(SIG[s][r])]
        if len(avail) < CS.MIN_AVAIL:
            return None
        vals = [SIG[s][r] for s in avail]
        mx = max(vals)
        winners = [s for s in avail if SIG[s][r] == mx]
        out = {CORE: 0.6}
        for s in winners:
            out[s] = 0.4 / len(winners)
        return out

    def ew_sat_target(r):
        avail = [s for s in SAT if np.isfinite(SIG[s][r])]
        if len(avail) < CS.MIN_AVAIL:
            return None
        out = {CORE: 0.8}
        for s in avail:
            out[s] = 0.2 / len(avail)
        return out

    bh_core = run_unit(bh_core_target, FACES[JUDGED_FACE])
    sat40_bare = run_unit(sat40_bare_target, FACES[JUDGED_FACE])
    ew_static = run_unit(ew_sat_target, FACES[JUDGED_FACE])

    # -- census gate (r188 law): every unit computed before finalize
    units_expected = (len(JUDGED_CELLS) * len(FACES) + K_NULLS + 3)
    units_have = (len(cell_recs) + len(null_recs) + 3)
    if units_have < units_expected:
        print(f"finalize census gate: {units_have}/{units_expected} units "
              "-- premature finalize refused, no artifact written")
        return 2

    # -- gates (shared library, zero hand-copied lines; prereg s4)
    line = sg.skill_line_v2(batch_cells=BATCH_CELLS, pool="core48",
                            null_pool=null_pool)
    g1, dsr, g2 = {}, {}, {}
    judged_series = {}
    for cell in JUDGED_CELLS:
        rec = cell_recs[(cell, JUDGED_FACE)]
        rets = rec["returns"].iloc[1:]        # drop NaN head interval
        judged_series[cell] = rets
        g1[cell] = sg.g1_prime_v2(
            sharpe_full=DRV._sharpe(rets), returns=rets,
            batch_cells=BATCH_CELLS, pool="core48", null_pool=null_pool,
            n_trades=rec["n_trades"], n_entries=rec["n_entries"])
        dsr[cell] = sg.deflated_sharpe_ratio(
            rets, n_trials=line["n_eff"], var_null_sr=sigma ** 2)
    fam_pbo = cscv_pbo(align_returns(judged_series))
    for cell in JUDGED_CELLS:
        g2[cell] = sg.g2_registration_v2(
            g1_pass=bool(g1[cell]["pass_v2"]), dsr=dsr[cell],
            pbo=fam_pbo["pbo"])

    g1_errs = {c: v.get("error") for c, v in g1.items()
               if isinstance(v, dict) and "error" in v}
    if g1_errs:
        first = next(iter(g1_errs.items()))
        print(f"finalize FAIL-CLOSED: g1 errored for {len(g1_errs)}/"
              f"{len(g1)} cells (first: {first[0]} -> "
              f"{str(first[1])[:120]}) -- no artifact written")
        return 2

    # -- D6 (registered members reject face + same-batch disclosure)
    try:
        member_rets, member_cutoffs = load_member_rets()
        d6 = {c: d6_block(judged_series[c], member_rets)
              for c in JUDGED_CELLS}
        d6["member_cutoffs"] = member_cutoffs
    except Exception as exc:
        d6 = {"status": "pending_error", "error": repr(exc)[:200]}
    same_batch = {}
    for a in JUDGED_CELLS:
        row = {}
        for b in JUDGED_CELLS:
            if a == b:
                continue
            v, ov = _corr(judged_series[a], judged_series[b])
            row[b] = {"corr": v, "overlap_days": ov}
        same_batch[a] = row
    h4 = h4_family_faces(judged_series, P)

    # -- descriptive clauses + x1/x3 stability (s4)
    descriptive = {}
    for cell in JUDGED_CELLS:
        xm = DRV.metrics(cell_recs[(cell, JUDGED_FACE)])
        yr2 = xm["yearly"]
        stable = {}
        for face in ("x1", "x3"):
            yf = DRV.metrics(cell_recs[(cell, face)])["yearly"]
            common = [y for y in yr2 if y in yf]
            stable[face] = {
                "sign_match_years": int(sum(
                    1 for y in common if (yr2[y] > 0) == (yf[y] > 0))),
                "n_common_years": len(common),
            }
        xm["cost_stability"] = stable
        descriptive[cell] = {
            "full_ann_positive": bool((xm["ann_ret"] or 0) > 0),
            "oos_dual_positive": bool(
                (xm["oos"]["sharpe"] or 0) > 0
                and (xm["oos"]["ann_ret"] or 0) > 0),
            "max_dd_line_pass": bool((xm["max_dd"] or 0) >= MAXDD_LINE),
            "no_crash_year": bool(all(
                v > CRASH_YEAR_LINE for v in yr2.values())),
            "crash_year_line": CRASH_YEAR_LINE,
            "x1_x3_yearly_stability": stable,
        }

    # -- regime descriptive column + gate-occupancy axis (never a switch)
    reg_col = regime_v3_column(days)
    gate_axis = {}
    for arm in THRESHOLDS:
        st = GATES[arm]
        per_year = {}
        for r in rebals:
            y = int(days[r].year)
            per_year.setdefault(y, {"active": 0, "gated": 0})
            per_year[y]["active"] += 1
            if st[r]:
                per_year[y]["gated"] += 1
        gate_axis[arm] = {"occupancy_per_year": per_year,
                          "probe_faces": gate_faces[arm]}
    sat_picks = {}
    for cell in JUDGED_CELLS:
        if not cell.startswith("SAT40_DD"):
            continue
        arm = cell.split("_")[-1]
        tf = make_sat40_dd_target(SIG, GATES[arm])
        leg_counts = {s: 0 for s in SAT}
        for r in P["rebal_days"]:
            tgt = tf(r)
            if not tgt:
                continue
            for s in tgt:
                if s != CORE:
                    leg_counts[s] += 1
        sat_picks[cell] = leg_counts

    # -- cells block (judged face carries per-transition fill rows)
    cells_out = {}
    for cell in JUDGED_CELLS:
        per_face = {}
        for face in FACES:
            mrec = DRV.metrics(cell_recs[(cell, face)])
            if face == JUDGED_FACE:
                mrec["cost_stability"] = descriptive[cell][
                    "x1_x3_yearly_stability"]
                mrec["transitions"] = DRV._compact_transitions(
                    cell_recs[(cell, face)])
            per_face[face] = mrec
        cells_out[cell] = per_face
    judged_returns_audit = {
        cell: [round(float(v), 6) for v in judged_series[cell].tolist()]
        for cell in JUDGED_CELLS}

    nulls_out = {
        "config": {"base": SEED_BASE, "registered": "cn_core_ddctl_p1",
                   "draws": K_NULLS, "face": f"{JUDGED_FACE}_judged",
                   "rule": "one uniform draw among AVAILABLE satellite "
                           "legs per rebalance (rng per sleeve, schedule "
                           "order); SAT40 weight structure; same-arm "
                           "core dd-gate (held-constant mechanism); "
                           "same availability/warmup face (prereg "
                           "s3.4; CORE_DD cells judged vs "
                           "satellite-bearing nulls = conservative "
                           "face note)",
                   "null0_draws_head": null_draws_head},
        "n_values": len(null_vals),
        "values_rounded": null_pool["values"],
        "coverage": null_pool["coverage"],
    }
    baselines_out = {
        "core_only_buy_hold_510880": DRV.metrics(bh_core),
        "sat40_bare_ungated_composite": DRV.metrics(sat40_bare),
        "static_8020_core_ew_satellite": DRV.metrics(ew_static),
        "note": "activation-anchored passive faces (disclosure only); "
                "sat40_bare = family strongest judged-negative cell "
                "re-derived in-batch = the dd-gate increment yardstick "
                "(prereg s3.4/s5.4); skill-line passive anchor = "
                "core48 pool via the shared library (s4)",
    }

    led = sg.append_ledger(
        "CN-CORE-DDCTL-P1", LEDGER_TRIALS,
        file_name="results/cn_core_ddctl/p1_results.json",
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="4 judged cells {CORE_DD,SAT40_DD}x{DD10,DD20} core=510880 "
             "ballast with OWN trailing-252 drawdown hysteresis gate "
             "(ON dd<-X%, OFF dd>-X/2, quarterly family grid, state "
             "carried, R261 doctrine residual 'dd-control sits on the "
             "CORE leg'); satellite=7-leg style-momentum argmax law "
             "NEVER gated (family s5.3 MISS) + K=100 two-arm "
             "random-satellite nulls with same-arm gate (seeds "
             "20261130/20261180 +i, registered cn_core_ddctl_p1 at "
             "the R263 freeze commit); V2 ADV20-tiered cost, judge face "
             "x2, 1%ADV queue-fill, clean_value bridge face; prereg "
             "research/CN_CORE_DDCTL_PREREG.md frozen R263; "
             "T-2026-09-26-73 s3 slice-6 (doctrine residual, no-reopen "
             "law respected)")

    att = json.load(open(ATT_JSON, encoding="utf-8"))
    d6_rejects = ({c: ((d6.get(c) or {}).get("member_face", {})
                       .get("reject")) for c in JUDGED_CELLS}
                  if d6.get("status") != "pending_error" else None)
    att["entries"].append({
        "batch": "CN-CORE-DDCTL-P1",
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "measurement",
        "cells_ledger_delta": LEDGER_TRIALS,
        "ledger_total_after": led["total"],
        "gates": {
            "panel_pass": True,
            "g1_prime_pass": {c: bool(g1[c]["pass_v2"])
                              for c in JUDGED_CELLS},
            "g2_eligible": {c: bool(g2[c]["eligible_v2"])
                            for c in JUDGED_CELLS},
            "d6_reject": d6_rejects,
        },
        "eliminated": LEDGER_TRIALS - sum(
            1 for c in JUDGED_CELLS if g2[c]["eligible_v2"]),
        "refs": {"prereg": "research/CN_CORE_DDCTL_PREREG.md",
                 "ticket": TICKET},
    })

    import hashlib
    prereg_sha = hashlib.sha256(
        open(PREREG, "rb").read().replace(b"\r\n", b"\n")).hexdigest()

    payload = {
        **sg.cutoff_meta(EVIDENCE_CUTOFF),
        "meta": {
            "batch": "CN-CORE-DDCTL-P1", "ticket": TICKET,
            "prereg": "research/CN_CORE_DDCTL_PREREG.md",
            "prereg_sha256_lf_normalized": prereg_sha,
            "judge_face": f"{JUDGED_FACE} (whole-V2 doubled, side_cost_x2 "
                          "family precedent, always on); x1/x3 disclosure "
                          "tracks",
            "seed_base_registered": "cn_core_ddctl_p1=20261130",
            "cost_basis": "V2 ADV20-tiered (knowledge/rules.py CostPatch "
                          "single source) + 1% ADV participation cap with "
                          "DAY-QUEUED fills (fill_days counters per "
                          "transition; missing-bar days = no fill, NaN "
                          "ADV conservative zero cap)",
            "accounting": "signal close r -> fills from open r+1 (T+1); "
                          "quarterly 63d grid anchor 62; daily close "
                          "valuation; cash zero-yield; warmup = "
                          "cash-honest; MIN_AVAIL=3 (family); tie -> "
                          "satellite weight split; core dd-gate NEVER "
                          "touches the satellite; re-anchor supersedes "
                          "incomplete transitions",
            "panel": "8-leg union timeline T=3333 (2013-01-04..2026-09-22) "
                     "family-verbatim; signal = rolling-252 on FULL union "
                     "calendar; sim prices = clean_value bridge face; "
                     "ADV20 = raw volume x close CNY; frozen event set 3, "
                     "CORE zero events; dd axis = core clean_value "
                     "trailing-252 max on FULL history, probe-identity "
                     "fail-closed (results/core_ddctl_probe.json)",
            "machinery_reuse": "CS=cn_core_sat_p1 panel/gates/schedule "
                               "(frozen batch single source); DRV="
                               "cn_div_lowvol_rot_p1 engine (LEGS=8 "
                               "injection via CS import); SRP slice-E "
                               "loaders/event guard; science_gates shared "
                               "criteria; crisis windows = family "
                               "five-window set",
            "machine": CS._machine_id(),
        },
        "panel_gates": P["gates"],
        "events_detail": P["events_detail"],
        "cells": cells_out,
        "nulls": nulls_out,
        "baselines": baselines_out,
        "skill_line": line,
        "g1_prime_v2": g1,
        "g2_registration_v2": g2,
        "family_pbo": {k: fam_pbo[k] for k in
                       ("pbo", "n_blocks", "n_trials", "n_rows",
                        "n_combinations") if k in fam_pbo},
        "dsr": dsr,
        "d6_correlation": d6,
        "same_batch_corr": same_batch,
        "h4_disclosure_faces": h4,
        "descriptive": descriptive,
        "regime_columns": {
            "market_v3_axis": reg_col,
            "gate_occupancy_axis": gate_axis,
            "satellite_picks": sat_picks,
        },
        "judged_x2_returns_6dp_audit": judged_returns_audit,
        "n_trials": LEDGER_TRIALS,
        "audit": {
            "elapsed_sec": round(time.time() - t0, 1),
            "workers": 1,
            "units_expected": units_expected,
            "units_computed": units_have,
            "blind_run_flags": {
                "deterministic_sim": "no wall-clock inside sim outputs; "
                                     "gate states precomputed by pure "
                                     "function (no closure mutation); "
                                     "double-run identity via selftest",
                "queue_rule_frozen": "sells before buys; caps from "
                                     "ADV20(t-1); buys lot-rounded; NaN "
                                     "ADV/missing-bar days = no fill",
            },
        },
        "trials_ledger": led,
    }
    json.loads(json.dumps(payload, default=str))     # validate before write
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = OUT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, OUT_JSON)
    tmp = ATT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(att, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, ATT_JSON)
    _write_csv(cells_out, g1, g2, d6)
    _log(f"finalize: ledger total={led['total']} | g1="
         f"{ {c: g1[c]['pass_v2'] for c in JUDGED_CELLS} } g2="
         f"{ {c: g2[c]['eligible_v2'] for c in JUDGED_CELLS} } | "
         f"elapsed={round(time.time() - t0, 1)}s")
    print(f"[cn_core_ddctl] written {OUT_JSON}; g1="
          f"{ {c: g1[c]['pass_v2'] for c in JUDGED_CELLS} }")
    return 0


def _write_csv(cells_out, g1, g2, d6):
    import csv as _csv
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(["cell", "face", "sharpe", "ann_ret", "max_dd",
                    "oos_sharpe", "oos_ann", "n_entries", "n_trades",
                    "n_active_rebal", "fill_days_max", "n_superseded",
                    "traded_notional", "cost_total", "g1_pass",
                    "g2_eligible", "d6_max_abs_corr"])
        for cell, per_face in cells_out.items():
            for face, m in per_face.items():
                mf = ((d6.get(cell) or {}).get("member_face", {})
                      if face == JUDGED_FACE else {})
                w.writerow([cell, face, m["sharpe"], m["ann_ret"],
                            m["max_dd"], m["oos"]["sharpe"],
                            m["oos"]["ann_ret"], m["n_entries"],
                            m["n_trades"], m["n_active_rebal"],
                            m["fill_days_max"], m["n_superseded"],
                            m["traded_notional_total"], m["cost_total"],
                            g1[cell]["pass_v2"] if face == JUDGED_FACE
                            else "",
                            g2[cell]["eligible_v2"]
                            if face == JUDGED_FACE else "",
                            mf.get("max_abs_corr", "")])


# ---------------------------------------------------------------- selftest


def selftest() -> int:
    fails = []

    def ok(fid, cond, detail=""):
        print(f"  [{'PASS' if cond else 'FAIL'}] {fid} {detail}")
        if not cond:
            fails.append(fid)

    # [C1] frozen constants (prereg numbers, drift guard)
    ok("[C1] frozen constants", all([
        SEED_BASE == 20_261_130
        and sg.SEED_REGISTRY.get("cn_core_ddctl_p1") == SEED_BASE,
        K_NULLS == 100 and K_PER_ARM == 50 and BATCH_CELLS == 4
        and LEDGER_TRIALS == 104,
        THRESHOLDS == {"DD10": 10, "DD20": 20} and W_DD == 252,
        JUDGED_CELLS == ("CORE_DD10", "CORE_DD20",
                         "SAT40_DD10", "SAT40_DD20"),
        JUDGED_FACE == "x2" and set(FACES) == {"x1", "x2", "x3"},
        EVIDENCE_CUTOFF == "2026-09-22" and OOS_START == "2025-01-01",
        CORE == "510880" and len(SAT) == 7,
        D6_REJECT == 0.7 and MAXDD_LINE == -0.35
        and CRASH_YEAR_LINE == -0.30,
        CS.T_FROZEN == 3333 and CS.FIRST_ACTIVE_FROZEN == "2013-07-17"
        and CS.MIN_AVAIL == 3 and CS.REBAL_STEP == 63,
    ]))

    # [C2] dd math: known synthetic drawdowns, exact window semantics
    s = pd.Series([100.0, 120.0, 90.0, 99.0, 108.0, 108.0])
    rm = s.rolling(3, min_periods=3).max()
    dd = s / rm - 1.0
    ok("[C2] dd math", all([
        np.isnan(dd.iloc[1]),
        abs(dd.iloc[2] - (90.0 / 120.0 - 1.0)) < 1e-12,
        abs(dd.iloc[3] - (99.0 / 120.0 - 1.0)) < 1e-12,
        abs(dd.iloc[4]) < 1e-12 and abs(dd.iloc[5]) < 1e-12,
    ]), f"dd={list(dd.round(4))}")

    # [C3] hysteresis state machine (pure function): ON at <-10%, stays
    # ON through (-10%,-5%], OFF only when dd > -5% (half-threshold)
    seq = [-0.05, -0.12, -0.11, -0.049, -0.05, -0.0501, -0.13, -0.06]
    days8 = pd.bdate_range("2020-01-01", periods=len(seq))
    dd8 = pd.Series(seq, index=days8)
    reb8 = list(range(len(seq)))
    st8 = gate_states(dd8, reb8, 10)
    ok("[C3] hysteresis machine", [st8[r] for r in reb8]
       == [False, True, True, False, False, False, True, True],
       f"states={[st8[r] for r in reb8]}")

    # [C4] target faces: warmup/<3-avail None; CORE_DD ON={} OFF={core};
    #      SAT40_DD ON={sat:.4} OFF={core:.6+sat:.4}; strict tie split
    sig = {"510050": np.array([0.10, 0.10, 0.10, np.nan]),
           "510300": np.array([0.05, 0.05, 0.05, 0.05]),
           "512100": np.array([0.01, 0.10, 0.01, np.nan]),
           "510500": np.full(4, np.nan), "159915": np.full(4, np.nan),
           "588000": np.full(4, np.nan), "563300": np.full(4, np.nan)}
    gon = {0: True, 1: True, 2: False}
    t_core = make_core_dd_target(sig, gon)
    t_sat = make_sat40_dd_target(sig, gon)
    ok("[C4a] CORE_DD faces", t_core(0) == {} and t_core(2) == {CORE: 1.0}
       and t_core(3) is None)
    ok("[C4b] SAT40_DD faces", t_sat(0) == {"510050": 0.4}
       and t_sat(1) == {"510050": 0.2, "512100": 0.2}
       and t_sat(2) == {CORE: 0.6, "510050": 0.4} and t_sat(3) is None,
       f"on={t_sat(0)} tie={t_sat(1)} off={t_sat(2)}")
    ok("[C4c] gate OFF default for unknown r",
       make_core_dd_target(sig, {})(0) == {CORE: 1.0})

    # [C5] null determinism + gate carried in nulls (same seed = same
    # draws; gate ON null has NO core key)
    tn1 = make_null_target(sig, gon, SEED_BASE)
    tn2 = make_null_target(sig, gon, SEED_BASE + 1)
    d1 = [tn1(r) for r in (0, 1, 2)]
    tn1b = make_null_target(sig, gon, SEED_BASE)
    _ = [tn1b(r) for r in (0, 1, 2)]
    ok("[C5a] null determinism", tn1.draws == tn1b.draws
       and len(d1) == 3 and all(d1[0].get(CORE) is None
                                for _ in [0]) and CORE in d1[2])
    ok("[C5b] null seed face", tn2.draws != tn1.draws)

    # [M2] engine on the family hermetic panel: SAT40_DD gate-OFF
    # anchor + T+1 + double-run identity (CS fixtures single source)
    P0 = CS._hermetic_panel()
    sig0 = {s: np.full(P0["n"], np.nan) for s in SAT}
    MA_gate_free = {s: np.zeros(P0["n"]) for s in SAT}
    for r in P0["rebal_days"]:
        sig0["510050"][r] = 0.10
        sig0["510300"][r] = 0.05
        sig0["512100"][r] = 0.01
    tf = make_sat40_dd_target(sig0, {})
    rec = DRV.simulate(P0, tf, FACES["x2"])
    tr = [t for t in rec["transitions"]
          if t["anchor_r"] == P0["rebal_days"][0]][0]
    ok("[M2a] T+1 exec", tr["first_exec"] == P0["rebal_days"][0] + 1)
    ok("[M2b] 60/40 target anchored",
       tr["target"] == {CORE: 0.6, "510050": 0.4}
       and abs(tr["entry_notional"] - 1_000_000.0) < 5_000,
       f"target={tr['target']}")
    rec2 = DRV.simulate(P0, make_sat40_dd_target(sig0, {}), FACES["x2"])
    ok("[M2c] double-run identity",
       np.array_equal(np.asarray(rec["returns"]),
                      np.asarray(rec2["returns"]), equal_nan=True))

    # [M2d] gate-ON face on the engine: core sold to cash, satellite
    # leg stays (target carries NO core key)
    gon2 = {r: True for r in P0["rebal_days"]}
    recg = DRV.simulate(P0, make_sat40_dd_target(sig0, gon2),
                        FACES["x2"])
    trg = [t for t in recg["transitions"]
           if t["anchor_r"] == P0["rebal_days"][0]][0]
    ok("[M2d] gate-ON target = satellite-only",
       trg["target"] == {"510050": 0.4}
       and bool(np.isfinite(
           np.asarray(recg["returns"])[~np.isnan(
               np.asarray(recg["returns"]))]).all()))

    # [M9] REAL-corpus dd-axis probe identity (fail-closed face): the
    # derived gate faces must equal the frozen probe exactly
    P = CS.load_panel()
    g = P["gates"]
    ok("[M9a] real panel gates", bool(g["all_ok"] and g["first_active_ok"]),
       f"T={g['T']} first_active={g['first_active_rebal']}")
    global P_DAYS
    P_DAYS = P["days"]
    dd_tl = build_dd_axis(P)
    rebals = active_rebals(P)
    probe, faces = gate_axis_probe_identity(dd_tl, rebals)
    ok("[M9b] probe identity DD10",
       faces["DD10"]["on_transitions"] == 6
       and faces["DD10"]["off_transitions"] == 5
       and faces["DD10"]["gated_rebal_count"] == 34
       and faces["DD10"]["active_rebal_count"] == 51
       and faces["DD10"]["first_on_date"] == "2013-07-17",
       f"got={faces['DD10']}")
    ok("[M9c] probe identity DD20",
       faces["DD20"]["on_transitions"] == 4
       and faces["DD20"]["off_transitions"] == 4
       and faces["DD20"]["gated_rebal_count"] == 10
       and faces["DD20"]["first_on_date"] == "2014-01-21",
       f"got={faces['DD20']}")

    # [M10] gate state determinism: recompute = same states (pure fn)
    st_a = gate_states(dd_tl, rebals, 10)
    st_b = gate_states(dd_tl, rebals, 10)
    ok("[M10] gate recompute identity", st_a == st_b
       and sum(1 for v in st_a.values() if v) == 34)

    print(f"cn_core_ddctl_p1 selftest: 13-leg battery, {len(fails)} FAIL")
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
