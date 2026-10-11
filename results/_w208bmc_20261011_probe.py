# -*- coding: utf-8 -*-
"""W208 pre-seat probe (bm-c interactive window, 2026-10-11; standing CEO fill-order
2026-10-08 + O-20261009-2334 §1-2 + CEO idle-reprimand 2026-10-11 ~12:4x).
Machine-derived from the LIVE post-W207 universe (r587: never transcribed).
W208 candidate = first FREE number after the registered W207 (all of W203..W207
five-face LIVE on origin, zero injection needed). Staircase SIXTY-EIGHTH instance
expected; W141 leg2 law + E36 card; next-freezer re-derive mandate standing."""
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
receipt = {"probe": "W208 pre-seat probe (bm-c interactive, 2026-10-11, CEO fill-order + idle-reprimand window)", "legs": {}}

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True, creationflags=CREAT)

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS) | set(CROSSFACE_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1)) | set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 0: registry shape (single state: tail=W207 live) ------------------------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 208))
assert keys == base_keys, f"leg0 failed: registry keys tail {keys[-5:]}"
W207_A = tuple(N1_BANDS[207]["a"]); W207_B = tuple(N1_BANDS[207]["b_exit"])
assert W207_A == (470_204, 472_203) and W207_B == (472_204, 472_403), "leg0 W207 row drift"
assert N1_BANDS[207].get("engine_owner") == "bm-b", "leg0 W207 owner drift (expect bm-b 41st own wave)"
assert tuple(N1_BANDS[204]["a"]) == (463_604, 465_603) and \
    N1_BANDS[204].get("engine_owner") == "bm-c", "leg0 W204 bm-c row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(keys) == 205 and len(owner_rows) == 197 and len(bmc_rows) == 37 and len(bma_rows) == 119, \
    f"leg0 ordinal drift: rows={len(keys)} owner={len(owner_rows)} bmc={len(bmc_rows)} bma={len(bma_rows)}"

w207_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w207_results.json"), encoding="utf-8"))
led = (w207_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == led.get("prev_total") + 2200, f"leg0 W207 ledger chain drift {led}"
npc = w207_out["null_pool_cumulative"]["merged"]
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W207", "owner_rows": len(owner_rows),
                           "bmc_rows": len(bmc_rows), "bma_rows": len(bma_rows),
                           "ordinal": 198, "bmc_ordinal": 37,
                           "w207_ledger_head": led.get("total"), "w207_prev": led.get("prev_total"),
                           "w207_K": npc["n_values"], "w207_mu": npc["mu"], "w207_sigma": npc["sigma"],
                           "w207_wonly_mu": w207_out["null_pool_cumulative"]["w207_only"]["mu"]}
print(f"leg0: {len(N1_BANDS)} rows tail=W207 owner={len(owner_rows)} -> 198th wave, bm-c 37th owned; W207 ledger head {led.get('total')} K={npc['n_values']}")

# --- leg 1: honest forward walk from the live W207 tails -------------------------
ARITH_A = (W207_A[1] + 1, W207_A[1] + WIDTH_A)
ARITH_B = (W207_B[1] + 1, W207_B[1] + WIDTH_B)

def first_clean(lo, width, trace=None, extra_bands=()):
    hops = 0; prev_lo = lo
    while True:
        hi = lo + width - 1
        bad_pts = [p for p in points if lo <= p <= hi]
        bad_bands = [b for b in list(bands) + list(extra_bands) + actual if overlaps((lo, hi), b)]
        if not bad_pts and not bad_bands:
            return (lo, hi), hops
        jump = max([p + 1 for p in bad_pts] + [b[1] + 1 for b in bad_bands])
        assert jump > prev_lo, f"non-rotational violation: jump {jump} <= {prev_lo}"
        if trace is not None:
            trace.append({"hop": hops + 1, "window": [lo, hi], "jump_to": jump})
        lo = jump; prev_lo = lo; hops += 1

