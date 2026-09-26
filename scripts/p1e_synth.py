"""P1E_SYNTH runner (research/shortline/P1E_SYNTH.md, frozen r229 bm-b).

zoo survivor pair zoo_pair_2 = (zoo85_stv, zoo92_coin_team) joint
composite IC batch: K=2 oriented-z equal-weight min_valid=2 (PS2 sec.2 /
XSTOCK lineage), judged at h10 against nullA (exhaustive C(7,2)=21
same-bias-same-scale pairs from the mother-batch 7-member shelf,
primary included) and nullB (50 K=2 white-noise pairs on the primary
mask class M_close_tr, seeds 67200+2i / 67200+2i+1, each member
oriented by its own IS IC sign = P-2 matched directional-bias).

Reuse only, zero new science logic (prereg sec.3/sec.6):
  - p1e_ic_batch: load_panels / build_masks / equivalence_gate
    (write-once p1e_equiv.json) / MEMBERS frozen order
  - p1c harness: fwd_rets / gates_v123 (recorded-v1 constants)
  - science_gates.ledger_head (r112 canonical recursive one-chain head;
    r231 fix: the narrow top-level+shortline face of
    p1c_stock_ic_batch._chain_head_total cannot see nested batch dirs
    such as results/wild_route/ and forked the chain at r226)
  - p1e_factors frozen constructors (mother batch r219)
  - composite_ic: xs_zscore (z semantics, min 5 valid) / stats_block /
    IS_END
  - shortline_p1_ic._ic_series_fast (gated fast IC path)
  - science_gates: append_ledger (pure fn -> caller MUST embed, r217) +
    SEED_REGISTRY['p1e_synth_null_b']=67200 (r229)

Determinism anchor (VOID-grade): the 7 member panels are rebuilt via the
same frozen constructors on the same frozen cache; h10 IS/OOS IC must
reproduce the mother-batch records (results/shortline/p1e_zoo_behavior
.json rows) within 5e-5 -- fail = exit 2, zero artifacts (PS2 gate-3).

Ledger: append_ledger('P1E_SYNTH', 72 + 2-if-V1-passed, ...) -- the +2
h5/h20 primary report columns are conditional (prereg sec.0/sec.4);
delta-idempotent re-finalize keeps the frozen block verbatim (r61).

Subcommands (idempotent; safe to kill/restart -- deterministic
single-shot with end-of-run atomic checkpoint):
  selftest   offline hermetic fixtures (no writes)
  run        single shard -> results/shortline/p1e_synth_parts.json
  finalize   fail-closed gates + ledger + results JSON/CSV +
             gate_attrition row (harvest-round science work, r203)
  status     checkpoint census
"""
import argparse
import inspect
import itertools
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import p1e_ic_batch as B                     # established P-1e harness
import p1c_stock_ic_batch as P1C             # recorded-v1 gate constants
import p1e_factors as F                      # frozen constructors (r219)
from composite_ic import IS_END, stats_block, xs_zscore
from shortline_p1_ic import _ic_series_fast
from science_gates import SEED_REGISTRY, append_ledger, ledger_head

OUT_DIR = B.OUT_DIR                          # results/shortline
RES_DIR = os.path.join(ROOT, "research", "shortline")
PARTS_JSON = os.path.join(OUT_DIR, "p1e_synth_parts.json")
RESULT_JSON = os.path.join(OUT_DIR, "p1e_synth.json")
RESULT_CSV = os.path.join(RES_DIR, "p1e_synth_results.csv")
MOTHER_JSON = os.path.join(OUT_DIR, "p1e_zoo_behavior.json")
ATTRITION_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

H_GATE = 10                                  # primary judgement horizon
H_REPORT = [5, 20]                           # conditional report columns
N_NULLB = 50
SEED_NULLB = int(SEED_REGISTRY["p1e_synth_null_b"])   # 67200, r229
NULL_Q = 0.95
CUTOFF = "2026-09-22"                        # frozen cache evidence_cutoff
IS_END_TS = pd.Timestamp(IS_END)
ANCHOR_TOL = 5e-5                            # mother-record reproduction
BATCH_BASE = 72                              # 1 primary + 21 nullA + 50 nullB
Z_MIN_NAMES = 5                              # composite_ic xs_zscore min_n
MIN_VALID = 2                                # K=2 composite floor (PS2)
ORIENT = -1.0                                # frozen: 7/7 members negative
PRIMARY = ("zoo85_stv", "zoo92_coin_team")    # zoo_pair_2 (mother pool h10)
RAM_GUARD_GB = 6.0                           # est peak ~5GB + headroom


# ------------------------------------------------------------------ helpers

def _ic_is_ic(fdf, fwd_h):
    """IS-segment |IC| mean via the gated fast path (null legs)."""
    s = _ic_series_fast(fdf, fwd_h)
    blk = stats_block(s[s.index <= IS_END_TS])
    return blk.get("ic_mean"), blk


