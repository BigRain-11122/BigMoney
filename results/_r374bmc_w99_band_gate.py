# -*- coding: utf-8 -*-
"""W99 band disjoint machine-gate (law sec.4 tail law: verify before landing).

W99 candidate = first FREE number after the registered W98 row (bm-a r582
freeze, landed origin 8be174832). SINGLE STATE (W98 registered, no seat
gap): A side = arithmetic continuation from the W98 A tail; B side =
pinned-skip derive per D-20261002-05 (arithmetic window 58_401..58_600
REFUSED at SEED_REGISTRY points [58_500, 58_550] -- in-band mid hits ->
past-hit restart, first clean window from hit+1).

Bands (machine-derived, NOT transcribed -- r335/r535 law):
  A 241_004..243_003  (W98 A tail 241_003 + 1, stride 2_000) -- verify CLEAN
  B <derived>         (pinned skip from 58_401, stride 200) -- verify CLEAN

Machine-verified against: all registered N1 wave bands (W2..W98 live),
N3-R1 used-seed band 70_000..70_005 (MSG-183x r529 mandatory leg), probe
cluster 95_000..95_003 (r335 leg), v1 in-use + W1 ext bands, live
SEED_REGISTRY values, N2/N4 probe points, N2-W15 draft probe points,
lfc/options actuals, and the bm-c W99 seat MSG-20261002-1625 (own, on
origin per r565; NO peer W99 seat allowed).

r374 bm-c freeze-window run. READ-ONLY vs the live table + origin.
"""
import subprocess
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000

W99_A = (241_004, 243_003)        # candidate (derived, gate must confirm)
W99_B = (58_551, 58_750)          # pinned-skip prediction (gate derives)
W98_TAIL_A = (239_004, 241_003)   # registered W98 (bm-a r582, live table tail)
W98_TAIL_B = (58_201, 58_400)
OWN_SEAT = "MSG-20261002-1625-bmc"   # own W99 seat MSG (pushed pre-freeze r565)

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
assert keys == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 99)), \
    f"leg0 failed: keys tail drift {keys[-5:]}"
assert N1_BANDS[98]["a"] == W98_TAIL_A and \
    N1_BANDS[98]["b_exit"] == W98_TAIL_B and \
    N1_BANDS[98].get("engine_owner") == "bm-a", "leg0 failed: W98 row drift"
assert N1_BANDS[97]["a"] == (237_004, 239_003) and \
    N1_BANDS[97]["b_exit"] == (58_001, 58_200) and \
    N1_BANDS[97].get("engine_owner") == "bm-b", "leg0 failed: W97 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
assert len(owner_rows) == 88, \
    f"leg0 failed: engine_owner rows {len(owner_rows)} (expect 88)"
assert len(bmc_rows) == 28, \
    f"leg0 failed: bm-c rows {len(bmc_rows)} (expect 28)"
print(f"leg0: {len(N1_BANDS)} registered rows, tail=W{keys[-1]} (W98 bm-a, "
      f"single state zero seat gap); engine_owner rows={len(owner_rows)} + "
      f"candidate -> W99 = bm-c 29th owned, EIGHTY-NINTH engine wave by "
      f"machine-derive (88 registered + candidate)")

# --- leg 0b: NO peer W99 seat claim on origin (own seat allowed) ---------------
peer_claims = []
_names_all = []
for _pfx in ("fleet/inbox/", "fleet/inbox/processed/"):
    _r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", _pfx],
                        capture_output=True, creationflags=CREAT)
    _names_all.append(_r.stdout.decode("utf-8", "replace"))
    for _ln in _r.stdout.decode("utf-8", "replace").splitlines():
        if "w99" in _ln.lower() and OWN_SEAT not in _ln:
            peer_claims.append(_ln)
assert not peer_claims, f"leg0b failed: peer W99 seat MSG on origin: {peer_claims}"
_r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                     "fleet/inbox/"], capture_output=True, creationflags=CREAT)
assert OWN_SEAT in _r.stdout.decode("utf-8", "replace"), \
    "leg0b failed: own W99 seat MSG NOT on origin (r565 pre-freeze push missing)"
print("leg0b: zero PEER W99 seat MSGs on origin (inbox+processed scanned); "
      "own seat MSG-20261002-1625-bmc on origin confirmed (r565 law)")

# --- leg 0c: W98 seat MSG on origin (upstream published seat) ------------------
_names = "".join(_names_all)
assert "MSG-20261002-1603-bma-w98-seat" in _names, \
    "leg0c failed: bm-a W98 seat MSG not on origin (upstream published seat missing)"
print("leg0c: bm-a W98 seat MSG on origin confirmed (upstream published seat)")

# --- leg 1: first-clean-window derive (arithmetic continuation + refusal scan) -
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))

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
            for b in bands + [LFC_ACTUAL, OPTIONS_ACTUAL] + V1_IN_USE + W1_EXT:
                if overlaps((lo, hi), b):
                    hit = f"band {b}"
                    break
        if hit is None:
            return (lo, hi), hops
        # D-20261002-05 pinned semantics: past-hit restart (hit + 1)
        nxt = (hit + 1) if isinstance(hit, int) else hi + 1
        print(f"  refusal-scan {tag}: window {lo}..{hi} refused at {hit} -> "
              f"past-hit restart {nxt} (D-20261002-05)")
        lo = nxt
        hops += 1
        assert hops < 50, "refusal scan runaway"

