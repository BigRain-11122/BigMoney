# -*- coding: utf-8 -*-
"""W240 pre-seat probe (bm-a loop window r986, 2026-10-14 13:3x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20261013 22:1x
CPU standing-open order + O-20260924-1730 claim-ignite same-round law +
never-dry supply line O-1819 + O-20261010-2350-bm-c sec.2 seat-first law:
seats do NOT queue behind freeze windows and MUST NOT wait for the prior wave
to burn out -- queue depth is the physical guarantee of saturation.
Upstream face = W238 registered+FINALIZED (bm-a r985 own-wave closeout: seat
MSG-20261014-0745-bma-w238-seat + freeze splice r984 50fa77623 five-face
bands A 538_404..540_403 / B 540_404..540_603 + engine self-burn 12/12
delivered 12:44:04 zero kill-restart + six-gate PRE-FINALIZE thirteenth
consecutive + finalize one-pass ledger 945,735+2,200=947,935 EXACT / merged
pool K=521,520 + five-key ALL PASS _w238bma_fivekey_receipt.json + sec78
backfill + product n1_w238_results.json + finalize MSG-20261014-1255) AND
W239 = DECLARED seat (bm-c 09:14: seat MSG-20261014-0914-bmc-w239-seat with
ADMIT receipt _w239bmc_20261014_probe_receipt.json; W239 freeze unblocked
post-W238-finalize per finalize MSG-20261014-1255-bma-w238-finalize, waits-
upstream physical dependency DISARMED, bm-c freeze chain next). This W240
seat IS the seat-first queue-depth supply (depth 2: W239 declared + this
candidate); the W240 FREEZE waits-upstream on W239 finalize (physical
dependency, seat MSG note; per the W239 probe leg4 mandate: re-derive on the
post-W239-DECLARED universe AND reserve the own-wave A window when deriving
B, W141 precedent, never transcribe r587; seed-gap face: W239 A/B are
decoupled, do NOT assume the staircase A-base==prior-B-tail+1 equality).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W239-DECLARED
universe: registry keys + seed points + bands all live-imported, zero
hard-coded band values in the walk inputs; W239 prior-wave bands machine-read
from the frozen ADMIT receipt JSON (registry row when the bm-c splice has
landed, receipt face otherwise -- both live, zero transcription); NEW FACE
anticipated by the W239 probe leg4: the naive W240 A continuation is refused
by live SEED_REGISTRY point 545_500 above the registered tail (first
seed-refusal face in the post-540k region) -- the honest forward walk
governs, A base = first clean window at-or-after the naive continuation,
non-rotational r587 forward-monotone enforced in-walk.
Bloodline: _w239bmc_20261014_probe.py derive machinery verbatim, W240 facts
live-registry/receipt-driven; dual-state leg0 (registry-first, receipt-face
fallback for the pending bm-c splice)."""
import re
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
receipt = {"probe": "W240 pre-seat probe (bm-a loop r986 window, 2026-10-14 13:3x, CEO fill-order standing + seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + O-20261013-22:1x CPU standing-open; post-W239-DECLARED universe, upstream W238 registered+FINALIZED (bm-a r985) + W239 declared seat (bm-c 0914 MSG + ADMIT receipt, freeze chain unblocked post-1255-finalize); W240 seat = queue-depth supply depth-2, freeze waits-upstream W239 finalize)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W238 landed face + W239 prior-wave declared face ---
keys = sorted(N1_BANDS)
w239_splice_landed = 239 in N1_BANDS
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \
    list(range(16, 240 if w239_splice_landed else 239))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W236_A = tuple(N1_BANDS[236]["a"])
W236_B = tuple(N1_BANDS[236]["b_exit"])
assert W236_A == (534_004, 536_003) and W236_B == (536_004, 536_203) and \
    N1_BANDS[236].get("engine_owner") == "bm-a", "leg0 failed: W236 registry row drift"
W237_A = tuple(N1_BANDS[237]["a"])
W237_B = tuple(N1_BANDS[237]["b_exit"])
assert W237_A == (536_204, 538_203) and W237_B == (538_204, 538_403) and \
    N1_BANDS[237].get("engine_owner") == "bm-c", "leg0 failed: W237 registry row drift (bm-c r990 own-wave closeout face)"
assert W237_A[0] == W236_B[1] + 1, "leg0 failed: W237 A base != W236 B tail+1 (registry face drift)"
assert W237_B[0] == W237_A[1] + 1, "leg0 failed: W237 B base != own-A tail+1 (registry face drift)"
W238_A = tuple(N1_BANDS[238]["a"])
W238_B = tuple(N1_BANDS[238]["b_exit"])
assert W238_A == (538_404, 540_403) and W238_B == (540_404, 540_603) and \
    N1_BANDS[238].get("engine_owner") == "bm-a", "leg0 failed: W238 registry row drift (bm-a r985 own-wave closeout face)"
assert W238_A[0] == W237_B[1] + 1, "leg0 failed: W238 A base != W237 B tail+1 (registry face drift)"
assert W238_B[0] == W238_A[1] + 1, "leg0 failed: W238 B base != own-A tail+1 (registry face drift)"

# W238 finalize landed face (upstream for the bm-c W239 chain; W240 seat does NOT wait on it)
w238_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w238_results.json")
w238_fivekey = os.path.join(ROOT, "results", "_w238bma_fivekey_receipt.json")
assert os.path.exists(w238_results), "leg0 failed: n1_w238_results.json absent (W238 finalize not landed)"
w238_fk = json.load(open(w238_fivekey, encoding="utf-8"))
assert w238_fk.get("five_keys_all_pass") is True, "leg0 failed: W238 five-key receipt five_keys_all_pass drift"

# W239 prior-wave bands: registry-first (bm-c five-face splice landed), receipt-face otherwise
w239_receipt = json.load(open(os.path.join(ROOT, "results",
                                            "_w239bmc_20261014_probe_receipt.json"),
                               encoding="utf-8"))
assert w239_receipt.get("verdict") == "ADMIT", "leg0 failed: W239 ADMIT receipt verdict drift"
rc_bands = w239_receipt["bands"]
W239_A = (rc_bands["a_lo"], rc_bands["a_hi"])
W239_B = (rc_bands["b_lo"], rc_bands["b_hi"])
if w239_splice_landed:
    assert tuple(N1_BANDS[239]["a"]) == W239_A and \
        tuple(N1_BANDS[239]["b_exit"]) == W239_B, \
        "leg0 failed: registry W239 row != ADMIT receipt bands (two-faces drift)"
    assert N1_BANDS[239].get("engine_owner") == "bm-c", "leg0 failed: W239 engine_owner drift"
# consistency of the prior-wave face vs the W238-registered tail (never transcribed r587;
# seed-decoupled face per the W239 receipt leg1 relation_asserts: A base at-or-after the
# prior-wave B tail+1 floor, B base == prior-wave B tail+1)
assert W239_A[0] >= W238_B[1] + 1, "leg0 failed: W239 A base < W238 B tail+1 floor (receipt face drift)"
assert W239_B[0] == W238_B[1] + 1, "leg0 failed: W239 B base != W238 B tail+1 (receipt face drift)"
assert not overlaps(W239_A, W238_A) and not overlaps(W239_A, W238_B) and \
    not overlaps(W239_B, W238_A) and not overlaps(W239_B, W238_B) and \
    not overlaps(W239_A, W239_B), "leg0 failed: W239 declared bands overlap prior-wave or own bands"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
if w239_splice_landed:
    assert owner_total == 229 and len(bmc_rows) == 66, \
        f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 229/66 post-W239-splice)"
