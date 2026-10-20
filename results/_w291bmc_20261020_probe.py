# -*- coding: utf-8 -*-
"""W291 PRE-SEAT PROBE (bm-c loop window r1166, 2026-10-20 ~18:1x).

Universe = post-W290-REGISTERED 280 owner rows (W290 = bm-c own wave COMPLETE
chain: seat probe ADMIT r1166 + prereg freeze r1164 + five-face splice
cef6e85f5d + engine self-burn 12/12 + sixgate 53rd PRE-FINALIZE ALL PASS +
finalize EXACT ledger 1,062,341 / merged K=635,920 + fivekeys 6/6 r1165;
sec.7/8 backfill absorbed r1165).

W291 = 281st wave, bm-c 110th own wave candidate. Bands are DERIVED HERE from
the live registered universe (r587 live-walk law; zero transcription): the
staircase face (A hops past the prior wave's B band; B reserves the own-wave A
window) has been continuing since W251, so the seat declares the walk result and
the W291 prereg freezes to it -- never the other way round.
"""
import json, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf

W_PREV = 290
WIDTH_A = 2_000
WIDTH_B = 200

owner_rows = sorted(w for w, c in pf.N1_BANDS.items() if (c or {}).get("engine_owner"))
bma_rows = [w for w in owner_rows if pf.N1_BANDS[w]["engine_owner"] == "bm-a"]
bmb_rows = [w for w in owner_rows if pf.N1_BANDS[w]["engine_owner"] == "bm-b"]
bmc_rows = [w for w in owner_rows if pf.N1_BANDS[w]["engine_owner"] == "bm-c"]
assert len(owner_rows) == 280 and len(bmc_rows) == 109 and max(owner_rows) == W_PREV, \
    f"leg0 universe drift: owner={len(owner_rows)} bm-c={len(bmc_rows)} max={max(owner_rows)} (expect 280/109/290)"

wprev = pf.N1_BANDS[W_PREV]
fin_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w290_results.json")
assert os.path.exists(fin_path), "W290 finalize product missing -- chain dep not met"
fin = json.load(open(fin_path, encoding="utf-8"))
led = (fin.get("science_gates") or {}).get("ledger") or {}
ledger_total = led.get("total")
merged_n = (fin.get("null_pool_cumulative") or {}).get("merged", {}).get("n_values")
assert ledger_total == 1_062_341 and merged_n == 635_920, \
    f"W290 finalize anchors drift: {ledger_total} / {merged_n} (expect 1,062,341 / 635,920)"

# ---------- registered refuser point map (live walk) ----------
reg_int_pts = {}
for w, c in pf.N1_BANDS.items():
    if not c:
        continue
    a0, a1 = c["a"]
    b0, b1 = c["b_exit"]
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


# A: arithmetic continuation from the registered W290 A tail, then hop
arith_a = [wprev["a"][1] + 1, wprev["a"][1] + WIDTH_A]
A_clean, hops_A, A_chain = walk(arith_a[0], WIDTH_A)
# B: arithmetic continuation from the registered W290 B tail, then own-A reservation
arith_b = [wprev["b_exit"][1] + 1, wprev["b_exit"][1] + WIDTH_B]
B_naive_clean, hops_b0, B_chain0 = walk(arith_b[0], WIDTH_B)
B_naive_inside_A = not (B_naive_clean[1] < A_clean[0] or B_naive_clean[0] > A_clean[1])
if B_naive_inside_A:
    B_clean, hops_b2, B_chain2 = walk(max(A_clean[1] + 1, arith_b[0]), WIDTH_B)
    B_chain = [{"hop": 1, "window": B_naive_clean, "jump_to": B_clean[0],
                "refuser_bands": [list(A_clean)], "refuser_pts_sample": [],
                "kind": "own-A reservation cascade"}]
    hops_B = 1
else:
    B_clean, B_chain = B_naive_clean, B_chain0
    hops_B = hops_b0

A0, A1 = A_clean
B0, B1 = B_clean

