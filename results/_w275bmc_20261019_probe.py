# -*- coding: utf-8 -*-
"""W275 pre-seat probe (bm-c loop window r1106, 2026-10-19 ~03:4x;
queue-head supply lane: upstream W274 = bm-c OWN WAVE complete chain
(seat MSG-20261019-012x-bmc-w274-seat origin 70b21a0264 -> prereg freeze
ddc158b5047596ea CAS-graft 6f31f6e073 r1104 -> five-face splice
CLEAN-AT-BIRTH 7th gen ec907d164 r1105
(setwave birth-station presence gates _set_wave(274):1/(273):0/(272):0 held;
clean-at-birth 7th generation, 2 disclosed heals all pre-splice
authoring faces, zero engine-mechanics heal) + engine
self-burn 12/12 appender-batched b3c8a83c5c+b4c0271044
-> sixgate PRE-FINALIZE ALL PASS 37th consecutive r1105 + finalize one-pass
n1_w274_results.json r1105 ledger 1,027,135 EXACT (1,024,935+2,200) / merged
pool K=600,720 EXACT (598,520+2,200) + fivekeys 6/6 + sec.7/8 backfilled
r1105 cycle estate acf37937ec + closeout c4e752d682) -- NO in-flight seat upstream: the W275 FREEZE is
UNBLOCKED at seat time. Universe face = post-W274-REGISTERED (live registry,
264 owner rows: bm-a 130 / bm-b 41 / bm-c 93 incl W274; W275 candidate =
265th wave, bm-c 94th own wave).
STAIRCASE CONTINUATION face (W274 probe receipt leg4 note named it; live
re-derive governs r587): naive W275 A continuation 620_101..622_100 is
REFUSED at the REGISTERED W274 B band 620_101..620_300 -> A hops past
620_300 to first-clean 620_301..622_300 (TWENTY-FOURTH consecutive A-hop
expected); B naive 620_301..620_500 is CLEAN vs registered BUT lands INSIDE
the own-wave A first-clean window -> own-A reservation hops B past 622_300
to first-clean 622_301..622_500 (TWENTY-FIFTH consecutive above-own-A
expected; B base==own-A tail+1 floor).
Bloodline: _w274bmc_20261019_probe.py derive machinery verbatim
(walk/gates/constants), W275 facts live-registry-driven, compact re-authoring
this window per r971 large-task honest-split law; live walk governs, never
transcribed r587."""
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
receipt = {"probe": "W275 pre-seat probe (bm-c loop r1106 window, 2026-10-19 ~03:4x, queue-head supply lane: upstream W274 = bm-c OWN WAVE complete chain (finalize ledger 1,027,135 / K=600,720 landed r1105 chain); NO in-flight seat upstream -- W275 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; universe = post-W274-REGISTERED 264 owner rows)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W272..W274 landed faces + chain-relation anchors ---
keys = sorted(N1_BANDS)
w274_splice_landed = 274 in N1_BANDS
assert w274_splice_landed, "leg0 failed: W274 splice not landed (registry row absent -- r1105 splice face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 275))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert 275 not in N1_BANDS, "leg0 failed: W275 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W275 universe honestly, do not seat on a stale universe)"

W272_A = tuple(N1_BANDS[272]["a"])
W272_B = tuple(N1_BANDS[272]["b_exit"])
assert W272_A == (613_701, 615_700) and W272_B == (615_701, 615_900) and \
    N1_BANDS[272].get("engine_owner") == "bm-c", "leg0 failed: W272 registry row drift (bm-c r1100 clean-at-birth 5th-gen splice c99ee20a4 face)"

W273_A = tuple(N1_BANDS[273]["a"])
W273_B = tuple(N1_BANDS[273]["b_exit"])
assert W273_A == (615_901, 617_900) and W273_B == (617_901, 618_100) and \
    N1_BANDS[273].get("engine_owner") == "bm-c", "leg0 failed: W273 registry row drift (bm-c r1102 clean-at-birth 6th-gen splice 04f2127db face)"

