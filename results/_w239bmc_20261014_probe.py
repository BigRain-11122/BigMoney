# -*- coding: utf-8 -*-
"""W239 pre-seat probe (bm-c loop window r991, 2026-10-14 09:1x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20261013 22:1x
CPU standing-open order + O-20260924-1730 claim-ignite same-round law +
never-dry supply line O-1819 + O-20261010-2350-bm-c sec.2 seat-first law:
seats do NOT queue behind freeze windows and MUST NOT wait for the prior wave
to burn out -- queue depth is the physical guarantee of saturation.
Upstream face = W237 registered+FINALIZED (bm-c r990 own-wave estate-absorb
closeout: seat MSG-20261014-0654-bmc-w237-seat @ origin 9312ef7ac + prereg
d311a5439 + five-face splice e4a23cc7a + engine self-burn 12/12
38f6e6b87/d7fd42a62 + six-gate PRE-FINALIZE twelfth consecutive + finalize
one-pass landed + five-key ALL PASS _w237bmc_fivekey_receipt.json; ledger
942,989+2,200=945,189 EXACT, merged pool K=519,320 machine-read) AND W238 =
DECLARED seat (bm-a 07:45: seat MSG-20261014-0745-bma-w238-seat with ADMIT
receipt _w238bma_20261014_probe_receipt.json; W238 freeze unblocked
post-W237-finalize per finalize MSG-20261014-0855-bmc-w237-finalize, bm-a
freeze-prep chain in flight). This W239 seat IS the seat-first queue-depth
supply (depth 2: W238 declared + this candidate); the W239 FREEZE
waits-upstream on W238 finalize (physical dependency, seat MSG note; per the
W238 seat MSG leg4 mandate: re-derive on the post-W238-DECLARED universe AND
reserve the own-wave A window when deriving B, W141 precedent, never
transcribe r587).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W238-DECLARED
universe: registry keys + seed points + bands all live-imported, zero
hard-coded band values in the walk inputs; W238 prior-wave bands machine-read
from the frozen ADMIT receipt JSON (registry row when the bm-a splice has
landed, receipt face otherwise -- both live, zero transcription); NEW FACE
anticipated by the W238 seat MSG leg4: the W239 A walk hops PAST the
prior-wave B tail+1 (live SEED_REGISTRY refusers) -- the honest forward walk
governs, A base = first clean window at-or-after the naive continuation,
non-rotational r587 forward-monotone enforced in-walk.
Bloodline: _w238bma_20261014_probe.py derive machinery verbatim, W239 facts
live-registry/receipt-driven; dual-state leg0 (registry-first, receipt-face
fallback for the pending bm-a splice)."""
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
receipt = {"probe": "W239 pre-seat probe (bm-c loop r991 window, 2026-10-14 09:1x, CEO fill-order standing + seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + O-20261013-22:1x CPU standing-open; post-W238-DECLARED universe, upstream W237 registered+FINALIZED (bm-c r990) + W238 declared seat (bm-a 0745 MSG + ADMIT receipt, freeze chain in flight post-0855-finalize); W239 seat = queue-depth supply depth-2, freeze waits-upstream W238 finalize)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W237 landed face + W238 prior-wave declared face ---
keys = sorted(N1_BANDS)
w238_splice_landed = 238 in N1_BANDS
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \
    list(range(16, 239 if w238_splice_landed else 238))
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

# W237 finalize landed face (upstream for the bm-a W238 chain; W239 seat does NOT wait on it)
w237_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w237_results.json")
w237_fivekey = os.path.join(ROOT, "results", "_w237bmc_fivekey_receipt.json")
assert os.path.exists(w237_results), "leg0 failed: n1_w237_results.json absent (W237 finalize not landed)"
w237_fk = json.load(open(w237_fivekey, encoding="utf-8"))
assert w237_fk.get("five_keys_all_pass") is True, "leg0 failed: W237 five-key receipt five_keys_all_pass drift"

# W238 prior-wave bands: registry-first (bm-a five-face splice landed), receipt-face otherwise
w238_receipt = json.load(open(os.path.join(ROOT, "results",
                                            "_w238bma_20261014_probe_receipt.json"),
                               encoding="utf-8"))
assert w238_receipt.get("verdict") == "ADMIT", "leg0 failed: W238 ADMIT receipt verdict drift"
rc_bands = w238_receipt["bands"]
W238_A = (rc_bands["a_lo"], rc_bands["a_hi"])
W238_B = (rc_bands["b_lo"], rc_bands["b_hi"])
if w238_splice_landed:
    assert tuple(N1_BANDS[238]["a"]) == W238_A and \
        tuple(N1_BANDS[238]["b_exit"]) == W238_B, \
        "leg0 failed: registry W238 row != ADMIT receipt bands (two-faces drift)"
    assert N1_BANDS[238].get("engine_owner") == "bm-a", "leg0 failed: W238 engine_owner drift"
# staircase consistency of the prior-wave face vs the W237-registered tail (never transcribed r587)
assert W238_A[0] == W237_B[1] + 1, "leg0 failed: W238 A base != W237 B tail+1 (receipt face drift)"
assert W238_B[0] == W238_A[1] + 1, "leg0 failed: W238 B base != own-A tail+1 (receipt face drift)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
if w238_splice_landed:
    assert owner_total == 228 and len(bma_rows) == 122, \
        f"leg0 ordinal drift: owner={owner_total} bma={len(bma_rows)} (expect 228/122 post-W238-splice)"
else:
    assert owner_total == 227 and len(bma_rows) == 121, \
        f"leg0 ordinal drift: owner={owner_total} bma={len(bma_rows)} (expect 227/121 post-W237-registration per the r990 five-key receipt ordinal faces)"
assert len(bmc_rows) == 65, f"leg0 bmc ordinal drift: {len(bmc_rows)} (expect 65 post-W237-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"
ordinal = owner_total + (0 if w238_splice_landed else 1) + 1
assert ordinal == 229, f"leg0 ordinal derive: {ordinal} != 229"
bmc_ordinal = len(bmc_rows) + 1
assert bmc_ordinal == 66, f"leg0 bmc ordinal derive: {bmc_ordinal} != 66"

# W238 declared seat on origin (the queue-depth-1 face this W239 seat extends)
outseat238 = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
seat_hits = [ln for ln in outseat238.splitlines()
             if "w238" in ln.lower() and "seat" in ln.lower()]
assert seat_hits, "leg0 failed: W238 seat MSG not found on origin (declared face absent)"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W238-registered" if w238_splice_landed else "W237-registered (W238 splice pending)",
    "w238_splice_landed": w238_splice_landed,
    "w238_face": "registry-row" if w238_splice_landed else "ADMIT-receipt (declared, splice pending bm-a lane)",
    "w238_bands": {"A": list(W238_A), "B": list(W238_B)},
    "w237_finalize_landed": True,
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal, "bmc_ordinal": bmc_ordinal,
    "bmc_ordinal_note": ("bm-c attempt-continuity: 65 live bm-c rows (tail=W237 registered+FINALIZED "
                          "bm-c r990 own-wave estate-absorb closeout) + this candidate = 66th owned; engine wave "
                          f"ordinal = {owner_total} registry owner rows + W238 declared (bm-a 122nd, splice pending) "
                          "+ this candidate = 229th; live derive governs r359"),
    "anchor": ("W237 registered+FINALIZED upstream (finalize one-pass: ledger 945,189 / "
               "K=519,320 / five-key ALL PASS _w237bmc_fivekey_receipt.json; n1_w237_results.json "
               "landed; finalize MSG-20261014-0855-bmc-w237-finalize) + W238 declared seat (bm-a 0745 MSG + ADMIT "
               "receipt; freeze unblocked post-W237-finalize, bm-a chain in flight); this W239 SEAT does not wait "
               "for the W238 burn per seat-first law O-20261010-2350 sec.2 (queue-depth supply depth-2, "
               "禁等上一波烧完才占下一席); the W239 FREEZE waits-upstream on W238 finalize "
               "(physical dependency, seat MSG note + next-window watch armed)")}
