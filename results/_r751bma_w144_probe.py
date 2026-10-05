# -*- coding: utf-8 -*-
"""r751 bm-a W144 pre-seat probe -- read-only band derivation before the
seat MSG publication (r565 early-visibility law: seat published=reserved
BEFORE the freeze commit; the seat must carry the machine-derived bands).

W144 candidate = first FREE number after the REGISTERED W143 row (bm-a
r750 freeze 86d3b070c; W143 finalize landed same-window r751 one-pass
6d93bd7ba, ledger head 710,611, merged pool K=312,520).
Derivation faces (STAIRCASE GEOMETRY third instance, W141 precedent
leg2 law + E36 card: A hops past prior B, B hops past own A):
  A  arithmetic continuation from the registered W143 A tail 331_403 + 1,
     stride 2_000 -> 331_404..333_403 REFUSED (the registered W143 B band
     331_404..331_603 sits exactly at the arithmetic start -- the r750
     W143 gate leg3 projection note anticipated this refusal: "the
     registered W143 B band 331_404..331_603 will refuse the naive W144
     A window (staircase A-hops-prior-B)"). Honest forward walk hops past
     the W143 B band -> first-clean 331_604..333_603, hops=1; A base ==
     prior-wave B tail+1 (331_603+1) machine-checkable (A-hops-prior-B
     staircase third instance; non-rotational r587 forward-monotone
     assert enforced in-walk).
  B  arithmetic continuation from the registered W143 B tail 331_603 + 1,
     stride 200 -> 331_604..331_803 CLEAN on the registered universe
     (zero registered conflicts; r750 W143 gate leg3 projected this
     window CLEAN) but the naive first-clean lands INSIDE the W144
     own-wave A window 331_604..333_603 -- same-freeze mutual exclusion
     (W141 precedent, leg2 law). The walk WITH the own-wave A window
     reserved jumps to 333_604 -> first-clean 333_604..333_803, hops=1;
     B base == own-wave A tail+1 (333_603+1) machine-checkable.
This honors the r750 W143 gate leg3 mandatory note verbatim: "W144
freezer MUST re-derive (r587) and MUST apply the same-freeze mutual
exclusion: reserve the W144 own-wave A window when deriving B (W141
precedent, leg2 law, E36 card)" -- both obligations honored here,
re-derived never transcribed (r587).
Machine-verified against: all registered N1 wave bands (W2..W14,
W16..W143), N3-R1 used-seed band, probe cluster 95_000..95_003 (r335 leg),
cross-face probe points 95_004/95_006 (r602 leg), v1 in-use + W1 ext bands,
SEED_REGISTRY live values, N2/N4 probe points, N2-W15 draft probe points,
lfc/options actual draw ranges.
Bloodline: r750 _r750bma_w143_probe.py verbatim + W144 facts + staircase
A-hops-prior-B third instance (E36 card).
"""
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
W143_A_TAIL = 331_403
W143_B_TAIL = 331_603
WIDTH_A = 2_000
WIDTH_B = 200

N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
assert PROBE_SEEDS == (95_000, 95_001, 95_002, 95_003), \
    "refusal-facts identity drift (r335 law: probe cluster frozen)"
CROSSFACE_PROBE_POINTS = (95_004, 95_006)
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
receipt = {"probe": "r751 W144 pre-seat probe", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

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

# --- leg 0: registry shape (single state: W143 registered, tail=W143) ---------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 144))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert N1_BANDS[143]["a"] == (329_404, W143_A_TAIL) and \
    N1_BANDS[143]["b_exit"] == (331_404, W143_B_TAIL) and \
    N1_BANDS[143].get("engine_owner") == "bm-a", "leg0 failed: W143 row drift"
assert N1_BANDS[142]["a"] == (327_204, 329_203) and \
    N1_BANDS[142]["b_exit"] == (329_204, 329_403) and \
    N1_BANDS[142].get("engine_owner") == "bm-a", "leg0 failed: W142 row drift"
assert N1_BANDS[141]["a"] == (325_004, 327_003) and \
    N1_BANDS[141]["b_exit"] == (327_004, 327_203) and \
    N1_BANDS[141].get("engine_owner") == "bm-a", "leg0 failed: W141 row drift"
MODE = ("B144 (registered W143, bm-a r750 freeze 86d3b070c; W143 finalize "
        "landed same-window r751 one-pass 6d93bd7ba, ledger head 710,611, "
        "merged pool K=312,520)")
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-a "
      f"rows={len(bma_rows)} -> W144 = bm-a "
      f"{len(bma_rows) + 1}th owned; W144 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")
