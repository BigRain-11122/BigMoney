"""PERPETUAL-N2-W19 runner -- alphagen channel beam feedback-search batch
(T23 U3 channel (1) "new grammar", slice-2 runner legs; W18 clone under
the r836 clone law: EVERY parameter explicitly checked, mechanical faces
verbatim, diffs confined to the frozen W19 parameter set + the W19 new
faces ordered by the prereg).

Prereg: research/PERPETUAL_N2_W19_PREREG.md (wave-level; DRAFT until the
freeze window lands; slice map in its appendix -- slice-2 = THIS runner +
hermetic selftest + FREEZE-GATE refuse-burn machine proof + refusal
receipt + pin-slice panel law).
Law: O-20260930-2340 N2 standing-supply face + O-20261011-0012 sec.ii
queue-deepen + O-1819 queue-never-empty + TRIAL_LABOR_LAW sec.1 standing
line + W18 sec.8 next-wave amendment order (attrition-priced B budget +
refusal-receipt decomposition -- the wave-level authorization for THIS
redesign); criteria law = T23 slice-2 calibration (family-level line only).

FROZEN METHOD (prereg sec.3; nothing outside it gates the verdict):
  - Grammar = census grammar frozen face, IMPORTED from
    scripts/t23_random_grammar_census.py (leaves/ops/windows constants,
    evaluator, panel loader, PIT mask, IC faces, permutation nulls --
    import-face reuse, zero rewrite; probe-anchor same-face assertions
    enforced in run() and selftest L1).
  - PIN-SLICE PANEL LAW (W19 new face, prereg sec.2): the panel is loaded
    with pin_end=CUTOFF_PIN -- the date axis is truncated to <= 2026-10-09
    BEFORE the trailing 500+census-warmup window take (t23.load_panel
    pin_end parameterization), so ANY burn day after further bar advances
    reproduces the census-instant panel window byte-identically: same
    window start (elig listed/fresh cumsum anchor identical), same window
    end, same fwd-ret tail-NaN face. Zero +/-N-day drift vs the census D1
    comparison face.
  - Generation = controlled feedback search (beam, NOT PPO-RL training):
    R1 24 random draws with tree height <= 2 -> top-6 by |ICIR| (h=1);
    R2 24 single-node leaf expansions of the R1 top-6 (products height
    <= 3) -> top-6; R3 14 further leaf expansions of the R2 top-6 under
    the PINNED split vector (3,3,3,3,1,1) -- top four parents 3 slots
    each, fifth and sixth 1 slot each; parents truncated in order if
    fewer than 6 evaluable. K = 62 total draws (W18=64: the R3 tail cut
    16->14 is the only geometry change; the R1/R2 exploration core is
    verbatim). In-batch dedup on the CANONICAL tree fingerprint
    (commutative ADD/MUL/CORR child ordering = "tree normalization");
    T-84s3 fingerprint dedup vs all consumed grammar rows -- the census
    48 unique formula strings (results/t23_census/CENSUS-2026-10-09.json)
    plus a belt-and-braces full TRIAL_GRAMMAR_LEDGER text scan; hits are
    excluded at draw time and honestly counted (draw budget is NOT
    redrawn -- 62 draws is the envelope).
  - Attrition guard = SKIP-ONLY face (W19 correction of the W18 compound
    guard): h1 skips > 10% of ENROLLED -> mechanism-suspect honest exit 2
    (empirical base: W18 2/50 = 4%). T-84s3 hits and in-batch duplicates
    are legal grammar-space collisions (census 25% precedent): disclosed,
    never a refuse reason.
  - Measurement face: h=1 next-day close-to-close rank-IC/ICIR (primary);
    h=5 decay descriptive only, never in the verdict line (census same
    face). min_cross=100 / min_periods=30 census gates.
  - Nulls: B=7 within-day same-mask factor-rank permutation draws per
    evaluated formula (census construction) -> POOLED null family;
    B priced off the 25% double-seed attrition evidence:
    B = ceil(300 / (62 * 0.75)) = 7 (W18 sec.8 lesson: budget derives as
    ceil(line / (K * survival)), never off the bare envelope). Pooled
    null ceiling 62 * 7 = 434; family line = pooled null p95.
  - SUFFICIENCY LINE = 300 pooled draws, EXPLICIT NON-LOWERING CLAUSE:
    the post-refuse downward adjustment of the line would be
    threshold-gaming; attrition prices the BUDGET (the path cost to the
    line), never the LINE itself. Achieving face: >= ceil(300/7) = 43 ok
    formulas; expected 62 * 0.75 = 46.5 ok (+3.5 headroom); expected
    pooled 325.5.
  - REFUSAL RECEIPT (W19 hard spec, prereg sec.3): EVERY rc2 refuse path
    (freeze-gate / panel gate / attrition guard / sufficiency line) lands
    results/alphagen_w19/refusal-<cutoff>.json carrying the FULL
    decomposition face (n_excluded_ledger_t84s3 / n_excluded_in_batch_dup
    / n_enrolled / n_h1_skip / n_ok / n_pooled; null where not yet
    derivable) -- W18 refused with decomposition only in stdout and the
    attrition source had to be re-derived by the r862 replay; that debt
    does not repeat. Refuse is still zero-product zero-ledger-row (the
    receipt is a receipt, not a batch product).
  - V1 (family-level, program-frozen, data-adaptive, zero hand-picking):
    observed family max |ICIR| > pooled null p95.
  - D1 leverage face (descriptive, NOT gating): feedback family max vs
    census random-search family anchors 0.353 / null p95 0.139, carrying
    the K-parity disclosure (K=62 vs census 64 = 96.9% draw parity; ok
    expectation 46.5 vs census 48 unique -- same-band, NOT claimed
    equal-budget).
  - M1 t face: per-member in-batch IC t = ic_mean/ic_std*sqrt(n_periods)
    declared through science_gates.m1_t_value_gate (missing t face =
    missing_input refusal, never waved through).
  - Trials ledger: science_gates.append_ledger("PERPETUAL-N2-W19", 496,
    file_name="results/alphagen_w19/W19-2026-10-09.json",
    evidence_cutoff="2026-10-09") -- dict schema, chain head re-derived
    at run time; re-run = finalize_already_landed no-op (pit-95 law).
  - evidence_cutoff pinned 2026-10-09 (census same-instant, forward
    lockbox D2); results JSON carries top-level
    science_gates.cutoff_meta("2026-10-09") (C2 visibility law).

SEED BANDS (freeze-time registration, r682 ladder-horizon derive +
Tools/seed_admit_gate.py rc0 first; DRAFT writes NO band values -- r702
band-drift lesson; this module reads them from science_gates.SEED_REGISTRY
at run time and NEVER hardcodes):
  perpetual_n2_w19_gen     -- beam generation streams, rng=[gen,round,
                              parent,slot]: R1 rng([gen,1,i]) i<24;
                              R2 rng([gen,2,p,j]) p<6,j<4; R3
                              rng([gen,3,p,j]) p<6, j<SPLIT[p],
                              SPLIT=(3,3,3,3,1,1)
  perpetual_n2_w19_scrnull -- permutation null family, rng=[scrnull,idx,b]
                              idx<62, b<7
  perpetual_n2_w19_unc     -- reserved uncertainty berth, freeze-window
                              wiring (W15 unc/judge precedent); consumed by
                              NO W19 core mechanism -- disclosed, not
                              asserted. FREEZE-GATE still requires it
                              (three-band law: any band missing -> refuse).
FREEZE-GATE: `run` refuses with rc2 (honest refuse, zero burn, refusal
receipt landed) while any of the three bands is absent from
SEED_REGISTRY.

Compute budget: K=62 draws + <=434 nulls = 496 <= 500 RETAIL_QUANT_TRACK
30-day budget gate; single-process pure-CPU short batch (O-2100 legal
window, census same machinery measured 564.1s for 4,160 draws -> this
batch ~496 draws est. <=120s + panel load); NOT in runnable_pool.

Subcommands:
  run       -- gated burn (FREEZE-GATE -> panel gate -> pit-95 idempotence
               -> pin-slice panel load -> beam -> attrition guard ->
               family faces -> payload + ledger block). Every rc2 refuse
               lands a refusal receipt with the full decomposition.
  probe     -- read-only fact face for the freeze window (panel gate,
               pin-slice wiring, band posture, census anchors, draft-probe
               receipts, closed families, grammar ledger, chain head,
               prereg markers, freeze-conditions checklist); receipt ->
               results/alphagen_w19/probe_latest.json
  selftest  -- hermetic offline legs (r116 law: zero network, zero engine,
               zero repo data reads; synthetic panels via the census
               _synth_panel import-face; the FREEZE-GATE machine-proof leg
               redirects the output faces to a system tempdir -- no repo
               file is touched).

Exit contract: run 0 = burn/no-op; 2 = freeze-gate refuse / awaiting
panel / mechanism suspect / insufficient pooled nulls (all rc2 with
refusal receipt). probe 0/2. selftest 0/1.

-- bm-b r863 slice-2 * marks +0 * SEED consumed only on run (post-freeze)
   * research output, not investment advice * live-trading gate = monthly
   review + CEO-only, unchanged.
"""
from __future__ import annotations

