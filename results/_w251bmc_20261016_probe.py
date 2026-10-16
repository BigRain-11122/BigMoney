# -*- coding: utf-8 -*-
"""W251 pre-seat probe (bm-c loop window r1046, 2026-10-16 08:5x; queue-head
supply lane: upstream W250 = bm-c OWN registered+FINALIZED complete chain
(seat r1043 window origin cc06f1f4a -> prereg r1045 LANDED 4f7a130ff ->
r1046 dead-window five-face splice 29930f489 (incl disclosed print-face heal
rows 68->69) -> engine self-burn 12/12 (ledger appends 486458150+77a4f529a
batched 6+6) -> r1046 continuation finalize: ledger 974,335 EXACT
(972,135+2,200) / merged pool K=547,920 (545,720+2,200) / fivekeys ALL PASS
results/_r1046bmc_w250_fivekeys.json / sixgate ALL PASS
results/_r1046bmc_w250_sixgate.json PRE-FINALIZE phase, gate-1 anchored to
landed git blob n1 22a957f851fd3adc / pf 40b0befe37ebbe2c)
-- NO in-flight seat upstream: the W251 FREEZE is UNBLOCKED at seat time (no
waits-upstream face; the W251 freezer proceeds prereg derive + five-face splice
on the post-W250-REGISTERED universe per seat-first law O-20261010-2350-bm-c
sec.2, prereg derive = next window FIRST ACTION).
Standing CEO fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x +
O-20261013 22:1x CPU standing-open + O-20260924-1730 claim-ignite same-round
law + never-dry supply line O-1819 + O-20261015-0025 full mobilization.
Universe face = post-W250-REGISTERED (live registry, 240 owner rows:
bm-a 129 / bm-b 41 / bm-c 70 incl W250; W251 candidate = 241st wave,
bm-c 71st owned).
Anticipated face (W250 prereg sec.5 item5 + W250 probe leg4, honest forward
face): naive W251 A continuation 567_501..569_500 first-clean hops=0 (no live
refusers) / naive B 545_301..545_500 REFUSED at start (SEED_REGISTRY seed
545_500 + W240..W249 A-ladder refusal face) -- the pre-W250 projected B
first-clean 565_501..565_700 is now INSIDE the registered W250 A band
565_501..567_500 = the post-W250 walk must hop past it AND past the own-wave
A window; live re-derive governs either way, non-rotational r587
forward-monotone enforced in-walk; never transcribe r587.
Bloodline: _w250bmc_20261016_probe.py derive machinery verbatim, W251 facts
live-registry-driven; leg0 extended with the W249->W250 chain-relation
anchors leg (+2,200/+2,200) and the no-skip-claim leg (W252/W253 inbox
vacancy -- seat numbering stays dense)."""
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
receipt = {"probe": "W251 pre-seat probe (bm-c loop r1046 window, 2026-10-16 08:5x, queue-head supply lane: upstream W250 = bm-c OWN registered+FINALIZED complete chain (r1046 continuation finalize ledger 974,335 / K=547,920); NO in-flight seat upstream -- W251 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing + O-20261015-0025 full mobilization; universe = post-W250-REGISTERED 240 owner rows)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W247..W250 landed faces + chain-relation anchors ---
keys = sorted(N1_BANDS)
w250_splice_landed = 250 in N1_BANDS
assert w250_splice_landed, "leg0 failed: W250 splice not landed (registry row absent -- r1046 splice face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 251))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert 251 not in N1_BANDS, "leg0 failed: W251 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W251 universe honestly, do not seat on a stale universe)"

W247_A = tuple(N1_BANDS[247]["a"])
W247_B = tuple(N1_BANDS[247]["b_exit"])
assert W247_A == (559_501, 561_500) and W247_B == (544_501, 544_700) and \
    N1_BANDS[247].get("engine_owner") == "bm-a", "leg0 failed: W247 registry row drift (bm-a splice+finalize face)"

W248_A = tuple(N1_BANDS[248]["a"])
W248_B = tuple(N1_BANDS[248]["b_exit"])
assert W248_A == (561_501, 563_500) and W248_B == (544_701, 544_900) and \
    N1_BANDS[248].get("engine_owner") == "bm-c", "leg0 failed: W248 registry row drift (bm-c r1036 absorb splice face)"

W249_A = tuple(N1_BANDS[249]["a"])
W249_B = tuple(N1_BANDS[249]["b_exit"])
assert W249_A == (563_501, 565_500) and W249_B == (544_901, 545_100) and \
    N1_BANDS[249].get("engine_owner") == "bm-c", "leg0 failed: W249 registry row drift (bm-c r1042 splice face)"

W250_A = tuple(N1_BANDS[250]["a"])
W250_B = tuple(N1_BANDS[250]["b_exit"])
assert W250_A == (565_501, 567_500) and W250_B == (545_101, 545_300) and \
    N1_BANDS[250].get("engine_owner") == "bm-c", "leg0 failed: W250 registry row drift (bm-c r1046 splice face)"
assert W250_A[0] == W249_A[1] + 1, \
    "leg0 failed: W250 A base != W249 A tail+1 (seed-gap A-continuation face drift)"