W274_A = tuple(N1_BANDS[274]["a"])
W274_B = tuple(N1_BANDS[274]["b_exit"])
assert W274_A == (618_101, 620_100) and W274_B == (620_101, 620_300) and \
    N1_BANDS[274].get("engine_owner") == "bm-c", "leg0 failed: W274 registry row drift (bm-c r1105 clean-at-birth 7th-gen splice ec907d164 face)"
assert W274_A[0] == W273_B[1] + 1, \
    "leg0 failed: W274 A base != W273 B tail+1 (staircase-affects-A twenty-third consecutive hop face drift)"
assert W274_B[0] == W274_A[1] + 1, \
    "leg0 failed: W274 B base != own-A tail+1 (above-own-A twenty-fourth consecutive face drift)"

for _w in (272, 273, 274):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

w272_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w272_results.json"), encoding="utf-8"))
w272_led = (w272_out.get("science_gates") or {}).get("ledger") or {}
w272_total = w272_led.get("total")
w272_merged_n = w272_out["null_pool_cumulative"]["merged"]["n_values"]

w273_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w273_results.json"), encoding="utf-8"))
w273_led = (w273_out.get("science_gates") or {}).get("ledger") or {}
w273_total = w273_led.get("total")
w273_merged_n = w273_out["null_pool_cumulative"]["merged"]["n_values"]

w274_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w274_results.json"), encoding="utf-8"))
w274_led = (w274_out.get("science_gates") or {}).get("ledger") or {}
w274_total = w274_led.get("total")
w274_merged_n = w274_out["null_pool_cumulative"]["merged"]["n_values"]
w274_klift = w274_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
assert w272_total == 1_022_735 and w272_merged_n == 596_320, \
    f"leg0 failed: W272 finalize anchors drift: total={w272_total} merged={w272_merged_n} (expect 1,022,735 / 596,320)"
assert w273_total == 1_024_935 and w273_merged_n == 598_520, \
    f"leg0 failed: W273 finalize anchors drift: total={w273_total} merged={w273_merged_n} (expect 1,024,935 / 598,520)"
assert w274_total == 1_027_135 and w274_merged_n == 600_720, \
    f"leg0 failed: W274 finalize anchors drift: total={w274_total} merged={w274_merged_n} (expect 1,027,135 / 600,720)"
assert w273_total == w272_total + 2_200 and w273_merged_n == w272_merged_n + 2_200, \
    "leg0 failed: W272->W273 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w274_total == w273_total + 2_200 and w274_merged_n == w273_merged_n + 2_200, \
    "leg0 failed: W273->W274 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w274_klift is not None and abs(w274_klift) <= 0.02, \
    f"leg0 failed: W274 K-lift out-of-band at seat time: {w274_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 264 and len(bmc_rows) == 93, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 264/93 post-W274-splice, W275 unregistered)"
ordinal = owner_total + 1
assert ordinal == 265, f"leg0 ordinal derive: {ordinal} != 265"
assert len(bma_rows) == 130, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 130 post-W274-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