import datetime as dt
import inspect
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# r817 pit law: ROOT precedes scripts/ so the `knowledge` namespace package
# resolves when science_gates imports it (dual-entry parity).
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import science_gates as sg                                  # noqa: E402
import t23_random_grammar_census as t23                     # noqa: E402

# ------------------------------------------------------------ frozen constants
BATCH = "PERPETUAL-N2-W19"
PREREG = "research/PERPETUAL_N2_W19_PREREG.md"
QUEUE_ROW = "state/queue/tech.md T23 (N2 U3 channel-1) slice-2 (W19)"
FAMILY_KEY = "alphagen_grammar_v1"
CUTOFF_PIN = "2026-10-09"                    # census same-instant law
OUT_DIR = os.path.join(ROOT, "results", "alphagen_w19")
PRODUCT = os.path.join(OUT_DIR, f"W19-{CUTOFF_PIN}.json")
PRODUCT_REL = f"results/alphagen_w19/W19-{CUTOFF_PIN}.json"
PROBE_RECEIPT = os.path.join(OUT_DIR, "probe_latest.json")
REFUSAL_RECEIPT = os.path.join(OUT_DIR, f"refusal-{CUTOFF_PIN}.json")
CENSUS_PRODUCT = os.path.join(ROOT, "results", "t23_census",
                              f"CENSUS-{CUTOFF_PIN}.json")
DRAFT_PROBE_RECEIPT = os.path.join(ROOT, "results",
                                   "_r862bmb_n2w19_draft_probe.json")
GRAMMAR_LEDGER = os.path.join(ROOT, "research", "TRIAL_GRAMMAR_LEDGER.md")

K_DRAWS = 62
R1_N, R2_N, R3_N = 24, 24, 14                # 24 + 24 + 14 = 62
TOP_BEAM = 6
R3_SPLIT = (3, 3, 3, 3, 1, 1)                # W19 split pin: top-6 parents,
#                                            # per-parent slots (3,3,3,3,1,1)
R1_HEIGHT_CAP = 2                             # prereg: R1 depth<=2
GRAM_HEIGHT_MAX = 3                           # grammar max_depth (census)
B_NULLS = 7                                   # ceil(300/(62*0.75)) -- attrition-
#                                             # priced null budget (W18 sec.8)
N_TRIALS = K_DRAWS + K_DRAWS * B_NULLS       # 62 + 434 = 496 <= 500 gate
MIN_POOLED_NULLS = 300                        # sufficiency line, NON-LOWERING
MAX_SKIP_FRAC = 0.10                          # skip-only attrition guard
MIN_CROSS = t23.MIN_CROSS                     # 100, census same gate
MIN_PERIODS = t23.MIN_PERIODS                 # 30, census same gate
HORIZONS = (1, 5)                             # h=1 primary, h=5 descriptive
PER_FILES_FLOOR = 5000                        # prereg data-completeness gate

BAND_KEYS = {
    "gen": "perpetual_n2_w19_gen",
    "scrnull": "perpetual_n2_w19_scrnull",
    "unc": "perpetual_n2_w19_unc",
}
BAND_WIDTH = 499                              # berth width (W15 band law)

# census calibration anchors (T23 slice-2 frozen readout; judgement-reading
# INPUT, never this batch's criteria line -- prereg sec.2)
CENSUS_ANCHORS = {
    "census_holds": True,
    "observed_family_max_abs_icir": 0.353,
    "null_family_p95": 0.139,
    "n_unique_formulas": 48,
    "k_formulas": 64,
    "evidence_cutoff": CUTOFF_PIN,
    "ledger_total": 876731,
}

A158_LINEAGE_PRIOR = t23.A158_LINEAGE_PRIOR

# probe-anchored IC machinery import face (zero rewrite; same-face
# assertions enforced at run() and selftest L1)
LOAD_PANEL = t23.load_panel
GATE_FACE = t23.gate_face
EVALUATE = t23.evaluate
IC_FACES = t23._formula_ic_faces
PERMUTE = t23._permute_ranks_within_mask
SYNTH_PANEL = t23._synth_panel
FWD_RET = t23.fwd_ret
FORMULA_STR = t23.formula_str
NODE_DEPTH = t23.node_depth
LEAF_NAMES = t23.LEAF_NAMES
ROLL_OPS = t23.ROLL_OPS
UN_OPS = t23.UN_OPS
BIN_OPS = t23.BIN_OPS
WINDOWS = t23.WINDOWS
_COMMUTATIVE = ("ADD", "MUL", "CORR")

# refusal-receipt decomposition keys (prereg sec.3 hard spec)
REFUSAL_KEYS = ("n_excluded_ledger_t84s3", "n_excluded_in_batch_dup",
                "n_enrolled", "n_h1_skip", "n_ok", "n_pooled")


# ------------------------------------------------------------------ freeze gate

def _bands_registered(registry=None):
    """(ok, face) -- three-band presence check (values disclosed, never
    asserted against hardcodes: DRAFT posture forbids band values in this
    file; the freeze window derives and registers them, r682 recipe)."""
    reg = sg.SEED_REGISTRY if registry is None else registry
    face, missing = {}, []
    for nm, key in BAND_KEYS.items():
        v = reg.get(key)
        face[nm] = {"key": key, "registered": v is not None,
                    "value": int(v) if isinstance(v, (int, float)) else None}
        if v is None:
            missing.append(key)
    return (not missing), face


# ------------------------------------------------------------------ generation

def sample_height(rng, cap):
    """Height-capped sampler over the census grammar constants (leaves /
    ops / windows imported; draw-order mirrors census _sample_node)."""
    r = float(rng.random())
    if cap <= 1 or r < 0.30:
        return ("leaf", LEAF_NAMES[int(rng.integers(len(LEAF_NAMES)))])
    if r < 0.70:
        if rng.random() < 0.75:
            op = ROLL_OPS[int(rng.integers(len(ROLL_OPS)))]
            d = WINDOWS[int(rng.integers(len(WINDOWS)))]
            return ("roll", op, d, sample_height(rng, cap - 1))
        op = UN_OPS[int(rng.integers(len(UN_OPS)))]
        return ("un", op, sample_height(rng, cap - 1))
    op = BIN_OPS[int(rng.integers(len(BIN_OPS)))]
    d = WINDOWS[int(rng.integers(len(WINDOWS)))] if op == "CORR" else None
    return ("bin", op, d, sample_height(rng, cap - 1),
            sample_height(rng, cap - 1))


def _canon(node):
    """Tree normalization: canonical child ordering for commutative
    binary ops (ADD/MUL/CORR) -- the in-batch dedup fingerprint face."""
    t = node[0]
    if t == "leaf":
        return node
    if t == "roll":
        return ("roll", node[1], node[2], _canon(node[3]))
    if t == "un":
        return ("un", node[1], _canon(node[2]))
    a, b = _canon(node[3]), _canon(node[4])
    if node[1] in _COMMUTATIVE and FORMULA_STR(b) < FORMULA_STR(a):
        a, b = b, a
    return ("bin", node[1], node[2], a, b)