print(f"leg0: {len(N1_BANDS)} rows tail={'W238-registered' if w238_splice_landed else 'W237-registered'}, W238 face={'registry' if w238_splice_landed else 'ADMIT-receipt'} A={W238_A} B={W238_B}, owner={owner_total} -> 229th wave candidate, bm-c 66th owned (continuity)")

# --- W239 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w239_seats = [ln for ln in all_inbox if "w239" in ln.lower() and "seat" in ln.lower()]
assert w239_seats == [], f"vacancy failed: W239 seats already exist: {w239_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '239: {"a": (' not in out_pf, "vacancy failed: W239 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W239"' not in outn1_vac, "vacancy failed: W239 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W239_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W239 per-wave prereg ALREADY on origin"
print("vacancy: W239 origin vacancy held (no seat / row / configs / prereg)")

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands.append(W238_A)
bands.append(W238_B)
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: honest forward walk from the W238 declared tails --------------------
ARITH_A = (W238_A[1] + 1, W238_A[1] + WIDTH_A)
ARITH_B = (W238_B[1] + 1, W238_B[1] + WIDTH_B)


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
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase A-hops-prior-B NINETY-NINTH "
                               "instance expected per the W238 seat MSG leg4 anticipation; "
                               "never transcribed r587)")
assert not overlaps(fc_a, W238_A) and not overlaps(fc_a, W238_B), \
    "leg1 failed: A overlaps prior-wave bands"
