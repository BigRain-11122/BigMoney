# -*- coding: utf-8 -*-
"""W262 pre-seat probe (bm-c loop window r1067, 2026-10-17 14:xx; queue-head
supply lane: upstream W261 = bm-c OWN registered+FINALIZED complete chain
(seat MSG-20261017-1225 origin cf23c4553 -> prereg r1066 LANDED 03ab504d7
(banned gate ADMIT rc0 at freeze) -> r1067 five-face freeze splice 68aad04b6
(zero post-splice heal; sixgate splice-integrity gate-1 n1 TRIPLE identity
worktree==receipt post==LANDED git blob 6df7875e7f9312cc / pf
34a5a2c68a20e3e4 git-diff-empty face) -> engine self-burn 12/12 (ledger
appends ad2aa9322+b88dc8fcd batched 6+5 self-commit) -> r1067
57th-gen absorb-continuation finalize: ledger 998,535 EXACT (996,335+2,200)
/ merged pool K=572,120 (569,920+2,200) / fivekeys ALL PASS
results/_r1067bmc_w261_fivekeys.json / sixgate PRE-FINALIZE ALL PASS
results/_r1067bmc_w261_sixgate.json 23rd consecutive correct-phase)
-- NO in-flight seat upstream: the W262 FREEZE is UNBLOCKED at seat time.
Universe face = post-W261-REGISTERED (live registry, 251 owner rows: bm-a 129
/ bm-b 41 / bm-c 81 incl W261; W262 candidate = 252nd wave). STAIRCASE
CONTINUATION face (W261 probe leg4 + prereg sec.5 item5 both projected; live
re-derive governs r587): naive W262 A continuation 591_501..593_500 is
REFUSED at the REGISTERED W261 B band 591_501..591_700 -> A hops past 591_700
to first-clean 591_701..593_700 (ELEVENTH consecutive A-hop expected); naive B
591_701..591_900 is CLEAN at naive BUT lands INSIDE the own-wave A
first-clean window -> own-A reservation hops B past 593_700 to 593_701..593_900
(TWELFTH consecutive above-own-A expected; B base==own-A tail+1 floor).
Bloodline: _w261bmc_20261017_probe.py derive machinery verbatim
(walk/gates/constants), W262 facts live-registry-driven, compact re-authoring
this window per r971 large-task honest-split law; live walk governs, never
transcribed r587."""
import subprocess
import sys, os, json
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000
WIDTH_A = 2_000
WIDTH_B = 200

