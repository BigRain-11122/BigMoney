# -*- coding: utf-8 -*-
"""r742 bm-a W137 pre-seat probe -- read-only band derivation before the
seat MSG publication (r565 early-visibility law: seat published=reserved
BEFORE the freeze commit; the seat must carry the machine-derived bands).

W137 candidate = first FREE number after the REGISTERED W136 row (bm-a
r741 freeze; W136 finalize landed same-window r742, ledger head 695,211,
merged pool K=297,120).
Derivation faces:
  A  arithmetic continuation from the registered W136 A tail 317_003 + 1,
     stride 2_000 -> 317_004..319_003, honest forward walk to first clean.
     Projection says CLEAN hops=0 (r741 band-gate leg3).
  B  arithmetic continuation from the registered W136 B tail 69_901 + 1,
     stride 200 -> 69_902..70_101 first REFUSED (N3-R1 used-seed band
     70_000..70_005 MSG-183x r529 leg + contiguous registered 2_000-wide
     bands 70_001..94_000), honest forward walk 12 hops -> 94_001..94_200.
     r587 non-rotational re-derive: every hop is a strict forward jump past
     the refusing object; per-hop chain machine-traced and pinned in the
     receipt; cross-checked against the r741 band-gate leg3 projection
     (B 94_001..94_200 hops=12) bit-for-bit.
Machine-verified against: all registered N1 wave bands (W2..W14,
W16..W136), N3-R1 used-seed band, probe cluster 95_000..95_003 (r335 leg),
cross-face probe points 95_004/95_006 (r602 leg), v1 in-use + W1 ext bands,
SEED_REGISTRY live values, N2/N4 probe points, N2-W15 draft probe points,
lfc/options actual draw ranges.
Bloodline: r741 _r741bma_w136_probe.py verbatim + W137 facts + B hop-chain
trace legs (hops=12 non-rotational law face).
"""
import subprocess
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000
W136_A_TAIL = 317_003
W136_B_TAIL = 69_901
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
receipt = {"probe": "r742 W137 pre-seat probe", "legs": {}}


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

# --- leg 0: registry shape (single state: W136 registered, tail=W136) ---------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 137))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert N1_BANDS[136]["a"] == (315_004, W136_A_TAIL) and \
    N1_BANDS[136]["b_exit"] == (69_702, W136_B_TAIL) and \
    N1_BANDS[136].get("engine_owner") == "bm-a", "leg0 failed: W136 row drift"
assert N1_BANDS[134]["a"] == (311_004, 313_003) and \
    N1_BANDS[134]["b_exit"] == (69_302, 69_501) and \
    N1_BANDS[134].get("engine_owner") == "bm-a", "leg0 failed: W134 row drift"
assert N1_BANDS[135]["a"] == (313_004, 315_003) and \
    N1_BANDS[135]["b_exit"] == (69_502, 69_701) and \
    N1_BANDS[135].get("engine_owner") == "bm-a", "leg0 failed: W135 row drift"
MODE = ("B137 (registered W136, bm-a r741 freeze; W136 finalize landed "
        "same-window r742, ledger head 695,211, merged pool K=297,120)")
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}, mode={MODE}")
print(f"leg0: engine_owner rows={len(owner_rows)} + candidate; bm-a "
      f"rows={len(bma_rows)} -> W137 = bm-a "
      f"{len(bma_rows) + 1}th owned; W137 ordinal = "
      f"{len(owner_rows) + 1}th engine wave by machine-derive")
assert len(owner_rows) == 126 and len(bma_rows) == 52, "leg0 ordinal drift"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W136",
                           "owner_rows": len(owner_rows),
                           "bma_rows": len(bma_rows),
                           "ordinal": 127, "bma_ordinal": 53}

# --- leg 1: honest forward walk from the registered W136 tails ----------------
ARITH_A = (W136_A_TAIL + 1, W136_A_TAIL + WIDTH_A)
ARITH_B = (W136_B_TAIL + 1, W136_B_TAIL + WIDTH_B)
assert ARITH_A == (317_004, 319_003), f"leg1-A drift: {ARITH_A}"
assert ARITH_B == (69_902, 70_101), f"leg1-B drift: {ARITH_B}"


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


def first_clean(lo, width, trace=None):
    """First clean window at/after lo; pinned D-20261002-05 past-hit
    restart semantics (lo jumps past the refusing point/band, law sec.4).
    r587 non-rotational face: per-hop trace + strict forward-monotone assert."""
    hops = 0
    prev_lo = lo
    while True:
        hi = lo + width - 1
        bad_pts = [p for p in points if lo <= p <= hi]
        bad_bands = [b for b in bands + actual if overlaps((lo, hi), b)]
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
                who.append(f"band{b[0]}..{b[1]}")
            trace.append({"hop": hops + 1, "window": [lo, hi],
                          "refusers": who, "jump_to": jump})
        lo = jump
        prev_lo = lo
        hops += 1