assert W250_B[0] == W249_B[1] + 1, \
    "leg0 failed: W250 B base != W249 B tail+1 (clean arithmetic continuation face drift)"

for _w in (248, 249, 250):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

w249_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w249_results.json")
w249_out = json.load(open(w249_results, encoding="utf-8"))
w249_led = (w249_out.get("science_gates") or {}).get("ledger") or {}
w249_total = w249_led.get("total")
w249_merged_n = None
try:
    w249_merged_n = w249_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w249_total == 972_135 and w249_merged_n == 545_720, \
    f"leg0 failed: W249 finalize anchors drift: total={w249_total} merged={w249_merged_n} (expect 972,135 / 545,720)"

w250_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w250_results.json")
w250_out = json.load(open(w250_results, encoding="utf-8"))
w250_led = (w250_out.get("science_gates") or {}).get("ledger") or {}
w250_total = w250_led.get("total")
w250_merged_n = None
w250_klift = None
try:
    w250_merged_n = w250_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
try:
    w250_klift = w250_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
except Exception:
    pass
assert w250_total == 974_335 and w250_merged_n == 547_920, \
    f"leg0 failed: W250 finalize anchors drift: total={w250_total} merged={w250_merged_n} (expect 974,335 / 547,920)"
assert w250_total == w249_total + 2_200 and w250_merged_n == w249_merged_n + 2_200, \
    "leg0 failed: W249->W250 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w250_klift is not None and abs(w250_klift) <= 0.02, \
    f"leg0 failed: W250 K-lift out-of-band at seat time: {w250_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 240 and len(bmc_rows) == 70, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 240/70 post-W250-splice, W251 unregistered)"
ordinal = owner_total + 1
assert ordinal == 241, f"leg0 ordinal derive: {ordinal} != 241"
assert len(bma_rows) == 129, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 129 post-W250-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"
bmc_ordinal = len(bmc_rows) + 1
assert bmc_ordinal == 71, f"leg0 bmc ordinal derive: {bmc_ordinal} != 71"

# --- leg 0.5: no-skip-claim leg (seat numbering density) + chain-complete face --
out_inbox = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
all_inbox = out_inbox.splitlines()
w251_seats_pre = [ln for ln in all_inbox if "w251" in ln.lower() and "seat" in ln.lower()]
assert w251_seats_pre == [], f"leg0.5 failed: W251 seat already claimed on origin: {w251_seats_pre} (vacancy broken -- yield per fleet README sec.4)"
skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w252", "w253")) and "seat" in ln.lower()]
assert skip_claims == [], f"leg0.5 failed: skip-ahead seat claims exist (W252/W253 without W251 seated -- seat-numbering density violated): {skip_claims}"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W250-registered+FINALIZED (bm-c own-wave complete)",
    "w250_splice_landed": w250_splice_landed,
    "w250_bands": {"A": list(W250_A), "B": list(W250_B)},
    "w249_bands": {"A": list(W249_A), "B": list(W249_B)},
    "w250_finalize_landed": True,
    "w250_finalize_anchors": {"ledger_total": w250_total, "merged_n": w250_merged_n,
                               "skill_line_delta_k_lift": w250_klift},
    "chain_relation": {"w249_total": w249_total, "w250_total": w250_total,
                        "ledger_delta": w250_total - w249_total,
                        "k_delta": w250_merged_n - w249_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W250 complete: registered+FINALIZED; the W251 FREEZE is UNBLOCKED at seat time -- prereg derive = next window FIRST ACTION on the post-W250 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal, "bmc_ordinal": bmc_ordinal,
    "bmc_ordinal_note": ("bm-c 71st owned [W248, W249, W250, now W251 -- attempt-continuity: "
                          "live derive governs r359]; engine wave ordinal = "
                          "240 registry owner rows + this candidate = 241st"),
    "anchor": ("W250 registered+FINALIZED own-wave (bm-c seat r1043-window origin cc06f1f4a + prereg "
               "4f7a130ff + r1046 splice 29930f489 (incl disclosed print-face heal rows 68->69) + "
               "engine self-burn 12/12 (ledger appends 486458150+77a4f529a) + r1046 continuation "
               "finalize: ledger 974,335 EXACT (972,135+2,200) / K=547,920 "
               "(545,720+2,200) / fivekeys ALL PASS results/_r1046bmc_w250_fivekeys.json / "
               "sixgate ALL PASS results/_r1046bmc_w250_sixgate.json PRE-FINALIZE phase, gate-1 "
               "anchored to landed git blob n1 22a957f851fd3adc / pf 40b0befe37ebbe2c) -- this W251 SEAT "
               "= queue-head supply per seat-first law O-20261010-2350 sec.2 (seats never queue "
               "behind freeze windows; standing CEO fill-order + O-20261013 22:1x CPU "
               "standing-open + O-20261015-0025 full mobilization + never-dry O-1819); the W251 "
               "FREEZE is UNBLOCKED (no in-flight seat upstream): the freezer proceeds prereg "
               "derive + five-face splice re-derived on the post-W250 universe")}