# --- leg 0.5: no-skip-claim leg (seat numbering density) + chain-complete face --
out_inbox = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
all_inbox = out_inbox.splitlines()
w275_seats_pre = [ln for ln in all_inbox if "w275" in ln.lower() and "seat" in ln.lower()]
assert w275_seats_pre == [], f"leg0.5 failed: W275 seat already claimed on origin: {w275_seats_pre} (vacancy broken -- yield per fleet README sec.4)"
skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w276", "w277")) and "seat" in ln.lower()]
assert skip_claims == [], f"leg0.5 failed: skip-ahead seat claims exist (W276/W277 numbering density violated): {skip_claims}"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W274-registered+FINALIZED (bm-c own-wave complete r1105 chain)",
    "w274_bands": {"A": list(W274_A), "B": list(W274_B)},
    "w273_bands": {"A": list(W273_A), "B": list(W273_B)},
    "w274_finalize_landed": True,
    "w274_finalize_anchors": {"ledger_total": w274_total, "merged_n": w274_merged_n,
                                "skill_line_delta_k_lift": w274_klift},
    "chain_relation": {"w272_total": w272_total, "w273_total": w273_total,
                       "w274_total": w274_total,
                       "ledger_delta": w274_total - w273_total,
                       "k_delta": w274_merged_n - w273_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W274 complete: registered+FINALIZED r1105 chain; the W275 FREEZE is UNBLOCKED at seat time -- prereg derive = same-window/next-window FIRST ACTION on the post-W274 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal,
}
print(f"leg0: {len(N1_BANDS)} rows tail=W274-registered+FINALIZED (bm-c own-wave complete r1105 chain, W275 unregistered), W274 face=registry A={W274_A} B={W274_B}, chain-relation W272->W273->W274 ledger 1,022,735->1,024,935->1,027,135 (+2,200/+2,200) K 596,320->598,520->600,720 (+2,200/+2,200) OK, owner={owner_total} -> W275=265th wave candidate")
print("leg0.5: no W275 seat claim on origin (vacancy held) + zero skip-ahead W276/W277 seat claims (numbering density green) + waits-upstream=NONE (W275 freeze UNBLOCKED)")

# --- W275 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox2 = r_vac.stdout.decode("utf-8").splitlines()
w275_seats = [ln for ln in all_inbox2 if "w275" in ln.lower() and "seat" in ln.lower()]
assert w275_seats == [], f"vacancy failed: W275 seats already exist: {w275_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '275: {"a": (' not in out_pf, "vacancy failed: W275 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W275"' not in outn1_vac, "vacancy failed: W275 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W275_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W275 per-wave prereg ALREADY on origin"
print("vacancy: W275 origin vacancy held (no seat / row / configs / prereg)")

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS)
points |= set(PROBE_SEEDS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: honest forward walk from the W270 REGISTERED tails ------------------
ARITH_A = (W274_A[1] + 1, W274_A[1] + WIDTH_A)
ARITH_B = (W274_B[1] + 1, W274_B[1] + WIDTH_B)


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
assert fc_a == (620_301, 622_300) and hops_a == 1, ("leg1 A staircase face: live walk refused "
                                "the naive start 620_101..622_100 at the REGISTERED W274 B band "
                                "620_101..620_300 (staircase-affects-A TWENTY-FOURTH consecutive hop; "
                                "the W274 probe receipt leg4 note projection confirmed live per r587 -- "
                                "live walk governs; if this fires the universe changed again: "
                                "re-read the live trace honestly)")
assert not overlaps(fc_a, W272_A) and not overlaps(fc_a, W272_B), \
    "leg1 failed: A overlaps prior-wave W272 registered bands"
assert not overlaps(fc_a, W273_A) and not overlaps(fc_a, W273_B), \
    "leg1 failed: A overlaps prior-wave W273 registered bands"
assert not overlaps(fc_a, W274_A) and not overlaps(fc_a, W274_B), \
    "leg1 failed: A overlaps prior-wave W274 registered bands"
assert fc_a[0] >= W274_B[1] + 1, \
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
# B honest face: naive start 620_301..620_500 CLEAN vs registered BUT lands INSIDE the own-wave
# W275 A first-clean window 620_301..622_300 (own-A reservation face, cascade per the W274
# probe receipt leg4 note projection, superseded live per r587); walk governs.
assert fc_b[0] > ARITH_B[0] or hops_b == 0, \
    "leg1 B walk non-rotational/governance violation"
assert fc_b[0] > W274_B[1], \
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W272_A) and not overlaps(fc_b, W272_B), \
    "leg1 failed: B overlaps prior-wave W272 registered bands"
