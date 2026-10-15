# -*- coding: utf-8 -*-
"""W249 pre-seat probe (bm-c loop window r1037, 2026-10-15 23:0x; queue-head
supply lane: upstream W248 = bm-c OWN registered+FINALIZED complete chain
(prereg r1035 20:0x -> dead-window five-face splice 21:36 -> r1036 absorb
finalize: ledger 969,935 EXACT (967,735+2,200) / merged pool K=543,520
(541,320+2,200) / fivekeys ALL PASS _r1036bmc_w248_fivekeys.json / sixgate
dual-sha16 pf fd8b95810b45c48c + n1 72e95889017708ba / engine self-burn 12/12)
-- NO in-flight seat upstream: the W249 FREEZE is UNBLOCKED at seat time (no
waits-upstream face; the W249 freezer proceeds prereg derive + five-face splice
on the post-W248-REGISTERED universe per seat-first law O-20261010-2350-bm-c
sec.2, prereg derive = next window FIRST ACTION).
Standing CEO fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x +
O-20261013 22:1x CPU standing-open + O-20260924-1730 claim-ignite same-round
law + never-dry supply line O-1819 + O-20261015-0025 full mobilization.
Universe face = post-W248-REGISTERED (live registry, 238 owner rows:
bm-a 129 / bm-b 41 / bm-c 68 incl W248; W249 candidate = 239th wave,
bm-c 69th owned).
Anticipated face (W248 probe leg4, honest forward face): naive W249 A
continuation 563_501..565_500 first-clean hops=0 (no live refusers) / naive B
544_901..545_100 first-clean hops=0 (clean arithmetic continuation) -- live
re-derive governs either way, non-rotational r587 forward-monotone enforced
in-walk; never transcribe r587.
Bloodline: _w248bmc_20261015_probe.py derive machinery verbatim, W249 facts
live-registry-driven; leg0 extended with the chain-relation anchors leg
(W247->W248 ledger/K continuity +2200/+2200) and the no-skip-claim leg
(W250/W251 inbox vacancy -- seat numbering stays dense)."""
import subprocess
import sys, os, json
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
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
receipt = {"probe": "W249 pre-seat probe (bm-c loop r1037 window, 2026-10-15 23:0x, queue-head supply lane: upstream W248 = bm-c OWN registered+FINALIZED complete chain (r1036 absorb finalize ledger 969,935 / K=543,520); NO in-flight seat upstream -- W249 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing + O-20261015-0025 full mobilization; universe = post-W248-REGISTERED 238 owner rows)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W245..W248 landed faces + chain-relation anchors ---
keys = sorted(N1_BANDS)
w248_splice_landed = 248 in N1_BANDS
assert w248_splice_landed, "leg0 failed: W248 splice not landed (registry row absent -- r1036 absorb face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 249))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert 249 not in N1_BANDS, "leg0 failed: W249 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W249 universe honestly, do not seat on a stale universe)"

W245_A = tuple(N1_BANDS[245]["a"])
W245_B = tuple(N1_BANDS[245]["b_exit"])
assert W245_A == (555_501, 557_500) and W245_B == (542_001, 542_200) and \
    N1_BANDS[245].get("engine_owner") == "bm-a", "leg0 failed: W245 registry row drift"

W246_A = tuple(N1_BANDS[246]["a"])
W246_B = tuple(N1_BANDS[246]["b_exit"])
assert W246_A == (557_501, 559_500) and W246_B == (542_201, 542_400) and \
    N1_BANDS[246].get("engine_owner") == "bm-a", "leg0 failed: W246 registry row drift"
assert W246_B[0] == W245_B[1] + 1, \
    "leg0 failed: W246 B base != W245 B tail+1 (registry face drift: double-clean arithmetic continuation)"

W247_A = tuple(N1_BANDS[247]["a"])
W247_B = tuple(N1_BANDS[247]["b_exit"])
assert W247_A == (559_501, 561_500) and W247_B == (544_501, 544_700) and \
    N1_BANDS[247].get("engine_owner") == "bm-a", "leg0 failed: W247 registry row drift (bm-a splice+finalize face)"
assert W247_A[0] == W246_A[1] + 1, \
    "leg0 failed: W247 A base != W246 A tail+1 (seed-gap A-continuation face drift)"

W248_A = tuple(N1_BANDS[248]["a"])
W248_B = tuple(N1_BANDS[248]["b_exit"])
assert W248_A == (561_501, 563_500) and W248_B == (544_701, 544_900) and \
    N1_BANDS[248].get("engine_owner") == "bm-c", "leg0 failed: W248 registry row drift (bm-c r1036 absorb splice face)"
assert W248_A[0] == W247_A[1] + 1, \
    "leg0 failed: W248 A base != W247 A tail+1 (seed-gap A-continuation face drift)"
assert W248_B[0] == W247_B[1] + 1, \
    "leg0 failed: W248 B base != W247 B tail+1 (post-staircase-hop arithmetic continuation face drift)"

for _w in (246, 247, 248):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