# ---------- relation asserts (staircase face, fail-closed) ----------
relation_asserts = {
    "A_staircase_hop_past_registered_W290_B": hops_A >= 1 and any(
        any(b[0] <= wprev["b_exit"][1] and b[1] >= wprev["b_exit"][0] for b in h["refuser_bands"])
        for h in A_chain),
    "A_base_ge_priorB_tail_plus1": A0 >= wprev["b_exit"][1] + 1,
    "B_naive_clean_vs_registered": B_naive_clean == arith_b,
    "B_hop_lands_inside_A": B_naive_inside_A,
    "B_lands_above_own_A": B0 > A1,
    "AB_mutual_exclusion": B0 > A1,
    "B_base_eq_own_A_tail_plus1": B0 == A1 + 1,
}
assert relation_asserts["A_base_ge_priorB_tail_plus1"], "A floor relation broken"
assert relation_asserts["B_lands_above_own_A"], "B must land above own-A"
assert relation_asserts["B_base_eq_own_A_tail_plus1"], "own-A reservation floor broken"

# bands must be clear of every registered wave (walk already guarantees this)
for w, c in pf.N1_BANDS.items():
    if not c:
        continue
    for lo, hi in ((A0, A1), (B0, B1)):
        for key in ("a", "b_exit"):
            r0, r1 = c[key]
            assert hi < r0 or lo > r1, f"W291 band overlaps registered W{w}"

