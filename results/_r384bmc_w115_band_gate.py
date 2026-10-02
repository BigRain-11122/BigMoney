# -*- coding: utf-8 -*-
"""W115 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W115 candidate = first FREE number after the REGISTERED W114 row (bm-a r594
freeze ddacf2616, bands A 271_004..273_003 / B 62_201..62_400). SINGLE STATE
zero seat gap: W2..W114 all registered (W113 bm-c eeb062290 + W114 bm-a
ddacf2616). Own seat MSG-20261002-2130-bmc-w115-seat published=reserved,
pushed to origin ac241dd32 BEFORE this freeze per r565 law (payload = seat
MSG + pre-seat probe results/_r383bmc_w115_probe.py, deletion-set EMPTY,
rev.A = only published face).

Bands (machine-derived, NOT transcribed -- r335/r535/r587 law):
  A 273_004..275_003  (arithmetic continuation from the registered W114 A tail)
  B 62_501..62_700    (arithmetic 62_401..62_600 REFUSED in-band at SEED_REGISTRY
                       grid_sleeve_p1=62_500 mid-window -> pinned D-20261002-05
                       past-hit restart at hit+1; window-step-chain reading
                       62_601..62_800 BANNED per W68-B negative anchor)

r384 bm-c freeze-window run. READ-ONLY vs the live table + origin.
"""
import subprocess, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000

W115_A = (273_004, 275_003)
W115_B = (62_501, 62_700)
W114_TAIL_A = (271_004, 273_003)   # registered W114 (bm-a r594, live table tail)
W114_TAIL_B = (62_201, 62_400)
OWN_SEAT = "MSG-20261002-2130-bmc-w115-seat"

N3R1_USED = (70_000, 70_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
WIDTH_A = 2_000
WIDTH_B = 200

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True, creationflags=CREAT)

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)

# --- leg 0: registry shape + registered-tail parity ---------------------------
keys = sorted(N1_BANDS)
expect_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 115))
assert keys == expect_keys, f"leg0 failed: keys tail drift {keys[-5:]}"
assert N1_BANDS[111]["a"] == (265_004, 267_003) and \
    N1_BANDS[111]["b_exit"] == (61_401, 61_600) and \
    N1_BANDS[111].get("engine_owner") == "bm-b", "leg0 failed: W111 row drift"
assert N1_BANDS[112]["a"] == (267_004, 269_003) and \
    N1_BANDS[112]["b_exit"] == (61_601, 61_800) and \
    N1_BANDS[112].get("engine_owner") == "bm-a", "leg0 failed: W112 row drift"
assert N1_BANDS[113]["a"] == (269_004, 271_003) and \
    N1_BANDS[113]["b_exit"] == (62_001, 62_200) and \
    N1_BANDS[113].get("engine_owner") == "bm-c", "leg0 failed: W113 row drift"
assert N1_BANDS[114]["a"] == W114_TAIL_A and \
    N1_BANDS[114]["b_exit"] == W114_TAIL_B and \
    N1_BANDS[114].get("engine_owner") == "bm-a", "leg0 failed: W114 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
assert len(owner_rows) == 104, f"leg0 failed: engine_owner rows {len(owner_rows)} (expect 104)"
assert len(bmc_rows) == 33, f"leg0 failed: bm-c rows {len(bmc_rows)} (expect 33)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} (W114 bm-a registered); "
      f"engine_owner rows={len(owner_rows)} + candidate -> W115 = 105th engine wave, "
      f"bm-c {len(bmc_rows) + 1}th owned wave by machine-derive")

# --- leg 0b: NO peer W115 seat claim on origin (own seat allowed; r374 dual-dir) -
peer_claims = []
own_seen = False
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w115" in _ln.lower() and "seat" in _ln.lower():
            if OWN_SEAT in _ln:
                own_seen = True
            else:
                peer_claims.append(_ln)
assert not peer_claims, f"leg0b failed: peer W115 seat MSG on origin: {peer_claims}"
assert own_seen, "leg0b failed: own W115 seat MSG NOT on origin (r565 missing)"
print(f"leg0b: zero PEER W115 seat MSGs on origin (inbox+processed dual-dir r374); "
      f"own seat {OWN_SEAT} on origin confirmed (r565 law, push ac241dd32)")