(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A)
b_trace = []
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace, extra_bands=(fc_a,))
(fc_b_naive, hops_b_naive) = first_clean(ARITH_B[0], WIDTH_B)
assert fc_a[0] == W207_B[1] + 1, "leg1 staircase A base != prior-B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], "leg1 A not refused (staircase expected)"
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
assert fc_a == (472_404, 474_403) and fc_b == (474_404, 474_603), \
    f"leg1 band drift: A {fc_a} B {fc_b}"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive, "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation REFUSED at start by registered W207 B band "
                    "472_204..472_403 (staircase A-hops-prior-B SIXTY-EIGHTH instance, E36 card); "
                    "honest forward walk, non-rotational r587"),
    "B_semantics": ("B naive first-clean lands INSIDE own-wave A window -- same-freeze mutual "
                    "exclusion (W141 precedent, leg2 law); reserved walk past own-A"),
}
print(f"leg1: A {fc_a[0]}..{fc_a[1]} hops={hops_a} + B {fc_b[0]}..{fc_b[1]} hops={hops_b} (staircase held)")

# --- leg 2: full universe conflict scan ------------------------------------------
conflicts = []
for tag, band in (("A", fc_a), ("B", fc_b)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} x W208-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W208-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W208-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W208-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W208-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W208-{tag}")
assert not conflicts, f"leg2 failed: W208 conflicts {conflicts}"

# --- leg 3: origin vacancy (ABSORB MODE: bm-a's stale W208 seat exists and is the
# absorb premise; row/configs/prereg must still be ABSENT so the takeover freeze
# can land -- r899/r915 dead-estate law, 01:29 seat stale 11h with no prereg/five-face;
# bm-a loop (round 872, alive 12:38) has not picked it up) -----------------------
r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                    "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT, capture_output=True)
seats = [ln for ln in r.stdout.decode("utf-8").splitlines()
         if "w208" in ln.lower() and "seat" in ln.lower()]
assert seats == ["fleet/inbox/processed/MSG-2026-10-11-0129-bma-w208-seat.md"], \
    f"leg3 failed: W208 seat face drift: {seats}"
out_pf = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                                 cwd=ROOT, encoding="utf-8", errors="replace")
assert '208: {"a": (' not in out_pf, "leg3 failed: W208 row ALREADY on origin"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
                                cwd=ROOT, encoding="utf-8", errors="replace")
assert '"batch": "PERPETUAL-N1-W208"' not in outn1, "leg3 failed: W208 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                  "research/PERPETUAL_N1_W208_PREREG.md"], cwd=ROOT,
                                 encoding="utf-8", errors="replace").strip()
assert not outpre, "leg3 failed: W208 prereg ALREADY on origin (absorb premise broken)"
receipt["legs"]["leg2"] = {"conflicts": 0}
receipt["legs"]["leg3"] = {"origin_vacancy": True,
                           "absorb_mode": ("bm-a seat MSG-2026-10-11-0129-bma-w208-seat (01:29, stale 11h, "
                                           "no prereg/five-face) = dead-estate absorb premise per r899/r915; "
                                           "takeover by bm-c interactive completes the chain, engine_owner stays "
                                           "bm-a per the seat claim; W209=bm-c tick-window seat+prereg on origin "
                                           "awaits this freeze per the chain-order law")}

# --- leg 4: W209+ projection ------------------------------------------------------
(fc209_a, h208a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc209_b, h208b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside209 = overlaps(fc209_b, fc209_a)
receipt["legs"]["leg4"] = {"W209p_A": f"{fc209_a[0]}..{fc209_a[1]}", "hops_A": h208a,
                           "W209p_B": f"{fc209_b[0]}..{fc209_b[1]}", "hops_B": h208b,
                           "W209p_B_lands_inside_W209p_A": inside209,
                           "note": ("W209+ naive projection on pre-W208 universe; W208-B-refuses-W209-A staircase "
                                    "anticipated once W208 B registered (SIXTY-NINETH instance anticipated); W209 freezer "
                                    "MUST re-derive on the post-W208 universe AND reserve own-wave A when deriving B "
                                    "(W141 precedent, leg2 law, E36 card) -- never transcribe r587)")}
print(f"leg4: W209+ projection A {fc209_a[0]}..{fc209_a[1]} / B {fc209_b[0]}..{fc209_b[1]} (inside: {inside209})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results", "_w208bmc_20261011_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W208 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (receipt written)")
