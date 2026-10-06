# -*- coding: utf-8 -*-
"""r783 bm-a W160 freeze-window band gate (single-state gate; dual-window derive
parity with the r782 pre-seat probe per r587/r763/r764/r766/r767/r769/r772/r779
precedent).
leg0: live registry shape (157 rows, tail=W159, ordinal 150, bm-a 76th)
leg0b: own W160 seat on origin + ZERO other W160 seats (r374 dual-direction
       scan: inbox + processed), commit-time ordering per fleet README sec.4
leg1: derive re-run in the freeze window, parity with the r782 pre-seat probe
       receipt asserted band-for-band, hop-for-hop
leg2: full reserved-universe conflict scan + origin vacancy re-check
leg3: W161+ projection (gate tail; next freezer re-derives, never transcribed)
Bloodline: r779 _r779bma_w159_band_gate.py machinery (derive core verbatim)."""
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
SEAT_NAME = "MSG-2026-10-06-162x-bma-w160-seat.md"
receipt = {"gate": "r783 W160 band gate", "legs": {}}


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

# --- leg 0: registry shape ------------------------------------------------------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 160))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W159_A = tuple(N1_BANDS[159]["a"])
W159_B = tuple(N1_BANDS[159]["b_exit"])
assert W159_A == (364_604, 366_603) and W159_B == (366_604, 366_803) and \
    N1_BANDS[159].get("engine_owner") == "bm-a", "leg0 failed: W159 row drift"
assert tuple(N1_BANDS[158]["a"]) == (362_404, 364_403) and \
    tuple(N1_BANDS[158]["b_exit"]) == (364_404, 364_603), "leg0 failed: W158 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 149 and len(bma_rows) == 75, "leg0 ordinal drift"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W159",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 150, "bma_ordinal": 76}
print(f"leg0: {len(N1_BANDS)} rows tail=W159, owner={len(owner_rows)} -> 150th wave, bm-a 76th owned")

# --- leg 0b: own seat on origin + zero other W160 seats (r374 dual-direction) ---
r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                    "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                   capture_output=True)
seats = [ln for ln in r.stdout.decode("utf-8").splitlines()
         if "w160" in ln.lower() and "seat" in ln.lower()]
own = [s for s in seats if s.endswith(SEAT_NAME)]
others = [s for s in seats if not s.endswith(SEAT_NAME)]
assert len(own) == 1, f"leg0b failed: own W160 seat not on origin: {seats}"
assert others == [], f"leg0b failed: other W160 seats exist: {others}"
receipt["legs"]["leg0b"] = {"own_seat_on_origin": True, "other_seats": 0,
                            "seat_commit": "566ec5f86 published (r782 pre-seat push via merge-absorb window, r565 law; zero --no-verify)"}
print(f"leg0b: own seat {SEAT_NAME} on origin, zero other seats (dual-dir)")

# --- leg 1: freeze-window derive re-run, parity with r782 pre-seat probe --------
ARITH_A = (W159_A[1] + 1, W159_A[1] + WIDTH_A)
ARITH_B = (W159_B[1] + 1, W159_B[1] + WIDTH_B)


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
b_trace = []
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace,
                             extra_bands=(fc_a,))
(fc_b_naive, hops_b_naive) = first_clean(ARITH_B[0], WIDTH_B)
assert fc_a[0] == W159_B[1] + 1, "leg1 staircase A base != prior-B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], "leg1 A not refused (staircase expected)"
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
probe_receipt = json.load(open(os.path.join(ROOT, "results",
                                            "_r782bma_w160_probe_receipt.json"),
                               encoding="utf-8"))
pleg1 = probe_receipt["legs"]["leg1"]
assert list(fc_a) == pleg1["A"] and hops_a == pleg1["hops_A"], "leg1 parity drift A"
assert list(fc_b) == pleg1["B"] and hops_b == pleg1["hops_B"], "leg1 parity drift B"
assert b_trace == pleg1["B_hop_chain"], "leg1 parity drift B hop chain"
assert list(ARITH_A) == pleg1["ARITH_A"] and \
    list(fc_b_naive) == pleg1["B_naive_first_clean"], "leg1 parity drift naive faces"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace, "parity_with_probe": True,
}
print(f"leg1: A {fc_a[0]}..{fc_a[1]} hops={hops_a} + B {fc_b[0]}..{fc_b[1]} hops={hops_b} -- parity with pre-seat probe HELD")

# --- leg 2: full reserved universe conflict scan + origin vacancy re-check -----
conflicts = []
for tag, band in (("A", fc_a), ("B", fc_b)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} x W160-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W160-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W160-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W160-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W160-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W160-{tag}")
assert not conflicts, f"leg2 failed: W160 conflicts {conflicts}"
out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                              cwd=ROOT, encoding="utf-8")
assert '160: {"a": (' not in out, "leg2 failed: W160 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
                                cwd=ROOT, encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W160"' not in outn1, "leg2 failed: W160 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                  "research/PERPETUAL_N1_W160_PREREG.md"], cwd=ROOT,
                                 encoding="utf-8").strip()
assert not outpre, "leg2 failed: W160 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0, "origin_vacancy": True}
print("leg2: zero conflicts, origin vacancy held (row/configs/prereg absent)")

# --- leg 3: W161+ projection (gate tail) ----------------------------------------
(fc161_a, h160a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc161_b, h160b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside160 = overlaps(fc161_b, fc161_a)
receipt["legs"]["leg3"] = {"W161p_A": f"{fc161_a[0]}..{fc161_a[1]}", "hops_A": h160a,
                           "W161p_B": f"{fc161_b[0]}..{fc161_b[1]}", "hops_B": h160b,
                           "W161p_B_lands_inside_W161p_A": inside160,
                           "note": "naive-B-inside-naive-A; the registered W160 B band 368_804..369_003 will refuse the naive W161 A window; W161 freezer MUST re-derive on the post-W160 universe AND reserve the own-wave A window when deriving B (W141 precedent, leg2 law, E36 staircase card)"}
print(f"leg3: W161+ projection A {fc161_a[0]}..{fc161_a[1]} hops={h160a} / B {fc161_b[0]}..{fc161_b[1]} hops={h160b} (B inside A: {inside160})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r783bma_w160_band_gate.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W160 BAND GATE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (gate receipt written)")