assert len(owner_rows) == 133 and len(bma_rows) == 59, "leg0 ordinal drift"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W143",
                           "owner_rows": len(owner_rows),
                           "bma_rows": len(bma_rows),
                           "ordinal": 134, "bma_ordinal": 60}

# --- leg 1: honest forward walk from the registered W143 tails ----------------
ARITH_A = (W143_A_TAIL + 1, W143_A_TAIL + WIDTH_A)
ARITH_B = (W143_B_TAIL + 1, W143_B_TAIL + WIDTH_B)
assert ARITH_A == (331_404, 333_403), f"leg1-A drift: {ARITH_A}"
assert ARITH_B == (331_604, 331_803), f"leg1-B drift: {ARITH_B}"


def refusal_facts(band):
    facts = []
    for p in sorted(points):
        if band[0] <= p <= band[1]:
            who = [k for k, v in science_gates.SEED_REGISTRY.items() if v == p]
            facts.append((p, who[0] if who else "probe/actual point"))
    for b in bands + actual:
        if overlaps(b, band):
            facts.append((b, "registered band/actual"))
    return facts


def first_clean(lo, width, trace=None, extra_bands=()):
    """First clean window at/after lo; pinned D-20261002-05 past-hit
    restart semantics (lo jumps past the refusing point/band, law sec.4).
    r587 non-rotational face: per-hop trace + strict forward-monotone assert.
    extra_bands: same-freeze reserved windows (own-wave A mutual exclusion)."""
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
            who = []
            for p in sorted(bad_pts):
                k = [kk for kk, v in science_gates.SEED_REGISTRY.items() if v == p]
                who.append(f"{p}({k[0] if k else 'probe/actual-point'})")
            for b in bad_bands:
                tag = "own-wave-A(same-freeze-mutual-exclusion)" if b in extra_bands \
                    else "registered band/actual"
                who.append(f"band{b[0]}..{b[1]}({tag})")
            trace.append({"hop": hops + 1, "window": [lo, hi],
                          "refusers": who, "jump_to": jump})
        lo = jump
        prev_lo = lo
        hops += 1


fA = refusal_facts(ARITH_A)
fB = refusal_facts(ARITH_B)
assert fA, "leg1-A arithmetic window unexpectedly CLEAN (W143 B band moved?)"
assert not fB, f"leg1-B arithmetic window REFUSED on registered universe: {fB}"
a_trace = []
(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A, trace=a_trace)
# naive B walk (registered universe only) -- lands inside the own-wave A window
(fc_b_naive, hops_b_naive) = first_clean(ARITH_B[0], WIDTH_B)
print(f"leg1: A arithmetic {ARITH_A[0]}..{ARITH_A[1]} "
      f"{'CLEAN' if not fA else 'REFUSED'} -> first-clean "
      f"{fc_a[0]}..{fc_a[1]} hops={hops_a}")
print(f"leg1: B arithmetic {ARITH_B[0]}..{ARITH_B[1]} CLEAN on registered "
      f"universe -> naive first-clean {fc_b_naive[0]}..{fc_b_naive[1]} "
      f"hops={hops_b_naive} "
      f"(INSIDE own-wave A window {fc_a[0]}..{fc_a[1]} -> mutual exclusion)")
assert (fc_a, hops_a) == ((331_604, 333_603), 1), \
    f"leg1-A derive drift: {fc_a} hops={hops_a}"
