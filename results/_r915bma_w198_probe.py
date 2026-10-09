# -*- coding: utf-8 -*-
"""r915 bm-a W198 pre-seat probe -- read-only band derivation before the seat
MSG publication (r565 early-visibility law). Machine-derived from the LIVE
post-W196-registration universe (r587: never transcribed).

W198 candidate = first FREE number after the REGISTERED W197 row (bm-a r915
dead-session five-face freeze 13:0x + estate-absorbed same round; burn COMPLETE
12/12 engine self-burned 13:01..13:12 while the first-attempt r915 session
died 13:13 pre-closeout (dead-estate absorbed per r899 law); finalize LANDED
r915 session one-pass origin 522a0aef5-lineage -- ledger 845,545+2,200=847,745
EXACT zero-deviation fourth consecutive window, K=429,120+2,200=431,320 EXACT,
four pred keys PASS; W198 freeze-time anchor = W197 finalize actuals per
r590, zero roll-forward this window).
Derivation faces (STAIRCASE GEOMETRY FIFTY-EIGHTH instance expected per
the W197 prereg sec5.5 leg4 projection + the W197 prereg sec8 succession
note; W141 leg2 law + E36 card; the mandatory post-W197 re-derive -- reserve
own-wave A when deriving B is MANDATORY, this probe IS that re-derive; naive
pre-W197-universe continuation is REFUSED here on the live universe, never
transcribed):
  A  arithmetic continuation from the registered W197 A tail (live-registry
     read) -- expected REFUSED at its own start by the registered W197 B band
     450_204..450_403 (staircase A-hops-prior-B 58th); honest forward walk ->
     first-clean, hops counted.
  B  arithmetic continuation from the registered W197 B tail -- naive lands
     INSIDE the W198 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean.
Bloodline: r910/r914 derive machinery verbatim, W198 facts
live-registry-driven."""
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
receipt = {"probe": "r915 W198 pre-seat probe", "legs": {}}


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

# --- leg 0: registry shape (single state: W197 registered, tail=W197) ----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 198))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W197_A = tuple(N1_BANDS[197]["a"])
W197_B = tuple(N1_BANDS[197]["b_exit"])
assert W197_A == (448_204, 450_203) and W197_B == (450_204, 450_403) and \
    N1_BANDS[197].get("engine_owner") == "bm-a", "leg0 failed: W197 row drift"
assert tuple(N1_BANDS[196]["a"]) == (446_004, 448_003) and \
    tuple(N1_BANDS[196]["b_exit"]) == (448_004, 448_203) and \
    N1_BANDS[196].get("engine_owner") == "bm-a", "leg0 W196 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 187 and len(bma_rows) == 112, "leg0 ordinal drift"

# W197 finalize product machine-read (r587 never-transcribe face; W197
# finalize LANDED r915 one-pass on origin (522a0aef5 rebased lineage);
# cross-file prev==total chain assert; W198 freeze-time anchor = W197
# finalize actuals per r590, zero roll-forward)
w197_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w197_results.json"), encoding="utf-8"))
led = (w197_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 847_745 and led.get("prev_total") == 845_545, \
    f"leg0 failed: W197 ledger machine-read drift {led}"
w196_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w196_results.json"), encoding="utf-8"))
led196 = (w196_out.get("science_gates") or {}).get("ledger") or {}
assert led196.get("total") == 845_545 and led.get("prev_total") == led196.get("total"), \
    "leg0 failed: chain-head prev != W196 total (cross-file drift)"
r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                    "results/perpetual_faces/"], cwd=ROOT, capture_output=True)
onr = r.stdout.decode("utf-8", errors="replace").splitlines()
assert "results/perpetual_faces/n1_w197_results.json" in onr, \
    "leg0 failed: W197 finalize product absent on origin"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W197",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 188, "bma_ordinal": 113,
                           "w197_ledger_head": led.get("total"),
                           "w196_status": ("registered bm-a r911 five-face freeze; burn COMPLETE "
                                           "12/12 engine self-burned 11:07..11:17 (r912 died "
                                           "pre-finalize, estate absorbed r913 per r899 law); "
                                           "finalize LANDED r913 session one-pass (ledger 845,545 "
                                           "EXACT, K=429,120 EXACT)"),
                           "w197_status": ("registered bm-a r915 dead-session five-face freeze "
                                           "13:0x + engine self-burn 12/12 13:01..13:12 (first-"
                                           "attempt session died 13:13 pre-closeout; dead-estate "
                                           "absorbed same-round r915 per r899 law); finalize LANDED "
                                           "r915 session one-pass origin 522a0aef5 (ledger 847,745 "
                                           "EXACT zero-deviation vs sec5 frozen projection fourth "
                                           "consecutive window, K=431,320 EXACT, four pred keys "
                                           "PASS) -- chain head FULLY CLEAN fourth consecutive "
                                           "window; W198 freeze-time anchor = W197 finalize actuals "
                                           "per r590, zero roll-forward")}
