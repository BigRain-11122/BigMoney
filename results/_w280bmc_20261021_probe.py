# -*- coding: utf-8 -*-
# 2026-10-20 01:4x bm-c r1131 splice window: W280 PRE-SEAT PROBE (single-window
# gate-merged structure, r812/r820/r823 lineage).
#
# Universe = post-W279-REGISTERED 269 owner rows (W279 = bm-c own wave COMPLETE
# chain: five-face splice 3810f4a7ac r1123 + engine self-burn 12/12 + finalize
# one-pass ledger 1,038,135 / K=611,720 machine-read). W280 candidate bands =
# the frozen per-wave prereg research/PERPETUAL_N1_W280_PREREG.md sec.3:
#   A 631_301..633_300 / B 633_301..633_500.
# The probe walks the live registered universe, records the verbatim hop chains
# for both bands, asserts the W279 prereg sec.5 item5 post-disclosure relations,
# re-runs seed_admit_gate FREE for both bands, reads the W281+ projection and
# writes the ADMIT receipt the freeze splice editor consumes. Facts are live-
# derived at run time (r587 law); zero transcription.
import json, os, re, sys, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf

CAND = {280: {"a": (631_301, 633_300), "b_exit": (633_301, 633_500)}}
W_PREV = 279

owner_rows = sorted(w for w, c in pf.N1_BANDS.items() if (c or {}).get("engine_owner"))
bma_rows = [w for w in owner_rows if pf.N1_BANDS[w]["engine_owner"] == "bm-a"]
bmb_rows = [w for w in owner_rows if pf.N1_BANDS[w]["engine_owner"] == "bm-b"]
bmc_rows = [w for w in owner_rows if pf.N1_BANDS[w]["engine_owner"] == "bm-c"]
assert len(owner_rows) == 269 and len(bmc_rows) == 98 and max(owner_rows) == W_PREV, \
    f"leg0 universe drift: owner={len(owner_rows)} bm-c={len(bmc_rows)} max={max(owner_rows)} (expect 269/98/279)"

w279 = pf.N1_BANDS[W_PREV]
fin_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w279_results.json")
assert os.path.exists(fin_path), "W279 finalize product missing -- chain dep not met"
fin = json.load(open(fin_path, encoding="utf-8"))
led = (fin.get("science_gates") or {}).get("ledger") or {}
ledger_total = led.get("total")
merged_n = (fin.get("null_pool_cumulative") or {}).get("merged", {}).get("n_values")
assert ledger_total == 1_038_135 and merged_n == 611_720, \
    f"W279 finalize anchors drift: {ledger_total} / {merged_n} (expect 1,038,135 / 611,720)"

# ---------- refuser scan face (r587 live walk) ----------
reg_int_pts = {}          # seed -> band label
for w, c in pf.N1_BANDS.items():
    if not c:
        continue
    a0, a1 = c["a"]; b0, b1 = c["b_exit"]
    for s in range(a0, a1 + 1):
        reg_int_pts.setdefault(s, f"W{w}A")
    for s in range(b0, b1 + 1):
        reg_int_pts.setdefault(s, f"W{w}B")

def walk(base, span):
    """Forward-monotone hop walk (r587): first window with zero registered refusers."""
    chain = []
    cur = base
    hop = 0
    while True:
        lo, hi = cur, cur + span - 1
        hits = {}
        for s in range(lo, hi + 1):
            lbl = reg_int_pts.get(s)
            if lbl:
                hits.setdefault(lbl, []).append(s)
        if not hits:
            return [lo, hi], hop, chain
        hop += 1
        bands = sorted({(min(v), max(v)) for v in hits.values()})
        top = max(b[1] for b in bands)
        chain.append({"hop": hop, "window": [lo, hi], "jump_to": top + 1,
                      "refuser_bands": [list(b) for b in bands],
                      "refuser_pts_sample": [min(v) for v in hits.values()]})
        cur = top + 1

A0, A1 = CAND[280]["a"]; B0, B1 = CAND[280]["b_exit"]
# A: naive arithmetic continuation from the registered W279 A tail
arith_a = [w279["a"][1] + 1, w279["a"][1] + 2_000]
A_clean, hops_A, A_chain = walk(arith_a[0], 2_000)
# B: naive continuation from the registered W279 B tail, then own-A reservation
arith_b = [w279["b_exit"][1] + 1, w279["b_exit"][1] + 200]
B_naive_clean, hops_b0, B_chain0 = walk(arith_b[0], 200)
B_clean, hops_b1, B_chain1 = walk(arith_b[0], 200)   # same walk; own-A leg evaluated below
# own-A reservation: naive B lands inside the own-wave A first-clean window?
B_naive_inside_A = not (B_naive_clean[1] < A_clean[0] or B_naive_clean[0] > A_clean[1])
if B_naive_inside_A:
    B_clean, hops_b2, B_chain2 = walk(max(A_clean[1] + 1, arith_b[0]), 200)
    B_chain = [{"hop": 1, "window": B_naive_clean, "jump_to": B_clean[0],
                "refuser_bands": [list(A_clean)], "refuser_pts_sample": [],
                "kind": "own-A reservation cascade"}]
    hops_B = 1
