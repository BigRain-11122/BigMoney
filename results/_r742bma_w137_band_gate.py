# -*- coding: utf-8 -*-
"""r742 bm-a W137 freeze-window band gate -- dual-window derive parity with the
pre-seat probe (r587/r384 pattern), plus own-seat presence check (r374 dual-dir
law + r565 published=reserved).  Runs BEFORE the freeze edits land.
Bloodline: r741 _r741bma_w136_band_gate.py verbatim + W137 facts
(A = arithmetic continuation from the registered W136 A tail 317_003+1
CLEAN hops=0; B = honest 12-hop forward walk from the registered W136 B
tail 69_901+1: first window refused by N3-R1 used-seed band + contiguous
registered 2_000-wide bands 70_001..94_000, lands at 94_001..94_200,
non-rotational r587 with per-hop trace + forward-monotone assert).
Receipt -> results/_r742bma_w137_band_gate.json
"""
import subprocess
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000
SEAT_PATH = "fleet/inbox/MSG-2026-10-05-202x-bma-w137-seat.md"
W136_A, W136_B = (315_004, 317_003), (69_702, 69_901)
WIDTH_A, WIDTH_B = 2_000, 200
N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
CROSSFACE_PROBE_POINTS = (95_004, 95_006)
LFC_ACTUAL, OPTIONS_ACTUAL = (30_000, 30_099), (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
receipt = {"probe": "r742 W137 freeze-window band gate", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS) | set(range(*N3R1_USED)) | {N3R1_USED[1]}
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape + ordinals (single state, must equal pre-seat) -------
keys = sorted(N1_BANDS)
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 137)), \
    f"leg0 registry keys drift: tail {keys[-5:]}"
assert N1_BANDS[136]["a"] == W136_A and N1_BANDS[136]["b_exit"] == W136_B \
    and N1_BANDS[136].get("engine_owner") == "bm-a", "leg0 W136 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 126 and len(bma_rows) == 52, "leg0 ordinal drift"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W136",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 127, "bma_ordinal": 53}
print(f"leg0: {len(N1_BANDS)} rows tail=W136, owner=126 -> 127th wave, bm-a 53rd owned")

# --- leg 0b: OWN seat published on origin (r565); zero OTHER W137 seats ---------
r = subprocess.run(["git", "show", f"origin/main:{SEAT_PATH}"], cwd=ROOT,
                   capture_output=True)
assert r.returncode == 0, "leg0b failed: own W137 seat MSG NOT on origin (r565)"
seat_txt = r.stdout.decode("utf-8", "replace")
assert "A 317_004..319_003" in seat_txt and "B 94_001..94_200" in seat_txt, \
    "leg0b failed: seat bands mismatch"
_r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                    capture_output=True)
seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
         if "w137" in ln.lower() and "seat" in ln.lower()]
assert seats == [SEAT_PATH], f"leg0b failed: unexpected W137 seats: {seats}"
receipt["legs"]["leg0b"] = {"own_seat_on_origin": True, "other_seats": 0,
                            "seat_commit": "af1c3c267 (pre-freeze push, merge-closeout per r524 law, zero --no-verify)"}
print("leg0b: own seat on origin, zero other W137 seats (r374 dual-dir scan)")

# --- leg 1: derive identical to pre-seat probe ----------------------------------
ARITH_A = (W136_A[1] + 1, W136_A[1] + WIDTH_A)
ARITH_B = (W136_B[1] + 1, W136_B[1] + WIDTH_B)
assert ARITH_A == (317_004, 319_003) and ARITH_B == (69_902, 70_101), "leg1 drift"


def first_clean(lo, width, trace=None):
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
            trace.append({"hop": hops + 1, "window": [lo, hi], "jump_to": jump})
        lo = jump
        prev_lo = lo
        hops += 1


b_trace = []
(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A)
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace)
assert (fc_a, hops_a) == ((317_004, 319_003), 0), f"leg1 A derive fork: {fc_a}"
assert (fc_b, hops_b) == ((94_001, 94_200), 12), f"leg1 B derive fork: {fc_b}"
receipt["legs"]["leg1"] = {"A": "317_004..319_003", "hops_A": 0,
                           "B": "94_001..94_200", "hops_B": 12,
                           "B_hop_chain": b_trace,
                           "B_semantics": "honest 12-hop forward walk: first "
                           "window 69_902..70_101 refused by N3-R1 used-seed "
                           "band + contiguous registered 2_000-wide bands "
                           "70_001..94_000; every hop a strict forward jump "
                           "past the refusing band (non-rotational r587, "
                           "forward-monotone assert in-walk); dual-window "
                           "derive parity with the pre-seat probe",
                           "derive_parity_with_pre_seat": True}
print("leg1: A 317_004..319_003 hops=0 + B 94_001..94_200 hops=12 "
      "(identical to pre-seat derive, zero fork; honest forward walk, "
      "non-rotational r587)")

# --- leg 2: full reserved universe conflicts + origin vacancy --------------------
conflicts = []
for tag, band in (("A", fc_a), ("B", fc_b)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} x W137-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W137-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W137-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W137-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W137-{tag} (MSG-183x)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W137-{tag}")
assert not conflicts, f"leg2 failed: W137 conflicts {conflicts}"
assert not overlaps(fc_a, fc_b), "leg2 failed: W137 A/B overlap"
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '137: {"a": (317_004' not in out, \
    "leg2 failed: W137 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W137"' not in outn1, \
    "leg2 failed: W137 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W137_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W137 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0, "origin_vacancy": True,
                          "seat": SEAT_PATH, "push": "af1c3c267 (pre-freeze push, merge-closeout per r524 law, zero --no-verify)"}
print("leg2: zero conflicts; origin vacancy holds (row/configs/prereg/seat)")

# --- leg 3: W138+ projection (gate tail, next freezer re-derives) -----------------
(fc138_a, h138a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc138_b, h138b) = first_clean(fc_b[1] + 1, WIDTH_B)
receipt["legs"]["leg3"] = {"W138p_A": f"{fc138_a[0]}..{fc138_a[1]}",
                           "hops_A": h138a,
                           "W138p_B": f"{fc138_b[0]}..{fc138_b[1]}",
                           "hops_B": h138b}
print(f"leg3: W138+ projection A {fc138_a[0]}..{fc138_a[1]} hops={h138a} / "
      f"B {fc138_b[0]}..{fc138_b[1]} hops={h138b} (next freezer re-derives)")

receipt["verdict"] = "ADMIT"
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r742bma_w137_band_gate.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print("W137 BAND GATE rc0 ADMIT: A 317_004..319_003 + B 94_001..94_200 "
      "(dual-window derive parity held; honest 12-hop forward walk "
      "non-rotational r587; receipt written)")
