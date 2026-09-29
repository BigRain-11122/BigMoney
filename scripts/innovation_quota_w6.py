# -*- coding: utf-8 -*-
"""INNOVATION_QUOTA_W6 runner -- RRG_ROTATION_P1 quadrant-rotation family
judged batch (INNOVATION-QUOTA-SLOT-6, zoo #91 rrg_quadrant_rotation,
param-frozen r216 digest sec.2 clean-room).

Laws frozen in research/INNOVATION_QUOTA_W6_PREREG.md (r458 bm-a berth +
r459 bm-a freeze, seed three-step law ALL GREEN via full import view,
results/_r459bma_w6_seed_law_facts.json; probe facts frozen
results/_r459bma_rrg_w6_probe_facts.json):

  panel   core48 via live.paper.load_core + build_panels, truncated to
          evidence cutoff 2026-09-22 (P-5C frozen binding). G-PANEL:
          n_syms 48 / 2020-01-02..2026-09-22 / 1631 days /
          member_row_min 797 / member_row_max 1631. G-ANCHOR
          (fail-closed bit-exact reconcile vs the r459 frozen probe
          facts, one-face-off = config mismatch VOID): 81 month-ends /
          66 decidable / first decidable 2021-04-30 / zero empty-leading
          month-end among decidable (carry rule zero-trigger proven) /
          leading size min4 med13 max20 / selection records 81x2 full
          (the bit-exact runner anchor) / n_trades engine face
          base=1022 unc=241 (checked at burn on the x1 cells).
  build   verbatim-import from results/_r459bma_rrg_w6_probe.py (r456
          paradigm, single source zero re-implementation drift):
          RS = member close / pool-EW NAV (daily-rebalanced mean of
          member returns); RS-Ratio = MA20(100*RS/RS.shift(220));
          RS-Momentum = MA20(100*RS-Ratio/RS-Ratio.shift(60)) (de
          Kempenaer ratio method, hub 100); leading = both axes > 100;
          selection = top-k by Euclidean distance from (100,100) among
          leading, code-asc tie-break, zero-leading -> carry previous
          (frozen determinism); month-end close decision, state
          effective from next bar (T+1, engine buys next-day open; T33
          gem_entry causality precedent). Variants FROZEN r459: base
          top-6 @ 0.95/6 (fleet 0.95 full-position convention,
          satisfies <=1/6 per-member cap) / unconstrained top-2 @
          0.95/2 (freeze-window fixed choice; top-1 rejected).
  cells   4 cells = 2 variants x 2 cost faces (prereg s0: every cell
          pays into N_eff, T33 face precedent): RRG-BASE-X1 (judged
          face), RRG-BASE-X2, RRG-UNC-X1 (judged face), RRG-UNC-X2
          (CostPatch(2.0) = 26.082bp/side stress disclosure column;
          judged cost face = V1 legacy base per freeze record). All
          four cells burned through the REAL engine path
          (engine.run_backtest via probe variant_cell, monthly entry
          marks, T+1 fills).
  window  batch accrual lo = 2021-05-06 (first decidable month-end
          2021-04-30 next bar; W5 lo=max(first_decidable)+1 same law),
          four-cell shared window (cross-cell PBO/CSCV date
          alignment); pre-lo panel days are construction warmup,
          discarded for batch comparability, disclosed.
  passive G1' passive term = core48 pool calibration artifact,
          live-read via SG.passive_baseline("core48") (prereg s4
          live-read law, no hand-copied lines). Virtual-starts beat
          passive = pool-EW benchmark series (prereg s3: benchmark =
          pool equal-weight NAV, the RRG construction's own
          benchmark).
  nulls   shared core48 collector (n=120, prereg s4; K=0 own nulls,
          T33 same-door); no per-cell null family this batch.
  starts  K=1000 virtual starts (k in [0, 1000), law s1 K>=1000):
          windows 6m/12m/24m = 126/252/504 trading days (252 ppy
          convention); beat = cell window cum ret (own cost face) >
          pool-EW benchmark window cum ret, per-window beat_rate
          disclosed. 100 random split windows (k in [1000, 1100),
          law s3 >= 100): split point in [0.2n, 0.8n], half-window
          Sharpe same-sign rate >= 80% = segment-stable. rng =
          np.random.default_rng([SEED, k]), one k-stream shared
          across cells (seed law frozen; no own-null k-alloc ->
          starts at 0, splits at 1000, disclosed).
  gates   G1'v2 per cell via science_gates.g1_prime_v2 (batch_cells
          = 4, s0 counting law: every cell pays), pool='core48'
          default named-pool reader, null_pool = shared collector
          default, passive_override = live passive_baseline("core48");
          n_trades/n_entries from the engine dual face
          (report_num_entries; F6 dual gate); DSR via
          deflated_sharpe_ratio on the raw cell series; family PBO
          via screening.pbo cscv_pbo CSCV-8 over the 4-cell matrix;
          G2 via g2_registration_v2. No hand-copied lines (O-2250).
  d6      frozen at the r459 probe window verbatim (prereg s1
          protocol): batch internal base-vs-unc 0.5513; vs T33 four
          in-book rotation cells max 0.4803 (unc x dual_momentum) /
          0.4489 (base x slope_r2) -- ALL < 0.7 reject line, merge
          clause ZERO triggers; vs registered six max 0.2811
          (COMPOSITE-CE-02). Runner copies the frozen d6 block (no
          re-computation: the admission record is the freeze-window
          artifact).
  ledger  append_ledger("RRG_ROTATION_P1", 4, "results/
          innovation_quota/RRG-ROTATION-P1.json", evidence_cutoff
          ="2026-09-22"); out["trials_ledger"] carries the return
          value (r434 pit law); gate_attrition measurement row to the
          EXECUTING machine's lane file (prereg s6:
          gate_attrition.<machine_id>.json, shared-file fallback when
          unreadable).
Products (prereg s6): results/innovation_quota/RRG-ROTATION-P1.json
(top evidence_cutoff + cutoff_meta + panel/anchor faces + passive +
4 cells + turnover faces + virtual starts + splits + frozen d6 +
funnel + gates + ledger).

Usage: run | verify | selftest   (exit 0 ok; 2 = fail-closed gate
refusal, including the r450 landed-state guard: a judged product
(trials_ledger present, read from CONTENT not existence/timestamps)
refuses re-run rc=2 unless INNOVATION_QUOTA_W6_REFINALIZE=1; a
phase-1-only product resumes cleanly). 'verify' = real-panel
G-ANCHOR reconcile only (read-only, no engine, no product, no
ledger -- build-time pre-verification face, burn stays with the
pool claim).
"""
import argparse
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "results"))