def _seg_blocks(fdf, fwd_h):
    s = _ic_series_fast(fdf, fwd_h)
    return {"full": stats_block(s),
            "is": stats_block(s[s.index <= IS_END_TS]),
            "oos": stats_block(s[s.index > IS_END_TS])}


def z_of(panel, mask, orient=ORIENT):
    """Mask -> cross-sectional z (composite_ic semantics, min 5 valid)
    -> frozen orientation. Output inherits the input panel's index and
    columns (J7 alignment-pitfall family, 4th-example guard)."""
    z = xs_zscore(panel.where(mask), min_n=Z_MIN_NAMES)
    assert z.index.equals(panel.index) and z.columns.equals(panel.columns), \
        "z axis drift (J7 family)"
    return orient * z


def composite_z2(za, zb):
    """K=2 equal-weight mean, min_valid=2 (both legs finite; PS2 sec.2)."""
    both = za.notna() & zb.notna()
    comp = (za + zb) / 2.0
    comp = comp.where(both)
    assert comp.index.equals(za.index) and comp.columns.equals(za.columns), \
        "composite axis drift (J7 family)"
    return comp


def _ram_guard():
    try:
        import psutil
        avail = psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        return None
    if avail < RAM_GUARD_GB:
        print(f"free-RAM guard: {avail:.1f}GB < {RAM_GUARD_GB}GB fleet "
              f"line -> honest refuse (exit 3, retryable)", flush=True)
        sys.exit(3)
    return avail


def load_mother_records():
    """Frozen mother-batch h10 IS/OOS IC records (4dp) per member."""
    with open(MOTHER_JSON, encoding="utf-8") as f:
        mother = json.load(f)
    recs = {}
    for r in mother["rows"]:
        recs[r["factor"]] = {"h10_is_ic": r.get("h10_is_ic"),
                             "h10_oos_ic": r.get("h10_oos_ic")}
    pool = list(mother.get("pool_h10") or [])
    return recs, pool


def anchor_compare(members, fwd10, recs):
    """VOID-grade determinism anchor: rebuilt member panels must reproduce
    the mother-batch h10 IS/OOS IC within ANCHOR_TOL (records are 4dp)."""
    detail, ok = {}, True
    for nm, panel in members.items():
        blk = _seg_blocks(panel, fwd10)
        is_got = blk["is"].get("ic_mean")
        oos_got = blk["oos"].get("ic_mean")
        is_rec = recs[nm]["h10_is_ic"]
        oos_rec = recs[nm]["h10_oos_ic"]
        d_is = (abs(float(is_got) - float(is_rec))
                if is_got is not None and is_rec is not None else 9.9)
        d_oos = (abs(float(oos_got) - float(oos_rec))
                 if oos_got is not None and oos_rec is not None else 9.9)
        row_ok = d_is <= ANCHOR_TOL and d_oos <= ANCHOR_TOL
        ok &= row_ok
        detail[nm] = {"is": {"got": is_got, "recorded": is_rec,
                             "delta": round(d_is, 6), "ok": bool(row_ok)},
                      "oos": {"got": oos_got, "recorded": oos_rec,
                              "delta": round(d_oos, 6)}}
        print(f"  anchor {nm}: is {is_got} vs {is_rec} (d={d_is:.1e}) | "
              f"oos {oos_got} vs {oos_rec} (d={d_oos:.1e}) "
              f"{'OK' if row_ok else 'FAIL'}", flush=True)
    return {"tol": ANCHOR_TOL, "members": detail, "pass": bool(ok)}, ok


# ------------------------------------------------------------------- run

