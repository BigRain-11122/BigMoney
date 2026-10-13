# -*- coding: utf-8 -*-
"""W236 pre-seat probe (bm-a loop window r971, 2026-10-14 05:4x; standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20260924-1730
claim-ignite same-round law + never-dry supply line + O-20261013-22:1x CPU
standing-open order). Upstream face = W235 FULL CYCLE LANDED (seat
MSG-20261013-2149-bmc inherited takeover r967-r969 engine_owner reassigned
bm-a per r976-continuation precedent, verified burn-complete by bm-c r980
fb4941a6f + prereg 89bd6962c verified bm-c r979 + splice b6a0c2f42 +
engine self-burn 12/12 03:45-03:56 + six-gate PRE-FINALIZE tenth consecutive
correct-phase + finalize one-pass r970 + five-key ALL PASS
_r970bma_w235_fivekey_receipt.json + sec78 backfill) -- SINGLE
STATE: W2..W235 ALL REGISTERED, zero in-flight declared seats. This probe IS
the W236 re-derive on the post-W235-REGISTERED universe mandated by the W235
five-key key5 projection (naive W236 A 533_804..535_803 / B 534_004..534_203
with W141 own-wave-A reservation re-derive mandate; r587: never transcribed).
-- read-only band derivation before the seat MSG publication (r565
early-visibility law). Machine-derived from the LIVE post-W235-REGISTERED
universe: registry keys + seed points + bands all live-imported, zero
hard-coded band values in the walk inputs; A base == prior-wave B tail+1 and
own-A -> first-clean; B base == own-wave A tail+1 machine-checkable relation.
Anchor face: W235 finalize LANDED (ledger head 940,789 = prev 938,589 + 2,200;
merged pool K=514,920 machine-read in leg0; five-key ALL PASS
_r970bma_w235_fivekey_receipt.json landed by the r970 own-wave closeout).
W236 freeze is GATED on nothing in-flight -- upstream fully landed, clean
chain-order window.
Bloodline: _w235bmc_20261013_probe.py derive machinery verbatim, W236 facts
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
receipt = {"probe": "W236 pre-seat probe (bm-a loop r971 window, 2026-10-14 05:4x, CEO fill-order standing + seat-first law + never-dry supply line + O-20261013-22:1x CPU standing-open; post-W235-REGISTERED single-state universe, upstream W235 full cycle landed seat MSG-20261013-2149-bmc inherited-takeover/prereg 89bd6962c/splice b6a0c2f42/engine self-burn 12/12 03:45-03:56/six-gate PRE-FINALIZE tenth consecutive/finalize one-pass r970/fivekey _r970bma_w235_fivekey_receipt.json)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape (post-W235 universe: tail=W235 registered) -----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 236))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W235_A = tuple(N1_BANDS[235]["a"])
W235_B = tuple(N1_BANDS[235]["b_exit"])
assert W235_A == (531_804, 533_803) and W235_B == (533_804, 534_003) and \
    N1_BANDS[235].get("engine_owner") == "bm-a", "leg0 failed: W235 row drift (bm-a r970 own-wave closeout face)"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 225 and len(bma_rows) == 120, \
    f"leg0 ordinal drift: owner={owner_total} bma={len(bma_rows)} (expect 225/120 post-W235-finalize per the r970 five-key receipt ordinal faces)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

w235_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w235_results.json"), encoding="utf-8"))
led = (w235_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 940_789 and led.get("prev_total") == 938_589, \
    f"leg0 failed: W235 ledger machine-read drift {led}"
w235_merged_n = w235_out["null_pool_cumulative"]["merged"]["n_values"]
assert w235_merged_n == 514_920, f"leg0 failed: W235 merged pool drift {w235_merged_n}"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W235-registered",
                          "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
                          "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
                          "ordinal": 226, "bma_ordinal": 121,
                          "bma_ordinal_note": ("bm-a attempt-continuity: W235 five-key receipt = 120th owned "
                                                "(119 live rows + W235 candidate at r970 own-wave closeout); this "
                                                "candidate = 121st per the same continuity; live derive governs r359"),
                          "anchor": ("W235 finalize LANDED (ledger 940,789 = prev 938,589 + 2,200, "
                                     "K=514,920, merged mu=-0.0928 sigma=0.2451 machine-read; inherited-takeover body "
                                     "(seat MSG-20261013-2149-bmc inherited takeover r967-r969 + prereg 89bd6962c + "
                                     "splice b6a0c2f42 + burn by engine self-commits + six-gate PRE-FINALIZE tenth "
                                     "consecutive correct-phase + finalize one-pass r970 + fivekey "
                                     "_r970bma_w235_fivekey_receipt.json + sec78 backfill); upstream W2..W235 ALL "
                                     "REGISTERED single state -- W236 freeze = clean chain-order window, zero "
                                     "in-flight declared seats")}
print(f"leg0: {len(N1_BANDS)} rows tail=W235 registered, owner={owner_total} -> 226th wave, bm-a 121st owned (continuity), anchor W235 ledger head {led.get('total')} K={w235_merged_n}")

# --- W236 own vacancy on origin (both states) ----------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                         "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                        capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w236_seats = [ln for ln in all_inbox if "w236" in ln.lower() and "seat" in ln.lower()]
assert w236_seats == [], f"vacancy failed: W236 seats already exist: {w236_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '236: {"a": (' not in out_pf, "vacancy failed: W236 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W236"' not in outn1_vac, "vacancy failed: W236 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W236_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W236 per-wave prereg ALREADY on origin"
print("vacancy: W236 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the registered W235 tails ------------------
ARITH_A = (W235_A[1] + 1, W235_A[1] + WIDTH_A)
ARITH_B = (W235_B[1] + 1, W235_B[1] + WIDTH_B)


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
assert fc_a[0] == W235_B[1] + 1, "leg1 staircase A base != prior-wave B tail+1"
assert fc_b[0] == fc_a[1] + 1, "leg1 staircase B base != own-A tail+1"
assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase A-hops-prior-B NINETY-SIXTH "
                               "instance expected per W235 five-key key5 projection line)")
assert overlaps(fc_b_naive, fc_a), "leg1 naive B expected INSIDE own-A (mutual exclusion face)"
assert not overlaps(fc_a, fc_b), "leg1 A/B overlap"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a,
    "B": list(fc_b), "hops_B": hops_b,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_chain": b_trace,
    "A_semantics": ("A arithmetic continuation from registered W235 A tail REFUSED at start by "
                    "registered W235 B band (staircase A-hops-prior-B NINETY-SIXTH instance, E36 "
                    "card, per the W235 five-key key5 projection + seat MSG leg4 anticipation; "
                    "never transcribed r587); honest forward walk hops past the W235 B band"),
    "B_semantics": ("B arithmetic continuation from registered W235 B tail CLEAN on the pre-W236 "
                    "universe BUT lands INSIDE the W236 own-wave A window (same-freeze mutual "
                    "exclusion, W141 precedent, band-gate leg2 law); the walk with the own-wave "
                    "A window reserved jumps to own-A tail+1"),
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

# --- leg 4: W237+ naive projection (pre-W236 universe) ---------------------------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
assert pA_fc == pA and pA_hops == 0, f"leg4 naive A expected clean: {pA_fc} hops={pA_hops}"
assert pB_fc == pB and pB_hops == 0, f"leg4 naive B expected clean: {pB_fc} hops={pB_hops}"
receipt["legs"]["leg4"] = {
    "W237p_A": f"{pA[0]}..{pA[1]}", "hops_A": pA_hops,
    "W237p_B": f"{pB[0]}..{pB[1]}", "hops_B": pB_hops,
    "W237p_B_lands_inside_W237p_A": bool(overlaps(pB, pA)),
    "note": ("W237+ naive projection on the pre-W236 universe (assuming the W236 seat bands "
             "declared here register verbatim); the registered W236 B band will refuse the "
             "naive W237 A window once W236 is registered (A-hops-prior-B NINETY-SEVENTH "
             "instance anticipated, E36 card, W141 precedent); W237 freezer MUST re-derive on "
             "the post-W236 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587.")}
print(f"leg4: W237+ naive A {pA[0]}..{pA[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w236bma_20261014_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
