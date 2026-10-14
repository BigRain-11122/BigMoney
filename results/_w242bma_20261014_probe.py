# -*- coding: utf-8 -*-
"""W242 pre-seat probe (bm-a loop window r995, 2026-10-14 18:0x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20261013 22:1x
CPU standing-open order + O-20260924-1730 claim-ignite same-round law +
never-dry supply line O-1819 + O-20261010-2350-bm-c sec.2 seat-first law:
seats do NOT queue behind freeze windows and MUST NOT wait for the prior wave
to burn out -- queue depth is the physical guarantee of saturation.
Upstream face = W240 registered+FINALIZED (bm-a r993 own-wave closeout: seat
MSG-20261014-1325-bma-w240-seat + freeze splice dc27f5217 five-face bands
A 545_501..547_500 / B 540_804..541_003 + engine self-burn 12/12 + six-gate
PRE-FINALIZE fourteenth consecutive + finalize one-pass ledger
950,135+2,200=952,335 EXACT / merged pool K=525,920 + five-key ALL PASS
_w240bma_fivekey_receipt.json + sec78 backfill + product n1_w240_results.json)
AND W241 = DECLARED seat (bm-c 17:55: seat MSG-20261014-1755-bmc-w241-seat
with ADMIT receipt _w241bmc_20261014_probe_receipt.json bands
A 547_501..549_500 / B 541_004..541_203; W241 freeze unblocked
post-W240-finalize per the finalize landing 17:09:55, bm-c chain next per
seat-first law O-20261011-0012 sec.ii). This W242 seat IS the seat-first
queue-depth supply (depth 2: W241 declared + this candidate); the W242
FREEZE waits-upstream on the W241 finalize (physical dependency, seat MSG
note; per the W241 probe leg4 mandate: re-derive on the post-W241-DECLARED
universe AND reserve the own-wave A window when deriving B, W141 precedent,
never transcribe r587; seed-gap face inherited: W241 A/B are decoupled, do
NOT assume the staircase A-base==prior-B-tail+1 equality).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W241-DECLARED
universe: registry keys + seed points + bands all live-imported, zero
hard-coded band values in the walk inputs; W241 prior-wave bands machine-read
from the frozen ADMIT receipt JSON (registry row when the bm-c splice has
landed, receipt face otherwise -- both live, zero transcription); face
anticipated by the W241 probe leg4: naive W242 A continuation 549_501..551_500
first-clean hops=0 (no live refusers) / naive B 541_204..541_403 first-clean
hops=0 NOT inside own-A -- honest forward walk governs either way,
non-rotational r587 forward-monotone enforced in-walk.
Bloodline: _w240bma_20261014_probe.py derive machinery verbatim (W241
assert style for the clean-continuation face), W242 facts
live-registry/receipt-driven; dual-state leg0 (registry-first, receipt-face
fallback for the pending bm-c splice)."""
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
receipt = {"probe": "W242 pre-seat probe (bm-a loop r995 window, 2026-10-14 18:0x, CEO fill-order standing + seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + O-20261013-22:1x CPU standing-open; post-W241-DECLARED universe, upstream W240 registered+FINALIZED (bm-a r993) + W241 declared seat (bm-c 17:55 MSG + ADMIT receipt, freeze chain unblocked post-W240-finalize-17:09:55); W242 seat = queue-depth supply depth-2, freeze waits-upstream W241 finalize)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W240 landed face + W241 prior-wave declared face ---
keys = sorted(N1_BANDS)
w241_splice_landed = 241 in N1_BANDS
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \
    list(range(16, 242 if w241_splice_landed else 241))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W238_A = tuple(N1_BANDS[238]["a"])
W238_B = tuple(N1_BANDS[238]["b_exit"])
assert W238_A == (538_404, 540_403) and W238_B == (540_404, 540_603) and \
    N1_BANDS[238].get("engine_owner") == "bm-a", "leg0 failed: W238 registry row drift"
W239_A = tuple(N1_BANDS[239]["a"])
W239_B = tuple(N1_BANDS[239]["b_exit"])
assert W239_A == (542_501, 544_500) and W239_B == (540_604, 540_803) and \
    N1_BANDS[239].get("engine_owner") == "bm-c", "leg0 failed: W239 registry row drift (bm-c r996 estate closeout face)"
assert W239_B[0] == W238_B[1] + 1, "leg0 failed: W239 B base != W238 B tail+1 (registry face drift)"
assert W239_A[0] >= W238_B[1] + 1, "leg0 failed: W239 A base below W238 B tail+1 floor (seed-gap face check)"
W240_A = tuple(N1_BANDS[240]["a"])
W240_B = tuple(N1_BANDS[240]["b_exit"])
assert W240_A == (545_501, 547_500) and W240_B == (540_804, 541_003) and \
    N1_BANDS[240].get("engine_owner") == "bm-a", "leg0 failed: W240 registry row drift (bm-a r992 splice + r993 finalize face)"
assert W240_B[0] == W239_B[1] + 1, "leg0 failed: W240 B base != W239 B tail+1 (registry face drift)"
assert W240_A[0] >= W239_B[1] + 1, "leg0 failed: W240 A base below W239 B tail+1 floor"

# W240 finalize landed face (upstream for the bm-c W241 chain; W242 seat does NOT wait on it)
w240_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w240_results.json")
w240_fivekey = os.path.join(ROOT, "results", "_w240bma_fivekey_receipt.json")
assert os.path.exists(w240_results), "leg0 failed: n1_w240_results.json absent (W240 finalize not landed)"
w240_fk = json.load(open(w240_fivekey, encoding="utf-8"))
assert w240_fk.get("five_keys_all_pass") is True, "leg0 failed: W240 five-key receipt five_keys_all_pass drift"

# W241 prior-wave bands: registry-first (bm-c five-face splice landed), receipt-face otherwise
w241_receipt = json.load(open(os.path.join(ROOT, "results",
                                            "_w241bmc_20261014_probe_receipt.json"),
                               encoding="utf-8"))
assert w241_receipt.get("verdict") == "ADMIT", "leg0 failed: W241 ADMIT receipt verdict drift"
rc_bands = w241_receipt["bands"]
W241_A = (rc_bands["a_lo"], rc_bands["a_hi"])
W241_B = (rc_bands["b_lo"], rc_bands["b_hi"])
if w241_splice_landed:
    assert tuple(N1_BANDS[241]["a"]) == W241_A and \
        tuple(N1_BANDS[241]["b_exit"]) == W241_B, \
        "leg0 failed: registry W241 row != ADMIT receipt bands (two-faces drift)"
    assert N1_BANDS[241].get("engine_owner") == "bm-c", "leg0 failed: W241 engine_owner drift"
# consistency of the prior-wave face vs the W240-registered tail (never transcribed r587;
# seed-decoupled face per the W241 receipt leg1 relation_asserts: A base at-or-after the
# prior-wave B tail+1 floor, B base == prior-wave B tail+1)
assert W241_A[0] >= W240_B[1] + 1, "leg0 failed: W241 A base < W240 B tail+1 floor (receipt face drift)"
assert W241_B[0] == W240_B[1] + 1, "leg0 failed: W241 B base != W240 B tail+1 (receipt face drift)"
assert not overlaps(W241_A, W240_A) and not overlaps(W241_A, W240_B) and \
    not overlaps(W241_B, W240_A) and not overlaps(W241_B, W240_B) and \
    not overlaps(W241_A, W241_B), "leg0 failed: W241 declared bands overlap prior-wave or own bands"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
if w241_splice_landed:
    assert owner_total == 231 and len(bmc_rows) == 67, \
        f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 231/67 post-W241-splice)"
    ordinal = owner_total + 1
