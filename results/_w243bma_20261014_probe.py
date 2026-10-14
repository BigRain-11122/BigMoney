# -*- coding: utf-8 -*-
"""W243 pre-seat probe (bm-a loop window r1000, 2026-10-14 21:0x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20261013 22:1x
CPU standing-open order + O-20260924-1730 claim-ignite same-round law +
never-dry supply line O-1819 + O-20261010-2350-bm-c sec.2 seat-first law:
seats do NOT queue behind freeze windows and MUST NOT wait for the prior wave
to burn out -- queue depth is the physical guarantee of saturation.
Upstream face = W241 registered+FINALIZED (bm-c own-wave closeout: seat
MSG-20261014-1755-bmc-w241-seat + freeze splice 8e980ce3e + engine self-burn
12/12 + finalize one-pass ledger 952,335+2,200=954,535 EXACT / merged pool
K=528,120 / five-key ALL PASS _w241bmc_fivekey_receipt.json + product
n1_w241_results.json) AND W242 = registered+FINALIZED (bm-a r999 own-wave
closeout absorbing the dead r998 session estate: seat
MSG-20261014-1814-bma-w242-seat + freeze splice 90db59fc3-pre estate five-face
bands A 549_501..551_500 / B 541_204..541_403 + engine self-burn 12/12 done
20:44 + finalize one-pass ledger 954,535+2,200=956,735 EXACT / merged pool
K=530,320 / skill_line 1.1934->1.1932 K-lift -0.0002 in-band + product
n1_w242_results.json). ZERO in-flight upstream seats at this seat window --
the W243 FREEZE is UNBLOCKED immediately (waits-upstream DISARMED by the W242
finalize landing 20:4x); this W243 seat = the queue-depth supply depth-1
(first seat of the new supply cycle after the W242 closeout).
Per the W242 probe leg4 mandate: re-derive live on the post-W242-REGISTERED
universe AND reserve the own-wave A window when deriving B, W141 precedent,
never transcribe r587; seed-gap face inherited: W242 A/B are decoupled, do NOT
assume the staircase A-base==prior-B-tail+1 equality.
Anticipated face (W242 probe leg4, honest forward face): naive W243 A
continuation 551_501..553_500 first-clean hops=0 (no live refusers) / naive B
541_404..541_603 hops=1 -- live refusal inside the naive window (SEED_REGISTRY
point face, honest forward walk first-clean 541_501..541_700) -- live
re-derive governs either way, non-rotational r587 forward-monotone enforced
in-walk.
Bloodline: _w242bma_20261014_probe.py derive machinery verbatim (W241
assert style for the clean-continuation face; B live-refusal hop face per the
W238-generation honest-walk precedent), W243 facts
live-registry/receipt-driven; single-state leg0 (W242 splice LANDED, registry
row face)."""
import subprocess
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
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
receipt = {"probe": "W243 pre-seat probe (bm-a loop r1000 window, 2026-10-14 21:0x, CEO fill-order standing + seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + O-20261013-22:1x CPU standing-open; post-W242-REGISTERED universe, upstream W241+W242 both registered+FINALIZED (W241 bm-c closeout ledger 954,535 / K=528,120; W242 bm-a r999 closeout ledger 956,735 / K=530,320); ZERO in-flight upstream seats -- W243 freeze UNBLOCKED at seat time, queue-depth supply depth-1)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W238..W242 landed faces + W242 finalize face ---
keys = sorted(N1_BANDS)
w242_splice_landed = 242 in N1_BANDS
assert w242_splice_landed, "leg0 failed: W242 splice not landed (registry row absent -- r998/r999 estate face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 243))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W238_A = tuple(N1_BANDS[238]["a"])
W238_B = tuple(N1_BANDS[238]["b_exit"])
assert W238_A == (538_404, 540_403) and W238_B == (540_404, 540_603) and \
    N1_BANDS[238].get("engine_owner") == "bm-a", "leg0 failed: W238 registry row drift"
W239_A = tuple(N1_BANDS[239]["a"])
W239_B = tuple(N1_BANDS[239]["b_exit"])
assert W239_A == (542_501, 544_500) and W239_B == (540_604, 540_803) and \
    N1_BANDS[239].get("engine_owner") == "bm-c", "leg0 failed: W239 registry row drift"
assert W239_B[0] == W238_B[1] + 1, "leg0 failed: W239 B base != W238 B tail+1 (registry face drift)"
assert W239_A[0] >= W238_B[1] + 1, "leg0 failed: W239 A base below W238 B tail+1 floor (seed-gap face check)"
W240_A = tuple(N1_BANDS[240]["a"])
W240_B = tuple(N1_BANDS[240]["b_exit"])
assert W240_A == (545_501, 547_500) and W240_B == (540_804, 541_003) and \
    N1_BANDS[240].get("engine_owner") == "bm-a", "leg0 failed: W240 registry row drift"
assert W240_B[0] == W239_B[1] + 1, "leg0 failed: W240 B base != W239 B tail+1 (registry face drift)"
assert W240_A[0] >= W239_B[1] + 1, "leg0 failed: W240 A base below W239 B tail+1 floor"
W241_A = tuple(N1_BANDS[241]["a"])
W241_B = tuple(N1_BANDS[241]["b_exit"])
assert W241_A == (547_501, 549_500) and W241_B == (541_004, 541_203) and \
    N1_BANDS[241].get("engine_owner") == "bm-c", "leg0 failed: W241 registry row drift"
assert W241_B[0] == W240_B[1] + 1, "leg0 failed: W241 B base != W240 B tail+1 (registry face drift)"
assert W241_A[0] >= W240_B[1] + 1, "leg0 failed: W241 A base below W240 B tail+1 floor"

# W241 finalize landed face (upstream transitive dep)
w241_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w241_results.json")
assert os.path.exists(w241_results), "leg0 failed: n1_w241_results.json absent (W241 finalize not landed)"

# W242 prior-wave bands: registry row face (splice LANDED)
W242_A = tuple(N1_BANDS[242]["a"])
W242_B = tuple(N1_BANDS[242]["b_exit"])
assert W242_A == (549_501, 551_500) and W242_B == (541_204, 541_403) and \
    N1_BANDS[242].get("engine_owner") == "bm-a", "leg0 failed: W242 registry row drift (bm-a r998 splice + r999 closeout face)"
assert W242_B[0] == W241_B[1] + 1, "leg0 failed: W242 B base != W241 B tail+1 (registry face drift)"
assert W242_A[0] >= W241_B[1] + 1, "leg0 failed: W242 A base below W241 B tail+1 floor (seed-gap face check)"

# W242 finalize landed face (the immediate upstream anchor)
w242_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w242_results.json")
assert os.path.exists(w242_results), "leg0 failed: n1_w242_results.json absent (W242 finalize not landed)"
w242_out = json.load(open(w242_results, encoding="utf-8"))
w242_led = (w242_out.get("science_gates") or {}).get("ledger") or {}
w242_total = w242_led.get("total")
w242_merged_n = None
w242_klift = None
try:
    w242_merged_n = w242_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
try:
    w242_klift = w242_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
except Exception:
    pass
assert w242_total == 956_735 and w242_merged_n == 530_320, \
    f"leg0 failed: W242 finalize anchors drift: total={w242_total} merged={w242_merged_n} (expect 956,735 / 530,320)"
assert w242_klift is not None and abs(w242_klift) <= 0.02, \
    f"leg0 failed: W242 K-lift out-of-band at seat time: {w242_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 232 and len(bmc_rows) == 67, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 232/67 post-W242-splice)"
ordinal = owner_total + 1
assert ordinal == 233, f"leg0 ordinal derive: {ordinal} != 233"
assert len(bma_rows) == 124, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 124 post-W242-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"
bma_ordinal = len(bma_rows) + 1
assert bma_ordinal == 125, f"leg0 bma ordinal derive: {bma_ordinal} != 125"

# W242 seat on origin (the prior closeout chain face)
outseat242 = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
seat_hits = [ln for ln in outseat242.splitlines()
             if "w242" in ln.lower() and "seat" in ln.lower()]
assert seat_hits, "leg0 failed: W242 seat MSG not found on origin (closeout chain face absent)"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W242-registered",
    "w242_splice_landed": w242_splice_landed,
    "w242_face": "registry-row",
    "w242_bands": {"A": list(W242_A), "B": list(W242_B)},
    "w242_finalize_landed": True,
    "w242_finalize_anchors": {"ledger_total": w242_total, "merged_n": w242_merged_n,
                               "skill_line_delta_k_lift": w242_klift},
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal, "bma_ordinal": bma_ordinal,
    "bma_ordinal_note": ("bm-a attempt-continuity: 124 live bm-a rows (tail=W242 registered+FINALIZED "
                          "bm-a r999 own-wave closeout: ledger 956,735 EXACT / merged pool K=530,320 / "
                          "skill_line 1.1934->1.1932 K-lift -0.0002 in-band) + this candidate = 125th owned; engine wave "
                          f"ordinal = {owner_total} registry owner rows + this candidate = 233rd; live derive governs r359"),
    "anchor": ("W241+W242 both registered+FINALIZED upstream (W241 bm-c closeout ledger 954,535 / K=528,120; "
               "W242 bm-a r999 closeout ledger 956,735 / K=530,320; n1_w242_results.json landed); "
               "ZERO in-flight upstream seats at seat time -- the W243 FREEZE is UNBLOCKED immediately "
               "(waits-upstream DISARMED by the W242 finalize landing 20:4x); this W243 SEAT = "
               "queue-depth supply depth-1 (first seat of the new supply cycle) per seat-first law "
               "O-20261010-2350 sec.2 (seats never queue behind freeze windows; standing CEO fill-order "
               "2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x + O-20261013 22:1x CPU standing-open + never-dry O-1819)")}