print(f"leg0: {len(N1_BANDS)} rows tail=W250-registered+FINALIZED (bm-c own-wave complete, W251 unregistered), W250 face=registry A={W250_A} B={W250_B}, chain-relation W249->W250 ledger 972,135->974,335 (+2,200) K 545,720->547,920 (+2,200) OK, owner={owner_total} -> W251=241st wave candidate, bm-c 71st owned")
print("leg0.5: no W251 seat claim on origin (vacancy held) + zero skip-ahead W252/W253 seat claims (numbering density green) + waits-upstream=NONE (W251 freeze UNBLOCKED)")

# --- W251 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox2 = r_vac.stdout.decode("utf-8").splitlines()
w251_seats = [ln for ln in all_inbox2 if "w251" in ln.lower() and "seat" in ln.lower()]
assert w251_seats == [], f"vacancy failed: W251 seats already exist: {w251_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '251: {"a": (' not in out_pf, "vacancy failed: W251 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W251"' not in outn1_vac, "vacancy failed: W251 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W251_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W251 per-wave prereg ALREADY on origin"
print("vacancy: W251 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the W250 REGISTERED tails ------------------
ARITH_A = (W250_A[1] + 1, W250_A[1] + WIDTH_A)
ARITH_B = (W250_B[1] + 1, W250_B[1] + WIDTH_B)


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
assert fc_a[0] == ARITH_A[0], ("leg1 A refused at naive start (W250 prereg sec.5 item5 + "
                                "W250 probe leg4 anticipated first-clean 567_501..569_500 hops=0 "
                                "on this universe; never transcribe r587 -- if this fires the "
                                "universe changed: re-read the live trace honestly)")
assert not overlaps(fc_a, W249_A) and not overlaps(fc_a, W249_B), \
    "leg1 failed: A overlaps prior-wave W249 registered bands"
assert not overlaps(fc_a, W250_A) and not overlaps(fc_a, W250_B), \
    "leg1 failed: A overlaps prior-wave W250 registered bands"
assert fc_a[0] >= W250_B[1] + 1, \
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
# B honest face: naive start REFUSED (W250 prereg sec.5 item5 projection: seed 545_500 +
# W240..W249 A-ladder refusal face); the walk governs -- record the trace verbatim.
assert fc_b[0] > ARITH_B[0] or hops_b == 0, \
    "leg1 B walk non-rotational/governance violation"
assert fc_b[0] > W250_B[1], \
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W249_A) and not overlaps(fc_b, W249_B), \
    "leg1 failed: B overlaps prior-wave W249 registered bands"
assert not overlaps(fc_b, W250_A) and not overlaps(fc_b, W250_B), \
    "leg1 failed: B overlaps prior-wave W250 registered bands"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace_own,
    "B_naive": list(ARITH_B), "B_naive_refused_at_start": fc_b[0] != ARITH_B[0] or hops_b > 0,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "B_lands_above_own_A": fc_b[0] > fc_a[1],
    "A_semantics": ("A arithmetic continuation from the REGISTERED W250 A tail "
                    "567_500+1 = 567_501..569_500 is CLEAN at naive start on the "
                    "post-W250-REGISTERED universe (fourteenth consecutive seed-gap "
                    "A-continuation face, anticipated by the W250 prereg sec.5 item5 + "
                    "W250 probe leg4 and confirmed live; never transcribe r587); A base = "
                    "first clean window, forward-monotone non-rotational r587 enforced "
                    "in-walk; A base >= registered prior-wave B tail+1 floor relation"),
    "B_semantics": ("B walk from the REGISTERED W250 B tail 545_300+1 = 545_301 is "
                    "REFUSED at naive start (SEED_REGISTRY seed 545_500 + the W240..W249 "
                    "A-ladder bands, per the W250 prereg sec.5 item5 projection) -- the "
                    "pre-W250 projected first-clean 565_501..565_700 is now INSIDE the "
                    "registered W250 A band 565_501..567_500, so the post-W250 walk hops "
                    "past it AND past the own-wave A window (own-A reservation standard "
                    "leg); B_hop lands-inside-A=false leg; live trace recorded verbatim"),
    "relation_asserts": {"A_clean_at_naive_start": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": fc_b[0] == ARITH_B[0] and hops_b == 0,
                          "B_base_above_W250_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "W249_W250_bands_respected_A": True,
                          "W249_W250_bands_respected_B": True}}
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

# --- leg 4: W252+ naive projection (pre-W251 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W252p_A_naive": f"{pA[0]}..{pA[1]}", "W252p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W252p_A_naive_refusers_seeds": pA_refusers,
    "W252p_B_naive": f"{pB[0]}..{pB[1]}", "W252p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W252p_B_lands_inside_W252p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W252+ projection on the pre-W251 universe (assuming the W251 seat bands "
             "declared here register verbatim). The W252 freezer MUST re-derive on the "
             "post-W251 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587; seed-gap face inherited from W239..W250: "
             "A/B decoupled, re-read the live trace, do NOT assume the staircase "
             "A-base==prior-B-tail+1 equality.")}
print(f"leg4: W252+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w251bmc_20261016_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
