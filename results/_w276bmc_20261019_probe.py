# -*- coding: utf-8 -*-
"""W276 pre-seat probe (bm-c loop window r1109, 2026-10-19 ~05:5x;
queue-head supply lane: upstream W275 = bm-c OWN WAVE complete chain
(seat MSG-20261019-034x-bmc-w275-seat origin bf4bbbde1 -> prereg freeze
e4e1ce44f5afd03b 1fcc0bc30f r1107 -> five-face splice
CLEAN-AT-BIRTH 8th gen 018782314d r1108
(setwave birth-station presence gates _set_wave(275):1/(274):0/(273):0 held;
clean-at-birth 8th generation, zero heals of any class) + engine
self-burn 12/12 appender-batched 5089f02250+e639699d59
-> sixgate PRE-FINALIZE ALL PASS 38th consecutive r1108 + finalize one-pass
n1_w275_results.json r1108 ledger 1,029,335 EXACT (1,027,135+2,200) / merged
pool K=602,920 EXACT (600,720+2,200) + fivekeys 6/6 + sec.7/8 backfilled
r1108 cycle estate fc01636095 + closeout c77ee358f5) -- NO in-flight seat upstream: the W276 FREEZE is
UNBLOCKED at seat time. Universe face = post-W275-REGISTERED (live registry,
265 owner rows: bm-a 130 / bm-b 41 / bm-c 94 incl W275; W276 candidate =
266th wave, bm-c 95th own wave).
STAIRCASE CONTINUATION face (W275 probe receipt leg4 note named it; live
re-derive governs r587): naive W276 A continuation 622_301..624_300 is
REFUSED at the REGISTERED W275 B band 622_301..622_500 -> A hops past
622_500 to first-clean 622_501..624_500 (TWENTY-FIFTH consecutive A-hop
expected); B naive 622_501..622_700 is CLEAN vs registered BUT lands INSIDE
the own-wave A first-clean window -> own-A reservation hops B past 624_500
to first-clean 624_501..624_700 (TWENTY-SIXTH consecutive above-own-A
expected; B base==own-A tail+1 floor).
Bloodline: _w275bmc_20261019_probe.py derive machinery verbatim
(walk/gates/constants), W276 facts live-registry-driven, compact re-authoring
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
receipt = {"probe": "W276 pre-seat probe (bm-c loop r1109 window, 2026-10-19 ~05:5x, queue-head supply lane: upstream W275 = bm-c OWN WAVE complete chain (finalize ledger 1,029,335 / K=602,920 landed r1108 chain); NO in-flight seat upstream -- W276 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; universe = post-W275-REGISTERED 265 owner rows)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W273..W275 landed faces + chain-relation anchors ---
keys = sorted(N1_BANDS)
w275_splice_landed = 275 in N1_BANDS
assert w275_splice_landed, "leg0 failed: W275 splice not landed (registry row absent -- r1108 splice face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 276))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert 276 not in N1_BANDS, "leg0 failed: W276 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W276 universe honestly, do not seat on a stale universe)"

W273_A = tuple(N1_BANDS[273]["a"])
W273_B = tuple(N1_BANDS[273]["b_exit"])
assert W273_A == (615_901, 617_900) and W273_B == (617_901, 618_100) and \
    N1_BANDS[273].get("engine_owner") == "bm-c", "leg0 failed: W273 registry row drift (bm-c r1102 clean-at-birth 6th-gen splice 04f2127db face)"

W274_A = tuple(N1_BANDS[274]["a"])
W274_B = tuple(N1_BANDS[274]["b_exit"])
assert W274_A == (618_101, 620_100) and W274_B == (620_101, 620_300) and \
    N1_BANDS[274].get("engine_owner") == "bm-c", "leg0 failed: W274 registry row drift (bm-c r1105 clean-at-birth 7th-gen splice ec907d164 face)"

W275_A = tuple(N1_BANDS[275]["a"])
W275_B = tuple(N1_BANDS[275]["b_exit"])
assert W275_A == (620_301, 622_300) and W275_B == (622_301, 622_500) and \
    N1_BANDS[275].get("engine_owner") == "bm-c", "leg0 failed: W275 registry row drift (bm-c r1108 clean-at-birth 8th-gen splice 018782314d face)"
assert W275_A[0] == W274_B[1] + 1, \
    "leg0 failed: W275 A base != W274 B tail+1 (staircase-affects-A twenty-fourth consecutive hop face drift)"
assert W275_B[0] == W275_A[1] + 1, \
    "leg0 failed: W275 B base != own-A tail+1 (above-own-A twenty-fifth consecutive face drift)"

for _w in (273, 274, 275):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

w273_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w273_results.json"), encoding="utf-8"))
w273_led = (w273_out.get("science_gates") or {}).get("ledger") or {}
w273_total = w273_led.get("total")
w273_merged_n = w273_out["null_pool_cumulative"]["merged"]["n_values"]

w274_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w274_results.json"), encoding="utf-8"))
w274_led = (w274_out.get("science_gates") or {}).get("ledger") or {}
w274_total = w274_led.get("total")
w274_merged_n = w274_out["null_pool_cumulative"]["merged"]["n_values"]

w275_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w275_results.json"), encoding="utf-8"))
w275_led = (w275_out.get("science_gates") or {}).get("ledger") or {}
w275_total = w275_led.get("total")
w275_merged_n = w275_out["null_pool_cumulative"]["merged"]["n_values"]
w275_klift = w275_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
assert w273_total == 1_024_935 and w273_merged_n == 598_520, \
    f"leg0 failed: W273 finalize anchors drift: total={w273_total} merged={w273_merged_n} (expect 1,024,935 / 598,520)"
assert w274_total == 1_027_135 and w274_merged_n == 600_720, \
    f"leg0 failed: W274 finalize anchors drift: total={w274_total} merged={w274_merged_n} (expect 1,027,135 / 600,720)"
assert w275_total == 1_029_335 and w275_merged_n == 602_920, \
    f"leg0 failed: W275 finalize anchors drift: total={w275_total} merged={w275_merged_n} (expect 1,029,335 / 602,920)"
assert w274_total == w273_total + 2_200 and w274_merged_n == w273_merged_n + 2_200, \
    "leg0 failed: W273->W274 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w275_total == w274_total + 2_200 and w275_merged_n == w274_merged_n + 2_200, \
    "leg0 failed: W274->W275 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w275_klift is not None and abs(w275_klift) <= 0.02, \
    f"leg0 failed: W275 K-lift out-of-band at seat time: {w275_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 265 and len(bmc_rows) == 94, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 265/94 post-W275-splice, W276 unregistered)"
ordinal = owner_total + 1
assert ordinal == 266, f"leg0 ordinal derive: {ordinal} != 266"
assert len(bma_rows) == 130, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 130 post-W275-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

# --- leg 0.5: no-skip-claim leg (seat numbering density) + chain-complete face --
out_inbox = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
all_inbox = out_inbox.splitlines()
w276_seats_pre = [ln for ln in all_inbox if "w276" in ln.lower() and "seat" in ln.lower()]
assert w276_seats_pre == [], f"leg0.5 failed: W276 seat already claimed on origin: {w276_seats_pre} (vacancy broken -- yield per fleet README sec.4)"
skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w277", "w278")) and "seat" in ln.lower()]
assert skip_claims == [], f"leg0.5 failed: skip-ahead seat claims exist (W277/W278 numbering density violated): {skip_claims}"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W275-registered+FINALIZED (bm-c own-wave complete r1108 chain)",
    "w275_bands": {"A": list(W275_A), "B": list(W275_B)},
    "w274_bands": {"A": list(W274_A), "B": list(W274_B)},
    "w275_finalize_landed": True,
    "w275_finalize_anchors": {"ledger_total": w275_total, "merged_n": w275_merged_n,
                                "skill_line_delta_k_lift": w275_klift},
    "chain_relation": {"w273_total": w273_total, "w274_total": w274_total,
                       "w275_total": w275_total,
                       "ledger_delta": w275_total - w274_total,
                       "k_delta": w275_merged_n - w274_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W275 complete: registered+FINALIZED r1108 chain; the W276 FREEZE is UNBLOCKED at seat time -- prereg derive = same-window/next-window FIRST ACTION on the post-W275 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal,
}
print(f"leg0: {len(N1_BANDS)} rows tail=W275-registered+FINALIZED (bm-c own-wave complete r1108 chain, W276 unregistered), W275 face=registry A={W275_A} B={W275_B}, chain-relation W273->W274->W275 ledger 1,024,935->1,027,135->1,029,335 (+2,200/+2,200) K 598,520->600,720->602,920 (+2,200/+2,200) OK, owner={owner_total} -> W276=266th wave candidate")
print("leg0.5: no W276 seat claim on origin (vacancy held) + zero skip-ahead W277/W278 seat claims (numbering density green) + waits-upstream=NONE (W276 freeze UNBLOCKED)")

# --- W276 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox2 = r_vac.stdout.decode("utf-8").splitlines()
w276_seats = [ln for ln in all_inbox2 if "w276" in ln.lower() and "seat" in ln.lower()]
assert w276_seats == [], f"vacancy failed: W276 seats already exist: {w276_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '276: {"a": (' not in out_pf, "vacancy failed: W276 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W276"' not in outn1_vac, "vacancy failed: W276 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W276_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W276 per-wave prereg ALREADY on origin"
print("vacancy: W276 origin vacancy held (no seat / row / configs / prereg)")

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
ARITH_A = (W275_A[1] + 1, W275_A[1] + WIDTH_A)
ARITH_B = (W275_B[1] + 1, W275_B[1] + WIDTH_B)


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
assert fc_a == (622_501, 624_500) and hops_a == 1, ("leg1 A staircase face: live walk refused "
                                "the naive start 622_301..624_300 at the REGISTERED W275 B band "
                                "622_301..622_500 (staircase-affects-A TWENTY-FIFTH consecutive hop; "
                                "the W275 probe receipt leg4 note projection confirmed live per r587 -- "
                                "live walk governs; if this fires the universe changed again: "
                                "re-read the live trace honestly)")
assert not overlaps(fc_a, W273_A) and not overlaps(fc_a, W273_B), \
    "leg1 failed: A overlaps prior-wave W273 registered bands"
assert not overlaps(fc_a, W274_A) and not overlaps(fc_a, W274_B), \
    "leg1 failed: A overlaps prior-wave W274 registered bands"
assert not overlaps(fc_a, W275_A) and not overlaps(fc_a, W275_B), \
    "leg1 failed: A overlaps prior-wave W275 registered bands"
assert fc_a[0] >= W275_B[1] + 1, \
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
# B honest face: naive start 622_501..622_700 CLEAN vs registered BUT lands INSIDE the own-wave
# W276 A first-clean window 622_501..624_500 (own-A reservation face, cascade per the W275
# probe receipt leg4 note projection, superseded live per r587); walk governs.
assert fc_b[0] > ARITH_B[0] or hops_b == 0, \
    "leg1 B walk non-rotational/governance violation"
assert fc_b[0] > W275_B[1], \
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W273_A) and not overlaps(fc_b, W273_B), \
    "leg1 failed: B overlaps prior-wave W273 registered bands"
assert not overlaps(fc_b, W274_A) and not overlaps(fc_b, W274_B), \
    "leg1 failed: B overlaps prior-wave W274 registered bands"
assert not overlaps(fc_b, W275_A) and not overlaps(fc_b, W275_B), \
    "leg1 failed: B overlaps prior-wave W275 registered bands"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace_own,
    "B_naive": list(ARITH_B), "B_naive_refused_at_start": fc_b[0] != ARITH_B[0] or hops_b > 0,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "B_lands_above_own_A": fc_b[0] > fc_a[1],
    "A_semantics": ("A arithmetic continuation from the REGISTERED W275 A tail "
                    "622_300+1 = 622_301..624_300 is REFUSED at naive start on the "
                    "post-W275-REGISTERED universe (the REGISTERED W275 B band "
                    "622_301..622_500 sits INSIDE the naive A window: staircase-"
                    "affects-A TWENTY-FIFTH consecutive A-hop, confirming the W275 "
                    "probe receipt leg4 note projection live per r587; live walk "
                    "governs); the walk hops past the W275 B tail 622_500 -> A "
                    "first-clean 622_501..624_500 (hops=1); forward-monotone "
                    "non-rotational r587 enforced in-walk; A base >= registered "
                    "prior-wave B tail+1 floor"),
    "B_semantics": ("B walk from the REGISTERED W275 B tail 622_500+1 = 622_501 is "
                    "CLEAN at naive start vs the registered universe but the naive "
                    "window 622_501..622_700 lands INSIDE the own-wave W276 A "
                    "first-clean window 622_501..624_500 (own-A reservation cascade "
                    "face, per the W275 probe receipt leg4 note projection "
                    "confirmed live) -- the own-A reservation standard leg hops B "
                    "past the own-wave A tail 624_500 -> first-clean 624_501..624_700 "
                    "(B lands above own-A, base==own-A tail+1 face, TWENTY-SIXTH "
                    "consecutive above-own-A); B_hop lands-inside-A=false leg; live "
                    "trace recorded verbatim"),
    "relation_asserts": {"A_clean_at_naive_start": False,
                          "A_staircase_hop_past_W275_B": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": fc_b[0] == ARITH_B[0] and hops_b == 0,
                          "B_base_above_W275_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "B_lands_above_own_A": True,
                          # r1100 heal: the seat-time clone left these two labels
                          # one triple stale; the overlap checks above were already
                          # vs W273/W274/W275 registered bands (correct) -- labels
                          # rolled to the candidate-below triple, disclosed in the
                          # W272 freeze receipt + round report.
                          "W273_W274_W275_bands_respected_A": True,
                          "W273_W274_W275_bands_respected_B": True}}
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

# --- leg 4: W277+ naive projection (pre-W276 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W277p_A_naive": f"{pA[0]}..{pA[1]}", "W277p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W277p_A_naive_refusers_seeds": pA_refusers,
    "W277p_B_naive": f"{pB[0]}..{pB[1]}", "W277p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W277p_B_lands_inside_W277p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W277+ projection on the pre-W276 universe (assuming the W276 seat bands "
             "declared here register verbatim). ONCE W276 REGISTERS, the naive W277 A "
             "start 624_501 is REFUSED by the registered W276 B band (live-derived at "
             "W276 seat time; expected 624_501..624_700) "
             "(staircase-affects-A TWENTY-SIXTH consecutive A-hop expected) AND the W277 B "
             "naive start lands inside the own-A reservation face; the W277 freezer "
             "MUST re-derive on the post-W276 universe AND reserve the own-wave A "
             "window when deriving B -- never transcribe r587; staircase face "
             "continuing since W251 (A hops over prior B; B lands above own-A): "
             "re-read the live trace, do NOT assume the A-base==prior-B-tail+1 or "
             "B-base==own-A-tail+1 equalities.")}
print(f"leg4: W277+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w276bmc_20261019_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