assert a_trace and a_trace[0]["jump_to"] == 331_604, "leg1-A hop chain drift"
assert fc_a[0] == W143_B_TAIL + 1, \
    "leg1-A staircase machine-check failed: A base != prior-wave B tail+1"
assert (fc_b_naive, hops_b_naive) == ((331_604, 331_803), 0), \
    f"leg1 naive-B geometry drift: {fc_b_naive} hops={hops_b_naive}"
assert overlaps(fc_b_naive, fc_a), "leg1 naive-B not inside own-wave A"
# B walk WITH the own-wave A window reserved (same-freeze mutual exclusion)
b_trace2 = []
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace2,
                             extra_bands=(fc_a,))
print(f"leg1: B first-clean WITH own-wave A reserved -> {fc_b[0]}..{fc_b[1]} "
      f"hops={hops_b}")
assert (fc_b, hops_b) == ((333_604, 333_803), 1), \
    f"leg1-B derive drift: {fc_b} hops={hops_b}"
assert not overlaps(fc_a, fc_b), "A/B overlap"
assert fc_b[0] == fc_a[1] + 1, \
    "leg1-B machine-check failed: B base != own-wave A tail+1"
# the last hop of the honest chain must be the own-A mutual-exclusion hop
assert b_trace2[-1]["refusers"] and \
    "own-wave-A" in b_trace2[-1]["refusers"][0] and \
    b_trace2[-1]["jump_to"] == 333_604, "own-A mutual-exclusion hop not last"

W144_A = fc_a
W144_B = fc_b

# --- leg 1b: cross-window convergence with the r750 W143 gate-tail projection --
assert W144_A == (331_604, 333_603) and hops_a == 1, \
    f"leg1b failed: A fork vs W143 gate-tail projection: {W144_A}"
print("leg1b: A converges with the r750 W143 band-gate leg3 projection -- the "
      "projection anticipated the naive A window 331_404..333_403 would be "
      "refused by the registered W143 B band; this re-derive (post-W143 "
      "universe) hops past it -> 331_604..333_603 hops=1, A-hops-prior-B "
      "staircase third instance (A base == W143 B tail+1 machine-checkable; "
      "r587 re-derive-never-transcribe law held). B: the projection "
      "disclosed the same-freeze mutual-exclusion obligation -- honored: "
      "naive B 331_604..331_803 lands inside the own-wave A window -> "
      "reserved walk -> 333_604..333_803 hops=1 (B base == own-A tail+1 "
      "machine-checkable). The MANDATORY note is honored on both faces, "
      "disclosed, not a fork.")
receipt["legs"]["leg1"] = {
    "A": "331_604..333_603", "hops_A": 1,
    "A_refused_at_arithmetic_by": "registered W143 B band 331_404..331_603",
    "A_hop_chain": a_trace,
    "B": "333_604..333_803", "hops_B": 1,
    "B_naive_first_clean": "331_604..331_803", "B_naive_hops": 0,
    "B_naive_lands_inside_own_wave_A": True,
    "B_hop_chain": b_trace2,
    "A_semantics": ("A arithmetic continuation from the registered W143 "
                    "A tail 331_403 + 1 -> 331_404..333_403 REFUSED (the "
                    "registered W143 B band 331_404..331_603 sits at the "
                    "arithmetic start, as the r750 W143 gate leg3 "
                    "projection note anticipated); honest forward walk "
                    "hops past the W143 B band -> first-clean "
                    "331_604..333_603, hops=1, non-rotational (r587) "
                    "forward-monotone assert enforced in-walk; A base == "
                    "prior-wave B tail+1 (331_603+1 == 331_604) "
                    "machine-checkable relation (A-hops-prior-B staircase "
                    "third instance, E36 card)"),
    "B_semantics": ("B arithmetic continuation from the registered W143 "
                    "B tail 331_603 + 1 -> 331_604..331_803 CLEAN on the "
                    "registered universe BUT lands INSIDE the W144 "
                    "own-wave A window 331_604..333_603 -- same-freeze "
                    "mutual exclusion (W141 precedent, leg2 law); the walk "
                    "with the own-wave A window reserved jumps to 333_604 "
                    "-> first-clean 333_604..333_803, hops=1, "
                    "non-rotational (r587) forward-monotone assert "
                    "enforced in-walk; B base == own-wave A tail+1 "
                    "(333_603+1 == 333_604) machine-checkable relation"),
    "r750_projection_mandatory_note": ("honored on both faces: re-derive on "
                                       "the post-W143 universe (done) AND "
                                       "own-wave A reservation when "
                                       "deriving B (done)"),
}

