# -*- coding: utf-8 -*-
"""r930 bm-a W203 pre-seat probe -- read-only band derivation before the seat
MSG publication (r565 early-visibility law). Machine-derived from the LIVE
post-W202-registration universe (r587: never transcribed).

W203 candidate = first FREE number after the REGISTERED W202 row (bm-a r927
five-face freeze landed d372c9xx lineage (five-face receipt validated selftest
9/9) + engine self-burn 12/12 (shard-11 done 20:45:04); finalize product
LANDED r928 one-pass push c76a84dc2 -- ledger 856,545+2,200=858,745 EXACT,
K=442,320 EXACT, skill_line_v2 1.1886->1.1887; W203 freeze-time anchor =
W202 finalize actuals per r590, zero roll-forward this window).
Derivation faces (STAIRCASE GEOMETRY SIXTY-THIRD instance expected per the
W202 pre-seat probe leg4 projection note (W202-B-refuses-W203-A staircase
anticipated, E36 card); W141 leg2 law + E36 card; the mandatory
post-W202 re-derive -- reserve own-wave A when deriving B is MANDATORY, this
probe IS that re-derive; the naive pre-W202-universe continuation 461_204..463_203
is REFUSED here on the live universe by the registered W202 B band, never
transcribed).
Hardening vs r924 lineage: all subprocess git calls pinned to the REAL git
path (gitsilent forwarder in PATH swallows stdout on read ops -> r924-lineage
leg3 vacancy checks could pass vacuously; this probe makes them non-vacuous,
10-08 19:52 pit law).
Bloodline: r918/r920/r921/r924 derive machinery verbatim, W203 facts
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

GIT = r"C:\Program Files\Git\cmd\git.exe"
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
receipt = {"probe": "r930 W203 pre-seat probe", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


def git_run(args):
    return subprocess.run([GIT] + args, cwd=ROOT, capture_output=True,
                           creationflags=CREAT)


git_run(["fetch", "origin"])

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

# --- leg 0: registry shape (single state: W202 registered, tail=W202) ----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 203))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W202_A = tuple(N1_BANDS[202]["a"])
W202_B = tuple(N1_BANDS[202]["b_exit"])
assert W202_A == (459_204, 461_203) and W202_B == (461_204, 461_403) and \
    N1_BANDS[202].get("engine_owner") == "bm-a", "leg0 failed: W202 row drift"
assert tuple(N1_BANDS[201]["a"]) == (457_004, 459_003) and \
    tuple(N1_BANDS[201]["b_exit"]) == (459_004, 459_203) and \
    N1_BANDS[201].get("engine_owner") == "bm-a", "leg0 W201 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 192 and len(bma_rows) == 117, "leg0 ordinal drift"

# W202 finalize product machine-read (r587 never-transcribe face; W202
# finalize product LANDED r928 one-pass push c76a84dc2; cross-file
# prev==total chain assert; W203 freeze-time anchor = W202 finalize actuals
# per r590, zero roll-forward)
w202_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w202_results.json"), encoding="utf-8"))
led = (w202_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 858_745 and led.get("prev_total") == 856_545, \
    f"leg0 failed: W202 ledger machine-read drift {led}"
w201_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w201_results.json"), encoding="utf-8"))
led201 = (w201_out.get("science_gates") or {}).get("ledger") or {}
assert led201.get("total") == 856_545 and led.get("prev_total") == led201.get("total"), \
    "leg0 failed: chain-head prev != W201 total (cross-file drift)"
r = git_run(["ls-tree", "--name-only", "origin/main", "--",
             "results/perpetual_faces/"])
onr = r.stdout.decode("utf-8", errors="replace").splitlines()
assert "results/perpetual_faces/n1_w202_results.json" in onr, \
    "leg0 failed: W202 finalize product absent on origin"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W202",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 193, "bma_ordinal": 118,
                           "w202_ledger_head": led.get("total"),
                           "w201_status": ("registered bm-a r923 five-face freeze (dead-session "
                                            "estate absorption c1937ac47) + engine self-burn "
                                            "12/12; finalize LANDED r924 estate-absorb push "
                                            "b71610ba4 (ledger 854,345+2,200=856,545 EXACT, "
                                            "K=440,120 EXACT, skill_line_v2 1.1885)"),
                           "w202_status": ("registered bm-a r927 five-face freeze (d372c9xx "
                                            "lineage; five-face receipt validated selftest 9/9; "
                                            "r926 build + r927 freeze + burn, seat chain opened "
                                            "r924 19:35 publication) + engine self-burn 12/12 "
                                            "(shard-11 done 20:45:04); finalize product LANDED "
                                            "r928 one-pass push c76a84dc2 (ledger "
                                            "856,545+2,200=858,745 EXACT, K=442,320 EXACT, "
                                            "skill_line_v2 1.1886->1.1887) -- W203 freeze-time "
                                            "anchor = W202 finalize actuals per r590, zero "
                                            "roll-forward")}
print(f"leg0: {len(N1_BANDS)} rows tail=W202, owner={len(owner_rows)} -> 193rd wave, bm-a 118th owned, anchor W202 ledger head {led.get('total')} (finalize product LANDED, chain clean)")

# --- leg 1: honest forward walk from the live-registry W202 tails -------------
ARITH_A = (W202_A[1] + 1, W202_A[1] + WIDTH_A)
ARITH_B = (W202_B[1] + 1, W202_B[1] + WIDTH_B)


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
assert fc_a[0] == W202_B[1] + 1, "leg1 staircase A base != prior-B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase expected per W202 pre-seat "
                               "probe leg4 projection note (W202-B-refuses-W203-A staircase "
                               "anticipated, E36 card))")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation REFUSED at start by registered W202 B band "
                    "461_204..461_403 (staircase A-hops-prior-B SIXTY-THIRD instance, E36 "
                    "card; W202 pre-seat probe leg4 projection note fulfilled); honest "
                    "forward walk, non-rotational r587"),
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W203-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W203-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W203-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W203-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W203-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W203-{tag}")
assert not conflicts, f"leg2 failed: W203 conflicts {conflicts}"

# --- leg 3: origin vacancy (W203 seat must NOT exist yet; row/configs absent) --
r = git_run(["ls-tree", "--name-only", "-r", "origin/main", "--",
             "fleet/inbox/", "fleet/inbox/processed/"])
inbox_lines = r.stdout.decode("utf-8", errors="replace").splitlines()
assert len(inbox_lines) > 0, "leg3 failed: origin inbox ls-tree EMPTY (git read must be non-vacuous)"
seats = [ln for ln in inbox_lines
         if "w203" in ln.lower() and "seat" in ln.lower()]
assert seats == [], f"leg3 failed: W203 seats already exist: {seats}"
out = git_run(["show", "origin/main:scripts/perpetual_faces.py"]).stdout.decode("utf-8", errors="replace")
assert len(out) > 1000, "leg3 failed: origin perpetual_faces.py read EMPTY (git read must be non-vacuous)"
assert '203: {"a": (' not in out, "leg3 failed: W203 row ALREADY on origin (r511 tail-lock)"
outn1 = git_run(["show", "origin/main:scripts/perpetual_faces_n1.py"]).stdout.decode("utf-8", errors="replace")
assert len(outn1) > 1000, "leg3 failed: origin perpetual_faces_n1.py read EMPTY (git read must be non-vacuous)"
assert '"batch": "PERPETUAL-N1-W203"' not in outn1, "leg3 failed: W203 WAVE_CONFIGS ALREADY on origin"
outpre = git_run(["ls-tree", "--name-only", "origin/main", "--",
                  "research/PERPETUAL_N1_W203_PREREG.md"]).stdout.decode("utf-8", errors="replace").strip()
assert not outpre, "leg3 failed: W203 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0}
receipt["legs"]["leg3"] = {"origin_vacancy": True, "non_vacuous_git_reads": True}

# --- leg 4: W204+ projection (probe tail, next freezer re-derives) -------------
(fc204_a, h203a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc204_b, h203b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside203 = overlaps(fc204_b, fc204_a)
receipt["legs"]["leg4"] = {"W204p_A": f"{fc204_a[0]}..{fc204_a[1]}", "hops_A": h203a,
                           "W204p_B": f"{fc204_b[0]}..{fc204_b[1]}", "hops_B": h203b,
                           "W204p_B_lands_inside_W204p_A": inside203,
                           "note": ("W204+ naive projection on pre-W203 universe; "
                                    "the registered W203 B band will refuse the naive W204 A "
                                    "window once W203 is registered (W203-B-refuses-W204-A "
                                    "staircase anticipated, E36 card); W204 freezer MUST "
                                    "re-derive on the post-W203 universe AND reserve own-wave A "
                                    "when deriving B (W141 precedent, leg2 law, E36 staircase "
                                    "card) -- never transcribe r587)")}
print(f"leg4: W204+ projection A {fc204_a[0]}..{fc204_a[1]} hops={h203a} / B {fc204_b[0]}..{fc204_b[1]} hops={h203b} (B inside A: {inside203})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r930bma_w203_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W203 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
