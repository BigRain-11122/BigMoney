# -*- coding: utf-8 -*-
"""W192 pre-seat probe (bm-c interactive window, CEO direct order 2026-10-08 ~23:5x
'自己去领回测任务排满') -- read-only band derivation before the seat MSG
publication (r565 early-visibility law). Machine-derived from the LIVE
post-W191-declaration universe (r587: never transcribed).

W192 candidate = first FREE number after the W191 SEAT (bm-a r892 seat MSG +
r893 prereg freeze ea42ee94a; W191 five-face band row PENDING on origin at
probe time -- W191 bands are FROZEN-DECLARED in its prereg and are injected
into this probe's universe with origin-text verification, honest note).
Derivation faces (STAIRCASE GEOMETRY FIFTY-SECOND instance expected, W141
leg2 law + E36 card; anticipated verbatim by the W191 prereg sec5.5 + r892
probe leg4 -- "W192 freezer MUST re-derive on the post-W191 universe AND
reserve own-wave A when deriving B" is MANDATORY, this probe IS that
re-derive; naive pre-W191-universe projection A 437_004..439_003 / B
437_204..437_403 is REFUSED here on the live universe, never transcribed):
  A  arithmetic continuation from the declared W191 A tail -- expected
     REFUSED at its own start by the declared W191 B band 437_004..437_203
     (staircase A-hops-prior-B 52nd); honest forward walk -> first-clean.
  B  arithmetic continuation from the declared W191 B tail -- naive lands
     INSIDE the W192 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean.
Bloodline: r892 _r892bma_w191_probe.py derive machinery verbatim, W192 facts
live-registry-driven; W191-declared-band injection = the r892-leg4-mandated
post-W191 universe (probe-time honest note: N1_BANDS tail still W190, W191
five-face pending bm-a side)."""
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
receipt = {"probe": "W192 pre-seat probe (bm-c interactive, CEO fill-order 2026-10-08 ~23:5x)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- W191 declared bands: origin-text verified (frozen prereg + seat on origin)
w191_pre = subprocess.check_output(
    ["git", "show", "origin/main:research/PERPETUAL_N1_W191_PREREG.md"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert "A-ext seed=435_004..437_003" in w191_pre and \
       "B-ext exit seed=437_004..437_203" in w191_pre, \
    "W191 declared bands not found in origin prereg text"
W191_DECL_A = (435_004, 437_003)
W191_DECL_B = (437_004, 437_203)
r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                    "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                   capture_output=True)
w191_seats = [ln for ln in r.stdout.decode("utf-8").splitlines()
              if "w191" in ln.lower() and "seat" in ln.lower()]
assert w191_seats, "W191 seat MSG missing on origin (universe premise drift)"

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
bands += [W191_DECL_A, W191_DECL_B]     # post-W191-declaration universe (r892 leg4 mandate)
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (single state: N1_BANDS tail=W190, W191 five-face pending)
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 191))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W190_A = tuple(N1_BANDS[190]["a"])
W190_B = tuple(N1_BANDS[190]["b_exit"])
assert W190_A == (432_804, 434_803) and W190_B == (434_804, 435_003) and \
    N1_BANDS[190].get("engine_owner") == "bm-a", "leg0 failed: W190 row drift"
assert tuple(N1_BANDS[189]["a"]) == (430_604, 432_603) and \
    tuple(N1_BANDS[189]["b_exit"]) == (432_604, 432_803), "leg0 W189 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 180 and len(bmc_rows) == 34 and len(bma_rows) == 106, \
    "leg0 ordinal drift"

w190_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w190_results.json"), encoding="utf-8"))
led = (w190_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 825_328 and led.get("prev_total") == 823_128, \
    f"leg0 failed: W190 ledger machine-read drift {led}"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W190",
                           "owner_rows": len(owner_rows), "bmc_rows": len(bmc_rows),
                           "ordinal": 182, "bmc_ordinal": 35,
                           "w190_ledger_head": led.get("total"),
                           "w191_status": ("seat-reserved + prereg-frozen bm-a (r892 MSG + r893 ea42ee94a); "
                                           "five-face band row PENDING on origin at probe time -- declared "
                                           "bands 435_004..437_003 / 437_004..437_203 origin-text-verified "
                                           "and injected into this universe per the r892-leg4 mandate"),
                           "w191_declared": {"A": list(W191_DECL_A), "B": list(W191_DECL_B)}}
print(f"leg0: {len(N1_BANDS)} rows tail=W190, owner={len(owner_rows)} -> 182nd wave, bm-c 35th owned, anchor W190 ledger head {led.get('total')}; W191 five-face pending (declared bands injected)")

# --- leg 1: honest forward walk from the declared W191 tails ------------------
ARITH_A = (W191_DECL_A[1] + 1, W191_DECL_A[1] + WIDTH_A)
ARITH_B = (W191_DECL_B[1] + 1, W191_DECL_B[1] + WIDTH_B)


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
assert fc_a[0] == W191_DECL_B[1] + 1, "leg1 staircase A base != prior-B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase expected per W191 prereg sec5.5 "
                              "+ r892 probe leg4 MANDATORY re-derive)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
assert fc_a == (437_204, 439_203) and fc_b == (439_204, 439_403), \
    f"leg1 band drift vs W191 sec5.5 mandate: A {fc_a} B {fc_b}"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation REFUSED at start by declared W191 B band "
                    "437_004..437_203 (staircase A-hops-prior-B FIFTY-SECOND instance, E36 card; "
                    "W191 prereg sec5.5 + r892 W191 probe leg4 anticipated and MANDATED this "
                    "re-derive); honest forward walk, non-rotational r587"),
    "B_semantics": ("B naive first-clean lands INSIDE own-wave A window -- same-freeze mutual "
                    "exclusion (W141 precedent, leg2 law); reserved walk past own-A, hops machine-counted"),
}
print(f"leg1: A {fc_a[0]}..{fc_a[1]} hops={hops_a} + B {fc_b[0]}..{fc_b[1]} hops={hops_b} (naive B {fc_b_naive[0]}..{fc_b_naive[1]} inside own-A; staircase held)")

