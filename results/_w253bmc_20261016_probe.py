# -*- coding: utf-8 -*-
"""W253 pre-seat probe (bm-c loop window r1050, 2026-10-16 12:xx; queue-head
supply lane: upstream W252 = bm-c OWN registered+FINALIZED complete chain
(seat MSG-20261016-10xx origin f9441de67 -> prereg r1049 LANDED 472cc8386 ->
r1050 dead-window five-face splice e63561df3 (zero post-splice heal; 5 authoring
defect classes caught pre-splice by count-asserted gates) -> engine self-burn
12/12 (ledger appends cbf6411bf+b3d563f4f batched 6+6 self-commit) -> r1050
absorb-continuation finalize: ledger 978,735 EXACT (976,535+2,200) / merged pool
K=552,320 (550,120+2,200) / fivekeys ALL PASS results/_r1050bmc_w252_fivekeys.json
/ sixgate ALL PASS results/_r1050bmc_w252_sixgate.json PRE-FINALIZE phase, gate-1
triple identity worktree==receipt==landed git blob n1 7252c90bad52de99 /
pf b3eed1c579e7f22f) -- NO in-flight seat upstream: the W253 FREEZE is
UNBLOCKED at seat time. Universe face = post-W252-REGISTERED (live registry,
242 owner rows: bm-a 129 / bm-b 41 / bm-c 72 incl W252; W253 candidate = 243rd
wave). STAIRCASE CONTINUATION face (W252 probe leg4 + prereg sec.5 item5 both
projected; live re-derive governs r587): naive W253 A continuation
571_701..573_700 is REFUSED at the REGISTERED W252 B band 571_701..571_900
-> A hops past 571_900 to first-clean 571_901..573_900 (second consecutive
A-hop); naive B 571_901..572_100 is CLEAN at naive BUT lands INSIDE the own-wave
A first-clean window -> own-A reservation hops B past 573_900 to
573_901..574_100 (third consecutive above-own-A; B base==own-A tail+1).
Bloodline: _w252bmc_20261016_probe.py derive machinery verbatim (walk/gates/
constants), W253 facts live-registry-driven, compact re-authoring this window
per r971 large-task honest-split law (bands expectations from W252 probe leg4
projection + prereg sec.5 item5; live walk governs, never transcribed r587)."""
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
receipt = {"probe": "W253 pre-seat probe (bm-c loop r1050 window, 2026-10-16 12:xx, queue-head supply lane: upstream W252 = bm-c OWN registered+FINALIZED complete chain (r1050 absorb-continuation finalize ledger 978,735 / K=552,320); NO in-flight seat upstream -- W253 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing + O-20261015-0025 full mobilization; universe = post-W252-REGISTERED 242 owner rows)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W250..W252 landed faces + chain-relation anchors ---
keys = sorted(N1_BANDS)
w252_splice_landed = 252 in N1_BANDS
assert w252_splice_landed, "leg0 failed: W252 splice not landed (registry row absent -- r1050 splice face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 253))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert 253 not in N1_BANDS, "leg0 failed: W253 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W253 universe honestly, do not seat on a stale universe)"

W250_A = tuple(N1_BANDS[250]["a"])
W250_B = tuple(N1_BANDS[250]["b_exit"])
assert W250_A == (565_501, 567_500) and W250_B == (545_101, 545_300) and \
    N1_BANDS[250].get("engine_owner") == "bm-c", "leg0 failed: W250 registry row drift (bm-c r1046 splice face)"

W251_A = tuple(N1_BANDS[251]["a"])
W251_B = tuple(N1_BANDS[251]["b_exit"])
assert W251_A == (567_501, 569_500) and W251_B == (569_501, 569_700) and \
    N1_BANDS[251].get("engine_owner") == "bm-c", "leg0 failed: W251 registry row drift (bm-c r1048 splice face)"

W252_A = tuple(N1_BANDS[252]["a"])
W252_B = tuple(N1_BANDS[252]["b_exit"])
assert W252_A == (569_701, 571_700) and W252_B == (571_701, 571_900) and \
    N1_BANDS[252].get("engine_owner") == "bm-c", "leg0 failed: W252 registry row drift (bm-c r1050 splice face)"
assert W252_A[0] == W251_B[1] + 1, \
    "leg0 failed: W252 A base != W251 B tail+1 (staircase-affects-A first-hop face drift)"
