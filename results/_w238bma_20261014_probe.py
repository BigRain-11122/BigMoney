# -*- coding: utf-8 -*-
"""W238 pre-seat probe (bm-a loop window r976, 2026-10-14 07:4x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law + never-dry supply line O-1819 + O-20261013-22:1x
CPU standing-open order + O-20261010-2350-bm-c sec.2 seat-first law: seats do
NOT queue behind freeze windows and MUST NOT wait for the prior wave to burn
out -- queue depth is the physical guarantee of saturation.
Upstream face = W236 registered+FINALIZED (bm-a r975 own-wave estate-absorb
closeout: seat MSG-20261014-0446-bma-w236-seat 5c25db795 + prereg 67ade8314 +
five-face splice 6e798bd22 + engine self-burn 12/12 06:52-07:03 + six-gate
PRE-FINALIZE eleventh consecutive + finalize one-pass 16dd2cda0 + five-key ALL
PASS _r975bma_w236_fivekey_receipt.json + sec78 backfill; ledger
940,789+2,200=942,989 EXACT, merged pool K=517,120 machine-read) AND W237 =
DECLARED seat (bm-c 06:54: seat MSG-20261014-0654-bmc-w237-seat @ origin
9312ef7ac with ADMIT receipt _w237bmc_20261014_probe_receipt.json; W237
freeze unblocked same-window post-W236-finalize, M12 chain-order). This W238
seat IS the seat-first queue-depth supply (depth 2: W237 declared + this
candidate); the W238 FREEZE waits-upstream on W237 finalize (physical
dependency, seat MSG note; per the W237 seat MSG leg4 mandate: re-derive on
the post-W237-DECLARED universe AND reserve the own-wave A window when
deriving B, W141 precedent, never transcribe r587).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W237-DECLARED
universe: registry keys + seed points + bands all live-imported, zero
hard-coded band values in the walk inputs; W237 prior-wave bands machine-read
from the frozen ADMIT receipt JSON (registry row when the bm-c splice has
landed, receipt face otherwise -- both live, zero transcription); A base ==
prior-wave B tail+1 and own-A -> first-clean; B base == own-wave A tail+1
machine-checkable relation.
Bloodline: _w237bmc_20261014_probe.py derive machinery verbatim, W238 facts
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
receipt = {"probe": "W238 pre-seat probe (bm-a loop r976 window, 2026-10-14 07:4x, CEO fill-order standing + seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + O-20261013-22:1x CPU standing-open; post-W237-DECLARED universe, upstream W236 registered+FINALIZED 16dd2cda0 + W237 declared seat 9312ef7ac freeze-unblocked; W238 seat = queue-depth supply depth-2, freeze waits-upstream W237 finalize)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W236 landed face + W237 prior-wave declared face ---
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 237))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W235_A = tuple(N1_BANDS[235]["a"])
W235_B = tuple(N1_BANDS[235]["b_exit"])
assert W235_A == (531_804, 533_803) and W235_B == (533_804, 534_003) and \
    N1_BANDS[235].get("engine_owner") == "bm-a", "leg0 failed: W235 row drift (bm-a r970 own-wave closeout face)"
W236_A = tuple(N1_BANDS[236]["a"])
W236_B = tuple(N1_BANDS[236]["b_exit"])
assert W236_A == (534_004, 536_003) and W236_B == (536_004, 536_203) and \
    N1_BANDS[236].get("engine_owner") == "bm-a", "leg0 failed: W236 registry row drift (bm-a r975 own-wave closeout face)"
assert W236_A[0] == W235_B[1] + 1, "leg0 failed: W236 A base != W235 B tail+1 (registry face drift)"
assert W236_B[0] == W236_A[1] + 1, "leg0 failed: W236 B base != own-A tail+1 (registry face drift)"

# W236 finalize landed face (upstream for the W237 chain; W238 seat does NOT wait on it)
w236_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w236_results.json")
w236_fivekey = os.path.join(ROOT, "results", "_r975bma_w236_fivekey_receipt.json")
assert os.path.exists(w236_results), "leg0 failed: n1_w236_results.json absent (W236 finalize not landed)"
w236_fk = json.load(open(w236_fivekey, encoding="utf-8"))
assert w236_fk.get("five_keys_all_pass") is True, "leg0 failed: W236 five-key receipt five_keys_all_pass drift"

# W237 prior-wave bands: registry-first (bm-c five-face splice landed), receipt-face otherwise
w237_receipt = json.load(open(os.path.join(ROOT, "results",
                                            "_w237bmc_20261014_probe_receipt.json"),
                               encoding="utf-8"))
assert w237_receipt.get("verdict") == "ADMIT", "leg0 failed: W237 ADMIT receipt verdict drift"
rc_bands = w237_receipt["bands"]
W237_A = (rc_bands["a_lo"], rc_bands["a_hi"])
W237_B = (rc_bands["b_lo"], rc_bands["b_hi"])
splice_landed = 237 in N1_BANDS
if splice_landed:
    assert tuple(N1_BANDS[237]["a"]) == W237_A and \
        tuple(N1_BANDS[237]["b_exit"]) == W237_B, \
        "leg0 failed: registry W237 row != ADMIT receipt bands (two-faces drift)"
    assert N1_BANDS[237].get("engine_owner") == "bm-c", "leg0 failed: W237 engine_owner drift"
# staircase consistency of the prior-wave face vs the W236-registered tail (never transcribed r587)
assert W237_A[0] == W236_B[1] + 1, "leg0 failed: W237 A base != W236 B tail+1 (receipt face drift)"
assert W237_B[0] == W237_A[1] + 1, "leg0 failed: W237 B base != own-A tail+1 (receipt face drift)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 226 and len(bma_rows) == 121, \
    f"leg0 ordinal drift: owner={owner_total} bma={len(bma_rows)} (expect 226/121 post-W236-finalize per the r975 five-key receipt ordinal faces)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

# W237 declared seat on origin (the queue-depth-1 face this W238 seat extends)
outseat237 = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
seat_hits = [ln for ln in outseat237.splitlines()
             if "w237" in ln.lower() and "seat" in ln.lower()]
assert seat_hits, "leg0 failed: W237 seat MSG not found on origin (declared face absent)"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W236-registered (W237 splice pending)" if not splice_landed else "W237-registered",
    "w237_splice_landed": splice_landed,
    "w237_face": "registry-row" if splice_landed else "ADMIT-receipt (declared, splice pending bm-c lane)",
    "w237_bands": {"A": list(W237_A), "B": list(W237_B)},
    "w236_finalize_landed": True,
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": 228, "bma_ordinal": 122,
    "bma_ordinal_note": ("bm-a attempt-continuity: 121 live bm-a rows (tail=W236 registered+FINALIZED "
                          "bm-a r975 estate-absorb closeout) + this candidate = 122nd owned; engine wave "
                          "ordinal = 226 registry owner rows + W237 declared (bm-c 65th, splice pending) "
                          "+ this candidate = 228th; live derive governs r359"),
    "anchor": ("W236 registered+FINALIZED upstream (finalize one-pass 16dd2cda0: ledger 942,989 / "
               "K=517,120 / five-key ALL PASS _r975bma_w236_fivekey_receipt.json; n1_w236_results.json "
               "landed) + W237 declared seat (bm-c 9312ef7ac + ADMIT receipt; freeze unblocked "
               "post-W236-finalize, M12 chain-order next); this W238 SEAT does not wait for the W237 "
               "burn per seat-first law O-20261010-2350 sec.2 (queue-depth supply depth-2, "
               "禁等上一波烧完才占下一席); the W238 FREEZE waits-upstream on W237 finalize "
               "(physical dependency, seat MSG note + next-window watch armed)")}
print(f"leg0: {len(N1_BANDS)} rows tail=W236-registered, W237 face={'registry' if splice_landed else 'ADMIT-receipt'} A={W237_A} B={W237_B}, owner={owner_total} -> 228th wave candidate, bm-a 122nd owned (continuity)")

# --- W238 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w238_seats = [ln for ln in all_inbox if "w238" in ln.lower() and "seat" in ln.lower()]
assert w238_seats == [], f"vacancy failed: W238 seats already exist: {w238_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '238: {"a": (' not in out_pf, "vacancy failed: W238 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W238"' not in outn1_vac, "vacancy failed: W238 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W238_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W238 per-wave prereg ALREADY on origin"
print("vacancy: W238 origin vacancy held (no seat / row / configs / prereg)")

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands.append(W237_A)
bands.append(W237_B)
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: honest forward walk from the W237 declared tails --------------------
ARITH_A = (W237_A[1] + 1, W237_A[1] + WIDTH_A)
ARITH_B = (W237_B[1] + 1, W237_B[1] + WIDTH_B)


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
assert fc_a[0] == W237_B[1] + 1, "leg1 staircase A base != prior-wave B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase A-hops-prior-B NINETY-EIGHTH "
                               "instance expected per W237 seat MSG leg4 anticipation; "
                               "never transcribed r587)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation from the W237 declared A tail REFUSED at start by "
                    "the W237 declared B band (staircase A-hops-prior-B NINETY-EIGHTH instance, E36 card, "
                    "per the W237 seat MSG leg4 anticipation; never transcribed r587); honest "
                    "forward walk hops past the W237 declared B band"),
    "B_semantics": ("B arithmetic continuation from the W237 declared B tail CLEAN on the "
                    "pre-W238 universe BUT lands INSIDE the W238 own-wave A window (same-freeze "
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

# --- leg 4: W239+ naive projection (pre-W238 universe, honest forward face) -----
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W239p_A_naive": f"{pA[0]}..{pA[1]}", "W239p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W239p_A_naive_refusers_seeds": pA_refusers,
    "W239p_B_naive": f"{pB[0]}..{pB[1]}", "W239p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W239p_B_lands_inside_W239p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W239+ projection on the pre-W238 universe (assuming the W238 seat bands "
             "declared here register verbatim). NEW FACE vs the W237 leg4 window: the naive "
             "W239 A continuation 540_404..542_403 is REFUSED by live SEED_REGISTRY points "
             f"{pA_refusers} (machine-read, first occurrence above the 538k registered tail) -> honest "
             "forward walk first-clean A "
             f"{pA_fc[0]}..{pA_fc[1]} hops={pA_hops}; the registered W238 B band will also refuse the "
             "naive W239 A window once W238 registers (A-hops-prior-B NINETY-NINTH instance "
             "anticipated, E36 card, W141 precedent); W239 freezer MUST re-derive on the "
             "post-W238 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587.")}
print(f"leg4: W239+ naive A {pA[0]}..{pA[1]} refused-by-seeds {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w238bma_20261014_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
