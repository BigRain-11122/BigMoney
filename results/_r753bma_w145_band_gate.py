# -*- coding: utf-8 -*-
"""r753 bm-a W145 freeze-window band gate -- dual-window derive parity with the
pre-seat probe (r587/r384 pattern), plus own-seat presence check (r374 dual-dir
law + r565 published=reserved).  Runs BEFORE the freeze edits land.
Bloodline: r752 _r752bma_w144_band_gate.py verbatim + W145 facts
(STAIRCASE GEOMETRY fourth instance, E36 card: A = first-clean past the
registered W144 B band -- the arithmetic continuation 333_604..335_603 is
REFUSED at its own start by the W144 B band 333_604..333_803, hops=1,
A base == prior-B tail+1 machine-checkable, A-hops-prior-B fourth instance;
B = first-clean past the own-wave A window -- the arithmetic continuation
333_804..334_003 is CLEAN on the registered universe but lands INSIDE the
W145 own-wave A window, same-freeze mutual exclusion (W141 precedent, leg2
law), reserved walk -> 335_804..336_003, hops=1, B base == own-A tail+1
machine-checkable, non-rotational r587 forward-monotone assert enforced
in-walk).
Seat path note: the W145 seat MSG (r753 seat commit 55c2a1715, delivered via
two-hop merge push d5fdbb317 -- first push raced origin forward = r524
behind-signal, merge-mode closeout, zero --no-verify) sits at
fleet/inbox/ pending bm-c ack, so leg0b reads it there -- dual-dir scan
unchanged.
Receipt -> results/_r753bma_w145_band_gate.json
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
SEAT_PATH = "fleet/inbox/MSG-2026-10-06-023x-bma-w145-seat.md"
W144_A, W144_B = (331_604, 333_603), (333_604, 333_803)
WIDTH_A, WIDTH_B = 2_000, 200
N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
CROSSFACE_PROBE_POINTS = (95_004, 95_006)
LFC_ACTUAL, OPTIONS_ACTUAL = (30_000, 30_099), (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
receipt = {"probe": "r753 W145 freeze-window band gate", "legs": {}}


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
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 145)), \
    f"leg0 registry keys drift: tail {keys[-5:]}"
assert N1_BANDS[144]["a"] == W144_A and N1_BANDS[144]["b_exit"] == W144_B \
    and N1_BANDS[144].get("engine_owner") == "bm-a", "leg0 W144 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 134 and len(bma_rows) == 60, "leg0 ordinal drift"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W144",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 135, "bma_ordinal": 61}
print(f"leg0: {len(N1_BANDS)} rows tail=W144, owner=134 -> 135th wave, bm-a 61st owned")

# --- leg 0b: OWN seat published on origin (r565); zero OTHER W145 seats ---------
r = subprocess.run(["git", "show", f"origin/main:{SEAT_PATH}"], cwd=ROOT,
                   capture_output=True)
assert r.returncode == 0, "leg0b failed: own W145 seat MSG NOT on origin (r565)"
seat_txt = r.stdout.decode("utf-8", "replace")
assert "A 333_804..335_803" in seat_txt and "B 335_804..336_003" in seat_txt, \
    "leg0b failed: seat bands mismatch"
_r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                    capture_output=True)
seats = [ln for ln in _r.stdout.decode("utf-8").splitlines()
         if "w145" in ln.lower() and "seat" in ln.lower()]
assert seats == [SEAT_PATH], f"leg0b failed: unexpected W145 seats: {seats}"
receipt["legs"]["leg0b"] = {"own_seat_on_origin": True, "other_seats": 0,
                            "seat_commit": "55c2a1715 (two-hop merge delivery d5fdbb317, r524 law zero --no-verify)"}
print("leg0b: own seat on origin (inbox/ path, pending bm-c ack), zero other W145 seats (r374 dual-dir scan)")

# --- leg 1: derive identical to pre-seat probe ----------------------------------
ARITH_A = (W144_A[1] + 1, W144_A[1] + WIDTH_A)
ARITH_B = (W144_B[1] + 1, W144_B[1] + WIDTH_B)
assert ARITH_A == (333_604, 335_603) and ARITH_B == (333_804, 334_003), "leg1 drift"


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
assert (fc_a, hops_a) == ((333_804, 335_803), 1), f"leg1 A derive fork: {fc_a}"
assert (fc_b_naive, hops_b_naive) == ((333_804, 334_003), 0), \
    f"leg1 naive-B derive fork: {fc_b_naive}"
assert (fc_b, hops_b) == ((335_804, 336_003), 1), f"leg1 B derive fork: {fc_b}"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
assert fc_a[0] == W144_B[1] + 1 and fc_b[0] == fc_a[1] + 1, \
    "leg1 staircase machine-checks failed (A base != prior-B tail+1 or B base != own-A tail+1)"
receipt["legs"]["leg1"] = {"A": "333_804..335_803", "hops_A": 1,
                           "B": "335_804..336_003", "hops_B": 1,
                           "B_naive_first_clean": "333_804..334_003",
                           "B_naive_hops": 0,
                           "B_hop_chain": b_trace,
                           "A_semantics": ("A arithmetic continuation 333_604..335_603 "
                           "REFUSED at its own start by the registered W144 B band "
                           "333_604..333_803 (as the r752 gate-tail projection "
                           "note anticipated); honest forward walk hops past it -> "
                           "333_804..335_803, hops=1, non-rotational r587 "
                           "forward-monotone assert in-walk; A base == prior-wave "
                           "B tail+1 machine-checkable (A-hops-prior-B staircase "
                           "fourth instance, E36 card)"),
                           "B_semantics": ("B arithmetic continuation 333_804..334_003 "
                           "CLEAN on the registered universe but lands INSIDE the "
                           "W145 own-wave A window -- same-freeze mutual exclusion "
                           "(W141 precedent, leg2 law) -- the reserved walk jumps "
                           "to 335_804 -> first-clean 335_804..336_003, hops=1, "
                           "non-rotational r587 forward-monotone assert in-walk; "
                           "B base == own-wave A tail+1 machine-checkable relation"),
                           "derive_parity_with_pre_seat": True}
print("leg1: A 333_804..335_803 hops=1 + B 335_804..336_003 hops=1 "
      "(identical to pre-seat derive, zero fork; staircase geometry held: "
      "A hops past prior B, B hops past own A)")

# --- leg 2: full reserved universe conflicts + origin vacancy --------------------
conflicts = []
for tag, band in (("A", fc_a), ("B", fc_b)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} x W145-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W145-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W145-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W145-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W145-{tag} (MSG-183x)")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W145-{tag}")
assert not conflicts, f"leg2 failed: W145 conflicts {conflicts}"
assert not overlaps(fc_a, fc_b), "leg2 failed: W145 A/B overlap"
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
    encoding="utf-8")
assert '145: {"a": (333_804' not in out, \
    "leg2 failed: W145 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
    encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W145"' not in outn1, \
    "leg2 failed: W145 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W145_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W145 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0, "origin_vacancy": True,
                          "seat": SEAT_PATH, "push": "55c2a1715 -> d5fdbb317 (two-hop merge delivery, r524 law)"}
print("leg2: zero conflicts; origin vacancy holds (row/configs/prereg/seat)")

# --- leg 3: W146+ projection (gate tail, next freezer re-derives) -----------------
(fc146_a, h146a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc146_b, h146b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside146 = overlaps(fc146_b, fc146_a)
receipt["legs"]["leg3"] = {"W146p_A": f"{fc146_a[0]}..{fc146_a[1]}",
                           "hops_A": h146a,
                           "W146p_B": f"{fc146_b[0]}..{fc146_b[1]}",
                           "hops_B": h146b,
                           "W146p_B_lands_inside_W146p_A": inside146,
                           "note": ("W146+ naive projection on the pre-W145-"
                                    "registration universe: A first-clean "
                                    "335_804..337_803 CLEAN hops=0 / B "
                                    "first-clean 336_004..336_203 CLEAN hops=0 "
                                    "-- naive B lands INSIDE the naive A "
                                    "window AND the registered W145 B band "
                                    "335_804..336_003 will refuse the naive "
                                    "W146 A window once registered; W146 "
                                    "freezer MUST re-derive on the post-W145 "
                                    "universe AND reserve the own-wave A "
                                    "window when deriving B (W141 precedent, "
                                    "same-freeze mutual exclusion, leg2 law, "
                                    "E36 staircase card) -- never transcribe r587")}
print(f"leg3: W146+ projection A {fc146_a[0]}..{fc146_a[1]} hops={h146a} / "
      f"B {fc146_b[0]}..{fc146_b[1]} hops={h146b} (B inside A: {inside146}; "
      "next freezer re-derives; same-freeze mutual exclusion + staircase "
      "mandatory at W146)")

receipt["verdict"] = "ADMIT"
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r753bma_w145_band_gate.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print("W145 BAND GATE rc0 ADMIT: A 333_804..335_803 + B 335_804..336_003 "
      "(dual-window derive parity held; staircase geometry: A hops past "
      "prior B, B first-clean past own-wave A; receipt written)")