assert W252_B[0] == W252_A[1] + 1, \
    "leg0 failed: W252 B base != own-A tail+1 (above-own-A second consecutive face drift)"

for _w in (250, 251, 252):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

w251_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w251_results.json"), encoding="utf-8"))
w251_led = (w251_out.get("science_gates") or {}).get("ledger") or {}
w251_total = w251_led.get("total")
w251_merged_n = w251_out["null_pool_cumulative"]["merged"]["n_values"]
assert w251_total == 976_535 and w251_merged_n == 550_120, \
    f"leg0 failed: W251 finalize anchors drift: total={w251_total} merged={w251_merged_n} (expect 976,535 / 550,120)"

w252_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w252_results.json"), encoding="utf-8"))
w252_led = (w252_out.get("science_gates") or {}).get("ledger") or {}
w252_total = w252_led.get("total")
w252_merged_n = w252_out["null_pool_cumulative"]["merged"]["n_values"]
w252_klift = w252_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
assert w252_total == 978_735 and w252_merged_n == 552_320, \
    f"leg0 failed: W252 finalize anchors drift: total={w252_total} merged={w252_merged_n} (expect 978,735 / 552,320)"
assert w252_total == w251_total + 2_200 and w252_merged_n == w251_merged_n + 2_200, \
    "leg0 failed: W251->W252 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w252_klift is not None and abs(w252_klift) <= 0.02, \
    f"leg0 failed: W252 K-lift out-of-band at seat time: {w252_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 242 and len(bmc_rows) == 72, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 242/72 post-W252-splice, W253 unregistered)"
ordinal = owner_total + 1
assert ordinal == 243, f"leg0 ordinal derive: {ordinal} != 243"
assert len(bma_rows) == 129, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 129 post-W252-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

# --- leg 0.5: no-skip-claim leg (seat numbering density) + chain-complete face --
out_inbox = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
all_inbox = out_inbox.splitlines()
w253_seats_pre = [ln for ln in all_inbox if "w253" in ln.lower() and "seat" in ln.lower()]
assert w253_seats_pre == [], f"leg0.5 failed: W253 seat already claimed on origin: {w253_seats_pre} (vacancy broken -- yield per fleet README sec.4)"
skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w254", "w255")) and "seat" in ln.lower()]
assert skip_claims == [], f"leg0.5 failed: skip-ahead seat claims exist (W253/W254 numbering density violated): {skip_claims}"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W252-registered+FINALIZED (bm-c own-wave complete)",
    "w252_bands": {"A": list(W252_A), "B": list(W252_B)},
    "w251_bands": {"A": list(W251_A), "B": list(W251_B)},
    "w252_finalize_landed": True,
    "w252_finalize_anchors": {"ledger_total": w252_total, "merged_n": w252_merged_n,
                               "skill_line_delta_k_lift": w252_klift},
    "chain_relation": {"w251_total": w251_total, "w252_total": w252_total,
                        "ledger_delta": w252_total - w251_total,
                        "k_delta": w252_merged_n - w251_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W252 complete: registered+FINALIZED; the W253 FREEZE is UNBLOCKED at seat time -- prereg derive = next window FIRST ACTION on the post-W252 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal,
}
print(f"leg0: {len(N1_BANDS)} rows tail=W252-registered+FINALIZED (bm-c own-wave complete, W253 unregistered), W252 face=registry A={W252_A} B={W252_B}, chain-relation W251->W252 ledger 976,535->978,735 (+2,200) K 550,120->552,320 (+2,200) OK, owner={owner_total} -> W253=243rd wave candidate")
print("leg0.5: no W253 seat claim on origin (vacancy held) + zero skip-ahead W254/W255 seat claims (numbering density green) + waits-upstream=NONE (W253 freeze UNBLOCKED)")

