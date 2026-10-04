"""r692 bm-a N2-W15 slice-2 generate-machinery smoke probe.

Real-path plumbing verification (r494 real-run law) WITHOUT any batch
product: 6 subspace draws through the full generate face chain (draw ->
tl14 exclusion real-read -> signal frame -> 14-overlay effective mask ->
fingerprint + naive returns -> collapse) on the REAL leg-L panel.
Zero candidates-file write, zero ledger, zero registry write (bands
simulated in-memory only; the live registry stays DRAFT-pending).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import numpy as np
import pandas as pd

import science_gates as sg
import trial_labor_w1 as tl1
import trial_labor_w2 as tl2
import trial_labor_w3 as tl3
import trial_labor_w4 as tl4
import trial_labor_w5 as tl5
import trial_labor_w6 as tl6
import trial_labor_w7 as tl7
import trial_labor_w8 as tl8
import trial_labor_w14 as tl14
import perpetual_faces_n2 as n2

t0 = time.time()
# --- in-memory band simulation ONLY (live registry untouched) ---
sg.SEED_REGISTRY["perpetual_n2_w15_gen"] = n2.BAND_GEN
sg.SEED_REGISTRY["perpetual_n2_w15_scrnull"] = n2.BAND_SCRNULL
sg.SEED_REGISTRY["perpetual_n2_w15_unc"] = n2.BAND_UNC
gate_ok, gate_bad = n2._bands_registered()
assert gate_ok, f"freeze-gate sim failed: {gate_bad}"

grammar = n2.load_grammar()
tl1.GRAMMAR = grammar
prices, P, idx, listed, cen = tl1._load_leg("L")
close = P["close"]
try:
    bl = pd.read_csv(tl1.B_LAYER_MASK)
    ok_codes = set(bl.loc[bl["ok_static"] == True, "code"].astype(str))
    overlap = sorted(s for s in close.columns if s in ok_codes)
except Exception:
    overlap = []
fundamental_ok = None
if overlap:
    fundamental_ok = pd.DataFrame(False, index=close.index,
                                  columns=close.columns)
    for s in overlap:
        fundamental_ok[s] = True
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
print(f"exclusion rows real-read: {len(excl_rows)}; sources: "
      f"{len(excl_disc) if isinstance(excl_disc, (list, dict)) else excl_disc}")

cands, excl_hits = [], 0
for fam, slot in (("A", 0), ("B", 0)):
    for i, (_, cand) in enumerate(n2.draw_candidate_subspace_w15(
            grammar, fam, slot, 3, n2.SEED_GEN)):
        cand["candidate_id"] = f"SMOKE-{fam}-{i:02d}"
        if fam == "A":
            cand["template_trader"] = \
                grammar["families"]["A"][slot]["trader_id"]
        hit = tl14._excluded_w14(cand, excl_rows)
        if hit:
            excl_hits += 1
            continue
        cands.append(cand)
print(f"draws 6 -> excluded {excl_hits} -> kept {len(cands)}")

fps, series = [], []
for cand in cands:
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
keep, fp_col, corr_elim = n2._collapse_by_fingerprint(fps, series, cands)
print(f"dedup: fp groups {len(fp_col)}, corr collapses {len(corr_elim)},"
      f" final keep {len(keep)} of {len(cands)}")

# screen-machinery cross-face: one candidate through the REAL engine
# with the shared worker-state face (probe-face parity) -- proves the
# run-leg state wiring end-to-end (zero checkpoint, zero claim)
prep_stub = {"starts": [p for p in range(len(idx))
                        if idx[p] >= tl1.LEG_L_FLOOR
                        and p >= tl1.WARMUP_TD
                        and p <= len(idx) - 1 - n2.W6M
                        and listed.iloc[p] >= tl1.MIN_LISTED][:50],
             "passive_6m_ret": {}}
for p in prep_stub["starts"][:50]:
    sdate, edate = idx[p], idx[p + n2.W6M - 1]
    syms = close.columns[close.loc[sdate].notna()]
    rel = tl1.passive_rel(close, syms, sdate, edate)
    prep_stub["passive_6m_ret"][int(p)] = round(
        float(rel.iloc[-1] - 1.0), 6)
state = n2._leg_state_shared(prices, P, fundamental_ok, grammar,
                             prep_stub)
tl1._init_worker(state)          # REAL worker initializer path
cell = {"cell_id": "SMOKE|ONE", "kind": "cand",
        "cand": cands[0],
        "template": ({t["trader_id"]: t for t in tl1.A_TEMPLATES}
                      .get(cands[0].get("template_trader"))
                      if cands[0]["family"] == "A" else None)}
row = n2._screen_cell_w15(cell)
print(f"engine row: k_active={row['k_active']} "
      f"entries={row['n_entries']} beat6m_k={row['beat6m_k']} "
      f"rate={row['beat6m_rate']} no_entries={row['no_entries']}")

payload = {"probe": "n2_w15_generate_machinery_smoke",
           "generated": n2._now_iso(), "machine": n2._machine_id(),
           "evidence_cutoff": n2.CUTOFF,
           "freeze_gate_sim": "in-memory only (live registry DRAFT)",
           "draws": 6, "excluded": excl_hits, "dedup_keep": len(keep),
           "engine_row": {k: row[k] for k in
                          ("k_active", "n_entries", "beat6m_k",
                           "beat6m_rate", "no_entries")},
           "ledger_effect": 0, "registry_write": False,
           "elapsed_s": round(time.time() - t0, 2)}
out = os.path.join(tl1.PATHS.results_dir,
                   "_r692bma_n2_gen_smoke.json")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump(payload, f, ensure_ascii=False, indent=1, default=float)
print(f"SMOKE PASS -> {os.path.relpath(out, tl1.PATHS.root)} "
      f"({payload['elapsed_s']}s)")
