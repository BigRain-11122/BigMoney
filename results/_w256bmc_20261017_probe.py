# -*- coding: utf-8 -*-
"""W256 pre-seat probe (bm-c loop window r1057, 2026-10-17 0x:xx; queue-head
supply lane: upstream W255 = bm-c OWN registered+FINALIZED complete chain
(seat MSG-20261016-22xx origin cb79242ed -> prereg r1056 LANDED 72d292ea3 ->
r1057 dead-window five-face freeze splice e166afc6c (2 disclosed needle heals
+ 2 blanket-duplication sub heals caught pre-splice by count-asserted gates;
sixgate splice-integrity gate-1 n1 TRIPLE identity worktree==receipt post==
LANDED git blob c6dfb4291c09be1e / pf worktree==receipt post d4a9d7164ba9490e
CRLF face) -> engine self-burn 12/12 (ledger appends b1414b81a+f931cf102
batched 6+6 self-commit) -> r1057 48th-gen absorb-continuation finalize: ledger
985,335 EXACT (983,135+2,200) / merged pool K=558,920 (556,720+2,200) /
fivekeys ALL PASS results/_r1057bmc_w255_fivekeys.json / sixgate PRE-FINALIZE
ALL PASS results/_r1057bmc_w255_sixgate.json 17th consecutive correct-phase)
-- NO in-flight seat upstream: the W256 FREEZE is UNBLOCKED at seat time.
Universe face = post-W255-REGISTERED (live registry, 245 owner rows: bm-a 129
/ bm-b 41 / bm-c 75 incl W255; W256 candidate = 246th wave). STAIRCASE
CONTINUATION face (W255 probe leg4 + prereg sec.5 item5 both projected; live
re-derive governs r587): naive W256 A continuation 578_301..580_300 is
REFUSED at the REGISTERED W255 B band 578_301..578_500 -> A hops past 578_500
to first-clean 578_501..580_500 (FIFTH consecutive A-hop expected); naive B
578_501..578_700 is CLEAN at naive BUT lands INSIDE the own-wave A
first-clean window -> own-A reservation hops B past 580_500 to 580_501..580_700
(SIXTH consecutive above-own-A expected; B base==own-A tail+1 floor).
Bloodline: _w255bmc_20261016_probe.py derive machinery verbatim
(walk/gates/constants), W256 facts live-registry-driven, compact re-authoring
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
receipt = {"probe": "W256 pre-seat probe (bm-c loop r1057 window, 2026-10-17 0x:xx, queue-head supply lane: upstream W255 = bm-c OWN registered+FINALIZED complete chain (r1057 48th-gen absorb-continuation finalize ledger 985,335 / K=558,920); NO in-flight seat upstream -- W256 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; universe = post-W255-REGISTERED 245 owner rows)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W253..W255 landed faces + chain-relation anchors ---
keys = sorted(N1_BANDS)
w255_splice_landed = 255 in N1_BANDS
assert w255_splice_landed, "leg0 failed: W255 splice not landed (registry row absent -- r1057 splice face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 256))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert 256 not in N1_BANDS, "leg0 failed: W256 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W256 universe honestly, do not seat on a stale universe)"

W253_A = tuple(N1_BANDS[253]["a"])
W253_B = tuple(N1_BANDS[253]["b_exit"])
assert W253_A == (571_901, 573_900) and W253_B == (573_901, 574_100) and \
    N1_BANDS[253].get("engine_owner") == "bm-c", "leg0 failed: W253 registry row drift (bm-c r1053 splice face)"

W254_A = tuple(N1_BANDS[254]["a"])
W254_B = tuple(N1_BANDS[254]["b_exit"])
assert W254_A == (574_101, 576_100) and W254_B == (576_101, 576_300) and \
    N1_BANDS[254].get("engine_owner") == "bm-c", "leg0 failed: W254 registry row drift (bm-c r1055 splice face)"
assert W254_A[0] == W253_B[1] + 1, \
    "leg0 failed: W254 A base != W253 B tail+1 (staircase-affects-A third consecutive hop face drift)"
assert W254_B[0] == W254_A[1] + 1, \
    "leg0 failed: W254 B base != own-A tail+1 (above-own-A fourth consecutive face drift)"

W255_A = tuple(N1_BANDS[255]["a"])
W255_B = tuple(N1_BANDS[255]["b_exit"])
assert W255_A == (576_301, 578_300) and W255_B == (578_301, 578_500) and \
    N1_BANDS[255].get("engine_owner") == "bm-c", "leg0 failed: W255 registry row drift (bm-c r1057 splice face)"
assert W255_A[0] == W254_B[1] + 1, \
    "leg0 failed: W255 A base != W254 B tail+1 (staircase-affects-A fourth consecutive hop face drift)"
assert W255_B[0] == W255_A[1] + 1, \
    "leg0 failed: W255 B base != own-A tail+1 (above-own-A fifth consecutive face drift)"

for _w in (253, 254, 255):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

w254_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w254_results.json"), encoding="utf-8"))
w254_led = (w254_out.get("science_gates") or {}).get("ledger") or {}
w254_total = w254_led.get("total")
w254_merged_n = w254_out["null_pool_cumulative"]["merged"]["n_values"]
assert w254_total == 983_135 and w254_merged_n == 556_720, \
    f"leg0 failed: W254 finalize anchors drift: total={w254_total} merged={w254_merged_n} (expect 983,135 / 556,720)"

w255_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w255_results.json"), encoding="utf-8"))
w255_led = (w255_out.get("science_gates") or {}).get("ledger") or {}
w255_total = w255_led.get("total")
w255_merged_n = w255_out["null_pool_cumulative"]["merged"]["n_values"]
w255_klift = w255_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
assert w255_total == 985_335 and w255_merged_n == 558_920, \
    f"leg0 failed: W255 finalize anchors drift: total={w255_total} merged={w255_merged_n} (expect 985,335 / 558,920)"
assert w255_total == w254_total + 2_200 and w255_merged_n == w254_merged_n + 2_200, \
    "leg0 failed: W254->W255 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w255_klift is not None and abs(w255_klift) <= 0.02, \
    f"leg0 failed: W255 K-lift out-of-band at seat time: {w255_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 245 and len(bmc_rows) == 75, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 245/75 post-W255-splice, W256 unregistered)"
ordinal = owner_total + 1
assert ordinal == 246, f"leg0 ordinal derive: {ordinal} != 246"
assert len(bma_rows) == 129, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 129 post-W255-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

# --- leg 0.5: no-skip-claim leg (seat numbering density) + chain-complete face --
out_inbox = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
all_inbox = out_inbox.splitlines()
w256_seats_pre = [ln for ln in all_inbox if "w256" in ln.lower() and "seat" in ln.lower()]
assert w256_seats_pre == [], f"leg0.5 failed: W256 seat already claimed on origin: {w256_seats_pre} (vacancy broken -- yield per fleet README sec.4)"
skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w257", "w258")) and "seat" in ln.lower()]
assert skip_claims == [], f"leg0.5 failed: skip-ahead seat claims exist (W256/W257 numbering density violated): {skip_claims}"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W255-registered+FINALIZED (bm-c own-wave complete)",
    "w255_bands": {"A": list(W255_A), "B": list(W255_B)},
    "w254_bands": {"A": list(W254_A), "B": list(W254_B)},
    "w255_finalize_landed": True,
    "w255_finalize_anchors": {"ledger_total": w255_total, "merged_n": w255_merged_n,
                               "skill_line_delta_k_lift": w255_klift},
    "chain_relation": {"w254_total": w254_total, "w255_total": w255_total,
                       "ledger_delta": w255_total - w254_total,
                       "k_delta": w255_merged_n - w254_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W255 complete: registered+FINALIZED; the W256 FREEZE is UNBLOCKED at seat time -- prereg derive = next window FIRST ACTION on the post-W255 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal,
}
print(f"leg0: {len(N1_BANDS)} rows tail=W255-registered+FINALIZED (bm-c own-wave complete, W256 unregistered), W255 face=registry A={W255_A} B={W255_B}, chain-relation W254->W255 ledger 983,135->985,335 (+2,200) K 556,720->558,920 (+2,200) OK, owner={owner_total} -> W256=246th wave candidate")
print("leg0.5: no W256 seat claim on origin (vacancy held) + zero skip-ahead W257/W258 seat claims (numbering density green) + waits-upstream=NONE (W256 freeze UNBLOCKED)")

# --- W256 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox2 = r_vac.stdout.decode("utf-8").splitlines()
w256_seats = [ln for ln in all_inbox2 if "w256" in ln.lower() and "seat" in ln.lower()]
assert w256_seats == [], f"vacancy failed: W256 seats already exist: {w256_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '256: {"a": (' not in out_pf, "vacancy failed: W256 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W256"' not in outn1_vac, "vacancy failed: W256 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W256_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W256 per-wave prereg ALREADY on origin"
print("vacancy: W256 origin vacancy held (no seat / row / configs / prereg)")

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: honest forward walk from the W255 REGISTERED tails ------------------
ARITH_A = (W255_A[1] + 1, W255_A[1] + WIDTH_A)
ARITH_B = (W255_B[1] + 1, W255_B[1] + WIDTH_B)


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
assert fc_a == (578_501, 580_500) and hops_a == 1, ("leg1 A staircase face: live walk refused "
                                "the naive start 578_301..580_300 at the REGISTERED W255 B band "
                                "578_301..578_500 (staircase-affects-A FIFTH consecutive hop; "
                                "the W255 prereg sec.5 item5 A-naive-CLEAN projection was a "
                                "pre-W255-universe face, superseded live per r587; if this fires "
                                "the universe changed again: re-read the live trace honestly)")
assert not overlaps(fc_a, W253_A) and not overlaps(fc_a, W253_B), \
    "leg1 failed: A overlaps prior-wave W253 registered bands"
assert not overlaps(fc_a, W254_A) and not overlaps(fc_a, W254_B), \
    "leg1 failed: A overlaps prior-wave W254 registered bands"
assert not overlaps(fc_a, W255_A) and not overlaps(fc_a, W255_B), \
    "leg1 failed: A overlaps prior-wave W255 registered bands"
assert fc_a[0] >= W255_B[1] + 1, \
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
# B honest face: naive start 578_501..578_700 CLEAN at naive BUT lands INSIDE the own-wave
# W256 A first-clean window 578_501..580_500 (own-A reservation face, cascade per the W255
# probe leg4 + prereg sec.5 item5 projections, superseded live per r587); walk governs.
assert fc_b[0] > ARITH_B[0] or hops_b == 0, \
    "leg1 B walk non-rotational/governance violation"
assert fc_b[0] > W255_B[1], \
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W253_A) and not overlaps(fc_b, W253_B), \
    "leg1 failed: B overlaps prior-wave W253 registered bands"
assert not overlaps(fc_b, W254_A) and not overlaps(fc_b, W254_B), \
    "leg1 failed: B overlaps prior-wave W254 registered bands"
assert not overlaps(fc_b, W255_A) and not overlaps(fc_b, W255_B), \
    "leg1 failed: B overlaps prior-wave W255 registered bands"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace_own,
    "B_naive": list(ARITH_B), "B_naive_refused_at_start": fc_b[0] != ARITH_B[0] or hops_b > 0,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "B_lands_above_own_A": fc_b[0] > fc_a[1],
    "A_semantics": ("A arithmetic continuation from the REGISTERED W255 A tail "
                    "578_300+1 = 578_301..580_300 is REFUSED at naive start on the "
                    "post-W255-REGISTERED universe (the REGISTERED W255 B band "
                    "578_301..578_500 sits INSIDE the naive A window: staircase-"
                    "affects-A FIFTH consecutive A-hop, superseding the W255 prereg "
                    "sec.5 item5 A-naive-CLEAN pre-W255-universe projection per "
                    "r587); the walk hops past the W255 B tail 578_500 -> A first-clean "
                    "578_501..580_500 (hops=1); forward-monotone non-rotational r587 "
                    "enforced in-walk; A base >= registered prior-wave B tail+1 floor"),
    "B_semantics": ("B walk from the REGISTERED W255 B tail 578_500+1 = 578_501 is "
                    "CLEAN at naive start but the naive window 578_501..578_700 lands "
                    "INSIDE the own-wave W256 A first-clean window 578_501..580_500 "
                    "(own-A reservation cascade face, per the W255 probe leg4 + "
                    "prereg sec.5 item5 projection faces superseded live) -- the "
                    "own-A reservation standard leg hops B past the own-wave A tail "
                    "580_500 -> first-clean 580_501..580_700 (B lands above own-A, "
                    "base==own-A tail+1 face, SIXTH consecutive above-own-A); "
                    "B_hop lands-inside-A=false leg; live trace recorded verbatim"),
    "relation_asserts": {"A_clean_at_naive_start": False,
                          "A_staircase_hop_past_W255_B": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": fc_b[0] == ARITH_B[0] and hops_b == 0,
                          "B_base_above_W255_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "B_lands_above_own_A": True,
                          "W253_W254_W255_bands_respected_A": True,
                          "W253_W254_W255_bands_respected_B": True}}
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

# --- leg 4: W257+ naive projection (pre-W256 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W257p_A_naive": f"{pA[0]}..{pA[1]}", "W257p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W257p_A_naive_refusers_seeds": pA_refusers,
    "W257p_B_naive": f"{pB[0]}..{pB[1]}", "W257p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W257p_B_lands_inside_W257p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W257+ projection on the pre-W256 universe (assuming the W256 seat bands "
             "declared here register verbatim). ONCE W256 REGISTERS, the naive W257 A "
             "start 580_501 is REFUSED by the registered W256 B band 580_501..580_700 "
             "(staircase-affects-A SIXTH consecutive A-hop expected) AND the W257 B "
             "naive start lands inside the own-A reservation face; the W257 freezer "
             "MUST re-derive on the post-W256 universe AND reserve the own-wave A "
             "window when deriving B -- never transcribe r587; staircase face "
             "continuing since W251 (A hops over prior B; B lands above own-A): "
             "re-read the live trace, do NOT assume the A-base==prior-B-tail+1 or "
             "B-base==own-A-tail+1 equalities.")}
print(f"leg4: W257+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w256bmc_20261017_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
