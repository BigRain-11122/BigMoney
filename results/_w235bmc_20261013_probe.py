# -*- coding: utf-8 -*-
"""W235 pre-seat probe (bm-c loop window r976 absorb, 2026-10-13 21:5x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law + never-dry supply line). Upstream face = W234 FULL CYCLE
LANDED (r974-window seat MSG-20261013-1955-bmc origin 260217d39 + dead-r976-window
prereg derive 252d5cc95 (R34 authored + subgen m31 + 18-level lineage replay 46/46
one deeper than W233 + PITFALL r958 4th instance caught live chain-leg assert ->
R34[3] heritage token fixed -> SUB block re-emitted -> rederived green)
+ dead-r976-continuation-window census-first derive (postsent calibration probe
24-face KEPT/24 LIVE/LEG231+LEG232/ASM sentinels, 86 shifts one-pass, receipt
parity W211..W229 fix) + five-face freeze splice landed de342250c
+ engine self-burn 12/12 batched ledger appends 39f7b8b0c/5022491bc/cbe25f1a4
self-committed (absorb-tail 3 shards appended by the r976 absorb window per
engine law sec.2 batched pattern) + r976-window six-gate PRE-FINALIZE 21:4x
correct phase per W217-debt standing law (ninth consecutive correct-phase wave,
W212-pattern zero recurrence) + finalize one-pass 21:5x: ledger 936,389+2,200=938,589
EXACT, merged pool K=512,720, results/perpetual_faces/n1_w234_results.json
machine-read + five-key ALL PASS _r976bmc_w234_fivekey_receipt.json + sec.7/8
machine-read backfilled into PERPETUAL_N1_W234_PREREG.md placeholders=0) -- SINGLE
STATE: W2..W234 ALL REGISTERED, zero in-flight declared seats. This probe IS
the W235 re-derive on the post-W234-REGISTERED universe mandated by the W234
probe leg4 + W234 prereg sec.8 projection (r587: never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W234-REGISTERED
universe (all upstream bands in N1_BANDS live import; no declared-injection
needed -- W210..W234 twenty-five faces all registered bm-c continuous).
Derivation faces (STAIRCASE GEOMETRY NINETY-FIFTH instance expected, W141
leg2 law + E36 card; the W234 probe leg4 + W234 prereg sec.8 anticipated
W235+ -- this probe IS that re-derive):
  A  arithmetic continuation from the registered W234 A tail -- expected
     REFUSED at its own start by the registered W234 B band (staircase
     A-hops-prior-B NINETY-FIFTH); honest forward walk -> first-clean; A base ==
     prior-wave B tail+1 machine-checkable relation.
  B  arithmetic continuation from the registered W234 B tail -- naive lands
     INSIDE the W235 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean; B base ==
     own-wave A tail+1 machine-checkable relation.
Anchor face: W234 finalize LANDED (ledger head 938,589 = prev 936,389 + 2,200;
merged pool K=512,720 machine-read in leg0; five-key ALL PASS
_r976bmc_w234_fivekey_receipt.json landed by the r976 absorb window).
W235 freeze is GATED on nothing in-flight -- upstream fully landed, clean
chain-order window.
Bloodline: _w234bmc_20261013_probe.py derive machinery verbatim, W235 facts
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
receipt = {"probe": "W235 pre-seat probe (bm-c loop r976 absorb window, 2026-10-13 21:5x, CEO fill-order standing + seat-first law + never-dry supply line; post-W234-REGISTERED single-state universe, upstream W234 full cycle landed r974-window seat MSG-1955 origin 260217d39/dead-r976-window prereg 252d5cc95/dead-r976-continuation-window splice landed de342250c+engine self-burn 39f7b8b0c+5022491bc+cbe25f1a4/six-gate PRE-FINALIZE 21:4x+finalize 21:5x/fivekey _r976bmc_w234_fivekey_receipt.json)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape (post-W234 universe: tail=W234 registered) -----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 235))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W234_A = tuple(N1_BANDS[234]["a"])
W234_B = tuple(N1_BANDS[234]["b_exit"])
assert W234_A == (529_604, 531_603) and W234_B == (531_604, 531_803) and \
    N1_BANDS[234].get("engine_owner") == "bm-c", "leg0 failed: W234 row drift (bm-c r976 continuation splice face)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 224 and len(bmc_rows) == 64, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 224/64 post-W234-splice per the r976 continuation splice receipt ordinal faces)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

w234_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w234_results.json"), encoding="utf-8"))
led = (w234_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 938_589 and led.get("prev_total") == 936_389, \
    f"leg0 failed: W234 ledger machine-read drift {led}"
w234_merged_n = w234_out["null_pool_cumulative"]["merged"]["n_values"]
assert w234_merged_n == 512_720, f"leg0 failed: W234 merged pool drift {w234_merged_n}"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W234-registered",
                          "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
                          "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
                          "ordinal": 225, "bmc_ordinal": 65,
                          "bmc_ordinal_note": ("bm-c attempt-continuity: W234 freeze receipt = 64th owned "
                                                "(63 live rows + W234 candidate at r976 continuation splice); this "
                                                "candidate = 65th per the same continuity; live derive governs r359"),
                          "anchor": ("W234 finalize LANDED (ledger 938,589 = prev 936,389 + 2,200, "
                                     "K=512,720, mu=-0.0928 sigma=0.2451 machine-read; dead-window body "
                                     "(prereg 252d5cc95 by dead r976 + splice de342250c by dead r976 continuation + burn by engine "
                                     "self-commits 39f7b8b0c/5022491bc/cbe25f1a4 absorb-tail); six-gate PRE-FINALIZE 21:4x correct phase "
                                     "per W217-debt standing law -- W235 burn window = PRE-FINALIZE standing law; "
                                     "upstream W2..W234 ALL REGISTERED single state -- W235 "
                                     "freeze = clean chain-order window, zero in-flight declared seats")}
print(f"leg0: {len(N1_BANDS)} rows tail=W234 registered, owner={owner_total} -> 224th wave, bm-c 65th owned (continuity), anchor W234 ledger head {led.get('total')} K={w234_merged_n}")

# --- W235 own vacancy on origin (both states) ----------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w235_seats = [ln for ln in all_inbox if "w235" in ln.lower() and "seat" in ln.lower()]
assert w235_seats == [], f"vacancy failed: W235 seats already exist: {w235_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '235: {"a": (' not in out_pf, "vacancy failed: W235 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W235"' not in outn1_vac, "vacancy failed: W235 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W235_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W235 per-wave prereg ALREADY on origin"
print("vacancy: W235 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the registered W234 tails ------------------
ARITH_A = (W234_A[1] + 1, W234_A[1] + WIDTH_A)
ARITH_B = (W234_B[1] + 1, W234_B[1] + WIDTH_B)


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
assert fc_a[0] == W234_B[1] + 1, "leg1 staircase A base != prior-wave B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase A-hops-prior-B NINETY-FIFTH "
                               "instance expected per W234 seat MSG leg4 projection line)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation from registered W234 A tail REFUSED at start by "
                    "registered W234 B band (staircase A-hops-prior-B NINETY-FIFTH instance, E36 "
                    "card, per the W234 seat MSG leg4 anticipation); honest forward walk, non-rotational r587"),
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
                conflicts.append(f"N1_BANDS W{wname}.{key} x W235-{tag}")
    for k, v in science_gates.SEED_REGISTRY.items():
        if isinstance(v, int) and band[0] <= v <= band[1]:
            conflicts.append(f"SEED_REGISTRY[{k}]={v} inside W235-{tag}")
    for nm, rng in (("lfc", LFC_ACTUAL), ("options", OPTIONS_ACTUAL)):
        if overlaps(rng, band):
            conflicts.append(f"{nm} actual x W235-{tag}")
    for nm, pp in (("N2/N4", N24_PROBE_POINTS), ("N2-W15", N2_W15_PROBE_POINTS),
                   ("crossface", CROSSFACE_PROBE_POINTS), ("probe", PROBE_SEEDS)):
        for p in pp:
            if band[0] <= p <= band[1]:
                conflicts.append(f"{nm} probe point {p} inside W235-{tag}")
    if overlaps(N3R1_USED, band):
        conflicts.append(f"N3-R1 used-seed band x W235-{tag}")
    for nm, bb in (("v1-in-use", V1_IN_USE), ("w1-ext", W1_EXT)):
        for r2 in bb:
            if overlaps(r2, band):
                conflicts.append(f"{nm} x W235-{tag}")
assert not conflicts, f"leg2 failed: W235 conflicts {conflicts}"

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

# --- leg 3: origin vacancy (recorded; W235 seat must NOT exist yet) -------------
receipt["legs"]["leg3"] = {"origin_vacancy": True}
print("leg3: origin vacancy held (no W235 seat / row / configs / prereq)")

# --- leg 4: W235+ projection (probe tail, next freezer re-derives) -------------
(fc235p_a, h235a) = first_clean(fc_a[1] + 1, WIDTH_A)
(fc235p_b, h235b) = first_clean(fc_b[1] + 1, WIDTH_B)
inside235 = overlaps(fc235p_b, fc235p_a)
receipt["legs"]["leg4"] = {"W235p_A": f"{fc235p_a[0]}..{fc235p_a[1]}", "hops_A": h235a,
                           "W235p_B": f"{fc235p_b[0]}..{fc235p_b[1]}", "hops_B": h235b,
                           "W235p_B_lands_inside_W235p_A": inside235,
                           "note": ("W235+ naive projection on pre-W235 universe; "
                                    "the registered W235 B band will refuse the naive W235 A window "
                                    "once W235 is registered (A-hops-prior-B NINETY-SIXTH instance "
                                    "anticipated); W235 freezer MUST re-derive on the post-W235 universe "
                                    "AND reserve own-wave A when deriving B (W141 precedent, leg2 law, "
                                    "E36 staircase card) -- never transcribe r587)")}
print(f"leg4: W235+ projection A {fc235p_a[0]}..{fc235p_a[1]} hops={h235a} / B {fc235p_b[0]}..{fc235p_b[1]} hops={h235b} (B inside A: {inside235})")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": f"{fc_a[0]}_{fc_a[1]}", "B": f"{fc_b[0]}_{fc_b[1]}"}
json.dump(receipt, open(os.path.join(ROOT, "results",
                                     "_w235bmc_20261013_probe_receipt.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"W235 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")
