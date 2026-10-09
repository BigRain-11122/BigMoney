# -*- coding: utf-8 -*-
"""W204 pre-seat probe (bm-c interactive window, 2026-10-10; standing CEO fill-order
2026-10-08 ~23:5x '自己去领回测任务排满' + O-20261009-2334-bm-b §1-2 本地满用令)
-- read-only band derivation before the seat MSG publication (r565 early-visibility
law). Machine-derived from the LIVE post-W202 universe + the DECLARED W203 bands
(r587: never transcribed).

W204 candidate = first FREE number after the bm-a W203 SEAT (r930 seat MSG
2026-10-09-2329 processed on origin; W203 five-face band row PENDING on origin
at probe time -- W203 bands are FROZEN-DECLARED in the bm-a seat MSG and are
injected into this probe's universe with origin-text verification, honest
note -- exact mirror of the W192/r892 declared-injection precedent).
Derivation faces (STAIRCASE GEOMETRY SIXTY-FOURTH instance expected, W141
leg2 law + E36 card; anticipated verbatim by the W203 seat leg4 projection +
r930 W203 probe leg4 -- 'W204 freezer MUST re-derive on the post-W203 universe
AND reserve own-wave A when deriving B' is MANDATORY, this probe IS that
re-derive):
  A  arithmetic continuation from the declared W203 A tail -- REFUSED at
     its own start by the declared W203 B band 463_404..463_603
     (staircase A-hops-prior-B 64th); honest forward walk -> first-clean.
  B  arithmetic continuation from the declared W203 B tail -- naive lands
     INSIDE the W204 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean.
Bloodline: _w192bmc_20261009_probe.py derive machinery verbatim, W204 facts
live-registry-driven; W203-declared-band injection = the r930-leg4-mandated
post-W203 universe (probe-time honest note: N1_BANDS tail still W202, W203
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
receipt = {"probe": "W204 pre-seat probe (bm-c interactive, 2026-10-10, CEO fill-order + O-2334 local-full-use)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- W203 declared bands: origin-text verified (bm-a seat MSG on origin) ---------
w203_seat = subprocess.check_output(
    ["git", "show", "origin/main:fleet/inbox/processed/MSG-2026-10-09-2329-bma-w203-seat.md"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert "**A 461_404..463_403**" in w203_seat and \
       "**B 463_404..463_603**" in w203_seat, \
    "W203 declared bands not found in origin seat MSG text"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '203: {"a": (' not in out_pf, \
    "W203 five-face row ALREADY on origin -- injection premise broken, re-derive live"
W203_DECL_A = (461_404, 463_403)
W203_DECL_B = (463_404, 463_603)

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
bands += [W203_DECL_A, W203_DECL_B]   # post-W203-declaration universe (r930 leg4 mandate)
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (single state: N1_BANDS tail=W202, W203 seat-reserved pending)
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 203))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W202_A = tuple(N1_BANDS[202]["a"])
W202_B = tuple(N1_BANDS[202]["b_exit"])
assert W202_A == (459_204, 461_203) and W202_B == (461_204, 461_403) and \
    N1_BANDS[202].get("engine_owner") == "bm-a", "leg0 failed: W202 row drift"
assert tuple(N1_BANDS[201]["a"]) == (457_004, 459_003) and \
    tuple(N1_BANDS[201]["b_exit"]) == (459_004, 459_203), "leg0 W201 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 192 and len(bmc_rows) == 35 and len(bma_rows) == 117, \
    f"leg0 ordinal drift: owner={len(owner_rows)} bmc={len(bmc_rows)} bma={len(bma_rows)}"

w202_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w202_results.json"), encoding="utf-8"))
led = (w202_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 858_745 and led.get("prev_total") == 856_545, \
    f"leg0 failed: W202 ledger machine-read drift {led}"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W202",
                           "owner_rows": len(owner_rows), "bmc_rows": len(bmc_rows),
                           "bma_rows": len(bma_rows),
                           "ordinal": 194, "bmc_ordinal": 36,
                           "w202_ledger_head": led.get("total"),
                           "w203_status": ("seat-reserved bm-a r930 (MSG-2026-10-09-2329 processed on origin); "
                                           "five-face band row PENDING on origin at probe time -- declared "
                                           "bands 461_404..463_403 / 463_404..463_603 origin-text-verified "
                                           "and injected into this universe per the r930 leg4 mandate"),
                           "w203_declared": {"A": list(W203_DECL_A), "B": list(W203_DECL_B)}}
print(f"leg0: {len(N1_BANDS)} rows tail=W202, owner={len(owner_rows)} -> 194th wave, bm-c 36th owned, anchor W202 ledger head {led.get('total')}; W203 five-face pending (declared bands injected)")

# --- leg 1: honest forward walk from the declared W203 tails ---------------------
ARITH_A = (W203_DECL_A[1] + 1, W203_DECL_A[1] + WIDTH_A)
ARITH_B = (W203_DECL_B[1] + 1, W203_DECL_B[1] + WIDTH_B)


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
assert fc_a[0] == W203_DECL_B[1] + 1, "leg1 staircase A base != prior-B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase expected per W203 seat leg4 "
                              "projection + r930 probe leg4 MANDATORY re-derive)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
assert fc_a == (463_604, 465_603) and fc_b == (465_604, 465_803), \
    f"leg1 band drift vs W203 sec5.5 mandate: A {fc_a} B {fc_b}"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation REFUSED at start by declared W203 B band "
                    "463_404..463_603 (staircase A-hops-prior-B SIXTY-FOURTH instance, E36 card; "
                    "W203 seat leg4 projection + r930 W203 probe leg4 anticipated and MANDATED this "
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W204-{tag}")
    for nm, db in (("W203-declared-A", W203_DECL_A), ("W203-declared-B", W203_DECL_B)):
        if overlaps(db, band):
            conflicts.append(f"{nm} x W204-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W204-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W204-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W204-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W204-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W204-{tag}")
assert not conflicts, f"leg2 failed: W204 conflicts {conflicts}"

# --- leg 3: origin vacancy (W204 seat must NOT exist yet; row/configs absent) --
r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                    "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                   capture_output=True)
seats = [ln for ln in r.stdout.decode("utf-8").splitlines()
         if "w204" in ln.lower() and "seat" in ln.lower()]
assert seats == [], f"leg3 failed: W204 seats already exist: {seats}"
assert '204: {"a": (' not in out_pf, "leg3 failed: W204 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
                                cwd=ROOT, encoding="utf-8", errors="replace")
assert '"batch": "PERPETUAL-N1-W204"' not in outn1, "leg3 failed: W204 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                  "research/PERPETUAL_N1_W204_PREREG.md"], cwd=ROOT,
                                 encoding="utf-8", errors="replace").strip()
assert not outpre, "leg3 failed: W204 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0}
receipt["legs"]["leg3"] = {"origin_vacancy": True}

# --- leg 4: W205+ projection (probe tail, next freezer re-derives) -------------
(fc205_a, h204a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc205_b, h204b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside205 = overlaps(fc205_b, fc205_a)
receipt["legs"]["leg4"] = {"W205p_A": f"{fc205_a[0]}..{fc205_a[1]}", "hops_A": h204a,
                           "W205p_B": f"{fc205_b[0]}..{fc205_b[1]}", "hops_B": h204b,
                           "W205p_B_lands_inside_W205p_A": inside205,
                           "note": ("W205+ naive projection on pre-W204 universe; "
                                    "W204-B-refuses-W205-A staircase anticipated once W204 B registered "
                                    "(A-hops-prior-B SIXTY-FIFTH instance anticipated); "
                                    "W205 freezer MUST re-derive on the post-W204 universe AND reserve "
                                    "own-wave A when deriving B (W141 precedent, leg2 law, E36 staircase card) "
                                    "-- never transcribe r587)")}
print(f"leg4: W205+ projection A {fc205_a[0]}..{fc205_a[1]} hops={h204a} / B {fc205_b[0]}..{fc205_b[1]} hops={h204b} (B inside A: {inside205})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_w204bmc_20261010_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W204 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
