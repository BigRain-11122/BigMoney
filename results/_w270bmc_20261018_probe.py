# -*- coding: utf-8 -*-
"""W270 pre-seat probe (bm-c loop window r1094, 2026-10-18 ~16:0x;
queue-head supply lane: upstream W269 = bm-c OWN WAVE complete chain
(seat MSG-20261018-1407-bmc-w269-seat origin d630d043b9 -> prereg freeze
67fe12710c r1092 -> five-face splice CLEAN-AT-BIRTH 2nd gen 440b07c94b r1093
(setwave birth-station presence gates _set_wave(269):1/(268):0/(267):0 held;
zero surgical heals; estate carries clean n1 per freeze receipt) + engine
self-burn 12/12 batched self-commits 32cbe26a1c+f59af28e77
-> sixgate PRE-FINALIZE ALL PASS 32nd consecutive r1093 + finalize one-pass
n1_w269_results.json r1093 ledger 1,016,135 EXACT (1,013,935+2,200) / merged
pool K=589,720 EXACT (587,520+2,200) + fivekeys 6/6 + sec.7/8 backfilled
r1093 estate 4eb8ec87cc) -- NO in-flight seat upstream: the W270 FREEZE is
UNBLOCKED at seat time. Universe face = post-W269-REGISTERED (live registry,
259 owner rows: bm-a 130 / bm-b 41 / bm-c 88 incl W269; W270 candidate =
260th wave, bm-c 89th own wave).
STAIRCASE CONTINUATION face (W269 probe receipt leg4 note named it; live
re-derive governs r587): naive W270 A continuation 609_101..611_100 is
REFUSED at the REGISTERED W269 B band 609_101..609_300 -> A hops past
609_300 to first-clean 609_301..611_300 (NINETEENTH consecutive A-hop
expected); B naive 609_301..609_500 is CLEAN vs registered BUT lands INSIDE
the own-wave A first-clean window -> own-A reservation hops B past 611_300
to first-clean 611_301..611_500 (TWENTIETH consecutive above-own-A
expected; B base==own-A tail+1 floor).
Bloodline: _w269bmc_20261018_probe.py derive machinery verbatim
(walk/gates/constants), W270 facts live-registry-driven, compact re-authoring
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
receipt = {"probe": "W270 pre-seat probe (bm-c loop r1094 window, 2026-10-18 ~16:0x, queue-head supply lane: upstream W269 = bm-c OWN WAVE complete chain (finalize ledger 1,016,135 / K=589,720 landed r1093 chain); NO in-flight seat upstream -- W270 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; universe = post-W269-REGISTERED 259 owner rows)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W267..W269 landed faces + chain-relation anchors ---
keys = sorted(N1_BANDS)
w269_splice_landed = 269 in N1_BANDS
assert w269_splice_landed, "leg0 failed: W269 splice not landed (registry row absent -- r1093 splice face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 270))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert 270 not in N1_BANDS, "leg0 failed: W270 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W270 universe honestly, do not seat on a stale universe)"

W267_A = tuple(N1_BANDS[267]["a"])
W267_B = tuple(N1_BANDS[267]["b_exit"])
assert W267_A == (602_701, 604_700) and W267_B == (604_701, 604_900) and \
    N1_BANDS[267].get("engine_owner") == "bm-c", "leg0 failed: W267 registry row drift (bm-c r1088 splice 7b9e9377 + setwave root-cure face)"

W268_A = tuple(N1_BANDS[268]["a"])
W268_B = tuple(N1_BANDS[268]["b_exit"])
assert W268_A == (604_901, 606_900) and W268_B == (606_901, 607_100) and \
    N1_BANDS[268].get("engine_owner") == "bm-c", "leg0 failed: W268 registry row drift (bm-c r1091 clean-at-birth splice 8bc7ac759e face)"

W269_A = tuple(N1_BANDS[269]["a"])
W269_B = tuple(N1_BANDS[269]["b_exit"])
assert W269_A == (607_101, 609_100) and W269_B == (609_101, 609_300) and \
    N1_BANDS[269].get("engine_owner") == "bm-c", "leg0 failed: W269 registry row drift (bm-c r1093 clean-at-birth 2nd-gen splice 440b07c94b face)"
assert W269_A[0] == W268_B[1] + 1, \
    "leg0 failed: W269 A base != W268 B tail+1 (staircase-affects-A eighteenth consecutive hop face drift)"
assert W269_B[0] == W269_A[1] + 1, \
    "leg0 failed: W269 B base != own-A tail+1 (above-own-A nineteenth consecutive face drift)"

for _w in (267, 268, 269):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

w267_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w267_results.json"), encoding="utf-8"))
w267_led = (w267_out.get("science_gates") or {}).get("ledger") or {}
w267_total = w267_led.get("total")
w267_merged_n = w267_out["null_pool_cumulative"]["merged"]["n_values"]

w268_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w268_results.json"), encoding="utf-8"))
w268_led = (w268_out.get("science_gates") or {}).get("ledger") or {}
w268_total = w268_led.get("total")
w268_merged_n = w268_out["null_pool_cumulative"]["merged"]["n_values"]

w269_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w269_results.json"), encoding="utf-8"))
w269_led = (w269_out.get("science_gates") or {}).get("ledger") or {}
w269_total = w269_led.get("total")
w269_merged_n = w269_out["null_pool_cumulative"]["merged"]["n_values"]
w269_klift = w269_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
assert w267_total == 1_011_735 and w267_merged_n == 585_320, \
    f"leg0 failed: W267 finalize anchors drift: total={w267_total} merged={w267_merged_n} (expect 1,011,735 / 585,320)"
assert w268_total == 1_013_935 and w268_merged_n == 587_520, \
    f"leg0 failed: W268 finalize anchors drift: total={w268_total} merged={w268_merged_n} (expect 1,013,935 / 587,520)"
assert w269_total == 1_016_135 and w269_merged_n == 589_720, \
    f"leg0 failed: W269 finalize anchors drift: total={w269_total} merged={w269_merged_n} (expect 1,016,135 / 589,720)"
assert w268_total == w267_total + 2_200 and w268_merged_n == w267_merged_n + 2_200, \
    "leg0 failed: W267->W268 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w269_total == w268_total + 2_200 and w269_merged_n == w268_merged_n + 2_200, \
    "leg0 failed: W268->W269 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w269_klift is not None and abs(w269_klift) <= 0.02, \
    f"leg0 failed: W269 K-lift out-of-band at seat time: {w269_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 259 and len(bmc_rows) == 88, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 259/88 post-W269-splice, W270 unregistered)"
ordinal = owner_total + 1
assert ordinal == 260, f"leg0 ordinal derive: {ordinal} != 260"
assert len(bma_rows) == 130, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 130 post-W269-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

# --- leg 0.5: no-skip-claim leg (seat numbering density) + chain-complete face --
out_inbox = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
all_inbox = out_inbox.splitlines()
w270_seats_pre = [ln for ln in all_inbox if "w270" in ln.lower() and "seat" in ln.lower()]
assert w270_seats_pre == [], f"leg0.5 failed: W270 seat already claimed on origin: {w270_seats_pre} (vacancy broken -- yield per fleet README sec.4)"
skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w271", "w272")) and "seat" in ln.lower()]
assert skip_claims == [], f"leg0.5 failed: skip-ahead seat claims exist (W271/W272 numbering density violated): {skip_claims}"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W269-registered+FINALIZED (bm-c own-wave complete r1093 chain)",
    "w269_bands": {"A": list(W269_A), "B": list(W269_B)},
    "w268_bands": {"A": list(W268_A), "B": list(W268_B)},
    "w269_finalize_landed": True,
    "w269_finalize_anchors": {"ledger_total": w269_total, "merged_n": w269_merged_n,
                                "skill_line_delta_k_lift": w269_klift},
    "chain_relation": {"w267_total": w267_total, "w268_total": w268_total,
                       "w269_total": w269_total,
                       "ledger_delta": w269_total - w268_total,
                       "k_delta": w269_merged_n - w268_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W269 complete: registered+FINALIZED r1093 chain; the W270 FREEZE is UNBLOCKED at seat time -- prereg derive = next window FIRST ACTION on the post-W269 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal,
}
print(f"leg0: {len(N1_BANDS)} rows tail=W269-registered+FINALIZED (bm-c own-wave complete r1093 chain, W270 unregistered), W269 face=registry A={W269_A} B={W269_B}, chain-relation W267->W268->W269 ledger 1,011,735->1,013,935->1,016,135 (+2,200/+2,200) K 585,320->587,520->589,720 (+2,200/+2,200) OK, owner={owner_total} -> W270=260th wave candidate")
print("leg0.5: no W270 seat claim on origin (vacancy held) + zero skip-ahead W271/W272 seat claims (numbering density green) + waits-upstream=NONE (W270 freeze UNBLOCKED)")

# --- W270 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox2 = r_vac.stdout.decode("utf-8").splitlines()
w270_seats = [ln for ln in all_inbox2 if "w270" in ln.lower() and "seat" in ln.lower()]
assert w270_seats == [], f"vacancy failed: W270 seats already exist: {w270_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '270: {"a": (' not in out_pf, "vacancy failed: W270 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W270"' not in outn1_vac, "vacancy failed: W270 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W270_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W270 per-wave prereg ALREADY on origin"
print("vacancy: W270 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the W269 REGISTERED tails ------------------
ARITH_A = (W269_A[1] + 1, W269_A[1] + WIDTH_A)
ARITH_B = (W269_B[1] + 1, W269_B[1] + WIDTH_B)


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
assert fc_a == (609_301, 611_300) and hops_a == 1, ("leg1 A staircase face: live walk refused "
                                "the naive start 609_101..611_100 at the REGISTERED W269 B band "
                                "609_101..609_300 (staircase-affects-A NINETEENTH consecutive hop; "
                                "the W269 probe receipt leg4 note projection confirmed live per r587 -- "
                                "live walk governs; if this fires the universe changed again: "
                                "re-read the live trace honestly)")
assert not overlaps(fc_a, W267_A) and not overlaps(fc_a, W267_B), \
    "leg1 failed: A overlaps prior-wave W267 registered bands"
assert not overlaps(fc_a, W268_A) and not overlaps(fc_a, W268_B), \
    "leg1 failed: A overlaps prior-wave W268 registered bands"
assert not overlaps(fc_a, W269_A) and not overlaps(fc_a, W269_B), \
    "leg1 failed: A overlaps prior-wave W269 registered bands"
assert fc_a[0] >= W269_B[1] + 1, \
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
# B honest face: naive start 609_301..609_500 CLEAN vs registered BUT lands INSIDE the own-wave
# W270 A first-clean window 609_301..611_300 (own-A reservation face, cascade per the W269
# probe receipt leg4 note projection, superseded live per r587); walk governs.
assert fc_b[0] > ARITH_B[0] or hops_b == 0, \
    "leg1 B walk non-rotational/governance violation"
assert fc_b[0] > W269_B[1], \
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W267_A) and not overlaps(fc_b, W267_B), \
    "leg1 failed: B overlaps prior-wave W267 registered bands"
assert not overlaps(fc_b, W268_A) and not overlaps(fc_b, W268_B), \
    "leg1 failed: B overlaps prior-wave W268 registered bands"
assert not overlaps(fc_b, W269_A) and not overlaps(fc_b, W269_B), \
    "leg1 failed: B overlaps prior-wave W269 registered bands"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace_own,
    "B_naive": list(ARITH_B), "B_naive_refused_at_start": fc_b[0] != ARITH_B[0] or hops_b > 0,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "B_lands_above_own_A": fc_b[0] > fc_a[1],
    "A_semantics": ("A arithmetic continuation from the REGISTERED W269 A tail "
                    "609_100+1 = 609_101..611_100 is REFUSED at naive start on the "
                    "post-W269-REGISTERED universe (the REGISTERED W269 B band "
                    "609_101..609_300 sits INSIDE the naive A window: staircase-"
                    "affects-A NINETEENTH consecutive A-hop, confirming the W269 "
                    "probe receipt leg4 note projection live per r587; live walk "
                    "governs); the walk hops past the W269 B tail 609_300 -> A "
                    "first-clean 609_301..611_300 (hops=1); forward-monotone "
                    "non-rotational r587 enforced in-walk; A base >= registered "
                    "prior-wave B tail+1 floor"),
    "B_semantics": ("B walk from the REGISTERED W269 B tail 609_300+1 = 609_301 is "
                    "CLEAN at naive start vs the registered universe but the naive "
                    "window 609_301..609_500 lands INSIDE the own-wave W270 A "
                    "first-clean window 609_301..611_300 (own-A reservation cascade "
                    "face, per the W269 probe receipt leg4 note projection "
                    "confirmed live) -- the own-A reservation standard leg hops B "
                    "past the own-wave A tail 611_300 -> first-clean 611_301..611_500 "
                    "(B lands above own-A, base==own-A tail+1 face, TWENTIETH "
                    "consecutive above-own-A); B_hop lands-inside-A=false leg; live "
                    "trace recorded verbatim"),
    "relation_asserts": {"A_clean_at_naive_start": False,
                          "A_staircase_hop_past_W269_B": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": fc_b[0] == ARITH_B[0] and hops_b == 0,
                          "B_base_above_W269_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "B_lands_above_own_A": True,
                          "W267_W268_W269_bands_respected_A": True,
                          "W267_W268_W269_bands_respected_B": True}}
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

# --- leg 4: W271+ naive projection (pre-W270 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W271p_A_naive": f"{pA[0]}..{pA[1]}", "W271p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W271p_A_naive_refusers_seeds": pA_refusers,
    "W271p_B_naive": f"{pB[0]}..{pB[1]}", "W271p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W271p_B_lands_inside_W271p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W271+ projection on the pre-W270 universe (assuming the W270 seat bands "
             "declared here register verbatim). ONCE W270 REGISTERS, the naive W271 A "
             "start 611_301 is REFUSED by the registered W270 B band 611_301..611_500 "
             "(staircase-affects-A TWENTIETH consecutive A-hop expected) AND the W271 B "
             "naive start lands inside the own-A reservation face; the W271 freezer "
             "MUST re-derive on the post-W270 universe AND reserve the own-wave A "
             "window when deriving B -- never transcribe r587; staircase face "
             "continuing since W251 (A hops over prior B; B lands above own-A): "
             "re-read the live trace, do NOT assume the A-base==prior-B-tail+1 or "
             "B-base==own-A-tail+1 equalities.")}
print(f"leg4: W271+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w270bmc_20261018_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
