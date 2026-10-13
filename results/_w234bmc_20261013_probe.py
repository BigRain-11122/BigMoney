# -*- coding: utf-8 -*-
"""W234 pre-seat probe (bm-c loop window r974, 2026-10-13 19:5x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law + never-dry supply line). Upstream face = W233 FULL CYCLE
LANDED (r968-window seat dd38a9da8 + dead-r972-window prereg derive 933e3ceea
(R33 authored + subgen m30 + 17-level lineage replay 46/46 + phase-B S-table
3 mis-aged pairs fixed, committed by the dead window itself) + dead-r973-window
census-first editor derive 8-round + five-face freeze splice landed 0ca920362 +
engine self-burn 12/12 batched ledger appends 6c1587483/d4cce3ffe self-committed +
r974-window six-gate PRE-FINALIZE 19:4x correct phase per W217-debt standing law
(eighth consecutive correct-phase wave, W212-pattern zero recurrence) + finalize
one-pass 19:5x: ledger 934,189+2,200=936,389 EXACT, merged pool K=510,520,
results/perpetual_faces/n1_w233_results.json machine-read + five-key ALL PASS
_r974bmc_w233_fivekey_receipt.json + sec.7/8 machine-read backfilled into
PERPETUAL_N1_W233_PREREG.md placeholders=0) -- SINGLE
STATE: W2..W233 ALL REGISTERED, zero in-flight declared seats. This probe IS
the W234 re-derive on the post-W233-REGISTERED universe mandated by the W233
probe leg4 + W233 prereg sec.8 projection (r587: never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W233-REGISTERED
universe (all upstream bands in N1_BANDS live import; no declared-injection
needed -- W210..W233 twenty-four faces all registered bm-c continuous).
Derivation faces (STAIRCASE GEOMETRY NINETY-FOURTH instance expected, W141
leg2 law + E36 card; the W233 probe leg4 + W233 prereg sec.8 anticipated
W234+ -- this probe IS that re-derive):
  A  arithmetic continuation from the registered W233 A tail -- expected
     REFUSED at its own start by the registered W233 B band (staircase
     A-hops-prior-B NINETY-FOURTH); honest forward walk -> first-clean; A base ==
     prior-wave B tail+1 machine-checkable relation.
  B  arithmetic continuation from the registered W233 B tail -- naive lands
     INSIDE the W234 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base ==
     own-wave A tail+1 machine-checkable relation.
Anchor face: W233 finalize LANDED (ledger head 936,389 = prev 934,189 + 2,200;
merged pool K=510,520 machine-read in leg0; five-key ALL PASS
_r974bmc_w233_fivekey_receipt.json landed by the r974 window).
W234 freeze is GATED on nothing in-flight -- upstream fully landed, clean
chain-order window.
Bloodline: _w233bmc_20261013_probe.py derive machinery verbatim, W234 facts
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
receipt = {"probe": "W234 pre-seat probe (bm-c loop r974 window, 2026-10-13 19:5x, CEO fill-order standing + seat-first law + never-dry supply line; post-W233-REGISTERED single-state universe, upstream W233 full cycle landed r968-window seat dd38a9da8/dead-r972-window prereg 933e3ceea/dead-r973-window splice landed 0ca920362+engine self-burn 6c1587483+d4cce3ffe/six-gate PRE-FINALIZE 19:4x+finalize 19:5x/fivekey _r974bmc_w233_fivekey_receipt.json)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape (post-W233 universe: tail=W233 registered) -----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 234))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W233_A = tuple(N1_BANDS[233]["a"])
W233_B = tuple(N1_BANDS[233]["b_exit"])
assert W233_A == (527_404, 529_403) and W233_B == (529_404, 529_603) and \
    N1_BANDS[233].get("engine_owner") == "bm-c", "leg0 failed: W233 row drift (bm-c r973 splice face)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 223 and len(bmc_rows) == 63, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 223/63 post-W233-splice per the r973 splice receipt ordinal faces)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

w233_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w233_results.json"), encoding="utf-8"))
led = (w233_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 936_389 and led.get("prev_total") == 934_189, \
    f"leg0 failed: W233 ledger machine-read drift {led}"
w233_merged_n = w233_out["null_pool_cumulative"]["merged"]["n_values"]
assert w233_merged_n == 510_520, f"leg0 failed: W233 merged pool drift {w233_merged_n}"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W233-registered",
                          "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
                          "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
                          "ordinal": 224, "bmc_ordinal": 64,
                          "bmc_ordinal_note": ("bm-c attempt-continuity: W233 freeze receipt = 63rd owned "
                                               "(62 live rows + W233 candidate at r973 splice); this "
                                               "candidate = 64th per the same continuity; live derive governs r359"),
                          "anchor": ("W233 finalize LANDED (ledger 936,389 = prev 934,189 + 2,200, "
                                     "K=510,520, mu=-0.0928 sigma=0.2451 machine-read; dead-window body "
                                     "(prereg 933e3ceea by dead r972 + splice 0ca920362 by dead r973 + burn by engine "
                                     "self-commits 6c1587483/d4cce3ffe); six-gate PRE-FINALIZE 19:4x correct phase "
                                     "per W217-debt standing law -- W234 burn window = PRE-FINALIZE standing law; "
                                     "upstream W2..W233 ALL REGISTERED single state -- W234 "
                                     "freeze = clean chain-order window, zero in-flight declared seats")}
print(f"leg0: {len(N1_BANDS)} rows tail=W233 registered, owner={owner_total} -> 223rd wave, bm-c 64th owned (continuity), anchor W233 ledger head {led.get('total')} K={w233_merged_n}")

# --- W234 own vacancy on origin (both states) ----------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w234_seats = [ln for ln in all_inbox if "w234" in ln.lower() and "seat" in ln.lower()]
assert w234_seats == [], f"vacancy failed: W234 seats already exist: {w234_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '234: {"a": (' not in out_pf, "vacancy failed: W234 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W234"' not in outn1_vac, "vacancy failed: W234 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W234_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W234 per-wave prereg ALREADY on origin"
print("vacancy: W234 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the registered W233 tails ------------------
ARITH_A = (W233_A[1] + 1, W233_A[1] + WIDTH_A)
ARITH_B = (W233_B[1] + 1, W233_B[1] + WIDTH_B)


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
assert fc_a[0] == W233_B[1] + 1, "leg1 staircase A base != prior-wave B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase A-hops-prior-B NINETY-FOURTH "
                               "instance expected per W233 seat MSG leg4 projection line)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation from registered W233 A tail REFUSED at start by "
                    "registered W233 B band (staircase A-hops-prior-B NINETY-FOURTH instance, E36 "
                    "card, per the W233 seat MSG leg4 anticipation); honest forward walk, non-rotational r587"),
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W234-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W234-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W234-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W234-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W234-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W234-{tag}")
assert not conflicts, f"leg2 failed: W234 conflicts {conflicts}"

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

# --- leg 3: origin vacancy (recorded; W234 seat must NOT exist yet) -------------
receipt["legs"]["leg3"] = {"origin_vacancy": True}
print("leg3: origin vacancy held (no W234 seat / row / configs / prereq)")

# --- leg 4: W234+ projection (probe tail, next freezer re-derives) -------------
(fc223_a, h222a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc223_b, h222b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside223 = overlaps(fc223_b, fc223_a)
receipt["legs"]["leg4"] = {"W234p_A": f"{fc223_a[0]}..{fc223_a[1]}", "hops_A": h222a,
                           "W234p_B": f"{fc223_b[0]}..{fc223_b[1]}", "hops_B": h222b,
                           "W234p_B_lands_inside_W234p_A": inside223,
                           "note": ("W234+ naive projection on pre-W234 universe; "
                                    "the registered W234 B band will refuse the naive W234 A window "
                                    "once W234 is registered (A-hops-prior-B NINETY-FIFTH instance "
                                    "anticipated); W234 freezer MUST re-derive on the post-W234 universe "
                                    "AND reserve own-wave A when deriving B (W141 precedent, leg2 law, "
                                    "E36 staircase card) -- never transcribe r587)")}
print(f"leg4: W234+ projection A {fc223_a[0]}..{fc223_a[1]} hops={h222a} / B {fc223_b[0]}..{fc223_b[1]} hops={h222b} (B inside A: {inside223})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_w234bmc_20261013_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W234 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