def run():
    t0 = time.time()
    if os.path.exists(PARTS_JSON):
        print("parts checkpoint exists -> resume-skip (deterministic "
              "single-shot)", flush=True)
        return 0
    avail = _ram_guard()
    idx, syms, meta, panels = B.load_panels({"close", "open", "tr", "vwap"})
    ev = B.equivalence_gate(panels, "p1e_synth/run")
    close, open_, tr, vwap = (panels["close"], panels["open"],
                              panels["tr"], panels["vwap"])
    fwd10 = close.shift(-H_GATE) / close - 1.0
    masks = B.build_masks(panels)
    recs, pool = load_mother_records()
    assert sorted(pool) == sorted(PRIMARY), \
        f"mother pool face drifted: {pool} (expected zoo_pair_2)"

    # ---- member panels: frozen constructors, one family at a time
    rets = close / close.shift(1) - 1.0
    members, z_panels = {}, {}

    def _mk(nm, panel):
        members[nm] = panel

    _mk("zoo85_terrified", F.build_zoo85_terrified(rets))
    _mk("zoo85_stv", F.build_zoo85_stv(rets, tr))
    _mk("zoo92_coin_team", F.build_zoo92_coin_team(close, open_, tr))
    fam, n_bad_arc = F.build_zoo93_arc_family(tr, vwap, close)
    for nm in ("zoo93_arc", "zoo93_vrc", "zoo93_src", "zoo93_krc"):
        members[nm] = fam[nm]
    print(f"member panels built ({time.time() - t0:.0f}s)", flush=True)

    # ---- VOID-grade determinism anchor (raw panels, mother path)
    anchor, anchor_ok = anchor_compare(members, fwd10, recs)
    if not anchor_ok:
        print("DETERMINISM ANCHOR FAIL - batch VOID "
              "(zero artifacts, exit 2)", flush=True)
        sys.exit(2)

    # ---- oriented z panels (mask -> z -> orient; class per prereg sec.2)
    for nm, cls in B.MEMBERS:
        z_panels[nm] = z_of(members[nm], masks[cls])
    mask_cells = {c: int(masks[c].sum().sum()) for c in
                  ("M_close", "M_close_tr", "M_arc")}
    del members, fam, rets, open_, tr, vwap, panels
    print(f"z panels built; mask cells {mask_cells} "
          f"({time.time() - t0:.0f}s)", flush=True)

    # ---- primary composite (h10 IS/OOS)
    tc = time.time()
    comp = composite_z2(z_panels[PRIMARY[0]], z_panels[PRIMARY[1]])
    h10 = _seg_blocks(comp, fwd10)
    print(f"primary h10: is_ic={h10['is'].get('ic_mean')} "
          f"ir={h10['is'].get('ic_ir')} oos_ic={h10['oos'].get('ic_mean')} "
          f"({time.time() - tc:.0f}s)", flush=True)
    del comp

    # ---- nullA: exhaustive C(7,2)=21 oriented pairs (same bias/scale)
    tc = time.time()
    nulla = []
    order = [nm for nm, _ in B.MEMBERS]
    for a, b in itertools.combinations(order, 2):
        s_is, _ = _ic_is_ic(composite_z2(z_panels[a], z_panels[b]), fwd10)
        nulla.append({"pair": [a, b], "abs_is_ic": (abs(float(s_is))
                          if s_is is not None else None),
                      "is_primary": (a, b) == PRIMARY})
    vals = [n["abs_is_ic"] for n in nulla]
    nulla_p95 = float(np.nanquantile(vals, NULL_Q))
    rank = sorted(nulla, key=lambda n: -(n["abs_is_ic"] or 9.9))
    primary_rank = [i for i, n in enumerate(rank) if n["is_primary"]][0] + 1
    print(f"nullA: n={len(nulla)} p95={nulla_p95:.4f} "
          f"primary rank={primary_rank}/21 ({time.time() - tc:.0f}s)",
          flush=True)

    # ---- nullB: 50 K=2 noise pairs, M_close_tr, own-IS-IC-sign orient
    tc = time.time()
    mask = masks["M_close_tr"]
    nullb = []
    for i in range(N_NULLB):
        seeds = (SEED_NULLB + 2 * i, SEED_NULLB + 2 * i + 1)
        z_o = []
        member_is = []
        for sd in seeds:
            rng = np.random.default_rng(sd)
            vals = pd.DataFrame(rng.standard_normal(close.shape),
                                index=close.index, columns=close.columns)
            z = xs_zscore(vals.where(mask), min_n=Z_MIN_NAMES)
            del vals
            is_ic, _ = _ic_is_ic(z, fwd10)
            member_is.append(None if is_ic is None else round(float(is_ic), 6))
            orient = 1.0 if (is_ic is None or float(is_ic) >= 0) else -1.0
            z_o.append(orient * z)
            del z
        s_is, _ = _ic_is_ic(composite_z2(z_o[0], z_o[1]), fwd10)
        nullb.append({"i": i, "seeds": list(seeds),
                      "member_is_ic": member_is,
                      "abs_is_ic": (abs(float(s_is))
                                    if s_is is not None else None)})
        del z_o
        if (i + 1) % 10 == 0:
            print(f"  nullB {i + 1}/{N_NULLB} ({time.time() - tc:.0f}s)",
                  flush=True)
    bvals = [n["abs_is_ic"] for n in nullb]
    nullb_p95 = float(np.nanquantile(bvals, NULL_Q))
    print(f"nullB: n={len(nullb)} p95={nullb_p95:.4f} "
          f"({time.time() - tc:.0f}s)", flush=True)

    # ---- preliminary V1 (runner-side only decides the conditional
    # h5/h20 report columns; authoritative gates live in finalize)
    is_ic10 = h10["is"].get("ic_mean")
    v1_prelim = (is_ic10 is not None
                 and abs(float(is_ic10)) > max(P1C.V1_FLOOR,
                                               nulla_p95, nullb_p95))
    h5 = h20 = None
    if v1_prelim:
        for h in H_REPORT:
            fwdh = close.shift(-h) / close - 1.0
            comp = composite_z2(z_panels[PRIMARY[0]], z_panels[PRIMARY[1]])
            blk = {"is": stats_block(
                       (_s := _ic_series_fast(comp, fwdh))
                       [_s.index <= IS_END_TS]),
                   "oos": stats_block(_s[_s.index > IS_END_TS])}
            if h == 5:
                h5 = blk
            else:
                h20 = blk
            del comp, fwdh
        print("conditional h5/h20 report columns computed (V1 prelim "
              "pass; snooping-discount label carried)", flush=True)

    parts = {
        "meta": {"batch": "P1E_SYNTH", "pre_reg":
                 "research/shortline/P1E_SYNTH.md (frozen r229, "
                 "commit ca1b45ee)",
                 "claim": "MSG-20260926-0644-bm-b (F-04, r229)",
                 "lane": "bm-b (machine-local p1c_stock cache + "
                 "turnover sidecar, r188 lane-pin)",
                 "date": time.strftime("%Y-%m-%d %H:%M"),
                 "is_end": str(IS_END), "gate_horizon": H_GATE,
                 "orientation": f"orient={ORIENT} frozen (mother 7/7 "
                 "negative IS IC)",
                 "min_valid": MIN_VALID, "z_min_names": Z_MIN_NAMES,
                 "mask_cells": mask_cells,
                 "zoo93_nonfinite_arc_cells": n_bad_arc,
                 "ram_guard_gb": RAM_GUARD_GB,
                 "ram_available_gb": (round(avail, 1)
                                      if avail is not None else None),
                 "engine_runs": 0},
        "equivalence": ev,
        "determinism_anchor": anchor,
        "mother_pool": list(PRIMARY),
        "primary": {"pair": list(PRIMARY),
                    "mask_classes": [dict(B.MEMBERS)[nm] for nm in PRIMARY],
                    "h10": h10, "h5": h5, "h20": h20,
                    "v1_prelim": bool(v1_prelim)},
        "nullA": {"pairs": nulla, "p95": round(nulla_p95, 4),
                  "primary_rank": primary_rank},
        "nullB": {"draws": nullb, "p95": round(nullb_p95, 4),
                  "seed_base": SEED_NULLB,
                  "seed_band": [SEED_NULLB, SEED_NULLB + 2 * N_NULLB],
                  "orient": "own IS IC sign (P-2 matched "
                  "directional-bias)"},
        "audit": {"elapsed_s": round(time.time() - t0, 1),
                  "workers": 1,
                  "cpu_cap_policy": "O-20260923-1738 single-proc "
                  "vectorized",
                  "ic_computations": 7 + 1 + len(nulla)
                  + 2 * N_NULLB + N_NULLB
                  + (len(H_REPORT) if v1_prelim else 0)},
    }
    json.loads(json.dumps(parts))            # verify-parse before write
    tmp = PARTS_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(parts, f, indent=2, ensure_ascii=False)
    os.replace(tmp, PARTS_JSON)
    print(f"run complete ({time.time() - t0:.0f}s): "
          f"nullA_p95={nulla_p95:.4f} nullB_p95={nullb_p95:.4f} "
          f"primary_is_ic={is_ic10} v1_prelim={v1_prelim}", flush=True)
    print(f"saved: {PARTS_JSON}", flush=True)
    return 0


