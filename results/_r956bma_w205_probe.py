# -*- coding: utf-8 -*-
"""r956 bm-a W205 pre-seat probe -- read-only band derivation before the seat
MSG publication (r565 early-visibility law). Machine-derived from the LIVE
post-W203-registration universe with the W204 DECLARED bands injected
(declared-injection precedent W192/r892, mirrored by bm-c at the W204 derive
for the then-declared W203 bands; W204 seat MSG-20261010-0022-bmc-w204-seat
pushed origin 7cf82c262, origin-text-verified in probe leg0; W204 five-face
freeze still PENDING upstream -- bm-c film-chain priority disclosed).

W205 candidate = first FREE number after the REGISTERED W203 row (bm-a r936
five-face freeze + engine self-burn 12/12; finalize product LANDED r938
(ledger 858,745+2,200=860,945 EXACT, K=442,320+2,200 machine-read in probe
leg0, cross-file prev==total chain assert W203/W202); W205 freeze-time anchor
= W203 finalize actuals per r590, zero roll-forward this window).
Derivation faces (STAIRCASE GEOMETRY SIXTY-FIFTH instance expected per the
W204 pre-seat probe leg4 projection note (W204-B-refuses-W205-A staircase
anticipated, E36 card); W141 leg2 law + E36 card; the mandatory
post-W204-declared re-derive -- reserve own-wave A when deriving B is
MANDATORY, this probe IS that re-derive; the naive pre-W204-declared
continuation 465_604..467_603 is REFUSED here on the live universe by the
W204 declared B band 465_604..465_803, never transcribed).
Hardening vs r924 lineage: all subprocess git calls pinned to the REAL git
path (gitsilent forwarder in PATH swallows stdout on read ops; 10-08 19:52
pit law). Abort-safe W204-state check: if the W204 row has LANDED on origin
perpetual_faces.py since this session's sync, the probe refuses (rc!=0) and
demands a fresh pull before deriving on the registered face.
Bloodline: _r930bma_w203_probe.py machinery verbatim, W205 facts
live-registry-driven."""
import re
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
W204_SEAT_MSG_ORIGIN = "fleet/inbox/processed/MSG-20261010-0022-bmc-w204-seat.md"
W204_PREREG_ORIGIN = "research/PERPETUAL_N1_W204_PREREG.md"
receipt = {"probe": "r956 W205 pre-seat probe", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


def git_run(args):
    return subprocess.run([GIT] + args, cwd=ROOT, capture_output=True,
                           creationflags=CREAT)


def parse_num(s):
    return int(s.replace("_", ""))


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

# --- leg 0: registry shape (single state: W203 registered, tail=W203;
#     W204 declared-only, injected from origin seat MSG text) ----------------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 204))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W203_A = tuple(N1_BANDS[203]["a"])
W203_B = tuple(N1_BANDS[203]["b_exit"])
assert W203_A == (461_404, 463_403) and W203_B == (463_404, 463_603) and \
    N1_BANDS[203].get("engine_owner") == "bm-a", "leg0 failed: W203 row drift"
assert tuple(N1_BANDS[202]["a"]) == (459_204, 461_203) and \
    tuple(N1_BANDS[202]["b_exit"]) == (461_204, 461_403) and \
    N1_BANDS[202].get("engine_owner") == "bm-a", "leg0 W202 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 193 and len(bma_rows) == 118, "leg0 ordinal drift"

# W204 freeze-state guard: if the W204 row has landed on origin since this
# session's sync, refuse -- the derivation must run on the registered face
# after a fresh pull (never derive on a stale mixed universe).
out_pf = git_run(["show", "origin/main:scripts/perpetual_faces.py"]).stdout.decode("utf-8", errors="replace")
assert len(out_pf) > 1000, "leg0 failed: origin perpetual_faces.py read EMPTY (git read must be non-vacuous)"
assert '204: {"a": (' not in out_pf, ("leg0 REFUSED: W204 row ALREADY on origin "
    "(bm-c freeze landed since session sync) -- re-pull and re-derive on the "
    "registered W204 face before claiming W205")

# W204 finalize product absence guard (the W205 freeze anchor is W203; W204
# burn/finalize belongs to bm-c's lane -- honest absence note only).
onr = git_run(["ls-tree", "--name-only", "origin/main", "--",
               "results/perpetual_faces/"]).stdout.decode("utf-8", errors="replace").splitlines()
assert len(onr) > 0, "leg0 failed: origin perpetual_faces ls-tree EMPTY (git read must be non-vacuous)"
assert "results/perpetual_faces/n1_w203_results.json" in onr, \
    "leg0 failed: W203 finalize product absent on origin"
w204_final_on_origin = "results/perpetual_faces/n1_w204_results.json" in onr

# W203 finalize product machine-read (r587 never-transcribe face; W203
# finalize product LANDED r938; cross-file prev==total chain assert;
# W205 freeze-time anchor = W203 finalize actuals per r590, zero roll-forward)
w203_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w203_results.json"), encoding="utf-8"))
led = (w203_out.get("science_gates") or {}).get("ledger") or {}
w202_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w202_results.json"), encoding="utf-8"))
led202 = (w202_out.get("science_gates") or {}).get("ledger") or {}
assert led202.get("total") == 858_745, \
    f"leg0 failed: W202 ledger machine-read drift {led202}"
assert led.get("prev_total") == led202.get("total"), \
    "leg0 failed: chain-head prev != W202 total (cross-file drift)"
assert led.get("total") == led.get("prev_total", 0) + 2_200, \
    f"leg0 failed: W203 ledger total != prev+2200 ({led})"

# W204 DECLARED bands injection (origin-text-verified from the W204 seat MSG
# + cross-checked against the W204 prereg on origin; declared-injection
# precedent W192/r892, mirrored by bm-c at the W204 derive)
seat_txt = git_run(["show", f"origin/main:{W204_SEAT_MSG_ORIGIN}"]).stdout.decode("utf-8", errors="replace")
assert len(seat_txt) > 500, "leg0 failed: W204 seat MSG origin read EMPTY"
ma = re.search(r"\*\*A (\d+_\d+)\.\.(\d+_\d+)\*\*", seat_txt)
mb = re.search(r"\*\*B (\d+_\d+)\.\.(\d+_\d+)\*\*", seat_txt)
assert ma and mb, "leg0 failed: W204 declared bands not found in origin seat MSG text"
W204_A = (parse_num(ma.group(1)), parse_num(ma.group(2)))
W204_B = (parse_num(mb.group(1)), parse_num(mb.group(2)))
assert W204_A == (463_604, 465_603) and W204_B == (465_604, 465_803), \
    f"leg0 failed: W204 declared band drift vs W204 prereg-declared universe {W204_A} {W204_B}"
pre_txt = git_run(["show", f"origin/main:{W204_PREREG_ORIGIN}"]).stdout.decode("utf-8", errors="replace")
assert len(pre_txt) > 1000, "leg0 failed: W204 prereg origin read EMPTY"
assert "A-ext seed=463_604..465_603" in pre_txt and \
    "B-ext exit seed=465_604..465_803" in pre_txt, \
    "leg0 failed: W204 declared bands cross-check vs origin prereg FAILED"
declared_bands = [W204_A, W204_B]
bands += declared_bands  # injected into the derivation universe

receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W203",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 195, "bma_ordinal": 119,
                           "w203_ledger_head": led.get("total"),
                           "w203_k_head": (w203_out.get("science_gates") or {}).get("skill_line_v2"),
                           "w204_state": ("declared bm-c seat MSG-20261010-0022 (origin 7cf82c262 "
                                           "push, origin-text-verified band extraction + prereg "
                                           "cross-check) + five-face freeze PENDING upstream "
                                           "(film-chain priority) + finalize product "
                                           f"{'PRESENT' if w204_final_on_origin else 'absent'} "
                                           "on origin -- declared-injection W192/r892 precedent"),
                           "w203_status": ("registered bm-a r936 five-face freeze (r930 seat "
                                            "publication dc00bfa54 pre-freeze r565 law) + engine "
                                            "self-burn 12/12; finalize product LANDED r938 (ledger "
                                            f"{led.get('prev_total')}+2,200={led.get('total')} "
                                            "EXACT machine-read, cross-file prev==total chain "
                                            "assert W203/W202) -- W205 freeze-time anchor = W203 "
                                            "finalize actuals per r590, zero roll-forward")}