else:
    assert owner_total == 228 and len(bmc_rows) == 65, \
        f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 228/65 post-W238-registration per the r985 five-key receipt ordinal faces)"
assert len(bma_rows) == 122, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 122 post-W238-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"
ordinal = owner_total + (0 if w239_splice_landed else 1) + 1
assert ordinal == 230, f"leg0 ordinal derive: {ordinal} != 230"
bma_ordinal = len(bma_rows) + 1
assert bma_ordinal == 123, f"leg0 bma ordinal derive: {bma_ordinal} != 123"

# W239 declared seat on origin (the queue-depth-1 face this W240 seat extends)
outseat239 = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
seat_hits = [ln for ln in outseat239.splitlines()
             if "w239" in ln.lower() and "seat" in ln.lower()]
assert seat_hits, "leg0 failed: W239 seat MSG not found on origin (declared face absent)"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W239-registered" if w239_splice_landed else "W238-registered (W239 splice pending)",
    "w239_splice_landed": w239_splice_landed,
    "w239_face": "registry-row" if w239_splice_landed else "ADMIT-receipt (declared, splice pending bm-c lane)",
    "w239_bands": {"A": list(W239_A), "B": list(W239_B)},
    "w238_finalize_landed": True,
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal, "bma_ordinal": bma_ordinal,
    "bma_ordinal_note": ("bm-a attempt-continuity: 122 live bm-a rows (tail=W238 registered+FINALIZED "
                          "bm-a r985 own-wave closeout) + this candidate = 123rd owned; engine wave "
                          f"ordinal = {owner_total} registry owner rows + W239 declared (bm-c 66th, splice pending) "
                          "+ this candidate = 230th; live derive governs r359"),
    "anchor": ("W238 registered+FINALIZED upstream (finalize one-pass: ledger 947,935 / "
               "K=521,520 / five-key ALL PASS _w238bma_fivekey_receipt.json; n1_w238_results.json "
               "landed; finalize MSG-20261014-1255-bma-w238-finalize) + W239 declared seat (bm-c 0914 MSG + ADMIT "
               "receipt; freeze unblocked post-W238-finalize, bm-c chain next); this W240 SEAT does not wait "
               "for the W239 burn per seat-first law O-20261010-2350 sec.2 (queue-depth supply depth-2, "
               "禁等上一波烧完才占下一席); the W240 FREEZE waits-upstream on W239 finalize "
               "(physical dependency, seat MSG note + next-window watch armed)")}