print(f"leg0: {len(N1_BANDS)} rows tail=W197, owner={len(owner_rows)} -> 188th wave, bm-a 113th owned, anchor W197 ledger head {led.get('total')} (finalize LANDED, chain clean)")

# --- leg 1: honest forward walk from the live-registry W196 tails -------------
ARITH_A = (W197_A[1] + 1, W197_A[1] + WIDTH_A)
ARITH_B = (W197_B[1] + 1, W197_B[1] + WIDTH_B)


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
assert fc_a[0] == W197_B[1] + 1, "leg1 staircase A base != prior-B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase expected per W197 prereg "
                               "sec5.5 leg4 projection + W197 prereg sec8 succession note "
                               "(W197-B-refuses-W198-A staircase anticipated, E36 card))")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation REFUSED at start by registered W197 B band "
                    "450_204..450_403 (staircase A-hops-prior-B FIFTY-EIGHTH instance, E36 card; "
                    "W197 prereg sec5.5 leg4 + W197 prereg sec8 succession note both fulfilled); "
                    "honest forward walk, non-rotational r587"),
    "B_semantics": ("B naive first-clean lands INSIDE own-wave A window -- same-freeze mutual "
                    "exclusion (W141 precedent, leg2 law); reserved walk past own-A, hops "
                    "machine-counted"),
}
print(f"leg1: A {fc_a[0]}..{fc_a[1]} hops={hops_a} + B {fc_b[0]}..{fc_b[1]} hops={hops_b} (naive B {fc_b_naive[0]}..{fc_b_naive[1]} inside own-A; staircase held)")

# --- leg 2: full reserved universe conflict scan ------------------------------
conflicts = []
for tag, band in (("A", fc_a), ("B", fc_b)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} x W198-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W198-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W198-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W198-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W198-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W198-{tag}")
assert not conflicts, f"leg2 failed: W198 conflicts {conflicts}"

# --- leg 3: origin vacancy (W197 seat must NOT exist yet; row/configs absent) --
r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                    "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                   capture_output=True)
seats = [ln for ln in r.stdout.decode("utf-8").splitlines()
         if "w198" in ln.lower() and "seat" in ln.lower()]
assert seats == [], f"leg3 failed: W198 seats already exist: {seats}"
out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                              cwd=ROOT, encoding="utf-8", errors="replace")
assert '198: {"a": (' not in out, "leg3 failed: W198 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
                                cwd=ROOT, encoding="utf-8", errors="replace")
assert '"batch": "PERPETUAL-N1-W198"' not in outn1, "leg3 failed: W198 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                  "research/PERPETUAL_N1_W198_PREREG.md"], cwd=ROOT,
                                 encoding="utf-8", errors="replace").strip()
assert not outpre, "leg3 failed: W198 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0}
receipt["legs"]["leg3"] = {"origin_vacancy": True}

# --- leg 4: W198+ projection (probe tail, next freezer re-derives) -------------
(fc199_a, h198a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc199_b, h198b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside198 = overlaps(fc199_b, fc199_a)
receipt["legs"]["leg4"] = {"W199p_A": f"{fc199_a[0]}..{fc199_a[1]}", "hops_A": h198a,
                           "W199p_B": f"{fc199_b[0]}..{fc199_b[1]}", "hops_B": h198b,
                           "W199p_B_lands_inside_W199p_A": inside198,
                           "note": ("W199+ naive projection on pre-W198 universe; "
                                    "the registered W198 B band will refuse the naive W199 A "
                                    "window once W198 is registered (W198-B-refuses-W199-A "
                                    "staircase anticipated, E36 card); W199 freezer MUST "
                                    "re-derive on the post-W198 universe AND reserve own-wave A "
                                    "when deriving B (W141 precedent, leg2 law, E36 staircase card) "
                                    "-- never transcribe r587)")}
print(f"leg4: W199+ projection A {fc199_a[0]}..{fc199_a[1]} hops={h198a} / B {fc199_b[0]}..{fc199_b[1]} hops={h198b} (B inside A: {inside198})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r915bma_w198_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W198 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
