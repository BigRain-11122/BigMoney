# -*- coding: utf-8 -*-
"""W255 pre-seat probe (bm-c loop window r1055, 2026-10-16 21:4x; queue-head
supply lane: upstream W254 = bm-c OWN registered+FINALIZED complete chain
(seat MSG-20261016-14xx origin fa70f3765 -> prereg r1054 LANDED e2c4b543e ->
r1055 splice 3eb691575 (zero post-splice heal; 4 authoring defect classes
caught pre-splice by count-asserted gates; sixgate splice-integrity gate-1 n1
triple identity worktree==receipt post==LANDED git blob 7b550e65716e0ada /
pf worktree==receipt post 924e87b3f02afb72 CRLF face) -> engine self-burn
12/12 (ledger appends c211d1269+fa2bc55e5 batched 6+6 self-commit) ->
r1055 absorb-continuation finalize: ledger 983,135 EXACT (980,935+2,200) /
merged pool K=556,720 (554,520+2,200) / fivekeys ALL PASS
results/_r1055bmc_w254_fivekeys.json / sixgate PRE-FINALIZE ALL PASS
results/_r1055bmc_w254_sixgate.json 16th consecutive correct-phase) -- NO
in-flight seat upstream: the W255 FREEZE is UNBLOCKED at seat time. Universe
face = post-W254-REGISTERED (live registry, 244 owner rows: bm-a 129 / bm-b
41 / bm-c 74 incl W254; W255 candidate = 245th wave). STAIRCASE CONTINUATION
face (W254 probe leg4 + prereg sec.5 item5 both projected; live re-derive
governs r587): naive W255 A continuation 576_101..578_100 is REFUSED at the
REGISTERED W254 B band 576_101..576_300 -> A hops past 576_300 to first-clean
576_301..578_300 (FOURTH consecutive A-hop); naive B 576_301..576_500 is
CLEAN at naive BUT lands INSIDE the own-wave A first-clean window -> own-A
reservation hops B past 578_300 to 578_301..578_500 (FIFTH consecutive
above-own-A; B base==own-A tail+1). Bloodline: _w254bmc_20261016_probe.py
derive machinery verbatim (walk/gates/constants), W255 facts
live-registry-driven, compact re-authoring this window per r971 large-task
honest-split law (bands expectations from W254 probe leg4 projection +
prereg sec.5 item5; live walk governs, never transcribed r587)."""
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
receipt = {"probe": "W255 pre-seat probe (bm-c loop r1055 window, 2026-10-16 21:4x, queue-head supply lane: upstream W254 = bm-c OWN registered+FINALIZED complete chain (r1055 absorb-continuation finalize ledger 983,135 / K=556,720); NO in-flight seat upstream -- W255 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; universe = post-W254-REGISTERED 244 owner rows)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W252..W254 landed faces + chain-relation anchors ---
keys = sorted(N1_BANDS)
w254_splice_landed = 254 in N1_BANDS
assert w254_splice_landed, "leg0 failed: W254 splice not landed (registry row absent -- r1055 splice face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 255))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert 255 not in N1_BANDS, "leg0 failed: W255 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W255 universe honestly, do not seat on a stale universe)"

W252_A = tuple(N1_BANDS[252]["a"])
W252_B = tuple(N1_BANDS[252]["b_exit"])
assert W252_A == (569_701, 571_700) and W252_B == (571_701, 571_900) and \
    N1_BANDS[252].get("engine_owner") == "bm-c", "leg0 failed: W252 registry row drift (bm-c r1050 splice face)"

W253_A = tuple(N1_BANDS[253]["a"])
W253_B = tuple(N1_BANDS[253]["b_exit"])
assert W253_A == (571_901, 573_900) and W253_B == (573_901, 574_100) and \
    N1_BANDS[253].get("engine_owner") == "bm-c", "leg0 failed: W253 registry row drift (bm-c r1053 splice face)"
assert W253_A[0] == W252_B[1] + 1, \
    "leg0 failed: W253 A base != W252 B tail+1 (staircase-affects-A second-hop face drift)"
assert W253_B[0] == W253_A[1] + 1, \
    "leg0 failed: W253 B base != own-A tail+1 (above-own-A third consecutive face drift)"

W254_A = tuple(N1_BANDS[254]["a"])
W254_B = tuple(N1_BANDS[254]["b_exit"])
assert W254_A == (574_101, 576_100) and W254_B == (576_101, 576_300) and \
    N1_BANDS[254].get("engine_owner") == "bm-c", "leg0 failed: W254 registry row drift (bm-c r1055 splice face)"
assert W254_A[0] == W253_B[1] + 1, \
    "leg0 failed: W254 A base != W253 B tail+1 (staircase-affects-A third consecutive hop face drift)"