print(f"leg0: {len(N1_BANDS)} rows tail={'W239-registered' if w239_splice_landed else 'W238-registered'}, W239 face={'registry' if w239_splice_landed else 'ADMIT-receipt'} A={W239_A} B={W239_B}, owner={owner_total} -> 230th wave candidate, bm-a 123rd owned (continuity)")

# --- W240 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w240_seats = [ln for ln in all_inbox if "w240" in ln.lower() and "seat" in ln.lower()]
assert w240_seats == [], f"vacancy failed: W240 seats already exist: {w240_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '240: {"a": (' not in out_pf, "vacancy failed: W240 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W240"' not in outn1_vac, "vacancy failed: W240 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W240_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W240 per-wave prereg ALREADY on origin"
print("vacancy: W240 origin vacancy held (no seat / row / configs / prereg)")

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands.append(W239_A)
bands.append(W239_B)
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: honest forward walk from the W239 declared tails --------------------
ARITH_A = (W239_A[1] + 1, W239_A[1] + WIDTH_A)
ARITH_B = (W239_B[1] + 1, W239_B[1] + WIDTH_B)


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
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (live SEED_REGISTRY refuser "
                               "545_500 anticipated by the W239 probe leg4 first-clean "
                               "545_501..547_500; never transcribe r587)")
assert not overlaps(fc_a, W239_A) and not overlaps(fc_a, W239_B), \
    "leg1 failed: A overlaps prior-wave declared bands"
assert fc_a[0] >= W239_B[1] + 1, \
    "leg1 failed: A base must land at-or-after prior-wave B tail+1 (mutual exclusion floor)"
assert fc_b[0] == W239_B[1] + 1, \
    "leg1 failed: B base != prior-wave B tail+1 (seed-decoupled face: own-A seed-hopped past the staircase base, B inherits it; re-read trace if refused)"
assert not overlaps(fc_b, fc_a), "leg1 failed: A/B overlap"
assert not overlaps(fc_b, W239_A) and not overlaps(fc_b, W239_B), \
    "leg1 failed: B overlaps prior-wave declared bands"
assert fc_b == fc_b_naive, "leg1 failed: B needed an own-A reservation jump (not expected on this universe; re-read trace)"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "A_semantics": ("A arithmetic continuation from the W239-DECLARED A tail REFUSED at start by "
                    "live SEED_REGISTRY point 545_500 (first seed-refusal face above the registered "
                    "tail, anticipated by the W239 probe leg4; never transcribed r587) -- NEW FACE "
                    "vs the W238 staircase: the refuser is a seed point, NOT the prior-wave B band "
                    "(W239 A/B are decoupled); the honest forward walk hops past the seed -> A base "
                    "= first clean window, forward-monotone non-rotational r587 enforced in-walk"),
    "B_semantics": ("B arithmetic continuation from the W239-DECLARED B tail CLEAN on the "
                    "post-W239-DECLARED universe and NOT inside the W240 own-wave A window (own-A "
                    "seed-hopped far above the decoupled gap); B base == prior-wave B tail+1 "
                    "machine-checkable; no own-A reservation jump needed (fc_b == fc_b_naive)"),
    "relation_asserts": {"A_base_ge_priorB_tail_plus1": True,
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

# --- leg 4: W241+ naive projection (pre-W240 universe, honest forward face) -----
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W241p_A_naive": f"{pA[0]}..{pA[1]}", "W241p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W241p_A_naive_refusers_seeds": pA_refusers,
    "W241p_B_naive": f"{pB[0]}..{pB[1]}", "W241p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W241p_B_lands_inside_W241p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W241+ projection on the pre-W240 universe (assuming the W240 seat bands "
             "declared here register verbatim). W241 freezer MUST re-derive on the "
             "post-W240 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587; the registered W240 B band will refuse the "
             "naive W241 A window only if it overlaps (seed-gap face inherited from "
             "W239: A/B decoupled, re-read the live trace, do NOT assume the staircase "
             "A-base==prior-B-tail+1 equality).")}
print(f"leg4: W241+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w240bma_20261014_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
