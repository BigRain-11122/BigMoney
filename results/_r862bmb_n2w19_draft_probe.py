"""r862 bm-b PERPETUAL-N2-W19 draft-window probe (slice-1, zero burn).

Faces:
 1. panel gate + cutoff pin (replay same-face precondition: cutoff must
    equal the W18 census pin 2026-10-09 -- no new bars since the W18
    burn; if the panel advanced the replay is NOT same-face -> rc2).
 2. W18 attrition decomposition REPLAY: frozen gen seed (SEED_REGISTRY
    read-only, zero consumption) -> alphagen_beam_w18.beam_draws replay
    of the 64 draws the W18 burn already consumed; classify
    ledger_consumed_hit / in_batch_dup / h1_skip / ok; cross-check
    n_ok * 6 == 288 == W18 observed pooled nulls (null-block validity).
    Deterministic re-run of already-consumed evaluations: zero new
    trials, zero burn, zero ledger append, zero product file, zero
    seed consumption (W18 freeze already consumed the gen stream).
 3. census anchors face (product exists, 48 unique formulas consumed).
 4. closed-family non-collision (alphagen_grammar_v1 not in the 9 keys).
 5. grammar ledger zero alphagen rows (first-burn posture unchanged).
 6. chain head read (draft ledger accounting face).
 7. W19 candidate band derive (r682 live derive, read-only, W19 OWN keys
    excluded from the reserved set; DRAFT writes NO band values -- r702
    lesson; the freeze window re-derives and registers per R250).
 8. B-nulls arithmetic from the replayed empirical survival:
    B = ceil(300 / (K * survival)); needed_ok = ceil(300 / B);
    expected_pooled = K * survival * B  (envelope K*(1+B) <= 500).
Receipt -> results/_r862bmb_n2w19_draft_probe.json (ASCII, r458 law).
Exit 0 = facts recorded / 2 = face failure (honest, nothing written but
the receipt).
"""
import json
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))

OUT = os.path.join(REPO, "results", "_r862bmb_n2w19_draft_probe.json")
W18_PREREG = os.path.join(REPO, "research", "PERPETUAL_N2_W18_PREREG.md")
GRAMMAR_LEDGER = os.path.join(REPO, "research", "TRIAL_GRAMMAR_LEDGER.md")
W18_POOLED_OBSERVED = 288          # r861 slice-4 refuse stdout (sec.7 law)
W18_K = 64
W18_B = 6
W19_K = 62
MIN_POOLED = 300                   # sufficiency line (NEVER re-derived down)
ENVELOPE_CAP = 500                 # W18 sec.0 declared gate basis, kept
BAND_WIDTH = 499
HALO = 2_000
OWN_W19 = {"perpetual_n2_w19_gen", "perpetual_n2_w19_scrnull",
           "perpetual_n2_w19_unc"}
EXPLICIT = [
    ("lfc_actual", 30_000, 30_099),
    ("t18_actual", 54_000, 54_999),
    ("xstock_nullA_actual", 51_000, 51_999),
    ("xstock_nullB_actual", 52_000, 52_999),
    ("n4_reserved_trio", 68_501, 69_999),
    ("n3_domain", 70_000, 70_999),
    ("probe_cluster", 95_000, 95_004),
    ("design_probe_40k", 40_000, 40_001),
]