assert W254_B[0] == W254_A[1] + 1, \
    "leg0 failed: W254 B base != own-A tail+1 (above-own-A fourth consecutive face drift)"

for _w in (252, 253, 254):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

w253_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w253_results.json"), encoding="utf-8"))
w253_led = (w253_out.get("science_gates") or {}).get("ledger") or {}
w253_total = w253_led.get("total")
w253_merged_n = w253_out["null_pool_cumulative"]["merged"]["n_values"]
assert w253_total == 980_935 and w253_merged_n == 554_520, \
    f"leg0 failed: W253 finalize anchors drift: total={w253_total} merged={w253_merged_n} (expect 980,935 / 554,520)"

w254_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w254_results.json"), encoding="utf-8"))
w254_led = (w254_out.get("science_gates") or {}).get("ledger") or {}
w254_total = w254_led.get("total")
w254_merged_n = w254_out["null_pool_cumulative"]["merged"]["n_values"]
w254_klift = w254_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
assert w254_total == 983_135 and w254_merged_n == 556_720, \
    f"leg0 failed: W254 finalize anchors drift: total={w254_total} merged={w254_merged_n} (expect 983,135 / 556,720)"
assert w254_total == w253_total + 2_200 and w254_merged_n == w253_merged_n + 2_200, \
    "leg0 failed: W253->W254 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w254_klift is not None and abs(w254_klift) <= 0.02, \
    f"leg0 failed: W254 K-lift out-of-band at seat time: {w254_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 244 and len(bmc_rows) == 74, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 244/74 post-W254-splice, W255 unregistered)"
ordinal = owner_total + 1
assert ordinal == 245, f"leg0 ordinal derive: {ordinal} != 245"
assert len(bma_rows) == 129, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 129 post-W254-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

# --- leg 0.5: no-skip-claim leg (seat numbering density) + chain-complete face --
out_inbox = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
all_inbox = out_inbox.splitlines()
w255_seats_pre = [ln for ln in all_inbox if "w255" in ln.lower() and "seat" in ln.lower()]
assert w255_seats_pre == [], f"leg0.5 failed: W255 seat already claimed on origin: {w255_seats_pre} (vacancy broken -- yield per fleet README sec.4)"
skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w256", "w257")) and "seat" in ln.lower()]
assert skip_claims == [], f"leg0.5 failed: skip-ahead seat claims exist (W255/W256 numbering density violated): {skip_claims}"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W254-registered+FINALIZED (bm-c own-wave complete)",
    "w254_bands": {"A": list(W254_A), "B": list(W254_B)},
    "w253_bands": {"A": list(W253_A), "B": list(W253_B)},
    "w254_finalize_landed": True,
    "w254_finalize_anchors": {"ledger_total": w254_total, "merged_n": w254_merged_n,
                               "skill_line_delta_k_lift": w254_klift},
    "chain_relation": {"w253_total": w253_total, "w254_total": w254_total,
                        "ledger_delta": w254_total - w253_total,
                        "k_delta": w254_merged_n - w253_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W254 complete: registered+FINALIZED; the W255 FREEZE is UNBLOCKED at seat time -- prereg derive = next window FIRST ACTION on the post-W254 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal,
}
print(f"leg0: {len(N1_BANDS)} rows tail=W254-registered+FINALIZED (bm-c own-wave complete, W255 unregistered), W254 face=registry A={W254_A} B={W254_B}, chain-relation W253->W254 ledger 980,935->983,135 (+2,200) K 554,520->556,720 (+2,200) OK, owner={owner_total} -> W255=245th wave candidate")
print("leg0.5: no W255 seat claim on origin (vacancy held) + zero skip-ahead W256/W257 seat claims (numbering density green) + waits-upstream=NONE (W255 freeze UNBLOCKED)")