N3R1_USED = (71_000, 71_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
CROSSFACE_PROBE_POINTS = (95_004, 95_006)
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
receipt = {"probe": "W262 pre-seat probe (bm-c loop r1067 window, 2026-10-17 14:xx, queue-head supply lane: upstream W261 = bm-c OWN registered+FINALIZED complete chain (r1067 57th-gen absorb-continuation finalize ledger 998,535 / K=572,120); NO in-flight seat upstream -- W262 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; universe = post-W261-REGISTERED 251 owner rows)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W259..W261 landed faces + chain-relation anchors ---
keys = sorted(N1_BANDS)
w261_splice_landed = 261 in N1_BANDS
assert w261_splice_landed, "leg0 failed: W261 splice not landed (registry row absent -- r1067 splice face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 262))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert 262 not in N1_BANDS, "leg0 failed: W262 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W262 universe honestly, do not seat on a stale universe)"

W259_A = tuple(N1_BANDS[259]["a"])
W259_B = tuple(N1_BANDS[259]["b_exit"])
assert W259_A == (585_101, 587_100) and W259_B == (587_101, 587_300) and \
    N1_BANDS[259].get("engine_owner") == "bm-c", "leg0 failed: W259 registry row drift (bm-c r1064 splice face)"

W260_A = tuple(N1_BANDS[260]["a"])
W260_B = tuple(N1_BANDS[260]["b_exit"])
assert W260_A == (587_301, 589_300) and W260_B == (589_301, 589_500) and \
    N1_BANDS[260].get("engine_owner") == "bm-c", "leg0 failed: W260 registry row drift (bm-c r1065 splice face)"

W261_A = tuple(N1_BANDS[261]["a"])
W261_B = tuple(N1_BANDS[261]["b_exit"])
assert W261_A == (589_501, 591_500) and W261_B == (591_501, 591_700) and \
    N1_BANDS[261].get("engine_owner") == "bm-c", "leg0 failed: W261 registry row drift (bm-c r1067 splice face)"
assert W261_A[0] == W260_B[1] + 1, \
    "leg0 failed: W261 A base != W260 B tail+1 (staircase-affects-A tenth consecutive hop face drift)"
assert W261_B[0] == W261_A[1] + 1, \
    "leg0 failed: W261 B base != own-A tail+1 (above-own-A eleventh consecutive face drift)"

for _w in (259, 260, 261):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

w260_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w260_results.json"), encoding="utf-8"))
w260_led = (w260_out.get("science_gates") or {}).get("ledger") or {}
w260_total = w260_led.get("total")
w260_merged_n = w260_out["null_pool_cumulative"]["merged"]["n_values"]

w261_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w261_results.json"), encoding="utf-8"))
w261_led = (w261_out.get("science_gates") or {}).get("ledger") or {}
w261_total = w261_led.get("total")
w261_merged_n = w261_out["null_pool_cumulative"]["merged"]["n_values"]
w261_klift = w261_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
assert w260_total == 996_335 and w260_merged_n == 569_920, \
    f"leg0 failed: W260 finalize anchors drift: total={w260_total} merged={w260_merged_n} (expect 996,335 / 569,920)"
assert w261_total == 998_535 and w261_merged_n == 572_120, \
    f"leg0 failed: W261 finalize anchors drift: total={w261_total} merged={w261_merged_n} (expect 998,535 / 572,120)"
assert w261_total == w260_total + 2_200 and w261_merged_n == w260_merged_n + 2_200, \
    "leg0 failed: W260->W261 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w261_klift is not None and abs(w261_klift) <= 0.02, \
    f"leg0 failed: W261 K-lift out-of-band at seat time: {w261_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 251 and len(bmc_rows) == 81, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 251/81 post-W261-splice, W262 unregistered)"
ordinal = owner_total + 1
assert ordinal == 252, f"leg0 ordinal derive: {ordinal} != 252"
assert len(bma_rows) == 129, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 129 post-W261-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

# --- leg 0.5: no-skip-claim leg (seat numbering density) + chain-complete face --
out_inbox = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
all_inbox = out_inbox.splitlines()
w262_seats_pre = [ln for ln in all_inbox if "w262" in ln.lower() and "seat" in ln.lower()]
assert w262_seats_pre == [], f"leg0.5 failed: W262 seat already claimed on origin: {w262_seats_pre} (vacancy broken -- yield per fleet README sec.4)"
skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w263", "w264")) and "seat" in ln.lower()]
assert skip_claims == [], f"leg0.5 failed: skip-ahead seat claims exist (W262/W263 numbering density violated): {skip_claims}"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W261-registered+FINALIZED (bm-c own-wave complete)",
    "w261_bands": {"A": list(W261_A), "B": list(W261_B)},
    "w260_bands": {"A": list(W260_A), "B": list(W260_B)},
    "w261_finalize_landed": True,
    "w261_finalize_anchors": {"ledger_total": w261_total, "merged_n": w261_merged_n,
                                "skill_line_delta_k_lift": w261_klift},
    "chain_relation": {"w260_total": w260_total, "w261_total": w261_total,
                       "ledger_delta": w261_total - w260_total,
                       "k_delta": w261_merged_n - w260_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W261 complete: registered+FINALIZED; the W262 FREEZE is UNBLOCKED at seat time -- prereg derive = next window FIRST ACTION on the post-W261 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal,
}
print(f"leg0: {len(N1_BANDS)} rows tail=W261-registered+FINALIZED (bm-c own-wave complete, W262 unregistered), W261 face=registry A={W261_A} B={W261_B}, chain-relation W260->W261 ledger 996,335->998,535 (+2,200) K 569,920->572,120 (+2,200) OK, owner={owner_total} -> W262=252nd wave candidate")
print("leg0.5: no W262 seat claim on origin (vacancy held) + zero skip-ahead W263/W264 seat claims (numbering density green) + waits-upstream=NONE (W262 freeze UNBLOCKED)")

# --- W262 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox2 = r_vac.stdout.decode("utf-8").splitlines()
w262_seats = [ln for ln in all_inbox2 if "w262" in ln.lower() and "seat" in ln.lower()]
assert w262_seats == [], f"vacancy failed: W262 seats already exist: {w262_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '262: {"a": (' not in out_pf, "vacancy failed: W262 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W262"' not in outn1_vac, "vacancy failed: W262 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W262_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W262 per-wave prereg ALREADY on origin"
print("vacancy: W262 origin vacancy held (no seat / row / configs / prereg)")

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS)
points |= set(PROBE_SEEDS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: honest forward walk from the W261 REGISTERED tails ------------------
ARITH_A = (W261_A[1] + 1, W261_A[1] + WIDTH_A)
ARITH_B = (W261_B[1] + 1, W261_B[1] + WIDTH_B)


def first_clean(lo, width, trace=None, extra_bands=()):
    hops = 0
    prev_lo = lo
    while True:
        hi = lo + width - 1
        bad_pts = [p for p in points if lo <= p <= hi]
        bad_bands = [b for b in list(bands) + list(extra_bands) + actual
                     if overlaps((lo, hi), b)]
        if not bad_pts and not bad_bands:
            return (lo, hi), hops
        jump = max([p + 1 for p in bad_pts] + [b[1] + 1 for b in bad_bands])
        assert jump > prev_lo, f"non-rotational violation: jump {jump} <= {prev_lo}"
        if trace is not None:
            trace.append({"hop": hops + 1, "window": [lo, hi], "jump_to": jump,
                          "refuser_pts": sorted(bad_pts),
                          "refuser_bands": [list(b) for b in bad_bands]})
        lo = jump
        prev_lo = lo
        hops += 1


a_trace = []
(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A, trace=a_trace)
# own-wave A reservation for B (standard leg): B walk reserves the own-A window
b_trace_own = []
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace_own,
                             extra_bands=(fc_a,))
