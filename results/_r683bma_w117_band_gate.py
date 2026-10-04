# -*- coding: utf-8 -*-
"""r683 bm-a W117 freeze-window band gate -- dual-window derive parity with the
pre-seat probe (r587/r384 pattern), plus own-seat presence check (r374 dual-dir
law + r565 published=reserved).  Runs BEFORE the freeze edits land.
Receipt -> results/_r683bma_w117_band_gate.json
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
SEAT_PATH = "fleet/inbox/MSG-2026-10-04-1535-bma-w117-seat.md"
W116_A, W116_B = (275_004, 277_003), (62_701, 62_900)
WIDTH_A, WIDTH_B = 2_000, 200
N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
CROSSFACE_PROBE_POINTS = (95_004, 95_006)
LFC_ACTUAL, OPTIONS_ACTUAL = (30_000, 30_099), (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
receipt = {"probe": "r683 W117 freeze-window band gate", "legs": {}}


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
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 117)), \
    f"leg0 registry keys drift: tail {keys[-5:]}"
assert N1_BANDS[116]["a"] == W116_A and N1_BANDS[116]["b_exit"] == W116_B \
    and N1_BANDS[116].get("engine_owner") == "bm-b", "leg0 W116 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 106 and len(bma_rows) == 33, "leg0 ordinal drift"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W116",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 107, "bma_ordinal": 34}
print(f"leg0: {len(N1_BANDS)} rows tail=W116, owner=106 -> 107th wave, bm-a 34th owned")

# --- leg 0b: OWN seat published on origin (r565); zero OTHER W117 seats ---------
r = subprocess.run(["git", "show", f"origin/main:{SEAT_PATH}"], cwd=ROOT,
                   capture_output=True)
assert r.returncode == 0, "leg0b failed: own W117 seat MSG NOT on origin (r565)"
seat_txt = r.stdout.decode("utf-8", "replace")
assert "A 277_004..279_003" in seat_txt and "B 65_050..65_249" in seat_txt, \
    "leg0b failed: seat bands mismatch"
_r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                    capture_output=True)
seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
         if "w117" in ln.lower() and "seat" in ln.lower()]
assert seats == [SEAT_PATH], f"leg0b failed: unexpected W117 seats: {seats}"
receipt["legs"]["leg0b"] = {"own_seat_on_origin": True, "other_seats": 0}
print("leg0b: own seat on origin, zero other W117 seats (r374 dual-dir scan)")

# --- leg 1: derive identical to pre-seat probe ----------------------------------
ARITH_A = (W116_A[1] + 1, W116_A[1] + WIDTH_A)
ARITH_B = (W116_B[1] + 1, W116_B[1] + WIDTH_B)
assert ARITH_A == (277_004, 279_003) and ARITH_B == (62_901, 63_100), "leg1 drift"


def first_clean(lo, width):
    hops = 0
    while True:
        hi = lo + width - 1
        bad_pts = [p for p in points if lo <= p <= hi]
        bad_bands = [b for b in bands + actual if overlaps((lo, hi), b)]
        if not bad_pts and not bad_bands:
            return (lo, hi), hops
        lo = max([p + 1 for p in bad_pts] + [b[1] + 1 for b in bad_bands])
        hops += 1


(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A)
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B)
assert (fc_a, hops_a) == ((277_004, 279_003), 0), f"leg1 A derive fork: {fc_a}"
assert (fc_b, hops_b) == ((65_050, 65_249), 1), f"leg1 B derive fork: {fc_b}"
receipt["legs"]["leg1"] = {"A": "277_004..279_003", "hops_A": 0,
                           "B": "65_050..65_249", "hops_B": 1,
                           "B_semantics": "pinned D-20261002-05 past-hit restart "
                           "(arith 62_901..63:100 refused at options actual "
                           "63_000..63_049 + registered W12 A band 63_050..65_049)",
                           "derive_parity_with_pre_seat": True}
print("leg1: A 277_004..279_003 hops=0 + B 65_050..65_249 hops=1 "
      "(identical to pre-seat derive, zero fork)")

# --- leg 2: full reserved universe conflicts + origin vacancy --------------------
conflicts = []
for tag, band in (("A", fc_a), ("B", fc_b)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} x W117-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W117-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W117-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W117-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W117-{tag} (MSG-183x)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W117-{tag}")
assert not conflicts, f"leg2 failed: W117 conflicts {conflicts}"
assert not overlaps(fc_a, fc_b), "leg2 failed: W117 A/B overlap"
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '117: {"a": (277_004' not in out, \
    "leg2 failed: W117 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W117"' not in outn1, \
    "leg2 failed: W117 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W117_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W117 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0, "origin_vacancy": True,
                           "seat": SEAT_PATH, "push": "380167da7 (pre-freeze, r565)"}
print("leg2: zero conflicts; origin vacancy holds (row/configs/prereg/seat)")

# --- leg 3: W118+ projection (gate tail, next freezer re-derives) -----------------
(fc118_a, h118a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc118_b, h118b) = first_clean(fc_b[1] + 1, WIDTH_B)
receipt["legs"]["leg3"] = {"W118p_A": f"{fc118_a[0]}..{fc118_a[1]}",
                           "hops_A": h118a,
                           "W118p_B": f"{fc118_b[0]}..{fc118_b[1]}",
                           "hops_B": h118b}
print(f"leg3: W118+ projection A {fc118_a[0]}..{fc118_a[1]} hops={h118a} / "
      f"B {fc118_b[0]}..{fc118_b[1]} hops={h118b} (next freezer re-derives)")

json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r683bma_w117_band_gate.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print("W117 BAND GATE rc0 ADMIT: A 277_004..279_003 + B 65_050..65_249 "
      "(dual-window derive parity held; receipt written)")