else:
    assert owner_total == 230 and len(bmc_rows) == 66, \
        f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 230/66 post-W240-registration per the r993 five-key receipt ordinal faces)"
    ordinal = owner_total + 2  # W241 declared candidate + this candidate
assert ordinal == 232, f"leg0 ordinal derive: {ordinal} != 232"
assert len(bma_rows) == 123, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 123 post-W240-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"
bma_ordinal = len(bma_rows) + 1
assert bma_ordinal == 124, f"leg0 bma ordinal derive: {bma_ordinal} != 124"

# W241 declared seat on origin (the queue-depth-1 face this W242 seat extends)
outseat241 = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
seat_hits = [ln for ln in outseat241.splitlines()
             if "w241" in ln.lower() and "seat" in ln.lower()]
assert seat_hits, "leg0 failed: W241 seat MSG not found on origin (declared face absent)"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W241-registered" if w241_splice_landed else "W240-registered (W241 splice pending)",
    "w241_splice_landed": w241_splice_landed,
    "w241_face": "registry-row" if w241_splice_landed else "ADMIT-receipt (declared, splice pending bm-c lane)",
    "w241_bands": {"A": list(W241_A), "B": list(W241_B)},
    "w240_finalize_landed": True,
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal, "bma_ordinal": bma_ordinal,
    "bma_ordinal_note": ("bm-a attempt-continuity: 123 live bm-a rows (tail=W240 registered+FINALIZED "
                          "bm-a r993 own-wave closeout: ledger 952,335 EXACT / merged pool K=525,920 / "
                          "five-key ALL PASS) + this candidate = 124th owned; engine wave "
                          f"ordinal = {owner_total} registry owner rows + W241 declared (bm-c 67th, splice pending) "
                          "+ this candidate = 232nd; live derive governs r359"),
    "anchor": ("W240 registered+FINALIZED upstream (finalize one-pass: ledger 952,335 / "
               "K=525,920 / five-key ALL PASS _w240bma_fivekey_receipt.json; n1_w240_results.json "
               "landed; bm-a r993 closeout) + W241 declared seat (bm-c 17:55 MSG + ADMIT "
               "receipt; freeze unblocked post-W240-finalize, bm-c chain next per seat-first law "
               "O-20261011-0012 sec.ii); this W242 SEAT does not wait "
               "for the W241 burn per seat-first law O-20261010-2350 sec.2 (queue-depth supply depth-2, "
               "seats never queue behind freeze windows); the W242 FREEZE waits-upstream on W241 finalize "
               "(physical dependency, seat MSG note + next-window watch armed)")}