ca, hops_a = first_clean(W98_TAIL_A[1] + 1, WIDTH_A, "A")
cb, hops_b = first_clean(W98_TAIL_B[1] + 1, WIDTH_B, "B")
assert ca == W99_A, f"leg1-A failed: derived first-clean {ca} != {W99_A}"
assert cb == W99_B, f"leg1-B failed: derived first-clean {cb} != {W99_B}"
print(f"leg1: A {W99_A[0]}..{W99_A[1]} CLEAN (arithmetic continuation from the "
      f"W98 A tail, single state; refusal hops A={hops_a}); B {W99_B[0]}.."
      f"{W99_B[1]} CLEAN (pinned-skip per D-20261002-05: arithmetic window "
      f"58_401..58_600 refused at SEED_REGISTRY in-band hits -> past-hit "
      f"restart; refusal hops B={hops_b})")
refusal_pts = sorted(p for p in points if 58_401 <= p <= 58_600)
print("  B refusal facts (SEED_REGISTRY values in the arithmetic window "
      f"58_401..58_600): {refusal_pts}")
reg_hit_names = {k: v for k, v in science_gates.SEED_REGISTRY.items()
                 if v in refusal_pts}
print(f"  refusal point registry keys: {reg_hit_names}")

# --- leg 2: full-universe conflict scan vs the CANDIDATE bands ----------------
conflicts = []
for tag, band in (("A", W99_A), ("B", W99_B)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} {lo}..{hi} x W99-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W99-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W99-{tag}")
    for p in N24_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2/N4 probe point {p} inside W99-{tag}")
    for p in N2_W15_PROBE_POINTS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"N2-W15 probe point {p} inside W99-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r in bb:
            if overlaps(r, band):
                conflicts.append(f"{nm} x W99-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W99-{tag} (MSG-183x leg)")
    for p in PROBE_SEEDS:
        if band[0] <= p <= band[1]:
            conflicts.append(f"probe seed {p} inside W99-{tag} (r335 leg)")
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
assert "99: {\"a\": (241_004" not in out, \
    "leg2 failed: W99 row ALREADY on origin (slot not vacant, r511 tail-lock)"
outn1 = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], encoding="utf-8")
assert '"batch": "PERPETUAL-N1-W99"' not in outn1, \
    "leg2 failed: W99 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W99_PREREG.md"], encoding="utf-8").strip()
assert not outpre, "leg2 failed: W99 per-wave prereg ALREADY on origin"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])} "
      f"| N3-R1 used band: {N3R1_USED[0]}..{N3R1_USED[1]} | probe cluster: "
      f"{PROBE_SEEDS[0]}..{PROBE_SEEDS[3]}")
if conflicts:
    print("W99 REFUSED:")
    for c in conflicts:
        print("  -", c)
    sys.exit(1)
print(f"W99 ADMIT: A {W99_A[0]}..{W99_A[1]} + B {W99_B[0]}..{W99_B[1]} "
      f"(A = arithmetic continuation from the registered W98 A tail; B = "
      f"D-20261002-05 pinned-skip derive past the SEED_REGISTRY in-band hits "
      f"{refusal_pts} of the refused arithmetic window 58_401..58_600) -- "
      f"clean vs all registered rows + registry + probes/actuals -- "
      f"engine_owner=bm-c (own seat MSG-20261002-1625-bmc on origin BEFORE "
      f"this freeze per r565). NOT a re-pick (R250: W99 bands were never "
      f"assigned).")

# --- W100+ projection (warning text for the law table row) --------------------
w100_a = (W99_A[1] + 1, W99_A[1] + WIDTH_A)
w100_b = (W99_B[1] + 1, W99_B[1] + WIDTH_B)
a_hits100 = sorted(p for p in points if w100_a[0] <= p <= w100_a[1]) or \
    [f"band {b}" for b in bands if overlaps(b, w100_a)]
b_hits100 = sorted(p for p in points if w100_b[0] <= p <= w100_b[1]) or \
    [f"band {b}" for b in bands if overlaps(b, w100_b)]
print(f"W100+ projection: A arithmetic +2_000 = {w100_a[0]}..{w100_a[1]} "
      f"-> {'CLEAN (verify at W100 prereg)' if not a_hits100 else 'REFUSED ' + str(a_hits100)}; "
      f"B +200 from W99 end = {w100_b[0]}..{w100_b[1]} "
      f"-> {'CLEAN (verify at W100 prereg)' if not b_hits100 else 'REFUSED ' + str(b_hits100)}")

# --- se_mu chain face (prereg sec.5 anchor cite, derive not transcribe) -------
import json
for _w in (92, 93, 94):
    _d = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                     f"n1_w{_w}_results.json"), encoding="utf-8"))
    _npc = _d.get("null_pool_cumulative", {})
    print(f"W{_w} finalize: merged mu={_npc.get('merged', {}).get('mu')} "
          f"sigma={_npc.get('merged', {}).get('sigma')} "
          f"se_mu={_npc.get('se_mu_at_k204720') or _npc.get('se_mu_at_k202520') or _npc.get('se_mu_at_k200320')} "
          f"A_p95={_d['families']['A_random_engine_exit'].get('full_sharpe_p95')} "
          f"K={_npc.get('merged', {}).get('n_values')}")