import science_gates as SG                      # shared gate library (O-2250)
from ce_transfer import COST_X1_RATE            # x1 = 13.041bp/side
from screening.pbo import cscv_pbo              # family PBO CSCV-8

# frozen construction single source (r456 verbatim-import paradigm)
from _r459bma_rrg_w6_probe import (TOP_K, PS, CUTOFF, build_rrg_faces,
                                   rrg_selection, selection_to_entry,
                                   variant_cell, load_panel)

OUT_DIR = os.path.join(ROOT, "results", "innovation_quota")
OUT_JSON = os.path.join(OUT_DIR, "RRG-ROTATION-P1.json")
OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)      # results root for lib faces
PROBE_FACTS = os.path.join(ROOT, "results", "_r459bma_rrg_w6_probe_facts.json")
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
ATT_JSON_SHARED = os.path.join(ROOT, "results", "gate_attrition.json")

BATCH_NAME = "RRG_ROTATION_P1"
BATCH_CELLS = 4                    # s0 counting law: every cell pays
EVIDENCE_CUTOFF = CUTOFF           # 2026-09-22 (P-5C frozen binding)
SEED_KEY = "innovation_quota_w6_rrg_rotation"
PBP = SG.PERIODS_PER_YEAR          # 252 gate-chain single-source
K_STARTS = 1000
K_SPLITS = 100
WIN_DAYS = {"6m": 126, "12m": 252, "24m": 504}
D6_REJECT = 0.7                    # prereg s1 merge-clause line
TURNOVER_BUDGET = 50               # prereg s3: 50/year (T33 same door)
BATCH_LO = "2021-05-06"            # frozen: first-decidable ME next bar
SEED = None                        # filled from SG.SEED_REGISTRY at run

# 4 cells = 2 variants x 2 cost faces (prereg s0); key = (variant, mult, face)
CELL_FACES = [("base", 1.0, "x1"), ("base", 2.0, "x2"),
              ("unc", 1.0, "x1"), ("unc", 2.0, "x2")]
CELL_NAME = {("base", 1.0, "x1"): "RRG-BASE-X1",
             ("base", 2.0, "x2"): "RRG-BASE-X2",
             ("unc", 1.0, "x1"): "RRG-UNC-X1",
             ("unc", 2.0, "x2"): "RRG-UNC-X2"}

_PANEL_OVERRIDE = None             # selftest synthetic-panel injection hook
_ATT_OVERRIDE = None               # selftest attrition-path override


def gate_refuse(msg):
    print(f"GATE-REFUSE(exit2): {msg}")
    return 2


def sharpe_of(series):
    """NaN-safe nan-aware Sharpe (r442 pit law): non-finite dropped, a
    degenerate all-zero face returns 0.0, never NaN via raw mean/std."""
    r = np.asarray(series, dtype=float)
    r = r[np.isfinite(r)]
    if len(r) < 2:
        return 0.0
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(PBP)) if sd > 0 else 0.0


def cum_ret(series, lo, hi):
    """Window cumulative return over indices [lo, hi)."""
    seg = np.asarray(series[lo:hi], dtype=float)
    seg = seg[np.isfinite(seg)]
    return float(np.prod(1.0 + seg) - 1.0) if len(seg) else 0.0


