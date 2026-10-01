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

Subcommands (slice-1; run/screen/finalize/supply land with the freeze
window per the prereg draft sequencing):
  probe        2 out-of-band subspace draws (seeds 95_004, ledger +0,
               zero registry, design face only) through the real
               tl14 engine face -> results/perpetual_faces/
               _n2_w15_probe.json (N1 95_002/95_003 probe precedent)
  status       read-only inventory (grammar, family slots, subspace
               size, shard/product presence)
  selftest     hermetic offline legs (zero network, zero engine):
               import face + grammar determinism, subspace draw
               determinism + shape law, seed-band disjoint machine
               check vs SEED_REGISTRY, pool handshake parity

Seed bands (law sec.4 N2/N4 row: N2 packs from 30_000+ outside every
registered band; lfc_p1_screen=30_000 in use -> first free window):
  PROPOSED (registered only at the freeze commit):
    perpetual_n2_w15_gen     = 31_000   (Sobol + axis stream)
    perpetual_n2_w15_scrnull = 31_500   (screen null family)
    perpetual_n2_w15_unc     = 32_000   (uncertainty resample)
  Probe seeds 95_004/95_005 = out-of-band design probes (N1 95_002/
  95_003 precedent; never registered, never in any batch ledger).
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import trial_labor_w1 as tl1  # noqa: E402
import trial_labor_w2 as tl2  # noqa: E402
import trial_labor_w3 as tl3  # noqa: E402
import trial_labor_w4 as tl4  # noqa: E402
import trial_labor_w5 as tl5  # noqa: E402
import trial_labor_w6 as tl6  # noqa: E402
import trial_labor_w7 as tl7  # noqa: E402
import trial_labor_w8 as tl8  # noqa: E402
import trial_labor_w14 as tl14  # noqa: E402  (grammar + engine face)
import science_gates as sg  # noqa: E402

WAVE = 15
BATCH = "PERPETUAL-N2-W15"
LAW_REF = ("research/PERPETUAL_FACES.md v1.0 sec.2 N2 row + sec.4 "
           "drafting order (T-133 s2, O-2026-09-30-2340)")
PREREG = ("research/PERPETUAL_N2_W15_PREREG.md (wave-level; DRAFT "
          "until runner legs land + freeze commit; R99/R250)")
CUTOFF = tl14.CUTOFF                      # 2026-09-22 same-window law
PROBE_SEED = 95_004                       # out-of-band (N1 95_002 law)
# --- PROPOSED bands (freeze-time registration; disjoint leg machine-
#     checks these against SEED_REGISTRY + N1 declared bands) ---
BAND_GEN = 31_000
BAND_SCRNULL = 31_500
BAND_UNC = 32_000
BAND_WIDTH = 499                          # 31_000..31_499 etc.
FROZEN_GRAMMAR_SHA16 = "a231bf10940e7878"  # tl14 build, pinned

OUT_DIR = os.path.join(tl1.PATHS.results_dir, "perpetual_faces")
PROBE_OUT = os.path.join(OUT_DIR, "_n2_w15_probe.json")

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
def _pool_claim(entry_id: str, shard_key: str, detail: str) -> None:
    """Worker-side half (slice-2 run legs call this on verified done;
    identical face to the N1 canon so the launcher harvest flip lands
    the shard done)."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = os.path.join(root, "results", "pool_claims",
                     entry_id.replace("/", "_"))
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, f"{shard_key}.{_machine_id()}.json")
    now = _now_iso()
    with open(fp, "w", encoding="utf-8") as f:
        json.dump({"machine_id": _machine_id(), "state": "closed",
                   "pid": os.getpid(), "heartbeat": now, "outcome": "ok",
                   "exit_code": 0, "closed_at": now, "result_ref": detail},
                  f, ensure_ascii=False, indent=1)
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
    print("runner legs: slice-1 (probe/status/selftest) landed; "
          "run/screen/finalize/supply land with the freeze window")
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
    hits = []
    for nm, base in bands:
        lo, hi = base, base + BAND_WIDTH
        for k, v in reg.items():
            if lo <= float(v) <= hi:
                hits.append(f"{nm}~{k}@{int(v)}")
    # N1 in-use bands (law sec.4 ledger: 12_100..14_099 W2 ...
    # 28_100..28_299 W7) + N3 70_000+ + probe seeds out-of-band check
    n1_ranges = [(12_100, 14_099), (14_100, 16_099), (16_100, 18_099),
                 (21_100, 21_299), (21_300, 21_499), (21_500, 21_699),
                 (21_700, 21_899), (21_900, 23_899), (23_900, 25_899),
                 (25_900, 26_099), (26_100, 28_099), (28_100, 28_299)]
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
    print("ALL PASS" if ok else "FAIL PRESENT")
    return 0 if ok else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="perpetual_faces_n2")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    sub.add_parser("status")
    sub.add_parser("selftest")
    a = p.parse_args(argv)
    if a.cmd == "probe":
        return cmd_probe()
    if a.cmd == "status":
        return cmd_status()
    if a.cmd == "selftest":
        return cmd_selftest()
    return 2


if __name__ == "__main__":
    sys.exit(main())