# --- leg 1: first-clean-window derive (pinned D-20261002-05: mid-window hit -> hit+1) --
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))

def first_clean(start, width, tag):
    lo = start; hops = 0
    while True:
        hi = lo + width - 1
        hit = None
        for p in sorted(points):
            if lo <= p <= hi:
                hit = p; break
        if hit is None:
            for b in bands + [LFC_ACTUAL, OPTIONS_ACTUAL] + V1_IN_USE + W1_EXT:
                if overlaps((lo, hi), b):
                    hit = f"band {b}"; break
        if hit is None:
            return (lo, hi), hops
        nxt = (hit + 1) if isinstance(hit, int) else hi + 1
        print(f"  refusal-scan {tag}: window {lo}..{hi} refused at {hit} -> restart {nxt} (D-20261002-05)")
        lo = nxt; hops += 1
        assert hops < 50, "refusal scan runaway"

ca, hops_a = first_clean(W114_TAIL_A[1] + 1, WIDTH_A, "A")
cb, hops_b = first_clean(W114_TAIL_B[1] + 1, WIDTH_B, "B")
assert ca == W115_A, f"leg1-A failed: derived {ca} != {W115_A}"
assert cb == W115_B, f"leg1-B failed: derived {cb} != {W115_B}"
assert hops_a == 0 and hops_b == 1, f"leg1 hops drift A={hops_a} B={hops_b}"
print(f"leg1: A {W115_A[0]}..{W115_A[1]} CLEAN (hops={hops_a}) + "
      f"B {W115_B[0]}..{W115_B[1]} CLEAN (hops={hops_b}, pinned past-hit restart "
      f"over the in-band 62_500 refusal; arithmetic window 62_401..62_600 "
      f"refused at SEED_REGISTRY grid_sleeve_p1=62_500 mid-window 100/200 non-edge)")

# --- leg 2: full-universe conflict scan vs the CANDIDATE bands ------------------
conflicts = []
for tag, band in (("A", W115_A), ("B", W115_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W115-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W115-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W115-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W115-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W115-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W115-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W115-{tag}")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W115-{tag} (r335 leg)")
out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT, encoding="utf-8")
assert "115: {\"a\": (273_004" not in out, "leg2 failed: W115 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT, encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W115"' not in outn1, "leg2 failed: W115 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--", "research/PERPETUAL_N1_W115_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert not outpre, "leg2 failed: W115 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W115 REFUSED:")
    for c in conflicts: print("  -", c)
    sys.exit(1)
print(f"W115 ADMIT: A {W115_A[0]}..{W115_A[1]} + B {W115_B[0]}..{W115_B[1]} "
      f"(A = arithmetic continuation from the registered W114 A tail; B = pinned "
      f"D-20261002-05 past-hit restart over the in-band 62_500 refusal) -- clean vs "
      f"all registered rows + registry + probes/actuals -- engine_owner=bm-c (own "
      f"seat {OWN_SEAT} on origin BEFORE this freeze per r565, push ac241dd32, "
      f"payload = seat MSG + pre-seat probe, deletion-set EMPTY, rev.A only face). "
      f"NOT a re-pick (R250: W115 bands were never assigned).")

# --- W116+ projection (pinned D-20261002-05 semantics: mid-window hit -> hit+1) --
w116_a = (W115_A[1] + 1, W115_A[1] + WIDTH_A)
w116_b = (W115_B[1] + 1, W115_B[1] + WIDTH_B)
(fc116_a, h116a) = first_clean(w116_a[0], WIDTH_A, "W116-A")
(fc116_b, h116b) = first_clean(w116_b[0], WIDTH_B, "W116-B")
print(f"W116+ projection (pinned law): A first-clean {fc116_a[0]}..{fc116_a[1]} "
      f"hops={h116a} -> CLEAN (verify at W116 prereg); "
      f"B first-clean {fc116_b[0]}..{fc116_b[1]} hops={h116b} -> CLEAN "
      f"(verify at W116 prereg). Cross-check vs own seat MSG disclosure "
      f"(A 275_004..277_003 / B 62_701..62_900): machine-derived at this window, "
      f"next freezer must re-derive never transcribe (r587 law).")