# --- leg 2: full reserved universe conflict scan ------------------------------
conflicts = []
for tag, band in (("A", fc_a), ("B", fc_b)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} x W192-{tag}")
    for nm, db in (("W191-declared-A", W191_DECL_A), ("W191-declared-B", W191_DECL_B)):
        if overlaps(db, band):
            conflicts.append(f"{nm} x W192-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W192-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W192-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W192-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W192-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W192-{tag}")
assert not conflicts, f"leg2 failed: W192 conflicts {conflicts}"

# --- leg 3: origin vacancy (W192 seat must NOT exist yet; row/configs absent) --
r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                    "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                   capture_output=True)
seats = [ln for ln in r.stdout.decode("utf-8").splitlines()
         if "w192" in ln.lower() and "seat" in ln.lower()]
assert seats == [], f"leg3 failed: W192 seats already exist: {seats}"
out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                              cwd=ROOT, encoding="utf-8", errors="replace")
assert '192: {"a": (' not in out, "leg3 failed: W192 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
                                cwd=ROOT, encoding="utf-8", errors="replace")
assert '"batch": "PERPETUAL-N1-W192"' not in outn1, "leg3 failed: W192 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                  "research/PERPETUAL_N1_W192_PREREG.md"], cwd=ROOT,
                                 encoding="utf-8", errors="replace").strip()
assert not outpre, "leg3 failed: W192 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0}
receipt["legs"]["leg3"] = {"origin_vacancy": True}

# --- leg 4: W193+ projection (probe tail, next freezer re-derives) -------------
(fc193_a, h192a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc193_b, h192b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside192 = overlaps(fc193_b, fc193_a)
receipt["legs"]["leg4"] = {"W193p_A": f"{fc193_a[0]}..{fc193_a[1]}", "hops_A": h192a,
                           "W193p_B": f"{fc193_b[0]}..{fc193_b[1]}", "hops_B": h192b,
                           "W193p_B_lands_inside_W193p_A": inside192,
                           "note": ("W193+ naive projection on pre-W192 universe; "
                                    "W192-B-refuses-W193-A staircase anticipated once W192 B registered "
                                    "(A-hops-prior-B FIFTY-THIRD instance anticipated); "
                                    "W193 freezer MUST re-derive on the post-W192 universe AND reserve "
                                    "own-wave A when deriving B (W141 precedent, leg2 law, E36 staircase card) "
                                    "-- never transcribe r587)")}
print(f"leg4: W193+ projection A {fc193_a[0]}..{fc193_a[1]} hops={h192a} / B {fc193_b[0]}..{fc193_b[1]} hops={h192b} (B inside A: {inside192})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_w192bmc_20261009_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W192 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
