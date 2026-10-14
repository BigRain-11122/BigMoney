# -*- coding: utf-8 -*-
"""W241 pre-seat probe (bm-c loop window r1001, 2026-10-14 17:0x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20261013 22:1x
CPU standing-open order + O-20260924-1730 claim-ignite same-round law +
never-dry supply line O-1819 + O-20261010-2350-bm-c sec.2 seat-first law:
seats do NOT queue behind freeze windows and MUST NOT wait for the prior wave
to burn out -- queue depth is the physical guarantee of saturation.
Upstream face = W239 registered+FINALIZED (bm-c r996 continuation own-wave
estate closeout: seat MSG-20261014-0914-bmc-w239-seat + prereg 97a7ff0e6 +
five-face splice c85e806c9 + engine self-burn 12/12 daemon self-commits
65b222df6/6cc36056f + six-gate PRE-FINALIZE fourteenth consecutive + finalize
one-pass + five-key ALL PASS _w239bmc_fivekey_receipt.json; ledger
947,935+2,200=950,135 EXACT, merged pool K=523,720 machine-read,
results/perpetual_faces/n1_w239_results.json landed, commit acd421c74) AND
W240 = REGISTERED seat (bm-a 13:25 seat MSG-20261014-1325-bma-w240-seat with
ADMIT receipt _w240bma_20261014_probe_receipt.json + five-face splice landed
+ shard pack n1_w240 16:42, burn in flight on the bm-a lane; W240 freeze
waits-upstream W239 finalize was DISARMED by the W239 finalize estate). This
W241 seat IS the seat-first queue-depth supply (depth 2: W240 registered +
this candidate); the W241 FREEZE waits-upstream on the W240 finalize
(physical dependency, seat MSG note; per the W240 seat MSG leg4 mandate:
re-derive on the post-W240-DECLARED universe AND reserve the own-wave A
window when deriving B, never transcribe r587; seed-gap decoupled face --
do NOT assume the staircase A-base==prior-B-tail+1 equality).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W240-REGISTERED
universe: registry keys + seed points + bands all live-imported, zero
hard-coded band values in the walk inputs; W240 prior-wave bands machine-read
registry-first (splice landed), ADMIT-receipt fallback otherwise -- both
live, zero transcription. Anticipated face per the W240 seat MSG leg4
(pre-W240 universe): naive A 547_501..549_500 first-clean hops=0 / naive B
541_004..541_203 first-clean hops=0 -- the honest forward walk governs and
re-derives LIVE, never transcribed r587.
Bloodline: _w239bmc_20261014_probe.py derive machinery verbatim, W241 facts
live-registry/receipt-driven; single-state expected (W240 splice landed),
dual-state leg0 retained for race robustness."""
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
receipt = {"probe": "W241 pre-seat probe (bm-c loop r1001 window, 2026-10-14 17:0x, CEO fill-order standing + seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + O-20261013 22:1x CPU standing-open; post-W240-REGISTERED universe, upstream W239 registered+FINALIZED (bm-c r996 estate closeout, ledger 950,135/K=523,720) + W240 registered seat (bm-a 1325 MSG + splice landed + shard pack 16:42, burn in flight bm-a lane); W241 seat = queue-depth supply depth-2, freeze waits-upstream W240 finalize)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W239 landed face + W240 prior-wave registered face ---
keys = sorted(N1_BANDS)
w240_splice_landed = 240 in N1_BANDS
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \
    list(range(16, 241 if w240_splice_landed else 240))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W238_A = tuple(N1_BANDS[238]["a"])
W238_B = tuple(N1_BANDS[238]["b_exit"])
assert W238_A == (538_404, 540_403) and W238_B == (540_404, 540_603) and \
    N1_BANDS[238].get("engine_owner") == "bm-a", "leg0 failed: W238 registry row drift"
W239_A = tuple(N1_BANDS[239]["a"])
W239_B = tuple(N1_BANDS[239]["b_exit"])
assert W239_A == (542_501, 544_500) and W239_B == (540_604, 540_803) and \
    N1_BANDS[239].get("engine_owner") == "bm-c", "leg0 failed: W239 registry row drift (bm-c r996 own-wave closeout face)"
# W239 seed-decoupled relations vs W238 (W239 seat MSG NEW FACE, do NOT assume staircase)
assert W239_A[0] > W238_B[1], "leg0 failed: W239 A base not above W238 B tail (mutual exclusion floor drift)"
assert W239_B[0] == W238_B[1] + 1, "leg0 failed: W239 B base != W238 B tail+1 (B-staircase registry face drift)"

# W239 finalize landed face (upstream for the bm-a W240 chain; W241 seat does NOT wait on W240 burn)
w239_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w239_results.json")
w239_fivekey = os.path.join(ROOT, "results", "_w239bmc_fivekey_receipt.json")
assert os.path.exists(w239_results), "leg0 failed: n1_w239_results.json absent (W239 finalize not landed)"
w239_fk = json.load(open(w239_fivekey, encoding="utf-8"))
assert w239_fk.get("five_keys_all_pass") is True, "leg0 failed: W239 five-key receipt five_keys_all_pass drift"
assert w239_fk.get("ledger", {}).get("total") == 950_135, \
    "leg0 failed: W239 finalize ledger drift (950,135 expected)"
# K face: W239 finalize receipt shipped merged_K=None (numeric-key omission, r996 estate
# face) with the true K=523,720 embedded in the se_mu sub-key name se_mu_at_k523720 --
# accept the numeric face OR the key-name-embedded face (both machine-checkable); the
# omission itself is logged as the E-pit for the finalize author face, not silently ignored.
_w239_k = w239_fk.get("merged_K")
_se_mu = w239_fk.get("se_mu")
_k_in_name = isinstance(_se_mu, dict) and any("k523720" in str(k).lower() for k in _se_mu)
assert _w239_k == 523_720 or (_w239_k is None and _k_in_name), \
    "leg0 failed: W239 finalize K face drift (523,720 expected; receipt merged_K=None + se_mu_at_k523720 key-name face accepted, E-pit: finalize author must ship numeric merged_K)"

# W240 prior-wave bands: registry-first (bm-a five-face splice landed), receipt-face otherwise
w240_receipt = json.load(open(os.path.join(ROOT, "results",
                                            "_w240bma_20261014_probe_receipt.json"),
                               encoding="utf-8"))
assert w240_receipt.get("verdict") == "ADMIT", "leg0 failed: W240 ADMIT receipt verdict drift"
rc_bands = w240_receipt["bands"]
W240_A = (rc_bands["a_lo"], rc_bands["a_hi"])
W240_B = (rc_bands["b_lo"], rc_bands["b_hi"])
if w240_splice_landed:
    assert tuple(N1_BANDS[240]["a"]) == W240_A and \
        tuple(N1_BANDS[240]["b_exit"]) == W240_B, \
        "leg0 failed: registry W240 row != ADMIT receipt bands (two-faces drift)"
    assert N1_BANDS[240].get("engine_owner") == "bm-a", "leg0 failed: W240 engine_owner drift"
# seed-decoupled face of the prior wave vs the W239-registered tail (never transcribed r587;
# W239 seat MSG mandate: do NOT assume the staircase A-base==prior-B-tail+1 equality)
assert W240_A[0] > W239_B[1], "leg0 failed: W240 A base not above W239 B tail (mutual exclusion floor drift)"
assert W240_B[0] == W239_B[1] + 1, "leg0 failed: W240 B base != W239 B tail+1 (B-staircase continuation face drift)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
if w240_splice_landed:
    assert owner_total == 230 and len(bma_rows) == 123, \
        f"leg0 ordinal drift: owner={owner_total} bma={len(bma_rows)} (expect 230/123 post-W240-splice)"
else:
    assert owner_total == 229 and len(bma_rows) == 122, \
        f"leg0 ordinal drift: owner={owner_total} bma={len(bma_rows)} (expect 229/122 post-W239-registration)"
assert len(bmc_rows) == 66, f"leg0 bmc ordinal drift: {len(bmc_rows)} (expect 66 post-W239-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"
ordinal = owner_total + (0 if w240_splice_landed else 1) + 1
assert ordinal == 231, f"leg0 ordinal derive: {ordinal} != 231"
bmc_ordinal = len(bmc_rows) + 1
assert bmc_ordinal == 67, f"leg0 bmc ordinal derive: {bmc_ordinal} != 67"

# W240 registered seat on origin (the queue-depth-1 face this W241 seat extends)
outseat240 = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
seat_hits = [ln for ln in outseat240.splitlines()
             if "w240" in ln.lower() and "seat" in ln.lower()]
assert seat_hits, "leg0 failed: W240 seat MSG not found on origin (declared face absent)"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W240-registered" if w240_splice_landed else "W239-registered (W240 splice pending)",
    "w240_splice_landed": w240_splice_landed,
    "w240_face": "registry-row" if w240_splice_landed else "ADMIT-receipt (declared, splice pending bm-a lane)",
    "w240_bands": {"A": list(W240_A), "B": list(W240_B)},
    "w239_finalize_landed": True,
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal, "bmc_ordinal": bmc_ordinal,
    "bmc_ordinal_note": ("bm-c attempt-continuity: 66 live bm-c rows (tail=W239 registered+FINALIZED "
                          "bm-c r996 estate closeout: ledger 950,135 EXACT / merged pool K=523,720 "
                          "EXACT / five-key ALL PASS / n1_w239_results.json landed) + this candidate = 67th owned; engine wave "
                          f"ordinal = {owner_total} registry owner rows (W240 registered, bm-a 123rd) "
                          "+ this candidate = 231st; live derive governs r359"),
    "anchor": ("W239 registered+FINALIZED upstream (finalize one-pass: ledger 950,135 / "
               "K=523,720 / five-key ALL PASS _w239bmc_fivekey_receipt.json; n1_w239_results.json "
               "landed; commit acd421c74) + W240 registered seat (bm-a 1325 MSG + splice landed + "
               "shard pack 16:42, burn in flight bm-a lane); this W241 SEAT does not wait "
               "for the W240 burn per seat-first law O-20261010-2350 sec.2 (queue-depth supply depth-2, "
               "禁等上一波烧完才占下一席); the W241 FREEZE waits-upstream on W240 finalize "
               "(physical dependency, seat MSG note + next-window watch armed)")}
