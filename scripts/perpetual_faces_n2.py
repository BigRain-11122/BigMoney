"""PERPETUAL_FACES N2 random-subspace furnace, wave W15 runner --
T-133 s2 canon drafting-order face 3 (CEO O-2026-09-30-2340).

Law: research/PERPETUAL_FACES.md v1.0 sec.2 N2 row + sec.4 drafting
order (N1-W2 -> N3-R1 -> N2-W15 -> N4-B1; FROZEN bm-b r484).
Wave prereg: research/PERPETUAL_N2_W15_PREREG.md (DRAFT until the
run/screen/finalize legs land + freeze commit; R99 zero-burn-before-
freeze, R250 one-step -- seeds registered only at the freeze commit).

N2 mechanism (canon sec.2 N2 row): random-SUBSPACE combination
sampling over the W1-W14 frozen grammar full library.  The W14 trial
labor draw samples each of the 14 overlay axes INDEPENDENTLY from its
full domain (none-or-active), so mixed-overlay combinations live in
the sparse tail.  The W15 subspace layer makes combination space the
MAJORITY of the sample: per draw, first draw k_active ~ U{1..14} and
a uniform random ACTIVE SUBSET of the overlay axes (STOP/GATE/VOL/
YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI/CNT), pin every
inactive axis to "none", then sample active-axis values from their
NON-NONE domains + base R/X/S/T + per-family Sobol param box
(mass_trial_w1 paradigm, tl14 consumption order verbatim).

Import-face reuse law (prereg sec.6; W13/W14 chain precedent):
  grammar/axes = trial_labor_w14.build_grammar_w14 (frozen 18-tuple
                library, sha16 a231bf10940e7878; chain tl1..tl14)
  engine face = trial_labor_w14.run_candidate_curve_w14 (zero re-impl)
  panel load  = tl1._load_leg("L") + tl1.v3_state_series (same-source)
  Sobol box   = tl14 draw_candidate_sobol_w14 mapping pattern
  pool claim  = perpetual_faces_n1._pool_claim canon (r496 three-call)
N2 IS a candidate funnel face (canon sec.2 note): survivors of the
screen stage feed the judge stage (separate per-stage freeze per
mass_trial_w1 precedent) -- D6 same-family gate + T-84s3 dedup apply
to enrolled candidates; ledger appends at each stage finalize with
actual cell counts only.

Subcommands (slice-1 + slice-2 legs; burns gated on the freeze commit):
  probe        2 out-of-band subspace draws (seeds 95_004, ledger +0,
               zero registry, design face only) through the real
               tl14 engine face -> results/perpetual_faces/
               _n2_w15_probe.json (N1 95_002/95_003 probe precedent)
  status       read-only inventory (grammar, family slots, subspace
               size, shard/product presence)
  generate     slice-2: per-slot subspace streams round-robin (A 500 /
               B 4,500 raw, W13 same split) -> tl14 28-source
               exclusion real-read -> T-84s3 fingerprint dedup on the
               effective signal face -> n2_w15_candidates.json
               (FREEZE-GATED: bands registered in SEED_REGISTRY, R99/
               R250; candidates file present = same-grammar rerun
               FORBIDDEN)
  screen-prep  slice-2: G-PANEL + G-VOL..G-CNT raw-full-history gates +
               G-ANCHOR replay parity + G-CENSUS leg-L starts/passive
               precompute -> n2_w15_prep_state.json (fail-closed)
  run          slice-2: pool shard executor (screen cells incl. K=200
               scrnull nulls; checkpoint jsonl append-per-cell; r496
               three-call pool claim on verified done)
  screen-finalize  slice-2: id-level dup probe (r482) + null-p95
               survival line (tl2._finalize_math) + k_active segmented
               disclosure + ledger append PERPETUAL-N2-W15-SCREEN
  finalize     slice-2: wave closeout (pool shard closure verify + wave
               results audit summary; ledger already appended at
               screen-finalize per prereg sec.3 -- double append
               refused pit-95)
  selftest     hermetic offline legs (zero network, zero engine,
               zero repo data files; slice-2 legs cover the real
               freeze-gate/exclusion/dedup/tiling/scanner/beat6m/null-
               draw paths with synthetic fixtures, r494 real-path law)

Seed bands (law sec.4 N2/N4 row: N2 packs from 30_000+ outside every
registered band; lfc_p1_screen=30_000 in use -> first free window):
  PROPOSED (registered only at the freeze commit):
    perpetual_n2_w15_gen     = 541_500   (Sobol + axis stream)
    perpetual_n2_w15_scrnull = 542_000   (screen null family)
    perpetual_n2_w15_unc     = 542_500   (uncertainty resample)
  Probe seeds 95_004/95_005 = out-of-band design probes (N1 95_002/
  95_003 precedent; never registered, never in any batch ledger).
"""
import argparse
import csv
import hashlib
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import trial_labor_w1 as tl1  # noqa: E402
import trial_labor_w2 as tl2  # noqa: E402
import trial_labor_w3 as tl3  # noqa: E402
import trial_labor_w4 as tl4  # noqa: E402
import trial_labor_w5 as tl5  # noqa: E402
import trial_labor_w6 as tl6  # noqa: E402
import trial_labor_w7 as tl7  # noqa: E402
import trial_labor_w8 as tl8  # noqa: E402
import trial_labor_w14 as tl14  # noqa: E402  (grammar + engine face)
import mass_trial_w1 as mtw1    # noqa: E402  (judge grid import-face:
                                # _collapse_survivors/_dual_nulls/
                                # _yearly_returns -- sec.9 zero-rewrite)
import science_gates as sg  # noqa: E402

WAVE = 15
BATCH = "PERPETUAL-N2-W15"
LAW_REF = ("research/PERPETUAL_FACES.md v1.0 sec.2 N2 row + sec.4 "
           "drafting order (T-133 s2, O-2026-09-30-2340)")
PREREG = ("research/PERPETUAL_N2_W15_PREREG.md (wave-level; DRAFT "
          "until runner legs land + freeze commit; R99/R250)")
CUTOFF = tl14.CUTOFF                      # 2026-09-22 same-window law
PROBE_SEED = 95_004                       # out-of-band (N1 95_002 law)
# --- bands (freeze-time registration; disjoint leg machine-checks
#     these against SEED_REGISTRY + live N1_BANDS + N3 berth) ---
# r492 bm-c slice-3 freeze window: the prereg sec.5 original pick
# 31_000/31_500/32_000 was REFUSED by the band gate -- all three bands
# fall inside N1 W8 A 30_100..32_099 (unc also straddles W9 A
# 32_100..34_099); the slice-1 L4 N1 snapshot was a stale W2..W7 hand
# list that hid W8+. Forced skip per band-law sec.4 (W12/W13/W109
# precedent; NOT a re-pick -- R250: these berths were never assigned,
# zero cells burned). Re-derived placement = r682 ladder-horizon law
# (lower bound >= A_head_end + 130 waves x 2,000; A head 281,003 at
# scan time) -> X=541,500; ADMIT receipt
# results/_r492bmc_n2_band_gate.txt (4 refusal facts + 421 reserved
# intervals + trio CLEAN).
BAND_GEN = 541_500
BAND_SCRNULL = 542_000
BAND_UNC = 542_500
BAND_WIDTH = 499                          # 541_500..541_999 etc.
FROZEN_GRAMMAR_SHA16 = "a231bf10940e7878"  # tl14 build, pinned

OUT_DIR = os.path.join(tl1.PATHS.results_dir, "perpetual_faces")
PROBE_OUT = os.path.join(OUT_DIR, "_n2_w15_probe.json")

# --- slice-2 batch faces (prereg sec.0/sec.3) --------------------------
RES_DIR = os.path.join(tl1.PATHS.results_dir, "n2_w15")
CANDIDATES_FILE = os.path.join(RES_DIR, "n2_w15_candidates.json")
PREP_FILE = os.path.join(RES_DIR, "n2_w15_prep_state.json")
SCREEN_FILE = os.path.join(RES_DIR, "n2_w15_screen.json")
SCREEN_CSV = os.path.join(RES_DIR, "n2_w15_screen_cells.csv")
WAVE_RESULTS = os.path.join(RES_DIR, "n2_w15_wave_results.json")
CKPT_DIR = os.path.join(RES_DIR, "checkpoint")
BATCH_SCREEN = "PERPETUAL-N2-W15-SCREEN"
N_A = 500                     # raw draws family A (W13 same split)
N_B = 4500                    # raw draws family B (raw 5,000 total)
K_NULLS = 200                 # screen-null family K (prereg sec.3)
NSHARDS = 12                  # prereg sec.0 compute budget: 12 shards
SEED_GEN = BAND_GEN            # 541_500 (registered at freeze commit)
SEED_NULL = BAND_SCRNULL       # 542_000
SEED_UNC = BAND_UNC            # 542_500
W6M = tl2.W6M                  # 126 td, frozen 6m window (tl2 face)

# --- s3 judge face (prereg sec.9/sec.9.1; berth perpetual_n2_w15_judge
#     registered at the sec.9.1 freeze commit per R250 one-step law;
#     grid isomorphic to mass_trial_w1 sec.9.1: p5c FROZEN_CENSUS legs
#     L/D x windows {6m,12m,24m} x cost {x1 engine default, x2
#     CostPatch(2.0) t22 Erratum-1 multiplier law} x regime 3-way
#     segments + dual nulls B=2000 block=20 circular + P=2000
#     sign-flip, rng=[seed, cell_idx], resample faces only) ---
JUDGE_BATCH = "PERPETUAL-N2-W15-JUDGE"
JUDGE_BER = "perpetual_n2_w15_judge"     # SEED_REGISTRY key
JUDGE_STATE_FILE = os.path.join(RES_DIR, "n2_w15_judge_state.json")
JUDGE_OUT_FILE = os.path.join(RES_DIR, "n2_w15_judge.json")
JUDGE_REFINALIZE_ENV = "PERPETUAL_N2_W15_JUDGE_REFINALIZE"
JUDGE_COLLAPSE_LINE = 0.999              # sec.9 entry dedup line
JUDGE_SHARDS_DEFAULT = 12                # sec.9.1 freeze: pool shards
D6_REJECT_LINE = 0.7                     # sec.1/sec.9 D6 vs REG6
REG6 = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
        "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")
D6_MIN_OVERLAP = 60                      # honest-alignment floor

# --- the 14 overlay axes of the frozen 18-tuple (indices 4..17),
#     module-sourced verbatim (import-face; never hand-copied).  Each
#     entry = (axis name, module constant).  Order = the tl14 frozen
#     consumption order STOP..CNT verbatim. ---
OVERLAY_AXES = (
    ("stop", tl2.AXIS_STOP),
    ("gate", tl3.AXIS_GATE),
    ("vol", tl4.AXIS_VOL),
    ("yang", tl5.AXIS_YANG),
    ("vconf", tl6.AXIS_VCONF),
    ("streak", tl7.AXIS_STREAK),
    ("tstate", tl14.AXIS_TSTATE),
    ("amp", tl14.AXIS_AMP),
    ("mom", tl14.AXIS_MOM),
    ("std", tl14.AXIS_STD),
    ("rsqr", tl14.AXIS_RSQR),
    ("sumn", tl14.AXIS_SUMN),
    ("resi", tl14.AXIS_RESI),
    ("cnt", tl14.AXIS_CNT),
)
OVERLAY_NON_NONE = tuple([v for v in ax if v != "none"]
                         for _, ax in OVERLAY_AXES)
N_OVERLAY = len(OVERLAY_AXES)              # 14


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S") + time.strftime("%z")[:3] \
        + ":" + time.strftime("%z")[3:]


def _machine_id() -> str:
    try:
        return json.load(open(os.path.join(
            tl1.PATHS.root, "fleet", "machine.json"),
            encoding="utf-8")).get("machine_id", "unknown")
    except Exception:
        return "unknown"


# --- pool harvest handshake (r496 canon, three-call-point law; N1
#     perpetual_faces_n1._pool_claim verbatim face) --------------------------
def _claim_payload(detail: str) -> dict:
    """Pure payload builder for the r496 pool-claim face (slice-1
    canon keys; factored for hermetic selftest coverage)."""
    now = _now_iso()
    return {"machine_id": _machine_id(), "state": "closed",
            "pid": os.getpid(), "heartbeat": now, "outcome": "ok",
            "exit_code": 0, "closed_at": now, "result_ref": detail}