def fp_raw(node):
    return FORMULA_STR(node)


def fp_canon(node):
    return FORMULA_STR(_canon(node))


def _leaf_paths(node, prefix=()):
    t = node[0]
    if t == "leaf":
        return [prefix]
    if t == "roll":
        return _leaf_paths(node[3], prefix + (3,))
    if t == "un":
        return _leaf_paths(node[2], prefix + (2,))
    return (_leaf_paths(node[3], prefix + (3,))
            + _leaf_paths(node[4], prefix + (4,)))


def _replace_at(node, path, repl):
    if not path:
        return repl
    idx, rest = path[0], path[1:]
    t = node[0]
    if t == "roll":
        return ("roll", node[1], node[2], _replace_at(node[3], rest, repl))
    if t == "un":
        return ("un", node[1], _replace_at(node[2], rest, repl))
    if idx == 3:
        return ("bin", node[1], node[2], _replace_at(node[3], rest, repl),
                node[4])
    return ("bin", node[1], node[2], node[3],
            _replace_at(node[4], rest, repl))


def expand_leaf(rng, parent):
    """Single-node leaf expansion; replacement subtree height budget
    = 4 - parent_height (>=1) so every product respects the grammar
    height bound 3 (deep leaves degrade to leaf swaps, still a draw)."""
    h = NODE_DEPTH(parent)
    budget = max(1, GRAM_HEIGHT_MAX + 1 - h)
    paths = _leaf_paths(parent)
    k = int(rng.integers(len(paths)))
    repl = sample_height(rng, budget)
    return _replace_at(parent, paths[k], repl)


# ------------------------------------------------------------------ enrollment

def _enroll_draw(node, origin, seen_raw, seen_canon, consumed, ledger_text):
    """Draw-time T-84s3 + in-batch dedup. Returns (record, exclusion):
    exactly one is non-None. record carries fp faces + origin only; IC
    faces are attached by the caller (evaluation lives in the beam)."""
    raw, can = fp_raw(node), fp_canon(node)
    if raw in consumed or (ledger_text and raw in ledger_text):
        return None, {"formula": raw, "origin": origin,
                      "reason": "ledger_consumed_hit"}
    if can in seen_canon or raw in seen_raw:
        return None, {"formula": raw, "origin": origin,
                      "reason": "in_batch_dup"}
    seen_raw.add(raw)
    seen_canon.add(can)
    return {"formula": raw, "fp_canon": can, "origin": origin,
            "depth": NODE_DEPTH(node), "node": node}, None


# ------------------------------------------------------------------ IC faces

def _panel_dates(panel):
    rows = panel["census_rows"]
    return np.asarray(pd.to_datetime(
        np.asarray(list(panel["cal"]), dtype="datetime64[us]")))[rows]


def h1_face(panel, node, cal_us, min_cross, min_periods):
    """(block, n_dates) for the h=1 primary face; census faces verbatim."""
    rows = panel["census_rows"]
    F = EVALUATE(node, panel["leaves"])[rows, :]
    fwd = FWD_RET(panel["leaves"]["CLOSE"], 1)[rows, :]
    s, nser = IC_FACES(F, fwd, panel["elig"][rows, :], cal_us)
    keep = nser >= min_cross
    s = s[s.index.isin(nser.index[keep])]
    blk = t23.stats_block(s)
    ok = ("ic_ir" in blk and blk.get("n_periods", 0) >= min_periods)
    return blk, int(keep.sum()), ok


def _select_top(cands, n):
    """Deterministic top-n by |ICIR|: evaluable first, then by |ic_ir|
    desc, ties by formula string (zero hand-picking, reproducible)."""
    def key(i):
        c = cands[i]
        if not c.get("h1_ok"):
            return (1, 0.0, c["formula"])
        return (0, -abs(c["h1"]["ic_ir"]), c["formula"])
    return sorted(range(len(cands)), key=key)[:n]