# --- W253 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox2 = r_vac.stdout.decode("utf-8").splitlines()
w253_seats = [ln for ln in all_inbox2 if "w253" in ln.lower() and "seat" in ln.lower()]
assert w253_seats == [], f"vacancy failed: W253 seats already exist: {w253_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '253: {"a": (' not in out_pf, "vacancy failed: W253 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W253"' not in outn1_vac, "vacancy failed: W253 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W253_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W253 per-wave prereg ALREADY on origin"
print("vacancy: W253 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the W252 REGISTERED tails ------------------
ARITH_A = (W252_A[1] + 1, W252_A[1] + WIDTH_A)
ARITH_B = (W252_B[1] + 1, W252_B[1] + WIDTH_B)


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
assert fc_a == (571_901, 573_900) and hops_a == 1, ("leg1 A staircase face: live walk refused "
                                "the naive start 571_701..573_700 at the REGISTERED W252 B band "
                                "571_701..571_900 (staircase-affects-A SECOND consecutive hop; "
                                "the W252 prereg sec.5 item5 A-CLEAN-at-naive projection was a "
                                "pre-W252-universe face, superseded live per r587; if this fires "
                                "the universe changed again: re-read the live trace honestly)")
assert not overlaps(fc_a, W251_A) and not overlaps(fc_a, W251_B), \
    "leg1 failed: A overlaps prior-wave W251 registered bands"
assert not overlaps(fc_a, W252_A) and not overlaps(fc_a, W252_B), \
    "leg1 failed: A overlaps prior-wave W252 registered bands"
assert fc_a[0] >= W252_B[1] + 1, \
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
# B honest face: naive start 571_901..572_100 CLEAN at naive but lands INSIDE the own-wave
# W253 A first-clean window 571_901..573_900 (own-A reservation face, cascade per the W252
# probe leg4 + prereg sec.5 item5 projections, superseded live per r587); walk governs.
assert fc_b[0] > ARITH_B[0] or hops_b == 0, \
    "leg1 B walk non-rotational/governance violation"
assert fc_b[0] > W252_B[1], \
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W251_A) and not overlaps(fc_b, W251_B), \
    "leg1 failed: B overlaps prior-wave W251 registered bands"
assert not overlaps(fc_b, W252_A) and not overlaps(fc_b, W252_B), \
    "leg1 failed: B overlaps prior-wave W252 registered bands"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace_own,
    "B_naive": list(ARITH_B), "B_naive_refused_at_start": fc_b[0] != ARITH_B[0] or hops_b > 0,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "B_lands_above_own_A": fc_b[0] > fc_a[1],
    "A_semantics": ("A arithmetic continuation from the REGISTERED W252 A tail "
                    "571_700+1 = 571_701..573_700 is REFUSED at naive start on the "
                    "post-W252-REGISTERED universe (the REGISTERED W252 B band "
                    "571_701..571_900 sits INSIDE the naive A window: staircase-"
                    "affects-A SECOND consecutive A-hop, superseding the W252 prereg "
                    "sec.5 item5 A-CLEAN-at-naive pre-W252-universe projection per "
                    "r587); the walk hops past the W252 B tail 571_900 -> A first-clean "
                    "571_901..573_900 (hops=1); forward-monotone non-rotational r587 "
                    "enforced in-walk; A base >= registered prior-wave B tail+1 floor"),
    "B_semantics": ("B walk from the REGISTERED W252 B tail 571_900+1 = 571_901 is "
                    "CLEAN at naive start but the naive window 571_901..572_100 lands "
                    "INSIDE the own-wave W253 A first-clean window 571_901..573_900 "
                    "(own-A reservation cascade face, per the W252 probe leg4 + "
                    "prereg sec.5 item5 projection faces superseded live) -- the "
                    "own-A reservation standard leg hops B past the own-wave A tail "
                    "573_900 -> first-clean 573_901..574_100 (B lands above own-A, "
                    "base==own-A tail+1 face, THIRD consecutive above-own-A); "
                    "B_hop lands-inside-A=false leg; live trace recorded verbatim"),
    "relation_asserts": {"A_clean_at_naive_start": False,
                          "A_staircase_hop_past_W252_B": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": fc_b[0] == ARITH_B[0] and hops_b == 0,
                          "B_base_above_W252_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "B_lands_above_own_A": True,
                          "W251_W252_bands_respected_A": True,
                          "W251_W252_bands_respected_B": True}}
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

# --- leg 4: W254+ naive projection (pre-W253 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W254p_A_naive": f"{pA[0]}..{pA[1]}", "W254p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W254p_A_naive_refusers_seeds": pA_refusers,
    "W254p_B_naive": f"{pB[0]}..{pB[1]}", "W254p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W254p_B_lands_inside_W254p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W254+ projection on the pre-W253 universe (assuming the W253 seat bands "
             "declared here register verbatim). The W254 freezer MUST re-derive on the "
             "post-W253 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587; staircase face continuing since W251 "
             "(A hops over prior B; B lands above own-A): re-read the live trace, do NOT "
             "assume the A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities.")}
print(f"leg4: W254+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w253bmc_20261016_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