# --------------------------------------------------------------- finalize

def _validate_parts(p):
    """Fail-closed pre-check (r217: any error/missing part = refuse,
    zero artifacts)."""
    problems = []
    if not (p.get("determinism_anchor") or {}).get("pass"):
        problems.append("determinism anchor not pass")
    if not (p.get("equivalence") or {}).get("pass"):
        problems.append("equivalence gate not pass")
    na = (p.get("nullA") or {}).get("pairs") or []
    if len(na) != 21:
        problems.append(f"nullA pairs={len(na)} != 21")
    if sum(1 for n in na if n.get("is_primary")) != 1:
        problems.append("nullA primary flag count != 1")
    if any(n.get("abs_is_ic") is None or not np.isfinite(n["abs_is_ic"])
           for n in na):
        problems.append("nullA has non-finite abs_is_ic")
    nb = (p.get("nullB") or {}).get("draws") or []
    if len(nb) != N_NULLB:
        problems.append(f"nullB draws={len(nb)} != {N_NULLB}")
    if any(n.get("abs_is_ic") is None or not np.isfinite(n["abs_is_ic"])
           for n in nb):
        problems.append("nullB has non-finite abs_is_ic (prereg sec.6 "
                        "anchor-5 invariant)")
    pr = p.get("primary") or {}
    for seg in ("is", "oos"):
        if "ic_mean" not in ((pr.get("h10") or {}).get(seg) or {}):
            problems.append(f"primary h10 {seg} block missing ic_mean")
    is_blk = (pr.get("h10") or {}).get("is") or {}
    if "ic_ir" not in is_blk or "n_periods" not in is_blk:
        problems.append("primary h10 is block missing ic_ir/n_periods "
                        "(gates_v123 inputs)")
    if pr.get("v1_prelim") and (pr.get("h5") is None
                                or pr.get("h20") is None):
        problems.append("v1_prelim pass but conditional h5/h20 missing")
    if not pr.get("v1_prelim") and (pr.get("h5") is not None
                                    or pr.get("h20") is not None):
        problems.append("conditional h5/h20 present without v1_prelim")
    return problems