def _cell_stats(ser):
    r = np.asarray(ser, dtype=float)
    fin = r[np.isfinite(r)]
    n = len(fin)
    eq = np.cumprod(1.0 + fin)
    dd = float((eq / np.maximum.accumulate(eq) - 1.0).min()) if n else 0.0
    ann = float(eq[-1] ** (PBP / max(n, 1)) - 1.0) if n else 0.0
    return {"sharpe_full": round(sharpe_of(r), 4),
            "ann_ret": round(ann, 6),
            "max_dd": round(dd, 6), "n_days": int(len(r))}


def _jsonable_metrics(m):
    out = {}
    for k, v in m.items():
        if isinstance(v, bool):
            out[k] = v
        elif isinstance(v, (int, float)):
            out[k] = float(v) if math.isfinite(float(v)) else None
    return out


def _sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ------------------------------------------------------- G-ANCHOR reconcile
def derive_faces(close):
    """Re-derive the construction faces on a panel (probe verbatim
    functions, no engine, no performance metrics)."""
    nav, rs_ratio, rs_mom = build_rrg_faces(close)
    sels = {v: rrg_selection(rs_ratio, rs_mom, TOP_K[v]) for v in TOP_K}
    # idempotence self-check (probe same law)
    sels2 = {v: rrg_selection(rs_ratio, rs_mom, TOP_K[v]) for v in TOP_K}
    for v in TOP_K:
        assert list(sels2[v].values()) == list(sels[v].values()), \
            f"selection re-derivation drift ({v})"
    me_days = sorted(sels["base"].keys())
    recs = {v: {str(d.date()): list(sels[v][d]) for d in me_days}
            for v in TOP_K}

    lead_sizes, decidable_mes = [], []
    zero_lead = carry_while_decidable = 0
    for d in me_days:
        rsr, rsm = rs_ratio.loc[d], rs_mom.loc[d]
        ok = rsr.notna() & rsm.notna()
        lead = ok & (rsr > 100.0) & (rsm > 100.0)
        decidable = bool(ok.any())
        if decidable:
            decidable_mes.append(d)
            if not bool(lead.any()):
                zero_lead += 1
            else:
                lead_sizes.append(int(lead.sum()))
            if not sels["base"][d]:
                carry_while_decidable += 1

    def _jac(a, b):
        A, B = set(a), set(b)
        if not A and not B:
            return 1.0
        return len(A & B) / len(A | B)

    jac = {v: [] for v in TOP_K}
    for v in TOP_K:
        vals = list(sels[v].values())
        for a, b in zip(vals, vals[1:]):
            jac[v].append(_jac(a, b))
    contain_n = contain_hit = 0
    for d in me_days:
        b, u = set(sels["base"][d]), set(sels["unc"][d])
        if u:
            contain_n += 1
            contain_hit += int(u.issubset(b))
    ls = np.asarray(lead_sizes, dtype=int)
    return {
        "g_panel": {"n_syms": int(close.shape[1]),
                    "panel_first": str(close.index[0].date()),
                    "panel_last": str(close.index[-1].date()),
                    "n_days": int(len(close.index)),
                    "member_row_min": int(close.notna().sum().min()),
                    "member_row_max": int(close.notna().sum().max())},
        "nav_anchor": {"nav_first": round(float(nav.iloc[0]), 6),
                       "nav_last": round(float(nav.iloc[-1]), 6)},
        "month_end_census": {
            "n_month_ends": int(len(me_days)),
            "first_decidable_me": str(decidable_mes[0].date())
            if decidable_mes else None,
            "n_decidable_me": int(len(decidable_mes)),
            "n_me_no_decidable_member": int(len(me_days) - len(decidable_mes)),
            "n_me_zero_leading": int(zero_lead),
            "n_me_carry_while_decidable": int(carry_while_decidable),
            "leading_size_min": int(ls.min()) if len(ls) else None,
            "leading_size_median": float(np.median(ls)) if len(ls) else None,
            "leading_size_max": int(ls.max()) if len(ls) else None},
        "selection_records": recs,
        "variants_jaccard": {
            v: round(float(np.mean(jac[v])), 4) if jac[v] else None
            for v in TOP_K},
        "unc_in_base": {"rate": round(contain_hit / contain_n, 4)
                        if contain_n else None, "n": int(contain_n)},
    }


