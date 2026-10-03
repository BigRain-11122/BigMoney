# -*- coding: utf-8 -*-
"""W115 UN-PARK machine-gate (r445 bm-c; law sec.4 tail law: verify before landing).

Un-park provenance: freeze prepared r384 bm-c (band gate ADMIT rc0
results/_r384bmc_w115_band_gate.py + pre-seat probe results/_r383bmc_w115_probe.py
rc0) -> PARKED r385 bm-c per O-20261002-2115 sec.2 supply-priority (N1
deprioritized; engine firepower -> new faces; parked.diff 22,244B + parked
prereg committed to origin with PARKED banner) -> UN-PARK r445 bm-c per the
park MSG recovery condition (fleet/inbox/processed/MSG-2026-10-02-2200-bmc-ALL-
w115-park.md): "新方向族炉线稳定（T-145/T-146/千人 wave-2 落地）或 CEO/GM 明令".
Condition evidence at this window: (1) MASS_TRIAL_W2 (千人 wave-2, 805 cells,
O-20261002-2115 sec.1 line-3) LANDED r444 bm-c + adopted same-round (w2_judge.json
complete=true, commit-side adoption 4f4100dc1; G2-eligible 0 honest negative);
(2) r444 bm-c pre-registered ruling: "W2 landing unblocks N1 supply reopen --
engine tick to draft next wave; py_low zero-ignition post-landing = supply-chain
P0 to GM, watch window starts now"; (3) the watch FIRED: bm-c engine alive
(Tools/saturation_engine.py status rc0, heartbeat fresh) but queue_depth=0,
burns_active=[], py_cpu 0.12% idle-starved -- the parked W115 row is the only
bm-c-lane supply; (4) zero new-face claimable for the bm-c engine at this window
(fund-trio NULLS burns = bm-b lane per MSG-1132/1155 division, owner_since
2026-10-04 04:20:12 in flight; pool has no bm-c-claimable engine face) -> the
un-park takes NO firepower from the new-direction line.

This gate re-runs the FULL r384 gate assertion set (leg0 registry parity /
leg0b seat dual-dir / leg1 first-clean derive pinned D-20261002-05 / leg2
conflict scan) with ONE adaptation: leg2's prereg vacancy check now EXPECTS
the OWN PARKED prereg on origin (r385 park artifact, banner + anchor verified
against the live n1_w114_results.json) instead of refusing it; peer W115
prereg variants remain refused. Plus a new anchor-roll leg (r576/r590 law):
latest landed finalize must still be W114 (K=248,720, chain head 615,348) so
the parked prereg's anchor (W114 landed values) is CURRENT with zero roll
displacement.

READ-ONLY vs the live table + origin. NOT a re-pick (R250: W115 bands were
never assigned).
"""
import subprocess, sys, os, json, re
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

# --- leg 0: registry shape + registered-tail parity (r384 re-run) --------------
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

# --- leg 2: full-universe conflict scan + vacancy (prereg = OWN PARKED face) ----
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
# ADAPTED for un-park: the on-origin prereg must be the OWN PARKED r385 face
# (banner + W114 anchor values), NOT a vacancy violation; peer variants refused.
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--", "research/PERPETUAL_N1_W115_PREREG.md"], cwd=ROOT, encoding="utf-8").strip()
assert outpre, "leg2 failed (un-park): OWN parked W115 prereg MISSING on origin (park artifact lost)"
pre_blob = subprocess.check_output(["git", "show", "origin/main:research/PERPETUAL_N1_W115_PREREG.md"], cwd=ROOT)
pre_text = pre_blob.decode("utf-8", "replace")
assert "PARKED" in pre_text, "leg2 failed (un-park): on-origin W115 prereg lacks the r385 PARKED banner"
for _needle in ("615,348", "248,720", "\u22120.09291186715985847",
                "\u22120.10410004545454546", "0.24488503216820995"):
    assert _needle in pre_text, f"leg2 failed (un-park): parked prereg anchor value {_needle} missing"
print(f"N1_BANDS rows: {len(N1_BANDS)} | SEED_REGISTRY int values: "
      f"{len([v for v in science_gates.SEED_REGISTRY.values() if isinstance(v,int)])}")
if conflicts:
    print("W115 REFUSED:")
    for c in conflicts: print("  -", c)
    sys.exit(1)
print(f"W115 UN-PARK ADMIT: A {W115_A[0]}..{W115_A[1]} + B {W115_B[0]}..{W115_B[1]} "
      f"(A = arithmetic continuation from the registered W114 A tail; B = pinned "
      f"D-20261002-05 past-hit restart over the in-band 62_500 refusal) -- clean vs "
      f"all registered rows + registry + probes/actuals -- engine_owner=bm-c (own "
      f"seat {OWN_SEAT} on origin BEFORE the freeze per r565, push ac241dd32; "
      f"own parked prereg on origin verified as the r385 park artifact). "
      f"NOT a re-pick (R250: W115 bands were never assigned).")

# --- leg 3 (un-park new): anchor-roll check (r576/r590 law) ---------------------
# Latest landed finalize must still be W114 so the parked prereg's anchor
# (W114 landed values) is CURRENT with zero roll displacement. Machine-derived
# from the live product, never transcribed.
d114 = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w114_results.json"), encoding="utf-8"))
npc = d114["null_pool_cumulative"]
K = npc["merged"]["n_values"]
mu = npc["merged"]["mu"]
sigma = npc["merged"]["sigma"]
assert K == 248720, f"leg3 failed: W114 K drift {K} (expect 248,720)"
assert abs(mu - (-0.09291186715985847)) < 1e-15, f"leg3 failed: W114 merged mu drift {mu}"
assert abs(sigma - 0.24488503216820995) < 1e-15, f"leg3 failed: W114 sigma drift {sigma}"
assert not os.path.exists(os.path.join(ROOT, "results", "perpetual_faces", "n1_w115_results.json")), \
    "leg3 failed: n1_w115_results.json already exists (newer finalize landed -> re-derive anchor)"
import glob
finals = [os.path.basename(f) for f in glob.glob(os.path.join(ROOT, "results", "perpetual_faces", "n1_w*_results.json"))]
assert len(finals) == 112, f"leg3 failed: N1 finalize file count {len(finals)} (expect 112 = W2..W114)"
print(f"leg3 (anchor-roll): latest landed finalize = W114 (K={K}, chain head 615,348) -- "
      f"zero newer finalize -> parked prereg anchor CURRENT, zero roll displacement "
      f"(r576/r590 law satisfied with re-verification, no re-derivation needed)")

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