# --- W255 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox2 = r_vac.stdout.decode("utf-8").splitlines()
w255_seats = [ln for ln in all_inbox2 if "w255" in ln.lower() and "seat" in ln.lower()]
assert w255_seats == [], f"vacancy failed: W255 seats already exist: {w255_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '255: {"a": (' not in out_pf, "vacancy failed: W255 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W255"' not in outn1_vac, "vacancy failed: W255 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W255_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W255 per-wave prereg ALREADY on origin"
print("vacancy: W255 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the W254 REGISTERED tails ------------------
ARITH_A = (W254_A[1] + 1, W254_A[1] + WIDTH_A)
ARITH_B = (W254_B[1] + 1, W254_B[1] + WIDTH_B)


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
assert fc_a == (576_301, 578_300) and hops_a == 1, ("leg1 A staircase face: live walk refused "
                                "the naive start 576_101..578_100 at the REGISTERED W254 B band "
                                "576_101..576_300 (staircase-affects-A FOURTH consecutive hop; "
                                "the W254 prereg sec.5 item5 A-naive-CLEAN projection was a "
                                "pre-W254-universe face, superseded live per r587; if this fires "
                                "the universe changed again: re-read the live trace honestly)")
assert not overlaps(fc_a, W252_A) and not overlaps(fc_a, W252_B), \
    "leg1 failed: A overlaps prior-wave W252 registered bands"
assert not overlaps(fc_a, W253_A) and not overlaps(fc_a, W253_B), \
    "leg1 failed: A overlaps prior-wave W253 registered bands"
assert not overlaps(fc_a, W254_A) and not overlaps(fc_a, W254_B), \
    "leg1 failed: A overlaps prior-wave W254 registered bands"
assert fc_a[0] >= W254_B[1] + 1, \
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
# B honest face: naive start 576_301..576_500 CLEAN at naive BUT lands INSIDE the own-wave
# W255 A first-clean window 576_301..578_300 (own-A reservation face, cascade per the W254
# probe leg4 + prereg sec.5 item5 projections, superseded live per r587); walk governs.
assert fc_b[0] > ARITH_B[0] or hops_b == 0, \
    "leg1 B walk non-rotational/governance violation"
assert fc_b[0] > W254_B[1], \
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W252_A) and not overlaps(fc_b, W252_B), \
    "leg1 failed: B overlaps prior-wave W252 registered bands"
assert not overlaps(fc_b, W253_A) and not overlaps(fc_b, W253_B), \
    "leg1 failed: B overlaps prior-wave W253 registered bands"
assert not overlaps(fc_b, W254_A) and not overlaps(fc_b, W254_B), \
    "leg1 failed: B overlaps prior-wave W254 registered bands"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace_own,
    "B_naive": list(ARITH_B), "B_naive_refused_at_start": fc_b[0] != ARITH_B[0] or hops_b > 0,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "B_lands_above_own_A": fc_b[0] > fc_a[1],
    "A_semantics": ("A arithmetic continuation from the REGISTERED W254 A tail "
                    "576_100+1 = 576_101..578_100 is REFUSED at naive start on the "
                    "post-W254-REGISTERED universe (the REGISTERED W254 B band "
                    "576_101..576_300 sits INSIDE the naive A window: staircase-"
                    "affects-A FOURTH consecutive A-hop, superseding the W254 prereg "
                    "sec.5 item5 A-naive-CLEAN pre-W254-universe projection per "
                    "r587); the walk hops past the W254 B tail 576_300 -> A first-clean "
                    "576_301..578_300 (hops=1); forward-monotone non-rotational r587 "
                    "enforced in-walk; A base >= registered prior-wave B tail+1 floor"),
    "B_semantics": ("B walk from the REGISTERED W254 B tail 576_300+1 = 576_301 is "
                    "CLEAN at naive start but the naive window 576_301..576_500 lands "
                    "INSIDE the own-wave W255 A first-clean window 576_301..578_300 "
                    "(own-A reservation cascade face, per the W254 probe leg4 + "
                    "prereg sec.5 item5 projection faces superseded live) -- the "
                    "own-A reservation standard leg hops B past the own-wave A tail "
                    "578_300 -> first-clean 578_301..578_500 (B lands above own-A, "
                    "base==own-A tail+1 face, FIFTH consecutive above-own-A); "
                    "B_hop lands-inside-A=false leg; live trace recorded verbatim"),
    "relation_asserts": {"A_clean_at_naive_start": False,
                          "A_staircase_hop_past_W254_B": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": fc_b[0] == ARITH_B[0] and hops_b == 0,
                          "B_base_above_W254_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "B_lands_above_own_A": True,
                          "W252_W253_W254_bands_respected_A": True,
                          "W252_W253_W254_bands_respected_B": True}}
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

# --- leg 4: W256+ naive projection (pre-W255 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W256p_A_naive": f"{pA[0]}..{pA[1]}", "W256p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W256p_A_naive_refusers_seeds": pA_refusers,
    "W256p_B_naive": f"{pB[0]}..{pB[1]}", "W256p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W256p_B_lands_inside_W256p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W256+ projection on the pre-W255 universe (assuming the W255 seat bands "
             "declared here register verbatim). ONCE W255 REGISTERS, the naive W256 A "
             "start 578_301 is REFUSED by the registered W255 B band 578_301..578_500 "
             "(staircase-affects-A FIFTH consecutive A-hop expected) AND the W256 B "
             "naive start 578_501..578_700 is refused by the own-A reservation face; "
             "the W256 freezer MUST re-derive on the post-W255 universe AND reserve "
             "the own-wave A window when deriving B -- never transcribe r587; "
             "staircase face continuing since W251 (A hops over prior B; B lands above "
             "own-A): re-read the live trace, do NOT assume the A-base==prior-B-tail+1 "
             "or B-base==own-A-tail+1 equalities.")}
print(f"leg4: W256+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w255bmc_20261016_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