def finalize():
    t0 = time.time()
    if not os.path.exists(PARTS_JSON):
        print("FINALIZE REFUSED: parts checkpoint missing (run first)",
              flush=True)
        sys.exit(2)
    with open(PARTS_JSON, encoding="utf-8") as f:
        p = json.load(f)
    problems = _validate_parts(p)
    if problems:
        print("FINALIZE REFUSED (fail-closed, zero artifacts):", flush=True)
        for x in problems:
            print(f"  - {x}", flush=True)
        sys.exit(2)

    na = p["nullA"]["pairs"]
    nb = p["nullB"]["draws"]
    nulla_p95 = round(float(np.quantile(
        [n["abs_is_ic"] for n in na], NULL_Q)), 4)
    nullb_p95 = round(float(np.quantile(
        [n["abs_is_ic"] for n in nb], NULL_Q)), 4)
    assert nulla_p95 == p["nullA"]["p95"], "nullA p95 drift vs parts"
    assert nullb_p95 == p["nullB"]["p95"], "nullB p95 drift vs parts"
    v1_thr = max(P1C.V1_FLOOR, nulla_p95, nullb_p95)
    gates = P1C.gates_v123(p["primary"]["h10"]["is"],
                           p["primary"]["h10"]["oos"],
                           {"p95_abs_ic": max(nulla_p95, nullb_p95)})
    v1 = gates["v1"]
    if v1 != p["primary"]["v1_prelim"]:
        print("FINALIZE REFUSED: authoritative V1 != runner v1_prelim "
              "(determinism breach)", flush=True)
        sys.exit(2)
    batch_trials = BATCH_BASE + (2 if v1 else 0)

    # ---- delta-idempotent ledger (r61/p1c precedent)
    old = None
    if os.path.exists(RESULT_JSON):
        try:
            with open(RESULT_JSON, encoding="utf-8") as f:
                old = json.load(f)
        except Exception:
            old = None
    if old is not None and old.get("meta", {}).get("batch") == "P1E_SYNTH":
        ledger = old["trials_ledger"]
        print("re-finalize: frozen ledger block kept verbatim "
              "(delta-idempotent)", flush=True)
    else:
        ledger = append_ledger(                    # pure fn -> EMBED r217
            "P1E_SYNTH", batch_trials,
            file_name="shortline/p1e_synth.json",
            note="factor-ledger accounting: 1 primary + 21 nullA "
                 "(C(7,2) exhaustive, primary included = same bias "
                 "same scale) + 50 nullB (K=2 noise, M_close_tr, "
                 "seeds 67200..67299 own-IS-IC-sign oriented) "
                 f"+{2 if v1 else 0} conditional h5/h20 report "
                 "columns (V1-gated, snooping discount); delta-"
                 "idempotent; engine ledger N untouched (zero engine "
                 "runs)",
            evidence_cutoff=CUTOFF,
            # r231: prev = canonical recursive chain head (r112 face).
            # The narrow helper (top-level + shortline/ one level, no
            # recursion) missed results/wild_route/ and produced a
            # same-prev fork at r226 (P-1e block 183292 below the real
            # head 184754) -- prereg sec.3 demands the live chain head.
            prev_total=ledger_head()["total"])
    assert isinstance(ledger, dict) and "total" in ledger, "ledger embed"

    # ---- results JSON
    pr = dict(p["primary"])
    pr["gates"] = gates
    pr["v1_thr"] = round(v1_thr, 4)
    out = {
        "meta": dict(p["meta"],
                     multiplicity="1 primary + 21 nullA (exhaustive "
                     "C(7,2), primary included = same bias same scale, "
                     "PS2 precedent) + 50 nullB; h10 sole gate horizon; "
                     "h5/h20 conditional report columns carry the "
                     "snooping-discount label",
                     verdict_branch_prewritten="prereg sec.8 PASS/FAIL "
                     "dispositions frozen pre-run",
                     zero_authorization="neighbor check granted column "
                     "eligibility only; this batch's scientific standing "
                     "comes entirely from its own pre-run freeze"),
        "evidence_cutoff": CUTOFF,               # C2 legal key (top level)
        "science_gates": {"cutoff_meta": CUTOFF},
        "equivalence": p["equivalence"],
        "determinism_anchor": p["determinism_anchor"],
        "thresholds": {"nullA_p95": nulla_p95, "nullB_p95": nullb_p95,
                       "v1_thr": round(v1_thr, 4),
                       "v1_floor": P1C.V1_FLOOR,
                       "v2_ir_line": P1C.V2_IR_LINE,
                       "v3_retain": 0.5,
                       "a3_min_periods": P1C.MIN_PERIODS_GATE,
                       "primary_rank_of_21": p["nullA"]["primary_rank"]},
        "primary": pr,
        "nullA": {"p95": nulla_p95,
                  "primary_rank": p["nullA"]["primary_rank"],
                  "pairs": na},
        "nullB": dict(p["nullB"], p50_abs_ic=round(float(np.median(
            [n["abs_is_ic"] for n in nb])), 6)),
        "counts": {"primary": 1, "nullA": len(na), "nullB": len(nb),
                   "n_eff": BATCH_BASE,
                   "conditional_report_columns": 2 if v1 else 0,
                   "batch_trials_ledger": batch_trials},
        "trials_ledger": ledger,
        "audit": dict(p["audit"], finalize_elapsed_s=round(time.time() - t0, 1)),
    }
    json.loads(json.dumps(out))               # verify-parse before write
    tmp = RESULT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    os.replace(tmp, RESULT_JSON)

    h10is, h10oos = pr["h10"]["is"], pr["h10"]["oos"]
    flat = {"role": "primary", "pair": "+".join(pr["pair"]),
            "is_ic": h10is.get("ic_mean"), "is_ir": h10is.get("ic_ir"),
            "is_n": h10is.get("n_periods"),
            "oos_ic": h10oos.get("ic_mean"), "oos_n": h10oos.get("n_periods"),
            "v1_thr": round(v1_thr, 4), "v1": v1, "v2": gates["v2"],
            "v3": gates["v3"], "a3": gates["a3"], "pass": gates["pass"],
            "rank_of_21": p["nullA"]["primary_rank"]}
    for h, blk in (("h5", pr.get("h5")), ("h20", pr.get("h20"))):
        if blk:
            flat[f"{h}_is_ic"] = blk["is"].get("ic_mean")
            flat[f"{h}_oos_ic"] = blk["oos"].get("ic_mean")
    rows = [flat]
    for n in na:
        rows.append(dict(role="nullA", pair="+".join(n["pair"]),
                         abs_is_ic=n["abs_is_ic"],
                         is_primary=n["is_primary"]))
    for n in nb:
        rows.append(dict(role="nullB", i=n["i"],
                         seeds=",".join(str(s) for s in n["seeds"]),
                         member_is_ic=",".join(
                             str(x) for x in n["member_is_ic"]),
                         abs_is_ic=n["abs_is_ic"]))
    pd.DataFrame(rows).to_csv(RESULT_CSV, index=False, encoding="utf-8")

    # ---- gate_attrition row (r212/r217 precedent)
    try:
        with open(ATTRITION_JSON, encoding="utf-8") as f:
            att = json.load(f)
        att.setdefault("entries", []).append({
            "batch": "P1E_SYNTH", "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "measurement", "cells_ledger_delta": batch_trials,
            "ledger_total_after": ledger["total"],
            "gates": {"v1_thr": round(v1_thr, 4), "nullA_p95": nulla_p95,
                      "nullB_p95": nullb_p95, "v1": v1, "v2": gates["v2"],
                      "v3": gates["v3"], "a3": gates["a3"],
                      "pass": gates["pass"],
                      "primary_is_ic": p["primary"]["h10"]["is"].get("ic_mean"),
                      "primary_oos_ic": p["primary"]["h10"]["oos"].get("ic_mean"),
                      "primary_rank_of_21": p["nullA"]["primary_rank"]},
            "eliminated": 0 if gates["pass"] else 1,
            "refs": {"results": "results/shortline/p1e_synth.json",
                     "prereg": "research/shortline/P1E_SYNTH.md",
                     "note": "factor-layer measurement; PASS=zero "
                     "authorization, strategy-level transformation "
                     "requires a separate prereg (prereg sec.8)"}}
        )
        json.loads(json.dumps(att))
        tmp = ATTRITION_JSON + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(att, f, indent=2, ensure_ascii=False)
        os.replace(tmp, ATTRITION_JSON)
    except Exception as ex:
        print(f"gate_attrition append FAILED ({ex}) - disclosed, "
              "non-blocking", flush=True)

    print(f"finalize: gates={gates} v1_thr={v1_thr:.4f} "
          f"rank={p['nullA']['primary_rank']}/21", flush=True)
    print(f"ledger: {json.dumps(ledger)}", flush=True)
    print(f"saved: {RESULT_JSON}", flush=True)
    print(f"saved: {RESULT_CSV}", flush=True)
    return 0


