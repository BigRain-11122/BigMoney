"""r865 bm-b PERPETUAL-N2-W20 draft-window probe (slice-1, zero burn).

Replication-wave draft facts (NO replay needed -- W19 refused-burn
zero-decomposition debt was repaid at r864: the SUCCESS payload itself
carries the full attrition decomposition; this probe reads faces, it
never re-runs consumed evaluations):

 1. panel gate + cutoff pin floor (cutoff >= 2026-10-09; Sunday no-op
    expected; pin-slice law makes any later burn same-window -- face
    discloses the current cutoff honestly).
 2. W19 consumed-formulas face: results/alphagen_w19/W19-2026-10-09.json
    -> family.records (51 enrolled = 48 ok + 3 h1-skip) -- the W20
    T-84s3 dedup source grows by these 51 formula strings (each burned
    an h1 evaluation at W19; re-burn would waste a draw slot).
    Reconciliation: 48 ok x B(7) = 336 == observed n_pooled.
 3. census anchors face (48 unique consumed; holds=true; 0.353/0.139 --
    the D1 comparison input, unchanged).
 4. closed-family non-collision (alphagen_grammar_v1 not in the 9 keys).
 5. grammar-ledger text face (alphagen rows == 0; belt-and-braces scan
    source unchanged; the W19 consumed face is carried by the RESULT
    FILE source, disclosed).
 6. chain head read (draft accounting face; expect 877,227).
 7. W20 candidate band derive (r682 live derive, read-only; W20 OWN
    keys excluded from the reserved set; W18+W19 registered keys WITH
    halos included -> walk past the W19 family band top 739,000;
    DRAFT writes NO band values -- r702 lesson; freeze re-derives).
 8. B-nulls arithmetic from the W19 empirical survival (48/62):
    B = ceil(300 / (K * survival)); needed_ok = ceil(300 / B);
    envelope K*(1+B) <= 500. B=7 is the ONLY feasible budget under the
    500 cap (B=8 -> 62*9=558 > cap) -- the survival requirement
    >= 300/(62*7) = 69.04% carries the disclosed risk face (enlarged
    dedup source may raise collisions; refusal receipt protects).

Receipt -> results/_r865bmb_n2w20_draft_probe.json (ASCII, r458 law).
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

OUT = os.path.join(REPO, "results", "_r865bmb_n2w20_draft_probe.json")
W19_PRODUCT = os.path.join(REPO, "results", "alphagen_w19",
                           "W19-2026-10-09.json")
W19_PREREG = os.path.join(REPO, "research", "PERPETUAL_N2_W19_PREREG.md")
W20_PREREG = os.path.join(REPO, "research", "PERPETUAL_N2_W20_PREREG.md")
GRAMMAR_LEDGER = os.path.join(REPO, "research", "TRIAL_GRAMMAR_LEDGER.md")
CENSUS_PRODUCT = os.path.join(REPO, "results", "t23_census",
                              "CENSUS-2026-10-09.json")
W19_K = 62
W20_K = 62
W19_B = 7
W19_POOLED_OBSERVED = 336          # r864 slice-4 success stdout (sec.7)
W19_OK_OBSERVED = 48
W19_ENROLLED_OBSERVED = 51
MIN_POOLED = 300                   # sufficiency line (NEVER re-derived down)
ENVELOPE_CAP = 500
BAND_WIDTH = 499
HALO = 2_000
OWN_W20 = {"perpetual_n2_w20_gen", "perpetual_n2_w20_scrnull",
           "perpetual_n2_w20_unc"}
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
    import t23_random_grammar_census as t23      # noqa: E402
    import perpetual_faces as n1mod              # noqa: E402

    out = {"probe": "PERPETUAL-N2-W20 draft-window probe (r865 bm-b)",
           "zero_burn": True, "zero_ledger_append": True, "zero_seeds": True,
           "zero_product_file": True, "faces": {}}
    rc = 0

    # ---- face 1: panel gate + cutoff pin floor (pin-slice law: burn may
    # land on any later day; the window is truncated to the pin)
    face = t23.gate_face()
    f1 = {"ready": face["ready"], "cutoff": str(face["cutoff"]),
          "per_files_on_disk": face["per_files_on_disk"],
          "cutoff_pin": "2026-10-09",
          "cutoff_floor_ok": str(face["cutoff"]) >= "2026-10-09",
          "same_instant_now": str(face["cutoff"]) == "2026-10-09"}
    out["faces"]["panel_gate"] = f1
    if not (f1["ready"] and f1["cutoff_floor_ok"]):
        out["verdict"] = "FACE_FAIL panel gate / cutoff floor"
        _dump(out)
        return 2

    # ---- face 2: W19 consumed-formulas face (the new W20 dedup source)
    with open(W19_PRODUCT, encoding="utf-8") as f:
        w19 = json.load(f)
    recs = w19["family"]["records"]
    ok_recs = [r for r in recs if r.get("h1_ok")]
    skip_recs = [r for r in recs if not r.get("h1_ok")]
    w19_formulas = [r["formula"] for r in recs]
    dd = w19["audit"]["attrition_decomposition"]
    f2 = {"w19_product": "results/alphagen_w19/W19-2026-10-09.json",
          "n_records": len(recs), "n_ok": len(ok_recs),
          "n_h1_skip": len(skip_recs),
          "unique_formulas": len(set(w19_formulas)),
          "dedup_source_grows_by": len(set(w19_formulas)),
          "decomp_reconciliation": {
              "n_enrolled": dd["n_enrolled"],
              "n_excluded_ledger_t84s3": dd["n_excluded_ledger_t84s3"],
              "n_excluded_in_batch_dup": dd["n_excluded_in_batch_dup"],
              "n_h1_skip": dd["n_h1_skip"], "n_ok": dd["n_ok"],
              "n_pooled": dd["n_pooled"],
              "ok_times_b_eq_observed":
                  dd["n_ok"] * W19_B == W19_POOLED_OBSERVED
                  == dd["n_pooled"],
              "envelope_reconciliation":
                  dd["n_enrolled"] + dd["n_excluded_ledger_t84s3"]
                  + dd["n_excluded_in_batch_dup"] == W19_K},
          "survival_frac_of_draws": round(dd["n_ok"] / W19_K, 4),
          "attrition_frac_of_draws": round(1 - dd["n_ok"] / W19_K, 4),
          "skip_frac_of_enrolled":
              round(dd["n_h1_skip"] / dd["n_enrolled"], 4)}
    out["faces"]["w19_consumed_face"] = f2
    if not (f2["decomp_reconciliation"]["ok_times_b_eq_observed"]
            and f2["decomp_reconciliation"]["envelope_reconciliation"]
            and len(set(w19_formulas)) == W19_ENROLLED_OBSERVED
            and len(ok_recs) == W19_OK_OBSERVED):
        out["verdict"] = "FACE_FAIL W19 consumed face does not reconcile"
        _dump(out)
        return 2

    # ---- face 3: census anchors (+ union with the new W19 source)
    with open(CENSUS_PRODUCT, encoding="utf-8") as f:
        census = json.load(f)
    census_formulas = {r["formula"]
                       for r in census["census"]["formulas"]}
    union = census_formulas | set(w19_formulas)
    f3 = {"census_product": "results/t23_census/CENSUS-2026-10-09.json",
          "n_consumed_formulas": len(census_formulas),
          "census_holds": census["census"]["census_holds"],
          "observed_family_max_abs_icir":
              census["census"]["observed_family_max_abs_icir"],
          "null_family_p95": census["census"]["null_family_p95"],
          "union_census_w19": len(union),
          "overlap_census_w19":
              len(census_formulas & set(w19_formulas)),
          "overlap_expected_zero": True}
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

    # ---- face 5: grammar-ledger text face (belt-and-braces scan source)
    with open(GRAMMAR_LEDGER, encoding="utf-8", errors="replace") as f:
        ledger_text = f.read()
    hits = [ln.strip()[:100] for ln in ledger_text.splitlines()
            if "alphagen" in ln.lower()]
    f5 = {"alphagen_rows": len(hits), "rows": hits,
          "note": "W19/W18/census consumed formulas are carried by the "
                  "census product + W19 result-file sources (draw-time "
                  "T-84s3); the ledger text scan stays belt-and-braces"}
    out["faces"]["grammar_ledger"] = f5

    # ---- face 6: chain head
    head = sg.ledger_head()
    f6 = {"chain_head": head,
          "expected": 877227,
          "matches_w19_closeout": head["total"] == 877227}
    out["faces"]["chain_head"] = f6

    # ---- face 7: W20 candidate band derive (read-only)
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
           if isinstance(v, (int, float)) and k not in OWN_W20}
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
    w19_keys = {k: int(sg.SEED_REGISTRY[k]) for k in sg.SEED_REGISTRY
                if isinstance(sg.SEED_REGISTRY[k], (int, float))
                and k.startswith("perpetual_n2_w19_")}
    w19_halo_top = max((v + HALO for v in w19_keys.values()), default=None)
    f7 = {"n1_bands_rows": len(rows), "max_wave": f"W{max_wave}",
          "a_head_end": a_head_end,
          "a_horizon": [horizon_lo, horizon_hi],
          "w19_registered_keys": w19_keys,
          "w19_family_halo_top": w19_halo_top,
          "naive_next_slot_after_w19":
              (max(w19_keys.values()) + 500) if w19_keys else None,
          "derive_forced_past_w19_halo": True,
          "reserved_intervals_n": len(reserved),
          "candidate_x_readonly": x,
          "candidate_trio": None if x is None else
          [[x, x + BAND_WIDTH], [x + 500, x + 500 + BAND_WIDTH],
           [x + 1_000, x + 1_000 + BAND_WIDTH]],
          "skipped_collision_xs": walk,
          "note": "draft-window readout only; freeze window re-derives "
                  "live and registers per R250 one-step law; DRAFT "
                  "writes NO band values (r702 lesson)"}
    out["faces"]["w20_band_derive"] = f7

    # ---- face 8: B-nulls arithmetic from the W19 empirical survival
    surv = f2["survival_frac_of_draws"]
    b_floor = MIN_POOLED / (W20_K * surv) if surv > 0 else float("inf")
    b_derived = math.ceil(b_floor) if surv > 0 else None
    envelope = None if b_derived is None else W20_K * (1 + b_derived)
    needed_ok = (math.ceil(MIN_POOLED / b_derived)
                 if b_derived else None)
    expected_pooled = (round(W20_K * surv * b_derived, 1)
                       if b_derived else None)
    fail_margin_ok = (round(W20_K * surv - needed_ok, 2)
                      if b_derived else None)
    surv_required = (round(MIN_POOLED / (W20_K * b_derived), 4)
                     if b_derived else None)
    b_next_envelope = (W20_K * (1 + b_derived + 1)
                       if b_derived else None)
    f8 = {"w20_k": W20_K, "b_derived": b_derived,
          "b_derivation": f"ceil({MIN_POOLED} / ({W20_K} * {surv}))",
          "b_only_feasible_under_cap": b_next_envelope is not None
          and b_next_envelope > ENVELOPE_CAP,
          "survival_required_for_b": surv_required,
          "survival_empirical_faces": {"census": 0.75,
                                       "w19": surv},
          "envelope_k_times_1plus_b": envelope,
          "envelope_cap": ENVELOPE_CAP,
          "envelope_within_cap": envelope is not None
                                 and envelope <= ENVELOPE_CAP,
          "needed_ok_formulas": needed_ok,
          "expected_ok": round(W20_K * surv, 2),
          "expected_pooled": expected_pooled,
          "margin_ok_formulas_above_needed": fail_margin_ok,
          "risk_disclosure": "dedup source grows by 51 W19-enrolled "
                             "formulas -> collision attrition may rise; "
                             "if pooled < 300 the runner refuses with a "
                             "full-decomposition receipt (W18/W19 law); "
                             "the LINE never moves",
          "sufficiency_line": MIN_POOLED,
          "line_note": "sufficiency line stays 300 (never re-derived "
                       "down: post-freeze adjustment prohibition face); "
                       "the BUDGET derives up instead; B=7 is the only "
                       "budget the 500 cap admits"}
    out["faces"]["b_nulls_arithmetic"] = f8

    # ---- face 9: prereg posture markers (DRAFT law: no band values)
    with open(W19_PREREG, encoding="utf-8") as f:
        w19_text = f.read()
    draft_exists = os.path.exists(W20_PREREG)
    if draft_exists:
        with open(W20_PREREG, encoding="utf-8") as f:
            w20_text = f.read()
        band_leak = [s for s in ("739,500", "739500", "740,000", "740000",
                                 "740,500", "740500")
                     if s in w20_text]
        f9 = {"w20_prereg_exists": True, "band_value_leak": band_leak,
              "frozen_marker_absent": "FROZEN" not in w20_text[:200],
              "w19_frozen_still_true":
                  "FROZEN" in w19_text[:400],
              "ok": not band_leak}
    else:
        f9 = {"w20_prereg_exists": False, "ok": False,
              "note": "prereg draft lands in this same round window "
                      "(slice-1); probe face recorded pre-write"}
    out["faces"]["prereg_posture"] = f9

    out["verdict"] = "FACTS_RECORDED"
    out["w20_design_summary"] = {
        "wave": "PERPETUAL-N2-W20 (replication wave)",
        "research_question": "does the W19 family readout (V1 HOLDS "
                             "0.38, D1 leverage 0.38 vs census 0.353) "
                             "replicate under an INDEPENDENT seed band",
        "k_draws": W20_K,
        "rounds": "R1=24->top6, R2=24 (top6 x 4)->top6, "
                  "R3=14 (r2_top[0..3] x 3 + r2_top[4..5] x 1)",
        "b_nulls_per_formula": b_derived,
        "envelope_trials": envelope,
        "sufficiency_line_pooled": MIN_POOLED,
        "dedup_source": "census 48 + W19 enrolled 51 + ledger text",
    }
    _dump(out)
    ok_all = (f8["envelope_within_cap"] and x is not None
              and f8["b_only_feasible_under_cap"])
    return 0 if ok_all else 2


def _dump(out):
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True, ensure_ascii=True)
    print(json.dumps({"verdict": out.get("verdict"),
                      "receipt": os.path.basename(OUT)}))


if __name__ == "__main__":
    sys.exit(main())