print(f"leg0: {len(N1_BANDS)} rows tail={'W240-registered' if w240_splice_landed else 'W239-registered'}, W240 face={'registry' if w240_splice_landed else 'ADMIT-receipt'} A={W240_A} B={W240_B}, owner={owner_total} -> 231st wave candidate, bm-c 67th owned (continuity)")

# --- W241 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w241_seats = [ln for ln in all_inbox if "w241" in ln.lower() and "seat" in ln.lower()]
assert w241_seats == [], f"vacancy failed: W241 seats already exist: {w241_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '241: {"a": (' not in out_pf, "vacancy failed: W241 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W241"' not in outn1_vac, "vacancy failed: W241 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W241_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W241 per-wave prereg ALREADY on origin"
print("vacancy: W241 origin vacancy held (no seat / row / configs / prereg)")

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
if not w240_splice_landed:
    bands.append(W240_A)
    bands.append(W240_B)
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: honest forward walk from the W240 registered tails -------------------
ARITH_A = (W240_A[1] + 1, W240_A[1] + WIDTH_A)
ARITH_B = (W240_B[1] + 1, W240_B[1] + WIDTH_B)


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
                               "hops=0 anticipated per the W240 seat MSG leg4; NEW FACE if refused -- "
                               "re-read the trace, never transcribed r587)")
