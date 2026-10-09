# -*- coding: utf-8 -*-
"""r924 bm-a W202 pre-seat probe -- read-only band derivation before the seat
MSG publication (r565 early-visibility law). Machine-derived from the LIVE
post-W201-registration universe (r587: never transcribed).

W202 candidate = first FREE number after the REGISTERED W201 row (bm-a r923
five-face freeze landed via dead-session estate absorption c1937ac47 (r922
died pre-commit: freeze receipt 18:41 + registry edits 465 lines validated
selftest 9/9) + engine self-burn 12/12; finalize product LANDED r924
estate-absorb push b71610ba4 -- ledger 854,345+2,200=856,545 EXACT, K=440,120
EXACT, skill_line_v2 1.1883->1.1885; W202 freeze-time anchor = W201 finalize
actuals per r590, zero roll-forward this window).
Derivation faces (STAIRCASE GEOMETRY SIXTY-SECOND instance expected per the
W201 prereg leg4 projection note (W201-B-refuses-W202-A staircase
anticipated, E36 card); W141 leg2 law + E36 card; the mandatory
post-W201 re-derive -- reserve own-wave A when deriving B is MANDARY, this
probe IS that re-derive; the naive pre-W201-universe continuation 459_004..461_003
is REFUSED here on the live universe by the registered W201 B band, never
transcribed).
Bloodline: r918/r920/r921 derive machinery verbatim, W202 facts live-registry-driven."""
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
receipt = {"probe": "r924 W202 pre-seat probe", "legs": {}}


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

# --- leg 0: registry shape (single state: W201 registered, tail=W201) ----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 202))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W201_A = tuple(N1_BANDS[201]["a"])
W201_B = tuple(N1_BANDS[201]["b_exit"])
assert W201_A == (457_004, 459_003) and W201_B == (459_004, 459_203) and \
    N1_BANDS[201].get("engine_owner") == "bm-a", "leg0 failed: W201 row drift"
assert tuple(N1_BANDS[200]["a"]) == (454_804, 456_803) and \
    tuple(N1_BANDS[200]["b_exit"]) == (456_804, 457_003) and \
    N1_BANDS[200].get("engine_owner") == "bm-a", "leg0 W200 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 191 and len(bma_rows) == 116, "leg0 ordinal drift"

# W201 finalize product machine-read (r587 never-transcribe face; W201
# finalize product LANDED r924 estate-absorb push b71610ba4 (dead r923 session
# generated 19:05:50, successor absorb+push same window); cross-file
# prev==total chain assert; W202 freeze-time anchor = W201 finalize actuals
# per r590, zero roll-forward)
w201_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w201_results.json"), encoding="utf-8"))
led = (w201_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 856_545 and led.get("prev_total") == 854_345, \
    f"leg0 failed: W201 ledger machine-read drift {led}"
w200_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w200_results.json"), encoding="utf-8"))
led200 = (w200_out.get("science_gates") or {}).get("ledger") or {}
assert led200.get("total") == 854_345 and led.get("prev_total") == led200.get("total"), \
    "leg0 failed: chain-head prev != W200 total (cross-file drift)"
r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                    "results/perpetual_faces/"], cwd=ROOT, capture_output=True)
onr = r.stdout.decode("utf-8", errors="replace").splitlines()
assert "results/perpetual_faces/n1_w201_results.json" in onr, \
    "leg0 failed: W201 finalize product absent on origin"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W201",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 192, "bma_ordinal": 117,
                           "w201_ledger_head": led.get("total"),
                           "w200_status": ("registered bm-a r921 five-face freeze + engine "
                                           "self-burn 12/12; finalize LANDED r921 one-pass "
                                           "push bdfe1efba (ledger 854,345 EXACT, K=437,920)"),
                           "w201_status": ("registered bm-a r923 five-face freeze (dead-session "
                                            "estate absorption c1937ac47; r922 died pre-commit, "
                                            "freeze receipt 18:41 validated) + engine self-burn "
                                            "12/12; finalize product generated 19:05:50, LANDED "
                                            "r924 estate-absorb push b71610ba4 (ledger "
                                            "854,345+2,200=856,545 EXACT, K=440,120 EXACT, "
                                            "skill_line_v2 1.1885) -- W202 freeze-time anchor = "
                                            "W201 finalize actuals per r590, zero roll-forward")}