print(f"leg0: {len(N1_BANDS)} rows tail=W203, owner={len(owner_rows)} -> 195th wave, bm-a 119th owned; W204 declared {W204_A[0]}..{W204_A[1]} / {W204_B[0]}..{W204_B[1]} injected (origin-verified); anchor W203 ledger head {led.get('total')} (finalize LANDED, chain clean)")

# --- leg 1: honest forward walk from the W204-DECLARED tails ------------------
ARITH_A = (W204_A[1] + 1, W204_A[1] + WIDTH_A)
ARITH_B = (W204_B[1] + 1, W204_B[1] + WIDTH_B)


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
assert fc_a[0] == W204_B[1] + 1, "leg1 staircase A base != prior-wave B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase expected per W204 pre-seat "
                               "probe leg4 projection note (W204-B-refuses-W205-A staircase "
                               "anticipated, E36 card))")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation REFUSED at its start by the W204 declared B band "
                    "465_604..465_803 (staircase A-hops-prior-B SIXTY-FIFTH instance, E36 "
                    "card; W204 pre-seat probe leg4 projection note fulfilled); honest "
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W205-{tag}")
    for nm, db in (("W204-declared-A", W204_A), ("W204-declared-B", W204_B)):
        if overlaps(db, band):
            conflicts.append(f"{nm} x W205-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W205-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W205-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W205-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W205-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W205-{tag}")