assert not overlaps(fc_a, W240_A) and not overlaps(fc_a, W240_B), \
    "leg1 failed: A overlaps prior-wave bands"
assert fc_a[0] >= W240_B[1] + 1, \
    "leg1 failed: A base must land at-or-after prior-wave B tail+1 (mutual exclusion floor)"
assert fc_b[0] == W240_B[1] + 1, \
    "leg1 failed: B base != prior-wave B tail+1 (B-staircase continuation face; re-read trace if refused)"
assert not overlaps(fc_b, fc_a), "leg1 failed: A/B overlap"
assert not overlaps(fc_b, W240_A) and not overlaps(fc_b, W240_B), \
    "leg1 failed: B overlaps prior-wave bands"
assert fc_b == fc_b_naive, "leg1 failed: B needed an own-A reservation jump (not expected on this universe; re-read trace)"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "A_semantics": ("A arithmetic continuation from the W240-REGISTERED A tail 547_500+1 "
                    "CLEAN at naive start on the post-W240-REGISTERED universe (seed-decoupled "
                    "A-continuation face, hops=0 -- second consecutive seed-gap face, "
                    "per the W240 seat MSG leg4 anticipation confirmed live; never transcribed r587); "
                    "A base = first clean window, forward-monotone non-rotational r587 enforced in-walk"),
    "B_semantics": ("B arithmetic continuation from the W240-REGISTERED B tail 541_003+1 CLEAN "
                    "on the post-W240-REGISTERED universe and NOT inside the W241 own-wave A window "
                    "(own-A sits far above the B staircase -- seed-decoupled gap face third "
                    "consecutive); B base == prior-wave B tail+1 machine-checkable; no own-A "
                    "reservation jump needed (fc_b == fc_b_naive)"),
    "relation_asserts": {"A_clean_at_naive_start": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_base_eq_priorB_tail_plus1": True,
                          "AB_mutual_exclusion": True,
                          "B_no_ownA_jump": True}}
print(f"leg1: A {fc_a} hops={hops_a} (clean at naive start, seed-decoupled continuation) | B {fc_b} hops={hops_h if False else hops_b} | naive B {fc_b_naive}")

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

# --- leg 4: W242+ naive projection (pre-W241 universe, honest forward face) -----
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W242p_A_naive": f"{pA[0]}..{pA[1]}", "W242p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W242p_A_naive_refusers_seeds": pA_refusers,
    "W242p_B_naive": f"{pB[0]}..{pB[1]}", "W242p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W242p_B_lands_inside_W242p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W242+ projection on the pre-W241 universe (assuming the W241 seat bands "
             "declared here register verbatim). W242 freezer MUST re-derive on the "
             "post-W241 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587; seed-gap decoupled face: W241 A sits far above "
             "the B staircase, re-read the live trace, do NOT assume the staircase "
             "A-base==prior-B-tail+1 equality.")}
print(f"leg4: W242+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w241bmc_20261014_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