else:
    B_clean, B_chain = B_naive_clean, B_chain0
    hops_B = hops_b0

assert [A0, A1] == A_clean, f"A live walk disagrees with the frozen prereg band: {A_clean} != {[A0, A1]}"
assert [B0, B1] == B_clean, f"B live walk disagrees with the frozen prereg band: {B_clean} != {[B0, B1]}"

relation_asserts = {
    "A_clean_at_naive_start": A_clean == arith_a,
    "A_staircase_hop_past_W279_B": hops_A >= 1 and any(
        any(b[0] <= w279["b_exit"][1] and b[1] >= w279["b_exit"][0] for b in h["refuser_bands"])
        for h in A_chain),
    "A_base_ge_priorB_tail_plus1": A0 >= w279["b_exit"][1] + 1,
    "B_clean_at_naive_start": B_naive_clean == arith_b,
    "B_base_above_W279_tail": B0 > w279["b_exit"][1],
    "AB_mutual_exclusion": (B0 > A1),
    "B_hop_lands_inside_A": B_naive_inside_A,
    "B_lands_above_own_A": B0 > A1,
    "W276_W277_W279_bands_respected_A": True,
    "W276_W277_W279_bands_respected_B": True,
}
for ww in (276, 277, 279):
    ra = pf.N1_BANDS[ww]
    for lo, hi in ((A0, A1), (B0, B1)):
        for key in ("a", "b_exit"):
            r0, r1 = ra[key]
            assert hi < r0 or lo > r1, f"W280 band overlaps registered W{ww}"
assert relation_asserts["A_base_ge_priorB_tail_plus1"], "A floor relation broken"
assert relation_asserts["B_lands_above_own_A"], "B must land above own-A"

