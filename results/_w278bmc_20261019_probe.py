# -*- coding: utf-8 -*-
"""W278 pre-seat probe (bm-c loop window r1114-continuation, 2026-10-19 ~10:2x;
queue-head supply lane: upstream W277 = bm-c OWN WAVE complete chain
(seat MSG-20261019-080x-bmc-w277-seat origin c5f8b88f91 -> prereg freeze
45ee1de94c7d36fd e0bc4a0ddd r1113 -> five-face splice
CLEAN-AT-BIRTH 10th gen 9e53371814 r1114
(setwave birth-station presence gates _set_wave(277):1/(276):0/(275):0 held;
clean-at-birth 10th generation, 2 disclosed editor gate-region table-heals (faces absent from canon, zero canon anomalies; r1114 editor header disclosure)) + engine
self-burn 12/12 appender-batched 0df07c846b+644b4f8459
-> sixgate PRE-FINALIZE ALL PASS 40th consecutive r1114-continuation + finalize one-pass
n1_w277_results.json r1114-continuation ledger 1,033,735 EXACT (1,031,535+2,200) / merged
pool K=607,320 EXACT (605,120+2,200) + fivekeys 6/6 + sec.7/8 backfilled
r1114-continuation cycle estate (sixgate+finalize+fivekeys+sec78 landed same-window; closeout rides the same-window estate commit)) -- NO in-flight seat upstream: the W278 FREEZE is
UNBLOCKED at seat time. Universe face = post-W277-REGISTERED (live registry,
267 owner rows: bm-a 130 / bm-b 41 / bm-c 96 incl W277; W278 candidate =
268th wave, bm-c 97th own wave).
STAIRCASE CONTINUATION face (W277 probe receipt leg4 note named it; live
re-derive governs r587): naive W278 A continuation 626_701..628_700 is
REFUSED at the REGISTERED W277 B band 626_701..626_900 -> A hops past
626_900 to first-clean 626_901..628_900 (TWENTY-SEVENTH consecutive A-hop
expected); B naive 626_901..627_100 is CLEAN vs registered BUT lands INSIDE
the own-wave A first-clean window -> own-A reservation hops B past 628_900
to first-clean 628_901..629_100 (TWENTY-EIGHTH consecutive above-own-A
expected; B base==own-A tail+1 floor).
Bloodline: _w277bmc_20261019_probe.py derive machinery verbatim
(walk/gates/constants), W278 facts live-registry-driven, compact re-authoring
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
receipt = {"probe": "W278 pre-seat probe (bm-c loop r1114-continuation window, 2026-10-19 ~10:2x, queue-head supply lane: upstream W277 = bm-c OWN WAVE complete chain (finalize ledger 1,033,735 / K=607,320 landed r1114-continuation chain); NO in-flight seat upstream -- W278 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; universe = post-W277-REGISTERED 267 owner rows)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W275..W277 landed faces + chain-relation anchors ---
keys = sorted(N1_BANDS)
w277_splice_landed = 277 in N1_BANDS
assert w277_splice_landed, "leg0 failed: W277 splice not landed (registry row absent -- r1114 splice face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 278))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert 278 not in N1_BANDS, "leg0 failed: W278 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W278 universe honestly, do not seat on a stale universe)"

W275_A = tuple(N1_BANDS[275]["a"])
W275_B = tuple(N1_BANDS[275]["b_exit"])
assert W275_A == (620_301, 622_300) and W275_B == (622_301, 622_500) and \
    N1_BANDS[275].get("engine_owner") == "bm-c", "leg0 failed: W275 registry row drift (bm-c r1108 clean-at-birth 8th-gen splice 018782314d face)"

W276_A = tuple(N1_BANDS[276]["a"])
W276_B = tuple(N1_BANDS[276]["b_exit"])
assert W276_A == (622_501, 624_500) and W276_B == (624_501, 624_700) and \
    N1_BANDS[276].get("engine_owner") == "bm-c", "leg0 failed: W276 registry row drift (bm-c r1111 clean-at-birth 9th-gen splice 354a645155 face)"

W277_A = tuple(N1_BANDS[277]["a"])
W277_B = tuple(N1_BANDS[277]["b_exit"])
assert W277_A == (624_701, 626_700) and W277_B == (626_701, 626_900) and \
    N1_BANDS[277].get("engine_owner") == "bm-c", "leg0 failed: W277 registry row drift (bm-c r1114 clean-at-birth 10th-gen splice 9e53371814 face)"
assert W277_A[0] == W276_B[1] + 1, \
    "leg0 failed: W277 A base != W276 B tail+1 (staircase-affects-A twenty-sixth consecutive hop face drift)"
assert W277_B[0] == W277_A[1] + 1, \
    "leg0 failed: W277 B base != own-A tail+1 (above-own-A twenty-seventh consecutive face drift)"

for _w in (275, 276, 277):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

w275_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w275_results.json"), encoding="utf-8"))
w275_led = (w275_out.get("science_gates") or {}).get("ledger") or {}
w275_total = w275_led.get("total")
w275_merged_n = w275_out["null_pool_cumulative"]["merged"]["n_values"]

w276_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w276_results.json"), encoding="utf-8"))
w276_led = (w276_out.get("science_gates") or {}).get("ledger") or {}
w276_total = w276_led.get("total")
w276_merged_n = w276_out["null_pool_cumulative"]["merged"]["n_values"]

w277_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w277_results.json"), encoding="utf-8"))
w277_led = (w277_out.get("science_gates") or {}).get("ledger") or {}
w277_total = w277_led.get("total")
w277_merged_n = w277_out["null_pool_cumulative"]["merged"]["n_values"]
w277_klift = w277_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
assert w275_total == 1_029_335 and w275_merged_n == 602_920, \
    f"leg0 failed: W275 finalize anchors drift: total={w275_total} merged={w275_merged_n} (expect 1,029,335 / 602,920)"
assert w276_total == 1_031_535 and w276_merged_n == 605_120, \
    f"leg0 failed: W276 finalize anchors drift: total={w276_total} merged={w276_merged_n} (expect 1,031,535 / 605,120)"
assert w277_total == 1_033_735 and w277_merged_n == 607_320, \
    f"leg0 failed: W277 finalize anchors drift: total={w277_total} merged={w277_merged_n} (expect 1,033,735 / 607,320)"
assert w276_total == w275_total + 2_200 and w276_merged_n == w275_merged_n + 2_200, \
    "leg0 failed: W275->W276 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w277_total == w276_total + 2_200 and w277_merged_n == w276_merged_n + 2_200, \
    "leg0 failed: W276->W277 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w277_klift is not None and abs(w277_klift) <= 0.02, \
    f"leg0 failed: W277 K-lift out-of-band at seat time: {w277_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 267 and len(bmc_rows) == 96, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 267/96 post-W277-splice, W278 unregistered)"
ordinal = owner_total + 1
assert ordinal == 268, f"leg0 ordinal derive: {ordinal} != 268"
assert len(bma_rows) == 130, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 130 post-W277-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

# --- leg 0.5: no-skip-claim leg (seat numbering density) + chain-complete face --
out_inbox = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
all_inbox = out_inbox.splitlines()
w278_seats_pre = [ln for ln in all_inbox if "w278" in ln.lower() and "seat" in ln.lower()]
assert w278_seats_pre == [], f"leg0.5 failed: W278 seat already claimed on origin: {w278_seats_pre} (vacancy broken -- yield per fleet README sec.4)"
skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w279", "w280")) and "seat" in ln.lower()]
assert skip_claims == [], f"leg0.5 failed: skip-ahead seat claims exist (W279/W280 numbering density violated): {skip_claims}"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W277-registered+FINALIZED (bm-c own-wave complete r1114-continuation chain)",
    "w277_bands": {"A": list(W277_A), "B": list(W277_B)},
    "w276_bands": {"A": list(W276_A), "B": list(W276_B)},
    "w277_finalize_landed": True,
    "w277_finalize_anchors": {"ledger_total": w277_total, "merged_n": w277_merged_n,
                                "skill_line_delta_k_lift": w277_klift},
    "chain_relation": {"w275_total": w275_total, "w276_total": w276_total,
                       "w277_total": w277_total,
                       "ledger_delta": w277_total - w276_total,
                       "k_delta": w277_merged_n - w276_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W277 complete: registered+FINALIZED r1114-continuation chain; the W278 FREEZE is UNBLOCKED at seat time -- prereg derive = same-window/next-window FIRST ACTION on the post-W277 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal,
}
print(f"leg0: {len(N1_BANDS)} rows tail=W277-registered+FINALIZED (bm-c own-wave complete r1114-continuation chain, W278 unregistered), W277 face=registry A={W277_A} B={W277_B}, chain-relation W275->W276->W277 ledger 1,029,335->1,031,535->1,033,735 (+2,200/+2,200) K 602,920->605,120->607,320 (+2,200/+2,200) OK, owner={owner_total} -> W278=268th wave candidate")
print("leg0.5: no W278 seat claim on origin (vacancy held) + zero skip-ahead W279/W280 seat claims (numbering density green) + waits-upstream=NONE (W278 freeze UNBLOCKED)")

# --- W278 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox2 = r_vac.stdout.decode("utf-8").splitlines()
w278_seats = [ln for ln in all_inbox2 if "w278" in ln.lower() and "seat" in ln.lower()]
assert w278_seats == [], f"vacancy failed: W278 seats already exist: {w278_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '278: {"a": (' not in out_pf, "vacancy failed: W278 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W278"' not in outn1_vac, "vacancy failed: W278 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W278_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W278 per-wave prereg ALREADY on origin"
print("vacancy: W278 origin vacancy held (no seat / row / configs / prereg)")

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
ARITH_A = (W277_A[1] + 1, W277_A[1] + WIDTH_A)
ARITH_B = (W277_B[1] + 1, W277_B[1] + WIDTH_B)


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
assert fc_a == (626_901, 628_900) and hops_a == 1, ("leg1 A staircase face: live walk refused "
                                "the naive start 626_701..628_700 at the REGISTERED W277 B band "
                                "626_701..626_900 (staircase-affects-A TWENTY-SEVENTH consecutive hop; "
                                "the W277 probe receipt leg4 note projection confirmed live per r587 -- "
                                "live walk governs; if this fires the universe changed again: "
                                "re-read the live trace honestly)")
assert not overlaps(fc_a, W275_A) and not overlaps(fc_a, W275_B), \
    "leg1 failed: A overlaps prior-wave W275 registered bands"
assert not overlaps(fc_a, W276_A) and not overlaps(fc_a, W276_B), \
    "leg1 failed: A overlaps prior-wave W276 registered bands"
assert not overlaps(fc_a, W277_A) and not overlaps(fc_a, W277_B), \
    "leg1 failed: A overlaps prior-wave W277 registered bands"
assert fc_a[0] >= W277_B[1] + 1, \
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
# B honest face: naive start 626_901..627_100 CLEAN vs registered BUT lands INSIDE the own-wave
# W278 A first-clean window 626_901..628_900 (own-A reservation face, cascade per the W277
# probe receipt leg4 note projection, superseded live per r587); walk governs.
assert fc_b[0] > ARITH_B[0] or hops_b == 0, \
    "leg1 B walk non-rotational/governance violation"
assert fc_b[0] > W277_B[1], \
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W275_A) and not overlaps(fc_b, W275_B), \
    "leg1 failed: B overlaps prior-wave W275 registered bands"
assert not overlaps(fc_b, W276_A) and not overlaps(fc_b, W276_B), \
    "leg1 failed: B overlaps prior-wave W276 registered bands"
assert not overlaps(fc_b, W277_A) and not overlaps(fc_b, W277_B), \
    "leg1 failed: B overlaps prior-wave W277 registered bands"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace_own,
    "B_naive": list(ARITH_B), "B_naive_refused_at_start": fc_b[0] != ARITH_B[0] or hops_b > 0,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "B_lands_above_own_A": fc_b[0] > fc_a[1],
    "A_semantics": ("A arithmetic continuation from the REGISTERED W277 A tail "
                    "626_700+1 = 626_701..628_700 is REFUSED at naive start on the "
                    "post-W277-REGISTERED universe (the REGISTERED W277 B band "
                    "626_701..626_900 sits INSIDE the naive A window: staircase-"
                    "affects-A TWENTY-SEVENTH consecutive A-hop, confirming the W277 "
                    "probe receipt leg4 note projection live per r587; live walk "
                    "governs); the walk hops past the W277 B tail 626_900 -> A "
                    "first-clean 626_901..628_900 (hops=1); forward-monotone "
                    "non-rotational r587 enforced in-walk; A base >= registered "
                    "prior-wave B tail+1 floor"),
    "B_semantics": ("B walk from the REGISTERED W277 B tail 626_900+1 = 626_901 is "
                    "CLEAN at naive start vs the registered universe but the naive "
                    "window 626_901..627_100 lands INSIDE the own-wave W278 A "
                    "first-clean window 626_901..628_900 (own-A reservation cascade "
                    "face, per the W277 probe receipt leg4 note projection "
                    "confirmed live) -- the own-A reservation standard leg hops B "
                    "past the own-wave A tail 628_900 -> first-clean 628_901..629_100 "
                    "(B lands above own-A, base==own-A tail+1 face, TWENTY-EIGHTH "
                    "consecutive above-own-A); B_hop lands-inside-A=false leg; live "
                    "trace recorded verbatim"),
    "relation_asserts": {"A_clean_at_naive_start": False,
                          "A_staircase_hop_past_W277_B": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": fc_b[0] == ARITH_B[0] and hops_b == 0,
                          "B_base_above_W277_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "B_lands_above_own_A": True,
                          # r1100 heal: the seat-time clone left these two labels
                          # one triple stale; the overlap checks above were already
                          # vs W275/W276/W277 registered bands (correct) -- labels
                          # rolled to the candidate-below triple, disclosed in the
                          # W272 freeze receipt + round report.
                          "W275_W276_W277_bands_respected_A": True,
                          "W275_W276_W277_bands_respected_B": True}}
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

# --- leg 4: W279+ naive projection (pre-W278 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W279p_A_naive": f"{pA[0]}..{pA[1]}", "W279p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W279p_A_naive_refusers_seeds": pA_refusers,
    "W279p_B_naive": f"{pB[0]}..{pB[1]}", "W279p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W279p_B_lands_inside_W279p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W279+ projection on the pre-W278 universe (assuming the W278 seat bands "
             "declared here register verbatim). ONCE W278 REGISTERS, the naive W279 A "
             "start 628_901 is REFUSED by the registered W278 B band (live-derived at "
             "W278 seat time; expected 628_901..629_100) "
             "(staircase-affects-A TWENTY-EIGHTH consecutive A-hop expected) AND the W279 B "
             "naive start lands inside the own-A reservation face; the W279 freezer "
             "MUST re-derive on the post-W278 universe AND reserve the own-wave A "
             "window when deriving B -- never transcribe r587; staircase face "
             "continuing since W251 (A hops over prior B; B lands above own-A): "
             "re-read the live trace, do NOT assume the A-base==prior-B-tail+1 or "
             "B-base==own-A-tail+1 equalities.")}
print(f"leg4: W279+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w278bmc_20261019_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