assert fc_a == (591_701, 593_700) and hops_a == 1, ("leg1 A staircase face: live walk refused "
                                "the naive start 591_501..593_500 at the REGISTERED W261 B band "
                                "591_501..591_700 (staircase-affects-A ELEVENTH consecutive hop; "
                                "the W261 prereg sec.5 item5 pre-W261-universe projection was "
                                "superseded live per r587; if this fires the universe changed "
                                "again: re-read the live trace honestly)")
assert not overlaps(fc_a, W259_A) and not overlaps(fc_a, W259_B), \
    "leg1 failed: A overlaps prior-wave W259 registered bands"
assert not overlaps(fc_a, W260_A) and not overlaps(fc_a, W260_B), \
    "leg1 failed: A overlaps prior-wave W260 registered bands"
assert not overlaps(fc_a, W261_A) and not overlaps(fc_a, W261_B), \
    "leg1 failed: A overlaps prior-wave W261 registered bands"
assert fc_a[0] >= W261_B[1] + 1, \
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
# B honest face: naive start 591_701..591_900 CLEAN at naive BUT lands INSIDE the own-wave
# W262 A first-clean window 591_701..593_700 (own-A reservation face, cascade per the W261
# probe leg4 + prereg sec.5 item5 projections, superseded live per r587); walk governs.
assert fc_b[0] > ARITH_B[0] or hops_b == 0, \
    "leg1 B walk non-rotational/governance violation"
assert fc_b[0] > W261_B[1], \
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W259_A) and not overlaps(fc_b, W259_B), \
    "leg1 failed: B overlaps prior-wave W259 registered bands"
assert not overlaps(fc_b, W260_A) and not overlaps(fc_b, W260_B), \
    "leg1 failed: B overlaps prior-wave W260 registered bands"