assert not overlaps(fc_b, W273_A) and not overlaps(fc_b, W273_B), \
    "leg1 failed: B overlaps prior-wave W273 registered bands"
assert not overlaps(fc_b, W274_A) and not overlaps(fc_b, W274_B), \
    "leg1 failed: B overlaps prior-wave W274 registered bands"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace_own,
    "B_naive": list(ARITH_B), "B_naive_refused_at_start": fc_b[0] != ARITH_B[0] or hops_b > 0,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "B_lands_above_own_A": fc_b[0] > fc_a[1],
    "A_semantics": ("A arithmetic continuation from the REGISTERED W274 A tail "
                    "620_100+1 = 620_101..622_100 is REFUSED at naive start on the "
                    "post-W274-REGISTERED universe (the REGISTERED W274 B band "
                    "620_101..620_300 sits INSIDE the naive A window: staircase-"
                    "affects-A TWENTY-FOURTH consecutive A-hop, confirming the W274 "
                    "probe receipt leg4 note projection live per r587; live walk "
                    "governs); the walk hops past the W274 B tail 620_300 -> A "
                    "first-clean 620_301..622_300 (hops=1); forward-monotone "
                    "non-rotational r587 enforced in-walk; A base >= registered "
                    "prior-wave B tail+1 floor"),
    "B_semantics": ("B walk from the REGISTERED W274 B tail 620_300+1 = 620_301 is "
                    "CLEAN at naive start vs the registered universe but the naive "
                    "window 620_301..620_500 lands INSIDE the own-wave W275 A "
                    "first-clean window 620_301..622_300 (own-A reservation cascade "
                    "face, per the W274 probe receipt leg4 note projection "
                    "confirmed live) -- the own-A reservation standard leg hops B "
                    "past the own-wave A tail 622_300 -> first-clean 622_301..622_500 "
                    "(B lands above own-A, base==own-A tail+1 face, TWENTY-FIFTH "
                    "consecutive above-own-A); B_hop lands-inside-A=false leg; live "
                    "trace recorded verbatim"),
    "relation_asserts": {"A_clean_at_naive_start": False,
                          "A_staircase_hop_past_W274_B": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": fc_b[0] == ARITH_B[0] and hops_b == 0,
                          "B_base_above_W274_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "B_lands_above_own_A": True,
                          # r1100 heal: the seat-time clone left these two labels
                          # one triple stale; the overlap checks above were already
                          # vs W272/W273/W274 registered bands (correct) -- labels
                          # rolled to the candidate-below triple, disclosed in the
                          # W272 freeze receipt + round report.
                          "W272_W273_W274_bands_respected_A": True,
                          "W272_W273_W274_bands_respected_B": True}}
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

# --- leg 4: W276+ naive projection (pre-W275 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W276p_A_naive": f"{pA[0]}..{pA[1]}", "W276p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W276p_A_naive_refusers_seeds": pA_refusers,
    "W276p_B_naive": f"{pB[0]}..{pB[1]}", "W276p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W276p_B_lands_inside_W276p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W276+ projection on the pre-W275 universe (assuming the W275 seat bands "
             "declared here register verbatim). ONCE W275 REGISTERS, the naive W276 A "
             "start 622_301 is REFUSED by the registered W275 B band (live-derived at "
             "W275 seat time; expected 622_301..622_500) "
             "(staircase-affects-A TWENTY-FIFTH consecutive A-hop expected) AND the W276 B "
             "naive start lands inside the own-A reservation face; the W276 freezer "
             "MUST re-derive on the post-W275 universe AND reserve the own-wave A "
             "window when deriving B -- never transcribe r587; staircase face "
             "continuing since W251 (A hops over prior B; B lands above own-A): "
             "re-read the live trace, do NOT assume the A-base==prior-B-tail+1 or "
             "B-base==own-A-tail+1 equalities.")}
print(f"leg4: W276+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w275bmc_20261019_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