def anchor_drift(derived, facts):
    """Bit-exact face-by-face reconcile vs the frozen probe facts.
    Returns a drift list (empty = all faces bit-exact)."""
    bad = []
    for k in ("n_syms", "panel_first", "panel_last", "n_days",
              "member_row_min", "member_row_max"):
        if derived["g_panel"][k] != facts["g_panel"][k]:
            bad.append(f"G-PANEL.{k}: {derived['g_panel'][k]} != "
                       f"{facts['g_panel'][k]}")
    for k in ("nav_first", "nav_last"):
        if derived["nav_anchor"][k] != facts["nav_anchor"][k]:
            bad.append(f"nav_anchor.{k}: {derived['nav_anchor'][k]} != "
                       f"{facts['nav_anchor'][k]}")
    for k in ("n_month_ends", "first_decidable_me", "n_decidable_me",
              "n_me_no_decidable_member", "n_me_zero_leading",
              "n_me_carry_while_decidable", "leading_size_min",
              "leading_size_median", "leading_size_max"):
        dv = derived["month_end_census"][k]
        fv = facts["month_end_census"][k]
        if k == "leading_size_median":
            same = (dv is None and fv is None) or \
                (dv is not None and fv is not None
                 and float(dv) == float(fv))
        else:
            same = dv == fv
        if not same:
            bad.append(f"month_end_census.{k}: {dv} != {fv}")
    fr = facts["selection_records"]
    for v in TOP_K:
        drec = derived["selection_records"][v]
        fkeys = list(fr[v].keys())
        if list(drec.keys()) != fkeys:
            bad.append(f"selection_records.{v}: month-end key set drift")
            continue
        for d in fkeys:
            if drec[d] != fr[v][d]:
                bad.append(f"selection_records.{v}[{d}]: "
                           f"{drec[d]} != {fr[v][d]}")
                if len(bad) > 12:
                    return bad          # cap the flood, refusal is total
    for v in TOP_K:
        dv = derived["variants_jaccard"][v]
        fv = facts["variants"][v]["mean_consecutive_jaccard"]
        if dv != fv:
            bad.append(f"variants.{v}.jaccard: {dv} != {fv}")
    if derived["unc_in_base"]["rate"] != facts["variants"]["unc_in_base_rate"] \
            or derived["unc_in_base"]["n"] != facts["variants"]["unc_in_base_n"]:
        bad.append(f"variants.unc_in_base: {derived['unc_in_base']} != "
                   f"({facts['variants']['unc_in_base_rate']}, "
                   f"{facts['variants']['unc_in_base_n']})")
    return bad


