# -*- coding: utf-8 -*-
"""r747 bm-a W141 pre-seat probe -- read-only band derivation before the
seat MSG publication (r565 early-visibility law: seat published=reserved
BEFORE the freeze commit; the seat must carry the machine-derived bands).

W141 candidate = first FREE number after the REGISTERED W140 row (bm-a
r745 freeze 5e3984200; W140 finalize landed same-window r746 one-pass,
ledger head 704,011, merged pool K=305,920).
Derivation faces:
  A  arithmetic continuation from the registered W140 A tail 325_003 + 1,
     stride 2_000 -> 325_004..327_003, honest forward walk to first clean.
     r745 W140 gate-tail projection says CLEAN hops=0 (verified here).
  B  arithmetic continuation from the registered W140 B tail 94_800 + 1,
     stride 200 -> 94_801..95_000 REFUSED (probe seed 95_000 inside, r335
     leg). Honest forward walk from 94_801 hops past the probe cluster
     (95_000..95_006) and the long registered band mass, landing at
     325_004..325_203 after 116 hops -- INSIDE the W141 own-wave A window
     (same-freeze mutual exclusion, band-gate leg2 law). The walk continues
     past the own-wave A window -> first-clean 327_004..327_203, hops=117
     total (non-rotational r587 forward-monotone assert enforced in-walk).
     This honors the r745 W140 gate-tail projection note verbatim: "B
     re-derive MANDATORY at W141 prereg, the baseline lands inside the
     now-registered W140 A band" -- the re-derive crosses BOTH the W140 A
     band AND the own-wave W141 A window (the projection anticipated the
     first, the second is the same-freeze mutual-exclusion face, disclosed).
Machine-verified against: all registered N1 wave bands (W2..W14,
W16..W140), N3-R1 used-seed band, probe cluster 95_000..95_003 (r335 leg),
cross-face probe points 95_004/95_006 (r602 leg), v1 in-use + W1 ext bands,
SEED_REGISTRY live values, N2/N4 probe points, N2-W15 draft probe points,
lfc/options actual draw ranges.
Bloodline: r745 _r745bma_w140_probe.py verbatim + W141 facts + own-wave-A
mutual-exclusion B face.
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
W140_A_TAIL = 325_003
W140_B_TAIL = 94_800
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
receipt = {"probe": "r747 W141 pre-seat probe", "legs": {}}


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

# --- leg 0: registry shape (single state: W140 registered, tail=W140) ---------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 141))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert N1_BANDS[140]["a"] == (323_004, W140_A_TAIL) and \
    N1_BANDS[140]["b_exit"] == (94_601, W140_B_TAIL) and \
    N1_BANDS[140].get("engine_owner") == "bm-a", "leg0 failed: W140 row drift"
assert N1_BANDS[138]["a"] == (319_004, 321_003) and \
    N1_BANDS[138]["b_exit"] == (94_201, 94_400) and \
    N1_BANDS[138].get("engine_owner") == "bm-a", "leg0 failed: W138 row drift"
assert N1_BANDS[139]["a"] == (321_004, 323_003) and \
    N1_BANDS[139]["b_exit"] == (94_401, 94_600) and \
    N1_BANDS[139].get("engine_owner") == "bm-a", "leg0 failed: W139 row drift"
MODE = ("B141 (registered W140, bm-a r745 freeze 5e3984200; W140 finalize "
        "landed same-window r746 one-pass, ledger head 704,011, merged pool "
        "K=305,920)")
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-a "
      f"rows={len(bma_rows)} -> W141 = bm-a "
      f"{len(bma_rows) + 1}th owned; W141 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")
assert len(owner_rows) == 130 and len(bma_rows) == 56, "leg0 ordinal drift"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W140",
                           "owner_rows": len(owner_rows),
                           "bma_rows": len(bma_rows),
                           "ordinal": 131, "bma_ordinal": 57}

# --- leg 1: honest forward walk from the registered W140 tails ----------------
ARITH_A = (W140_A_TAIL + 1, W140_A_TAIL + WIDTH_A)
ARITH_B = (W140_B_TAIL + 1, W140_B_TAIL + WIDTH_B)
assert ARITH_A == (325_004, 327_003), f"leg1-A drift: {ARITH_A}"
assert ARITH_B == (94_801, 95_000), f"leg1-B drift: {ARITH_B}"


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
assert not fA, f"leg1-A arithmetic window REFUSED: {fA}"
assert fB, "leg1-B arithmetic window unexpectedly CLEAN (probe cluster moved?)"
b_trace = []
(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A)
# naive B walk (registered universe only) -- lands inside the own-wave A window
(fc_b_naive, hops_b_naive) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace)
print(f"leg1: A arithmetic {ARITH_A[0]}..{ARITH_A[1]} "
      f"{'CLEAN' if not fA else 'REFUSED'} -> first-clean "
      f"{fc_a[0]}..{fc_a[1]} hops={hops_a}")
print(f"leg1: B arithmetic {ARITH_B[0]}..{ARITH_B[1]} REFUSED -> naive "
      f"first-clean {fc_b_naive[0]}..{fc_b_naive[1]} hops={hops_b_naive} "
      f"(INSIDE own-wave A window {fc_a[0]}..{fc_a[1]} -> mutual exclusion)")
assert overlaps(fc_b_naive, fc_a) and fc_b_naive == (325_004, 325_203) \
    and hops_b_naive == 116, "leg1 naive-B geometry drift"
# B walk WITH the own-wave A window reserved (same-freeze mutual exclusion)
b_trace2 = []
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace2,
                             extra_bands=(fc_a,))
print(f"leg1: B first-clean WITH own-wave A reserved -> {fc_b[0]}..{fc_b[1]} "
      f"hops={hops_b}")
assert fc_b == (327_004, 327_203) and hops_b == 117, \
    f"leg1-B derive drift: {fc_b} hops={hops_b}"
assert not overlaps(fc_a, fc_b), "A/B overlap"
# the last hop of the honest chain must be the own-A mutual-exclusion hop
assert b_trace2[-1]["refusers"] and \
    "own-wave-A" in b_trace2[-1]["refusers"][0] and \
    b_trace2[-1]["jump_to"] == 327_004, "own-A mutual-exclusion hop not last"
assert [t["jump_to"] for t in b_trace2][:116] == \
       [t["jump_to"] for t in b_trace][:116], "naive prefix divergence"

W141_A = fc_a
W141_B = fc_b

# --- leg 1b: cross-window convergence with the r745 W140 gate-tail projection --
assert W141_A == (325_004, 327_003) and hops_a == 0, \
    f"leg1b failed: A fork vs W140 gate-tail projection: {W141_A}"
print("leg1b: A converges bit-for-bit with the r745 W140 band-gate leg3 "
      "projection (325_004..327_003 hops=0; r587 re-derive-never-transcribe "
      "law held). B: the r745 projection disclosed the pre-W140 baseline "
      "323_004..323_203 hops=115 with the re-derive-MANDATORY note; this "
      "re-derive (post-W140 universe) crosses the W140 A band as anticipated "
      "AND the own-wave W141 A window (same-freeze mutual exclusion, leg2 "
      "law) -> 327_004..327_203 hops=117 -- the MANDATORY note is honored, "
      "the own-A hop is the honest additional face, disclosed, not a fork.")
receipt["legs"]["leg1"] = {
    "A": "325_004..327_003", "hops_A": 0, "A_clean_at_arithmetic": True,
    "B": "327_004..327_203", "hops_B": 117,
    "B_naive_first_clean": "325_004..325_203", "B_naive_hops": 116,
    "B_naive_lands_inside_own_wave_A": True,
    "B_hop_chain": b_trace2,
    "A_semantics": ("A arithmetic continuation from the registered W140 "
                    "A tail 325_003 + 1 -> 325_004..327_003 CLEAN at the "
                    "arithmetic window, zero hops, non-rotational (r587) "
                    "forward-monotone assert enforced in-walk"),
    "B_semantics": ("B arithmetic continuation from the registered W140 "
                    "B tail 94_800 + 1 -> 94_801..95_000 REFUSED (probe "
                    "seed 95_000, r335 leg); honest forward walk from "
                    "94_801: 116 hops land 325_004..325_203 INSIDE the "
                    "W141 own-wave A window -- same-freeze mutual "
                    "exclusion (band-gate leg2 law) -- the walk continues "
                    "past the own-wave A window and lands 327_004..327_203, "
                    "117 hops total, non-rotational (r587) forward-monotone "
                    "assert enforced in-walk; B base == own-wave A tail + 1 "
                    "(327_003 + 1 == 327_004) machine-checkable relation"),
    "r745_projection_mandatory_note": ("honored: B re-derive crossed the "
                                       "registered W140 A band as the note "
                                       "anticipated; the own-wave A hop is "
                                       "the additional honest face"),
}

# --- leg 2: candidate ADMIT-derivation vs registry points/bands ----------------
conflicts = []
for tag, band in (("A", W141_A), ("B", W141_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W141-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W141-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W141-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W141-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W141-{tag}")
    for p in CROSSFACE_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"cross-face probe point {p} inside W141-{tag} (r602 leg)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W141-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W141-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W141-{tag} (r335 leg)")

out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '141: {"a": (325_004' not in out, \
    "leg2 failed: W141 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W141"' not in outn1, \
    "leg2 failed: W141 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W141_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W141 per-wave prereg ALREADY on origin"
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT, capture_output=True)
w141_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
              if "w141" in ln.lower() and "seat" in ln.lower()]
assert not w141_seats, f"leg2 failed: W141 seat already published: {w141_seats}"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W141 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
receipt["legs"]["leg2"] = {"conflicts": 0, "origin_vacancy": True}
print(f"W141 ADMIT-derive: A {W141_A[0]}..{W141_A[1]} hops={hops_a} + "
      f"B {W141_B[0]}..{W141_B[1]} hops={hops_b} "
      f"(mode={MODE}; B first-clean past own-wave A, same-freeze mutual "
      "exclusion) -- clean vs all registered rows + registry + probes/"
      "actuals -- publish seat MSG with these bands, then full gate with "
      "leg0b seat-on-origin check.")

# --- W142+ projection (warning text for the law table row) --------------------
# naive independent derives on the post-W141-candidate universe: the W142
# freezer re-derives with the W141 A/B bands registered + must apply the
# same-freeze mutual exclusion to its own A/B pair (W141 precedent).
(fc142_a, h142a) = first_clean(W141_A[1] + 1, WIDTH_A)
(fc142_b, h142b) = first_clean(W141_B[1] + 1, WIDTH_B)
f142a = refusal_facts(fc142_a)
f142b = refusal_facts(fc142_b)
inside142 = overlaps(fc142_b, fc142_a)
print(f"W142+ projection: A first-clean {fc142_a[0]}..{fc142_a[1]} hops={h142a} "
      f"-> {'CLEAN (verify at W142 prereg)' if not f142a else 'REFUSED ' + str(f142a)}; "
      f"B first-clean {fc142_b[0]}..{fc142_b[1]} hops={h142b} "
      f"-> {'CLEAN (verify at W142 prereg)' if not f142b else 'REFUSED ' + str(f142b)}; "
      f"naive B lands inside naive A: {inside142} "
      "(same-freeze mutual exclusion applies at W142, W141 precedent)")
receipt["legs"]["leg3"] = {"W142p_A": f"{fc142_a[0]}..{fc142_a[1]}",
                           "hops_A": h142a,
                           "W142p_B": f"{fc142_b[0]}..{fc142_b[1]}",
                           "hops_B": h142b,
                           "W142p_B_lands_inside_W142p_A": inside142,
                           "note": ("W142 freezer MUST re-derive (r587) and MUST "
                                    "apply the same-freeze mutual exclusion: "
                                    "reserve the W142 own-wave A window when "
                                    "deriving B (W141 precedent, leg2 law)")}

receipt["verdict"] = "ADMIT"
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r747bma_w141_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print("receipt -> results/_r747bma_w141_probe_receipt.json")