assert not conflicts, f"leg2 failed: W205 conflicts {conflicts}"

# --- leg 3: origin vacancy (W205 seat must NOT exist yet; row/configs absent) --
r = git_run(["ls-tree", "--name-only", "-r", "origin/main", "--",
             "fleet/inbox/", "fleet/inbox/processed/"])
inbox_lines = r.stdout.decode("utf-8", errors="replace").splitlines()
assert len(inbox_lines) > 0, "leg3 failed: origin inbox ls-tree EMPTY (git read must be non-vacuous)"
seats = [ln for ln in inbox_lines
         if "w205" in ln.lower() and "seat" in ln.lower()]
assert seats == [], f"leg3 failed: W205 seats already exist: {seats}"
assert '205: {"a": (' not in out_pf, "leg3 failed: W205 row ALREADY on origin (r511 tail-lock)"
outn1 = git_run(["show", "origin/main:scripts/perpetual_faces_n1.py"]).stdout.decode("utf-8", errors="replace")
assert len(outn1) > 1000, "leg3 failed: origin perpetual_faces_n1.py read EMPTY (git read must be non-vacuous)"
assert '"batch": "PERPETUAL-N1-W205"' not in outn1, "leg3 failed: W205 WAVE_CONFIGS ALREADY on origin"
outpre = git_run(["ls-tree", "--name-only", "origin/main", "--",
                  "research/PERPETUAL_N1_W205_PREREG.md"]).stdout.decode("utf-8", errors="replace").strip()
assert not outpre, "leg3 failed: W205 per-wave prereg ALREADY on origin"
receipt["legs"]["leg2"] = {"conflicts": 0}
receipt["legs"]["leg3"] = {"origin_vacancy": True, "non_vacuous_git_reads": True}

# --- leg 4: W206+ projection (probe tail, next freezer re-derives) -------------
(fc206_a, h205a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc206_b, h205b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside205 = overlaps(fc206_b, fc206_a)
receipt["legs"]["leg4"] = {"W206p_A": f"{fc206_a[0]}_{fc206_a[1]}", "hops_A": h205a,
                           "W206p_B": f"{fc206_b[0]}_{fc206_b[1]}", "hops_B": h205b,
                           "W206p_B_lands_inside_W206p_A": inside205,
                           "note": ("W206+ naive projection on the pre-W205 universe; "
                                    "the registered W205 B band will refuse the naive W206 A "
                                    "window once W205 is registered (W205-B-refuses-W206-A "
                                    "staircase anticipated, E36 card); W206 freezer MUST "
                                    "re-derive on the post-W205 universe (and the post-W204 "
                                    "universe once bm-c's freeze lands) AND reserve own-wave A "
                                    "when deriving B (W141 precedent, leg2 law, E36 staircase "
                                    "card) -- never transcribe r587)")}
print(f"leg4: W206+ projection A {fc206_a[0]}..{fc206_a[1]} hops={h205a} / B {fc206_b[0]}..{fc206_b[1]} hops={h205b} (B inside A: {inside205})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_r956bma_w205_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W205 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