assert fc_a[0] >= W238_B[1] + 1, \
    "leg1 failed: A base must land at-or-after prior-wave B tail+1 (mutual exclusion floor)"
assert fc_b[0] == W238_B[1] + 1, \
    "leg1 failed: B base != prior-wave B tail+1 (seed-decoupled face: own-A hopped past the staircase base, B inherits it; re-read trace if refused)"
assert not overlaps(fc_b, fc_a), "leg1 failed: A/B overlap"
assert not overlaps(fc_b, W238_A) and not overlaps(fc_b, W238_B), \
    "leg1 failed: B overlaps prior-wave bands"
assert fc_b == fc_b_naive, "leg1 failed: B needed an own-A reservation jump (not expected on this universe; re-read trace)"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "A_semantics": ("A arithmetic continuation from the W238-DECLARED A tail REFUSED at start by "
                    "the W238 declared B band (staircase A-hops-prior-B NINETY-NINTH instance, E36 card, "
                    "per the W238 seat MSG leg4 anticipation; never transcribed r587) AND by live "
                    "SEED_REGISTRY points -- NEW FACE (first above the 538k registered tail): the honest "
                    "forward walk hops past the prior-wave B tail+1; A base = first clean window, "
                    "forward-monotone non-rotational r587 enforced in-walk"),
    "B_semantics": ("B arithmetic continuation from the W238-DECLARED B tail CLEAN on the "
                    "post-W238-DECLARED universe and NOT inside the W239 own-wave A window (own-A "
                    "seed-hopped past the staircase base -- first seed-decoupled A/B gap face); B "
                    "base == prior-wave B tail+1 machine-checkable; no own-A reservation jump needed "
                    "(fc_b == fc_b_naive)"),
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

# --- leg 4: W240+ naive projection (pre-W239 universe, honest forward face) -----
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W240p_A_naive": f"{pA[0]}..{pA[1]}", "W240p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W240p_A_naive_refusers_seeds": pA_refusers,
    "W240p_B_naive": f"{pB[0]}..{pB[1]}", "W240p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W240p_B_lands_inside_W240p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W240+ projection on the pre-W239 universe (assuming the W239 seat bands "
             "declared here register verbatim). W240 freezer MUST re-derive on the "
             "post-W239 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587; the registered W239 B band will refuse the "
             "naive W240 A window only if it overlaps (seed-gap face: W239 A/B are "
             "decoupled, re-read the live trace, do NOT assume the staircase "
             "A-base==prior-B-tail+1 equality).")}
print(f"leg4: W240+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w239bmc_20261014_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
