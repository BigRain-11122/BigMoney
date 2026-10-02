# -*- coding: utf-8 -*-
"""W108 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W108 candidate = first FREE number after the REGISTERED W106 row (bm-b r585
freeze, landed origin d6b2952e3 / synced c01fe5880) SKIPPING the published
W107 seat (bm-a MSG-20261002-1759, published=reserved r518-1). Dual-state:
state A = W107 published-unregistered (skip-past-published chain); state B
= W107 registered (arithmetic continuation over the registered table).
Both states must converge to identical bands (W90 r579 / W94 r580 family).

Bands (machine-derived, NOT transcribed -- r335/r535 law):
  A 259_004..261_003  (skip W107 pub 257_004..259_003, hops=1)
  B 60_601..60_800    (skip W107 pub 60_401..60_600, hops=1)

Machine-verified against: all registered N1 wave bands (W2..W106 live, or
W2..W107 in state B), the PUBLISHED W107 seat bands (skip-past-published
r518-1 leg), N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 mandatory
leg), probe cluster 95_000..95_003 (r335 leg), v1 in-use + W1 ext bands,
live SEED_REGISTRY values, N2/N4 probe points, N2-W15 draft probe points,
lfc/options actuals, and the bm-c W108 seat MSG-20261002-1804 (own, on
origin per r565; NO peer W108 seat allowed).

r378 bm-c freeze-window run. READ-ONLY vs the live table + origin.
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000

W108_A = (259_004, 261_003)        # candidate (derived, gate must confirm)
W108_B = (60_601, 60_800)          # skip-past-published prediction
W106_TAIL_A = (255_004, 257_003)   # registered W106 (bm-b r585, live table tail)
W106_TAIL_B = (60_201, 60_400)
W107_PUB_A = (257_004, 259_003)    # bm-a W107 published seat (r518-1 reserved)
W107_PUB_B = (60_401, 60_600)
OWN_SEAT = "MSG-20261002-1804-bmc"   # own W108 seat MSG (pushed pre-freeze r565)
W107_SEAT = "MSG-20261002-1759-bma"  # bm-a W107 seat MSG (skip target, leg0c)

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

# --- leg 0: registry shape + registered-tail parity (DUAL-STATE) ---------------
keys = sorted(N1_BANDS)
keys_a = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 107))
keys_b = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 108))
if keys == keys_a:
    STATE = "A"
elif keys == keys_b:
    STATE = "B"
else:
    raise AssertionError(f"leg0 failed: unexpected registry shape {keys[-5:]}")
assert N1_BANDS[106]["a"] == W106_TAIL_A and \
    N1_BANDS[106]["b_exit"] == W106_TAIL_B and \
    N1_BANDS[106].get("engine_owner") == "bm-b", "leg0 failed: W106 row drift"
assert N1_BANDS[105]["a"] == (253_004, 255_003) and \
    N1_BANDS[105]["b_exit"] == (60_001, 60_200) and \
    N1_BANDS[105].get("engine_owner") == "bm-c", "leg0 failed: W105 row drift"
if STATE == "B":
    assert N1_BANDS[107]["a"] == W107_PUB_A and \
        N1_BANDS[107]["b_exit"] == W107_PUB_B and \
        N1_BANDS[107].get("engine_owner") == "bm-a", \
        "leg0 failed: W107 row drift vs published bands"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
expect_owner = 96 if STATE == "A" else 97
assert len(owner_rows) == expect_owner, \
    f"leg0 failed: engine_owner rows {len(owner_rows)} (expect {expect_owner})"
assert len(bmc_rows) == 31, \
    f"leg0 failed: bm-c rows {len(bmc_rows)} (expect 31)"
ordinal = expect_owner + 1
print(f"leg0[state {STATE}]: {len(N1_BANDS)} registered rows, tail=W{keys[-1]}; "
      f"engine_owner rows={len(owner_rows)} + candidate -> W108 = bm-c 32nd "
      f"owned, ordinal {ordinal} engine wave by machine-derive (prose "
      f"ordinal drift disclosed per r359 law)")

# --- leg 0b: NO peer W108 seat claim on origin (own seat allowed) ---------------
peer_claims = []
_names_all = []
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    _names_all.append(_r.stdout.decode("utf-8", "replace"))
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w108" in _ln.lower() and OWN_SEAT not in _ln:
            peer_claims.append(_ln)
assert not peer_claims, f"leg0b failed: peer W108 seat MSG on origin: {peer_claims}"
_r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                     "fleet/inbox/"], capture_output=True, creationflags=CREAT)
assert OWN_SEAT in _r.stdout.decode("utf-8", "replace"), \
    "leg0b failed: own W108 seat MSG NOT on origin (r565 pre-freeze push missing)"
print("leg0b: zero PEER W108 seat MSGs on origin (inbox+processed scanned); "
      "own seat MSG-20261002-1804-bmc on origin confirmed (r565 law)")

# --- leg 0c: W107 seat MSG on origin (upstream published seat, skip target) ----
_names = "".join(_names_all)
assert W107_SEAT in _names, \
    "leg0c failed: bm-a W107 seat MSG not on origin (skip target missing)"
print("leg0c: bm-a W107 seat MSG on origin confirmed (published=reserved "
      "r518-1 skip target; W107 pub bands in the refusal universe)")

# --- leg 1: first-clean-window derive (skip-past-published + refusal scan) ------
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
PUB_BANDS = [W107_PUB_A, W107_PUB_B]

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

ca, hops_a = first_clean(W106_TAIL_A[1] + 1, WIDTH_A, "A")
cb, hops_b = first_clean(W106_TAIL_B[1] + 1, WIDTH_B, "B")
assert ca == W108_A, f"leg1-A failed: derived first-clean {ca} != {W108_A}"
assert cb == W108_B, f"leg1-B failed: derived first-clean {cb} != {W108_B}"
print(f"leg1[state {STATE}]: A {W108_A[0]}..{W108_A[1]} CLEAN (skip-past-"
      f"published W107 band {W107_PUB_A[0]}..{W107_PUB_A[1]} then arithmetic "
      f"continuation, hops A={hops_a}); B {W108_B[0]}..{W108_B[1]} CLEAN "
      f"(skip-past-published W107 band {W107_PUB_B[0]}..{W107_PUB_B[1]} then "
      f"arithmetic continuation, hops B={hops_b}; dual-state convergent "
      f"identical bands, no fork face)")
refusal_pts_a = sorted(p for p in points if 257_004 <= p <= 259_003)
refusal_pts_b = sorted(p for p in points if 60_401 <= p <= 60_800)
print(f"  A skip-window point-facts (257_004..259_003): {refusal_pts_a}")
print(f"  B window point-facts (60_401..60_800): {refusal_pts_b}")

# --- leg 2: full-universe conflict scan vs the CANDIDATE bands ----------------
conflicts = []
for tag, band in (("A", W108_A), ("B", W108_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W108-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W108-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W108-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W108-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W108-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W108-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W108-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W108-{tag} (r335 leg)")
    for pb, nm in ((W107_PUB_A, "W107-pub-A"), (W107_PUB_B, "W107-pub-B")):
        if overlaps(pb, band):
            conflicts.append(f"{nm} x W108-{tag} (r518-1 reserved)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "108: {\"a\": (259_004" not in out, \
    "leg2 failed: W108 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W108"' not in outn1, \
    "leg2 failed: W108 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W108_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg2 failed: W108 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W108 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W108 ADMIT[state {STATE}]: A {W108_A[0]}..{W108_A[1]} + B "
      f"{W108_B[0]}..{W108_B[1]} (A = skip-past-published W107 then "
      f"arithmetic continuation; B = skip-past-published W107 then "
      f"arithmetic continuation) -- clean vs all registered rows + W107 "
      f"published bands + registry + probes/actuals -- engine_owner=bm-c "
      f"(own seat MSG-20261002-1804-bmc on origin BEFORE this freeze per "
      f"r565). NOT a re-pick (R250: W108 bands were never assigned).")

# --- W109+ projection (warning text for the law table row) --------------------
w109_a = (W108_A[1] + 1, W108_A[1] + WIDTH_A)
w109_b = (W108_B[1] + 1, W108_B[1] + WIDTH_B)
a_hits = sorted(p for p in points if w109_a[0] <= p <= w109_a[1]) or \
    [f"band {b}" for b in bands + PUB_BANDS if overlaps(b, w109_a)]
b_hits = sorted(p for p in points if w109_b[0] <= p <= w109_b[1]) or \
    [f"band {b}" for b in bands + PUB_BANDS if overlaps(b, w109_b)]
print(f"W109+ projection: A arithmetic +2_000 = {w109_a[0]}..{w109_a[1]} "
      f"-> {'CLEAN (verify at W109 prereg)' if not a_hits else 'REFUSED ' + str(a_hits)}; "
      f"B +200 from W108 end = {w109_b[0]}..{w109_b[1]} "
      f"-> {'CLEAN (verify at W109 prereg)' if not b_hits else 'REFUSED ' + str(b_hits)}")

# --- se_mu chain face (prereg sec.5 anchor cite, derive not transcribe) --------
import json
for _w in (101, 102):
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
