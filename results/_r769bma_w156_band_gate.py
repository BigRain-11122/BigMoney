# -*- coding: utf-8 -*-
"""r769 bm-a W156 freeze-window band gate (single-state gate; dual-window derive
parity with the r769 pre-seat probe per r587/r763/r764/r766/r767 precedent).
leg0: live registry shape (153 rows, tail=W155, ordinal 146, bm-a 72st)
leg0b: own W156 seat on origin + ZERO other W156 seats (r374 dual-direction
       scan: inbox + processed), commit-time ordering per fleet README sec.4
leg1: derive re-run in the freeze window, parity with the pre-seat probe
       receipt asserted band-for-band, hop-for-hop
leg2: full reserved-universe conflict scan + origin vacancy re-check
leg3: W157+ projection (gate tail; next freezer re-derives, never transcribed)
Bloodline: r767 W155 gate machinery (derive core verbatim from the probe)."""
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
SEAT_NAME = "MSG-2026-10-06-1009-bma-w156-seat.md"
receipt = {"gate": "r769 W156 band gate", "legs": {}}


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
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 156))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W155_A = tuple(N1_BANDS[155]["a"])
W155_B = tuple(N1_BANDS[155]["b_exit"])
assert W155_A == (355_804, 357_803) and W155_B == (357_804, 358_003) and \
    N1_BANDS[155].get("engine_owner") == "bm-a", "leg0 failed: W155 row drift"
assert tuple(N1_BANDS[154]["a"]) == (353_604, 355_603) and \
    tuple(N1_BANDS[154]["b_exit"]) == (355_604, 355_803), "leg0 failed: W153 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 145 and len(bma_rows) == 71, "leg0 ordinal drift"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W155",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 146, "bma_ordinal": 72}
print(f"leg0: {len(N1_BANDS)} rows tail=W155, owner={len(owner_rows)} -> 146th wave, bm-a 72st owned")

# --- leg 0b: own seat on origin + zero other W156 seats (r374 dual-direction) ---
r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                    "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                   capture_output=True)
seats = [ln for ln in r.stdout.decode("utf-8").splitlines()
         if "w156" in ln.lower() and "seat" in ln.lower()]
own = [s for s in seats if s.endswith(SEAT_NAME)]
others = [s for s in seats if not s.endswith(SEAT_NAME)]
assert len(own) == 1, f"leg0b failed: own W156 seat not on origin: {seats}"
assert others == [], f"leg0b failed: other W156 seats exist: {others}"
receipt["legs"]["leg0b"] = {"own_seat_on_origin": True, "other_seats": 0,
                            "seat_commit": "ffce2936f published (r769 pre-seat push, r565 law; W155 finalize products + bm-c r611 wave merge-absorbed in the same-window push d27177b43)"}
print(f"leg0b: own seat {SEAT_NAME} on origin, zero other seats (dual-dir)")

# --- leg 1: freeze-window derive re-run, parity with pre-seat probe ------------
ARITH_A = (W155_A[1] + 1, W155_A[1] + WIDTH_A)
ARITH_B = (W155_B[1] + 1, W155_B[1] + WIDTH_B)


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
assert fc_a[0] == W155_B[1] + 1, "leg1 staircase A base != prior-B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], "leg1 A not refused (staircase expected)"
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
probe_receipt = json.load(open(os.path.join(ROOT, "results",
                                            "_r769bma_w156_probe_receipt.json"),
                               encoding="utf-8"))
pleg1 = probe_receipt["legs"]["leg1"]
assert list(fc_a) == pleg1["A"] and hops_a == pleg1["hops_A"], "leg1 parity drift A"
assert list(fc_b) == pleg1["B"] and hops_b == pleg1["hops_B"], "leg1 parity drift B"
assert b_trace == pleg1["B_hop_chain"], "leg1 parity drift B hop chain"
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W156-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W156-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W156-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W156-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W156-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W156-{tag}")
assert not conflicts, f"leg2 failed: W156 conflicts {conflicts}"
out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                              cwd=ROOT, encoding="utf-8")
assert '156: {"a": (' not in out, "leg2 failed: W156 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
                                cwd=ROOT, encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W156"' not in outn1, "leg2 failed: W156 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                  "research/PERPETUAL_N1_W156_PREREG.md"], cwd=ROOT,
                                 encoding="utf-8").strip()
assert not outpre, "leg2 failed: W156 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0, "origin_vacancy": True}
print("leg2: zero conflicts, origin vacancy held (row/configs/prereg absent)")

# --- leg 3: W157+ projection (gate tail) ----------------------------------------
(fc157_a, h156a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc157_b, h156b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside156 = overlaps(fc157_b, fc157_a)
receipt["legs"]["leg3"] = {"W157p_A": f"{fc157_a[0]}..{fc157_a[1]}", "hops_A": h156a,
                           "W157p_B": f"{fc157_b[0]}..{fc157_b[1]}", "hops_B": h156b,
                           "W157p_B_lands_inside_W157p_A": inside156,
                           "note": "naive-B-inside-naive-A; the registered W156 B band 357_804..358_003 will refuse the naive W156 A window; W156 freezer MUST re-derive on the post-W156 universe AND reserve the own-wave A window when deriving B (W141 precedent, leg2 law, E36 staircase card)"}
print(f"leg3: W157+ projection A {fc157_a[0]}..{fc157_a[1]} hops={h156a} / B {fc157_b[0]}..{fc157_b[1]} hops={h156b} (B inside A: {inside156})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r769bma_w156_band_gate.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W156 BAND GATE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (gate receipt written)")