w247_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w247_results.json")
w247_out = json.load(open(w247_results, encoding="utf-8"))
w247_led = (w247_out.get("science_gates") or {}).get("ledger") or {}
w247_total = w247_led.get("total")
w247_merged_n = None
try:
    w247_merged_n = w247_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w247_total == 967_735 and w247_merged_n == 541_320, \
    f"leg0 failed: W247 finalize anchors drift: total={w247_total} merged={w247_merged_n} (expect 967,735 / 541,320)"

w248_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w248_results.json")
w248_out = json.load(open(w248_results, encoding="utf-8"))
w248_led = (w248_out.get("science_gates") or {}).get("ledger") or {}
w248_total = w248_led.get("total")
w248_merged_n = None
w248_klift = None
try:
    w248_merged_n = w248_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
try:
    w248_klift = w248_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
except Exception:
    pass
assert w248_total == 969_935 and w248_merged_n == 543_520, \
    f"leg0 failed: W248 finalize anchors drift: total={w248_total} merged={w248_merged_n} (expect 969,935 / 543,520)"
assert w248_total == w247_total + 2_200 and w248_merged_n == w247_merged_n + 2_200, \
    "leg0 failed: W247->W248 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w248_klift is not None and abs(w248_klift) <= 0.02, \
    f"leg0 failed: W248 K-lift out-of-band at seat time: {w248_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 238 and len(bmc_rows) == 68, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 238/68 post-W248-splice, W249 unregistered)"
ordinal = owner_total + 1
assert ordinal == 239, f"leg0 ordinal derive: {ordinal} != 239"
assert len(bma_rows) == 129, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 129 post-W248-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"
bmc_ordinal = len(bmc_rows) + 1
assert bmc_ordinal == 69, f"leg0 bmc ordinal derive: {bmc_ordinal} != 69"

# --- leg 0.5: no-skip-claim leg (seat numbering density) + chain-complete face --
out_inbox = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
all_inbox = out_inbox.splitlines()
w249_seats_pre = [ln for ln in all_inbox if "w249" in ln.lower() and "seat" in ln.lower()]
assert w249_seats_pre == [], f"leg0.5 failed: W249 seat already claimed on origin: {w249_seats_pre} (vacancy broken -- yield per fleet README sec.4)"
skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w250", "w251")) and "seat" in ln.lower()]
assert skip_claims == [], f"leg0.5 failed: skip-ahead seat claims exist (W250/W251 without W249 seated -- seat-numbering density violated): {skip_claims}"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W248-registered+FINALIZED (bm-c own-wave complete)",
    "w248_splice_landed": w248_splice_landed,
    "w248_bands": {"A": list(W248_A), "B": list(W248_B)},
    "w247_bands": {"A": list(W247_A), "B": list(W247_B)},
    "w248_finalize_landed": True,
    "w248_finalize_anchors": {"ledger_total": w248_total, "merged_n": w248_merged_n,
                               "skill_line_delta_k_lift": w248_klift},
    "chain_relation": {"w247_total": w247_total, "w248_total": w248_total,
                        "ledger_delta": w248_total - w247_total,
                        "k_delta": w248_merged_n - w247_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W248 complete: registered+FINALIZED; the W249 FREEZE is UNBLOCKED at seat time -- prereg derive = next window FIRST ACTION on the post-W248 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal, "bmc_ordinal": bmc_ordinal,
    "bmc_ordinal_note": ("bm-c 69th owned [W241, W248, now W249 -- attempt-continuity: the "
                          "superseded W245-bmc seat claim (quarantined 20261015T0924) left the "
                          "live rows intact; live derive governs r359]; engine wave ordinal = "
                          "238 registry owner rows + this candidate = 239th"),
    "anchor": ("W248 registered+FINALIZED own-wave (bm-c r1035 prereg + dead-window splice "
               "21:36 + r1036 absorb finalize: ledger 969,935 EXACT (967,735+2,200) / K=543,520 "
               "(541,320+2,200) / fivekeys ALL PASS results/_r1036bmc_w248_fivekeys.json / "
               "sixgate dual-sha16 pf fd8b95810b45c48c + n1 72e95889017708ba) -- this W249 SEAT "
               "= queue-head supply per seat-first law O-20261010-2350 sec.2 (seats never queue "
               "behind freeze windows; standing CEO fill-order + O-20261013 22:1x CPU "
               "standing-open + O-20261015-0025 full mobilization + never-dry O-1819); the W249 "
               "FREEZE is UNBLOCKED (no in-flight seat upstream): the freezer proceeds prereg "
               "derive + five-face splice re-derived on the post-W248 universe")}
print(f"leg0: {len(N1_BANDS)} rows tail=W248-registered+FINALIZED (bm-c own-wave complete, W249 unregistered), W248 face=registry A={W248_A} B={W248_B}, chain-relation W247->W248 ledger 967,735->969,935 (+2,200) K 541,320->543,520 (+2,200) OK, owner={owner_total} -> W249=239th wave candidate, bm-c 69th owned")
print("leg0.5: no W249 seat claim on origin (vacancy held) + zero skip-ahead W250/W251 seat claims (numbering density green) + waits-upstream=NONE (W249 freeze UNBLOCKED)")