# ---------- seed_admit_gate FREE (both bands) ----------
gate_lines = []
for base, span in ((A0, WIDTH_A), (B0, WIDTH_B)):
    g = subprocess.run([sys.executable, os.path.join(REPO, "Tools", "seed_admit_gate.py"),
                        str(base), "--span", str(span)],
                       cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert g.returncode == 0, f"seed_admit_gate FAIL base={base}: {g.stdout} {g.stderr}"
    gate_lines.append((g.stdout.strip().splitlines() or [f"rc0 base={base}"])[-1])

# ---------- W292+ projection (pre-W292 universe) ----------
pA = walk(A1 + 1, WIDTH_A)
pB = walk(B1 + 1, WIDTH_B)


def fmt(b):
    return f"{b[0] // 1000}_{b[0] % 1000:03d}..{b[1] // 1000}_{b[1] % 1000:03d}"


proj = {
    "W292p_A_naive": fmt(pA[0]), "W292p_A_first_clean": fmt(pA[0]), "hops_A": pA[1],
    "W292p_B_naive": fmt(pB[0]), "W292p_B_first_clean": fmt(pB[0]), "hops_B": pB[1],
    "W292p_B_lands_inside_W292p_A_naive": not (pB[0][1] < pA[0][0] or pB[0][0] > pA[0][1]),
    "note": ("W292+ projection on the pre-W292 universe (assuming the W291 seat bands declared here register "
             "verbatim). ONCE W291 REGISTERS, the naive W292 A start is REFUSED by the registered W291 B band "
             "(staircase-affects-A next consecutive A-hop expected) AND the W292 B naive start lands inside the "
             "own-A reservation face; the W292 freezer MUST re-derive on the post-W291 universe AND reserve the "
             "own-wave A window when deriving B -- never transcribe r587."),
}

receipt = {
    "probe": ("W291 pre-seat probe (bm-c loop r1166 window, 2026-10-20 ~18:1x, queue-head supply lane: "
              "upstream W290 = bm-c OWN WAVE complete chain (finalize ledger 1,062,341 / K=635,920 landed "
              "r1165); NO in-flight seat upstream -- W291 FREEZE UNBLOCKED at seat time; "
              "seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; "
              "universe = post-W290-REGISTERED 280 owner rows)"),
    "legs": {
        "leg0": {"rows": len(owner_rows),
                 "tail": "W290-registered+FINALIZED (bm-c own-wave complete r1165 chain)",
                 "wprev_bands": {"A": list(wprev["a"]), "B": list(wprev["b_exit"])},
                 "wprev_minus1_bands": {"A": list(pf.N1_BANDS[W_PREV - 1]["a"]), "B": list(pf.N1_BANDS[W_PREV - 1]["b_exit"])},
                 "wprev_finalize_landed": True,
                 "wprev_finalize_anchors": {"ledger_total": ledger_total, "merged_n": merged_n,
                                           "skill_line_delta_k_lift": led.get("skill_line_delta_k_lift")},
                 "inflight_upstream": False,
                 "waits_upstream": ("NONE (W290 complete: registered+FINALIZED r1165 chain; the W291 "
                                    "FREEZE is UNBLOCKED at seat time -- prereg derive = next-window FIRST ACTION "
                                    "on the post-W290 universe)"),
                 "owner_rows": len(owner_rows), "bmc_rows": len(bmc_rows),
                 "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
                 "ordinal": len(owner_rows) + 1},
        "leg1": {"ARITH_A": arith_a, "ARITH_B": arith_b, "A": [A0, A1], "hops_A": hops_A,
                 "A_hop_chain": A_chain, "B": [B0, B1], "hops_B": hops_B,
                 "B_hop_chain": B_chain, "B_naive": arith_b,
                 "B_naive_refused_at_start": B_naive_inside_A,
                 "B_lands_above_own_A": True,
                 "A_semantics": (f"A arithmetic continuation from the REGISTERED W290 A tail "
                                 f"{wprev['a'][1]}+1 = {arith_a[0]}..{arith_a[1]} is REFUSED at naive start "
                                 f"(the REGISTERED W290 B band {wprev['b_exit'][0]}..{wprev['b_exit'][1]} sits "
                                 f"INSIDE the naive A window: staircase-affects-A next consecutive A-hop); the "
                                 f"walk hops past the W290 B tail {wprev['b_exit'][1]} -> A first-clean "
                                 f"{A0}..{A1} (hops={hops_A}); forward-monotone non-rotational r587"),
                 "B_semantics": (f"B walk from the REGISTERED W290 B tail {wprev['b_exit'][1]}+1 = {arith_b[0]} "
                                 f"is CLEAN at naive start vs the registered universe but the naive window "
                                 f"{arith_b[0]}..{arith_b[1]} lands INSIDE the own-wave W291 A first-clean "
                                 f"window {A0}..{A1} (own-A reservation cascade) -- B hops past the own-wave A "
                                 f"tail {A1} -> first-clean {B0}..{B1} (base==own-A tail+1); live trace verbatim"),
                 "relation_asserts": relation_asserts},
        "leg2": {"AB_mutual_exclusion": relation_asserts["AB_mutual_exclusion"],
                 "A": [A0, A1], "B": [B0, B1], "seed_admit_gate": gate_lines,
                 "note": "both bands FREE per seed_admit_gate (O-20261010-1945-bm-a ADMIT convention); zero overlap"},
        "leg3": {"universe": "post-W290-REGISTERED", "owner_rows": len(owner_rows),
                 "bands_clear": True,
                 "note": "live registered universe scanned point-wise; both landing windows carry zero refusers"},
        "leg4": dict(proj, candidate_bands={"A": [A0, A1], "B": [B0, B1]}),
    },
    "verdict": "ADMIT",
    "bands": {"A": [A0, A1], "B": [B0, B1], "a_lo": A0, "a_hi": A1, "b_lo": B0, "b_hi": B1},
}
out = os.path.join(REPO, "results", "_w291bmc_20261020_probe_receipt.json")
open(out, "w", encoding="utf-8").write(json.dumps(receipt, indent=1, ensure_ascii=False))
print(json.dumps({"verdict": receipt["verdict"], "bands": receipt["bands"],
                  "hops_A": hops_A, "hops_B": hops_B,
                  "A_chain": A_chain, "B_chain": B_chain,
                  "relation": relation_asserts, "gates": gate_lines,
                  "W292_proj": {k: proj[k] for k in ("W292p_A_naive", "W292p_B_naive", "hops_A", "hops_B")}},
                 ensure_ascii=False, indent=1))