def load_probe_facts(path=None):
    with open(path or PROBE_FACTS, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------- attrition
def _att_json_path():
    """prereg s6: the EXECUTING machine's lane file (gate_attrition.<id>
    .json); shared-file fallback when machine.json unreadable."""
    try:
        with open(MACHINE_JSON, encoding="utf-8") as fh:
            mid = json.load(fh).get("machine_id")
        if mid:
            return os.path.join(ROOT, "results",
                                f"gate_attrition.{mid}.json")
    except Exception:
        pass
    return ATT_JSON_SHARED


def _attr_row(batch, delta, total, gates, entries):
    path = _ATT_OVERRIDE or _att_json_path()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    else:
        d = {"entries": []}
    row = {"batch": batch,
           "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "kind": "measurement", "cells_ledger_delta": delta,
           "ledger_total_after": total, "gates": gates,
           "entries": entries}
    own = [i for i, e in enumerate(d["entries"])
           if e.get("batch") == batch and e.get("kind") == "measurement"]
    if own:
        d["entries"][own[-1]] = row
    else:
        d["entries"].append(row)
    with open(path + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(path + ".tmp", path)


# --------------------------------------------------------- starts / splits
def virtual_starts(series_by_face, passive):
    """K=1000 random virtual starts x 3 windows (law s1); one rng per k
    shared across faces (per-window identical start, nested windows
    honest overlap disclosed); beat = cell window cum (own cost face)
    > pool-EW benchmark window cum (prereg s3 benchmark law)."""
    out = {"n_starts": K_STARTS, "windows_days": WIN_DAYS, "cells": {}}
    n = len(passive)
    wmax = max(WIN_DAYS.values())
    los = []
    for k in range(K_STARTS):
        rng = np.random.default_rng([SEED, k])
        los.append(int(rng.integers(0, n - wmax)))
    for name, ser in series_by_face.items():
        s = np.asarray(ser, dtype=float)
        wins = {}
        for wname, w in WIN_DAYS.items():
            hits = 0
            for k in range(K_STARTS):
                lo = los[k]
                hits += int(cum_ret(s, lo, lo + w) >
                            cum_ret(passive, lo, lo + w))
            wins[wname] = {"beats": hits,
                           "beat_rate": round(hits / K_STARTS, 4)}
        out["cells"][name] = wins
    return out


def split_windows(series_by_face):
    """100 random split windows (law s3): split point in [0.2n, 0.8n],
    half-window Sharpe same-sign rate >= 80% = segment-stable."""
    out = {}
    for name, ser in series_by_face.items():
        r = np.asarray(ser, dtype=float)
        n = len(r)
        agree = 0
        for k in range(K_SPLITS):
            rng = np.random.default_rng([SEED, 1000 + k])
            cut = int(rng.integers(int(0.2 * n), int(0.8 * n)))
            a, b = sharpe_of(r[:cut]), sharpe_of(r[cut:])
            agree += int((a > 0) == (b > 0))
        rate = agree / K_SPLITS
        out[name] = {"same_sign_rate": round(rate, 4),
                     "segment_stable": bool(rate >= 0.80),
                     "n_splits": K_SPLITS}
    return out


# --------------------------------------------------------------- drivers
def cmd_verify(facts=None, close=None):
    """Real-panel G-ANCHOR reconcile (read-only; no engine, no product,
    no ledger). Build-time pre-verification face."""
    facts = facts or load_probe_facts()
    if close is None:
        close, _prices = load_panel()
    derived = derive_faces(close)
    bad = anchor_drift(derived, facts)
    if bad:
        for b in bad[:12]:
            print(f"  drift: {b}")
        print(f"GATE-REFUSE(exit2): G-ANCHOR drift {len(bad)} face(s) vs "
              f"frozen probe facts -- config mismatch VOID (one-face-off "
              f"law)")
        return 2
    print("G-ANCHOR verify: ALL faces bit-exact vs frozen probe facts "
          f"({facts['month_end_census']['n_month_ends']} month-ends x "
          f"{len(TOP_K)} variants, panel {derived['g_panel']['panel_first']}"
          f"..{derived['g_panel']['panel_last']})")
    return 0


def phase1_write(product):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    return product


def finalize(product, cells):
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, encoding="utf-8") as fh:
                old = json.load(fh)
            prev_total = (old.get("trials_ledger") or {}).get("prev_total")
        except Exception:
            prev_total = None
    passive_override = SG.passive_baseline("core48")   # live-read (s4 law)
    gates = {}
    for f3 in CELL_FACES:
        cname = CELL_NAME[f3]
        net = cells[f3]["batch_rets"]
        st = cells[f3]["stats"]
        g1 = SG.g1_prime_v2(st["sharpe_full"], net,
                            batch_cells=BATCH_CELLS, pool="core48",
                            results_dir=OUT_DIR_RESULTS,
                            n_trades=cells[f3]["n_trades"],
                            n_entries=cells[f3]["n_entries"],
                            passive_override=passive_override)
        dsr = SG.deflated_sharpe_ratio(
            net, n_trials=g1["skill_line"]["n_eff"])
        gates[cname] = {"g1_prime_v2": g1, "dsr": dsr,
                        "cost_face_role": "judged" if f3[2] == "x1"
                        else "stress-disclosure"}
    mat = pd.DataFrame({CELL_NAME[f3]: np.asarray(cells[f3]["batch_rets"],
                                                   dtype=float)
                        for f3 in CELL_FACES})
    pbo = cscv_pbo(mat)
    for cname in gates:
        gates[cname]["g2"] = SG.g2_registration_v2(
            gates[cname]["g1_prime_v2"]["pass_v2"], gates[cname]["dsr"],
            float(pbo["pbo"]))
    ledger = SG.append_ledger(BATCH_NAME, BATCH_CELLS,
                              file_name="results/innovation_quota/"
                                        "RRG-ROTATION-P1.json",
                              evidence_cutoff=EVIDENCE_CUTOFF,
                              prev_total=prev_total)
    product["gates"] = gates
    product["family_pbo"] = pbo
    product["passive_override_fed"] = passive_override
    n_pass = sum(1 for g in gates.values()
                 if g["g1_prime_v2"]["pass_v2"])
    n_g2 = sum(1 for g in gates.values() if g["g2"]["eligible_v2"])
    product["funnel"] = {
        "harvest_column": 1,
        "harvest_note": "zoo #91 rrg_quadrant_rotation param-frozen "
                        "untried family, r459 probe facts (quota line: "
                        "first cross-sectional quadrant-rotation gate)",
        "gate_column": f"{n_pass}/{BATCH_CELLS} g1_prime_v2 pass, "
                       f"{n_g2}/{BATCH_CELLS} G2-eligible (judged)",
    }
    product["trials_ledger"] = ledger          # r434 pit law: value carried
    product["judgment_note"] = ("judged per prereg s4 via shared library "
                                "(batch_cells=4 s0 counting law, every "
                                "cell pays); judged-negative family = "
                                "slot closed + new-evidence reopen note "
                                "(law s5); G2-eligible cell = T-34 "
                                "fastline candidate pool registration "
                                "face, intake walks the CE admission "
                                "harness separately; T0 brake authority "
                                "stays with REGIME_GUARD")
    phase1_write(product)
    _attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]),
              {"g1_pass": {c: gates[c]["g1_prime_v2"]["pass_v2"]
                           for c in gates},
               "g2_eligible": {c: gates[c]["g2"]["eligible_v2"]
                               for c in gates},
               "family_pbo": pbo},
              {"n_trades": {CELL_NAME[f3]: cells[f3]["n_trades"]
                            for f3 in CELL_FACES},
               "n_entries": {CELL_NAME[f3]: cells[f3]["n_entries"]
                             for f3 in CELL_FACES}})
    return product