def _pool_claim(entry_id: str, shard_key: str, detail: str) -> None:
    """Worker-side half (slice-2 run legs call this on verified done;
    identical face to the N1 canon so the launcher harvest flip lands
    the shard done)."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = os.path.join(root, "results", "pool_claims",
                     entry_id.replace("/", "_"))
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, f"{shard_key}.{_machine_id()}.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(_claim_payload(detail), f, ensure_ascii=False, indent=1)
    print(f"pool claim closed: {os.path.basename(fp)}", flush=True)


def entry_shard_of(shard: int, nshards: int) -> tuple:
    """Pool entry/shard identity (T-133 s2 registration face:
    PERPETUAL-N2-W15-SHARD-<i> / n2w15-<i>of<N>)."""
    return (f"PERPETUAL-N2-W15-SHARD-{shard}",
            f"n2w15-{shard}of{nshards}")


# ------------------------------------------------------------- grammar face
def load_grammar() -> dict:
    """Frozen 18-tuple library via tl14 build (pure compute, hermetic;
    sha pinned)."""
    g = tl14.build_grammar_w14()
    sha16 = str(g.get("grammar_sha256", ""))[:16]
    assert sha16 == FROZEN_GRAMMAR_SHA16, \
        f"grammar sha drift {sha16} != pinned {FROZEN_GRAMMAR_SHA16}"
    return g


# ---------------------------------------------------- subspace draw layer
def draw_candidate_subspace_w15(grammar, family, slot, n_draws, seed):
    """Yield (draw_idx, cand) with the W15 random-subspace overlay
    (prereg sec.3 draft face).

    Per draw, frozen consumption order (single default_rng stream,
    seed=[seed+fam_idx, 7919] -- tl14 axis-stream convention):
      1. k_active  ~ U{1..14}        (subspace cardinality)
      2. subset    ~ U-choose(14, k) (which overlay axes are ACTIVE,
                                       sorted, no replacement)
      3. base R/X/S/T axis indices   (always sampled, full domains)
      4. active-axis value indices   (NON-NONE domains, in OVERLAY_AXES
                                       order; inactive axes pinned
                                       "none")
    Params: per-family Sobol box (scrambled, seed=seed+fam_idx) mapped
    over the family's multi-valued domains (tl14 mapping verbatim).
    Deterministic, zero band use (probe/design seeds excluded from the
    batch face by construction)."""
    from scipy.stats import qmc
    fam_idx = slot if family == "A" else 6 + slot   # A 0-5, B 6+ (tl14)
    spec = grammar["families"][family][slot]
    mk = f"{spec['module']}.{spec['fn']}"
    dom = grammar["value_domains"][mk]
    names = sorted(nm for nm, vs in dom.items() if len(vs) > 1)
    sob = qmc.Sobol(max(1, len(names)), scramble=True,
                    seed=seed + fam_idx)
    box = sob.random(n_draws)
    rng = np.random.default_rng([seed + fam_idx, 7919])
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
        k_active = int(rng.integers(1, N_OVERLAY + 1))
        active = sorted(rng.choice(N_OVERLAY, size=k_active,
                                   replace=False).tolist())
        r_ = int(rng.integers(0, len(tl1.AXIS_FILTERS)))
        x_ = int(rng.integers(0, len(tl1.AXIS_EXITS)))
        s_ = int(rng.integers(0, len(tl1.AXIS_SIZING)))
        t_ = int(rng.integers(0, len(tl1.AXIS_TIMING)))
        axis = [tl1.AXIS_FILTERS[r_], tl1.AXIS_EXITS[x_],
                tl1.AXIS_SIZING[s_], tl1.AXIS_TIMING[t_]]
        active_set = []
        for pos in range(N_OVERLAY):
            dom_nn = OVERLAY_NON_NONE[pos]
            if pos in active:
                v = dom_nn[int(rng.integers(0, len(dom_nn)))]
                axis.append(v)
                active_set.append(OVERLAY_AXES[pos][0])
            else:
                axis.append("none")
        yield i, {"module": spec["module"], "fn": spec["fn"],
                  "sig_params": params, "axis": axis,
                  "family": family, "slot": slot,
                  "subspace_active": active_set,
                  "subspace_k": k_active}


def _subspace_bookkeeping(cand: dict) -> dict:
    """Honest subspace disclosure per draw (audit face)."""
    ax = cand["axis"]
    return {"k_active": cand["subspace_k"],
            "active_axes": list(cand["subspace_active"]),
            "axis_tuple": list(ax),
            "n_axis_slots": len(ax)}


# ------------------------------------------------------------- probe face
def cmd_probe() -> int:
    """2 out-of-band subspace draws through the REAL tl14 engine face
    (design probe only: ledger +0, zero registry, N1 95_002/95_003
    precedent).  Proves end-to-end: tl14 import face + subspace draw +
    panel/state plumbing + engine run + honest bookkeeping."""
    print(f"=== N2-W15 probe (out-of-band seed {PROBE_SEED}, "
          f"ledger +0) ===")
    t0 = time.time()
    grammar = load_grammar()
    draws = []
    for family, slot in (("A", 0), ("B", 0)):
        got = list(draw_candidate_subspace_w15(
            grammar, family, slot, 1, PROBE_SEED))
        assert len(got) == 1
        _, cand = got[0]
        cand["candidate_id"] = f"W15-PROBE-{family}{slot}"
        if family == "A":
            cand["template_trader"] = tl1.A_TEMPLATES[slot]["trader_id"]
        draws.append((family, slot, cand))
    # --- panel + shared states (screen-shard caliber, built ONCE) ---
    tl1.GRAMMAR = grammar
    prices, P, idx, listed, cen = tl1._load_leg("L")
    states = tl1.v3_state_series()
    try:
        import pandas as pd
        bl = pd.read_csv(tl1.B_LAYER_MASK)
        ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
        overlap = sorted(s for s in P["close"].columns if s in ok_codes)
    except Exception:
        overlap = []
    if overlap:
        import pandas as pd
        fundamental_ok = pd.DataFrame(False, index=P["close"].index,
                                      columns=P["close"].columns)
        for s in overlap:
            fundamental_ok[s] = True
    else:
        fundamental_ok = None
    shared = {
        "gate_state": tl3.gate_state_series(prices),
        "vol_state": tl4.vol_state_series(prices),
        "yang_state": tl5.yang_state_series(prices),
        "vconf_state": tl6.vconf_state_series(prices),
        "streak_state": tl7.streak_state_series(prices),
        "tstate_state": tl8.tstate_state_series(prices),
        "amp_state": tl14.amp_state_series(prices),
        "mom_state": tl14.mom_state_series(prices),
        "std_state": tl14.std_state_series(prices),
        "rsqr_state": tl14.rsqr_state_series(prices),
        "sumn_state": tl14.sumn_state_series(prices),
        "resi_state": tl14.resi_state_series(prices),
        "cnt_state": tl14.cnt_state_series(prices),
        "fundamental_ok": fundamental_ok,
    }
    atr20 = tl2.atr20_series(prices)
    results = []
    for family, slot, cand in draws:
        t1 = time.time()
        template = (tl1.A_TEMPLATES[slot] if family == "A" else None)
        out = tl14.run_candidate_curve_w14(
            cand, template, prices, P, states, atr20, **shared)
        eq, trades, metrics = out[0], out[1], out[2]
        row = {"candidate_id": cand["candidate_id"],
               "module": cand["module"], "fn": cand["fn"],
               "family": family, "slot": slot,
               **_subspace_bookkeeping(cand),
               "n_days": int(len(eq)),
               "final_eq": round(float(eq.iloc[-1]), 6),
               "sharpe_full": round(float(tl1.sharpe(eq)), 4)
               if len(eq) >= 30 and float(eq.iloc[0]) > 0 else None,
               "n_trades": int(metrics.get("num_trades", 0)),
               "n_entries": int(metrics.get("num_entries", 0)),
               "elapsed_s": round(time.time() - t1, 2)}
        results.append(row)
        print(f"  probe {cand['candidate_id']}: k={row['k_active']} "
              f"active={row['active_axes']} days={row['n_days']} "
              f"trades={row['n_trades']} sharpe={row['sharpe_full']}")
    payload = {"batch": f"{BATCH}-PROBE", "generated": _now_iso(),
               "machine": _machine_id(), "law_ref": LAW_REF,
               "prereg": PREREG, "evidence_cutoff": CUTOFF,
               **sg.cutoff_meta(CUTOFF),
               "probe_seed": PROBE_SEED,
               "ledger_effect": 0,
               "grammar_sha256": grammar["grammar_sha256"],
               "frozen_grammar_sha16": FROZEN_GRAMMAR_SHA16,
               "design_note": ("out-of-band design probe (95_00x law); "
                              "NOT a batch face -- zero ledger, zero "
                              "registry, zero screen/judge effect"),
               "results": results,
               "elapsed_s": round(time.time() - t0, 2)}
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(PROBE_OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, default=float)
    print(f"probe OK -> {os.path.relpath(PROBE_OUT, tl1.PATHS.root)} "
          f"({payload['elapsed_s']}s)")
    return 0


# ------------------------------------------- slice-2 freeze gate (R99/R250)
def _bands_registered() -> tuple:
    """Freeze-commit gate: the three N2-W15 berths must be registered
    in science_gates.SEED_REGISTRY with the exact prereg sec.5 values
    before ANY burn leg runs (R99 zero-burn-before-freeze + R250
    one-step: seeds registered only at the freeze commit).  Returns
    (ok, missing/ drifted detail)."""
    need = {"perpetual_n2_w15_gen": BAND_GEN,
            "perpetual_n2_w15_scrnull": BAND_SCRNULL,
            "perpetual_n2_w15_unc": BAND_UNC}
    bad = [f"{k}={sg.SEED_REGISTRY.get(k)!r}!={v}"
           for k, v in need.items()
           if sg.SEED_REGISTRY.get(k) != v]
    return (not bad), bad


def _freeze_gate(stage: str) -> int:
    """Shared burn-leg gate head; returns process rc (2 = honest
    refuse, zero products) when the freeze commit has not landed."""
    ok, bad = _bands_registered()
    if not ok:
        print(f"FREEZE-GATE [{stage}]: bands NOT registered -- "
              f"{'; '.join(bad)} (R99 zero-burn-before-freeze / R250 "
              "one-step; slice-3 freeze commit registers the berths; "
              "honest refuse, zero products)")
        return 2
    return 0


# ------------------------------------------------- null draw (scrnull band)
def _null_axis_draw_w15(i: int):
    """Deterministic screen-null draw per prereg sec.3: rng=[SEED_NULL,
    i] at the N2 scrnull berth 542_000 (zero stream overlap with any
    registered band by construction, selftest L4); consumption order =
    tl14 `_null_axis_draw` same-face caliber verbatim = p_on regime ->
    EIGHTEEN-tuple axis R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/
    TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI/CNT -> signal matrix (frozen
    runner face, all fourteen overlay legs included)."""
    rng = np.random.default_rng([SEED_NULL, i])
    p_on = tl1.NULL_P_REGIMES[int(rng.integers(len(tl1.NULL_P_REGIMES)))]
    ax = (tl1.AXIS_FILTERS[int(rng.integers(len(tl1.AXIS_FILTERS)))],
          tl1.AXIS_EXITS[int(rng.integers(len(tl1.AXIS_EXITS)))],
          tl1.AXIS_SIZING[int(rng.integers(len(tl1.AXIS_SIZING)))],
          tl1.AXIS_TIMING[int(rng.integers(len(tl1.AXIS_TIMING)))],
          tl2.AXIS_STOP[int(rng.integers(len(tl2.AXIS_STOP)))],
          tl3.AXIS_GATE[int(rng.integers(len(tl3.AXIS_GATE)))],
          tl4.AXIS_VOL[int(rng.integers(len(tl4.AXIS_VOL)))],
          tl5.AXIS_YANG[int(rng.integers(len(tl5.AXIS_YANG)))],
          tl6.AXIS_VCONF[int(rng.integers(len(tl6.AXIS_VCONF)))],
          tl7.AXIS_STREAK[int(rng.integers(len(tl7.AXIS_STREAK)))],
          tl8.AXIS_TSTATE[int(rng.integers(len(tl8.AXIS_TSTATE)))],
          tl14.AXIS_AMP[int(rng.integers(len(tl14.AXIS_AMP)))],
          tl14.AXIS_MOM[int(rng.integers(len(tl14.AXIS_MOM)))],
          tl14.AXIS_STD[int(rng.integers(len(tl14.AXIS_STD)))],
          tl14.AXIS_RSQR[int(rng.integers(len(tl14.AXIS_RSQR)))],
          tl14.AXIS_SUMN[int(rng.integers(len(tl14.AXIS_SUMN)))],
          tl14.AXIS_RESI[int(rng.integers(len(tl14.AXIS_RESI)))],
          tl14.AXIS_CNT[int(rng.integers(len(tl14.AXIS_CNT)))])
    return p_on, list(ax), rng


# ------------------------------------------- screen cell math (factored)
def _beat6m_row(eq, metrics, starts, passive) -> dict:
    """beat6m row math, W14 `_screen_cell_w14` caliber verbatim and
    factored for hermetic real-path coverage (r494): >= comparison per
    frozen prereg text; binomial z/p on the full starts count.  The
    no_entries honesty leg (len(eq) < 30 or nonpositive first equity)
    is applied by the caller."""
    k = n_win = 0
    for p in starts:
        if p + W6M - 1 >= len(eq):
            continue
        n_win += 1
        cret = float(eq.iloc[p + W6M - 1] / eq.iloc[p] - 1.0)
        if cret >= passive[p]:        # prereg sec.3 literal ">="
            k += 1
    rate = k / n_win if n_win else 0.0
    n = len(starts)
    z = (k - 0.5 * n) / math.sqrt(0.25 * n) if n else 0.0
    pval = 2 * (1 - tl1._norm_cdf(abs(z)))
    return {"no_entries": False,
            "beat6m_k": k, "beat6m_n": n_win,
            "beat6m_rate": round(rate, 6),
            "binom_z": round(z, 4), "binom_p": round(pval, 6),
            "sharpe_full": round(float(tl1.sharpe(eq)), 4),
            "dd_full": round(float(tl1.max_drawdown(eq)), 4),
            "n_trades": int(metrics.get("num_trades", 0)),
            "n_entries": int(metrics.get("num_entries", 0))}


def _screen_cell_w15(cell: dict) -> dict:
    """One W15 screen cell: full leg-L backtest through the REAL tl14
    engine face with the candidate's subspace 18-tuple (inactive
    overlays pinned "none" = engine identity members by construction),
    or a scrnull null cell; -> beat6m row (pool worker; W14
    `_screen_cell_w14` caliber + subspace disclosure columns)."""
    st = tl1._ST
    kind, cand, template = cell["kind"], cell["cand"], cell.get("template")
    P, prices, states = st["P"], st["prices"], st["states"]
    starts, passive = st["starts"], st["passive_6m"]
    close = P["close"]
    if kind == "null":
        p_on, ax, rng = _null_axis_draw_w15(cell["i"])
        cand = {"module": "null", "fn": "random_signal",
                "sig_params": {"p_on": p_on}, "axis": ax,
                "candidate_id": f"W15-NULL-{cell['i']:04d}",
                "family": "NULL"}
        mat = rng.random((len(close.index), len(close.columns)))
        out = tl14.run_candidate_curve_w14(
            cand, None, prices, P, states, st["atr20"],
            rng_matrix=mat, p_on=p_on, gate_state=st.get("gate_state"),
            vol_state=st.get("vol_state"), yang_state=st.get("yang_state"),
            vconf_state=st.get("vconf_state"),
            streak_state=st.get("streak_state"),
            tstate_state=st.get("tstate_state"),
            amp_state=st.get("amp_state"), mom_state=st.get("mom_state"),
            std_state=st.get("std_state"), rsqr_state=st.get("rsqr_state"),
            sumn_state=st.get("sumn_state"),
            resi_state=st.get("resi_state"),
            cnt_state=st.get("cnt_state"))
    else:
        out = tl14.run_candidate_curve_w14(
            cand, template, prices, P, states, st["atr20"],
            fundamental_ok=st["fundamental_ok"],
            gate_state=st.get("gate_state"),
            vol_state=st.get("vol_state"), yang_state=st.get("yang_state"),
            vconf_state=st.get("vconf_state"),
            streak_state=st.get("streak_state"),
            tstate_state=st.get("tstate_state"),
            amp_state=st.get("amp_state"), mom_state=st.get("mom_state"),
            std_state=st.get("std_state"), rsqr_state=st.get("rsqr_state"),
            sumn_state=st.get("sumn_state"),
            resi_state=st.get("resi_state"),
            cnt_state=st.get("cnt_state"))
    eq, trades, metrics = out[0], out[1], out[2]
    (fired, gz, vz, yz, cz, sz, tz, az, mz, dz, rz, nz, rz2, cnz) = out[5:]
    row = {"cell_id": cell["cell_id"],
           "candidate_id": cand["candidate_id"],
           "family": cand["family"],
           "k_active": cand.get("subspace_k"),
           "active_axes": (list(cand["subspace_active"])
                           if cand.get("subspace_active") is not None
                           else None),
           "stop_face": cand["axis"][4], "stop_fired": int(fired),
           "gate_face": cand["axis"][5], "gate_zeroed": int(gz),
           "vol_face": cand["axis"][6], "vol_zeroed": int(vz),
           "yang_face": cand["axis"][7], "yang_zeroed": int(yz),
           "vconf_face": cand["axis"][8], "vconf_zeroed": int(cz),
           "streak_face": cand["axis"][9], "streak_zeroed": int(sz),
           "tstate_face": cand["axis"][10], "tstate_zeroed": int(tz),
           "amp_face": cand["axis"][11], "amp_zeroed": int(az),
           "mom_face": cand["axis"][12], "mom_zeroed": int(mz),
           "std_face": cand["axis"][13], "std_zeroed": int(dz),
           "rsqr_face": cand["axis"][14], "rsqr_zeroed": int(rz),
           "sumn_face": cand["axis"][15], "sumn_zeroed": int(nz),
           "resi_face": cand["axis"][16], "resi_zeroed": int(rz2),
           "cnt_face": cand["axis"][17], "cnt_zeroed": int(cnz)}
    if len(eq) < 30 or float(eq.iloc[0]) <= 0:
        row.update({"no_entries": True, "beat6m_k": 0,
                    "beat6m_n": len(starts), "beat6m_rate": 0.0,
                    "sharpe_full": None,
                    "n_trades": int(metrics.get("num_trades", 0)),
                    "n_entries": int(metrics.get("num_entries", 0))})
        return row
    row.update({"module": cand.get("module"), "fn": cand.get("fn")})
    row.update(_beat6m_row(eq, metrics, starts, passive))
    return row


def _cell_list_n2():
    """Distinct candidate cells + K null cells (deterministic order,
    shard-split by index; W1-W14 `_cell_list` caliber)."""
    cands = json.load(open(CANDIDATES_FILE, encoding="utf-8"))["candidates"]
    a_by_trader = {t["trader_id"]: t for t in tl1.A_TEMPLATES}
    cells = []
    for c in cands:
        template = (a_by_trader.get(c.get("template_trader"))
                    if c["family"] == "A" else None)
        cells.append({"cell_id": f"SCREEN|{c['candidate_id']}",
                      "kind": "cand", "cand": c, "template": template})
    for i in range(K_NULLS):
        cells.append({"cell_id": f"SCREEN|NULL-{i:04d}", "kind": "null",
                      "i": i, "cand": None})
    return cells


# ------------------------------- checkpoint scanner (r670 pairing law)
def _ckpt_path(shard: int, shards: int) -> str:
    return os.path.join(CKPT_DIR, f"n2_screen_shard_{shard}of{shards}.jsonl")


def _scan_done(ck: str) -> set:
    """Done set from a shard checkpoint; a row counts as done ONLY with
    a non-empty screen payload (cell_id + beat6m_n + family keys
    present) -- r670 done-judgment non-empty-payload law (empty poison
    rows never count as done)."""
    done = set()
    if not os.path.exists(ck):
        return done
    with open(ck, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
                if (r.get("cell_id") and "beat6m_n" in r
                        and r.get("family")):
                    done.add(r["cell_id"])
            except Exception:
                pass
    return done


def _load_screen_rows_n2() -> list:
    """All shard checkpoint rows (finalize face; every
    n2_screen_shard_*of*.jsonl in the checkpoint dir)."""
    rows = []
    if not os.path.isdir(CKPT_DIR):
        return rows
    for f in sorted(os.listdir(CKPT_DIR)):
        if f.startswith("n2_screen_shard_") and f.endswith(".jsonl"):
            with open(os.path.join(CKPT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln:
                        try:
                            rows.append(json.loads(ln))
                        except Exception:
                            pass
    return rows


# --------------------------- dedup collapse (factored, T-84 s3 face)
def _collapse_by_fingerprint(fps, series, candidates):
    """T-84s3 dedup gate, factored from the W14 cmd_generate caliber
    (same law both legs): fingerprint groups keep the lowest
    candidate_id, then corr >= 0.999 naive-returns twins collapse
    keep-lowest-id.  Returns (final_keep_idx, fp_collapsed,
    corr_elim)."""
    fp_groups = {}
    for i, fp in enumerate(fps):
        fp_groups.setdefault(fp, []).append(i)
    keep, fp_collapsed = set(), []
    for fp, members in fp_groups.items():
        members.sort(key=lambda k: candidates[k]["candidate_id"])
        keep.add(members[0])
        fp_collapsed.append(
            {"kept": candidates[members[0]]["candidate_id"],
             "eliminated": [candidates[m]["candidate_id"]
                            for m in members[1:]]})
    idx_keep = sorted(keep)
    mat = np.vstack([series[i] for i in idx_keep]) if idx_keep \
        else np.zeros((0, 0))
    sd = mat.std(axis=1) if idx_keep else np.zeros(0)
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
                    corr_elim.append(
                        {"pair": sorted([ka, kb]),
                         "corr": round(float(corr[a_, b_]), 6),
                         "eliminated":
                             candidates[ib if ka < kb else ia]
                             ["candidate_id"]})
    final_keep = [i for i in idx_keep if i not in dead]
    return final_keep, fp_collapsed, corr_elim


# --------------------------------------------- shared leg-L state (probe face)
def _leg_state_shared(prices, P, fundamental_ok, grammar, prep):
    """Shared worker state on the SAME face the r510 probe ran (all 14
    overlay states from leg-L prices; G-ANCHOR-FACE same-face law)."""
    return {"P": P, "prices": prices, "states": tl1.v3_state_series(),
            "starts": prep["starts"],
            "passive_6m": {int(k): v for k, v in
                           prep["passive_6m_ret"].items()},
            "fundamental_ok": fundamental_ok, "grammar": grammar,
            "atr20": tl2.atr20_series(prices),
            "gate_state": tl3.gate_state_series(prices),
            "vol_state": tl4.vol_state_series(prices),
            "yang_state": tl5.yang_state_series(prices),
            "vconf_state": tl6.vconf_state_series(prices),
            "streak_state": tl7.streak_state_series(prices),
            "tstate_state": tl8.tstate_state_series(prices),
            "amp_state": tl14.amp_state_series(prices),
            "mom_state": tl14.mom_state_series(prices),
            "std_state": tl14.std_state_series(prices),
            "rsqr_state": tl14.rsqr_state_series(prices),
            "sumn_state": tl14.sumn_state_series(prices),
            "resi_state": tl14.resi_state_series(prices),
            "cnt_state": tl14.cnt_state_series(prices)}


# ---------------------------------------------------- generate face (s2)
def cmd_generate() -> int:
    """Prereg sec.3 generate stage on the subspace face (W13/W14
    cmd_generate caliber): per-slot subspace streams consumed in global
    round-robin (A 500 / B 4,500 raw) -> tl14 28-source exclusion
    real-read -> T-84s3 dedup gate on the effective signal face ->
    n2_w15_candidates.json.  FREEZE-GATED (R99/R250); candidates file
    present = same-grammar rerun FORBIDDEN.  Zero engine cells
    burned."""
    rc = _freeze_gate("generate")
    if rc:
        return rc
    t0 = time.time()
    print(f"=== {BATCH} generate (prereg DRAFT, bands registered) ===")
    if os.path.exists(CANDIDATES_FILE):
        print("GENERATE-GATE: n2_w15_candidates.json exists -- "
              "same-grammar rerun FORBIDDEN (TRIAL_LABOR_LAW sec.4 "
              "face); refusing")
        return 2
    grammar = load_grammar()
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=2880)
    # r691 bm-b: cap calibrated to the trio-occupation horizon (FUND
    # NULLS burns hold RAM<4GB until 10-06..08 ETAs). A 40min cap on a
    # multi-day-blocked host only chains exit-2 refusals into crash-
    # fuse same-hash freezes (r379 family); 48h lets the shard land
    # in-place when VALUE completes.
    if not ram_ok:
        print(f"GENERATE-GATE: free RAM {ram_min}GB < 4GB after bounded "
              "wait (three-sample r354 law) -- honest refuse, pool "
              "retries when RAM frees")
        return 2
    tl1.GRAMMAR = grammar
    prices, P, idx, listed, cen = tl1._load_leg("L")
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
    shared = {"gate_state": tl3.gate_state_series(prices),
             "vol_state": tl4.vol_state_series(prices),
             "yang_state": tl5.yang_state_series(prices),
             "vconf_state": tl6.vconf_state_series(prices),
             "streak_state": tl7.streak_state_series(prices),
             "tstate_state": tl8.tstate_state_series(prices),
             "amp_state": tl14.amp_state_series(prices),
             "mom_state": tl14.mom_state_series(prices),
             "std_state": tl14.std_state_series(prices),
             "rsqr_state": tl14.rsqr_state_series(prices),
             "sumn_state": tl14.sumn_state_series(prices),
             "resi_state": tl14.resi_state_series(prices),
             "cnt_state": tl14.cnt_state_series(prices)}
    excl_rows, excl_disc = tl14._load_exclusion_rows_w14(grammar)

    # ---- draws: per-slot subspace streams in global round-robin
    candidates, excluded_log = [], []
    excl_hits = {"A": 0, "B": 0}
    for family, n_draws in (("A", N_A), ("B", N_B)):
        slots = grammar["families"][family]
        n_slots = len(slots)
        streams = {s: draw_candidate_subspace_w15(
                      grammar, family, s,
                      (n_draws - s + n_slots - 1) // n_slots, SEED_GEN)
                  for s in range(n_slots)}
        for i in range(n_draws):
            slot = i % n_slots
            _, cand = next(streams[slot])
            cand["candidate_id"] = f"W15-{family}-{i:04d}"
            cand["provenance"] = {"seed": SEED_GEN,
                                  "family_idx": (slot if family == "A"
                                                 else 6 + slot),
                                  "stream_draw_idx": i // n_slots,
                                  "global_draw_idx": i}
            if family == "A":
                cand["template_trader"] = slots[slot]["trader_id"]
            hit = tl14._excluded_w14(cand, excl_rows)
            if hit:
                excl_hits[family] += 1
                excluded_log.append(
                    {"candidate_id": cand["candidate_id"],
                     "module": cand["module"], "fn": cand["fn"],
                     "axis": cand["axis"], "face": hit})
                continue
            candidates.append(cand)
        print(f"  raw draws {family}={n_draws}, exclusion hits "
              f"{excl_hits[family]}")

    # ---- dedup gate (T-84 s3) on the effective signal face
    fps, series = [], []
    for j, cand in enumerate(candidates):
        mk = f"{cand['module']}.{cand['fn']}"
        mask = tl1._signal_frame(cand, P, grammar["faces"][mk])
        mask = mask.reindex(index=close.index,
                            columns=close.columns).fillna(0)
        mask = tl1.apply_filter(mask, cand["axis"][0], P, fundamental_ok)
        mask = tl1.apply_timing(mask, cand["axis"][3])
        S = tl14._effective_signal_mask_w14(
            mask, prices, cand["axis"][4], atr20,
            cand["axis"][5], cand["axis"][6], cand["axis"][7],
            cand["axis"][8], cand["axis"][9], cand["axis"][10],
            cand["axis"][11], cand["axis"][12], cand["axis"][13],
            cand["axis"][14], cand["axis"][15], cand["axis"][16],
            cand["axis"][17], **shared)
        fps.append(tl1._fingerprint(S))
        series.append(tl1._naive_returns(S, close).values)
        del mask, S
        if (j + 1) % 250 == 0:
            print(f"  [dedup face] {j + 1}/{len(candidates)}", flush=True)
    final_keep, fp_collapsed, corr_elim = _collapse_by_fingerprint(
        fps, series, candidates)
    distinct = [candidates[i] for i in final_keep]

    # subspace disclosure faces (k_active histogram + active-axis counts)
    k_hist, axis_active = {}, {}
    for c in distinct:
        k_hist[c["subspace_k"]] = k_hist.get(c["subspace_k"], 0) + 1
        for nm in c["subspace_active"]:
            axis_active[nm] = axis_active.get(nm, 0) + 1
    payload = {"batch": BATCH, "stage": "generate", "wave": WAVE,
               "prereg": PREREG, "evidence_cutoff": CUTOFF,
               **sg.cutoff_meta(CUTOFF),
               "grammar_sha256": grammar["grammar_sha256"],
               "frozen_grammar_sha16": FROZEN_GRAMMAR_SHA16,
               "machine": _machine_id(), "generated": _now_iso(),
               "n": len(distinct), "candidates": distinct,
               "draws": {"A": N_A, "B": N_B, "raw": N_A + N_B,
                         "seed_gen": SEED_GEN},
               "exclusion": {"hits": excl_hits,
                             "excluded_log": excluded_log,
                             "sources": excl_disc,
                             "note": "tl14 28-source exclusion face "
                                     "real-read (import-face); W15 "
                                     "new-syntax cells = legal "
                                     "non-exclusion (prereg sec.3)"},
               "dedup": {"raw": len(candidates), "distinct": len(distinct),
                         "fingerprint_collapse_groups": fp_collapsed,
                         "corr_collapses": corr_elim,
                         "note": "T-84s3 dedup legs on the generate-"
                                 "stage effective signal face (all "
                                 "fourteen overlay legs applied, frozen "
                                 "composition order; naive-hold returns, "
                                 "zero engine burn); engine faces run at "
                                 "screen (W1 precedent)"},
               "subspace_disclosure": {
                   "k_active_histogram": k_hist,
                   "active_axis_counts": axis_active,
                   "note": "random-subspace majority-combination face "
                           "(canon sec.2 N2 row); inactive axes pinned "
                           "none = engine identity members"},
               "audit": {"ram_gate_gb": ram_min,
                         "seed_berth_note": "berths 541_500/542_000/"
                         "542_500 registered at the freeze commit "
                         "(R250 one-step; slice-3); generate consumed "
                         "post-registration only (R99)"}}
    os.makedirs(RES_DIR, exist_ok=True)
    tl1._dump(CANDIDATES_FILE, payload)
    print(f"generate done: raw {N_A + N_B} -> exclusion hits "
          f"{sum(excl_hits.values())} -> dedup distinct {len(distinct)} "
          f"(fp-collapses {len(fp_collapsed)}, corr-collapses "
          f"{len(corr_elim)})")
    print(f"k_active histogram: {json.dumps(k_hist, sort_keys=True)}")
    print(f"active axis counts: {json.dumps(axis_active, sort_keys=True)}")
    print(f"products: n2_w15_candidates.json (elapsed "
          f"{time.time() - t0:.1f}s, zero engine cells burned)")
    return 0


# ------------------------------------------------- screen-prep face (s2)
def cmd_screen_prep() -> int:
    """G-PANEL + G-VOL..G-CNT raw-full-history fail-closed gates +
    G-ANCHOR grammar replay parity + G-CENSUS leg-L starts/passive
    precompute (prereg sec.2: tl14 gate chain same-face reuse, W14
    frozen caliber; identity faces run BEFORE the candidates-presence
    refusal per the r446bmb identity-first-run law)."""
    rc = _freeze_gate("screen-prep")
    if rc:
        return rc
    print(f"=== {BATCH} screen-prep (fail-closed gates) ===")
    if not os.path.exists(CANDIDATES_FILE):
        print("PREP-TAIL-GATE: n2_w15_candidates.json absent -- generate "
              "pending (identity faces below still run first per the "
              "identity-first-run law)")
        gen_pending = True
    else:
        gen_pending = False
    grammar = load_grammar()
    # tl1.GRAMMAR must be pinned before the G-ANCHOR replay loop:
    # tl14.run_candidate_curve_w14 reads tl1's global (probe/generate/
    # run legs all pin it; first real-data prep run crashed without).
    tl1.GRAMMAR = grammar

    prices_full = tl1.load_core()
    cut = pd.Timestamp(CUTOFF)
    prices_full = {s: df[df.index <= cut] for s, df in prices_full.items()}
    n_members = len(prices_full)
    bad = [s for s, df in prices_full.items()
           if len(df) < 60 or str(df.index[-1].date()) != CUTOFF
           or not {"open", "high", "low", "close", "volume"}
           <= set(df.columns)]
    gp = {"members": n_members, "bad": bad,
          "pass": bool(n_members == 48 and not bad)}
    if not gp["pass"]:
        print(f"PREP-GATE FAIL: G-PANEL {gp}")
        return 1

    # G-VOL..G-CNT raw-full-history gates (fail-closed err faces)
    full_gates = [("G-VOL", tl4._vol_state_full),
                  ("G-YANG", tl5._yang_state_full),
                  ("G-VCONF", tl6._vconf_state_full),
                  ("G-STREAK", tl7._streak_state_full),
                  ("G-TSTATE", tl8._tstate_state_full),
                  ("G-AMP", tl14._amp_state_full),
                  ("G-MOM", tl14._mom_state_full),
                  ("G-STD", tl14._std_state_full),
                  ("G-RSQR", tl14._rsqr_state_full),
                  ("G-SUMN", tl14._sumn_state_full),
                  ("G-RESI", tl14._resi_state_full),
                  ("G-CNT", tl14._cnt_state_full)]
    gate_meta = {}
    for gname, fn in full_gates:
        state_full, err = fn()
        if err:
            print(f"PREP-GATE FAIL: {gname} {err} (prereg sec.2 "
                  "fail-closed) -- refuse")
            return 1
        gate_meta[gname] = "PASS (raw full-history face)"
    vol_state_full, _ = tl4._vol_state_full()
    vol_meta_core = vol_state_full[2]

    # G-ANCHOR: six registered templates replayed through the grammar
    # default-axis identity face (all-none 18-tuple -> tl1 engine parity)
    pcut = prices_full
    Pfull = tl1.build_panels(pcut)
    anchors = {}
    for t in tl1.A_TEMPLATES:
        trader = tl1.load_trader(t["trader_id"])
        a = tl1.anchor_gate(trader, prices_full)
        if not a["ok"]:
            print(f"PREP-GATE FAIL: live anchor drift {t['trader_id']}")
            return 1
        cand = {"module": t["module"], "fn": t["fn"],
                "sig_params": t["sig_params"],
                "axis": list(tl1.DEFAULT_AXIS) + ["none"] * N_OVERLAY}
        eq, *_ = tl14.run_candidate_curve_w14(
            cand, t, pcut, Pfull, tl1.v3_state_series())
        got_is = tl1.sharpe(eq[eq.index < tl1.OOS_START])
        got_oos = tl1.sharpe(eq[eq.index >= tl1.OOS_START])
        mine_ok = (abs(round(float(got_is), 4)
                       - a["got"]["in_sample"]["sharpe"]) < 1e-9
                   and abs(round(float(got_oos), 4)
                           - a["got"]["out_sample"]["sharpe"]) < 1e-9)
        anchors[t["trader_id"]] = {
            "live_ok": True, "grammar_replay_is": round(float(got_is), 4),
            "grammar_replay_oos": round(float(got_oos), 4),
            "grammar_face_faithful": bool(mine_ok)}
        if not mine_ok:
            print(f"PREP-GATE FAIL: grammar replay != live anchor "
                  f"{t['trader_id']} (is {got_is:.4f} vs "
                  f"{a['got']['in_sample']['sharpe']}, oos {got_oos:.4f} "
                  f"vs {a['got']['out_sample']['sharpe']})")
            return 1
    ga = {"pass": True, "anchors": anchors}

    # G-CENSUS leg-L + structural passes + starts/passive precompute
    prices, P, idx, listed, cen = tl1._load_leg("L")
    if cen != tl1.FROZEN_CENSUS["L"]:
        print(f"PREP-GATE FAIL: leg-L census drift {cen} != "
              f"{tl1.FROZEN_CENSUS['L']}")
        return 1
    gc_ = {"pass": True, "census": cen, "frozen": tl1.FROZEN_CENSUS["L"]}
    for member, gate_name in ((tl7.STREAK_MEMBER, "streak"),
                              (tl8.TSTATE_MEMBER, "tstate"),
                              (tl14.AMP_MEMBER, "amp"),
                              (tl14.MOM_MEMBER, "mom"),
                              (tl14.STD_MEMBER, "std"),
                              (tl14.RSQR_MEMBER, "rsqr"),
                              (tl14.SUMN_MEMBER, "sumn"),
                              (tl14.RESI_MEMBER, "resi"),
                              (tl14.CNT_MEMBER, "cnt")):
        if member not in prices:
            print(f"PREP-GATE FAIL: leg-L panel missing {gate_name} "
                  f"member {member} ({gate_name} series underivable)")
            return 1
    legl_checks = {}
    _, _, gate_meta_legl = tl3.gate_state_series(prices)
    legl_checks["gate"] = "PASS"
    _, _, vol_meta = tl4.vol_state_series(prices)
    if not tl4._vol_structure_pass(vol_meta):
        print(f"PREP-GATE FAIL: G-VOL leg-L structural invariants "
              f"broken {vol_meta} -- honest refuse")
        return 1
    legl_checks["vol"] = "PASS"
    _, _, yang_meta = tl5.yang_state_series(prices)
    if not tl5._yang_structure_pass(yang_meta):
        print(f"PREP-GATE FAIL: G-YANG leg-L structural invariants "
              f"broken {yang_meta} -- honest refuse")
        return 1
    legl_checks["yang"] = "PASS"
    _, _, vconf_meta = tl6.vconf_state_series(prices)
    if not tl6._vconf_structure_pass(vconf_meta):
        print(f"PREP-GATE FAIL: G-VCONF leg-L structural invariants "
              f"broken {vconf_meta} -- honest refuse")
        return 1
    legl_checks["vconf"] = "PASS"
    _, _, streak_meta = tl7.streak_state_series(prices)
    if not tl7._streak_structure_pass(streak_meta):
        print(f"PREP-GATE FAIL: G-STREAK leg-L structural invariants "
              f"broken {streak_meta} -- honest refuse")
        return 1
    legl_checks["streak"] = "PASS"
    _, _, tstate_meta = tl8.tstate_state_series(prices)
    if not tl8._tstate_structure_pass(tstate_meta):
        print(f"PREP-GATE FAIL: G-TSTATE leg-L structural invariants "
              f"broken {tstate_meta} -- honest refuse")
        return 1
    legl_checks["tstate"] = "PASS"
    _, _, amp_meta = tl14.amp_state_series(prices)
    if not tl14._amp_structure_pass(amp_meta):
        print(f"PREP-GATE FAIL: G-AMP leg-L structural invariants "
              f"broken {amp_meta} -- honest refuse")
        return 1
    legl_checks["amp"] = "PASS"
    _, _, mom_meta = tl14.mom_state_series(prices)
    if not tl14._mom_structure_pass(mom_meta):
        print(f"PREP-GATE FAIL: G-MOM leg-L structural invariants "
              f"broken {mom_meta} -- honest refuse")
        return 1
    legl_checks["mom"] = "PASS"
    _o20, _d20, std_meta, _o10, _d10 = tl14.std_state_series(prices)
    if not tl14._std_structure_pass(std_meta):
        print(f"PREP-GATE FAIL: G-STD leg-L structural invariants "
              f"broken {std_meta} -- honest refuse")
        return 1
    legl_checks["std"] = "PASS"
    _r20o, _r20d, rsqr_meta, _r10o, _r10d = tl14.rsqr_state_series(prices)
    if not tl14._rsqr_structure_pass(rsqr_meta):
        print(f"PREP-GATE FAIL: G-RSQR leg-L structural invariants "
              f"broken {rsqr_meta} -- honest refuse")
        return 1
    legl_checks["rsqr"] = "PASS"
    _n20o, _n20d, sumn_meta, _n10o, _n10d = tl14.sumn_state_series(prices)
    if not tl14._sumn_structure_pass(sumn_meta):
        print(f"PREP-GATE FAIL: G-SUMN leg-L structural invariants "
              f"broken {sumn_meta} -- honest refuse")
        return 1
    legl_checks["sumn"] = "PASS"
    _ro, _rd, resi_meta = tl14.resi_state_series(prices)
    if not tl14._resi_structure_pass(resi_meta):
        print(f"PREP-GATE FAIL: G-RESI leg-L structural invariants "
              f"broken {resi_meta} -- honest refuse")
        return 1
    legl_checks["resi"] = "PASS"
    _cd5o, _cd5d, _cn20o, _cn20d, cnt_meta = tl14.cnt_state_series(prices)
    if not tl14._cnt_structure_pass(cnt_meta):
        print(f"PREP-GATE FAIL: G-CNT leg-L structural invariants "
              f"broken {cnt_meta} -- honest refuse")
        return 1
    legl_checks["cnt"] = "PASS"
    close = P["close"]
    n = len(idx)
    starts = [p for p in range(n)
              if idx[p] >= tl1.LEG_L_FLOOR and p >= tl1.WARMUP_TD
              and p <= n - 1 - W6M and listed.iloc[p] >= tl1.MIN_LISTED]
    if len(starts) != tl1.FROZEN_CENSUS["L"]["6m"]:
        print(f"PREP-GATE FAIL: 6m starts {len(starts)} != "
              f"{tl1.FROZEN_CENSUS['L']['6m']}")
        return 1
    passive_6m = {}
    for p in starts:
        sdate = idx[p]
        edate = idx[p + W6M - 1]
        syms = close.columns[close.loc[sdate].notna()]
        rel = tl1.passive_rel(close, syms, sdate, edate)
        passive_6m[int(p)] = round(float(rel.iloc[-1] - 1.0), 6)

    # candidates-presence gate at the TAIL (identity-first-run law)
    cg = None
    if gen_pending:
        print("PREP-GATE FAIL: generate pending (identity faces above "
              "ALL PASS on real data)")
        return 2
    cg = json.load(open(CANDIDATES_FILE, encoding="utf-8"))
    if str(cg.get("grammar_sha256", ""))[:16] != FROZEN_GRAMMAR_SHA16:
        print("PREP-GATE FAIL: candidates grammar_sha256 != frozen "
              "anchor")
        return 1

    prep = {"batch": BATCH, "wave": WAVE, "prereg": PREREG,
            "evidence_cutoff": CUTOFF, **tl1.cutoff_meta(CUTOFF),
            "grammar_sha256": grammar["grammar_sha256"],
            "gates": {"G-PANEL": gp, "G-ANCHOR": ga, "G-CENSUS": gc_,
                      "G-EXCLUDE": {"pass": True,
                                    "hits": cg["exclusion"]["hits"],
                                    "sources":
                                        cg["exclusion"]["sources"]},
                      **gate_meta},
            "legl_structural": legl_checks,
            "gate_meta": gate_meta_legl, "vol_meta": vol_meta,
            "yang_meta": yang_meta, "vconf_meta": vconf_meta,
            "streak_meta": streak_meta, "tstate_meta": tstate_meta,
            "amp_meta": amp_meta, "mom_meta": mom_meta,
            "std_meta": std_meta, "rsqr_meta": rsqr_meta,
            "sumn_meta": sumn_meta, "resi_meta": resi_meta,
            "cnt_meta": cnt_meta, "vol_meta_core48": vol_meta_core,
            "n_distinct": cg["n"], "n_starts_6m": len(starts),
            "starts": starts, "passive_6m_ret": passive_6m,
            "generated": _now_iso()}
    os.makedirs(RES_DIR, exist_ok=True)
    tl1._dump(PREP_FILE, prep)
    print(f"prep PASS: panel {gp['members']}/48, anchors "
          f"{len(anchors)}/6 faithful, census {cen}, starts "
          f"{len(starts)}, passive precomputed, leg-L structural "
          f"{len(legl_checks)}/14 PASS")
    return 0


# -------------------------------------------------- pool run face (s2)
def cmd_run(shard: int, shards: int, workers) -> int:
    """Pool shard executor for the screen stage: cells split by
    i % shards == shard (r670 tiling law), checkpoint append-per-cell
    (kill-safe resume), r496 three-call pool claim on verified done."""
    rc = _freeze_gate("run")
    if rc:
        return rc
    print(f"=== {BATCH} screen shard {shard}of{shards} ===")
    for p, what in ((PREP_FILE, "n2_w15_prep_state.json"),
                    (CANDIDATES_FILE, "n2_w15_candidates.json")):
        if not os.path.exists(p):
            print(f"RUN-GATE: {what} absent -- run screen-prep (and "
                  "generate) first")
            return 2
    prep = json.load(open(PREP_FILE, encoding="utf-8"))
    cells = _cell_list_n2()
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=2880)
    if not ram_ok:
        print(f"RUN-GATE: free RAM {ram_min}GB < 4GB after bounded "
              "wait (three-sample r354 law) -- honest refuse, pool "
              "retries when RAM frees")
        return 2
    tl1.GRAMMAR = load_grammar()
    mine = [c for i, c in enumerate(cells) if i % shards == shard]
    prices, P, idx, listed, cen = tl1._load_leg("L")
    try:
        bl = pd.read_csv(tl1.B_LAYER_MASK)
        ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
        overlap = sorted(s for s in P["close"].columns if s in ok_codes)
    except Exception:
        overlap = []
    if overlap:
        fundamental_ok = pd.DataFrame(False, index=P["close"].index,
                                      columns=P["close"].columns)
        for s in overlap:
            fundamental_ok[s] = True
    else:
        fundamental_ok = None
    state = _leg_state_shared(prices, P, fundamental_ok,
                              tl1.GRAMMAR, prep)
    ck = _ckpt_path(shard, shards)
    os.makedirs(CKPT_DIR, exist_ok=True)
    done = _scan_done(ck)
    todo = [c for c in mine if c["cell_id"] not in done]
    print(f"shard cells {len(mine)}, done {len(done)}, todo {len(todo)}")

    def on_result(key, payload):
        os.makedirs(CKPT_DIR, exist_ok=True)
        with open(ck, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(tl1._j(payload), ensure_ascii=False,
                                default=float) + "\n")

    if todo:
        jobs = [(c["cell_id"], _screen_cell_w15, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                               desc=f"n2w15 screen s{shard}",
                               initializer=tl1._init_worker,
                               initargs=(state,), on_result=on_result)
    done_after = _scan_done(ck)
    missing_mine = [c["cell_id"] for c in mine
                    if c["cell_id"] not in done_after]
    if missing_mine:
        print(f"RUN-INCOMPLETE: {len(missing_mine)}/{len(mine)} shard "
              f"cells absent post-burn (checkpoint retained, honest "
              f"refuse, NO pool claim); first missing: "
              f"{missing_mine[:3]}")
        return 2
    entry_id, shard_key = entry_shard_of(shard, shards)
    _pool_claim(entry_id, shard_key,
                f"{len(mine)} cells done, ckpt {os.path.basename(ck)}")
    print(f"shard {shard}of{shards} complete -> {ck} ({len(mine)} "
          f"cells, pool claim closed)")
    return 0


# --------------------------------------------- screen-finalize face (s2)
def cmd_screen_finalize() -> int:
    """id-level dup probe (r482/r685 law: keep-first on dup) + missing
    gate + null-p95 survival line (tl2._finalize_math same-face) +
    k_active / active-axis segmented survival + ledger append
    PERPETUAL-N2-W15-SCREEN (prereg sec.3) + CSV/JSON products."""
    rc = _freeze_gate("screen-finalize")
    if rc:
        return rc
    print(f"=== {BATCH} screen-finalize ===")
    landed = tl6.finalize_already_landed(BATCH_SCREEN, SCREEN_FILE)
    if landed is not None:
        print(f"FINALIZE-IDEMPOTENT-GUARD: {BATCH_SCREEN} already "
              f"landed (ledger total={landed.get('total')}); re-run "
              "refused (pit-95 double-append guard; re-run channel = "
              "fresh prereg + fresh batch name)")
        return 2
    if not os.path.exists(CANDIDATES_FILE):
        print("SCREEN-FINALIZE-GATE: generate pending "
              "(n2_w15_candidates.json absent) -- nothing to finalize")
        return 2
    cells = _cell_list_n2()
    rows = _load_screen_rows_n2()
    # id-level dup probe (r482 law): keep-first on duplicate cell_id,
    # zero information loss, disclosed in the payload
    by_id, dup_ids = {}, []
    for r in rows:
        cid = r.get("cell_id")
        if not cid:
            continue
        if cid in by_id:
            dup_ids.append(cid)
        else:
            by_id[cid] = r
    if dup_ids:
        print(f"  [dup probe] {len(dup_ids)} duplicate cell_ids -> "
              f"keep-first dedup (r482 law); first: {dup_ids[:3]}")
    missing = [c["cell_id"] for c in cells if c["cell_id"] not in by_id]
    if missing:
        print(f"FINALIZE-GATE: {len(missing)} cells incomplete -- "
              f"finalize refused (checkpoint retained); first missing: "
              f"{missing[:3]}")
        return 2
    null_rows = [by_id[f"SCREEN|NULL-{i:04d}"] for i in range(K_NULLS)]
    cand_rows = [by_id[c["cell_id"]] for c in cells if c["kind"] == "cand"]
    p95, survivors = tl2._finalize_math(cand_rows, null_rows)
    null_rates = [r["beat6m_rate"] for r in null_rows]
    # subspace segmentation (the N2 research face): per-k_active and
    # per-active-axis survival
    k_seg = {}
    axis_seg = {}
    for r in cand_rows:
        k = r.get("k_active")
        s = k_seg.setdefault(k, {"n_cells": 0, "n_survivors": 0})
        s["n_cells"] += 1
        s["n_survivors"] += int(bool(r["survives_screen"]))
        for nm in (r.get("active_axes") or []):
            a = axis_seg.setdefault(nm, {"n_cells": 0, "n_survivors": 0})
            a["n_cells"] += 1
            a["n_survivors"] += int(bool(r["survives_screen"]))
    for seg in (k_seg, axis_seg):
        for key, s in seg.items():
            s["survival_rate"] = round(
                s["n_survivors"] / s["n_cells"], 6) if s["n_cells"] else 0.0
    n_distinct = len(cand_rows)
    batch_trials = n_distinct + K_NULLS
    ledger = tl1.append_ledger(
        BATCH_SCREEN, batch_trials,
        "results/n2_w15/n2_w15_screen.json", evidence_cutoff=CUTOFF)
    out = {"batch": BATCH, "stage": "screen", "wave": WAVE,
           "prereg": PREREG, **sg.cutoff_meta(CUTOFF),
           "grammar_sha256": load_grammar()["grammar_sha256"],
           "n_distinct": n_distinct, "k_nulls": K_NULLS,
           "dup_probe": {"n_dup_ids": len(dup_ids),
                         "dedup_rule": "keep-first (r482 law)",
                         "first_dups": dup_ids[:5]},
           "null_family": {"rates": [round(x, 4) for x in null_rates],
                           "median": round(float(np.median(null_rates)),
                                           4),
                           "p95_line": round(p95, 6),
                           "p_regimes": list(tl1.NULL_P_REGIMES),
                           "seed": SEED_NULL,
                           "draw_order": "p_on regime -> EIGHTEEN-tuple "
                                         "axis R/X/S/T/STOP/GATE/VOL/"
                                         "YANG/VCONF/STREAK/TSTATE/AMP/"
                                         "MOM/STD/RSQR/SUMN/RESI/CNT -> "
                                         "signal matrix (tl14 same-face "
                                         "caliber at the N2 scrnull "
                                         "berth 542_000)"},
           "survival_rule": "beat6m_rate > null_p95 (prereg sec.4, "
                            "frozen)",
           "survivors": survivors, "n_survivors": len(survivors),
           "k_active_segmented_survival": k_seg,
           "active_axis_segmented_survival": axis_seg,
           "batch_cells": batch_trials, "trials_ledger": ledger,
           "audit": {"note": "one full leg-L backtest per cell (V1 "
                             "13.041bp x2 base cost, T+1); all "
                             "fourteen overlay legs at the engine face "
                             "frozen composition order (inactive axes "
                             "pinned none = identity members); beat6m "
                             "comparison operator >= per frozen prereg "
                             "text; survival math imported from "
                             "tl2._finalize_math (W2 identical law); "
                             "workers BelowNormal; checkpoint "
                             "append-per-cell; id-dup keep-first per "
                             "r482 law"},
           "generated": _now_iso()}
    tl1._dump(SCREEN_FILE, out)
    cols = ["cell_id", "candidate_id", "family", "module", "fn",
            "k_active", "active_axes", "no_entries", "beat6m_k",
            "beat6m_n", "beat6m_rate", "binom_z", "binom_p",
            "sharpe_full", "dd_full", "n_trades", "n_entries",
            "stop_face", "stop_fired", "gate_face", "gate_zeroed",
            "vol_face", "vol_zeroed", "yang_face", "yang_zeroed",
            "vconf_face", "vconf_zeroed", "streak_face",
            "streak_zeroed", "tstate_face", "tstate_zeroed",
            "amp_face", "amp_zeroed", "mom_face", "mom_zeroed",
            "std_face", "std_zeroed", "rsqr_face", "rsqr_zeroed",
            "sumn_face", "sumn_zeroed", "resi_face", "resi_zeroed",
            "cnt_face", "cnt_zeroed", "survives_screen"]
    with open(SCREEN_CSV, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in cand_rows:
            w.writerow(r)
    print(f"screen finalize: distinct {n_distinct} + nulls {K_NULLS}, "
          f"null p95 {p95:.4f}, survivors {len(survivors)} "
          f"(dup keep-first {len(dup_ids)})")
    print(f"k_active segmented survival: "
          f"{json.dumps(k_seg, sort_keys=True)}")
    print(f"active-axis segmented survival: "
          f"{json.dumps(axis_seg, sort_keys=True)}")
    print(f"products: n2_w15_screen.json + n2_w15_screen_cells.csv "
          f"(ledger total {ledger['total']})")
    return 0


# -------------------------------------------------- wave finalize (s2)
def cmd_finalize() -> int:
    """Wave closeout (slice-3 burn chain tail): verify the screen
    product + every pool shard claim closed, then write the wave
    results audit summary.  Ledger ALREADY appended at screen-finalize
    (prereg sec.3) -- this leg never appends (pit-95)."""
    rc = _freeze_gate("finalize")
    if rc:
        return rc
    print(f"=== {BATCH} finalize (wave closeout) ===")
    if os.path.exists(WAVE_RESULTS):
        print("FINALIZE-GATE: n2_w15_wave_results.json exists -- "
              "already closed; re-run refused (idempotency face)")
        return 2
    if not os.path.exists(SCREEN_FILE):
        print("FINALIZE-GATE: screen product absent -- screen-finalize "
              "first")
        return 2
    screen = json.load(open(SCREEN_FILE, encoding="utf-8"))
    claims_dir = os.path.join(tl1.PATHS.results_dir, "pool_claims")
    shard_status = {}
    for shard in range(NSHARDS):
        entry_id, shard_key = entry_shard_of(shard, NSHARDS)
        d = os.path.join(claims_dir, entry_id.replace("/", "_"))
        files = sorted(os.listdir(d)) if os.path.isdir(d) else []
        closed = [f for f in files if f.endswith(".json")]
        shard_status[shard_key] = {
            "claim_files": len(closed), "closed": bool(closed)}
    open_shards = [k for k, v in shard_status.items() if not v["closed"]]
    if open_shards:
        print(f"FINALIZE-GATE: {len(open_shards)}/{NSHARDS} pool "
              f"shards have no closed claim (harvest pending) -- "
              f"refuse; open: {open_shards[:4]}")
        return 2
    wave = {"batch": BATCH, "stage": "finalize", "wave": WAVE,
            "prereg": PREREG, **sg.cutoff_meta(CUTOFF),
            "evidence_cutoff": CUTOFF,
            "grammar_sha256": screen.get("grammar_sha256"),
            "screen_ref": os.path.relpath(SCREEN_FILE,
                                          tl1.PATHS.root),
            "n_distinct": screen.get("n_distinct"),
            "k_nulls": screen.get("k_nulls"),
            "null_p95": screen.get("null_family", {}).get("p95_line"),
            "n_survivors": screen.get("n_survivors"),
            "survivors": screen.get("survivors"),
            "k_active_segmented_survival":
                screen.get("k_active_segmented_survival"),
            "active_axis_segmented_survival":
                screen.get("active_axis_segmented_survival"),
            "pool_shards": shard_status,
            "ledger_note": "ledger appended at screen-finalize "
                           "(PERPETUAL-N2-W15-SCREEN, prereg sec.3); "
                           "wave closeout zero-append (pit-95)",
            "next_stage": "survivors -> judge batch (separate "
                          "per-stage freeze, mass_trial_w1 precedent)",
            "generated": _now_iso(), "machine": _machine_id()}
    os.makedirs(RES_DIR, exist_ok=True)
    tl1._dump(WAVE_RESULTS, wave)
    print(f"finalize: wave closed, {NSHARDS}/{NSHARDS} shards claimed, "
          f"survivors {wave['n_survivors']} -> "
          f"{os.path.relpath(WAVE_RESULTS, tl1.PATHS.root)}")
    return 0


# ========================= s3 judge face (slice-4, prereg sec.9.1) ====

def _judge_band_registered() -> bool:
    return JUDGE_BER in sg.SEED_REGISTRY


def _judge_freeze_gate(stage: str) -> int:
    """Judge-leg gate head: base trio bands (slice-2 face) + the judge
    berth registered at the sec.9.1 freeze commit (R99 zero-burn-
    before-freeze / R250 one-step; rc 2 = honest refuse, zero
    products)."""
    rc = _freeze_gate(stage)
    if rc:
        return rc
    if not _judge_band_registered():
        print(f"FREEZE-GATE [{stage}]: judge berth {JUDGE_BER} NOT "
              "registered -- sec.9.1 freeze commit pending (R99/R250; "
              "honest refuse, zero products)")
        return 2
    return 0


def _judge_ckpt_path(shard: int, shards: int) -> str:
    return os.path.join(
        CKPT_DIR, f"n2_w15_judge_shard_{shard}of{shards}.jsonl")


def _judge_scan_done(ck: str) -> set:
    """Done set from a judge shard checkpoint; a row counts as done
    ONLY with a full judged payload (cell_id + legs +
    legL_daily_returns) -- r670 non-empty-payload law."""
    done = set()
    if not os.path.exists(ck):
        return done
    with open(ck, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
                if (r.get("cell_id") and "legs" in r
                        and r.get("legL_daily_returns")):
                    done.add(r["cell_id"])
            except Exception:
                pass
    return done


def _b_layer_fundamental_ok(P) -> object:
    """fundamental_ok mask for a leg panel (screen cmd_run face
    verbatim; B_LAYER_MASK ok_static codes)."""
    try:
        bl = pd.read_csv(tl1.B_LAYER_MASK)
        ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
        overlap = sorted(s for s in P["close"].columns if s in ok_codes)
    except Exception:
        return None
    if not overlap:
        return None
    fundamental_ok = pd.DataFrame(False, index=P["close"].index,
                                  columns=P["close"].columns)
    for s in overlap:
        fundamental_ok[s] = True
    return fundamental_ok


def _judge_leg_state(prices, P, fundamental_ok, grammar) -> dict:
    """Per-leg shared overlay state on the SAME screen face
    (_leg_state_shared reuse; dummy prep keys for the two screen-only
    fields the judge state carries itself -- zero re-implementation of
    the 14 series)."""
    return _leg_state_shared(prices, P, fundamental_ok, grammar,
                             {"starts": [], "passive_6m_ret": {}})


def _judge_replay(st_leg: dict, cand, template, face: str):
    """One (leg, cost-face) replay through the SAME tl14 stack as the
    screen (sec.9: screen/judge zero-migration); x2 = sg.CostPatch(2.0)
    context (t22 Erratum-1 multiplier law, engine single source)."""
    cmgr = None
    if face == "x2":
        cmgr = sg.CostPatch(2.0)
        cmgr.__enter__()
    try:
        out = tl14.run_candidate_curve_w14(
            cand, template, st_leg["prices"], st_leg["P"],
            st_leg["states"], st_leg["atr20"],
            fundamental_ok=st_leg["fundamental_ok"],
            gate_state=st_leg.get("gate_state"),
            vol_state=st_leg.get("vol_state"),
            yang_state=st_leg.get("yang_state"),
            vconf_state=st_leg.get("vconf_state"),
            streak_state=st_leg.get("streak_state"),
            tstate_state=st_leg.get("tstate_state"),
            amp_state=st_leg.get("amp_state"),
            mom_state=st_leg.get("mom_state"),
            std_state=st_leg.get("std_state"),
            rsqr_state=st_leg.get("rsqr_state"),
            sumn_state=st_leg.get("sumn_state"),
            resi_state=st_leg.get("resi_state"),
            cnt_state=st_leg.get("cnt_state"))
    finally:
        if cmgr is not None:
            cmgr.__exit__(None, None, None)
    return out


def _judge_cell_w15(cell: dict) -> dict:
    """One collapsed-survivor judged cell (pool worker; sec.9.1 grid
    isomorphic to mass_trial_w1 _judge_cell: legs L/D x cost x1/x2 x
    windows {6m,12m,24m} sliced from full curves + regime segments
    (T-22 sec.3 frozen 3-way proxy) + dual nulls + G1'/DSR inputs +
    descriptive clauses; replay via the tl14 screen stack)."""
    st = tl1._ST
    cand, template = cell["cand"], cell.get("template")
    out = {"cell_id": cell["cell_id"],
           "candidate_id": cand["candidate_id"],
           "family": cand["family"], "i": cell["i"],
           "k_active": cand.get("subspace_k"),
           "active_axes": (list(cand["subspace_active"])
                           if cand.get("subspace_active") is not None
                           else None)}
    legs, legL_daily = {}, None
    for leg in ("L", "D"):
        st_leg = st["legs"][leg]
        idx = st_leg["idx"]
        faces = {}
        for face in ("x1", "x2"):
            o = _judge_replay(st_leg, cand, template, face)
            eq, metrics = o[0], o[2]
            beat = {}
            for wname, w in tl1.WINDOWS.items():
                k = tot = 0
                for p in st["starts"][leg][wname]:
                    if p + w - 1 >= len(eq):
                        continue
                    tot += 1
                    cret = float(eq.iloc[p + w - 1] / eq.iloc[p] - 1.0)
                    if cret > st["passive"][leg][wname][str(p)]:
                        k += 1
                beat[wname] = {"k": k, "n": tot,
                               "rate": round(k / tot, 6) if tot else 0.0}
            faces[face] = {
                "sharpe_full": round(float(tl1.sharpe(eq)), 4),
                "n_trades": int(metrics.get("num_trades", 0)),
                "n_entries": int(metrics.get("num_entries", 0)),
                "max_dd": round(float(tl1.max_drawdown(eq)), 4),
                "yearly": mtw1._yearly_returns(eq), "beat": beat,
            }
            if leg == "L" and face == "x1":
                legL_daily = eq.pct_change().fillna(0.0)
        # regime segments at window starts (T-22 sec.3 3-way proxy;
        # the v3 series is the same face the replay consumed)
        s_series = st_leg["states"].reindex(idx)
        segs = {"bear": 0, "bull": 0, "chop": 0, "na": 0}
        for wname in tl1.WINDOWS:
            for p in st["starts"][leg][wname]:
                d = s_series.iloc[p] if p < len(s_series) else None
                st_ = tl1.REGIME_MAP.get(d, "na") if d == d else "na"
                segs[st_] += 1
        legs[leg] = {"x1": faces["x1"], "x2": faces["x2"],
                     "regime_start_windows": segs}
    out["legs"] = legs
    daily = [round(float(v), 8) for v in legL_daily.values]
    out["legL_daily_returns"] = daily
    eq_l = (1.0 + legL_daily).cumprod()     # reconstruct for OOS split
    oos = eq_l[eq_l.index >= st["oos_start"]]
    oos_sharpe = float(tl1.sharpe(oos)) if len(oos) > 2 else 0.0
    oos_ret = (float(oos.iloc[-1] / oos.iloc[0] - 1.0)
               if len(oos) > 1 else 0.0)
    n_days = max(len(eq_l), 1)
    ann = float(eq_l.iloc[-1] / eq_l.iloc[0]) ** (252.0 / n_days) - 1.0
    yearly = legs["L"]["x1"]["yearly"]
    x2_yearly = legs["L"]["x2"]["yearly"]
    worst_year = min(yearly.values()) if yearly else 0.0
    x2_worst = min(x2_yearly.values()) if x2_yearly else 0.0
    out["legL_oos"] = {"oos_sharpe": round(oos_sharpe, 4),
                       "oos_ret": round(oos_ret, 6)}
    out["descriptive"] = {
        "ann_pos": bool(ann > 0),
        "oos_dual_pos": bool(oos_sharpe > 0 and oos_ret > 0),
        "dd_ok": bool(legs["L"]["x1"]["max_dd"] >= -0.35),
        "no_crash_year": bool(worst_year > -0.30),
        "x2_yearly_stable": bool(x2_worst > -0.30),
    }
    out["dual_nulls"] = mtw1._dual_nulls(daily, cell["i"],
                                         seed=st["seed_judge"])
    n_eff = sum(legs[lg]["regime_start_windows"][s]
                for lg in legs for s in ("bear", "bull", "chop"))
    out["n_eff_start_windows"] = n_eff
    out["sample_sufficient"] = bool(
        n_eff >= 500 and all(legs[lg]["regime_start_windows"][s] >= 100
                            for lg in legs
                            for s in ("bear", "bull", "chop")))
    return out


def cmd_judge_prep() -> int:
    """sec.9.1 prep: screen-product gates + survivors anchor + census
    gates (both legs) + |corr|>=0.999 leg-L base-face daily-returns
    collapse (mass_trial_w1 import face) + starts/passive precompute
    (legs L/D x {6m,12m,24m}) -> n2_w15_judge_state.json.  Serial
    short batch (sec.9), RAM-gated honest refuse."""
    rc = _judge_freeze_gate("judge-prep")
    if rc:
        return rc
    print(f"=== {JUDGE_BATCH} judge-prep (sec.9.1) ===")
    for p in (SCREEN_FILE, CANDIDATES_FILE):
        if not os.path.exists(p):
            print(f"JUDGE-PREP-GATE FAIL: {os.path.basename(p)} absent")
            return 1
    screen = json.load(open(SCREEN_FILE, encoding="utf-8"))
    if not screen.get("trials_ledger"):
        print("JUDGE-PREP-GATE FAIL: screen product not finalized "
              "(trials_ledger absent)")
        return 1
    survivors = list(screen.get("survivors") or [])
    if not survivors:
        print("JUDGE-PREP-GATE FAIL: zero screen survivors")
        return 1
    sha = hashlib.sha256(
        open(CANDIDATES_FILE, "rb").read()).hexdigest()[:16]
    cands_all = json.load(open(CANDIDATES_FILE,
                               encoding="utf-8"))["candidates"]
    by_id = {c["candidate_id"]: c for c in cands_all}
    missing = [s for s in survivors if s not in by_id]
    if missing:
        print(f"JUDGE-PREP-GATE FAIL: {len(missing)} survivors absent "
              "from candidates file; first: "
              f"{missing[:3]}")
        return 1
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=0)
    if not ram_ok:
        print(f"JUDGE-PREP-GATE: free RAM {ram_min}GB < 4GB (r354 "
              "three-sample law; r691 cap window) -- honest refuse, "
              "pool retries when the RAM window opens")
        return 2
    tl1.GRAMMAR = load_grammar()
    a_by_trader = {t["trader_id"]: t for t in tl1.A_TEMPLATES}
    # ---- leg-L base-face daily returns for every survivor (serial)
    prices, P, idx, listed, cen = tl1._load_leg("L")
    if cen != tl1.FROZEN_CENSUS["L"]:
        print(f"JUDGE-PREP-GATE FAIL: leg-L census drift {cen} != "
              f"{tl1.FROZEN_CENSUS['L']}")
        return 1
    st_legL = _judge_leg_state(prices, P, _b_layer_fundamental_ok(P),
                               tl1.GRAMMAR)
    st_legL["idx"] = idx
    t0 = time.time()
    rets = {}
    for cid in sorted(survivors):
        c = by_id[cid]
        template = (a_by_trader.get(c.get("template_trader"))
                    if c["family"] == "A" else None)
        eq = _judge_replay(st_legL, c, template, "x1")[0]
        rets[cid] = (eq.pct_change().fillna(0.0)
                     if len(eq) >= 2 and float(eq.iloc[0]) > 0
                     else pd.Series(0.0, index=idx[:max(len(eq), 1)]))
    kept, clusters, eliminated = mtw1._collapse_survivors(
        pd.DataFrame({c: rets[c] for c in sorted(rets)}))
    # ---- dual-leg census + starts/passive precompute (w1 prep face)
    starts, passive, legs_meta = {}, {}, {}
    for leg in ("L", "D"):
        if leg == "L":
            pl, Pl, idxl, listedl, cenl = prices, P, idx, listed, cen
        else:
            pl, Pl, idxl, listedl, cenl = tl1._load_leg("D")
        if cenl != tl1.FROZEN_CENSUS[leg]:
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} census drift "
                  f"{cenl} != {tl1.FROZEN_CENSUS[leg]}")
            return 1
        n = len(idxl)
        close = Pl["close"]
        starts[leg], passive[leg] = {}, {}
        for wname, w in tl1.WINDOWS.items():
            floor = tl1.LEG_L_FLOOR if leg == "L" else tl1.LEG_D_FLOOR
            st_ = [p for p in range(n)
                   if idxl[p] >= floor and p >= tl1.WARMUP_TD
                   and p <= n - 1 - w
                   and (listedl.iloc[p] >= tl1.MIN_LISTED
                        if leg == "L" else True)]
            if len(st_) != tl1.FROZEN_CENSUS[leg][wname]:
                print(f"JUDGE-PREP-GATE FAIL: leg-{leg} {wname} "
                      f"starts {len(st_)} != "
                      f"{tl1.FROZEN_CENSUS[leg][wname]}")
                return 1
            starts[leg][wname] = st_
            passive[leg][wname] = {}
            for p in st_:
                sdate, edate = idxl[p], idxl[p + w - 1]
                syms = close.columns[close.loc[sdate].notna()]
                rel = tl1.passive_rel(close, syms, sdate, edate)
                passive[leg][wname][str(p)] = round(
                    float(rel.iloc[-1] - 1.0), 6)
        legs_meta[leg] = {"census": cenl, "n_days": n,
                          "first": str(idxl[0].date()),
                          "last": str(idxl[-1].date()),
                          "members": len(close.columns)}
    state = {"batch": JUDGE_BATCH, "evidence_cutoff": CUTOFF,
             **tl1.cutoff_meta(CUTOFF),
             "candidates_sha256_16": sha,
             "screen_ref": os.path.relpath(SCREEN_FILE, tl1.PATHS.root),
             "n_stage1_survivors": len(survivors),
             "n_judge_cells": len(kept),
             "collapse": {"line": JUDGE_COLLAPSE_LINE, "kept": kept,
                          "clusters": clusters,
                          "eliminated": eliminated,
                          "note": "representative = deterministic "
                                  "lowest candidate_id; original "
                                  "variants retained in this audit "
                                  "block (sec.9.1, mass_trial_w1 face)"},
             "starts": starts, "passive": passive, "legs": legs_meta,
             "seed_judge": sg.SEED_REGISTRY[JUDGE_BER],
             "wave": WAVE,
             "generated": _now_iso(), "machine": _machine_id()}
    os.makedirs(RES_DIR, exist_ok=True)
    tl1._dump(JUDGE_STATE_FILE, state)
    print(f"judge-prep PASS: survivors {len(survivors)} -> N_judge "
          f"{len(kept)} (collapsed {len(eliminated)}); census L/D == "
          f"frozen; passive precomputed ({time.time()-t0:.0f}s) -> "
          f"{os.path.basename(JUDGE_STATE_FILE)}")
    return 0


def cmd_judge(shard: int, shards: int, workers) -> int:
    """Sharded judged-cell burn (checkpoint jsonl per cell, cross-kill
    resume = skip recorded cell_ids; pool shard executor face = the
    screen cmd_run face, r670 tiling + r496 three-call claim)."""
    rc = _judge_freeze_gate("judge")
    if rc:
        return rc
    print(f"=== {JUDGE_BATCH} shard {shard}of{shards} ===")
    if not os.path.exists(JUDGE_STATE_FILE):
        print(f"JUDGE-GATE: judge-prep required first "
              f"({os.path.basename(JUDGE_STATE_FILE)} absent)")
        return 2
    state = json.load(open(JUDGE_STATE_FILE, encoding="utf-8"))
    cands_all = json.load(open(CANDIDATES_FILE,
                               encoding="utf-8"))["candidates"]
    by_id = {c["candidate_id"]: c for c in cands_all}
    a_by_trader = {t["trader_id"]: t for t in tl1.A_TEMPLATES}
    kept = sorted(state["collapse"]["kept"])
    cells = []
    for i, cid in enumerate(kept):
        c = by_id[cid]
        template = (a_by_trader.get(c.get("template_trader"))
                    if c["family"] == "A" else None)
        cells.append({"cell_id": f"JUDGE|{cid}", "candidate_id": cid,
                      "i": i, "cand": c, "template": template})
    mine = [c for i, c in enumerate(cells) if i % shards == shard]
    ram_min, ram_ok = tl2._ram_gate_gb(wait_min=2880)
    if not ram_ok:
        print(f"JUDGE-GATE: free RAM {ram_min}GB < 4GB after bounded "
              "wait (r354 three-sample law; r691 cap window) -- honest "
              "refuse, pool retries when RAM frees")
        return 2
    tl1.GRAMMAR = load_grammar()
    st = {"legs": {}, "starts": state["starts"],
          "passive": state["passive"],
          "seed_judge": state["seed_judge"],
          "grammar": tl1.GRAMMAR,
          "oos_start": pd.Timestamp(tl1.OOS_START)}
    for leg in ("L", "D"):
        prices, P, idx, listed, cen = tl1._load_leg(leg)
        if cen != tl1.FROZEN_CENSUS[leg]:
            print(f"JUDGE-GATE FAIL: leg-{leg} census drift {cen} != "
                  f"{tl1.FROZEN_CENSUS[leg]} (data moved under the "
                  "batch)")
            return 1
        ls = _judge_leg_state(prices, P, _b_layer_fundamental_ok(P),
                              tl1.GRAMMAR)
        ls["idx"] = idx
        st["legs"][leg] = ls
    ck = _judge_ckpt_path(shard, shards)
    os.makedirs(CKPT_DIR, exist_ok=True)
    done = _judge_scan_done(ck)
    todo = [c for c in mine if c["cell_id"] not in done]
    print(f"shard cells {len(mine)}, done {len(done)}, todo {len(todo)}")

    def on_result(key, payload):
        with open(ck, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(tl1._j(payload), ensure_ascii=False,
                                default=float) + "\n")

    if todo:
        jobs = [(c["cell_id"], _judge_cell_w15, (c,)) for c in todo]
        tl1.run_cells_parallel(jobs, workers=workers or tl1.worker_cap(),
                               desc=f"n2w15 judge s{shard}",
                               initializer=tl1._init_worker,
                               initargs=(st,), on_result=on_result)
    done_after = _judge_scan_done(ck)
    missing_mine = [c["cell_id"] for c in mine
                    if c["cell_id"] not in done_after]
    if missing_mine:
        print(f"JUDGE-INCOMPLETE: {len(missing_mine)}/{len(mine)} shard "
              f"cells absent post-burn (checkpoint retained, honest "
              "refuse, NO pool claim); first missing: "
              f"{missing_mine[:3]}")
        return 2
    # r708 claim-dir canon fix: the worker claim must land in the
    # per-shard entry dir (harvest scan matches claims/<entry_id>/ ==
    # pool entry id, r496/r201 contract); JUDGE_BATCH here left 10
    # closed claims invisible to the harvest flip (ghost-ready family).
    _pool_claim(f"PERPETUAL-N2-W15-JUDGE-SHARD-{shard}",
                f"n2w15judge-{shard}of{shards}",
                f"{len(mine)} judged cells done, ckpt "
                f"{os.path.basename(ck)}")
    print(f"shard {shard}of{shards} complete -> {ck} ({len(mine)} "
          "cells, pool claim closed)")
    return 0


def _d6_corr_cell(s: pd.Series, member_rets: dict) -> dict:
    """Pure D6 correlation face for one candidate daily-return series
    vs a dict of registered-member daily-return series (inner-date
    alignment only; overlap < D6_MIN_OVERLAP = honest
    insufficient-overlap, never a positional correlation)."""
    best, arg, min_ov = 0.0, None, None
    for tid, mr in member_rets.items():
        a, b = s.align(mr, join="inner")
        if len(a) < D6_MIN_OVERLAP:
            continue
        cc = abs(float(a.corr(b)))
        if not np.isfinite(cc):
            continue
        ov = len(a)
        if min_ov is None or ov < min_ov:
            min_ov = ov
        if cc > best:
            best, arg = cc, tid
    if arg is None:
        return {"max_corr_vs_registered": None, "argmax": None,
                "min_overlap_days": min_ov,
                "note": f"no member with >= {D6_MIN_OVERLAP} overlap "
                        "days -- insufficient-overlap disclosure"}
    return {"max_corr_vs_registered": round(best, 4), "argmax": arg,
            "min_overlap_days": min_ov}


def _d6_registered_face(judged: list) -> dict:
    """D6 (sec.9 operative face): per judged cell max|corr| vs the
    registered six members' daily returns -- ew6 canon member_run face
    (cn_rev_tilt_p1 load_member_rets precedent, r280 law; IDENTICAL
    code path to the live.paper anchor gate); leg-L dates rebuilt from
    the panel for honest date alignment."""
    import ew6_portfolio as E
    from live.paper import load_core
    if E.PRICES_FULL is None:
        E.PRICES_FULL = load_core()
    member_rets, cutoffs = {}, {}
    for tid in REG6:
        r = E.member_run(tid)
        eq = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        member_rets[tid] = eq.pct_change().dropna()
        cutoffs[tid] = r.get("cutoff")
    prices, P, idx, listed, cen = tl1._load_leg("L")
    cells = {}
    for r in judged:
        daily = r["legL_daily_returns"]
        if len(daily) != len(idx):
            cells[r["candidate_id"]] = {
                "max_corr_vs_registered": None, "argmax": None,
                "note": f"curve length {len(daily)} != leg-L panel "
                        f"{len(idx)} -- length drift, no positional "
                        "correlation (honest disclosure)"}
            continue
        s = pd.Series(daily, index=idx)
        cells[r["candidate_id"]] = _d6_corr_cell(s, member_rets)
    return {"reject_line": D6_REJECT_LINE,
            "members": list(REG6), "member_cutoffs": cutoffs,
            "caliber": "ew6 canon member_run daily returns (registered "
                       "6 members); same-batch same-family face "
                       "already enforced at entry by the 0.999 "
                       "collapse; overlap floor "
                       f"{D6_MIN_OVERLAP} days",
            "cells": cells}


def cmd_judge_finalize() -> int:
    """Aggregate judge shards -> G1'v2 + DSR + family PBO (CSCV 8
    blocks, family = A/B grammar family) + G2 + D6 (vs REG6, ew6
    canon) + E[FP] + verdicts + ledger append PERPETUAL-N2-W15-JUDGE
    (single-shot guard pit-95; refinalize env = only redo)."""
    rc = _judge_freeze_gate("judge-finalize")
    if rc:
        return rc
    print(f"=== {JUDGE_BATCH} judge-finalize ===")
    if not os.path.exists(JUDGE_STATE_FILE):
        print(f"FINALIZE-GATE: {os.path.basename(JUDGE_STATE_FILE)} "
              "absent (judge-prep first)")
        return 2
    n_eff_override = None
    redo_dsr_trials = None
    if os.path.exists(JUDGE_OUT_FILE):
        prev = json.load(open(JUDGE_OUT_FILE, encoding="utf-8"))
        if prev.get("complete") and "trials_ledger" in prev:
            if not os.environ.get(JUDGE_REFINALIZE_ENV):
                print(f"judge-finalize: complete product exists "
                      f"(idempotent no-op; set {JUDGE_REFINALIZE_ENV}=1 "
                      "to redo)")
                return 0
            n_eff_override = (int(prev["trials_ledger"]["prev_total"])
                              + int(prev["trials_ledger"]["batch_trials"]))
            redo_dsr_trials = int(prev["trials_ledger"]["prev_total"])
    state = json.load(open(JUDGE_STATE_FILE, encoding="utf-8"))
    kept = sorted(state["collapse"]["kept"])
    rows = []
    for f in sorted(os.listdir(CKPT_DIR)):
        if (f.startswith("n2_w15_judge_shard_")
                and f.endswith(".jsonl")):
            with open(os.path.join(CKPT_DIR, f), encoding="utf-8") as fh:
                for ln in fh:
                    if ln.strip():
                        rows.append(json.loads(ln))
    by_id = {r["cell_id"]: r for r in rows}
    missing = [f"JUDGE|{cid}" for cid in kept
               if f"JUDGE|{cid}" not in by_id]
    if missing:
        print(f"FINALIZE-GATE: {len(missing)} judged cells incomplete; "
              "refused (checkpoints retained)")
        return 2
    judged = [by_id[f"JUDGE|{cid}"] for cid in kept]
    n_judge = len(judged)
    n_trials = (redo_dsr_trials if redo_dsr_trials is not None
                else sg.ledger_head()["total"])
    for r in judged:
        rets = r["legL_daily_returns"]
        g1 = sg.g1_prime_v2(r["legs"]["L"]["x1"]["sharpe_full"], rets,
                            n_judge, pool="core48",
                            n_trades=r["legs"]["L"]["x1"]["n_trades"],
                            n_entries=r["legs"]["L"]["x1"]["n_entries"],
                            n_eff_override=n_eff_override)
        dsr = sg.deflated_sharpe_ratio(rets, n_trials=n_trials)
        r["g1_prime_v2"] = g1
        r["dsr"] = dsr
        r["g1_pass"] = g1["pass_v2"]
        r["verdict"] = ("pass" if (g1["pass_v2"]
                                   and r["sample_sufficient"])
                        else "insufficient-sample"
                        if not r["sample_sufficient"] else "fail")
    # family PBO (CSCV 8 blocks; family = grammar family A/B)
    fam_map = {}
    for r in judged:
        fam_map.setdefault(r["family"], []).append(r)
    pbos = {}
    for fam, rs in fam_map.items():
        if len(rs) < 8:
            pbos[fam] = {"pbo": None, "n_cells": len(rs),
                         "note": "insufficient (<8) -- G2 cannot pass"}
            for r in rs:
                r["family_pbo"] = None
            continue
        series = {r["candidate_id"]: pd.Series(r["legL_daily_returns"])
                  for r in rs}
        pbo = tl1.cscv_pbo(tl1.align_returns(series))
        pbo_val = pbo["pbo"] if isinstance(pbo, dict) else pbo
        pbos[fam] = {"pbo": round(float(pbo_val), 4),
                     "n_cells": len(rs)}
        for r in rs:
            r["family_pbo"] = pbos[fam]["pbo"]
    # D6 vs REG6 registered members (sec.9 operative face)
    d6 = _d6_registered_face(judged)
    for r in judged:
        r["g2_registration_v2"] = sg.g2_registration_v2(
            r["g1_pass"], r["dsr"], r.get("family_pbo"))
        r["d6"] = d6["cells"][r["candidate_id"]]
        r["d6_ok"] = bool(
            r["d6"].get("max_corr_vs_registered") is not None
            and r["d6"]["max_corr_vs_registered"] < D6_REJECT_LINE)
    eligible = [r["candidate_id"] for r in judged
                if r["g2_registration_v2"]["eligible_v2"] and r["d6_ok"]]
    e_fp = round(0.05 * n_judge, 2)
    out_rel = "n2_w15/" + os.path.basename(JUDGE_OUT_FILE)
    ledger = tl1.append_ledger(JUDGE_BATCH, n_judge, file_name=out_rel,
                               evidence_cutoff=CUTOFF,
                               note=f"T-133 s2 N2-W15 judge: {n_judge} "
                                    f"collapsed cells from "
                                    f"{state['n_stage1_survivors']} "
                                    "stage-1 survivors")
    desc_agg = {cl: sum(1 for r in judged if r["descriptive"][cl])
                for cl in ("ann_pos", "oos_dual_pos", "dd_ok",
                           "no_crash_year", "x2_yearly_stable")}
    summary = {
        "batch": JUDGE_BATCH, "evidence_cutoff": CUTOFF,
        **tl1.cutoff_meta(CUTOFF),
        "trials_ledger": ledger,
        "n_judge_cells": n_judge,
        "n_stage1_survivors": state["n_stage1_survivors"],
        "candidates_sha256_16": state["candidates_sha256_16"],
        "screen_ref": state["screen_ref"],
        "collapse_audit": {"line": JUDGE_COLLAPSE_LINE,
                           "eliminated": state["collapse"]["eliminated"],
                           "clusters": state["collapse"]["clusters"]},
        "n_wave_disclosure": {
            "screen_cells": 1154,
            "judged_cells": n_judge, "E_FP_nominal_5pct": e_fp,
            "note": "DSR>=0.95 gate IS the multiple-testing correction "
                    "(cumulative N deflation via live ledger-head "
                    "n_trials -- cross-wave N_eff never reset, prereg "
                    "sec.9); E[FP] disclosed at nominal 5% caliber"},
        "n_trials_head_at_finalize": n_trials,
        "family_pbo": pbos,
        "d6": d6,
        "descriptive_counts": desc_agg,
        "eligible_g2_d6": eligible, "n_eligible_g2_d6": len(eligible),
        "verdicts": {v: sum(1 for r in judged if r["verdict"] == v)
                     for v in ("pass", "fail", "insufficient-sample")},
        "cells": [{k: v for k, v in r.items()
                   if k != "legL_daily_returns"} for r in judged],
        "audit": {
            "judged_face": "legs L/D x cost x1/x2 x windows "
                           "{126,252,504} sliced from full curves "
                           "(p5c FROZEN_CENSUS caliber) + regime "
                           "segments (T-22 sec.3 3-way proxy) + dual "
                           "nulls (B=2000 block=20 circular + P=2000 "
                           "sign-flip, rng=["
                           f"{state['seed_judge']}, i]); replay via "
                           "tl14.run_candidate_curve_w14 screen stack "
                           "zero-migration; Sharpe gates on leg-L x1; "
                           "x2 = cost-stability descriptive; D6 vs "
                           "REG6 ew6 canon daily returns",
            "seed_judge": state["seed_judge"],
            "legs": state["legs"],
        },
        "complete": True,
        "generated": _now_iso(), "machine": _machine_id(),
    }
    tl1._dump(JUDGE_OUT_FILE, summary)
    print(f"judge-finalize: {n_judge} judged cells, E[FP]={e_fp}, "
          f"G2+D6 eligible {len(eligible)} -> {eligible[:10]}")
    return 0


# ------------------------------------------------------------- status face
def cmd_status() -> int:
    """Read-only inventory (no engine, no network beyond repo files)."""
    grammar = load_grammar()
    n_a = len(grammar["families"]["A"])
    n_b = len(grammar["families"]["B"])
    nn_sizes = [len(d) for d in OVERLAY_NON_NONE]
    prod = 1
    for n in nn_sizes:
        prod *= (n + 1)          # none-or-active per overlay axis
    base = (len(tl1.AXIS_FILTERS) * len(tl1.AXIS_EXITS)
            * len(tl1.AXIS_SIZING) * len(tl1.AXIS_TIMING))
    shard_dir = os.path.join(tl1.PATHS.results_dir, "n2_w15")
    shards = sorted(os.listdir(shard_dir)) if os.path.isdir(shard_dir) \
        else []
    print(f"=== {BATCH} status ===")
    print(f"grammar: frozen 18-tuple library sha16="
          f"{FROZEN_GRAMMAR_SHA16} cutoff={CUTOFF}")
    print(f"family slots: A={n_a} B={n_b} total={n_a + n_b}")
    print(f"subspace axes: {N_OVERLAY} overlays, non-none domains "
          f"{nn_sizes}")
    print(f"axis space: base {base:,} x overlay {prod:,} = "
          f"{base * prod:,} (independent-domain face)")
    print(f"prereg: {PREREG}")
    print(f"proposed bands (freeze-time registration): gen={BAND_GEN} "
          f"scrnull={BAND_SCRNULL} unc={BAND_UNC} width={BAND_WIDTH}")
    print(f"probe product: {os.path.basename(PROBE_OUT)} "
          f"({'present' if os.path.exists(PROBE_OUT) else 'absent'})")
    print(f"shard dir results/n2_w15: {len(shards)} files "
          f"{shards[:6]}")
    frozen_ok, bad = _bands_registered()
    print(f"freeze gate: bands registered={frozen_ok}"
          + (f" (drift: {bad})" if bad else ""))
    print("runner legs: slice-1 (probe/status/selftest) + slice-2 "
          "(generate/screen-prep/run/screen-finalize/finalize) landed "
          "@ r692 bm-a (Plan A adoption per MSG-2026-10-04-1845); "
          "slice-4 judge legs (judge-prep/judge/judge-finalize, sec.9.1) "
          "landed @ r702 bm-b -- burns freeze-gated on the base trio + "
          f"judge berth {JUDGE_BER} (sec.9.1 freeze commit)")
    jok = _judge_band_registered()
    print(f"judge freeze gate: berth registered={jok}")
    return 0


# ----------------------------------------------------------- selftest face
def _leg(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
          + (f" | {detail}" if detail else ""))
    return bool(ok)


def cmd_selftest() -> int:
    """Hermetic offline legs (zero network, zero engine runs, zero
    ledger writes)."""
    print(f"=== {BATCH} selftest (hermetic) ===")
    ok = True
    # L1 import-face + grammar determinism (pure compute)
    g1 = tl14.build_grammar_w14()
    g2 = tl14.build_grammar_w14()
    ok &= _leg("L1 import-face + grammar determinism",
               str(g1.get("grammar_sha256"))[:16]
               == str(g2.get("grammar_sha256"))[:16]
               == FROZEN_GRAMMAR_SHA16,
               f"sha16={FROZEN_GRAMMAR_SHA16} families "
               f"A={len(g1['families']['A'])} "
               f"B={len(g1['families']['B'])}")
    # L2 subspace draw determinism
    d1 = list(draw_candidate_subspace_w15(g1, "A", 0, 8, PROBE_SEED))
    d2 = list(draw_candidate_subspace_w15(g2, "A", 0, 8, PROBE_SEED))
    same = all(json.dumps(a[1], sort_keys=True, default=float)
               == json.dumps(b[1], sort_keys=True, default=float)
               for a, b in zip(d1, d2))
    ok &= _leg("L2 subspace draw determinism (same seed byte-equal)",
               same and len(d1) == 8)
    d3 = list(draw_candidate_subspace_w15(g1, "A", 0, 8, PROBE_SEED + 1))
    diff = any(json.dumps(a[1], sort_keys=True, default=float)
               != json.dumps(b[1], sort_keys=True, default=float)
               for a, b in zip(d1, d3))
    ok &= _leg("L2b seed sensitivity (different seed -> different "
               "draws)", diff)
    # L3 subspace shape law: base 4 + 14 overlay slots; active in
    # [1..14]; inactive pinned none; active values in non-none domain
    shape_ok = True
    for _, c in d1 + d3:
        ax = c["axis"]
        if len(ax) != 4 + N_OVERLAY:
            shape_ok = False
        if not (1 <= c["subspace_k"] <= N_OVERLAY):
            shape_ok = False
        if len(set(c["subspace_active"])) != c["subspace_k"]:
            shape_ok = False
        for pos in range(N_OVERLAY):
            v = ax[4 + pos]
            if c["subspace_k"] and OVERLAY_AXES[pos][0] \
                    in c["subspace_active"]:
                if v == "none" or v not in OVERLAY_NON_NONE[pos]:
                    shape_ok = False
            else:
                if v != "none":
                    shape_ok = False
    ok &= _leg("L3 subspace shape law (cardinality/subset/pinning/"
               "domains)", shape_ok,
               f"sample k={[c['subspace_k'] for _, c in d1]}")
    # L4 seed-band disjoint machine check (proposed bands vs
    # SEED_REGISTRY + declared N1 bands + N3 berth)
    reg = {k: v for k, v in sg.SEED_REGISTRY.items()
           if isinstance(v, (int, float))}
    bands = [("gen", BAND_GEN), ("scrnull", BAND_SCRNULL),
             ("unc", BAND_UNC)]
    own = {"perpetual_n2_w15_gen", "perpetual_n2_w15_scrnull",
           "perpetual_n2_w15_unc"}   # post-freeze own berths are not
    # collisions; value exactness is separately enforced by
    # _bands_registered at every burn leg (r675 posture-aware guard law:
    # same-batch variant -- guards written at DRAFT must survive the
    # freeze posture flip)
    hits = []
    for nm, base in bands:
        lo, hi = base, base + BAND_WIDTH
        for k, v in reg.items():
            if k in own:
                continue
            if lo <= float(v) <= hi:
                hits.append(f"{nm}~{k}@{int(v)}")
    # N1 in-use bands: LIVE derive from the N1 runner ledger (r492
    # freeze-window root-cause fix -- the slice-1 hand-copied list was a
    # W2..W7 stale snapshot which hid W8 A 30_100..32_099 and let the
    # original 31_000/31_500/32_000 pick through; import-face derive,
    # never hand-copy) + N3 70_000..70_999 berth
    import perpetual_faces as _n1mod
    n1_ranges = [(b["a"][0], b["a"][1])
                 for b in _n1mod.N1_BANDS.values()]
    n1_ranges += [(b["b_exit"][0], b["b_exit"][1])
                  for b in _n1mod.N1_BANDS.values()]
    n3_range = (70_000, 70_999)
    for nm, base in bands:
        lo, hi = base, base + BAND_WIDTH
        for a, b in n1_ranges + [n3_range]:
            if not (hi < a or lo > b):
                hits.append(f"{nm}~N1/N3-band[{a}..{b}]")
    for nm, base in bands:
        if any(a <= base <= b for a, b in n1_ranges + [n3_range]):
            hits.append(f"{nm}~inside N1/N3")
    probe_hit = [k for k, v in reg.items()
                 if float(v) in (95_002, 95_003, 95_004)]
    ok &= _leg("L4 seed-band disjoint machine check (30_000+ law "
               "域外顺延)", not hits and not probe_hit,
               f"hits={hits or 'none'} probe_hit={probe_hit or 'none'} "
               f"registry_n={len(reg)}")
    # L5 pool handshake parity (N1 canon three-call face)
    import inspect
    sig_claim = str(inspect.signature(_pool_claim))
    sig_shard = str(inspect.signature(entry_shard_of))
    ok &= _leg("L5 pool handshake parity (r496 canon)",
               "entry_id" in sig_claim and "shard_key" in sig_claim
               and "shard" in sig_shard and "nshards" in sig_shard,
               f"claim{sig_claim} shard{sig_shard}")
    # L6 frozen constants + cutoff same-window + probe out-of-band
    ok &= _leg("L6 frozen constants (cutoff same-window, wave, "
               "out-of-band probe)",
               CUTOFF == tl14.CUTOFF == "2026-09-22" and WAVE == 15
               and PROBE_SEED >= 95_000
               and PROBE_SEED not in set(reg.values()))
    # L7 axis import-face parity (module constants, not hand-copies)
    parity = (OVERLAY_AXES[0][1] is tl2.AXIS_STOP
              and OVERLAY_AXES[5][1] is tl7.AXIS_STREAK
              and OVERLAY_AXES[13][1] is tl14.AXIS_CNT)
    ok &= _leg("L7 overlay axis import-face parity (module-sourced)",
               parity)
    # L8 freeze-gate face (R99/R250): registered registry -> open;
    # missing/drifted -> refuse (in-memory simulation, zero file
    # writes; the LIVE registry state is disclosed, not asserted)
    live_ok, live_bad = _bands_registered()
    saved = {k: sg.SEED_REGISTRY.get(k) for k in
             ("perpetual_n2_w15_gen", "perpetual_n2_w15_scrnull",
              "perpetual_n2_w15_unc")}
    try:
        for k in saved:        # explicit unregister sim: pop keys
            sg.SEED_REGISTRY.pop(k, None)   # (DRAFT-era update(saved) was
        sim_bad = _bands_registered()       # a None-write; post-freeze
        # live keys would survive it and the refuse direction went
        # unverified -- r675 posture-aware law)
        sg.SEED_REGISTRY["perpetual_n2_w15_gen"] = BAND_GEN
        sg.SEED_REGISTRY["perpetual_n2_w15_scrnull"] = BAND_SCRNULL
        sg.SEED_REGISTRY["perpetual_n2_w15_unc"] = BAND_UNC
        sim_ok = _bands_registered()
    finally:
        for k, v in saved.items():
            if v is None:
                sg.SEED_REGISTRY.pop(k, None)
            else:
                sg.SEED_REGISTRY[k] = v
    ok &= _leg("L8 freeze-gate face (R99/R250 band registration)",
               (not sim_bad[0]) and sim_ok[0],
               f"live registered={live_ok} (live posture disclosed "
               f"honestly: pre-freeze=False DRAFT, post-freeze=True "
               f"FROZEN); unregistered->refuse, registered->open "
               f"both verified in-memory")
    # L9 exclusion import-face real-read: 28-source rows load non-
    # empty and a W15 subspace draw (new-syntax face) passes clean
    excl_rows, _disc = tl14._load_exclusion_rows_w14(g1)
    probe_cand = list(draw_candidate_subspace_w15(
        g1, "B", 0, 4, PROBE_SEED))[0][1]
    excl_hit = tl14._excluded_w14(probe_cand, excl_rows)
    ok &= _leg("L9 exclusion import-face real-read (tl14 28-source)",
               len(excl_rows) > 0 and not excl_hit,
               f"rows={len(excl_rows)}, W15 new-syntax draw "
               f"excluded={bool(excl_hit)} (legal non-exclusion face)")
    # L10 dedup collapse face (factored T-84s3 law): identical
    # fingerprints collapse keep-lowest-id; |corr|>=0.999 twins
    # (including anti-correlated twins) collapse keep-lowest-id;
    # distinct survive.  W14 caliber: fp_collapsed lists EVERY group
    # (singletons carry empty eliminated lists).
    cands = [{"candidate_id": f"SYN-{i:02d}"} for i in range(5)]
    base = np.array([0.01, -0.02, 0.03, -0.01, 0.02, 0.015])
    series = [base, base * 2.0, base * 1.0 + 1e-9,
              -base, np.array([0.5, 0.4, 0.6, 0.2, 0.1, 0.3])]
    fps = [hash("a"), hash("a"), hash("b"), hash("c"), hash("d")]
    keep, fp_col, corr_elim = _collapse_by_fingerprint(fps, series,
                                                      cands)
    kept_ids = sorted(cands[i]["candidate_id"] for i in keep)
    corr_elim_ids = sorted({e["eliminated"] for e in corr_elim})
    ok &= _leg("L10 dedup collapse face (fp keep-lowest + |corr| 0.999)",
               kept_ids == ["SYN-00", "SYN-04"]
               and len(fp_col) == 4
               and corr_elim_ids == ["SYN-02", "SYN-03"],
               f"kept={kept_ids} fp_groups={len(fp_col)} "
               f"corr_eliminated={corr_elim_ids}")
    # L11 shard tiling law (r670): i % shards split covers every cell
    # exactly once across shards (union == all, pairwise disjoint)
    cells = list(range(5200))        # prereg-scale synthetic census
    for shards in (12, 7, 1):
        mine = [[c for i, c in enumerate(cells)
                 if i % shards == s] for s in range(shards)]
        union = sorted(x for part in mine for x in part)
        tiling_ok = (union == cells
                     and sum(len(p) for p in mine) == len(cells))
        if not tiling_ok:
            break
    ok &= _leg("L11 shard tiling law (r670: union==all exactly once)",
               tiling_ok, f"shards in {12, 7, 1} over {len(cells)} cells")
    # L12 checkpoint scanner pairing (r670): scanner reads the EXACT
    # filename cmd_run writes; full row counts done, truncated/poison
    # rows never count (non-empty payload law) -- tempdir, zero repo
    # writes
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ck = os.path.join(td, "n2_screen_shard_3of12.jsonl")
        with open(ck, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(
                {"cell_id": "SCREEN|X-0001", "family": "B",
                 "beat6m_n": 1253, "beat6m_rate": 0.31}) + "\n")
            fh.write('{"cell_id": "SCREEN|X-0002", "family": "B"}\n')
            fh.write('{"cell_id": "SCREEN|X-0003"}\n')
            fh.write("not-json-garbage\n")
        done = _scan_done(ck)
        scan_ok = (done == {"SCREEN|X-0001"}
                   and os.path.basename(_ckpt_path(3, 12))
                   == "n2_screen_shard_3of12.jsonl")
    ok &= _leg("L12 checkpoint scanner pairing (r670 non-empty law)",
               scan_ok,
               f"done={sorted(done)}; poison rows correctly skipped")
    # L13 null draw face (scrnull berth): determinism + p_on domain +
    # 18-tuple shape + same consumption order as tl14 caliber
    p1, ax1, r1 = _null_axis_draw_w15(0)
    p2, ax2, _r2 = _null_axis_draw_w15(0)
    p3, ax3, _r3 = _null_axis_draw_w15(1)
    null_ok = (p1 == p2 and ax1 == ax2 and p1 in tl1.NULL_P_REGIMES
               and len(ax1) == 4 + N_OVERLAY
               and (p1 != p3 or ax1 != ax3))
    ok &= _leg("L13 null draw face (scrnull berth 542_000, tl14 "
               "same-face order)", null_ok,
               f"p_on={p1} axis_len={len(ax1)} "
               f"deterministic+seed-sensitive")
    # L14 beat6m math face (factored W14 caliber): >= comparison,
    # binom z/p, full 126-td window coverage on a synthetic curve
    n_eq = W6M + 4
    eq = pd.Series(np.linspace(1.0, 1.10, n_eq))
    starts = [0, 2]
    passive = {0: 0.01, 2: 0.05}
    row = _beat6m_row(eq, {"num_trades": 3, "num_entries": 2}, starts,
                      passive)
    k_exp = sum(1 for p in starts
                if float(eq.iloc[p + W6M - 1] / eq.iloc[p] - 1.0)
                >= passive[p])
    row_probe = {k: row[k] for k in ("beat6m_k", "beat6m_n",
                                     "beat6m_rate", "binom_z")}
    ok &= _leg("L14 beat6m math face (>= literal, binom z/p)",
               row["beat6m_n"] == 2 and row["beat6m_k"] == int(k_exp)
               and row["beat6m_rate"] == round(int(k_exp) / 2, 6)
               and abs(row["binom_z"]) > 0 and row["n_trades"] == 3,
               f"row={row_probe}")
    # L15 survival-math import face: run the REAL tl2._finalize_math
    # on synthetic rows (p95 = percentile-95 of null rates; survive
    # iff rate > p95; mutation + survivors-list contract)
    synth_cands = [{"candidate_id": "SYN-HI", "beat6m_rate": 0.90},
                   {"candidate_id": "SYN-LO", "beat6m_rate": 0.10}]
    synth_nulls = [{"beat6m_rate": r} for r in
                   (0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                    0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85,
                    0.88, 0.89)]
    p95_synth, surv_synth = tl2._finalize_math(synth_cands, synth_nulls)
    p95_exp = float(np.percentile([r["beat6m_rate"]
                                   for r in synth_nulls], 95))
    ok &= _leg("L15 survival math import face (tl2._finalize_math "
               "real run)", p95_synth == p95_exp
               and surv_synth == ["SYN-HI"]
               and synth_cands[1]["survives_screen"] is False,
               f"p95={p95_synth} survivors={surv_synth}")
    # L16 pool claim payload face (r496 canon): payload builder keys +
    # entry/shard identity wiring
    claim = _claim_payload("selftest detail")
    ok &= _leg("L16 pool claim payload face (r496 three-call canon)",
               all(k in claim for k in
                   ("machine_id", "state", "pid", "outcome",
                    "exit_code", "closed_at", "result_ref"))
               and claim["state"] == "closed"
               and claim["exit_code"] == 0
               and entry_shard_of(3, 12)
               == ("PERPETUAL-N2-W15-SHARD-3", "n2w15-3of12"),
               f"keys ok, ids={entry_shard_of(3, 12)}")
    # L17 product-path wiring: all slice-2 products under
    # results/n2_w15/, ckpt filename matches the scanner glob prefix,
    # ledger batch name frozen
    ok &= _leg("L17 product-path wiring (files/batch/ckpt glob)",
               os.path.dirname(CANDIDATES_FILE)
               .endswith(os.path.join("results", "n2_w15"))
               and os.path.basename(_ckpt_path(0, NSHARDS))
               .startswith("n2_screen_shard_")
               and BATCH_SCREEN == "PERPETUAL-N2-W15-SCREEN"
               and WAVE_RESULTS.endswith("n2_w15_wave_results.json"),
               f"ckpt={os.path.basename(_ckpt_path(0, NSHARDS))} "
               f"batch={BATCH_SCREEN}")
    # L18 judge freeze-gate face (R99/R250): base trio + judge berth
    # registered -> open; berth missing -> refuse (in-memory sim, zero
    # file writes; live posture disclosed not asserted)
    live_j = _judge_band_registered()
    saved_j = sg.SEED_REGISTRY.get(JUDGE_BER)
    try:
        sg.SEED_REGISTRY.pop(JUDGE_BER, None)
        sim_refuse = _judge_freeze_gate("selftest-judge")
        sg.SEED_REGISTRY[JUDGE_BER] = 545_000
        sim_open = _judge_freeze_gate("selftest-judge")
    finally:
        if saved_j is None:
            sg.SEED_REGISTRY.pop(JUDGE_BER, None)
        else:
            sg.SEED_REGISTRY[JUDGE_BER] = saved_j
    ok &= _leg("L18 judge freeze-gate face (berth registration)",
               sim_refuse == 2 and sim_open == 0,
               f"live registered={live_j} (posture disclosed "
               "honestly); unregistered->rc2, registered->rc0 both "
               "verified in-memory")
    # L19 judge checkpoint scanner pairing (r670 non-empty law):
    # scanner reads the EXACT filename cmd_judge writes; full judged
    # rows count, screen-shaped rows never count
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        jck = os.path.join(td, "n2_w15_judge_shard_5of12.jsonl")
        with open(jck, "w", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps({"cell_id": "JUDGE|X-1", "legs":
                                 {"L": {}},
                                 "legL_daily_returns": [0.01]}) + "\n")
            fh.write('{"cell_id": "JUDGE|X-2", "legs": {"L": {}}}\n')
            fh.write('{"cell_id": "JUDGE|X-3"}\n')
            fh.write("garbage\n")
        jdone = _judge_scan_done(jck)
        scan_j_ok = (jdone == {"JUDGE|X-1"}
                     and os.path.basename(_judge_ckpt_path(5, 12))
                     == "n2_w15_judge_shard_5of12.jsonl")
    ok &= _leg("L19 judge ckpt scanner pairing (r670 non-empty law)",
               scan_j_ok,
               f"done={sorted(jdone)}; partial/poison rows skipped")
    # L20 collapse import face (mass_trial_w1._collapse_survivors real
    # run): corr>=0.999 twins + anti-correlated twins collapse
    # keep-lowest-id; distinct survive
    base = np.array([0.02, -0.01, 0.03, -0.02, 0.01, 0.015])
    rets_df = pd.DataFrame({
        "C-00": base, "C-01": base * 1.0000001, "C-02": -base,
        "C-03": np.array([0.5, 0.2, -0.1, 0.3, 0.4, -0.2])})
    kept_j, clusters_j, elim_j = mtw1._collapse_survivors(
        rets_df, line=JUDGE_COLLAPSE_LINE)
    ok &= _leg("L20 collapse import face (mtw1 real run, 0.999)",
                kept_j == ["C-00", "C-03"]
                and sorted(clusters_j.get("C-00", [])) == ["C-01",
                                                           "C-02"],
                f"kept={kept_j} clusters={clusters_j}")
    # L21 dual-nulls import face (mtw1 real run): seed pin ->
    # identical output; B/P/block frozen shape
    dn1 = mtw1._dual_nulls(list(base), 7, seed=545_000)
    dn2 = mtw1._dual_nulls(list(base), 7, seed=545_000)
    dn3 = mtw1._dual_nulls(list(base), 8, seed=545_000)
    ok &= _leg("L21 dual-nulls import face (mtw1 seed pin)",
                dn1 == dn2 and dn1 != dn3 and dn1["B"] == 2000
                and dn1["P"] == 2000 and dn1["block"] == 20,
                f"B={dn1['B']} P={dn1['P']} block={dn1['block']} "
                f"deterministic+cell-sensitive")
    # L22 judge product-path wiring: judge products under
    # results/n2_w15/, ckpt prefix distinct from screen shards, batch
    # name frozen, D6 constants frozen
    ok &= _leg("L22 judge path/batch/D6 wiring",
                os.path.dirname(JUDGE_STATE_FILE)
                .endswith(os.path.join("results", "n2_w15"))
                and os.path.basename(_judge_ckpt_path(0,
                                                     JUDGE_SHARDS_DEFAULT))
                .startswith("n2_w15_judge_shard_")
                and not os.path.basename(
                    _judge_ckpt_path(0, JUDGE_SHARDS_DEFAULT)
                ).startswith("n2_screen_shard_")
                and JUDGE_BATCH == "PERPETUAL-N2-W15-JUDGE"
                and JUDGE_BER == "perpetual_n2_w15_judge"
                and D6_REJECT_LINE == 0.7 and len(REG6) == 6
                and JUDGE_COLLAPSE_LINE == 0.999,
                f"batch={JUDGE_BATCH} ber={JUDGE_BER} "
                f"d6_line={D6_REJECT_LINE}")
    # L23 D6 pure corr face (hermetic): identical series -> 1.0 reject
    # face; orthogonal -> pass face; short overlap -> honest None
    idxs = pd.date_range("2026-01-01", periods=200, freq="D")
    s_twin = pd.Series(list(np.resize(base, 200)), index=idxs)
    s_orth = pd.Series(
        (np.cos(np.arange(200) * 2.0)).tolist(), index=idxs)
    members = {"MEMBER-A": s_twin.copy(),
               "MEMBER-B": pd.Series(0.0, index=idxs[:10])}
    d6_twin = _d6_corr_cell(s_twin, members)
    d6_orth = _d6_corr_cell(s_orth, members)
    d6_none = _d6_corr_cell(s_twin, {"MEMBER-B":
                                      pd.Series(0.0,
                                                index=idxs[:10])})
    ok &= _leg("L23 D6 pure corr face (twin reject/orth pass/"
               "overlap-honest)",
                d6_twin["max_corr_vs_registered"] == 1.0
                and d6_twin["argmax"] == "MEMBER-A"
                and d6_orth["max_corr_vs_registered"] < 0.7
                and d6_none["max_corr_vs_registered"] is None,
                f"twin={d6_twin['max_corr_vs_registered']} "
                f"orth={d6_orth['max_corr_vs_registered']} "
                f"short={d6_none['max_corr_vs_registered']}")
    print("ALL PASS" if ok else "FAIL PRESENT")
    return 0 if ok else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="perpetual_faces_n2")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    sub.add_parser("status")
    sub.add_parser("selftest")
    sub.add_parser("generate")
    sub.add_parser("screen-prep")
    r = sub.add_parser("run")
    r.add_argument("--shard", type=int, required=True)
    r.add_argument("--shards", type=int, default=NSHARDS)
    r.add_argument("--workers", type=int, default=None)
    sub.add_parser("screen-finalize")
    sub.add_parser("finalize")
    sub.add_parser("judge-prep")
    jr = sub.add_parser("judge")
    jr.add_argument("--shard", type=int, required=True)
    jr.add_argument("--shards", type=int, default=JUDGE_SHARDS_DEFAULT)
    jr.add_argument("--workers", type=int, default=None)
    sub.add_parser("judge-finalize")
    a = p.parse_args(argv)
    if a.cmd == "probe":
        return cmd_probe()
    if a.cmd == "status":
        return cmd_status()
    if a.cmd == "selftest":
        return cmd_selftest()
    if a.cmd == "generate":
        return cmd_generate()
    if a.cmd == "screen-prep":
        return cmd_screen_prep()
    if a.cmd == "run":
        return cmd_run(a.shard, a.shards, a.workers)
    if a.cmd == "screen-finalize":
        return cmd_screen_finalize()
    if a.cmd == "finalize":
        return cmd_finalize()
    if a.cmd == "judge-prep":
        return cmd_judge_prep()
    if a.cmd == "judge":
        return cmd_judge(a.shard, a.shards, a.workers)
    if a.cmd == "judge-finalize":
        return cmd_judge_finalize()
    return 2


if __name__ == "__main__":
    sys.exit(main())
