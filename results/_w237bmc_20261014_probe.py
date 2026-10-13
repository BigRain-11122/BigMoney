# -*- coding: utf-8 -*-
"""W237 pre-seat probe (bm-c loop window r988, 2026-10-14 07:0x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law + never-dry supply line O-1819 + O-20261013-22:1x
CPU standing-open order + O-20261010-2350-bm-c sec.2 seat-first law: seats do
NOT queue behind freeze windows and MUST NOT wait for the prior wave to burn
out -- queue depth is the physical guarantee of saturation).
Upstream face = W236 seat published+reserved+frozen, BURN PENDING (seat MSG
2026-10-14-0446-bma-w236-seat @ origin 5c25db795 with probe
_w236bma_20261014 ADMIT receipt; per-wave prereg research/PERPETUAL_N1_W236_PREREG.md
landed r972 67ade8314; five-face perpetual_faces splice pending on the bm-a
lane; n1_w236_results.json absent = burn pending upstream). This seat IS the
seat-first queue-depth supply: the W237 freeze waits-upstream (W236 finalize
lands -> freeze derive same-window per the W236 seat MSG leg4 mandate: re-derive
on the post-W236-REGISTERED universe AND reserve the own-wave A window when
deriving B, W141 precedent, never transcribe r587).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W236-DECLARED
universe: registry keys + seed points + bands all live-imported, zero
hard-coded band values in the walk inputs; W236 prior-wave bands machine-read
from the frozen ADMIT receipt JSON (registry row when the bm-a splice has
landed, receipt face otherwise -- both live, zero transcription); A base ==
prior-wave B tail+1 and own-A -> first-clean; B base == own-wave A tail+1
machine-checkable relation.
Bloodline: _w236bma_20261014_probe.py derive machinery verbatim, W237 facts
live-registry/receipt-driven; dual-state leg0 (registry-first, receipt-face
fallback for the pending splice)."""
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
receipt = {"probe": "W237 pre-seat probe (bm-c loop r988 window, 2026-10-14 07:0x, CEO fill-order standing + seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + O-20261013-22:1x CPU standing-open; post-W236-DECLARED universe, upstream W236 seat 5c25db795 + prereg 67ade8314 landed, five-face splice + burn pending on the bm-a lane; seat-first queue-depth supply, freeze waits-upstream W236 finalize)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W236 prior-wave declared face ----------------------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 236))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W235_A = tuple(N1_BANDS[235]["a"])
W235_B = tuple(N1_BANDS[235]["b_exit"])
assert W235_A == (531_804, 533_803) and W235_B == (533_804, 534_003) and \
    N1_BANDS[235].get("engine_owner") == "bm-a", "leg0 failed: W235 row drift (bm-a r970 own-wave closeout face)"

# W236 prior-wave bands: registry-first (bm-a five-face splice landed), receipt-face otherwise
w236_receipt = json.load(open(os.path.join(ROOT, "results",
                                            "_w236bma_20261014_probe_receipt.json"),
                               encoding="utf-8"))
assert w236_receipt.get("verdict") == "ADMIT", "leg0 failed: W236 ADMIT receipt verdict drift"
rc_bands = w236_receipt["bands"]
W236_A = (rc_bands["a_lo"], rc_bands["a_hi"])
W236_B = (rc_bands["b_lo"], rc_bands["b_hi"])
splice_landed = 236 in N1_BANDS
if splice_landed:
    assert tuple(N1_BANDS[236]["a"]) == W236_A and \
        tuple(N1_BANDS[236]["b_exit"]) == W236_B, \
        "leg0 failed: registry W236 row != ADMIT receipt bands (two-faces drift)"
    assert N1_BANDS[236].get("engine_owner") == "bm-a", "leg0 failed: W236 engine_owner drift"
# staircase consistency of the prior-wave face vs the W235-registered tail (never transcribed r587)
assert W236_A[0] == W235_B[1] + 1, "leg0 failed: W236 A base != W235 B tail+1 (receipt face drift)"
assert W236_B[0] == W236_A[1] + 1, "leg0 failed: W236 B base != own-A tail+1 (receipt face drift)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 225 and len(bma_rows) == 120, \
    f"leg0 ordinal drift: owner={owner_total} bma={len(bma_rows)} (expect 225/120 post-W235-finalize per the r970 five-key receipt ordinal faces)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

outpre236 = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "origin/main", "--",
     "research/PERPETUAL_N1_W236_PREREG.md"], cwd=ROOT,
    encoding="utf-8", errors="replace").strip()
assert outpre236, "leg0 failed: W236 per-wave prereg NOT on origin (r972 67ade8314 face)"
w236_burn_pending = not os.path.exists(os.path.join(
    ROOT, "results", "perpetual_faces", "n1_w236_results.json"))
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W235-registered (W236 splice pending)" if not splice_landed else "W236-registered",
    "w236_splice_landed": splice_landed,
    "w236_face": "registry-row" if splice_landed else "ADMIT-receipt (declared+frozen, splice pending bm-a lane)",
    "w236_bands": {"A": list(W236_A), "B": list(W236_B)},
    "w236_burn_pending": w236_burn_pending,
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": 227, "bmc_ordinal": 65,
    "bmc_ordinal_note": ("bm-c attempt-continuity: 64 live bm-c rows + this candidate = 65th owned; "
                          "engine wave ordinal = 225 registry owner rows + W236 declared (bm-a 121st, "
                          "splice pending) + this candidate = 227th; live derive governs r359"),
    "anchor": ("W236 seat+frozen upstream (seat MSG-20261014-0446-bma-w236-seat @ origin 5c25db795 + "
               "ADMIT receipt + prereg 67ade8314 landed; five-face splice + burn pending on the bm-a lane; "
               "n1_w236_results.json absent); this SEAT does not wait for the W236 burn per seat-first law "
               "O-20261010-2350 sec.2 (queue-depth supply, 禁等上一波烧完才占下一席); the W237 FREEZE "
               "waits-upstream on W236 finalize (physical dependency, seat MSG note + M-row watch armed)")}
