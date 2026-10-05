# -*- coding: utf-8 -*-
"""r747 bm-a W141 freeze-window band gate -- dual-window derive parity with the
pre-seat probe (r587/r384 pattern), plus own-seat presence check (r374 dual-dir
law + r565 published=reserved).  Runs BEFORE the freeze edits land.
Bloodline: r745 _r745bma_w140_band_gate.py verbatim + W141 facts
(A = arithmetic continuation from the registered W140 A tail 325_003+1
CLEAN hops=0; B = first-clean past the own-wave A window -- the arithmetic
continuation 94_801..95_000 is REFUSED by probe seed 95_000; the honest
forward walk lands 325_004..325_203 inside the W141 A window after 116
hops, then continues past the own-wave A window (same-freeze mutual
exclusion, leg2 law) to 327_004..327_203, 117 hops total, non-rotational
r587 forward-monotone assert enforced in-walk).
Receipt -> results/_r747bma_w141_band_gate.json
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
SEAT_PATH = "fleet/inbox/MSG-2026-10-05-231x-bma-w141-seat.md"
W140_A, W140_B = (323_004, 325_003), (94_601, 94_800)
WIDTH_A, WIDTH_B = 2_000, 200
N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
CROSSFACE_PROBE_POINTS = (95_004, 95_006)
LFC_ACTUAL, OPTIONS_ACTUAL = (30_000, 30_099), (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
receipt = {"probe": "r747 W141 freeze-window band gate", "legs": {}}


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
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 141)), \
    f"leg0 registry keys drift: tail {keys[-5:]}"
assert N1_BANDS[140]["a"] == W140_A and N1_BANDS[140]["b_exit"] == W140_B \
    and N1_BANDS[140].get("engine_owner") == "bm-a", "leg0 W140 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 130 and len(bma_rows) == 56, "leg0 ordinal drift"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W140",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 131, "bma_ordinal": 57}
print(f"leg0: {len(N1_BANDS)} rows tail=W140, owner=130 -> 131st wave, bm-a 57th owned")

# --- leg 0b: OWN seat published on origin (r565); zero OTHER W141 seats ---------
r = subprocess.run(["git", "show", f"origin/main:{SEAT_PATH}"], cwd=ROOT,
                   capture_output=True)
assert r.returncode == 0, "leg0b failed: own W141 seat MSG NOT on origin (r565)"
seat_txt = r.stdout.decode("utf-8", "replace")
assert "A 325_004..327_003" in seat_txt and "B 327_004..327_203" in seat_txt, \
    "leg0b failed: seat bands mismatch"
_r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                    capture_output=True)
seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
         if "w141" in ln.lower() and "seat" in ln.lower()]
assert seats == [SEAT_PATH], f"leg0b failed: unexpected W141 seats: {seats}"
receipt["legs"]["leg0b"] = {"own_seat_on_origin": True, "other_seats": 0,
                            "seat_commit": "aaa4d9be8 (pre-freeze push, plain fast-forward delivery, zero --no-verify)"}
print("leg0b: own seat on origin, zero other W141 seats (r374 dual-dir scan)")

# --- leg 1: derive identical to pre-seat probe ----------------------------------
ARITH_A = (W140_A[1] + 1, W140_A[1] + WIDTH_A)
ARITH_B = (W140_B[1] + 1, W140_B[1] + WIDTH_B)
assert ARITH_A == (325_004, 327_003) and ARITH_B == (94_801, 95_000), "leg1 drift"


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
            trace.append({"hop": hops + 1, "window": [lo, hi], "jump_to": jump})
        lo = jump
        prev_lo = lo
        hops += 1


(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A)
(fc_b_naive, hops_b_naive) = first_clean(ARITH_B[0], WIDTH_B)
b_trace = []
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace,
                             extra_bands=(fc_a,))
assert (fc_a, hops_a) == ((325_004, 327_003), 0), f"leg1 A derive fork: {fc_a}"
assert (fc_b_naive, hops_b_naive) == ((325_004, 325_203), 116), \
    f"leg1 naive-B derive fork: {fc_b_naive}"
assert (fc_b, hops_b) == ((327_004, 327_203), 117), f"leg1 B derive fork: {fc_b}"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {"A": "325_004..327_003", "hops_A": 0,
                           "B": "327_004..327_203", "hops_B": 117,
                           "B_naive_first_clean": "325_004..325_203",
                           "B_naive_hops": 116,
                           "B_hop_chain": b_trace,
                           "B_semantics": ("B arithmetic continuation 94_801..95_000 "
                           "REFUSED by probe seed 95_000 (r335 leg); honest forward "
                           "walk lands 325_004..325_203 inside the W141 own-wave A "
                           "window after 116 hops -- same-freeze mutual exclusion "
                           "(leg2 law) -- continues past the own-wave A window to "
                           "327_004..327_203, 117 hops total; non-rotational r587 "
                           "forward-monotone assert in-walk; B base == own-wave A "
                           "tail+1 machine-checkable relation"),
                           "derive_parity_with_pre_seat": True}
print("leg1: A 325_004..327_003 hops=0 + B 327_004..327_203 hops=117 "
      "(identical to pre-seat derive, zero fork; naive B lands inside own-wave A "
      "-> same-freeze mutual exclusion applied)")

# --- leg 2: full reserved universe conflicts + origin vacancy --------------------
conflicts = []
for tag, band in (("A", fc_a), ("B", fc_b)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} x W141-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W141-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W141-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W141-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W141-{tag} (MSG-183x)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W141-{tag}")
assert not conflicts, f"leg2 failed: W141 conflicts {conflicts}"
assert not overlaps(fc_a, fc_b), "leg2 failed: W141 A/B overlap"
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '141: {"a": (325_004' not in out, \
    "leg2 failed: W141 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W141"' not in outn1, \
    "leg2 failed: W141 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W141_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W141 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0, "origin_vacancy": True,
                          "seat": SEAT_PATH, "push": "aaa4d9be8 (pre-freeze push, plain fast-forward delivery, zero --no-verify)"}
print("leg2: zero conflicts; origin vacancy holds (row/configs/prereg/seat)")

# --- leg 3: W142+ projection (gate tail, next freezer re-derives) -----------------
(fc142_a, h142a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc142_b, h142b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside142 = overlaps(fc142_b, fc142_a)
receipt["legs"]["leg3"] = {"W142p_A": f"{fc142_a[0]}..{fc142_a[1]}",
                           "hops_A": h142a,
                           "W142p_B": f"{fc142_b[0]}..{fc142_b[1]}",
                           "hops_B": h142b,
                           "W142p_B_lands_inside_W142p_A": inside142,
                           "note": ("W142+ naive projection on the pre-W141-"
                                    "registration universe: A 327_004..329_003 "
                                    "CLEAN hops=0 / B 327_204..327_403 CLEAN "
                                    "hops=0 -- naive B lands INSIDE the naive A "
                                    "window AND the W141 B band 327_004..327_203 "
                                    "will refuse the naive W142 A window once "
                                    "registered; W142 freezer MUST re-derive on "
                                    "the post-W141 universe AND reserve the "
                                    "own-wave A window when deriving B (W141 "
                                    "precedent, same-freeze mutual exclusion, "
                                    "leg2 law) -- never transcribe r587")}
print(f"leg3: W142+ projection A {fc142_a[0]}..{fc142_a[1]} hops={h142a} / "
      f"B {fc142_b[0]}..{fc142_b[1]} hops={h142b} (B inside A: {inside142}; "
      "next freezer re-derives; same-freeze mutual exclusion mandatory at W142)")

receipt["verdict"] = "ADMIT"
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r747bma_w141_band_gate.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print("W141 BAND GATE rc0 ADMIT: A 325_004..327_003 + B 327_004..327_203 "
      "(dual-window derive parity held; B first-clean past own-wave A, "
      "same-freeze mutual exclusion; receipt written)")