print(f"leg0: {len(N1_BANDS)} rows tail={'W241-registered' if w241_splice_landed else 'W240-registered'}, W241 face={'registry' if w241_splice_landed else 'ADMIT-receipt'} A={W241_A} B={W241_B}, owner={owner_total} -> 232nd wave candidate, bm-a 124th owned (continuity)")

# --- W242 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w242_seats = [ln for ln in all_inbox if "w242" in ln.lower() and "seat" in ln.lower()]
assert w242_seats == [], f"vacancy failed: W242 seats already exist: {w242_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '242: {"a": (' not in out_pf, "vacancy failed: W242 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W242"' not in outn1_vac, "vacancy failed: W242 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W242_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W242 per-wave prereg ALREADY on origin"
print("vacancy: W242 origin vacancy held (no seat / row / configs / prereg)")

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands.append(W241_A)
bands.append(W241_B)
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: honest forward walk from the W241 declared tails --------------------
ARITH_A = (W241_A[1] + 1, W241_A[1] + WIDTH_A)
ARITH_B = (W241_B[1] + 1, W241_B[1] + WIDTH_B)


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
                                "anticipated by the W241 probe leg4 first-clean 549_501..551_500 "
                                "hops=0; never transcribe r587 -- re-read the live trace if this fires")
assert not overlaps(fc_a, W241_A) and not overlaps(fc_a, W241_B), \
    "leg1 failed: A overlaps prior-wave declared bands"
assert fc_a[0] >= W241_B[1] + 1, \
    "leg1 failed: A base must land at-or-after prior-wave B tail+1 (mutual exclusion floor)"
assert fc_b[0] == W241_B[1] + 1, \
    "leg1 failed: B base != prior-wave B tail+1 (seed-decoupled face: own-A sits far above the staircase base, B inherits it; re-read trace if refused)"
assert not overlaps(fc_b, fc_a), "leg1 failed: A/B overlap"
assert not overlaps(fc_b, W241_A) and not overlaps(fc_b, W241_B), \
    "leg1 failed: B overlaps prior-wave declared bands"
assert fc_b == fc_b_naive, "leg1 failed: B needed an own-A reservation jump (not expected on this universe; re-read trace)"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "A_semantics": ("A arithmetic continuation from the W241-DECLARED A tail "
                    "549_500+1 = 549_501..551_500 is CLEAN at naive start on the "
                    "post-W241-DECLARED universe (seed-decoupled A-continuation face, "
                    "third consecutive seed-gap face, anticipated by the W241 probe leg4 "
                    "and confirmed live; never transcribed r587); A base = first clean "
                    "window, forward-monotone non-rotational r587 enforced in-walk; "
                    "A base >= prior-wave B tail+1 floor machine-checkable relation"),
    "B_semantics": ("B arithmetic continuation from the W241-DECLARED B tail "
                    "541_203+1 = 541_204..541_403 is CLEAN on the post-W241-DECLARED "
                    "universe and NOT inside the W242 own-wave A window 549_501..551_500 "
                    "(own-A sits far above the B staircase -- seed-decoupled gap face "
                    "fourth consecutive); B base == prior-wave B tail+1 machine-checkable; "
                    "no own-A reservation jump needed (fc_b == fc_b_naive)"),
    "relation_asserts": {"A_clean_at_naive_start": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_base_eq_priorB_tail_plus1": True,
                          "AB_mutual_exclusion": True,
                          "B_no_ownA_jump": True}}
print(f"leg1: A {fc_a} hops={hops_a} (seed-hop chain {[(t['window'], t['jump_to']) for t in a_trace]}) | B {fc_b} hops={hops_b} | naive B {fc_b_naive}")

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

# --- leg 4: W243+ naive projection (pre-W242 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W243p_A_naive": f"{pA[0]}..{pA[1]}", "W243p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W243p_A_naive_refusers_seeds": pA_refusers,
    "W243p_B_naive": f"{pB[0]}..{pB[1]}", "W243p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W243p_B_lands_inside_W243p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W243+ projection on the pre-W242 universe (assuming the W242 seat bands "
             "declared here register verbatim). W243 freezer MUST re-derive on the "
             "post-W242 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587; seed-gap face inherited from W239/W240/W241: "
             "A/B decoupled, re-read the live trace, do NOT assume the staircase "
             "A-base==prior-B-tail+1 equality.")}
print(f"leg4: W243+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w242bma_20261014_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