# --- leg 2: candidate ADMIT-derivation vs registry points/bands ----------------
conflicts = []
for tag, band in (("A", W144_A), ("B", W144_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W144-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W144-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W144-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W144-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W144-{tag}")
    for p in CROSSFACE_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"cross-face probe point {p} inside W144-{tag} (r602 leg)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W144-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W144-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W144-{tag} (r335 leg)")

out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '144: {"a": (331_604' not in out, \
    "leg2 failed: W144 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W144"' not in outn1, \
    "leg2 failed: W144 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W144_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W144 per-wave prereg ALREADY on origin"
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT, capture_output=True)
w144_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
              if "w144" in ln.lower() and "seat" in ln.lower()]
assert not w144_seats, f"leg2 failed: W144 seat already published: {w144_seats}"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W144 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
receipt["legs"]["leg2"] = {"conflicts": 0, "origin_vacancy": True}
print(f"W144 ADMIT-derive: A {W144_A[0]}..{W144_A[1]} hops={hops_a} + "
      f"B {W144_B[0]}..{W144_B[1]} hops={hops_b} "
      f"(mode={MODE}; A hops past prior-wave B, B first-clean past "
      "own-wave A, staircase geometry) -- clean vs all registered rows + "
      "registry + probes/actuals -- publish seat MSG with these bands, "
      "then full gate with leg0b seat-on-origin check.")

# --- W145+ projection (warning text for the law table row) --------------------
# naive independent derives on the pre-W144-registration universe: the W145
# freezer re-derives with the W144 A/B bands registered + must apply the
# same-freeze mutual exclusion to its own A/B pair (W141 precedent, E36).
(fc145_a, h145a) = first_clean(W144_A[1] + 1, WIDTH_A)
(fc145_b, h145b) = first_clean(W144_B[1] + 1, WIDTH_B)
f145a = refusal_facts(fc145_a)
f145b = refusal_facts(fc145_b)
inside145 = overlaps(fc145_b, fc145_a)
print(f"W145+ projection: A first-clean {fc145_a[0]}..{fc145_a[1]} hops={h145a} "
      f"-> {'CLEAN (verify at W145 prereg)' if not f145a else 'REFUSED ' + str(f145a)}; "
      f"B first-clean {fc145_b[0]}..{fc145_b[1]} hops={h145b} "
      f"-> {'CLEAN (verify at W145 prereg)' if not f145b else 'REFUSED ' + str(f145b)}; "
      f"naive B lands inside naive A: {inside145} "
      "(same-freeze mutual exclusion applies at W145, W141 precedent)")
receipt["legs"]["leg3"] = {"W145p_A": f"{fc145_a[0]}..{fc145_a[1]}",
                           "hops_A": h145a,
                           "W145p_B": f"{fc145_b[0]}..{fc145_b[1]}",
                           "hops_B": h145b,
                           "W145p_B_lands_inside_W145p_A": inside145,
                           "note": ("W145 freezer MUST re-derive (r587) and MUST "
                                    "apply the same-freeze mutual exclusion: "
                                    "reserve the W145 own-wave A window when "
                                    "deriving B (W141 precedent, leg2 law, "
                                    "E36 card); the registered W144 B band "
                                    f"{W144_B[0]}..{W144_B[1]} will refuse the naive "
                                    "W145 A window (staircase A-hops-prior-B)")}

receipt["verdict"] = "ADMIT"
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r751bma_w144_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print("receipt -> results/_r751bma_w144_probe_receipt.json")