print(f"leg0: {len(N1_BANDS)} rows tail=W201, owner={len(owner_rows)} -> 192nd wave, bm-a 117th owned, anchor W201 ledger head {led.get('total')} (finalize product LANDED, chain clean)")

# --- leg 1: honest forward walk from the live-registry W201 tails -------------
ARITH_A = (W201_A[1] + 1, W201_A[1] + WIDTH_A)
ARITH_B = (W201_B[1] + 1, W201_B[1] + WIDTH_B)


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
assert fc_a[0] == W201_B[1] + 1, "leg1 staircase A base != prior-B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase expected per W201 prereg "
                               "leg4 projection note (W201-B-refuses-W202-A staircase "
                               "anticipated, E36 card))")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation REFUSED at start by registered W201 B band "
                    "459_004..459_203 (staircase A-hops-prior-B SIXTY-SECOND instance, E36 "
                    "card; W201 prereg leg4 projection note fulfilled); honest forward walk, "
                    "non-rotational r587"),
    "B_semantics": ("B naive first-clean lands INSIDE own-wave A window -- same-freeze "
                    "mutual exclusion (W141 precedent, leg2 law); reserved walk past "
                    "own-A, hops machine-counted"),
}
print(f"leg1: A {fc_a[0]}..{fc_a[1]} hops={hops_a} + B {fc_b[0]}..{fc_b[1]} hops={hops_b} (naive B {fc_b_naive[0]}..{fc_b_naive[1]} inside own-A; staircase held)")

# --- leg 2: full reserved universe conflict scan ------------------------------
conflicts = []
for tag, band in (("A", fc_a), ("B", fc_b)):
    for wname, cfg in N1_BANDS.items():
        for key in ("a", "b_exit"):
            lo, hi = cfg[key]
            if overlaps((lo, hi), band):
                conflicts.append(f"N1_BANDS W{wname}.{key} x W202-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W202-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W202-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W202-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W202-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W202-{tag}")
assert not conflicts, f"leg2 failed: W202 conflicts {conflicts}"

# --- leg 3: origin vacancy (W202 seat must NOT exist yet; row/configs absent) --
r = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                    "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                   capture_output=True)
seats = [ln for ln in r.stdout.decode("utf-8").splitlines()
         if "w202" in ln.lower() and "seat" in ln.lower()]
assert seats == [], f"leg3 failed: W202 seats already exist: {seats}"
out = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                              cwd=ROOT, encoding="utf-8", errors="replace")
assert '202: {"a": (' not in out, "leg3 failed: W202 row ALREADY on origin (r511 tail-lock)"
outn1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
                                cwd=ROOT, encoding="utf-8", errors="replace")
assert '"batch": "PERPETUAL-N1-W202"' not in outn1, "leg3 failed: W202 WAVE_CONFIGS ALREADY on origin"
outpre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                  "research/PERPETUAL_N1_W202_PREREG.md"], cwd=ROOT,
                                 encoding="utf-8", errors="replace").strip()
assert not outpre, "leg3 failed: W202 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0}
receipt["legs"]["leg3"] = {"origin_vacancy": True}

# --- leg 4: W203+ projection (probe tail, next freezer re-derives) -------------
(fc203_a, h202a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc203_b, h202b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside202 = overlaps(fc203_b, fc203_a)
receipt["legs"]["leg4"] = {"W203p_A": f"{fc203_a[0]}..{fc203_a[1]}", "hops_A": h202a,
                           "W203p_B": f"{fc203_b[0]}..{fc203_b[1]}", "hops_B": h202b,
                           "W203p_B_lands_inside_W203p_A": inside202,
                           "note": ("W203+ naive projection on pre-W202 universe; "
                                    "the registered W202 B band will refuse the naive W203 A "
                                    "window once W202 is registered (W202-B-refuses-W203-A "
                                    "staircase anticipated, E36 card); W203 freezer MUST "
                                    "re-derive on the post-W202 universe AND reserve own-wave A "
                                    "when deriving B (W141 precedent, leg2 law, E36 staircase card) "
                                    "-- never transcribe r587)")}
print(f"leg4: W203+ projection A {fc203_a[0]}..{fc203_a[1]} hops={h202a} / B {fc203_b[0]}..{fc203_b[1]} hops={h202b} (B inside A: {inside202})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r924bma_w202_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W202 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