print(f"leg0: {len(N1_BANDS)} rows tail=W242-registered, W242 face=registry A={W242_A} B={W242_B}, owner={owner_total} -> 233rd wave candidate, bm-a 125th owned (continuity)")

# --- W243 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w243_seats = [ln for ln in all_inbox if "w243" in ln.lower() and "seat" in ln.lower()]
assert w243_seats == [], f"vacancy failed: W243 seats already exist: {w243_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '243: {"a": (' not in out_pf, "vacancy failed: W243 row ALREADY on origin (r511 tail-lock"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W243"' not in outn1_vac, "vacancy failed: W243 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W243_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W243 per-wave prereg ALREADY on origin"
print("vacancy: W243 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the W242 registered tails ------------------
ARITH_A = (W242_A[1] + 1, W242_A[1] + WIDTH_A)
ARITH_B = (W242_B[1] + 1, W242_B[1] + WIDTH_B)


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
b_trace = []
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace,
                             extra_bands=(fc_a,))
(fc_b_naive, hops_b_naive) = first_clean(ARITH_B[0], WIDTH_B)
assert fc_a[0] == ARITH_A[0], ("leg1 A refused at naive start (seed-decoupled clean continuation "
                                "anticipated by the W242 probe leg4 first-clean 551_501..553_500 "
                                "hops=0; never transcribe r587 -- re-read the live trace if this fires")
assert not overlaps(fc_a, W242_A) and not overlaps(fc_a, W242_B), \
    "leg1 failed: A overlaps prior-wave registered bands"
assert fc_a[0] >= W242_B[1] + 1, \
    "leg1 failed: A base must land at-or-after prior-wave B tail+1 (mutual exclusion floor)"
# B live-refusal face (W242 probe leg4 anticipation: hops=1 via a SEED_REGISTRY
# point inside the naive window). B base is NOT prior-wave B tail+1 EXACT in
# this face -- the honest forward walk governs; the hop chain is recorded and
# the refusal trace re-read live (never transcribed r587).
assert hops_b >= 1 and len(b_trace) >= 1, \
    "leg1 B unexpected zero-hop face (the W242 seat leg4 projected a live refusal inside the naive B window -- re-read the live trace; if the universe changed the honest walk governs and this assert must be re-derived honestly)"
assert fc_b[0] > W242_B[1], \
    "leg1 failed: B base must land above the prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: A/B overlap"
assert not overlaps(fc_b, W242_A) and not overlaps(fc_b, W242_B), \
    "leg1 failed: B overlaps prior-wave registered bands"
assert fc_b == fc_b_naive, "leg1 failed: B needed an own-A reservation jump (not expected on this universe; the refusal is a seed-point face, not an own-A face -- re-read trace if this fires)"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "A_semantics": ("A arithmetic continuation from the W242-REGISTERED A tail "
                    "551_500+1 = 551_501..553_500 is CLEAN at naive start on the "
                    "post-W242-REGISTERED universe (seed-decoupled A-continuation face, "
                    "fourth consecutive seed-gap face, anticipated by the W242 probe leg4 "
                    "and confirmed live; never transcribed r587); A base = first clean "
                    "window, forward-monotone non-rotational r587 enforced in-walk; "
                    "A base >= prior-wave B tail+1 floor machine-checkable relation"),
    "B_semantics": ("B arithmetic continuation from the W242-REGISTERED B tail "
                    "541_403+1 = 541_404..541_603 is REFUSED at the naive window by a live "
                    "SEED_REGISTRY seed point inside the window (live-seed refusal face, "
                    f"hops={hops_b}, hop chain recorded: {[(t['window'], t['jump_to'], t['refuser_pts']) for t in b_trace]}) -- "
                    "honest forward walk lands first-clean 541_501..541_700, which is NOT "
                    "inside the W243 own-wave A window 551_501..553_500 (own-A sits far "
                    "above the B staircase -- seed-decoupled gap face fifth consecutive); "
                    "B base != prior-wave B tail+1 EXACT in this face (live-seed hop) -- "
                    "the honest walk governs, B_no_ownA_jump=true (fc_b == fc_b_naive: no "
                    "own-A reservation jump needed)"),
    "relation_asserts": {"A_clean_at_naive_start": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_base_above_priorB_tail": True,
                          "B_live_seed_hop_face": True,
                          "AB_mutual_exclusion": True,
                          "B_no_ownA_jump": True}}
print(f"leg1: A {fc_a} hops={hops_a} (hop chain {[(t['window'], t['jump_to']) for t in a_trace]}) | B {fc_b} hops={hops_b} (refusal trace {[(t['window'], t['jump_to'], t['refuser_pts']) for t in b_trace]}) | naive B {fc_b_naive}")

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

# --- leg 4: W244+ naive projection (pre-W243 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W244p_A_naive": f"{pA[0]}..{pA[1]}", "W244p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W244p_A_naive_refusers_seeds": pA_refusers,
    "W244p_B_naive": f"{pB[0]}..{pB[1]}", "W244p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W244p_B_lands_inside_W244p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W244+ projection on the pre-W243 universe (assuming the W243 seat bands "
             "declared here register verbatim). W244 freezer MUST re-derive on the "
             "post-W243 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587; seed-gap face inherited from W239/W240/W241/W242: "
             "A/B decoupled, re-read the live trace, do NOT assume the staircase "
             "A-base==prior-B-tail+1 equality.")}
print(f"leg4: W244+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w243bma_20261014_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