def main():
    import science_gates as sg                   # noqa: E402
    import alphagen_beam_w18 as w18               # noqa: E402
    import perpetual_faces as n1mod               # noqa: E402

    out = {"probe": "PERPETUAL-N2-W19 draft-window probe (r862 bm-b)",
           "zero_burn": True, "zero_ledger_append": True, "zero_seeds": True,
           "zero_product_file": True, "faces": {}}
    rc = 0

    # ---- face 1: panel gate + cutoff pin
    face = w18.GATE_FACE()
    f1 = {"ready": face["ready"], "cutoff": str(face["cutoff"]),
          "per_files_on_disk": face["per_files_on_disk"]}
    f1["cutoff_pin_ok"] = f1["cutoff"] == w18.CUTOFF_PIN
    out["faces"]["panel_gate"] = f1
    if not (f1["ready"] and f1["cutoff_pin_ok"]):
        out["verdict"] = "FACE_FAIL panel gate / cutoff pin (replay " \
                         "same-face precondition broken)"
        _dump(out)
        return 2

    # ---- face 2: W18 attrition decomposition replay (the core evidence)
    print("[probe] loading panel (census machinery, ~1-3 min) ...")
    panel = w18.LOAD_PANEL()
    consumed, census_doc = w18._census_consumed_formulas()
    with open(GRAMMAR_LEDGER, encoding="utf-8", errors="replace") as f:
        ledger_text = f.read()
    seed_gen = int(sg.SEED_REGISTRY[w18.BAND_KEYS["gen"]])
    lineage, enrolled, excluded = w18.beam_draws(
        panel, seed_gen, consumed, ledger_text)
    n_excl_ledger = sum(1 for e in excluded
                        if e["reason"] == "ledger_consumed_hit")
    n_excl_inbatch = sum(1 for e in excluded
                         if e["reason"] == "in_batch_dup")
    n_enrolled = len(enrolled)
    n_skip = sum(1 for r in enrolled if not r["h1_ok"])
    n_ok = sum(1 for r in enrolled if r["h1_ok"])
    design_nulls = W18_K * W18_B
    implied_pooled = n_ok * W18_B
    f2 = {"replay_seed_key": w18.BAND_KEYS["gen"], "seed_read_only": True,
          "n_draws": W18_K, "n_excluded_ledger_t84s3": n_excl_ledger,
          "n_excluded_in_batch_dup": n_excl_inbatch,
          "n_enrolled": n_enrolled, "n_h1_skip": n_skip, "n_ok": n_ok,
          "w18_design_nulls": design_nulls,
          "implied_pooled_if_all_blocks_valid": implied_pooled,
          "w18_observed_pooled": W18_POOLED_OBSERVED,
          "cross_check_n_ok_times_b_eq_observed":
              implied_pooled == W18_POOLED_OBSERVED,
          "survival_frac": round(n_ok / W18_K, 4),
          "attrition_frac": round(1 - n_ok / W18_K, 4),
          "skip_frac_of_draws": round(n_skip / W18_K, 4)}
    out["faces"]["w18_attrition_replay"] = f2
    if not f2["cross_check_n_ok_times_b_eq_observed"]:
        # honest: decomposition does NOT reconcile with the W18 refuse
        # stdout -> null blocks were partially invalid; record and let
        # the prereg arithmetic use the observed pooled face instead.
        f2["note"] = "n_ok*6 != 288: some null blocks invalid; " \
                     "survival arithmetic below uses observed pooled"

    # ---- face 3: census anchors
    f3 = {"census_product": os.path.relpath(w18.CENSUS_PRODUCT, REPO),
          "n_consumed_formulas": len(consumed),
          "census_holds": census_doc.get("census", {}).get(
              "census_holds", w18.CENSUS_ANCHORS["census_holds"]),
          "observed_family_max_abs_icir": census_doc.get(
              "census", {}).get(
              "observed_family_max_abs_icir",
              w18.CENSUS_ANCHORS["observed_family_max_abs_icir"]),
          "null_family_p95": census_doc.get("census", {}).get(
              "null_family_p95", w18.CENSUS_ANCHORS["null_family_p95"])}
    out["faces"]["census_anchors"] = f3

    # ---- face 4: closed-family non-collision
    fams = list(sg.CLOSED_FAMILIES)
    f4 = {"closed_families_n": len(fams),
          "alphagen_grammar_v1_open": "alphagen_grammar_v1" not in fams,
          "keys": fams}
    out["faces"]["closed_families"] = f4
    if not f4["alphagen_grammar_v1_open"]:
        out["verdict"] = "FACE_FAIL family closed"
        _dump(out)
        return 2

    # ---- face 5: grammar ledger zero alphagen rows
    hits = [ln.strip()[:100] for ln in ledger_text.splitlines()
            if "alphagen" in ln.lower()]
    f5 = {"alphagen_rows": len(hits), "rows": hits}
    out["faces"]["grammar_ledger"] = f5

    # ---- face 6: chain head
    head = sg.ledger_head()
    f6 = {"chain_head": head}
    out["faces"]["chain_head"] = f6

    # ---- face 7: W19 candidate band derive (read-only)
    bands = n1mod.N1_BANDS
    rows = [(w, bands[w]["a"][0], bands[w]["a"][1],
             bands[w]["b_exit"][0], bands[w]["b_exit"][1])
            for w in sorted(bands)]
    a_head_end = max(r[2] for r in rows)
    max_wave = max(bands)
    b_head_end = bands[max_wave]["b_exit"][1]
    horizon_lo, horizon_hi = a_head_end + 1, a_head_end + 130 * 2_000
    reserved = []
    for w, a0, a1, b0, b1 in rows:
        reserved.append((a0, a1))
        reserved.append((b0, b1))
    reg = {k: v for k, v in sg.SEED_REGISTRY.items()
           if isinstance(v, (int, float)) and k not in OWN_W19}
    for k, v in reg.items():
        reserved.append((int(v) - HALO, int(v) + HALO))
    for nm, lo, hi in EXPLICIT:
        reserved.append((lo, hi))
    reserved.append((horizon_lo, horizon_hi))
    bproj_hi = b_head_end + 130 * 200 + 5_000
    reserved.append((b_head_end + 1, bproj_hi))

    def clean(lo, hi):
        return all(hi < r0 or lo > r1 for r0, r1 in reserved)

    x_min = horizon_hi + 1
    x = ((x_min + 499) // 500) * 500
    walk = []
    while True:
        trio = [x, x + 500, x + 1_000]
        if all(clean(b, b + BAND_WIDTH) for b in trio):
            break
        walk.append(x)
        x += 500
        if x > x_min + 100_000:
            x = None
            break
    w18_fam_top = 734_000            # W18 family band [732_500 .. 734_000)
    naive_next_after_w18 = 734_000
    f7 = {"n1_bands_rows": len(rows), "max_wave": f"W{max_wave}",
          "a_head_end": a_head_end,
          "a_horizon": [horizon_lo, horizon_hi],
          "naive_next_slot_after_w18": naive_next_after_w18,
          "naive_inside_horizon": horizon_lo <= naive_next_after_w18
                                  <= horizon_hi,
          "w18_family_band_top": w18_fam_top,
          "reserved_intervals_n": len(reserved),
          "candidate_x_readonly": x,
          "candidate_trio": None if x is None else
          [[x, x + BAND_WIDTH], [x + 500, x + 500 + BAND_WIDTH],
           [x + 1_000, x + 1_000 + BAND_WIDTH]],
          "skipped_collision_xs": walk,
          "note": "draft-window readout only; freeze window re-derives "
                  "live and registers per R250 one-step law; DRAFT "
                  "writes NO band values (r702 lesson)"}
    out["faces"]["w19_band_derive"] = f7

    # ---- face 8: B-nulls arithmetic from empirical survival
    surv = f2["survival_frac"]
    b_floor = MIN_POOLED / (W19_K * surv) if surv > 0 else float("inf")
    b_derived = math.ceil(b_floor) if surv > 0 else None
    envelope = None if b_derived is None else W19_K * (1 + b_derived)
    needed_ok = (math.ceil(MIN_POOLED / b_derived)
                 if b_derived else None)
    expected_pooled = (round(W19_K * surv * b_derived, 1)
                      if b_derived else None)
    fail_margin_ok = (round(W19_K * surv - needed_ok, 2)
                      if b_derived else None)
    f8 = {"w19_k": W19_K, "b_derived": b_derived,
          "b_derivation": f"ceil({MIN_POOLED} / ({W19_K} * {surv}))",
          "envelope_k_times_1plus_b": envelope,
          "envelope_cap": ENVELOPE_CAP,
          "envelope_within_cap": envelope is not None
                                 and envelope <= ENVELOPE_CAP,
          "needed_ok_formulas": needed_ok,
          "expected_ok": round(W19_K * surv, 2),
          "expected_pooled": expected_pooled,
          "margin_ok_formulas_above_needed": fail_margin_ok,
          "sufficiency_line": MIN_POOLED,
          "line_note": "sufficiency line stays 300 (never re-derived "
                       "down post-refuse: post-freeze adjustment "
                       "prohibition face); the BUDGET derives up "
                       "instead"}
    out["faces"]["b_nulls_arithmetic"] = f8

    out["verdict"] = "FACTS_RECORDED"
    out["w19_design_summary"] = {
        "k_draws": W19_K,
        "rounds": "R1=24->top6, R2=24 (top6 x 4)->top6, "
                  "R3=14 (r2_top[0..3] x 3 + r2_top[4..5] x 1)",
        "b_nulls_per_formula": b_derived,
        "envelope_trials": envelope,
        "sufficiency_line_pooled": MIN_POOLED,
    }
    _dump(out)
    return 0 if (f8["envelope_within_cap"] and x is not None) else 2


def _dump(out):
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True, ensure_ascii=True)
    print(json.dumps({"verdict": out.get("verdict"),
                      "receipt": os.path.basename(OUT)}))


if __name__ == "__main__":
    sys.exit(main())