# --- W249 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox2 = r_vac.stdout.decode("utf-8").splitlines()
w249_seats = [ln for ln in all_inbox2 if "w249" in ln.lower() and "seat" in ln.lower()]
assert w249_seats == [], f"vacancy failed: W249 seats already exist: {w249_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '249: {"a": (' not in out_pf, "vacancy failed: W249 row ALREADY on origin (r511 tail-lock"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W249"' not in outn1_vac, "vacancy failed: W249 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W249_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W249 per-wave prereg ALREADY on origin"
print("vacancy: W249 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the W248 REGISTERED tails ------------------
ARITH_A = (W248_A[1] + 1, W248_A[1] + WIDTH_A)
ARITH_B = (W248_B[1] + 1, W248_B[1] + WIDTH_B)


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
            trace.append({"hop": hops + 1, "window": [lo, hi], "jump_to": jump,
                          "refuser_pts": sorted(bad_pts),
                          "refuser_bands": [list(b) for b in bad_bands]})
        lo = jump
        prev_lo = lo
        hops += 1


a_trace = []
(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A, trace=a_trace)
# own-wave A reservation for B (standard leg): B walk reserves the own-A window
b_trace_own = []
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace_own,
                             extra_bands=(fc_a,))
assert fc_a[0] == ARITH_A[0], ("leg1 A refused at naive start (W248 probe leg4 anticipated "
                                "first-clean 563_501..565_500 hops=0 on this universe; never "
                                "transcribe r587 -- if this fires the universe changed: re-read "
                                "the live trace honestly)")
assert not overlaps(fc_a, W247_A) and not overlaps(fc_a, W247_B), \
    "leg1 failed: A overlaps prior-wave W247 registered bands"
assert not overlaps(fc_a, W248_A) and not overlaps(fc_a, W248_B), \
    "leg1 failed: A overlaps prior-wave W248 registered bands"
assert fc_a[0] >= W248_B[1] + 1, \
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
assert hops_b == 0 and fc_b == (544_901, 545_100), \
    f"leg1 B unexpected walk face (the W248 probe leg4 projected naive B 544_901..545_100 first-clean hops=0; if the universe changed the honest walk governs and this assert must be re-derived honestly): got hops={hops_b} fc_b={fc_b}"
assert fc_b[0] > W248_B[1], \
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W247_A) and not overlaps(fc_b, W247_B), \
    "leg1 failed: B overlaps prior-wave W247 registered bands"
assert not overlaps(fc_b, W248_A) and not overlaps(fc_b, W248_B), \
    "leg1 failed: B overlaps prior-wave W248 registered bands"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace_own,
    "B_naive_first_clean": list(fc_b), "B_naive_hops": hops_b,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "A_semantics": ("A arithmetic continuation from the REGISTERED W248 A tail "
                    "563_500+1 = 563_501..565_500 is CLEAN at naive start on the "
                    "post-W248-REGISTERED universe (twelfth consecutive seed-gap "
                    "A-continuation face, anticipated by the W248 probe leg4 and "
                    "confirmed live; never transcribe r587); A base = first clean "
                    "window, forward-monotone non-rotational r587 enforced in-walk; "
                    "A base >= registered prior-wave B tail+1 floor relation"),
    "B_semantics": ("B arithmetic continuation from the REGISTERED W248 B tail "
                    "544_900+1 = 544_901..545_100 is CLEAN at naive start (hops=0, "
                    "clean arithmetic continuation past the W239 staircase band-hop "
                    "landing; the registered W239 A band 542_501..544_500 and the "
                    "W247/W248 B bands all sit below the walk start); B_hop "
                    "lands-inside-A=false leg; B_no_ownA_jump=true (the clean B "
                    "window is below the own-A window)"),
    "relation_asserts": {"A_clean_at_naive_start": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": True,
                          "B_base_above_W248_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "W247_W248_bands_respected_A": True,
                          "W247_W248_bands_respected_B": True}}
print(f"leg1: A {fc_a} hops={hops_a} (hop chain {[(t['window'], t['jump_to']) for t in a_trace]}) | B {fc_b} hops={hops_b} (refusal trace {[(t['window'], t['jump_to'], t['refuser_bands']) for t in b_trace_own]})")

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

# --- leg 4: W250+ naive projection (pre-W249 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W250p_A_naive": f"{pA[0]}..{pA[1]}", "W250p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W250p_A_naive_refusers_seeds": pA_refusers,
    "W250p_B_naive": f"{pB[0]}..{pB[1]}", "W250p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W250p_B_lands_inside_W250p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W250+ projection on the pre-W249 universe (assuming the W249 seat bands "
             "declared here register verbatim). The W250 freezer MUST re-derive on the "
             "post-W249 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587; seed-gap face inherited from W239..W248: "
             "A/B decoupled, re-read the live trace, do NOT assume the staircase "
             "A-base==prior-B-tail+1 equality.")}
print(f"leg4: W250+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w249bmc_20261015_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