# ------------------------------------------------------------------ status

def status():
    print(f"parts={os.path.exists(PARTS_JSON)} "
          f"final={os.path.exists(RESULT_JSON)} "
          f"equiv={os.path.exists(B.EQUIV_JSON)} "
          f"mother={os.path.exists(MOTHER_JSON)}", flush=True)
    return 0


# ---------------------------------------------------------------- selftest

def _synth_panels(rng, T=2600, N=40):
    """Fixture calendar must span IS_END (2024-12-31) so the IS/OOS
    split produces two non-empty segments (production-form mirror,
    r157/r221 pairing law)."""
    idx = pd.date_range("2016-01-01", periods=T, freq="B")
    cols = [f"S{i}" for i in range(N)]
    close = pd.DataFrame(10.0 + np.cumsum(rng.normal(0, .2, (T, N)), axis=0),
                         index=idx, columns=cols)
    open_ = close.shift(1).fillna(10.0) * 1.001
    tr = pd.DataFrame(0.01 + 0.05 * rng.random((T, N)), index=idx,
                      columns=cols)
    vwap = close * (1.0 + 0.001 * rng.random((T, N)))
    return idx, cols, close, open_, tr, vwap


def selftest():
    t0 = time.time()
    ok_all = True

    def check(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}", flush=True)

    rng = np.random.default_rng(20260926)
    idx, cols, close, open_, tr, vwap = _synth_panels(rng)
    fwd10 = close.shift(-10) / close - 1.0
    mask_tr = close.notna() & tr.notna()

    print("[1/9] IC equivalence vs composite_ic.ic_series (prereg "
          "anchor-1):", flush=True)
    fac = pd.DataFrame(rng.standard_normal(close.shape), index=idx,
                       columns=cols)
    fac = fac.where(pd.DataFrame(rng.random(close.shape) < 0.8,
                                index=idx, columns=cols))
    ref = B.ic_series(fac, fwd10)
    fast = _ic_series_fast(fac, fwd10)
    common = ref.index.intersection(fast.index)
    worst = float((ref[common] - fast[common]).abs().max()) \
        if len(common) else 9.9
    check(f"equivalence max|d|={worst:.1e} <= 1e-6, len equal",
          worst <= 1e-6 and len(ref) == len(fast))

    print("[2/9] recipe monotonic anchor (prereg anchor-2, 1e-9):",
          flush=True)
    m = fwd10.notna() & (fwd10.notna().sum(axis=1).values[:, None] >= 5)
    z1 = xs_zscore(fwd10.where(m), min_n=Z_MIN_NAMES)
    z2 = xs_zscore(fwd10.where(m), min_n=Z_MIN_NAMES)
    comp = composite_z2(z1, z2)
    s = _ic_series_fast(comp, fwd10)
    mono = float(np.abs(s.values).max()) if len(s) else 0.0
    check(f"composite(=fwd legs) |IC| max={mono:.2e} ~= 1",
          len(s) > 0 and abs(mono - 1.0) < 1e-9)
    both = z1.notna() & z2.notna()
    ident = (float((comp[both] - z1[both]).abs().max().max())
             if bool(both.any().any()) else 9.9)
    check(f"equal-weight identity comp==leg (max|d|={ident:.1e} < 1e-12)",
          ident < 1e-12)
    z1_hole = z1.copy()
    z1_hole.iloc[10:15, 0] = np.nan            # one-leg hole
    comp_hole = composite_z2(z1_hole, z2)
    check("min_valid=2: one-leg hole -> composite NaN there",
          bool(comp_hole.iloc[10:15, 0].isna().all()))

    print("[3/9] determinism-anchor machinery (prereg anchor-3, VOID "
          "semantics):", flush=True)
    rets_s = close / close.shift(1) - 1.0
    panel = F.build_zoo85_terrified(rets_s)
    blk = _seg_blocks(panel, fwd10)
    rec = {"h10_is_ic": blk["is"]["ic_mean"],
           "h10_oos_ic": blk["oos"]["ic_mean"]}
    det, ok = anchor_compare({"fixture": panel}, fwd10,
                             {"fixture": rec})
    check("self-recorded anchor reproduces (delta 0)", ok and det["pass"])
    rec_bad = dict(rec, h10_is_ic=rec["h10_is_ic"] + 1e-3)
    det2, ok2 = anchor_compare({"fixture": panel}, fwd10,
                               {"fixture": rec_bad})
    check("poisoned record (+1e-3) -> anchor refuses (VOID path)",
          (not ok2) and (not det2["pass"]))

    print("[4/9] nullA enumeration (prereg anchor-4):", flush=True)
    order = [nm for nm, _ in B.MEMBERS]
    pairs = list(itertools.combinations(order, 2))
    check(f"C(7,2)={len(pairs)} == 21, unique, frozen order",
          len(pairs) == 21 and len(set(pairs)) == 21
          and pairs[0] == ("zoo85_terrified", "zoo85_stv"))
    check("primary (stv, coin_team) inside nullA (same bias/scale)",
          ("zoo85_stv", "zoo92_coin_team") in pairs)
    zn = {nm: xs_zscore(pd.DataFrame(
        rng.standard_normal(close.shape), index=idx, columns=cols)
        .where(mask_tr), min_n=Z_MIN_NAMES) for nm in order}
    vals = []
    for a, b in pairs:
        icv, _ = _ic_is_ic(composite_z2(zn[a], zn[b]), fwd10)
        vals.append(None if icv is None else abs(float(icv)))
    check("21 pair abs IS IC all finite on fixture",
          all(v is not None and np.isfinite(v) for v in vals))

    print("[5/9] nullB seeds + matched orientation (prereg anchor-5):",
          flush=True)
    seeds = [s for i in range(N_NULLB)
             for s in (SEED_NULLB + 2 * i, SEED_NULLB + 2 * i + 1)]
    check(f"seed base==67200 registry, band 67200..67299, 100 unique",
          SEED_NULLB == 67200 and len(set(seeds)) == 100
          and min(seeds) == 67200 and max(seeds) == 67299)
    # matched-orientation leg: single noise member, orient by own IS IC
    # sign -> oriented IS IC == |raw IS IC| (abs preserved, sign forced
    # non-negative) -- the P-2 'orientation is bias' matched treatment.
    n1 = pd.DataFrame(np.random.default_rng(67200)
                      .standard_normal(close.shape), index=idx,
                      columns=cols).where(mask_tr)
    z_n1 = xs_zscore(n1, min_n=Z_MIN_NAMES)
    raw_ic, _ = _ic_is_ic(z_n1, fwd10)
    orient = 1.0 if float(raw_ic) >= 0 else -1.0
    ori_ic, _ = _ic_is_ic(orient * z_n1, fwd10)
    check(f"orientation matched: raw {raw_ic} -> oriented {ori_ic} "
          f"(abs equal, sign >= 0)",
          np.isclose(abs(float(ori_ic)), abs(float(raw_ic)), atol=1e-9)
          and float(ori_ic) >= 0)

    print("[6/9] z semantics alignment (prereg anchor-6, J7 family 4th):",
          flush=True)
    zz = z_of(panel, mask_tr)
    check("z inherits panel index+columns",
          zz.index.equals(panel.index) and zz.columns.equals(panel.columns))
    check("mask respected: cells outside mask are NaN in z",
          bool(zz[~mask_tr].isna().all().all()))
    cc = composite_z2(zz, zz)
    check("composite inherits axes too",
          cc.index.equals(panel.index) and cc.columns.equals(panel.columns))

    print("[7/9] threshold composition via production gates_v123:",
          flush=True)
    gA = P1C.gates_v123({"ic_mean": 0.09, "ic_ir": 0.55, "n_periods": 600},
                        {"ic_mean": 0.07}, {"p95_abs_ic": 0.08})
    check("is 0.09 > max(0.02, nullA 0.08, nullB) -> V1 T; V2/V3 T -> pass",
          gA["v1"] and gA["v2"] and gA["v3"] and gA["pass"])
    gB = P1C.gates_v123({"ic_mean": 0.07, "ic_ir": 0.55, "n_periods": 600},
                        {"ic_mean": 0.06}, {"p95_abs_ic": 0.08})
    check("is 0.07 < raised nullA band -> V1 F (shelf-effect face)",
          (not gB["v1"]) and (not gB["pass"]))

    print("[8/9] frozen constants:", flush=True)
    check("H_GATE=10, BATCH_BASE=72, MIN_VALID=2, ORIENT=-1, cutoff",
          H_GATE == 10 and BATCH_BASE == 72 and MIN_VALID == 2
          and ORIENT == -1.0 and CUTOFF == "2026-09-22")
    check("primary == mother pool pair (zoo_pair_2)",
          PRIMARY == ("zoo85_stv", "zoo92_coin_team"))
    fin_src = inspect.getsource(finalize)
    check("ledger prev = canonical recursive ledger_head (r112 face; "
          "narrow _chain_head_total forked the chain r226/r231)",
          "prev_total=ledger_head()" in fin_src
          and "P1C._chain_head_total" not in fin_src)
    check("r217 embed law: finalize writes trials_ledger: ledger",
          '"trials_ledger": ledger' in fin_src)

    print("[9/9] data-face census (read-only):", flush=True)
    try:
        recs, pool = load_mother_records()
        check("mother records: 7 members, pool == zoo_pair_2",
              len(recs) == 7 and sorted(pool) == sorted(PRIMARY))
        check("cache fields + sidecar present",
              all(os.path.exists(os.path.join(B.CACHE_DIR, f + ".npy"))
                  for f in ("close", "open", "vwap"))
              and os.path.exists(os.path.join(B.CACHE_DIR,
                                              "turnover_derived.npy")))
    except Exception as ex:
        check(f"data-face census ({type(ex).__name__}: {str(ex)[:80]})",
              False)

    print(f"SELFTEST {'PASS' if ok_all else 'FAIL'} "
          f"({time.time() - t0:.0f}s)", flush=True)
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["selftest", "run", "finalize",
                                     "status"])
    a = ap.parse_args()
    if a.mode == "selftest":
        sys.exit(selftest())
    if a.mode == "status":
        sys.exit(status())
    if a.mode == "run":
        sys.exit(run())
    if a.mode == "finalize":
        sys.exit(finalize())


if __name__ == "__main__":
    main()
