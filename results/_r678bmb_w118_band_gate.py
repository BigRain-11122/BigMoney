# -*- coding: utf-8 -*-
"""r678 bm-b W118 freeze-window band gate -- dual-window derive parity with the
pre-seat probe (r587/r384 pattern), plus own-seat presence check (r374 dual-dir
law + r565 published=reserved).  Runs BEFORE the freeze edits land.
Receipt -> results/_r678bmb_w118_band_gate.json
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
SEAT_PATH = "fleet/inbox/MSG-2026-10-04-1532-bmb-w118-seat.md"
W117_A, W117_B = (277_004, 279_003), (65_050, 65_249)
WIDTH_A, WIDTH_B = 2_000, 200
N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
CROSSFACE_PROBE_POINTS = (95_004, 95_006)
LFC_ACTUAL, OPTIONS_ACTUAL = (30_000, 30_099), (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
receipt = {"probe": "r678 W118 freeze-window band gate", "legs": {}}


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
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 118)), \
    f"leg0 registry keys drift: tail {keys[-5:]}"
assert N1_BANDS[117]["a"] == W117_A and N1_BANDS[117]["b_exit"] == W117_B \
    and N1_BANDS[117].get("engine_owner") == "bm-a", "leg0 W117 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
assert len(owner_rows) == 107 and len(bmb_rows) == 39, "leg0 ordinal drift"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W117",
                           "owner_rows": len(owner_rows), "bmb_rows": len(bmb_rows),
                           "ordinal": 108, "bmb_ordinal": 40}
print(f"leg0: {len(N1_BANDS)} rows tail=W117, owner=107 -> 108th wave, bm-b 40th owned")

# --- leg 0b: OWN seat published on origin (r565); zero OTHER W118 seats ---------
r = subprocess.run(["git", "show", f"origin/main:{SEAT_PATH}"], cwd=ROOT,
                   capture_output=True)
assert r.returncode == 0, "leg0b failed: own W118 seat MSG NOT on origin (r565)"
seat_txt = r.stdout.decode("utf-8", "replace")
assert "A 279_004..281_003" in seat_txt and "B 65_250..65_449" in seat_txt, \
    "leg0b failed: seat bands mismatch"
_r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                    capture_output=True)
seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
         if "w118" in ln.lower() and "seat" in ln.lower()]
assert seats == [SEAT_PATH], f"leg0b failed: unexpected W118 seats: {seats}"
receipt["legs"]["leg0b"] = {"own_seat_on_origin": True, "other_seats": 0}
print("leg0b: own seat on origin, zero other W118 seats (r374 dual-dir scan)")

# --- leg 1: derive identical to pre-seat probe ----------------------------------
ARITH_A = (W117_A[1] + 1, W117_A[1] + WIDTH_A)
ARITH_B = (W117_B[1] + 1, W117_B[1] + WIDTH_B)
assert ARITH_A == (279_004, 281_003) and ARITH_B == (65_250, 65_449), "leg1 drift"


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
assert (fc_a, hops_a) == ((279_004, 281_003), 0), f"leg1 A derive fork: {fc_a}"
assert (fc_b, hops_b) == ((65_250, 65_449), 0), f"leg1 B derive fork: {fc_b}"
receipt["legs"]["leg1"] = {"A": "279_004..281_003", "hops_A": 0,
                           "B": "65_250..65_449", "hops_B": 0,
                           "derive_parity_with_pre_seat": True}
print("leg1: A 279_004..281_003 hops=0 + B 65_250..65_449 hops=0 "
      "(identical to pre-seat derive, zero fork)")

# --- leg 2: full reserved universe conflicts + origin vacancy --------------------
conflicts = []
for tag, band in (("A", fc_a), ("B", fc_b)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} x W118-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W118-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W118-{tag}")
    for p in N24_PROBE_POINTS + N2_W15_PROBE_POINTS + CROSSFACE_PROBE_POINTS + PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe point {p} inside W118-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for rr in bb:
            if overlaps(rr, band):
                conflicts.append(f"{nm} x W118-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W118-{tag}")

out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                              cwd=ROOT, encoding="utf-8")
assert '118: {"a": (279_004' not in out, "leg2: W118 row ALREADY on origin"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W118"' not in outn1, "leg2: W118 config on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W118_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2: W118 prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": conflicts, "vacant_on_origin": True}
if conflicts:
    print("W118 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print("leg2: zero conflicts; W118 slot vacant on origin (r511 tail-lock)")

# --- leg 3: W119+ projection (re-derive) -----------------------------------------
(ffc_a, hh_a) = first_clean(fc_a[1] + 1, WIDTH_A)
(ffc_b, hh_b) = first_clean(fc_b[1] + 1, WIDTH_B)
receipt["legs"]["leg3"] = {"W119_A": f"{ffc_a[0]}..{ffc_a[1]}", "hops_A": hh_a,
                           "W119_B": f"{ffc_b[0]}..{ffc_b[1]}", "hops_B": hh_b}
print(f"leg3: W119+ projection A {ffc_a[0]}..{ffc_a[1]} hops={hh_a} / "
      f"B {ffc_b[0]}..{ffc_b[1]} hops={hh_b} (next freezer re-derives, r587)")

receipt["verdict"] = "ADMIT"
receipt["ts"] = "2026-10-04T15:4x+08:00"
with open(os.path.join(ROOT, "results", "_r678bmb_w118_band_gate.json"), "w",
          encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("W118 BAND GATE ADMIT rc0 -- freeze edits may land")