assert not overlaps(fc_b, W261_A) and not overlaps(fc_b, W261_B), \
    "leg1 failed: B overlaps prior-wave W261 registered bands"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace_own,
    "B_naive": list(ARITH_B), "B_naive_refused_at_start": fc_b[0] != ARITH_B[0] or hops_b > 0,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "B_lands_above_own_A": fc_b[0] > fc_a[1],
    "A_semantics": ("A arithmetic continuation from the REGISTERED W261 A tail "
                    "591_500+1 = 591_501..593_500 is REFUSED at naive start on the "
                    "post-W261-REGISTERED universe (the REGISTERED W261 B band "
                    "591_501..591_700 sits INSIDE the naive A window: staircase-"
                    "affects-A ELEVENTH consecutive A-hop, superseding the W261 prereg "
                    "sec.5 item5 pre-W261-universe projection per r587); the walk hops "
                    "past the W261 B tail 591_700 -> A first-clean 591_701..593_700 "
                    "(hops=1); forward-monotone non-rotational r587 enforced in-walk; "
                    "A base >= registered prior-wave B tail+1 floor"),
    "B_semantics": ("B walk from the REGISTERED W261 B tail 591_700+1 = 591_701 is "
                    "CLEAN at naive start but the naive window 591_701..591_900 lands "
                    "INSIDE the own-wave W262 A first-clean window 591_701..593_700 "
                    "(own-A reservation cascade face, per the W261 probe leg4 + "
                    "prereg sec.5 item5 projection faces superseded live) -- the "
                    "own-A reservation standard leg hops B past the own-wave A tail "
                    "593_700 -> first-clean 593_701..593_900 (B lands above own-A, "
                    "base==own-A tail+1 face, TWELFTH consecutive above-own-A); "
                    "B_hop lands-inside-A=false leg; live trace recorded verbatim"),
    "relation_asserts": {"A_clean_at_naive_start": False,
                          "A_staircase_hop_past_W261_B": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": fc_b[0] == ARITH_B[0] and hops_b == 0,
                          "B_base_above_W261_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "B_lands_above_own_A": True,
                          "W259_W260_W261_bands_respected_A": True,
                          "W259_W260_W261_bands_respected_B": True}}
print(f"leg1: A {fc_a} hops={hops_a} (hop chain {[(t['window'], t['jump_to']) for t in a_trace]}) | B {fc_b} hops={hops_b} (refusal trace {[(t['window'], t['jump_to'], t['refuser_bands']) for t in b_trace_own]})")

# --- leg 2: seed_admit_gate rc0 ADMIT both bands (O-20261010-1945-bm-a convention) --
gate_lines = []
for base, span in ((fc_a[0], WIDTH_A), (fc_b[0], WIDTH_B)):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "Tools", "seed_admit_gate.py"),
                         str(base), "--span", str(span)], cwd=ROOT, capture_output=True,
                        text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "").strip().splitlines()
    verdict = out[-1] if out else f"rc{r.returncode} empty"
    assert r.returncode == 0 and "verdict=FREE" in verdict, \
        f"leg2 failed: gate rc={r.returncode} base={base} span={span}: {verdict}"
    gate_lines.append(f"seed_admit_gate rc0 base={base} span={span} "
                      f"checked={span} verdict=FREE")
receipt["legs"]["leg2"] = {"conflicts": 0, "seed_admit_gate": gate_lines}
print("leg2: " + " | ".join(gate_lines))

receipt["legs"]["leg3"] = {"origin_vacancy": True}
print("leg3: origin vacancy TRUE (seat/row/configs/prereg four-check green)")

# --- leg 4: W263+ naive projection (pre-W262 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W263p_A_naive": f"{pA[0]}..{pA[1]}", "W263p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W263p_A_naive_refusers_seeds": pA_refusers,
    "W263p_B_naive": f"{pB[0]}..{pB[1]}", "W263p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W263p_B_lands_inside_W263p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W263+ projection on the pre-W262 universe (assuming the W262 seat bands "
             "declared here register verbatim). ONCE W262 REGISTERS, the naive W263 A "
             "start 593_701 is REFUSED by the registered W262 B band 593_701..593_900 "
             "(staircase-affects-A TWELFTH consecutive A-hop expected) AND the W263 B "
             "naive start lands inside the own-A reservation face; the W263 freezer "
             "MUST re-derive on the post-W262 universe AND reserve the own-wave A "
             "window when deriving B -- never transcribe r587; staircase face "
             "continuing since W251 (A hops over prior B; B lands above own-A): "
             "re-read the live trace, do NOT assume the A-base==prior-B-tail+1 or "
             "B-base==own-A-tail+1 equalities.")}
print(f"leg4: W263+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w262bmc_20261017_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
