# -*- coding: utf-8 -*-
"""W105 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W105 candidate = first FREE number after the REGISTERED W103 row (bm-b r584
freeze, landed origin fbbde996f) SKIPPING the published W104 seat (bm-a
MSG-20261002-1712, published=reserved r518-1). A side = skip-past-published
then arithmetic continuation; B side = skip-past-published then the
D-20261002-05 pinned past-hit restart (arithmetic window 59_801..60_000
REFUSED at SEED_REGISTRY div_lowvol_p1=60_000 upper-edge endpoint ->
60_001..60_200; both readings converge, W74-B/W81 edge family, no fork).

Bands (machine-derived, NOT transcribed -- r335/r535 law):
  A 253_004..255_003  (skip W104 pub 251_004..253_003, hops=1) -- verify CLEAN
  B 60_001..60_200    (skip W104 pub 59_601..59_800 + 60_000 edge hit, hops=2)

Machine-verified against: all registered N1 wave bands (W2..W103 live), the
PUBLISHED W104 seat bands (skip-past-published r518-1 leg), N3-R1 used-seed
band 70_000..70_005 (MSG-183x r529 mandatory leg), probe cluster
95_000..95_003 (r335 leg), v1 in-use + W1 ext bands, live SEED_REGISTRY
values, N2/N4 probe points, N2-W15 draft probe points, lfc/options actuals,
and the bm-c W105 seat MSG-20261002-1738 (own, on origin per r565; NO peer
W105 seat allowed).

r376 bm-c freeze-window run. READ-ONLY vs the live table + origin.
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000

W105_A = (253_004, 255_003)        # candidate (derived, gate must confirm)
W105_B = (60_001, 60_200)          # pinned-skip prediction (gate derives)
W103_TAIL_A = (249_004, 251_003)   # registered W103 (bm-b r584, live table tail)
W103_TAIL_B = (59_401, 59_600)
W104_PUB_A = (251_004, 253_003)    # bm-a W104 published seat (r518-1 reserved)
W104_PUB_B = (59_601, 59_800)
OWN_SEAT = "MSG-20261002-1738-bmc"   # own W105 seat MSG (pushed pre-freeze r565)
W104_SEAT = "MSG-20261002-1712-bma"  # bm-a W104 seat MSG (skip target, leg0c)

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

subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)

# --- leg 0: registry shape + registered-tail parity ---------------------------
keys = sorted(N1_BANDS)
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 104)), \
    f"leg0 failed: keys tail drift {keys[-5:]}"
assert N1_BANDS[103]["a"] == W103_TAIL_A and \
    N1_BANDS[103]["b_exit"] == W103_TAIL_B and \
    N1_BANDS[103].get("engine_owner") == "bm-b", "leg0 failed: W103 row drift"
assert N1_BANDS[102]["a"] == (247_004, 249_003) and \
    N1_BANDS[102]["b_exit"] == (59_201, 59_400) and \
    N1_BANDS[102].get("engine_owner") == "bm-c", "leg0 failed: W102 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
assert len(owner_rows) == 93, \
    f"leg0 failed: engine_owner rows {len(owner_rows)} (expect 93)"
assert len(bmc_rows) == 30, \
    f"leg0 failed: bm-c rows {len(bmc_rows)} (expect 30)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} (W103 bm-b, "
      f"W104 seat-published unregistered honest note); engine_owner rows="
      f"{len(owner_rows)} + candidate -> W105 = bm-c 31st owned, "
      f"NINETY-FOURTH engine wave by machine-derive (93 registered + "
      f"candidate; prose ordinal drift disclosed per r359 law)")

# --- leg 0b: NO peer W105 seat claim on origin (own seat allowed) ---------------
peer_claims = []
_names_all = []
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    _names_all.append(_r.stdout.decode("utf-8", "replace"))
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w105" in _ln.lower() and OWN_SEAT not in _ln:
            peer_claims.append(_ln)
assert not peer_claims, f"leg0b failed: peer W105 seat MSG on origin: {peer_claims}"
_r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                     "fleet/inbox/"], capture_output=True, creationflags=CREAT)
assert OWN_SEAT in _r.stdout.decode("utf-8", "replace"), \
    "leg0b failed: own W105 seat MSG NOT on origin (r565 pre-freeze push missing)"
print("leg0b: zero PEER W105 seat MSGs on origin (inbox+processed scanned); "
      "own seat MSG-20261002-1738-bmc on origin confirmed (r565 law)")

# --- leg 0c: W104 seat MSG on origin (upstream published seat, skip target) ----
_names = "".join(_names_all)
assert W104_SEAT in _names, \
    "leg0c failed: bm-a W104 seat MSG not on origin (skip target missing)"
print("leg0c: bm-a W104 seat MSG on origin confirmed (published=reserved "
      "r518-1 skip target; W104 pub bands in the refusal universe)")

# --- leg 1: first-clean-window derive (skip-past-published + refusal scan) ------
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
PUB_BANDS = [W104_PUB_A, W104_PUB_B]

def first_clean(start, width, tag):
    lo = start
    hops = 0
    while True:
        hi = lo + width - 1
        hit = None
        for p in sorted(points):
            if lo <= p <= hi:
                hit = p
                break
        if hit is None:
            for b in bands + PUB_BANDS + [LFC_ACTUAL, OPTIONS_ACTUAL] + V1_IN_USE + W1_EXT:
                if overlaps((lo, hi), b):
                    hit = f"band {b}"
                    break
        if hit is None:
            return (lo, hi), hops
        # D-20261002-05 pinned semantics: past-hit restart (hit + 1)
        nxt = (hit + 1) if isinstance(hit, int) else hi + 1
        print(f"  refusal-scan {tag}: window {lo}..{hi} refused at {hit} -> "
              f"past-hit restart {nxt} (D-20261002-05 / r518-1)")
        lo = nxt
        hops += 1
        assert hops < 50, "refusal scan runaway"

ca, hops_a = first_clean(W103_TAIL_A[1] + 1, WIDTH_A, "A")
cb, hops_b = first_clean(W103_TAIL_B[1] + 1, WIDTH_B, "B")
assert ca == W105_A, f"leg1-A failed: derived first-clean {ca} != {W105_A}"
assert cb == W105_B, f"leg1-B failed: derived first-clean {cb} != {W105_B}"
print(f"leg1: A {W105_A[0]}..{W105_A[1]} CLEAN (skip-past-published W104 "
      f"band {W104_PUB_A[0]}..{W104_PUB_A[1]} then arithmetic continuation, "
      f"hops A={hops_a}); B {W105_B[0]}..{W105_B[1]} CLEAN (skip-past-"
      f"published W104 band {W104_PUB_B[0]}..{W104_PUB_B[1]} then pinned "
      f"past-hit restart past SEED_REGISTRY div_lowvol_p1=60_000 upper-edge "
      f"endpoint, hops B={hops_b}; both readings converge, W74-B/W81 edge "
      f"family, no fork face)")
refusal_pts = sorted(p for p in points if 59_801 <= p <= 60_000)
print("  B refusal facts (SEED_REGISTRY values in the refused arithmetic "
      f"window 59_801..60_000): {refusal_pts}")
reg_hit_names = {k: v for k, v in science_gates.SEED_REGISTRY.items()
                 if v in refusal_pts}
print(f"  refusal point registry keys: {reg_hit_names}")

# --- leg 2: full-universe conflict scan vs the CANDIDATE bands ----------------
conflicts = []
for tag, band in (("A", W105_A), ("B", W105_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W105-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W105-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W105-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W105-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W105-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W105-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W105-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W105-{tag} (r335 leg)")
    for pb, nm in ((W104_PUB_A, "W104-pub-A"), (W104_PUB_B, "W104-pub-B")):
        if overlaps(pb, band):
            conflicts.append(f"{nm} x W105-{tag} (r518-1 reserved)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "105: {\"a\": (253_004" not in out, \
    "leg2 failed: W105 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W105"' not in outn1, \
    "leg2 failed: W105 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W105_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg2 failed: W105 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W105 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W105 ADMIT: A {W105_A[0]}..{W105_A[1]} + B {W105_B[0]}..{W105_B[1]} "
      f"(A = skip-past-published W104 then arithmetic continuation; B = "
      f"skip-past-published W104 then pinned past-hit restart past "
      f"SEED_REGISTRY div_lowvol_p1=60_000 of the refused arithmetic window "
      f"59_801..60_000) -- clean vs all registered rows + W104 published "
      f"bands + registry + probes/actuals -- engine_owner=bm-c (own seat "
      f"MSG-20261002-1738-bmc on origin BEFORE this freeze per r565). "
      f"NOT a re-pick (R250: W105 bands were never assigned).")

# --- W106+ projection (warning text for the law table row) --------------------
w106_a = (W105_A[1] + 1, W105_A[1] + WIDTH_A)
w106_b = (W105_B[1] + 1, W105_B[1] + WIDTH_B)
a_hits = sorted(p for p in points if w106_a[0] <= p <= w106_a[1]) or \
    [f"band {b}" for b in bands + PUB_BANDS if overlaps(b, w106_a)]
b_hits = sorted(p for p in points if w106_b[0] <= p <= w106_b[1]) or \
    [f"band {b}" for b in bands + PUB_BANDS if overlaps(b, w106_b)]
print(f"W106+ projection: A arithmetic +2_000 = {w106_a[0]}..{w106_a[1]} "
      f"-> {'CLEAN (verify at W106 prereg)' if not a_hits else 'REFUSED ' + str(a_hits)}; "
      f"B +200 from W105 end = {w106_b[0]}..{w106_b[1]} "
      f"-> {'CLEAN (verify at W106 prereg)' if not b_hits else 'REFUSED ' + str(b_hits)}")

# --- se_mu chain face (prereg sec.5 anchor cite, derive not transcribe) --------
import json
for _w in (98, 99):
    _d = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                     f"n1_w{_w}_results.json"), encoding="utf-8"))
    _npc = _d.get("null_pool_cumulative", {})
    _se = [v for k, v in _npc.items() if k.startswith("se_mu")]
    print(f"W{_w} finalize: merged mu={_npc.get('merged', {}).get('mu')} "
          f"sigma={_npc.get('merged', {}).get('sigma')} "
          f"se_mu={_se} "
          f"A_p95={_d['families']['A_random_engine_exit'].get('full_sharpe_p95')} "
          f"A_p99={_d['families']['A_random_engine_exit'].get('full_sharpe_p99')} "
          f"K={_npc.get('merged', {}).get('n_values')} "
          f"klift_delta={_d['skill_line_v2_k_lift'].get('line_delta_k_lift')}")