def cmd_run():
    global SEED
    if SEED_KEY not in SG.SEED_REGISTRY:
        return gate_refuse(f"SEED_REGISTRY key {SEED_KEY} missing "
                           f"(freeze-window registration absent)")
    SEED = SG.SEED_REGISTRY[SEED_KEY]
    t0 = time.time()
    facts = load_probe_facts()
    if _PANEL_OVERRIDE is not None:
        close, prices = _PANEL_OVERRIDE
    else:
        close, prices = load_panel()
    derived = derive_faces(close)
    bad = anchor_drift(derived, facts)
    if bad:
        for b in bad[:12]:
            print(f"  drift: {b}")
        return gate_refuse(f"G-ANCHOR drift {len(bad)} face(s) vs frozen "
                           f"probe facts -- config mismatch VOID "
                           f"(one-face-off law)")
    print(f"G-ANCHOR reconcile: bit-exact ({time.time() - t0:.0f}s)",
          flush=True)

    lo_ts = pd.Timestamp(BATCH_LO)
    if lo_ts not in close.index:
        return gate_refuse(f"batch lo {BATCH_LO} not a panel bar")
    lo = int(close.index.get_loc(lo_ts))
    nav, _rs_ratio, _rs_mom = build_rrg_faces(close)
    passive_full = nav.pct_change().fillna(0.0)
    passive_ser = passive_full[passive_full.index >= lo_ts].to_numpy()
    passive_ew_stats = _cell_stats(passive_ser)
    years = len(passive_ser) / float(PBP)

    cells = {}
    for f3 in CELL_FACES:
        variant, mult, face = f3
        cname = CELL_NAME[f3]
        rets_full, n_trades, metrics = variant_cell(close, prices,
                                                    variant, cost_mult=mult)
        n_entries = int(metrics.get("num_entries", n_trades))
        r = rets_full[rets_full.index >= lo_ts]
        batch_rets = r.to_numpy()
        cells[f3] = {
            "batch_rets": batch_rets,
            "n_trades": int(n_trades), "n_entries": n_entries,
            "stats": _cell_stats(batch_rets),
            "engine_full_metrics": _jsonable_metrics(metrics),
        }
        print(f"  cell {cname}: sharpe={cells[f3]['stats']['sharpe_full']} "
              f"trades={n_trades} entries={n_entries} "
              f"({time.time() - t0:.0f}s)", flush=True)
    # engine n_trades anchor vs frozen probe facts (x1 cells bind;
    # None in synthetic selftest facts = tolerated non-face)
    nt_probe = {"base": facts["variants"]["base"]["n_trades_engine_face"],
                "unc": facts["variants"]["unc"]["n_trades_engine_face"]}
    for f3 in CELL_FACES:
        variant, mult, face = f3
        if face == "x1" and nt_probe[variant] is not None and \
                cells[f3]["n_trades"] != nt_probe[variant]:
            return gate_refuse(
                f"engine n_trades drift {CELL_NAME[f3]}: "
                f"{cells[f3]['n_trades']} != {nt_probe[variant]} "
                f"(frozen probe face)")

    series_by_face = {CELL_NAME[f3]: cells[f3]["batch_rets"]
                      for f3 in CELL_FACES}
    vstarts = virtual_starts(series_by_face, passive_ser)
    splits = split_windows({**series_by_face, "PASSIVE-EW-BENCH": passive_ser})

    cells_out = {}
    for f3 in CELL_FACES:
        variant, mult, face = f3
        cname = CELL_NAME[f3]
        c = cells[f3]
        epy = c["n_entries"] / years
        cells_out[cname] = {
            "variant": variant, "cost_face": face, "cost_mult": mult,
            "position_size_pct": PS[variant], "top_k": TOP_K[variant],
            **c["stats"],
            "n_trades": c["n_trades"], "n_entries": c["n_entries"],
            "entries_per_year": round(epy, 2),
            "turnover_budget_ok": bool(epy <= TURNOVER_BUDGET),
            "engine_full_metrics": c["engine_full_metrics"],
        }
    product = {
        "batch": BATCH_NAME,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "prereg": "research/INNOVATION_QUOTA_W6_PREREG.md (r458 bm-a "
                  "berth + r459 bm-a freeze, seed 20324500)",
        "prereg_sha256_16": _sha256_file(os.path.join(
            ROOT, "research", "INNOVATION_QUOTA_W6_PREREG.md"))[:16],
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "seed": {"base": SEED,
                 "k_substreams": "starts k in [0,1000); splits k in "
                                 "[1000,1100) -- rng([SEED, k]) one "
                                 "k-stream shared across cells/faces; "
                                 "no own-null family (shared core48 "
                                 "collector, prereg s4)"},
        "panel": derived["g_panel"],
        "nav_anchor": derived["nav_anchor"],
        "month_end_census": derived["month_end_census"],
        "selection_records": derived["selection_records"],
        "construction": "verbatim-import results/_r459bma_rrg_w6_probe.py "
                        "(r456 paradigm): RS-Ratio MA20 ratio method hub "
                        "100, RS-Momentum MA20, leading=both>100, top-k "
                        "by hub distance code-asc tie-break, zero-"
                        "leading carry; month-end close decision T+1 "
                        "engine fills (T33 gem_entry causality)",
        "variants": {"base": {"top_k": TOP_K["base"],
                              "position_size_pct": PS["base"]},
                     "unc": {"top_k": TOP_K["unc"],
                             "position_size_pct": PS["unc"]}},
        "batch_window": {"lo": BATCH_LO,
                         "first_decidable_me":
                             facts["month_end_census"]["first_decidable_me"],
                         "law": "lo = first-decidable month-end next bar "
                                "(W5 max(first_decidable)+1 same law); "
                                "four-cell shared window for cross-cell "
                                "PBO/CSCV alignment"},
        "cost_face": {"x1_rate_per_side": COST_X1_RATE,
                      "judged_face": "x1 (V1 legacy base)",
                      "x2_disclosure": "CostPatch(2.0) = 26.082bp/side "
                                      "stress face",
                      "turnover_budget_per_year": TURNOVER_BUDGET},
        "passive": {"passive_ew_bench": passive_ew_stats,
                    "note": "pool-EW benchmark = RRG construction's own "
                            "benchmark (prereg s3); G1' passive term = "
                            "core48 calibration artifact live-read "
                            "(separate face, prereg s4)"},
        "nulls": {"consumed": "shared core48 collector (K=0 own nulls, "
                              "prereg s4 / T33 same door)"},
        "cells": cells_out,
        "virtual_starts": vstarts, "splits": splits,
        "d6": {**facts["d6"],
               "reject_line": D6_REJECT,
               "provenance": "frozen at r459 probe window verbatim "
                             "(results/_r459bma_rrg_w6_probe_facts.json); "
                             "merge clause zero triggers = admission "
                             "record binding, not re-computed"},
    }
    product = phase1_write(product)
    print(f"phase-1 product written ({time.time() - t0:.0f}s)", flush=True)
    product = finalize(product, cells)
    n_pass = sum(1 for g in product["gates"].values()
                 if g["g1_prime_v2"]["pass_v2"])
    print(f"finalize ok: cells={len(cells)} g1_pass={n_pass}/{BATCH_CELLS} "
          f"ledger={product['trials_ledger']['total']} "
          f"elapsed={time.time() - t0:.0f}s")
    return 0