fA = refusal_facts(ARITH_A)
fB = refusal_facts(ARITH_B)
b_trace = []
(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A)
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace)
print(f"leg1: A arithmetic {ARITH_A[0]}..{ARITH_A[1]} "
      f"{'CLEAN' if not fA else 'REFUSED ' + str(fA)} -> first-clean "
      f"{fc_a[0]}..{fc_a[1]} hops={hops_a}")
print(f"leg1: B arithmetic {ARITH_B[0]}..{ARITH_B[1]} "
      f"{'CLEAN' if not fB else 'REFUSED'} -> first-clean "
      f"{fc_b[0]}..{fc_b[1]} hops={hops_b} (hop chain in receipt)")
assert not overlaps(fc_a, fc_b), "A/B overlap"

W137_A = fc_a
W137_B = fc_b

# --- leg 1b: cross-window convergence with the r741 W136 gate-tail projection (r587) --
assert W137_A == (317_004, 319_003) and hops_a == 0, \
    f"leg1b failed: A fork vs W136 gate-tail projection: {W137_A}"
assert W137_B == (94_001, 94_200) and hops_b == 12, \
    f"leg1b failed: B fork vs W136 gate-tail projection: {W137_B}"
print("leg1b: derive converges bit-for-bit with the r741 W136 band-gate leg3 "
      "projection (A 317_004..319_003 hops=0 / B 94_001..94_200 hops=12; "
      "r587 re-derive-never-transcribe law held)")
receipt["legs"]["leg1"] = {
    "A": "317_004..319_003", "hops_A": 0, "A_clean_at_arithmetic": True,
    "B": "94_001..94_200", "hops_B": 12,
    "B_hop_chain": b_trace,
    "B_semantics": ("first B window 69_902..70_101 refused by N3-R1 "
                    "used-seed band 70_000..70_005 (MSG-183x r529 leg) + "
                    "the contiguous registered 2_000-wide band 70_001..72_000; "
                    "12 strict forward hops over the contiguous registered "
                    "bands 70_001..94_000 land at 94_001..94_200 -- honest "
                    "forward walk, non-rotational (r587): every hop jumps "
                    "strictly past the refusing band, forward-monotone "
                    "assert enforced in-walk"),
    "derive_parity_with_gate_tail_projection": True,
}

# --- leg 2: candidate ADMIT-derivation vs registry points/bands ----------------
conflicts = []
for tag, band in (("A", W137_A), ("B", W137_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W137-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W137-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W137-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W137-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W137-{tag}")
    for p in CROSSFACE_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"cross-face probe point {p} inside W137-{tag} (r602 leg)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W137-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W137-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W137-{tag} (r335 leg)")

out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '137: {"a": (317_004' not in out, \
    "leg2 failed: W137 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W137"' not in outn1, \
    "leg2 failed: W137 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W137_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W137 per-wave prereg ALREADY on origin"
_r = subprocess.run(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT, capture_output=True)
w137_seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
              if "w137" in ln.lower() and "seat" in ln.lower()]
assert not w137_seats, f"leg2 failed: W137 seat already published: {w137_seats}"

print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W137 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
receipt["legs"]["leg2"] = {"conflicts": 0, "origin_vacancy": True}
print(f"W137 ADMIT-derive: A {W137_A[0]}..{W137_A[1]} hops={hops_a} + "
      f"B {W137_B[0]}..{W137_B[1]} hops={hops_b} "
      f"(mode={MODE}; A arithmetic CLEAN, B honest 12-hop forward walk) -- "
      "clean vs all registered rows + registry + probes/actuals -- publish "
      "seat MSG with these bands, then full gate with leg0b seat-on-origin "
      "check.")

# --- W138+ projection (warning text for the law table row) --------------------
(fc138_a, h138a) = first_clean(W137_A[1] + 1, WIDTH_A)
(fc138_b, h138b) = first_clean(W137_B[1] + 1, WIDTH_B)
f138a = refusal_facts(fc138_a)
f138b = refusal_facts(fc138_b)
print(f"W138+ projection: A first-clean {fc138_a[0]}..{fc138_a[1]} hops={h138a} "
      f"-> {'CLEAN (verify at W138 prereg)' if not f138a else 'REFUSED ' + str(f138a)}; "
      f"B first-clean {fc138_b[0]}..{fc138_b[1]} hops={h138b} "
      f"-> {'CLEAN (verify at W138 prereg)' if not f138b else 'REFUSED ' + str(f138b)}")
receipt["legs"]["leg3"] = {"W138p_A": f"{fc138_a[0]}..{fc138_a[1]}",
                           "hops_A": h138a,
                           "W138p_B": f"{fc138_b[0]}..{fc138_b[1]}",
                           "hops_B": h138b}

receipt["verdict"] = "ADMIT"
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r742bma_w137_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print("receipt -> results/_r742bma_w137_probe_receipt.json")
