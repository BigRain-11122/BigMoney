# -*- coding: utf-8 -*-
"""r772 bm-a W157 freeze-window band gate (single-state gate; dual-window derive
parity with the r772 pre-seat probe per r587/r763/r764/r766/r767/r769 precedent).
leg0: live registry shape (154 rows, tail=W156, ordinal 147, bm-a 73rd)
leg0b: own W157 seat on origin + ZERO other W157 seats (r374 dual-direction
       scan: inbox + processed), commit-time ordering per fleet README sec.4
leg1: derive re-run in the freeze window, parity with the pre-seat probe
       receipt asserted band-for-band, hop-for-hop
leg2: full reserved-universe conflict scan + origin vacancy re-check
leg3: W158+ projection (gate tail; next freezer re-derives, never transcribed)
Bloodline: r769 W156 gate machinery (derive core verbatim from the probe)."""
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
SEAT_NAME = "MSG-2026-10-06-113x-bma-w157-seat.md"
receipt = {"gate": "r772 W157 band gate", "legs": {}}


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
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 157))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W156_A = tuple(N1_BANDS[156]["a"])
W156_B = tuple(N1_BANDS[156]["b_exit"])
assert W156_A == (358_004, 360_003) and W156_B == (360_004, 360_203) and \
    N1_BANDS[156].get("engine_owner") == "bm-a", "leg0 failed: W156 row drift"
assert tuple(N1_BANDS[155]["a"]) == (355_804, 357_803) and \
    tuple(N1_BANDS[155]["b_exit"]) == (357_804, 358_003), "leg0 failed: W155 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 146 and len(bma_rows) == 72, "leg0 ordinal drift"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W156",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 147, "bma_ordinal": 73}
print(f"leg0: {len(N1_BANDS)} rows tail=W156, owner={len(owner_rows)} -> 147th wave, bm-a 73rd owned")

# --- leg 0b: own seat on origin + zero other W157 seats (r374 dual-direction) ---
r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                    "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                   capture_output=True)
seats = [ln for ln in r.stdout.decode("utf-8").splitlines()
         if "w157" in ln.lower() and "seat" in ln.lower()]
own = [s for s in seats if s.endswith(SEAT_NAME)]
others = [s for s in seats if not s.endswith(SEAT_NAME)]
assert len(own) == 1, f"leg0b failed: own W157 seat not on origin: {seats}"
assert others == [], f"leg0b failed: other W157 seats exist: {others}"
receipt["legs"]["leg0b"] = {"own_seat_on_origin": True, "other_seats": 0,
                            "seat_commit": "4af40c72d published (r772 pre-seat push, r565 law; direct fast-forward behind-0, W156 finalize products same-window 0c16da657)"}
print(f"leg0b: own seat {SEAT_NAME} on origin, zero other seats (dual-dir)")

# --- leg 1: freeze-window derive re-run, parity with pre-seat probe ------------
ARITH_A = (W156_A[1] + 1, W156_A[1] + WIDTH_A)
ARITH_B = (W156_B[1] + 1, W156_B[1] + WIDTH_B)


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
assert fc_a[0] == W156_B[1] + 1, "leg1 staircase A base != prior-B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], "leg1 A not refused (staircase expected)"
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
probe_receipt = json.load(open(os.path.join(ROOT, "results",
                                            "_r772bma_w157_probe_receipt.json"),
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W157-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W157-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W157-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W157-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W157-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W157-{tag}")
assert not conflicts, f"leg2 failed: W157 conflicts {conflicts}"
out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                              cwd=ROOT, encoding="utf-8")
assert '157: {"a": (' not in out, "leg2 failed: W157 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
                                cwd=ROOT, encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W157"' not in outn1, "leg2 failed: W157 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                  "research/PERPETUAL_N1_W157_PREREG.md"], cwd=ROOT,
                                 encoding="utf-8").strip()
assert not outpre, "leg2 failed: W157 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0, "origin_vacancy": True}
print("leg2: zero conflicts, origin vacancy held (row/configs/prereg absent)")

# --- leg 3: W158+ projection (gate tail) ----------------------------------------
(fc158_a, h157a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc158_b, h157b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside157 = overlaps(fc158_b, fc158_a)
receipt["legs"]["leg3"] = {"W158p_A": f"{fc158_a[0]}..{fc158_a[1]}", "hops_A": h157a,
                           "W158p_B": f"{fc158_b[0]}..{fc158_b[1]}", "hops_B": h157b,
                           "W158p_B_lands_inside_W158p_A": inside157,
                           "note": "naive-B-inside-naive-A; the registered W157 B band 362_204..362_403 will refuse the naive W158 A window; W158 freezer MUST re-derive on the post-W157 universe AND reserve the own-wave A window when deriving B (W141 precedent, leg2 law, E36 staircase card)"}
print(f"leg3: W158+ projection A {fc158_a[0]}..{fc158_a[1]} hops={h157a} / B {fc158_b[0]}..{fc158_b[1]} hops={h157b} (B inside A: {inside157})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r772bma_w157_band_gate.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W157 BAND GATE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (gate receipt written)")
