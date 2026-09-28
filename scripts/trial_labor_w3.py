# -*- coding: utf-8 -*-
"""TRIAL_LABOR_W3 runner -- T-97 mass-candidate trial wave-3 (5000-deep,
regime-gate deepening wave).

Prereg FROZEN (r391): research/TRIAL_LABOR_W3_PREREG.md -- generate
grammar + funnel rules + judgment lines all frozen; post-run only
sec.7/8 backfill.

Import-face law (prereg sec.6): enumeration/loading/anchor/envelope
primitives are IMPORTED from trial_labor_w1 (tl1); the initial-stop
overlay layer is IMPORTED from trial_labor_w2 (tl2); the Sobol
sample_draws pattern follows mass_trial_w1 (paradigm import); strategies/
factory + engine/backtester imported, never rewritten; engine/
exit_rules.py ZERO touch (gate overlay AND stop overlay are GRAMMAR
layers).

Engineering mapping disclosures (pre-run, zero cells burned):

  GATE overlay (prereg sec.3 face a; E1-mapping grammar-layer primitive):
  GATE state = signal-day-d close of member 510300 vs MA200 (rolling 200,
  min_periods=200); bull permits entry when close>=MA200, bear when
  close<MA200; gate-closed signal day -> effective signal zeroed (entry
  blocked; the engine-native signal-off exit semantics are the SAME
  primitive every template/cell uses when its own signal turns off -- no
  exit-rule change).  MA200 NaN window (first 199 bars) -> gate-closed
  on BOTH faces (conservative, disclosed per-cell via the panel-level
  na-window count).  gate=none = W1/W2 semantic baseline (identity).
  Composition order frozen everywhere (generate dedup face + engine
  face): signal -> filter -> timing -> GATE -> initial-stop.

  MASS survivor exclusion translation (declared conservative, exact-key
  law only): a MASS screen-survivor cell is translatable to the W3 cell
  key ONLY when axes are R=none (MASS R=bull/bear gate uses the csi300
  INDEX close vs MA200 -- a different series from the W3 GATE spec 510300
  ETF close; and prereg sec.1 rules gate faces legal-new cells), X=own
  (family-native exit == tl1 B-family template_default engine-default
  exit), S=full (no scale == equal_weight), T=daily (== daily_signal
  no-op).  X=t* (rising-edge entry semantics) and S=delever (0.5x bear
  scale on the csi300 bench) are machinery-different faces -> not
  translatable, counted + disclosed, never excluded.

Slice plan (W2 r358/r359 precedent; slice-1 + generate land this commit):
  - slice-1: build_grammar_w3 (tl1 grammar extended with the initial-stop
    axis [imported from tl2] + the regime-gate axis -> 10752 axis combos,
    new grammar sha16 != W1 a2fa15f4b06b3c40 != MASS 96269ebe766c3fc2 !=
    W2 1dd3d95792395cec) + gate overlay layer + selftest (hermetic:
    gate causality / NaN-window / gate=none parity legs) + grammar
    serialization;
  - slice-1b (same commit): generate (Sobol six-tuple draws + six-source
    exclusion with the declared MASS translation + effective-face dedup +
    ledger row + D6 disclosure column);
  - NEXT slices (physical dep: generate product; separate commits with
    MSG declarations per W2 r360/r362 precedent): screen (prep gates +
    K=200 nulls + survival line) / judge (dual-leg + dual nulls on seed
    20288500) / intake.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trial_labor_w1 as tl1  # import-face reuse law (prereg sec.6)
import trial_labor_w2 as tl2  # initial-stop overlay layer import law
from science_gates import SEED_REGISTRY  # noqa: E402

# ------------------------------------------------------------ frozen (prereg)
WAVE = "TRIAL_LABOR_W3"
PREREG = "research/TRIAL_LABOR_W3_PREREG.md"
CUTOFF = tl1.CUTOFF                      # "2026-09-22" (P-5C binding, sec.2)
SEED_GEN = SEED_REGISTRY["trial_labor_w3_gen"]        # 20287500
SEED_NULL = SEED_REGISTRY["trial_labor_w3_scrnull"]   # 20288000
SEED_UNC = SEED_REGISTRY["trial_labor_w3_unc"]        # 20288500
N_A = 500          # family A raw draws (sec.3: 6 templates round-robin)
N_B = 4500         # family B raw draws (72-fn machinery round-robin)
K_NULLS = 200       # screen null family size (sec.3; burned by the
                   # NEXT-slice screen subcommand, frozen here)
RES_DIR = os.path.join(tl1.PATHS.results_dir, "trial_labor_w3")
GRAMMAR_FILE = os.path.join(RES_DIR, "w3_grammar.json")
CANDIDATES_FILE = os.path.join(RES_DIR, "w3_candidates.json")
GRAMMAR_LEDGER = tl1.GRAMMAR_LEDGER
FROZEN_SHA16 = "cc59eab79db53436"   # slice-1 serialized face (r392)
PREP_FILE = os.path.join(RES_DIR, "prep_state.json")
SCREEN_FILE = os.path.join(RES_DIR, "w3_screen.json")
SCREEN_CSV = os.path.join(RES_DIR, "w3_screen_cells.csv")
JUDGE_STATE_FILE = os.path.join(RES_DIR, "judge_state.json")
JUDGE_FILE = os.path.join(RES_DIR, "w3_judge.json")
CKPT_DIR = os.path.join(RES_DIR, "checkpoint")
SCREEN_BATCH = "TRIAL_LAB_W3_SCREEN"   # prereg sec.3 ledger literal
JUDGE_BATCH = "TRIAL_LAB_W3_JUDGE"     # prereg sec.3 ledger literal
W6M = tl1.WINDOWS["6m"]                # leg-L 6m screen window (126 td)

# initial-stop axis: imported from tl2 (frozen levels, zero re-declare)
AXIS_STOP = tl2.AXIS_STOP
STOP_FORMULA = tl2.STOP_FORMULA
STOP_FILL_MAPPING = tl2.STOP_FILL_MAPPING

# regime entry-gate axis (prereg sec.3 expansion face a; frozen definition)
AXIS_GATE = ["none", "bull", "bear"]
AXIS_COMBOS = (len(tl1.AXIS_FILTERS) * len(tl1.AXIS_EXITS)
               * len(tl1.AXIS_SIZING) * len(tl1.AXIS_TIMING)
               * len(AXIS_STOP) * len(AXIS_GATE))
GATE_MEMBER = "510300"          # core48 member (prereg sec.2 probe fact)
GATE_SPEC = {
    "member": GATE_MEMBER,
    "ma_window": 200, "min_periods": 200,
    "bull": "close(d) >= MA200(d) permits entry (bull-participation face)",
    "bear": "close(d) < MA200(d) permits entry (bear-participation face)",
    "none": "no gate (W1/W2 semantic baseline face)",
    "info_set": "signal-day d close; entry fills d+1 open (T+1 causal, "
                "same info set as the signal, zero lookahead)",
    "nan_window": "first 199 bars MA200=NaN -> gate-closed on BOTH "
                  "bull/bear faces (conservative; panel-level na-window "
                  "count disclosed)",
    "overlay": "gate-closed signal day -> effective signal zeroed "
               "(grammar layer, MSG-0440 E1-mapping primitive; engine/"
               "exit_rules.py ZERO touch; engine-native signal-off exit "
               "semantics shared by every template/cell)",
    "composition_order": "signal -> filter -> timing -> GATE -> "
                         "initial-stop (frozen identically on the dedup "
                         "face and the engine face)",
}

MASS_SCREEN_CKPT = os.path.join("results", "mass_trial",
                                "screen_checkpoint.jsonl")
MASS_JUDGE_FILE = os.path.join("results", "mass_trial", "w1_judge.json")
W1_JUDGE_FILE = os.path.join(tl1.RES_DIR, "w1_judge.json")
W2_JUDGE_FILE = os.path.join(tl2.RES_DIR, "w2_judge.json")

MASS_TRANSLATION_NOTE = (
    "declared conservative exact-key translation: translatable iff "
    "R=none AND X=own AND S=full AND T=daily -> axis [none, "
    "template_default, equal_weight, daily_signal, none, none]; "
    "R=bull/bear = gate-series-different (csi300 INDEX close vs W3 GATE "
    "510300 ETF close) + prereg sec.1 gate-face legal-new clause; "
    "X=t* rising-edge entry semantics and S=delever 0.5x-bear-scale "
    "= machinery-different faces; non-translatable rows counted + "
    "disclosed, never excluded")


# ------------------------------------------------------------ grammar (slice-1)
def _grammar_sha16(grammar: dict) -> str:
    canon = json.dumps(
        {k: grammar[k] for k in sorted(grammar) if k != "grammar_sha256"},
        sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def build_grammar_w3():
    """tl1 grammar extended with the stop axis (tl2 import) + the regime
    gate axis + W3 seeds/counts (frozen face).

    Exclusion law (prereg sec.1): exact already-judged cells are excluded
    on the gate=none face; all W1-lineage judged cells are implicitly
    initial_stop=none AND gate=none; W2 survivor cells carry their own
    explicit stop face + implicit gate=none; MASS cells enter only via
    the declared conservative translation (see MASS_TRANSLATION_NOTE);
    gate=bull/bear faces = new-syntax legal cells (never excluded).
    """
    g = tl1.build_grammar()          # frozen W1 machinery: inventory+domains
    excl = []
    for band in ("registered_default_axis", "negative_default_axis"):
        for e in g["exclusion"][band]:
            excl.append({**e, "axis": list(e["axis"]) + ["none", "none"],
                         "face": f"{band}:stop-gate-none"})
    grammar = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        "grammar_kind": "w3-regime-gate-extended",
        "seeds": {"trial_labor_w3_gen": SEED_GEN,
                  "trial_labor_w3_scrnull": SEED_NULL,
                  "trial_labor_w3_unc": SEED_UNC,
                  "derivation": "Sobol(seed=20287500+family_idx, scramble) "
                                "param box + default_rng([20287500+family_idx,"
                                " 7919]) six-tuple axis stream "
                                "R/X/S/T/STOP/GATE (prereg s.3)"},
        "n_draws": {"A": N_A, "B": N_B}, "k_nulls": K_NULLS,
        "axes": {"filters": tl1.AXIS_FILTERS, "exits": tl1.AXIS_EXITS,
                 "sizing": tl1.AXIS_SIZING, "timing": tl1.AXIS_TIMING,
                 "initial_stop": AXIS_STOP, "gate": AXIS_GATE},
        "axis_combos": AXIS_COMBOS,
        "stop_formula": STOP_FORMULA,
        "stop_fill_mapping": STOP_FILL_MAPPING,
        "gate_spec": GATE_SPEC,
        "families": g["families"], "value_domains": g["value_domains"],
        "faces": g["faces"],
        "exclusion": {"stop_gate_none_face": excl,
                      "sources": list(g["exclusion"]["sources"])
                      + ["w1_screen.json survivors (generate-time)",
                         "w2_screen.json survivors (generate-time)",
                         "MASS screen survivors (generate-time, declared "
                         "translation)",
                         "w1_judge / MASS judged / w2_judge products "
                         "(generate-time real-read re-declare window)"],
                      "note": "exclusion face = gate=none only; cells with "
                              "explicit stop faces (W2 survivors) carry "
                              "their own stop value; gate=bull/bear = "
                              "new-syntax legal cells (prereg sec.1)"},
        "negative_priors": g.get("negative_priors"),
        "inventory_audit": {
            "non_grid_fns": len(g["value_domains"]),
            "a_templates": len(g["families"]["A"]),
            "a_unique_module_fn_keys": len(
                {(t["module"], t["fn"]) for t in g["families"]["A"]}),
            "b_fns": len(g["families"]["B"]),
            "modules_on_disk": 13,
            "grid_own_fns_excluded": 4,
            "count_note": "prereg prose 86-fn/B-76 count not reproducible "
                          "by any standard probe (all-visible=own=81 total); "
                          "W1-lineage inventory convention = frozen "
                          "generation face (B=72 machinery actual); W2 "
                          "MSG-0440 disclosure carries over verbatim",
        },
    }
    grammar["grammar_sha256"] = _grammar_sha16(grammar)
    return grammar


# ------------------------------------------------------ gate overlay layer
def gate_state_series(prices: dict):
    """Frozen GATE spec (prereg sec.2/3): member 510300 close vs MA200
    (rolling 200, min_periods=200) on the signal-day info set.

    Returns (bull_perm, bear_perm, meta): boolean Series on the member's
    own date index + panel-level flip counts.  MA200 NaN window -> BOTH
    faces gate-closed (conservative).  Deterministic pure function of the
    (cutoff-truncated) panel."""
    close = prices[GATE_MEMBER]["close"].sort_index()
    ma200 = close.rolling(GATE_SPEC["ma_window"],
                          min_periods=GATE_SPEC["min_periods"]).mean()
    bull = (close >= ma200)            # NaN comparisons are False already
    bear = (close < ma200) & ma200.notna()
    fb = int((bull.values[1:] != bull.values[:-1]).sum())
    fe = int((bear.values[1:] != bear.values[:-1]).sum())
    meta = {"na_window_bars": int(ma200.isna().sum()),
            "flips_bull_face": fb, "flips_bear_face": fe,
            "first_valid": (str(ma200.dropna().index[0].date())
                            if ma200.notna().any() else None)}
    return bull, bear, meta


def gate_zero_mask(mask: pd.DataFrame, gate_key: str, gate_state):
    """Grammar-layer regime entry gate (prereg sec.3 face a; E1-mapping
    primitive): gate-closed signal days -> effective signal zeroed
    (entry blocked; engine-native signal-off exit semantics -- the same
    primitive every cell uses when its own signal turns off; zero engine
    touch).  gate=none = W1/W2 semantic baseline (identity).  Member
    dates missing from the mask index -> gate-closed (conservative
    reindex law)."""
    if gate_key == "none":
        return mask
    bull, bear, _ = gate_state
    perm = bull if gate_key == "bull" else bear
    keep = perm.reindex(mask.index).fillna(False).astype(int)
    return mask.mul(keep, axis=0)


# ------------------------------------------------------------ Sobol draw leg
def draw_candidate_sobol_w3(grammar, family, slot, n_draws):
    """Yield (draw_idx, cand) for one family slot per prereg sec.3:
    Sobol over the normalized param box (seed=SEED_GEN+family_idx) mapped
    to discrete domain indices + six-tuple axis stream
    default_rng([SEED_GEN+family_idx, 7919]) in the frozen consumption
    order R/X/S/T/STOP/GATE.  Deterministic, zero band use."""
    from scipy.stats import qmc
    fam_idx = slot if family == "A" else 6 + slot   # A 0-5, B 6-77 (prereg)
    spec = grammar["families"][family][slot]
    mk = f"{spec['module']}.{spec['fn']}"
    dom = grammar["value_domains"][mk]
    names = sorted(nm for nm, vs in dom.items() if len(vs) > 1)
    sob = qmc.Sobol(max(1, len(names)), scramble=True,
                    seed=SEED_GEN + fam_idx)
    box = sob.random(n_draws)
    rng = np.random.default_rng([SEED_GEN + fam_idx, 7919])
    ax = list(zip(rng.integers(0, len(tl1.AXIS_FILTERS), n_draws),
                  rng.integers(0, len(tl1.AXIS_EXITS), n_draws),
                  rng.integers(0, len(tl1.AXIS_SIZING), n_draws),
                  rng.integers(0, len(tl1.AXIS_TIMING), n_draws),
                  rng.integers(0, len(AXIS_STOP), n_draws),
                  rng.integers(0, len(AXIS_GATE), n_draws)))
    for i in range(n_draws):
        params = {}
        j = 0
        for nm in sorted(dom):
            values = dom[nm]
            if len(values) <= 1:
                params[nm] = values[0] if values else None
                continue
            params[nm] = values[min(int(box[i, j] * len(values)),
                                    len(values) - 1)]
            j += 1
        r_, x_, s_, t_, st_, gt_ = ax[i]
        yield i, {"module": spec["module"], "fn": spec["fn"],
                  "sig_params": params,
                  "axis": [tl1.AXIS_FILTERS[r_], tl1.AXIS_EXITS[x_],
                           tl1.AXIS_SIZING[s_], tl1.AXIS_TIMING[t_],
                           AXIS_STOP[st_], AXIS_GATE[gt_]],
                  "family": family}


# ------------------------------------------------------- exclusion (six sources)
def _mass_translate_row(r):
    """Declared conservative exact-key translation (module-level note
    MASS_TRANSLATION_NOTE).  Returns an exclusion row (dict) or None."""
    ax = r.get("axes") or {}
    if not (ax.get("R") == "none" and ax.get("X") == "own"
            and ax.get("S") == "full" and ax.get("T") == "daily"):
        return None
    module, _, fn = r["family"].partition(".")
    return {"module": module, "fn": fn,
            "sig_params": dict(r.get("params") or {}),
            "axis": ["none", "template_default", "equal_weight",
                     "daily_signal", "none", "none"]}


def _load_exclusion_rows_w3(grammar):
    """Six-source exclusion (prereg sec.1), all real-read at generate
    time.  Sources 1-2 = frozen serialized grammar stop-gate-none face;
    3 = W1 screen survivors (implicit stop=none+gate=none); 4 = W2
    screen survivors (explicit stop face + implicit gate=none); 5 = MASS
    screen survivors via the declared translation; 6-8 = judged products
    (w1_judge / MASS judged / w2_judge) -- generate-time real-read
    re-declare window (declared-unavailable -> zero rows, no fabrication).
    """
    rows = list(grammar["exclusion"]["stop_gate_none_face"])
    disc = {"grammar_stop_gate_none_rows": len(rows)}

    def _screen_survivors(scr_path, cand_path, gate_pad, tag):
        if not (os.path.exists(scr_path) and os.path.exists(cand_path)):
            return f"declared-unavailable ({os.path.basename(scr_path)} " \
                   f"absent)"
        scr = json.load(open(scr_path, encoding="utf-8"))
        cands = {c["candidate_id"]: c for c in
                 json.load(open(cand_path, encoding="utf-8"))["candidates"]}
        n = 0
        for cid in sorted(scr.get("survivors", [])):
            c = cands[cid]
            rows.append({"module": c["module"], "fn": c["fn"],
                         "sig_params": c["sig_params"],
                         "axis": list(c["axis"]) + gate_pad,
                         "face": f"{tag}:stop-gate-none",
                         "candidate_id": cid})
            n += 1
        return n

    disc["w1_screen_survivors"] = _screen_survivors(
        os.path.join(tl1.RES_DIR, "w1_screen.json"),
        os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none", "none"], "w1_screen_survivor")
    disc["w2_screen_survivors"] = _screen_survivors(
        os.path.join(tl2.RES_DIR, "w2_screen.json"),
        os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none"], "w2_screen_survivor")

    # MASS screen survivors: declared translation, honest attrition
    if os.path.exists(MASS_SCREEN_CKPT):
        n_tr = n_bad = 0
        with open(MASS_SCREEN_CKPT, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                r = json.loads(ln)
                if r.get("row_type") != "candidate" \
                        or not r.get("screen_pass"):
                    continue
                tr = _mass_translate_row(r)
                if tr is None:
                    n_bad += 1
                    continue
                tr["face"] = "mass_screen_survivor:translated-exact"
                tr["candidate_id"] = r.get("id")
                rows.append(tr)
                n_tr += 1
        disc["mass_screen_survivors"] = {
            "consumed_pass_rows": n_tr + n_bad,
            "translated_exact_rows": n_tr,
            "non_translatable_disclosed": n_bad,
            "note": MASS_TRANSLATION_NOTE}
    else:
        disc["mass_screen_survivors"] = "declared-unavailable " \
                                        "(screen_checkpoint.jsonl absent)"

    # judged products: generate-time real-read re-declare window (prereg
    # sec.1/sec.9); absent -> declared-unavailable zero rows (expected:
    # all three judge batches pool-waiting at freeze time)
    def _judged_source(jpath, cand_path, gate_pad, tag, mass=False):
        if not os.path.exists(jpath):
            return "declared-unavailable at generate time " \
                   f"({os.path.basename(jpath)} absent; pool-waiting); " \
                   "zero rows"
        j = json.load(open(jpath, encoding="utf-8"))
        cells = j.get("cells", [])
        n = 0
        cands = {}
        if not mass and cand_path and os.path.exists(cand_path):
            cands = {c["candidate_id"]: c for c in json.load(
                open(cand_path, encoding="utf-8"))["candidates"]}
        for c in cells:
            if mass:
                tr = _mass_translate_row(c)
                if tr is None:
                    continue
                tr["face"] = f"{tag}:translated-exact"
                rows.append(tr)
            else:
                src = cands.get(c.get("candidate_id"))
                if src is None:
                    continue
                rows.append({"module": src["module"], "fn": src["fn"],
                             "sig_params": src["sig_params"],
                             "axis": list(src["axis"]) + gate_pad,
                             "face": f"{tag}:stop-gate-none",
                             "candidate_id": c.get("candidate_id")})
            n += 1
        return {"consumed_rows": n,
                "note": "judged product consumed as exclusion rows "
                        "(exact-key law, positive or negative verdicts "
                        "alike)"}

    disc["w1_judge_products"] = _judged_source(
        W1_JUDGE_FILE, os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none", "none"], "w1_judged")
    disc["mass_judge_products"] = _judged_source(
        MASS_JUDGE_FILE, None, None, "mass_judged", mass=True)
    disc["w2_judge_products"] = _judged_source(
        W2_JUDGE_FILE, os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none"], "w2_judged")
    # (d)-face judged-supply weighting: frozen baseline uniform stands
    # (prereg sec.0 declare; sec.9 re-declare window unexercised absent
    # a pre-generate append-confirm amendment -- disclosed, no fabrication)
    disc["judged_supply_weighting"] = (
        "frozen baseline uniform per prereg sec.0 declare (axis families "
        "equal allocation, zero judged weighting); sec.9 re-declare window "
        "requires a prereg-level append-confirm BEFORE generate runs -- "
        "none exists, uniform stands, availability of the three judge "
        "products disclosed above")
    return rows, disc


def _excluded_w3(cand, rows):
    """Exact already-judged cell test, gate=none face only (prereg sec.1:
    gate=bull/bear = new-syntax legal cells -- never excluded; W1-lineage
    cells implicitly stop=none+gate=none; W2 cells carry their own stop
    face).  Returns the exclusion face or None."""
    if cand["axis"][5] != "none":
        return None
    for e in rows:
        if (cand["module"], cand["fn"]) == (e["module"], e["fn"]) \
                and cand["sig_params"] == e["sig_params"] \
                and cand["axis"] == e["axis"]:
            return e.get("face", "excluded")
    return None


# -------------------------------------------- effective face + engine curves
def _effective_signal_mask_w3(mask, prices, stop_key, atr20, gate_key,
                              gate_state):
    """Dedup-face holdings proxy with the frozen composition order
    GATE -> initial-stop (prereg sec.3 dedup legs; zero engine burn).
    gate=none+stop=none = W1 identity; gate-only/stop-only/combined all
    deterministic faces of the same two grammar layers."""
    S = gate_zero_mask(mask, gate_key, gate_state)
    return tl2._effective_signal_mask(S, prices, stop_key, atr20)


def run_candidate_curve_w3(cand, template, prices, P, states, atr20=None,
                           fundamental_ok=None, rng_matrix=None, p_on=None,
                           gate_state=None):
    """One W3 candidate cell at the engine face with the gate overlay +
    initial-stop overlay carried per-cell (prereg sec.3 face a; frozen
    composition order filter -> timing -> GATE -> STOP).

    gate=none+stop=none -> byte-identical to the tl1 engine face;
    gate=none -> byte-identical to the tl2 W2 engine face (parity law,
    selftest-pinned).  Returns (eq, trades, metrics, params, patch,
    stop_fired, gate_zeroed).
    """
    stop_key = cand["axis"][4]
    gate_key = cand["axis"][5]
    if gate_state is None:
        gate_state = gate_state_series(prices)
    if stop_key != "none" and STOP_FORMULA[stop_key]["kind"] == "atr" \
            and atr20 is None:
        atr20 = tl2.atr20_series(prices)
    mk = f"{cand['module']}.{cand['fn']}"
    face = "null" if rng_matrix is not None else tl1.GRAMMAR["faces"][mk]
    if rng_matrix is not None:
        mask = tl1._signal_frame(None, P, face, rng_matrix=rng_matrix,
                                 p_on=p_on)
    else:
        mask = tl1._signal_frame(cand, P, face)
    mask = mask.reindex(index=P["close"].index,
                        columns=P["close"].columns).fillna(0)
    mask = tl1.apply_filter(mask, cand["axis"][0], P, fundamental_ok)
    mask = tl1.apply_timing(mask, cand["axis"][3])
    G = gate_zero_mask(mask, gate_key, gate_state)
    gate_zeroed = int((mask > 0).sum().sum() - (G > 0).sum().sum())
    if stop_key == "none":
        S, stop_fired = G, 0
    else:
        S = tl2._effective_signal_mask(G, prices, stop_key, atr20)
        d = (G > 0) & (S == 0)
        stop_fired = int(sum(int((d[c] & ~d[c].shift(1, fill_value=False)
                                 ).sum()) for c in d.columns))
    params, patch = tl1.candidate_engine_params(cand, template)
    params, scale = tl1.sizing_pieces(cand, P, states, params)
    params["report_num_entries"] = True
    dd_control = (template.get("registered_dd_control")
                  if template is not None else None)
    with tl1.ExitPatch(patch):
        res = tl1.run_backtest(prices, params, entry_signal=S,
                               exit_signal=(S <= 0),
                               entry_size_scale=scale, dd_control=dd_control)
    eq = pd.Series(res["equity_curve"],
                   index=P["close"].index[:len(res["equity_curve"])])
    return eq, res["trades"], res["metrics"], params, patch, stop_fired, \
        gate_zeroed


def _null_axis_draw_w3(i):
    """Deterministic null-cell draw per prereg sec.3: rng=[SEED_NULL, i];
    consumption order frozen = p_on regime -> six-tuple axis
    R/X/S/T/STOP/GATE -> signal matrix.  Same engine/cost/panel as
    candidate cells incl. the gate leg (BACKTEST_PLAN three iron rules)."""
    rng = np.random.default_rng([SEED_NULL, i])
    p_on = tl1.NULL_P_REGIMES[int(rng.integers(len(tl1.NULL_P_REGIMES)))]
    ax = (tl1.AXIS_FILTERS[int(rng.integers(len(tl1.AXIS_FILTERS)))],
          tl1.AXIS_EXITS[int(rng.integers(len(tl1.AXIS_EXITS)))],
          tl1.AXIS_SIZING[int(rng.integers(len(tl1.AXIS_SIZING)))],
          tl1.AXIS_TIMING[int(rng.integers(len(tl1.AXIS_TIMING)))],
          AXIS_STOP[int(rng.integers(len(AXIS_STOP)))],
          AXIS_GATE[int(rng.integers(len(AXIS_GATE)))])
    return p_on, list(ax), rng


# ------------------------------------------------------- generate slice (s2)
def cmd_generate() -> int:
    t0 = time.time()
    print(f"=== {WAVE} generate (prereg FROZEN {PREREG}) ===")
    if os.path.exists(CANDIDATES_FILE):
        print("GENERATE-GATE: w3_candidates.json exists -- same-grammar "
              "rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4); refusing")
        return 2
    if not os.path.exists(GRAMMAR_FILE):
        print("GENERATE-GATE: w3_grammar.json absent -- run `grammar` first")
        return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if _grammar_sha16(grammar) != grammar["grammar_sha256"] \
            or grammar["grammar_sha256"] != FROZEN_SHA16:
        print(f"GENERATE-GATE: grammar sha drift -- frozen anchor "
              f"{FROZEN_SHA16} != file {grammar['grammar_sha256']}; "
              "refusing")
        return 2
    ram_min, ram_ok = tl2._ram_gate_gb()
    if not ram_ok:
        print(f"GENERATE-GATE: free RAM {ram_min}GB < 4GB (three-sample "
              f"r354 law, dual-company discipline) -- honest refuse, pool "
              f"retries when RAM frees")
        return 2
    tl1.GRAMMAR = grammar           # tl1._signal_frame reads tl1's global
    prices = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    prices = {s: df[df.index <= cut] for s, df in prices.items()}
    P = tl1.build_panels(prices)
    close = P["close"]
    try:
        bl = pd.read_csv(tl1.B_LAYER_MASK)
        ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
        overlap = sorted(s for s in close.columns if s in ok_codes)
    except Exception as e:
        overlap = []
        print(f"  [warn] b_layer_mask load error: {str(e)[:120]}")
    if overlap:
        fundamental_ok = pd.DataFrame(False, index=close.index,
                                      columns=close.columns)
        for s in overlap:
            fundamental_ok[s] = True
    else:
        fundamental_ok = None
    atr20 = tl2.atr20_series(prices)
    gate_state = gate_state_series(prices)
    excl_rows, excl_disc = _load_exclusion_rows_w3(grammar)
    neg_fns = {(e["module"], e["fn"])
               for e in grammar["exclusion"]["stop_gate_none_face"]
               if str(e.get("face", "")).startswith("negative")}

    # ---- draws: per-slot Sobol streams consumed in global round-robin
    candidates, excluded_log = [], []
    excl_hits = {"A": 0, "B": 0}
    for family, n_draws in (("A", N_A), ("B", N_B)):
        slots = grammar["families"][family]
        n_slots = len(slots)
        streams = {s: draw_candidate_sobol_w3(
                       grammar, family, s,
                       (n_draws - s + n_slots - 1) // n_slots)
                   for s in range(n_slots)}
        for i in range(n_draws):
            slot = i % n_slots
            _, cand = next(streams[slot])
            cand["candidate_id"] = f"W3-{family}-{i:04d}"
            cand["provenance"] = {"seed": SEED_GEN,
                                  "family_idx": (slot if family == "A"
                                                 else 6 + slot),
                                  "stream_draw_idx": i // n_slots,
                                  "global_draw_idx": i}
            if family == "A":
                cand["template_trader"] = slots[slot]["trader_id"]
                cand["negative_prior"] = False
            else:
                cand["negative_prior"] = \
                    (cand["module"], cand["fn"]) in neg_fns
            hit = _excluded_w3(cand, excl_rows)
            if hit:
                excl_hits[family] += 1
                excluded_log.append({"candidate_id": cand["candidate_id"],
                                     "module": cand["module"],
                                     "fn": cand["fn"],
                                     "axis": cand["axis"], "face": hit})
                continue
            candidates.append(cand)
        print(f"  raw draws {family}={n_draws}, exclusion hits "
              f"{excl_hits[family]}")

    # ---- dedup gate (T-84 s3) on the effective signal face (streaming)
    fps, series = [], []
    for j, cand in enumerate(candidates):
        mk = f"{cand['module']}.{cand['fn']}"
        mask = tl1._signal_frame(cand, P, grammar["faces"][mk])
        mask = mask.reindex(index=close.index,
                            columns=close.columns).fillna(0)
        mask = tl1.apply_filter(mask, cand["axis"][0], P, fundamental_ok)
        mask = tl1.apply_timing(mask, cand["axis"][3])
        S = _effective_signal_mask_w3(mask, prices, cand["axis"][4], atr20,
                                      cand["axis"][5], gate_state)
        fps.append(tl1._fingerprint(S))
        series.append(tl1._naive_returns(S, close).values)
        del mask, S
        if (j + 1) % 250 == 0:
            print(f"  [dedup face] {j + 1}/{len(candidates)}", flush=True)

    fp_groups = {}
    for i, fp in enumerate(fps):
        fp_groups.setdefault(fp, []).append(i)
    keep, fp_collapsed = set(), []
    for fp, members in fp_groups.items():
        members.sort(key=lambda k: candidates[k]["candidate_id"])
        keep.add(members[0])
        fp_collapsed.append({"kept": candidates[members[0]]["candidate_id"],
                             "eliminated": [candidates[m]["candidate_id"]
                                            for m in members[1:]]})
    idx_keep = sorted(keep)
    mat = np.vstack([series[i] for i in idx_keep])
    sd = mat.std(axis=1)
    live_rows = [j for j in range(len(idx_keep)) if sd[j] > 1e-12]
    corr_elim, dead = [], set()
    if len(live_rows) >= 2:
        sub = mat[live_rows]
        corr = np.corrcoef(sub)
        for a_ in range(len(live_rows)):
            for b_ in range(a_ + 1, len(live_rows)):
                if abs(corr[a_, b_]) >= 0.999:
                    ia, ib = idx_keep[live_rows[a_]], idx_keep[live_rows[b_]]
                    ka = candidates[ia]["candidate_id"]
                    kb = candidates[ib]["candidate_id"]
                    dead.add(ib if ka < kb else ia)
                    corr_elim.append({"pair": sorted([ka, kb]),
                                      "corr": round(float(corr[a_, b_]), 6),
                                      "eliminated": candidates[
                                          ib if ka < kb else ia]
                                      ["candidate_id"]})
    final_keep = [i for i in idx_keep if i not in dead]
    distinct = [candidates[i] for i in final_keep]

    # gate/stop face counts (prereg sec.5.4 direction-reading faces)
    gate_counts, stop_counts = {}, {}
    for c in distinct:
        gate_counts[c["axis"][5]] = gate_counts.get(c["axis"][5], 0) + 1
        stop_counts[c["axis"][4]] = stop_counts.get(c["axis"][4], 0) + 1

    # D6 disclosure column (naive face; prereg sec.1 per-cell max|corr|)
    reg_series = tl2._registered_naive_series(P, grammar)
    reg_names = sorted(reg_series)
    R = np.vstack([reg_series[nm] for nm in reg_names]) \
        if reg_names else np.zeros((0, len(close.index)))
    Rc = R - R.mean(axis=1, keepdims=True)
    rn = np.linalg.norm(Rc, axis=1)
    if final_keep:
        F = np.vstack([series[i] for i in final_keep])
        Fc = F - F.mean(axis=1, keepdims=True)
        fn = np.linalg.norm(Fc, axis=1)
        cm = (Fc @ Rc.T) / np.outer(np.where(fn > 1e-12, fn, 1.0),
                                    np.where(rn > 1e-12, rn, 1.0))
    else:
        cm = np.zeros((0, len(reg_names)))
    for row, i in enumerate(final_keep):
        v = cm[row]
        finite = v[np.isfinite(v)]
        candidates[i]["max_corr_vs_registered_naive"] = (
            round(float(np.max(np.abs(finite))), 4)
            if len(finite) else None)

    payload = {"wave": WAVE, "stage": "generate", "prereg": PREREG,
               "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
               "grammar_sha256": grammar["grammar_sha256"],
               "n": len(distinct), "candidates": distinct,
               "exclusion": {"hits": excl_hits,
                             "excluded_log": excluded_log,
                             "sources": excl_disc,
                             "note": "cell key=(template, params, "
                                     "axis_config, initial_stop, gate); "
                                     "exclusion face = gate=none only "
                                     "(sec.1); gate=bull/bear = "
                                     "new-syntax legal cells"},
               "dedup": {"raw": len(candidates), "distinct": len(distinct),
                         "fingerprint_collapse_groups": fp_collapsed,
                         "corr_collapses": corr_elim,
                         "note": "dedup legs on the generate-stage "
                                 "effective signal face (gate overlay + "
                                 "stop overlay applied, frozen composition "
                                 "order; naive-hold returns, zero engine "
                                 "burn); engine faces run at screen "
                                 "(W1 precedent)"},
               "gate_face_counts": gate_counts,
               "stop_face_counts": stop_counts,
               "gate_state_meta": gate_state[2],
               "d6_disclosure": {
                   "max_corr_vs_registered_naive": "per-cell column; "
                   "naive-face caliber (dedup byproduct); D6 binding gate "
                   "at s4 intake recomputes at the engine face"},
               "audit": {"ram_gate_gb": ram_min,
                         "negative_prior_derivation": "derived from the "
                         "frozen grammar's negative_default_axis:stop-"
                         "gate-none exclusion faces (face derivation is "
                         "mechanical)",
                         "note": "Sobol per-slot streams in global "
                                 "round-robin; deterministic pre-burn "
                                 "stage; same-grammar rerun still FORBIDDEN "
                                 "post-consume"},
               "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    tl1._dump(CANDIDATES_FILE, payload)

    # grammar consumption ledger row (append-only; prereg sec.4/sec.6)
    ser_ts = time.strftime("%Y-%m-%d %H:%M",
                           time.localtime(os.path.getmtime(GRAMMAR_FILE)))
    raw_total = len(candidates) + sum(excl_hits.values())
    row = (f"| {WAVE} | {grammar['grammar_sha256'][:16]} | "
           f"raw {raw_total} (A{N_A}/B{N_B}, excl hits "
           f"{sum(excl_hits.values())}) | dedup -> {len(distinct)} "
           f"(gate faces {json.dumps(gate_counts, sort_keys=True)}) | "
           f"seeds gen={SEED_GEN} null={SEED_NULL} unc={SEED_UNC} | "
           f"serialized {ser_ts} (r392) + consumed "
           f"{time.strftime('%Y-%m-%d %H:%M:%S')} (pool "
           f"TRIAL-LABOR-W3-GENERATE, T-97 owner bm-a) | same-grammar "
           f"rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4) |\n")
    os.makedirs(os.path.dirname(GRAMMAR_LEDGER), exist_ok=True)
    if not os.path.exists(GRAMMAR_LEDGER):
        with open(GRAMMAR_LEDGER, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# TRIAL_GRAMMAR_LEDGER (append-only; TRIAL_LABOR_LAW "
                     "sec.4 same-grammar-rerun ban)\n\n"
                     "| wave | grammar_sha16 | raw | dedup | seeds | "
                     "consumed | law |\n|---|---|---|---|---|---|---|\n")
    with open(GRAMMAR_LEDGER, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(row)
    print(f"generate done: raw {raw_total} -> exclusion hits "
          f"{sum(excl_hits.values())} -> dedup distinct {len(distinct)} "
          f"(fp-collapses {len(fp_collapsed)}, corr-collapses "
          f"{len(corr_elim)})")
    print(f"gate faces: {json.dumps(gate_counts, sort_keys=True)}; "
          f"gate na-window {gate_state[2]['na_window_bars']} bars")
    print(f"products: w3_candidates.json + ledger row "
          f"(sha16 {grammar['grammar_sha256'][:16]})")
    print(f"elapsed {time.time() - t0:.1f}s (zero engine cells burned)")
    return 0


# ------------------------------------------------------------ status / grammar
def cmd_status() -> int:
    print(f"=== {WAVE} status ===")
    print(f"grammar file: {GRAMMAR_FILE} "
          f"({'EXISTS' if os.path.exists(GRAMMAR_FILE) else 'not built'})")
    for f in ("w3_candidates.json", "prep_state.json", "w3_screen.json",
              "w3_judge.json", "w3_intake.json"):
        p = os.path.join(RES_DIR, f)
        print(f"  {f}: {'EXISTS' if os.path.exists(p) else '-'}")
    if os.path.isdir(CKPT_DIR):
        for f in sorted(os.listdir(CKPT_DIR)):
            if f.endswith(".jsonl"):
                n = sum(1 for _ in open(os.path.join(CKPT_DIR, f),
                                        encoding="utf-8"))
                print(f"  checkpoint/{f}: {n} rows")
    print("slice map (W2 r358/r359/r360/r362 precedent): slice-1 grammar "
          "+ gate overlay + selftest + serialization LANDED r392; "
          "slice-1b generate LANDED r392 (pool TRIAL-LABOR-W3-GENERATE "
          "ready); NEXT slices: screen (prep + K=200 nulls + survival "
          "line; physical dep = w3_candidates.json) -> judge (dual-leg + "
          "dual nulls seed 20288500) -> intake -- separate commits with "
          "MSG declarations; parallel claim legal per T-50/T-64 slice "
          "precedent after MSG-declare")
    return 0


def cmd_grammar() -> int:
    """Serialize the frozen grammar face (prereg sec.3: value-domain table
    frozen at runner-build time; zero candidates drawn -- not a wave run)."""
    if FROZEN_SHA16 and os.path.exists(GRAMMAR_FILE):
        g = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
        if g["grammar_sha256"] == FROZEN_SHA16:
            print(f"w3_grammar.json already frozen at anchor "
                  f"{FROZEN_SHA16}; refusing overwrite (append-only face)")
            return 0
    g = build_grammar_w3()
    os.makedirs(RES_DIR, exist_ok=True)
    with open(GRAMMAR_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(g, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    chk = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    assert chk["grammar_sha256"] == g["grammar_sha256"]
    print(f"w3_grammar.json written: sha16={g['grammar_sha256'][:16]} "
          f"axis_combos={g['axis_combos']} B_fns={len(g['families']['B'])} "
          f"exclusion_entries={len(g['exclusion']['stop_gate_none_face'])}")
    print(f"HARDCODE this sha16 into FROZEN_SHA16 (slice-1 anchor step) "
          f"if not yet pinned: {g['grammar_sha256']}")
    return 0


# ------------------------------------------------------------------ selftest
def cmd_selftest() -> int:
    print(f"=== {WAVE} selftest (hermetic, slice-1 + generate face) ===")
    ok_n = 0
    fails = [0]

    def ok(name, cond):
        nonlocal ok_n
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok_n += 1
        if not cond:
            fails[0] += 1
        return bool(cond)

    # [1] grammar: counts + new sha + seed binding
    g = build_grammar_w3()
    ok("grammar deterministic (sha equal on rebuild)",
       g["grammar_sha256"] == build_grammar_w3()["grammar_sha256"])
    n_b = len(g["families"]["B"])
    ok(f"B family = machinery actual 72 (prereg prose 76 declared "
       f"divergent, got {n_b})", n_b == 72)
    ok("inventory audit: 77 non-grid fns, 13 modules on disk",
       g["inventory_audit"]["non_grid_fns"] == 77
       and g["inventory_audit"]["modules_on_disk"] == 13)
    ok("axis combos = 10752 (7x8x4x2x8x3)",
       g["axis_combos"] == 10752 == AXIS_COMBOS)
    ok("gate axis frozen 3 faces",
       g["axes"]["gate"] == AXIS_GATE and len(AXIS_GATE) == 3)
    ok("stop axis imported from tl2 (8 faces, zero re-declare)",
       g["axes"]["initial_stop"] == tl2.AXIS_STOP
       and g["stop_formula"] is tl2.STOP_FORMULA)
    ok("seeds bound (20287500/20288000/20288500)",
       (SEED_GEN, SEED_NULL, SEED_UNC) == (20287500, 20288000, 20288500))
    ok("new-syntax sha16 != W1/MASS/W2 faces",
       g["grammar_sha256"][:16] not in
       ("a2fa15f4b06b3c40", "96269ebe766c3fc2", "1dd3d95792395cec"))
    if FROZEN_SHA16:
        ok("serialized anchor == build face (FROZEN_SHA16 pinned)",
           g["grammar_sha256"] == FROZEN_SHA16)
    ok("exclusion carried on stop-gate-none face",
       len(g["exclusion"]["stop_gate_none_face"]) >= 6)
    ok("gate spec frozen fields present",
       all(k in g["gate_spec"] for k in
           ("member", "ma_window", "min_periods", "nan_window",
            "overlay", "composition_order")))

    # [2] gate series math on a synthetic controlled panel
    idx = pd.bdate_range("2020-01-01", periods=320)
    # controlled 510300 path: flat 100 for 210 bars (MA200 warms at 200),
    # then decline to 80 (below MA200), then surge to 130 (above)
    path = np.concatenate([np.full(210, 100.0),
                            np.linspace(100.0, 80.0, 60),
                            np.linspace(80.0, 130.0, 50)])
    gate_frames = {"510300": pd.DataFrame(
        {"open": path, "high": path * 1.01, "low": path * 0.99,
         "close": path, "volume": 1e4, "amount": 1e6}, index=idx)}
    bull, bear, meta = gate_state_series(gate_frames)
    exp_ma200 = pd.Series(path, index=idx).rolling(
        200, min_periods=200).mean()
    exp_bull = (pd.Series(path, index=idx) >= exp_ma200)
    exp_bear = (pd.Series(path, index=idx) < exp_ma200) \
        & exp_ma200.notna()
    ok("gate MA200 == rolling(200, min_periods=200).mean() (frozen spec)",
       int(exp_ma200.isna().sum()) == 199
       and meta["na_window_bars"] == 199
       and exp_ma200.first_valid_index() == idx[199])
    ok("NaN window gate-closed BOTH faces (first 199 bars)",
       not bull.iloc[:199].any() and not bear.iloc[:199].any())
    ok("bull/bear faces == literal spec booleans (identity of "
       "definition, valid days complementary)",
       bull.equals(exp_bull) and bear.equals(exp_bear)
       and bool((bull.iloc[199:] == ~bear.iloc[199:]).all()))
    # causality legs: crossing days flip the permission EXACTLY at the
    # crossing day (signal-day close basis: no d+1 lag, no lookahead)
    db = exp_bull.astype(int).diff()
    down_days = list(db[db == -1].index)
    up_days = list(db[db == 1].index)
    ok("crossing legs present in fixture (down+up both)", 
       len(down_days) >= 1 and len(up_days) >= 1)
    if down_days:
        d = down_days[0]
        ok("causality: bull closes EXACTLY at the first close<MA200 day",
           bool(bull[d]) is False and bool(bull[idx[idx.get_loc(d) - 1]])
           and bool(bear[d]))
    if up_days:
        u = up_days[-1]
        ok("causality: bull opens EXACTLY at the first close>=MA200 day "
           "(signal-day basis, entry fills d+1 open)",
           bool(bull[u]) and not bool(bull[idx[idx.get_loc(u) - 1]])
           and not bool(bear[u]))
    ok("flips counted per face (deterministic)",
       meta["flips_bull_face"] == int((bull.values[1:]
                                      != bull.values[:-1]).sum())
       and meta["flips_bear_face"] == int((bear.values[1:]
                                           != bear.values[:-1]).sum()))
    bull2, bear2, meta2 = gate_state_series(gate_frames)
    ok("gate state deterministic (double-run equal)",
       bull.equals(bull2) and bear.equals(bear2) and meta == meta2)

    # [3] gate_zero_mask unit legs (synthetic mask; reindex law)
    cols = ["500000", "500001"]
    mask = pd.DataFrame(0, index=idx, columns=cols, dtype=int)
    mask.iloc[150:320, 0] = 1          # spans NaN window + closed + open
    mask.iloc[150:320, 1] = 1
    z_none = gate_zero_mask(mask, "none", (bull, bear, meta))
    ok("gate=none is the identity (W1/W2 semantic baseline)",
       z_none is mask)
    keep_bull_win = bull.reindex(idx).fillna(False).astype(int)
    keep_bear_win = bear.reindex(idx).fillna(False).astype(int)
    z_bull = gate_zero_mask(mask, "bull", (bull, bear, meta))
    ok("bull face == mask * bull-permission (exact elementwise law)",
       z_bull["500000"].equals(mask["500000"].mul(keep_bull_win))
       and z_bull["500001"].equals(mask["500001"].mul(keep_bull_win)))
    z_bear = gate_zero_mask(mask, "bear", (bull, bear, meta))
    ok("bear face == mask * bear-permission (exact elementwise law)",
       z_bear["500000"].equals(mask["500000"].mul(keep_bear_win))
       and z_bear["500001"].equals(mask["500001"].mul(keep_bear_win)))
    ok("NaN-window signals blocked on BOTH faces (conservative)",
       int(z_bull.iloc[:199].sum().sum()) == 0
       and int(z_bear.iloc[:199].sum().sum()) == 0)
    ok("gate zero deterministic (double-run byte-equal)",
       gate_zero_mask(mask, "bull", (bull, bear, meta)).equals(z_bull))

    # [4] Sobol six-tuple draw determinism + domain binding
    c1 = list(draw_candidate_sobol_w3(g, "A", 0, 32))
    c2 = list(draw_candidate_sobol_w3(g, "A", 0, 32))
    ok("Sobol draw deterministic (32 draws byte-equal)",
       json.dumps(c1, sort_keys=True, default=str)
       == json.dumps(c2, sort_keys=True, default=str))
    ok("draw carries six-tuple axis with gate face",
       all(len(c["axis"]) == 6 and c["axis"][5] in AXIS_GATE
           for _, c in c1))
    ok("draw params inside frozen domains",
       all(c["sig_params"][nm] in g["value_domains"][
               f"{c['module']}.{c['fn']}"][nm]
           for _, c in c1
           for nm in c["sig_params"]))
    tot = sum(1 for _ in draw_candidate_sobol_w3(g, "B", 0, 64))
    ok("B-family stream yields declared count", tot == 64)

    # [5] exclusion law (prereg sec.1): gate=none face only; MASS declared
    # translation
    excl_rows = [
        {"module": "ta", "fn": "engulf_reversal",
         "sig_params": {"drop_th": -0.05},
         "axis": ["none", "template_default", "equal_weight",
                   "daily_signal", "none", "none"],
         "face": "registered_default_axis:stop-gate-none"},
        {"module": "patterns", "fn": "needle_probe",
         "sig_params": {"drop_th": -0.025, "shadow_pct": 0.03},
         "axis": ["liquidity", "profit_ladder", "regime_delever",
                  "daily_signal", "p3", "none"],
         "face": "w2_screen_survivor:stop-gate-none"},
        {"module": "ta", "fn": "bb_squeeze_breakout",
         "sig_params": {"entry_n": 34, "exit_n": 7},
         "axis": ["none", "template_default", "equal_weight",
                   "daily_signal", "none", "none"],
         "face": "mass_screen_survivor:translated-exact"}]
    c_reg = {"module": "ta", "fn": "engulf_reversal",
             "sig_params": {"drop_th": -0.05},
             "axis": ["none", "template_default", "equal_weight",
                      "daily_signal", "none", "none"]}
    ok("exclusion: registered default stop-gate-none cell rejected",
       _excluded_w3(c_reg, excl_rows) is not None)
    ok("exclusion: same cell stop!=none NOT excluded (new-syntax face)",
       _excluded_w3(dict(c_reg, axis=[*c_reg["axis"][:4], "p3", "none"]),
                    excl_rows) is None)
    ok("exclusion: same cell gate!=none NOT excluded (legal new face)",
       _excluded_w3(dict(c_reg, axis=[*c_reg["axis"][:5], "bull"]),
                    excl_rows) is None)
    c_w2 = {"module": "patterns", "fn": "needle_probe",
            "sig_params": {"drop_th": -0.025, "shadow_pct": 0.03},
            "axis": ["liquidity", "profit_ladder", "regime_delever",
                     "daily_signal", "p3", "none"]}
    ok("exclusion: W2 survivor with explicit stop=p3 face rejected on "
       "exact key",
       _excluded_w3(c_w2, excl_rows) is not None)
    c_mass = {"module": "ta", "fn": "bb_squeeze_breakout",
              "sig_params": {"entry_n": 34, "exit_n": 7},
              "axis": ["none", "template_default", "equal_weight",
                       "daily_signal", "none", "none"]}
    ok("exclusion: MASS translated-exact cell rejected",
       _excluded_w3(c_mass, excl_rows) is not None)
    tr_yes = _mass_translate_row({"family": "ta.bb_squeeze_breakout",
                                  "params": {"entry_n": 34, "exit_n": 7},
                                  "axes": {"R": "none", "X": "own",
                                           "S": "full", "T": "daily"}})
    tr_no = _mass_translate_row({"family": "trend.donchian_breakout",
                                 "params": {"entry_n": 34, "exit_n": 7},
                                 "axes": {"R": "bear", "X": "own",
                                          "S": "full", "T": "daily"}})
    tr_no2 = _mass_translate_row({"family": "trend.donchian_breakout",
                                  "params": {"entry_n": 34, "exit_n": 7},
                                  "axes": {"R": "none", "X": "t5",
                                           "S": "full", "T": "daily"}})
    tr_no3 = _mass_translate_row({"family": "trend.donchian_breakout",
                                  "params": {"entry_n": 34, "exit_n": 7},
                                  "axes": {"R": "none", "X": "own",
                                           "S": "delever", "T": "daily"}})
    tr_no4 = _mass_translate_row({"family": "trend.donchian_breakout",
                                  "params": {"entry_n": 34, "exit_n": 7},
                                  "axes": {"R": "none", "X": "own",
                                           "S": "full", "T": "weekly"}})
    ok("MASS translation: exact face translatable; R!=none/X=t*/"
       "S=delever/T=weekly NOT (declared conservative table)",
       tr_yes is not None
       and tr_yes["axis"] == ["none", "template_default", "equal_weight",
                              "daily_signal", "none", "none"]
       and tr_no is None and tr_no2 is None and tr_no3 is None
       and tr_no4 is None)
    ok("MASS translation: module/fn split + params carried verbatim",
       tr_yes["module"] == "ta" and tr_yes["fn"] == "bb_squeeze_breakout"
       and tr_yes["sig_params"] == {"entry_n": 34, "exit_n": 7})

    # [6] effective-face composition legs (gate -> stop; synthetic)
    flatA = pd.DataFrame({"open": 100.0, "high": 101.0, "low": 99.0,
                          "close": 100.0, "volume": 1000.0,
                          "amount": 1e5}, index=idx)
    dip = flatA.copy()
    dip.loc[idx[250], "low"] = 90.0       # pierces any p3 level on day 250
    mask6 = pd.DataFrame(0, index=idx, columns=["A", "B"], dtype=int)
    mask6.iloc[210:320, 0] = 1            # gate-valid zone (post-199)
    mask6.iloc[150:320, 1] = 1            # spans NaN window + valid zone
    gs = (bull, bear, meta)
    S_id = _effective_signal_mask_w3(mask6, {"A": dip, "B": flatA}, "none",
                                     None, "none", gs)
    ok("effective face: gate=none+stop=none is the identity",
       S_id.equals(mask6))
    S_gb = _effective_signal_mask_w3(mask6, {"A": dip, "B": flatA},
                                     "none", None, "bull", gs)
    S_gr = _effective_signal_mask_w3(mask6, {"A": dip, "B": flatA},
                                     "none", None, "bear", gs)
    ok("effective face: gate-only faces == mask * permission (exact)",
       S_gb["A"].equals(mask6["A"].mul(keep_bull_win))
       and S_gr["A"].equals(mask6["A"].mul(keep_bear_win)))
    S_gsBull = _effective_signal_mask_w3(mask6, {"A": dip, "B": flatA},
                                         "p3", None, "bull", gs)
    S_gsBear = _effective_signal_mask_w3(mask6, {"A": dip, "B": flatA},
                                          "p3", None, "bear", gs)
    S_gsBear2 = _effective_signal_mask_w3(mask6, {"A": dip, "B": flatA},
                                           "p3", None, "bear", gs)
    ok("effective face: gate+stop composed, deterministic (double-run "
       "byte-equal)",
       S_gsBear.equals(S_gsBear2))
    ok("effective face: composed bear face differs from gate-only bear "
       "(stop bites inside the gate-open decline window)",
       not S_gsBear.equals(S_gr)
       and int(((S_gsBear["A"] == 0) & (mask6["A"] == 1)
                & (keep_bear_win == 1)).sum()) > 0)
    ok("effective face: composed bull face never holds on bull-closed "
       "days (gate precedes stop arming)",
       int(((S_gsBull > 0) & (keep_bull_win == 0)).sum().sum()) == 0)
    # gate=none+stop=p3 parity vs the tl2 face (import law)
    S_tl2 = tl2._effective_signal_mask(mask6, {"A": dip, "B": flatA},
                                       "p3", None)
    S_w3n = _effective_signal_mask_w3(mask6, {"A": dip, "B": flatA}, "p3",
                                       None, "none", gs)
    ok("effective face: gate=none+stop=p3 == tl2 W2 face byte-equal "
       "(parity law)",
       S_w3n.equals(S_tl2))

    # [7] round-robin stream consumption == per-slot sequential streams
    n_slots_a = len(g["families"]["A"])
    n_rr = 18
    streams = {s: draw_candidate_sobol_w3(
                   g, "A", s, (n_rr - s + n_slots_a - 1) // n_slots_a)
               for s in range(n_slots_a)}
    rr = [next(streams[i % n_slots_a]) for i in range(n_rr)]
    seq = {s: [c for _, c in draw_candidate_sobol_w3(
                   g, "A", s, (n_rr - s + n_slots_a - 1) // n_slots_a)]
           for s in range(n_slots_a)}
    reassembled = [seq[i % n_slots_a][i // n_slots_a] for i in range(n_rr)]
    ok("round-robin consumption == per-slot sequential (identity)",
       json.dumps([c for _, c in rr], sort_keys=True, default=str)
       == json.dumps(reassembled, sort_keys=True, default=str))

    # [8] registered-six naive face via tl2 import (zero-variance ok)
    tl1.GRAMMAR = g
    frames2 = tl1._synth_prices(n_days=120, n_syms=3, seed=17)
    P2 = tl1.build_panels(frames2)
    reg = tl2._registered_naive_series(P2, g)
    ok("registered-six naive series built (6 members, panel-length)",
       len(reg) == 6 and all(len(v) == len(P2["close"].index)
                             for v in reg.values()))

    # [9] engine-face legs: parity + determinism + gate bites (null path)
    frames3 = tl1._synth_prices(n_days=320, n_syms=3, seed=23)
    # controlled 510300 path so the gate has open+closed zones post-MA200
    p3path = np.concatenate([np.full(210, 100.0),
                             np.linspace(100.0, 80.0, 60),
                             np.linspace(80.0, 130.0, 50)])
    frames3["510300"] = pd.DataFrame(
        {"open": p3path, "high": p3path * 1.01, "low": p3path * 0.99,
         "close": p3path, "volume": 1e4, "amount": 1e6}, index=frames3[
            "510300"].index)
    P3 = tl1.build_panels(frames3)
    st3 = pd.Series("GREEN", index=P3["close"].index)
    gs3 = gate_state_series(frames3)
    base = {"module": "volatility", "fn": "low_vol_long",
            "sig_params": {"n": 60, "top_k": 3, "rebal_days": None},
            "family": "B", "candidate_id": "ST-B-0000",
            "axis": ["none", "time_stop_5d", "equal_weight",
                     "daily_signal", "none", "none"]}
    eq_w3, *_ = run_candidate_curve_w3(base, None, frames3, P3, st3,
                                       gate_state=gs3)
    eq_tl1 = tl1.run_candidate_curve(
        dict(base, axis=base["axis"][:4]), None, frames3, P3, st3)[0]
    ok("engine face: gate=none+stop=none identical to tl1 face "
       "(byte-equal)",
       list(eq_w3.values) == list(eq_tl1.values))
    stop_c = dict(base, axis=[*base["axis"][:4], "p3", "none"])
    eq_s, tr_s, m_s, _, _, fired_s, gz_s = run_candidate_curve_w3(
        stop_c, None, frames3, P3, st3, gate_state=gs3)
    eq_s2 = tl2.run_candidate_curve_w2(
        dict(stop_c, axis=stop_c["axis"][:5]), None, frames3, P3, st3)[0]
    ok("engine face: gate=none+stop=p3 identical to tl2 W2 face "
       "(byte-equal parity law)",
       list(eq_s.values) == list(eq_s2.values) and fired_s >= 0)
    eq_s3, *_ = run_candidate_curve_w3(stop_c, None, frames3, P3, st3,
                                       gate_state=gs3)
    ok("engine face: deterministic (double-run byte-equal)",
       list(eq_s3.values) == list(eq_s.values))
    # gate bites at the engine face: same random null signals, gate=bull
    # vs gate=none -> different curves (null path needs no grammar face)
    rng_n = np.random.default_rng([4242, 1])
    mat_n = rng_n.random((len(P3["close"].index),
                          len(P3["close"].columns)))
    null_c = {"module": "null", "fn": "random_signal",
              "sig_params": {"p_on": 0.05},
              "axis": ["none", "template_default", "equal_weight",
                       "daily_signal", "none", "none"],
              "candidate_id": "ST-NULL-0", "family": "NULL"}
    eq_ng, *_ = run_candidate_curve_w3(null_c, None, frames3, P3, st3,
                                       rng_matrix=mat_n, p_on=0.05,
                                       gate_state=gs3)
    null_b = dict(null_c, axis=[*null_c["axis"][:5], "bull"])
    eq_bg, *_ = run_candidate_curve_w3(null_b, None, frames3, P3, st3,
                                       rng_matrix=mat_n, p_on=0.05,
                                       gate_state=gs3)
    eq_bg2, *_ = run_candidate_curve_w3(null_b, None, frames3, P3, st3,
                                        rng_matrix=mat_n, p_on=0.05,
                                        gate_state=gs3)
    ok("engine face: gate=bull bites (null-signal curve differs from "
       "gate=none; deterministic double-run)",
       list(eq_bg.values) != list(eq_ng.values)
       and list(eq_bg.values) == list(eq_bg2.values))

    # [10] null draw: determinism + six-tuple axis binding (prereg sec.3
    # frozen consumption order p_on -> R/X/S/T/STOP/GATE -> matrix)
    p1, ax1, rng1 = _null_axis_draw_w3(7)
    p1b, ax1b, rng1b = _null_axis_draw_w3(7)
    ok("null draw deterministic (p_on + six-tuple axis + rng state)",
       p1 == p1b and ax1 == ax1b
       and list(rng1.random(3)) == list(rng1b.random(3)))
    ok("null axis = six-tuple with stop+gate faces in frozen grids",
       len(ax1) == 6 and ax1[0] in tl1.AXIS_FILTERS
       and ax1[1] in tl1.AXIS_EXITS and ax1[2] in tl1.AXIS_SIZING
       and ax1[3] in tl1.AXIS_TIMING and ax1[4] in AXIS_STOP
       and ax1[5] in AXIS_GATE and p1 in tl1.NULL_P_REGIMES)

    # [11] ledger batch names frozen (prereg sec.3 literals)
    ok("ledger batch names frozen per prereg sec.3 literals",
       SCREEN_BATCH == "TRIAL_LAB_W3_SCREEN"
       and JUDGE_BATCH == "TRIAL_LAB_W3_JUDGE")

    # [12] grammar serialization round-trip (tempfile; no repo writes)
    import tempfile
    with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w", encoding="utf-8",
            newline="\n") as tf:
        json.dump(g, tf, ensure_ascii=False, indent=1, sort_keys=True)
        tmp_path = tf.name
    try:
        chk = json.load(open(tmp_path, encoding="utf-8"))
        ok("grammar serialization round-trip (sha stable)",
           chk["grammar_sha256"] == g["grammar_sha256"]
           and _grammar_sha16(chk) == g["grammar_sha256"])
    finally:
        os.unlink(tmp_path)

    print(f"selftest: {ok_n - fails[0]}/{ok_n} PASS, "
          f"{fails[0]} FAIL")
    return 1 if fails[0] else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("selftest")
    sub.add_parser("status")
    sub.add_parser("grammar")
    sub.add_parser("generate")
    a = ap.parse_args(argv)
    # r141 crash-lane law: explicit per-command forwarding; no zero-arg
    # dict dispatch; subcommands not yet built (screen/judge/intake) are
    # NOT registered here (half-built dispatch = forbidden face)
    return {"selftest": cmd_selftest, "status": cmd_status,
            "grammar": cmd_grammar, "generate": cmd_generate}[a.cmd]()


if __name__ == "__main__":
    raise SystemExit(main())