print(f"leg0: {len(N1_BANDS)} rows tail=W235, W236 face={'registry' if splice_landed else 'ADMIT-receipt'} A={W236_A} B={W236_B} burn_pending={w236_burn_pending}, owner={owner_total} -> 227th wave candidate, bm-c 65th owned (continuity)")

# --- W237 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w237_seats = [ln for ln in all_inbox if "w237" in ln.lower() and "seat" in ln.lower()]
assert w237_seats == [], f"vacancy failed: W237 seats already exist: {w237_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '237: {"a": (' not in out_pf, "vacancy failed: W237 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W237"' not in outn1_vac, "vacancy failed: W237 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W237_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W237 per-wave prereg ALREADY on origin"
print("vacancy: W237 origin vacancy held (no seat / row / configs / prereg)")

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands.append(W236_A)
bands.append(W236_B)
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: honest forward walk from the W236 declared tails --------------------
ARITH_A = (W236_A[1] + 1, W236_A[1] + WIDTH_A)
ARITH_B = (W236_B[1] + 1, W236_B[1] + WIDTH_B)


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
assert fc_a[0] == W236_B[1] + 1, "leg1 staircase A base != prior-wave B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase A-hops-prior-B NINETY-SEVENTH "
                               "instance expected per W236 seat MSG leg4 anticipation; "
                               "never transcribed r587)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation from the W236 declared A tail REFUSED at start by "
                    "the W236 B band (staircase A-hops-prior-B NINETY-SEVENTH instance, E36 card, "
                    "per the W236 seat MSG leg4 anticipation; never transcribed r587); honest "
                    "forward walk hops past the W236 B band"),
    "B_semantics": ("B arithmetic continuation from the W236 declared B tail CLEAN on the "
                    "pre-W237 universe BUT lands INSIDE the W237 own-wave A window (same-freeze "
                    "mutual exclusion, W141 precedent, band-gate leg2 law); the walk with the "
                    "own-wave A window reserved jumps to own-A tail+1"),
    "relation_asserts": {"A_base_eq_priorB_tail_plus1": True,
                          "B_base_eq_ownA_tail_plus1": True}}
print(f"leg1: A {fc_a} hops={hops_a} | B {fc_b} hops={hops_b} | naive B {fc_b_naive} inside own-A")

# --- leg 2: seed_admit_gate rc0 ADMIT both bands (O-20261010-1945-bm-a convention) --
gate_lines = []
for base, span in ((fc_a[0], WIDTH_A), (fc_b[0], WIDTH_B)):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "Tools", "seed_admit_gate.py"),
                         str(base), "--span", str(span)], cwd=ROOT, capture_output=True,
                        text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "").strip().splitlines()
    verdict = out[-1] if out else f"rc{r.returncode} empty"
    assert r.returncode == 0 and "verdict=FREE" in verdict, \
        f"leg2 failed: gate rc={r.returncode} base={base} span={span}: {verdict}"
    gate_lines.append(f"seed_admit_gate rc0 base={base} span={span} "
                      f"checked={span} verdict=FREE")
receipt["legs"]["leg2"] = {"conflicts": 0, "seed_admit_gate": gate_lines}
print("leg2: " + " | ".join(gate_lines))

receipt["legs"]["leg3"] = {"origin_vacancy": True}
print("leg3: origin vacancy TRUE (seat/row/configs/prereg four-check green)")

# --- leg 4: W238+ naive projection (pre-W237 universe) ---------------------------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
assert pA_fc == pA and pA_hops == 0, f"leg4 naive A expected clean: {pA_fc} hops={pA_hops}"
assert pB_fc == pB and pB_hops == 0, f"leg4 naive B expected clean: {pB_fc} hops={pB_hops}"
receipt["legs"]["leg4"] = {
    "W238p_A": f"{pA[0]}..{pA[1]}", "hops_A": pA_hops,
    "W238p_B": f"{pB[0]}..{pB[1]}", "hops_B": pB_hops,
    "W238p_B_lands_inside_W238p_A": bool(overlaps(pB, pA)),
    "note": ("W238+ naive projection on the pre-W237 universe (assuming the W237 seat bands "
             "declared here register verbatim); the registered W237 B band will refuse the "
             "naive W238 A window once W237 is registered (A-hops-prior-B NINETY-EIGHTH "
             "instance anticipated, E36 card, W141 precedent); W238 freezer MUST re-derive on "
             "the post-W237 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587.")}
print(f"leg4: W238+ naive A {pA[0]}..{pA[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w237bmc_20261014_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