def beam_draws(panel, seed_gen, consumed, ledger_text,
               min_cross=MIN_CROSS, min_periods=MIN_PERIODS):
    """The frozen W19 beam: R1 24 (height<=2) -> top-6; R2 24 leaf
    expansions -> top-6; R3 14 = R2 top-6 under the pinned split
    (3,3,3,3,1,1). Returns (lineage, enrolled, excluded).
    All rng streams derive from [seed_gen, round, parent, slot]."""
    cal_us = _panel_dates(panel)
    seen_raw, seen_canon = set(), set()
    lineage = {"r1": [], "r1_top6": [], "r2": [], "r2_top6": [],
               "r3": [], "r3_parents": []}
    enrolled, excluded = [], []

    def draw(node, origin):
        rec, excl = _enroll_draw(node, origin, seen_raw, seen_canon,
                                 consumed, ledger_text)
        if excl is not None:
            excluded.append(excl)
            lineage[origin[0].lower()].append(
                {"formula": excl["formula"], "excluded": excl["reason"]})
            return None
        blk, n_dates, ok = h1_face(panel, node, cal_us, min_cross,
                                   min_periods)
        rec.update({"h1": blk, "n_dates_h1": n_dates, "h1_ok": ok,
                    "skip": None if ok else "insufficient census periods "
                    "(h1)"})
        lineage[origin[0].lower()].append({"formula": rec["formula"],
                                           "ic_ir": blk.get("ic_ir"),
                                           "skip": rec["skip"]})
        enrolled.append(rec)
        return rec

    # R1: 24 random draws, height <= 2
    for i in range(R1_N):
        rng = np.random.default_rng([int(seed_gen), 1, int(i)])
        draw(sample_height(rng, R1_HEIGHT_CAP), ("R1", None, int(i)))
    r1_eval = [r for r in enrolled if r["origin"][0] == "R1" and r["h1_ok"]]
    r1_top = _select_top(r1_eval, TOP_BEAM)
    lineage["r1_top6"] = [r1_eval[i]["formula"] for i in r1_top]

    # R2: top-6 x 4 single-node leaf expansions (products height <= 3)
    for p, rec in enumerate([r1_eval[i] for i in r1_top]):
        for j in range(R2_N // TOP_BEAM):
            rng = np.random.default_rng([int(seed_gen), 2, int(p), int(j)])
            child = expand_leaf(rng, rec["node"])
            draw(child, ("R2", rec["formula"], int(j)))
    r2_eval = [r for r in enrolled if r["origin"][0] == "R2" and r["h1_ok"]]
    r2_top = _select_top(r2_eval, TOP_BEAM)
    lineage["r2_top6"] = [r2_eval[i]["formula"] for i in r2_top]

    # R3: W19 split pin -- R2 top-6 parents, per-parent slots per
    # R3_SPLIT (3,3,3,3,1,1); parents truncated in order if <6 evaluable
    parents = [r2_eval[i] for i in r2_top[:len(R3_SPLIT)]]
    lineage["r3_parents"] = [r["formula"] for r in parents]
    for p, rec in enumerate(parents):
        for j in range(R3_SPLIT[p]):
            rng = np.random.default_rng([int(seed_gen), 3, int(p), int(j)])
            child = expand_leaf(rng, rec["node"])
            draw(child, ("R3", rec["formula"], int(j)))
    return lineage, enrolled, excluded


def family_faces(panel, enrolled, seed_scrnull, b_nulls=B_NULLS,
                 min_cross=MIN_CROSS, min_periods=MIN_PERIODS,
                 min_pooled=MIN_POOLED_NULLS):
    """Family faces for the enrolled (kept) draws: h5 descriptive, M1 t
    gate, B=7 pooled permutation nulls, V1 family-level verdict."""
    rows = panel["census_rows"]
    cal_us = _panel_dates(panel)
    elig_c = panel["elig"][rows, :]
    pooled = []
    for idx, rec in enumerate(enrolled):
        node = rec["node"]
        recs_h = {"h1": rec["h1"]}
        fwd5 = FWD_RET(panel["leaves"]["CLOSE"], 5)[rows, :]
        F5 = EVALUATE(node, panel["leaves"])[rows, :]
        s5, n5 = IC_FACES(F5, fwd5, elig_c, cal_us)
        keep5 = n5 >= min_cross
        blk5 = t23.stats_block(s5[s5.index.isin(n5.index[keep5])])
        recs_h["h5"] = blk5
        rec["horizons"] = recs_h
        rec["n_dates_h5"] = int(keep5.sum())
        blk1 = rec["h1"]
        if rec["h1_ok"]:
            mean, sd, n = (blk1["ic_mean"], blk1["ic_std"],
                           blk1["n_periods"])
            t = (mean / sd) * float(np.sqrt(n)) if sd > 0 else None
            rec["m1_t_gate"] = sg.m1_t_value_gate(t)
            # B=7 within-day same-mask permutation nulls (census
            # construction, rng=[scrnull, idx, b] -- census stream law);
            # per-formula nulls are DESCRIPTIVE only (prereg sec.3)
            F1 = EVALUATE(node, panel["leaves"])[rows, :]
            fwd1 = FWD_RET(panel["leaves"]["CLOSE"], 1)[rows, :]
            eff = elig_c & np.isfinite(F1) & np.isfinite(fwd1)
            Fr = t23.rank_rows(eff, F1)
            Rr = t23.rank_rows(eff, fwd1)
            nser = pd.Series(eff.sum(axis=1), index=cal_us)
            per_null = []
            for b in range(b_nulls):
                rng = np.random.default_rng(
                    [int(seed_scrnull), int(idx), int(b)])
                Fp = PERMUTE(Fr, eff, rng)
                sb = t23.ic_from_ranks(Fp, Rr, cal_us)
                sb = sb[sb.index.isin(nser.index[nser >= min_cross])]
                blkb = t23.stats_block(sb)
                if "ic_ir" in blkb:
                    v = abs(blkb["ic_ir"])
                    pooled.append(v)
                    per_null.append(v)
            rec["null_abs_ir_p50"] = (round(float(np.quantile(
                per_null, 0.50)), 3) if per_null else None)
            rec["null_abs_ir_p95"] = (round(float(np.quantile(
                per_null, 0.95)), 3) if per_null else None)
        else:
            rec["m1_t_gate"] = sg.m1_t_value_gate(None)
            rec["null_abs_ir_p50"] = None
            rec["null_abs_ir_p95"] = None
    ok_recs = [r for r in enrolled if r.get("h1_ok")]
    obs_max = max((abs(r["h1"]["ic_ir"]) for r in ok_recs), default=None)
    n_pooled = len(pooled)
    null_p95 = (round(float(np.quantile(pooled, 0.95)), 3)
                if n_pooled >= min_pooled else None)
    holds = bool(obs_max is not None and null_p95 is not None
                 and obs_max > null_p95)
    abs_irs = sorted(abs(r["h1"]["ic_ir"]) for r in ok_recs)
    five_num = ([round(float(np.quantile(abs_irs, q)), 3)
                 for q in (0.0, 0.25, 0.5, 0.75, 1.0)]
                if abs_irs else None)
    for r in enrolled:
        r.pop("node", None)                    # trees out of the payload
    return {"records": enrolled, "n_ok": len(ok_recs),
            "n_pooled_nulls": n_pooled,
            "null_family_p95": null_p95,
            "observed_family_max_abs_icir": obs_max,
            "v1_holds": holds,
            "abs_icir_five_num": five_num}


# ------------------------------------------------------------- refusal receipt

def _refusal_receipt(reason, decomposition=None, extra=None):
    """W19 hard spec (prereg sec.3): EVERY rc2 refuse path lands a refusal
    receipt with the full decomposition face. Null fields = not derivable
    at that refuse point (beam not yet run / family not yet measured).
    Refuse is still zero-product zero-ledger-row: the receipt is a
    receipt, not a batch product."""
    dec = {k: None for k in REFUSAL_KEYS}
    if decomposition:
        dec.update(decomposition)
    out = {"refusal": reason, "batch": BATCH, "cutoff": CUTOFF_PIN,
           "prereg": PREREG, "decomposition": dec,
           "zero_product_files": True, "zero_ledger_rows": True,
           "decomposition_note": "null = not derivable at this refuse "
                                 "point (beam not yet run / family not "
                                 "yet measured)",
           "ts": dt.datetime.now().astimezone().isoformat(
               timespec="seconds")}
    if extra:
        out.update(extra)
    _dump(out, REFUSAL_RECEIPT)
    return out


# ------------------------------------------------------------------ run/probe

def _dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def _census_consumed_formulas():
    with open(CENSUS_PRODUCT, encoding="utf-8") as f:
        d = json.load(f)
    return {r["formula"] for r in d["census"]["formulas"]}, d


def cmd_probe():
    """Read-only fact face for the freeze window (zero burn, zero seed
    registration, zero ledger append). Receipt -> probe_latest.json."""
    out = {"probe": "PERPETUAL-N2-W19 runner fact probe (slice-2)",
           "zero_burn": True, "zero_ledger_append": True,
           "zero_seeds": True, "checks": {}}
    try:
        face = GATE_FACE()
        out["checks"]["panel_gate"] = {
            "ready": face["ready"], "cutoff": face["cutoff"],
            "per_files_on_disk": face["per_files_on_disk"],
            "disk_truth_override": face["disk_truth_override"],
            "ok": bool(face["ready"] and face["per_files_on_disk"]
                       >= PER_FILES_FLOOR
                       and str(face["cutoff"]) >= CUTOFF_PIN)}
        ok, bands = _bands_registered()
        out["checks"]["bands"] = {"face": bands, "freeze_gate_open": ok,
                                  "ok": True}          # posture disclosed
        consumed, census = _census_consumed_formulas()
        bad = sorted(k for k, v in CENSUS_ANCHORS.items()
                     if {"census_holds": census["census"]["census_holds"],
                         "observed_family_max_abs_icir":
                             census["census"]
                             ["observed_family_max_abs_icir"],
                         "null_family_p95":
                             census["census"]["null_family_p95"],
                         "n_unique_formulas":
                             census["census"]["n_unique_formulas"],
                         "k_formulas":
                             census["frozen_readout"]["k_formulas"],
                         "evidence_cutoff": census["evidence_cutoff"],
                         "ledger_total":
                             census["trials_ledger"]["total"]}.get(k) != v)
        out["checks"]["census_anchors"] = {
            "consumed_formula_n": len(consumed), "mismatches": bad,
            "ok": not bad}
        keys = sorted(sg.CLOSED_FAMILIES.keys())
        hits = [k for k in keys if any(
            w in k for w in ("alpha", "grammar", "formula"))]
        out["checks"]["closed_families"] = {
            "n_keys": len(keys), "family_key": FAMILY_KEY,
            "collides": FAMILY_KEY in sg.CLOSED_FAMILIES,
            "word_face_hits": hits,
            "ok": (FAMILY_KEY not in sg.CLOSED_FAMILIES and not hits)}
        with open(GRAMMAR_LEDGER, encoding="utf-8", errors="replace") as f:
            text = f.read()
        n_alpha = text.lower().count("alphagen")
        out["checks"]["grammar_ledger"] = {
            "alphagen_rows": n_alpha, "first_burn_confirmed": n_alpha == 0,
            "ok": n_alpha == 0}
        head = sg.ledger_head()
        out["checks"]["chain_head"] = {
            "total": head["total"],
            "monotone_ok": head["total"] >= CENSUS_ANCHORS["ledger_total"],
            "ok": head["total"] >= CENSUS_ANCHORS["ledger_total"]}
        with open(os.path.join(ROOT, PREREG), encoding="utf-8") as f:
            ptext = f.read()
        markers = ["PERPETUAL-N2-W19", FAMILY_KEY, "0.353", "0.139",
                   "null_family_p95", "K=62", "B=7", "300"]
        missing = [m for m in markers if m not in ptext]
        out["checks"]["prereg_markers"] = {
            "missing": missing, "sections": ptext.count("\u00a7"),
            "ok": (not missing) and ptext.count("\u00a7") >= 10}
        dp_ok, dp_face = False, None
        if os.path.exists(DRAFT_PROBE_RECEIPT):
            with open(DRAFT_PROBE_RECEIPT, encoding="utf-8") as f:
                d = json.load(f)
            faces = set((d.get("faces") or {}).keys())
            dp_face = sorted(faces)
            dp_ok = {"w18_attrition_replay", "w19_band_derive"} <= faces
        out["checks"]["draft_probe_receipt"] = {
            "path": "results/_r862bmb_n2w19_draft_probe.json",
            "faces": dp_face, "ok": dp_ok}
        out["checks"]["pin_slice_wiring"] = {
            "pin_end_param": "pin_end" in inspect.signature(
                t23.load_panel).parameters,
            "pin_cal_slice_fn": hasattr(t23, "_pin_cal_slice"),
            "cutoff_pin": CUTOFF_PIN,
            "legacy_default_untouched": True,
            "ok": ("pin_end" in inspect.signature(
                t23.load_panel).parameters
                and hasattr(t23, "_pin_cal_slice"))}
        out["checks"]["runner_freeze_conditions"] = {
            "c1_runner_selftest_freezegate_proof":
                "runner landed (this module); selftest L13 refuse-burn "
                "machine proof (rc2 + zero product + refusal receipt)",
            "c2_bands_derive_admit": "freeze window (r682 recipe + "
                                     "seed_admit_gate rc0)",
            "c3_criteria_shared_lib": "prereg sec.4 cites family-level "
                                      "line; freeze window verifies",
            "c4_d6_explicit": "prereg sec.1 D6 face; freeze window "
                              "verifies",
            "c5_meaning_gate_orders": "freeze window",
            "ok": True}
    except Exception as exc:                    # fail-closed
        out["verdict"] = "FAIL"
        out["fail_closed"] = repr(exc)
        _dump(out, PROBE_RECEIPT)
        print(json.dumps({"verdict": "FAIL", "fail_closed": repr(exc)}))
        return 2
    all_ok = all(c.get("ok") for c in out["checks"].values())
    out["verdict"] = "PASS" if all_ok else "FAIL"
    _dump(out, PROBE_RECEIPT)
    print(json.dumps({k: c.get("ok") for k, c in out["checks"].items()}))
    print("verdict:", out["verdict"])
    return 0 if all_ok else 2


def cmd_run():
    t0 = time.time()
    # probe-anchor same-face assertions (prereg sec.2 anchor 2 mandate)
    assert LOAD_PANEL is t23.load_panel and GATE_FACE is t23.gate_face
    assert EVALUATE is t23.evaluate and IC_FACES is t23._formula_ic_faces
    assert PERMUTE is t23._permute_ranks_within_mask
    assert FWD_RET is t23.fwd_ret and SYNTH_PANEL is t23._synth_panel

    ok, bands = _bands_registered()
    if not ok:
        _refusal_receipt("freeze_gate", None, {
            "bands": bands,
            "law": "three-band registration (r682 derive + seed_admit "
                   "gate) missing -> honest refuse, rc2"})
        print(json.dumps({
            "freeze_gate": "refuse", "zero_burn": True,
            "law": "three-band registration (r682 derive + seed_admit "
                   "gate) missing -> honest refuse, rc2",
            "bands": bands, "refusal_receipt": REFUSAL_RECEIPT,
            "prereg": PREREG}))
        return 2
    face = GATE_FACE()
    if (not face["ready"] or face["per_files_on_disk"] < PER_FILES_FLOOR
            or str(face["cutoff"]) < CUTOFF_PIN):
        _refusal_receipt("awaiting_panel", None, {"gate": face})
        print(json.dumps({"awaiting_panel": True, "gate": face,
                          "refusal_receipt": REFUSAL_RECEIPT}))
        return 2
    landed = sg.finalize_already_landed(BATCH, file_name=PRODUCT)
    if landed is not None:
        print(json.dumps({"already_landed": True,
                          "cutoff": CUTOFF_PIN, "landed_block": landed,
                          "action": "no-op (idempotent refuse)"}))
        return 0

    print(f"[w19] panel ready (cutoff {face['cutoff']}); loading panel "
          f"pin-sliced to <= {CUTOFF_PIN} ...")
    panel = LOAD_PANEL(pin_end=CUTOFF_PIN)     # W19 pin-slice panel law
    n_uni = len(panel["universe"])
    ns = panel["elig"][panel["census_rows"], :].sum(axis=1)
    panel_end = panel["cal"][-1]
    print(f"[w19] universe {n_uni}; census dates "
          f"{len(panel['census_rows'])}; eligible median "
          f"{float(np.median(ns)):.0f}; pinned window end {panel_end}")

    consumed, census = _census_consumed_formulas()
    with open(GRAMMAR_LEDGER, encoding="utf-8", errors="replace") as f:
        ledger_text = f.read()
    seed_gen = int(sg.SEED_REGISTRY[BAND_KEYS["gen"]])
    seed_scrnull = int(sg.SEED_REGISTRY[BAND_KEYS["scrnull"]])
    seed_unc = int(sg.SEED_REGISTRY[BAND_KEYS["unc"]])

    lineage, enrolled, excluded = beam_draws(panel, seed_gen, consumed,
                                             ledger_text)
    n_enrolled = len(enrolled)
    n_skip = sum(1 for r in enrolled if not r["h1_ok"])
    n_ok_so_far = n_enrolled - n_skip
    n_excl_ledger = sum(1 for e in excluded
                        if e["reason"] == "ledger_consumed_hit")
    n_excl_dup = sum(1 for e in excluded
                     if e["reason"] == "in_batch_dup")
    # W19 attrition guard = SKIP-ONLY face (W18 compound-face correction,
    # prereg sec.3): h1 skips > 10% of ENROLLED -> mechanism suspect;
    # T-84s3 / in-batch dup exclusions are legal grammar-space collisions
    # (census 25% precedent) -- disclosed, never a refuse reason.
    if not enrolled or n_skip > MAX_SKIP_FRAC * n_enrolled:
        _refusal_receipt("mechanism_suspect_skip_fraction", {
            "n_excluded_ledger_t84s3": n_excl_ledger,
            "n_excluded_in_batch_dup": n_excl_dup,
            "n_enrolled": n_enrolled, "n_h1_skip": n_skip,
            "n_ok": n_ok_so_far, "n_pooled": None}, {
            "law": f"h1 skips > {MAX_SKIP_FRAC:.0%} of enrolled "
                   f"(skip-only face; empirical base W18 2/50=4%)"})
        print(json.dumps({
            "mechanism_suspect": True, "n_skip": n_skip,
            "n_enrolled": n_enrolled,
            "law": f"h1 skips > {MAX_SKIP_FRAC:.0%} of enrolled "
                   f"(skip-only face)",
            "refusal_receipt": REFUSAL_RECEIPT}))
        return 2
    fam = family_faces(panel, enrolled, seed_scrnull)
    if fam["null_family_p95"] is None:
        _refusal_receipt("insufficient_pooled_nulls", {
            "n_excluded_ledger_t84s3": n_excl_ledger,
            "n_excluded_in_batch_dup": n_excl_dup,
            "n_enrolled": n_enrolled, "n_h1_skip": n_skip,
            "n_ok": fam["n_ok"], "n_pooled": fam["n_pooled_nulls"]}, {
            "law": f"pooled >= {MIN_POOLED_NULLS} sufficiency "
                   f"(NON-LOWERING: attrition prices the budget, "
                   f"never the line)"})
        print(json.dumps({
            "insufficient_pooled_nulls": True,
            "n_pooled": fam["n_pooled_nulls"],
            "law": f"pooled >= {MIN_POOLED_NULLS} sufficiency",
            "refusal_receipt": REFUSAL_RECEIPT}))
        return 2

    n_dup_ids = len(fam["records"]) - len({r["formula"] for r
                                           in fam["records"]})
    ledger = sg.append_ledger(BATCH, N_TRIALS, file_name=PRODUCT_REL,
                              evidence_cutoff=CUTOFF_PIN,
                              note="PERPETUAL-N2-W19 alphagen beam "
                                   f"feedback-search reference batch: "
                                   f"K={K_DRAWS} draws (R1/R2/R3="
                                   f"{R1_N}/{R2_N}/{R3_N}, R3 split "
                                   f"{R3_SPLIT}) + B={B_NULLS}/formula "
                                   "pooled permutation nulls "
                                   "(attrition-priced budget, W18 sec.8 "
                                   "lesson); zero engine runs "
                                   "(factor-reference face); family-level "
                                   "criteria V1 (T23 census calibration "
                                   "law)")
    payload = {
        **sg.cutoff_meta(CUTOFF_PIN),
        "probe": "PERPETUAL-N2-W19 beam feedback-search reference batch",
        "queue_row": QUEUE_ROW,
        "prereg": PREREG + " (posture at burn: FROZEN)",
        "family_key": FAMILY_KEY,
        "machine": "bm-b",
        "grammar": {
            "leaves": list(LEAF_NAMES), "roll_ops": list(ROLL_OPS),
            "un_ops": list(UN_OPS), "bin_ops": list(BIN_OPS),
            "windows": list(WINDOWS),
            "max_depth": GRAM_HEIGHT_MAX,
            "import_face": "scripts/t23_random_grammar_census.py "
                           "(zero rewrite; probe-anchor same-face "
                           "assertions enforced at run)",
        },
        "frozen_readout": {
            "k_draws": K_DRAWS, "rounds": {"R1": R1_N, "R2": R2_N,
                                            "R3": R3_N},
            "top_beam": TOP_BEAM,
            "r3_split": f"top-6 pinned split {R3_SPLIT}",
            "geometry_delta_vs_w18": "R3 16->14 only (exploration core "
                                     "R1/R2 verbatim; cut falls on the "
                                     "exploitation tail)",
            "b_nulls_per_formula": B_NULLS,
            "b_pricing": f"attrition-priced budget: ceil(300/(62*0.75))"
                         f"={B_NULLS} (W18 sec.8 lesson)",
            "sufficiency_line": MIN_POOLED_NULLS,
            "sufficiency_non_lowering_clause": "post-refuse downward "
                                                "line adjustment = "
                                                "threshold-gaming "
                                                "prohibition face; "
                                                "attrition prices the "
                                                "BUDGET never the LINE",
            "census_days": t23.CENSUS_DAYS, "min_cross": MIN_CROSS,
            "min_periods": MIN_PERIODS,
            "primary_face": "h=1 next-day close-to-close rank-IC ICIR "
                            "family max vs POOLED null p95",
            "descriptive_face": "h=5 decay + per-formula null p50/p95, "
                                 "not in verdict line",
            "verdict": "V1 = observed family max |ICIR| > pooled null "
                       "family p95 (>=300 pooled draws)",
        },
        "panel_face": {
            "cutoff": str(face["cutoff"]), "universe_n": n_uni,
            "per_files_on_disk": face["per_files_on_disk"],
            "census_dates": int(len(panel["census_rows"])),
            "eligible_median": int(float(np.median(ns))),
            "eligible_min": int(ns.min()), "eligible_max": int(ns.max()),
            "pin_end": CUTOFF_PIN,
            "pinned_window_end": str(panel_end),
            "pin_slice_law": "date-axis truncation to <= cutoff_pin "
                             "BEFORE the trailing-window take (t23."
                             "load_panel pin_end); elig listed/fresh "
                             "cumsum anchored to the census window "
                             "start; fwd-ret tail-NaN face identical "
                             "to the census instant; zero +/-N-day "
                             "drift on any later burn day",
        },
        "seeds": {
            "gen": [seed_gen, "rng=[gen,round,parent,slot]; R3 "
                    f"rng([gen,3,p,j]) j<SPLIT[p], SPLIT={R3_SPLIT}",
                    BAND_KEYS["gen"]],
            "scrnull": [seed_scrnull, "rng=[scrnull,idx,b] idx<"
                        f"{K_DRAWS} b<{B_NULLS}",
                        BAND_KEYS["scrnull"]],
            "unc": [seed_unc, "reserved berth, zero W19 core-mechanism "
                    "consumption (W15 unc/judge precedent; freeze-window "
                    "wiring) -- disclosed, not asserted",
                    BAND_KEYS["unc"]],
        },
        "beam_lineage": lineage,
        "dedup": {
            "n_excluded_ledger_t84s3": n_excl_ledger,
            "n_excl_in_batch_dup": n_excl_dup,
            "n_skip_h1": n_skip,
            "n_enrolled": n_enrolled,
            "ledger_face": "census 48 unique formula strings + full "
                           "TRIAL_GRAMMAR_LEDGER text scan (T-84s3)",
            "in_batch_face": "canonical tree fingerprint (commutative "
                             "ADD/MUL/CORR child ordering)",
            "exclusions_are_collisions_not_refusals": "T-84s3 hits and "
                                                       "in-batch dups "
                                                       "= legal grammar-"
                                                       "space collisions "
                                                       "(census 25% "
                                                       "precedent); "
                                                       "disclosed, "
                                                       "never a refuse "
                                                       "reason",
        },
        "family": fam,
        "leverage_face_d1": {
            "law": "descriptive only, NOT gating (prereg sec.4)",
            "census_random_family_max_abs_icir":
                CENSUS_ANCHORS["observed_family_max_abs_icir"],
            "census_random_null_family_p95":
                CENSUS_ANCHORS["null_family_p95"],
            "this_family_max_abs_icir": fam[
                "observed_family_max_abs_icir"],
            "leverage_positive_signal": bool(
                (fam["observed_family_max_abs_icir"] or 0.0)
                >= CENSUS_ANCHORS["observed_family_max_abs_icir"]),
            "k_parity_disclosure": f"K={K_DRAWS} vs census 64 = "
                                   f"{K_DRAWS/64:.1%} draw parity; ok "
                                   f"expectation 46.5 vs census 48 "
                                   f"unique -- same-band, equal-budget "
                                   f"NOT claimed (prereg sec.4)",
        },
        "riders": A158_LINEAGE_PRIOR,
        "trials_ledger": ledger,
        "audit": {
            "engine_runs": 0, "n_draws": N_TRIALS,
            "n_dup_ids": n_dup_ids,
            "attrition_decomposition": {       # full face on success too
                "n_excluded_ledger_t84s3": n_excl_ledger,
                "n_excluded_in_batch_dup": n_excl_dup,
                "n_enrolled": n_enrolled, "n_h1_skip": n_skip,
                "n_ok": fam["n_ok"], "n_pooled": fam["n_pooled_nulls"],
                "law": "W18 refused-burn zero-decomposition debt does "
                       "not repeat: the full decomposition lands on "
                       "every outcome face (refusal receipts AND "
                       "success payload)",
            },
            "is_split": "none -- 500-day reference window, census same "
                        "face (prereg sec.6 declaration)",
            "elapsed_sec": round(time.time() - t0, 1),
            "generated_at": dt.datetime.now().astimezone().isoformat(
                timespec="seconds"),
        },
    }
    _dump(payload, PRODUCT)
    print(json.dumps({
        "v1_holds": fam["v1_holds"],
        "observed_family_max_abs_icir": fam[
            "observed_family_max_abs_icir"],
        "null_family_p95_pooled": fam["null_family_p95"],
        "n_ok": fam["n_ok"], "n_pooled_nulls": fam["n_pooled_nulls"],
        "n_enrolled": n_enrolled,
        "n_excluded": len(excluded), "n_skip": n_skip,
        "n_draws": N_TRIALS, "out": PRODUCT,
        "elapsed_sec": payload["audit"]["elapsed_sec"],
    }, indent=1))
    return 0


# ------------------------------------------------------------------ selftest

def selftest():
    import shutil
    import tempfile
    ok = []

    def check(name, cond):
        ok.append((name, bool(cond)))
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")

    # L1 import-face identity (probe-anchor same-face mandate)
    import pa_lhb_ic
    check("L1a IC machinery import-face identity (census objects)",
          LOAD_PANEL is t23.load_panel and GATE_FACE is t23.gate_face
          and EVALUATE is t23.evaluate
          and IC_FACES is t23._formula_ic_faces
          and PERMUTE is t23._permute_ranks_within_mask
          and FWD_RET is pa_lhb_ic.fwd_ret
          and SYNTH_PANEL is t23._synth_panel)
    check("L1b grammar constants parity (census frozen face)",
          LEAF_NAMES == t23.LEAF_NAMES and ROLL_OPS == t23.ROLL_OPS
          and UN_OPS == t23.UN_OPS and BIN_OPS == t23.BIN_OPS
          and WINDOWS == t23.WINDOWS and GRAM_HEIGHT_MAX == 3
          and MIN_CROSS == 100 and MIN_PERIODS == 30)
    check("L1c W19 parameter checklist (r836 clone law)",
          BATCH == "PERPETUAL-N2-W19" and K_DRAWS == 62
          and (R1_N, R2_N, R3_N) == (24, 24, 14)
          and sum((R1_N, R2_N, R3_N)) == K_DRAWS
          and R3_SPLIT == (3, 3, 3, 3, 1, 1)
          and sum(R3_SPLIT) == R3_N and len(R3_SPLIT) == TOP_BEAM
          and B_NULLS == 7 and N_TRIALS == 496
          and MIN_POOLED_NULLS == 300 and MAX_SKIP_FRAC == 0.10
          and BAND_KEYS["gen"] == "perpetual_n2_w19_gen"
          and BAND_KEYS["scrnull"] == "perpetual_n2_w19_scrnull"
          and BAND_KEYS["unc"] == "perpetual_n2_w19_unc"
          and PRODUCT_REL == "results/alphagen_w19/W19-2026-10-09.json"
          and CUTOFF_PIN == "2026-10-09")

    # L2 sampler bounds + legality
    rng = np.random.default_rng(11)
    draws2 = [sample_height(rng, 2) for _ in range(200)]
    draws3 = [sample_height(rng, 3) for _ in range(200)]

    def legal(node):
        t = node[0]
        if t == "leaf":
            return node[1] in LEAF_NAMES
        if t == "roll":
            return (node[1] in ROLL_OPS and node[2] in WINDOWS
                    and legal(node[3]))
        if t == "un":
            return node[1] in UN_OPS and legal(node[2])
        return (node[1] in BIN_OPS
                and (node[2] in WINDOWS if node[1] == "CORR" else True)
                and legal(node[3]) and legal(node[4]))
    check("L2a cap-2 draws height<=2, all nodes legal",
          all(NODE_DEPTH(n) <= 2 for n in draws2)
          and all(legal(n) for n in draws2))
    check("L2b cap-3 draws height<=3, all nodes legal",
          all(NODE_DEPTH(n) <= 3 for n in draws3)
          and all(legal(n) for n in draws3))

    # L3 canonicalization (tree normalization face)
    a = ("bin", "ADD", None, ("leaf", "CLOSE"), ("leaf", "OPEN"))
    b = ("bin", "ADD", None, ("leaf", "OPEN"), ("leaf", "CLOSE"))
    s1 = ("bin", "SUB", None, ("leaf", "CLOSE"), ("leaf", "OPEN"))
    s2 = ("bin", "SUB", None, ("leaf", "OPEN"), ("leaf", "CLOSE"))
    check("L3 commutative fold (ADD) + non-fold (SUB)",
          fp_canon(a) == fp_canon(b) and fp_canon(s1) != fp_canon(s2))

    # L4 expansion bounds
    rng = np.random.default_rng(22)
    parents = [n for n in draws3 if NODE_DEPTH(n) >= 2][:40] or draws3[:40]
    prods = [expand_leaf(np.random.default_rng([7, i]), p)
             for i, p in enumerate(parents)]
    check("L4 leaf expansion products respect grammar height<=3",
          all(NODE_DEPTH(c) <= 3 for c in prods))

    # L5 enrollment dedup faces (draw-time T-84s3 + in-batch)
    seen_r, seen_c = set(), set()
    r1, e1 = _enroll_draw(a, ("R1", None, 0), seen_r, seen_c, set(), "")
    r2, e2 = _enroll_draw(b, ("R1", None, 1), seen_r, seen_c, set(), "")
    r3, e3 = _enroll_draw(s1, ("R1", None, 2), seen_r, seen_c,
                          {"SUB(CLOSE,OPEN)"}, "")
    r4, e4 = _enroll_draw(s2, ("R1", None, 3), seen_r, seen_c, set(), "")
    check("L5a novel kept + in-batch canon dup + consumed hit all "
          "classified",
          r1 is not None and e1 is None
          and r2 is None and e2["reason"] == "in_batch_dup"
          and r3 is None and e3["reason"] == "ledger_consumed_hit"
          and r4 is not None and e4 is None)
    vwap_ma = ("roll", "MA", 5, ("leaf", "VWAP"))
    _, e4 = _enroll_draw(vwap_ma, ("R1", None, 3), seen_r, seen_c,
                         set(), "later row: MA(VWAP,5) consumed")
    check("L5b ledger text-scan belt excludes (T-84s3 belt face)",
          e4 is not None and e4["reason"] == "ledger_consumed_hit")

    # L6 beam determinism + structure on a synthetic noise panel
    p_noise = SYNTH_PANEL(seed=777, signal=0.0)
    lin1, enr1, exc1 = beam_draws(p_noise, 999, set(), "",
                                  min_cross=10, min_periods=30)
    lin2, enr2, exc2 = beam_draws(p_noise, 999, set(), "",
                                  min_cross=10, min_periods=30)
    check("L6a beam deterministic (same seeds -> identical lineage)",
          json.dumps(lin1, sort_keys=True)
          == json.dumps(lin2, sort_keys=True)
          and [r["formula"] for r in enr1] == [r["formula"]
                                               for r in enr2])
    n_r1 = len(lin1["r1"])
    n_r2 = len(lin1["r2"])
    n_r3 = len(lin1["r3"])
    check("L6b structure counts 24/24/14 (draw envelope K=62)",
          n_r1 == R1_N and n_r2 == R2_N and n_r3 == R3_N
          and (n_r1 + n_r2 + n_r3) == K_DRAWS)
    r3_origins = ([(r["origin"][1], r["origin"][2])
                   for r in enr1 if r["origin"][0] == "R3"]
                  + [(e["origin"][1], e["origin"][2])
                     for e in exc1 if e["origin"][0] == "R3"])
    slots_by_parent = {}
    for pf, j in r3_origins:
        slots_by_parent.setdefault(pf, []).append(j)
    n_par = len(lin1["r3_parents"])
    exp_split = list(R3_SPLIT[:n_par])
    check("L6c R2 parents = R1 top-6, R3 parents = R2 top-6 under the "
          "pinned split (3,3,3,3,1,1)",
          len(lin1["r1_top6"]) == TOP_BEAM
          and len(lin1["r2_top6"]) == TOP_BEAM
          and all(f in lin1["r1_top6"] for f in
                  [r["origin"][1] for r in enr1
                   if r["origin"][0] == "R2"])
          and all(f in lin1["r2_top6"] for f, _ in r3_origins)
          and [len(slots_by_parent.get(p, []))
               for p in lin1["r3_parents"]] == exp_split)
    check("L6d enrolled+excluded == 62 (no redraw law)",
          len(enr1) + len(exc1) == K_DRAWS)

    # L7 family faces on noise panel: machinery well-formed
    fam_n = family_faces(p_noise, enr1, 8888, min_cross=10,
                         min_periods=30, min_pooled=10)
    check("L7a noise family machinery well-formed",
          fam_n["n_ok"] >= 0 and isinstance(fam_n["v1_holds"], bool)
          and fam_n["null_family_p95"] is not None
          and fam_n["abs_icir_five_num"] is not None
          and all("m1_t_gate" in r for r in fam_n["records"]))
    fam_n2 = family_faces(p_noise, enr2, 8888, min_cross=10,
                          min_periods=30, min_pooled=10)
    check("L7b family faces deterministic",
          json.dumps(fam_n, sort_keys=True)
          == json.dumps(fam_n2, sort_keys=True))
    check("L7c pooled null count == B(7) * n_ok (pooled family law)",
          fam_n["n_pooled_nulls"] == B_NULLS * fam_n["n_ok"])
    fps = [r["formula"] for r in fam_n["records"]]
    check("L7d dup probe n_dup_ids=0 (r482 law)",
          len(fps) == len(set(fps)))

    # L8 V1 on an injected-signal synthetic panel (census s4c kin)
    p_sig = SYNTH_PANEL(seed=778, signal=0.9)
    sig_nodes = [("leaf", "RET"),
                 ("roll", "MA", 5, ("leaf", "RET")),
                 ("bin", "SUB", None, ("leaf", "CLOSE"),
                  ("roll", "MA", 5, ("leaf", "CLOSE")))]
    sig_recs = []
    for i, n in enumerate(sig_nodes):
        blk, nd, okh = h1_face(p_sig, n, _panel_dates(p_sig), 10, 30)
        sig_recs.append({"formula": fp_raw(n), "fp_canon": fp_canon(n),
                         "origin": ("S", None, i),
                         "depth": NODE_DEPTH(n), "node": n,
                         "h1": blk, "n_dates_h1": nd, "h1_ok": okh,
                         "skip": None if okh else "insufficient"})
    fam_s = family_faces(p_sig, sig_recs, 8888, min_cross=10,
                         min_periods=30, min_pooled=6)
    check("L8 injected reversal signal -> V1 holds (family max > "
          "pooled p95)",
          fam_s["v1_holds"] is True
          and fam_s["observed_family_max_abs_icir"] > 0.25
          and fam_s["observed_family_max_abs_icir"]
          > fam_s["null_family_p95"])

    # L9 M1 t face
    s = pd.Series(np.random.default_rng(5).standard_normal(200) * 0.01
                  + 0.004)
    blk = t23.stats_block(s)
    t_manual = blk["ic_mean"] / blk["ic_std"] * float(
        np.sqrt(blk["n_periods"]))
    g_pass = sg.m1_t_value_gate(t_manual)
    g_none = sg.m1_t_value_gate(None)
    check("L9 M1 t = mean/std*sqrt(n) + gate pass / missing_input",
          abs(g_pass["t"] - round(t_manual, 6)) < 1e-9
          and g_pass["pass"] is True and g_pass["hurdle"] >= 3.0
          and g_none["missing_input"] is True
          and g_none["pass"] is False)

    # L10 freeze-gate posture (W15 L8 posture-aware law: both directions)
    live_ok, _ = _bands_registered()
    saved = {k: sg.SEED_REGISTRY.get(k) for k in BAND_KEYS.values()}
    try:
        for k in saved:
            sg.SEED_REGISTRY.pop(k, None)
        sim_bad, _ = _bands_registered()
        for i, (nm, key) in enumerate(BAND_KEYS.items()):
            sg.SEED_REGISTRY[key] = 900_000 + 500 * i
        sim_ok, sim_face = _bands_registered()
    finally:
        for k, v in saved.items():
            if v is None:
                sg.SEED_REGISTRY.pop(k, None)
            else:
                sg.SEED_REGISTRY[k] = v
        for stray in ("gen", "scrnull", "unc"):
            sg.SEED_REGISTRY.pop(stray, None)   # hygiene: no berth under
            # a short name ever (L10 sim never writes one after this fix;
            # pop keeps the sim hermetic even if regressed)
    check("L10 freeze-gate both directions (unregistered -> refuse; "
          "registered -> open; live posture disclosed honestly)",
          sim_bad is False and sim_ok is True
          and sim_face["unc"]["registered"] is True
          and isinstance(live_ok, bool))

    # L11 payload law
    check("L11a cutoff_meta top-level pin + product path pin",
          sg.cutoff_meta(CUTOFF_PIN)
          == {"evidence_cutoff": CUTOFF_PIN}
          and PRODUCT_REL == "results/alphagen_w19/W19-2026-10-09.json"
          and REFUSAL_RECEIPT.endswith("refusal-2026-10-09.json"))
    led = sg.append_ledger("W19_SELFTEST_DUMMY", N_TRIALS, file_name=None,
                           prev_total=100)
    check("L11b ledger block hermetic prev override + budget law",
          led["batch_trials"] == N_TRIALS == 496
          and led["prev_total"] == 100 and led["total"] == 596
          and N_TRIALS == K_DRAWS + K_DRAWS * B_NULLS <= 500
          and K_DRAWS * B_NULLS == 434
          and callable(sg.finalize_already_landed))
    check("L11c panel-gate pure face (disk-truth override law)",
          bool(t23.ua._disk_truth_override(
              True, {"per_files": 5217}, 0)) is True
          and bool(t23.ua._disk_truth_override(
              True, {"per_files": 5217}, 5217)) is False)

    # L12 pin-slice panel law (W19 prereg sec.2): pinned window invariant
    # to panel advance; load_panel carries the pin_end parameterization
    # with the legacy default untouched
    cal_all = [d.strftime("%Y-%m-%d") for d in
               pd.bdate_range("2025-01-01", periods=300)]
    win = t23._pin_cal_slice(cal_all, "2025-10-15", 40)
    adv = cal_all + [d.strftime("%Y-%m-%d") for d in
                     pd.bdate_range("2025-12-01", periods=10)]
    win_adv = t23._pin_cal_slice(adv, "2025-10-15", 40)
    legacy = t23._pin_cal_slice(cal_all, None, 40)
    check("L12a pin window invariant to panel advance (zero drift)",
          win == win_adv and len(win) == 40
          and win[-1] == "2025-10-15"
          and not any(d > "2025-10-15" for d in win))
    check("L12b pin_end=None legacy trailing-window behavior verbatim",
          legacy == cal_all[-40:])
    check("L12c load_panel pin_end wiring present",
          "pin_end" in inspect.signature(t23.load_panel).parameters)

    # L13 FREEZE-GATE refuse-burn machine proof (prereg sec.6 leg):
    # three bands absent -> cmd_run rc2 + ZERO batch-product writes +
    # refusal receipt landed with the null decomposition face. Hermetic:
    # output faces redirected to a system tempdir; no repo file touched;
    # freeze-gate branch sits before the panel gate so no data read.
    g_out, g_prod, g_ref = OUT_DIR, PRODUCT, REFUSAL_RECEIPT
    tmp = tempfile.mkdtemp(prefix="w19_fg_proof_")
    try:
        globals()["OUT_DIR"] = tmp
        globals()["PRODUCT"] = os.path.join(tmp, "W19-2026-10-09.json")
        globals()["REFUSAL_RECEIPT"] = os.path.join(
            tmp, "refusal-2026-10-09.json")
        for k in saved:                      # L10 already restored live;
            sg.SEED_REGISTRY.pop(k, None)    # ensure absent for the proof
        rc = cmd_run()
        prod_exists = os.path.exists(PRODUCT)
        with open(REFUSAL_RECEIPT, encoding="utf-8") as f:
            ref = json.load(f)
    finally:
        for k, v in saved.items():
            if v is None:
                sg.SEED_REGISTRY.pop(k, None)
            else:
                sg.SEED_REGISTRY[k] = v
        globals()["OUT_DIR"], globals()["PRODUCT"] = g_out, g_prod
        globals()["REFUSAL_RECEIPT"] = g_ref
        shutil.rmtree(tmp, ignore_errors=True)
    check("L13 FREEZE-GATE refuse machine-proof: rc2 + zero product "
          "writes + refusal receipt with full decomposition face",
          rc == 2 and not prod_exists
          and ref["refusal"] == "freeze_gate"
          and ref["zero_product_files"] is True
          and ref["zero_ledger_rows"] is True
          and all(ref["decomposition"][k] is None
                  for k in REFUSAL_KEYS))

    n_pass = sum(1 for _, c in ok if c)
    print(f"selftest: {n_pass}/{len(ok)} PASS")
    return 0 if n_pass == len(ok) else 1


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "probe":
        return cmd_probe()
    if cmd == "run":
        return cmd_run()
    print("usage: run | probe | selftest")
    return 1


if __name__ == "__main__":
    sys.exit(main())