# --------------------------------------------------------------- selftest
def _mk_synthetic_panel(tmp, n_syms=48):
    """Synthetic core48-like panel: 48 symbols with planted relative-
    strength drift segments so the quadrant state machine produces
    leading sets, month-end selections, carries and jaccard structure
    on both variants (engine consumes the same OHLCV face as real)."""
    dates = pd.bdate_range("2020-01-02", end="2026-09-22")
    n = len(dates)
    rng = np.random.default_rng(11)
    base = 0.002 * np.sin(np.arange(n) / 37.0)   # common market factor
    prices = {}
    for i in range(n_syms):
        drift = np.zeros(n)
        for seg in range(6):
            a = int(n * seg / 6)
            b = int(n * (seg + 1) / 6)
            drift[a:b] = rng.uniform(-0.0012, 0.0018)
        drift[0:320] = 0.0            # warmup face
        ret = base + drift + rng.normal(0, 0.008, n)
        close = pd.Series(2.0 * np.cumprod(1.0 + ret), index=dates)
        prices[f"sz{159900 + i}"] = pd.DataFrame(
            {"open": close * 0.999, "high": close * 1.01,
             "low": close * 0.99, "close": close,
             "volume": 1e6, "amount": 1e7}, index=dates)
    return prices


def cmd_selftest():
    global PROBE_FACTS, OUT_DIR, OUT_JSON, _PANEL_OVERRIDE, _ATT_OVERRIDE
    tmp = tempfile.mkdtemp(prefix="innovation_quota_w6_selftest_")
    ok = []
    try:
        prices = _mk_synthetic_panel(tmp)
        close = pd.DataFrame({s: df["close"] for s, df in prices.items()})
        derived = derive_faces(close)
        snap = json.loads(json.dumps(derived))   # deep snapshot (mutation
        # of the facts face must never alias back into derived)
        facts = {"probe": "synthetic selftest facts",
                 "g_panel": snap["g_panel"],
                 "nav_anchor": snap["nav_anchor"],
                 "month_end_census": snap["month_end_census"],
                 "selection_records": json.loads(json.dumps(
                     snap["selection_records"])),   # independent copy:
                 # perturb must never alias back into the restore source
                 "variants": {"base": {"top_k": 6,
                                       "n_trades_engine_face": None,
                                       "mean_consecutive_jaccard":
                                           derived["variants_jaccard"]["base"]},
                              "unc": {"top_k": 2,
                                      "n_trades_engine_face": None,
                                      "mean_consecutive_jaccard":
                                          derived["variants_jaccard"]["unc"]},
                              "unc_in_base_rate": derived["unc_in_base"]["rate"],
                              "unc_in_base_n": derived["unc_in_base"]["n"]},
                 "d6": {"batch_internal_base_vs_unc": 0.0,
                        "vs_t33_cells": {}, "merge_clause_applied": [],
                        "vs_registered_six": {"max_abs_corr": None,
                                              "argmax": None}}}
        facts_path = os.path.join(tmp, "facts.json")
        with open(facts_path, "w", encoding="utf-8") as fh:
            json.dump(facts, fh)
        PROBE_FACTS = facts_path
        ok.append(("anchor reconcile on derived facts (clean pass)",
                   cmd_verify(facts=facts, close=close) == 0))
        # drift refusal: perturb one selection record
        k0 = list(facts["selection_records"]["base"].keys())[0]
        facts["selection_records"]["base"][k0] = ["zz"]
        with open(facts_path, "w", encoding="utf-8") as fh:
            json.dump(facts, fh)
        ok.append(("anchor drift refusal (rc=2)",
                   cmd_verify(close=close) == 2))
        # restore
        facts["selection_records"]["base"][k0] = \
            snap["selection_records"]["base"][k0]
        with open(facts_path, "w", encoding="utf-8") as fh:
            json.dump(facts, fh)
        ok.append(("anchor restored -> clean again",
                   cmd_verify(close=close) == 0))

        # ---- full pipeline on synthetic panel, stateful faces stubbed
        OUT_DIR = os.path.join(tmp, "innovation_quota")
        OUT_JSON = os.path.join(OUT_DIR, "RRG-ROTATION-P1.json")
        _ATT_OVERRIDE = os.path.join(tmp, "gate_attrition.lane.json")
        _PANEL_OVERRIDE = (close, prices)
        _ne, _al, _pb = (SG.n_eff, SG.append_ledger, SG.passive_baseline)
        _real_cscv = globals()["cscv_pbo"]
        SG.n_eff = lambda bc, rd=None: int(bc)
        SG.append_ledger = lambda *a, **k: {"prev_total": 0, "total": 100,
                                            "batch": BATCH_NAME}
        SG.passive_baseline = lambda *a, **k: 0.10
        globals()["cscv_pbo"] = lambda mat: {"pbo": 0.1}
        try:
            rc = cmd_run()
            ok.append(("cmd_run on synthetic panel rc=0", rc == 0))
            if rc == 0:
                with open(OUT_JSON, encoding="utf-8") as fh:
                    prod = json.load(fh)
                ok.append(("product faces (cutoff_meta/cells/ledger)",
                           prod["evidence_cutoff"] == EVIDENCE_CUTOFF
                           and "cutoff_meta" in prod
                           and len(prod["cells"]) == 4
                           and set(prod["cells"]) == set(CELL_NAME.values())
                           and prod["trials_ledger"]["total"] == 100
                           and prod["passive_override_fed"] == 0.10))
                ok.append(("turnover budget flag face",
                           all("entries_per_year" in c
                               and "turnover_budget_ok" in c
                               for c in prod["cells"].values())))
                ok.append(("virtual starts 3-window + splits 100",
                           set(prod["virtual_starts"]["cells"])
                           == set(CELL_NAME.values())
                           and set(prod["virtual_starts"]["windows_days"])
                           == {"6m", "12m", "24m"}
                           and all(v["n_splits"] == 100
                                   for v in prod["splits"].values())))
                ok.append(("attrition lane row landed",
                           os.path.exists(_ATT_OVERRIDE)
                           and json.load(open(_ATT_OVERRIDE))["entries"][-1]
                           ["batch"] == BATCH_NAME))
                # ---- r450 landed-state guard
                ok.append(("r450 guard: judged product refuses (rc=2)",
                           _refuse_if_judged() == 2))
                with open(OUT_JSON + ".t", "w", encoding="utf-8") as fh:
                    json.dump({"phase1": True}, fh)
                os.replace(OUT_JSON + ".t", OUT_JSON)
                ok.append(("r450 guard: phase-1-only resumes (rc=0)",
                           _refuse_if_judged() == 0))
        finally:
            SG.n_eff, SG.append_ledger, SG.passive_baseline = _ne, _al, _pb
            globals()["cscv_pbo"] = _real_cscv
            _PANEL_OVERRIDE = None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n_okk = sum(1 for _, v in ok if v)
    print(f"innovation_quota_w6 selftest: {n_okk}/{len(ok)} PASS")
    for name, v in ok:
        if not v:
            print(f"  FAIL: {name}")
    return 0 if n_okk == len(ok) else 1


# ------------------------------------------------------------------ guard
def _refuse_if_judged():
    """r450 landed-state guard: read CONTENT (trials_ledger block), not
    existence/timestamps. Judged product refuses re-run (rc=2) unless
    INNOVATION_QUOTA_W6_REFINALIZE=1; phase-1-only product resumes."""
    if not os.path.exists(OUT_JSON):
        return 0
    try:
        with open(OUT_JSON, encoding="utf-8") as fh:
            old = json.load(fh)
    except Exception:
        return 0        # unreadable partial write -> resume path
    if (old.get("trials_ledger") or {}).get("total") is not None and \
            os.environ.get("INNOVATION_QUOTA_W6_REFINALIZE") != "1":
        print("GATE-REFUSE(exit2): RRG-ROTATION-P1.json already "
              "judged (trials_ledger present, content-read per r450); "
              "INNOVATION_QUOTA_W6_REFINALIZE=1 = only redo")
        return 2
    return 0


def main():
    try:
        # r236 GBK-console law: reconfigure at entry
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "verify", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return cmd_selftest()
    if a.cmd == "verify":
        return cmd_verify()
    guard = _refuse_if_judged()
    if guard:
        return guard
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
