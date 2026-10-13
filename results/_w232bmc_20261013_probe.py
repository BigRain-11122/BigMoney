# -*- coding: utf-8 -*-
"""W232 pre-seat probe (bm-c loop window r966, 2026-10-13 13:4x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law + never-dry supply line). Upstream face = W231 FULL CYCLE
LANDED (r963 seat 6638ddf9f + dead-r964-window prereg derive aebe0a5ac (FIFTEEN-level
lineage replay 46/46, committed by the dead r964 window itself) + dead-12:5x-window
editor derive absorbed by r966 + r966-window five-face freeze splice executed+landed
aee0bd9fa + engine self-burn 12/12 batched ledger appends 492972ee7/4e373b743
self-committed + six-gate PRE-FINALIZE 13:3x correct phase per W217-debt standing law
(sixth consecutive correct-phase wave, W212-pattern zero recurrence) + finalize
one-pass 13:3x: ledger 929,789+2,200=931,989 EXACT, merged pool K=506,120,
results/perpetual_faces/n1_w231_results.json machine-read + five-key ALL PASS
_r966bmc_w231_fivekey_receipt.json + sec.7/8 machine-read backfilled into
PERPETUAL_N1_W231_PREREG.md placeholders=0) -- SINGLE
STATE: W2..W231 ALL REGISTERED, zero in-flight declared seats. This probe IS
the W232 re-derive on the post-W231-REGISTERED universe mandated by the W231
probe leg4 + W231 prereg sec.8 projection (r587: never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W231-REGISTERED
universe (all upstream bands in N1_BANDS live import; no declared-injection
needed -- W210..W231 twenty-two faces all registered bm-c continuous).
Derivation faces (STAIRCASE GEOMETRY NINETY-SECOND instance expected, W141
leg2 law + E36 card; the W231 probe leg4 + W231 prereg sec.8 anticipated
W232+ -- this probe IS that re-derive):
  A  arithmetic continuation from the registered W231 A tail -- expected
     REFUSED at its own start by the registered W231 B band (staircase
     A-hops-prior-B NINETY-SECOND); honest forward walk -> first-clean; A base ==
     prior-wave B tail+1 machine-checkable relation.
  B  arithmetic continuation from the registered W231 B tail -- naive lands
     INSIDE the W232 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base ==
     own-wave A tail+1 machine-checkable relation.
Anchor face: W231 finalize LANDED (ledger head 931,989 = prev 929,789 + 2,200;
merged pool K=506,120 machine-read in leg0; five-key ALL PASS
_r966bmc_w231_fivekey_receipt.json landed by the r966 window).
W232 freeze is GATED on nothing in-flight -- upstream fully landed, clean
chain-order window.
Bloodline: _w231bmc_20261013_probe.py derive machinery verbatim, W232 facts
live-registry-driven; single-state universe (no declared-injection legs)."""
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
receipt = {"probe": "W232 pre-seat probe (bm-c loop r966 window, 2026-10-13 13:4x, CEO fill-order standing + seat-first law + never-dry supply line; post-W231-REGISTERED single-state universe, upstream W231 full cycle landed r963 seat 6638ddf9f/dead-r964-window prereg aebe0a5ac/r966-window splice landed aee0bd9fa+engine self-burn 492972ee7+4e373b743/six-gate PRE-FINALIZE 13:3x+finalize 13:3x/fivekey _r966bmc_w231_fivekey_receipt.json)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape (post-W231 universe: tail=W231 registered) -----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 232))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W231_A = tuple(N1_BANDS[231]["a"])
W231_B = tuple(N1_BANDS[231]["b_exit"])
assert W231_A == (523_004, 525_003) and W231_B == (525_004, 525_203) and \
    N1_BANDS[231].get("engine_owner") == "bm-c", "leg0 failed: W231 row drift (bm-c r966 splice face)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 221 and len(bmc_rows) == 61, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 221/61 post-W231-splice per the r966 splice receipt ordinal faces)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

w231_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w231_results.json"), encoding="utf-8"))
led = (w231_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 931_989 and led.get("prev_total") == 929_789, \
    f"leg0 failed: W231 ledger machine-read drift {led}"
w231_merged_n = w231_out["null_pool_cumulative"]["merged"]["n_values"]
assert w231_merged_n == 506_120, f"leg0 failed: W231 merged pool drift {w231_merged_n}"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W231-registered",
                          "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
                          "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
                          "ordinal": 222, "bmc_ordinal": 62,
                          "bmc_ordinal_note": ("bm-c attempt-continuity: W231 freeze receipt = 61st owned "
                                               "(60 live rows + W231 candidate at r966 splice); this "
                                               "candidate = 62nd per the same continuity; live derive governs r359"),
                          "anchor": ("W231 finalize LANDED (ledger 931,989 = prev 929,789 + 2,200, "
                                     "K=506,120, mu=-0.0927 sigma=0.2451 machine-read; r966-window body "
                                     "(prereg aebe0a5ac by dead r964 + splice aee0bd9fa by r966 + burn by engine "
                                     "self-commits 492972ee7/4e373b743); six-gate PRE-FINALIZE 13:3x correct phase "
                                     "per W217-debt standing law -- W232 burn window = PRE-FINALIZE standing law; "
                                     "upstream W2..W231 ALL REGISTERED single state -- W232 "
                                     "freeze = clean chain-order window, zero in-flight declared seats")}
print(f"leg0: {len(N1_BANDS)} rows tail=W231 registered, owner={owner_total} -> 221st wave, bm-c 62nd owned (continuity), anchor W231 ledger head {led.get('total')} K={w231_merged_n}")

# --- W232 own vacancy on origin (both states) ----------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w232_seats = [ln for ln in all_inbox if "w232" in ln.lower() and "seat" in ln.lower()]
assert w232_seats == [], f"vacancy failed: W232 seats already exist: {w232_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '232: {"a": (' not in out_pf, "vacancy failed: W232 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W232"' not in outn1_vac, "vacancy failed: W232 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W232_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W232 per-wave prereg ALREADY on origin"
print("vacancy: W232 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the registered W231 tails ------------------
ARITH_A = (W231_A[1] + 1, W231_A[1] + WIDTH_A)
ARITH_B = (W231_B[1] + 1, W231_B[1] + WIDTH_B)


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
assert fc_a[0] == W231_B[1] + 1, "leg1 staircase A base != prior-wave B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase A-hops-prior-B NINETY-SECOND "
                               "instance expected per W231 seat MSG leg4 projection line)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation from registered W231 A tail REFUSED at start by "
                    "registered W231 B band (staircase A-hops-prior-B NINETY-SECOND instance, E36 "
                    "card, per the W231 seat MSG leg4 anticipation); honest forward walk, non-rotational r587"),
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W232-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W232-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W232-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W232-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W232-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W232-{tag}")
assert not conflicts, f"leg2 failed: W232 conflicts {conflicts}"

# --- seed_admit_gate (O-20261010-1945-bm-a ADMIT convention upgrade) ------------
gate_lines = []
for base, span in ((fc_a[0], WIDTH_A), (fc_b[0], WIDTH_B)):
    g = subprocess.run([sys.executable, os.path.join(ROOT, "Tools", "seed_admit_gate.py"),
                        str(base), "--span", str(span)],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", creationflags=CREAT)
    assert g.returncode == 0, f"seed_admit_gate FAIL base={base}: {g.stdout} {g.stderr}"
    gate_lines.append(g.stdout.strip().splitlines()[-1] if g.stdout.strip() else f"rc0 base={base} span={span}")
receipt["legs"]["leg2"] = {"conflicts": 0, "seed_admit_gate": gate_lines}
print("leg2: conflicts=0; seed_admit_gate:", " | ".join(gate_lines))

# --- leg 3: origin vacancy (recorded; W232 seat must NOT exist yet) -------------
receipt["legs"]["leg3"] = {"origin_vacancy": True}
print("leg3: origin vacancy held (no W232 seat / row / configs / prereq)")

# --- leg 4: W232+ projection (probe tail, next freezer re-derives) -------------
(fc223_a, h222a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc223_b, h222b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside223 = overlaps(fc223_b, fc223_a)
receipt["legs"]["leg4"] = {"W232p_A": f"{fc223_a[0]}..{fc223_a[1]}", "hops_A": h222a,
                           "W232p_B": f"{fc223_b[0]}..{fc223_b[1]}", "hops_B": h222b,
                           "W232p_B_lands_inside_W232p_A": inside223,
                           "note": ("W232+ naive projection on pre-W232 universe; "
                                    "the registered W232 B band will refuse the naive W232 A window "
                                    "once W232 is registered (A-hops-prior-B NINETY-THIRD instance "
                                    "anticipated); W232 freezer MUST re-derive on the post-W232 universe "
                                    "AND reserve own-wave A when deriving B (W141 precedent, leg2 law, "
                                    "E36 staircase card) -- never transcribe r587)")}
print(f"leg4: W232+ projection A {fc223_a[0]}..{fc223_a[1]} hops={h222a} / B {fc223_b[0]}..{fc223_b[1]} hops={h222b} (B inside A: {inside223})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_w232bmc_20261013_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W232 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