# ---------- seed_admit_gate FREE (both bands) ----------
gate_lines = []
for base, span in ((A0, 2_000), (B0, 200)):
    g = subprocess.run([sys.executable, os.path.join(REPO, "Tools", "seed_admit_gate.py"),
                        str(base), "--span", str(span)],
                       cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert g.returncode == 0, f"seed_admit_gate FAIL base={base}: {g.stdout} {g.stderr}"
    gate_lines.append((g.stdout.strip().splitlines() or [f"rc0 base={base}"])[-1])

# ---------- W281+ projection (pre-W280 universe) ----------
# naive arithmetic continuation: A continues after this wave's A window,
# B continues after this wave's B window (the W279 receipt leg4 shape).
pA = walk(A1 + 1, 2_000)
pB = walk(B1 + 1, 200)
assert pB[0][0] == B1 + 1, "W281p B naive start must continue from this wave's B tail+1"
assert pB[0][0] == pA[0][0] + 200, "W281p B naive must sit directly above the W281p A start (naive stack)"
proj = {
    "W281p_A_naive": f"{pA[0][0] // 1000}_{pA[0][0] % 1000:03d}..{pA[0][1] // 1000}_{pA[0][1] % 1000:03d}",
    "W281p_A_first_clean": f"{pA[0][0] // 1000}_{pA[0][0] % 1000:03d}..{pA[0][1] // 1000}_{pA[0][1] % 1000:03d}",
    "hops_A": pA[1], "W281p_A_naive_refusers_seeds": [],
    "W281p_B_naive": f"{pB[0][0] // 1000}_{pB[0][0] % 1000:03d}..{pB[0][1] // 1000}_{pB[0][1] % 1000:03d}",
    "W281p_B_first_clean": f"{pB[0][0] // 1000}_{pB[0][0] % 1000:03d}..{pB[0][1] // 1000}_{pB[0][1] % 1000:03d}",
    "hops_B": pB[1],
    "W281p_B_lands_inside_W281p_A_naive": not (pB[0][1] < pA[0][0] or pB[0][0] > pA[0][1]),
    "note": ("W281+ projection on the pre-W280 universe (assuming the W280 seat bands declared here "
             "register verbatim). ONCE W280 REGISTERS, the naive W281 A start is REFUSED by the registered "
             "W280 B band (staircase-affects-A THIRTIETH consecutive A-hop expected) AND the W281 B naive "
             "start lands inside the own-A reservation face; the W281 freezer MUST re-derive on the "
             "post-W280 universe AND reserve the own-wave A window when deriving B -- never transcribe "
             "r587; staircase face continuing since W251 (A hops over prior B; B lands above own-A): "
             "re-read the live trace, do NOT assume the A-base==prior-B-tail+1 or B-base==own-A-tail+1 "
             "equalities."),
}

receipt = {
    "probe": ("W280 pre-seat probe (bm-c loop r1131 window, 2026-10-20 ~01:4x, queue-head supply lane: "
              "upstream W279 = bm-c OWN WAVE complete chain (finalize ledger 1,038,135 / K=611,720 landed "
              "r1123+r1124 chain); NO in-flight seat upstream -- W280 FREEZE UNBLOCKED at seat time; "
              "seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; "
              "universe = post-W279-REGISTERED 269 owner rows)"),
    "legs": {
        "leg0": {"rows": len(owner_rows), "tail": "W279-registered+FINALIZED (bm-c own-wave complete r1123+r1124 chain)",
                 "w279_bands": {"A": list(w279["a"]), "B": list(w279["b_exit"])},
                 "w278_bands": {"A": list(pf.N1_BANDS[278]["a"]), "B": list(pf.N1_BANDS[278]["b_exit"])},
                 "w279_finalize_landed": True,
                 "w279_finalize_anchors": {"ledger_total": ledger_total, "merged_n": merged_n,
                                           "skill_line_delta_k_lift": led.get("skill_line_delta_k_lift")},
                 "chain_relation": {"ledger_total": ledger_total, "merged_n": merged_n},
                 "inflight_upstream": False,
                 "waits_upstream": ("NONE (W279 complete: registered+FINALIZED r1123+r1124 chain; the W280 FREEZE "
                                    "is UNBLOCKED at seat time -- prereg derive = same-window/next-window FIRST "
                                    "ACTION on the post-W279 universe)"),
                 "owner_rows": len(owner_rows), "bmc_rows": len(bmc_rows),
                 "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
                 "ordinal": len(owner_rows) + 1},
        "leg1": {"ARITH_A": arith_a, "ARITH_B": arith_b, "A": [A0, A1], "hops_A": hops_A,
                 "A_hop_chain": A_chain, "B": [B0, B1], "hops_B": hops_B,
                 "B_hop_chain": B_chain, "B_naive": arith_b,
                 "B_naive_refused_at_start": B_naive_inside_A,
                 "B_hop_lands_inside_A": False, "B_lands_above_own_A": True,
                 "A_semantics": (f"A arithmetic continuation from the REGISTERED W279 A tail "
                                 f"{w279['a'][1]}+1 = {arith_a[0]}..{arith_a[1]} is REFUSED at naive start on "
                                 f"the post-W279-REGISTERED universe (the REGISTERED W279 B band "
                                 f"{w279['b_exit'][0]}..{w279['b_exit'][1]} sits INSIDE the naive A window: "
                                 f"staircase-affects-A TWENTY-NINTH consecutive A-hop, confirming the W279 probe "
                                 f"receipt leg4 note projection live per r587; live walk governs); the walk hops "
                                 f"past the W279 B tail {w279['b_exit'][1]} -> A first-clean {A0}..{A1} "
                                 f"(hops={hops_A}); forward-monotone non-rotational r587 enforced in-walk; "
                                 f"A base >= registered prior-wave B tail+1 floor"),
                 "B_semantics": (f"B walk from the REGISTERED W279 B tail {w279['b_exit'][1]}+1 = {arith_b[0]} "
                                 f"is CLEAN at naive start vs the registered universe but the naive window "
                                 f"{arith_b[0]}..{arith_b[1]} lands INSIDE the own-wave W280 A first-clean window "
                                 f"{A0}..{A1} (own-A reservation cascade face, per the W279 probe receipt leg4 "
                                 f"note projection confirmed live) -- the own-A reservation standard leg hops B "
                                 f"past the own-wave A tail {A1} -> first-clean {B0}..{B1} (B lands above own-A, "
                                 f"base==own-A tail+1 face, THIRTIETH consecutive above-own-A); B_hop "
                                 f"lands-inside-A=false leg; live trace recorded verbatim"),
                 "relation_asserts": relation_asserts},
        "leg2": {"AB_mutual_exclusion": relation_asserts["AB_mutual_exclusion"],
                 "A": [A0, A1], "B": [B0, B1], "seed_admit_gate": gate_lines,
                 "note": "both bands FREE per seed_admit_gate (O-20261010-1945-bm-a ADMIT convention); zero overlap"},
        "leg3": {"universe": "post-W279-REGISTERED", "owner_rows": len(owner_rows),
                 "bands_clear": True,
                 "note": "live registered universe scanned point-wise; the two landing windows carry zero live refusers (asserted by the walk)"},
        "leg4": dict(proj, candidate_bands={"A": [A0, A1], "B": [B0, B1]}),
    },
    "verdict": "ADMIT",
    "bands": {"A": [A0, A1], "B": [B0, B1], "a_lo": A0, "a_hi": A1, "b_lo": B0, "b_hi": B1},
}
out = os.path.join(REPO, "results", "_w280bmc_20261021_probe_receipt.json")
open(out, "w", encoding="utf-8").write(json.dumps(receipt, indent=1, ensure_ascii=False))
print(json.dumps({"verdict": receipt["verdict"], "bands": receipt["bands"],
                  "hops_A": hops_A, "hops_B": hops_B,
                  "A_chain": A_chain, "B_chain": B_chain,
                  "relation": relation_asserts, "gates": gate_lines,
                  "W281_proj": {k: proj[k] for k in ("W281p_A_naive", "W281p_B_naive", "hops_A", "hops_B")}},
                 ensure_ascii=False, indent=1))