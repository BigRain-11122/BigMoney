# -*- coding: utf-8 -*-
"""W269 pre-seat probe (bm-c loop window r1091, 2026-10-18 ~14:2x;
queue-head supply lane: upstream W268 = bm-c OWN WAVE complete chain
(seat MSG-20261018-1229-bmc-w268-seat origin b9ad2f1119 -> prereg freeze
f1ec8231c7 r1090 -> five-face splice CLEAN-AT-BIRTH 8bc7ac759e r1091
(derive editor p3_setwave_rootcure rep + phase5 presence gates prevented
the r1076-family setwave defect at the birth station; zero surgical heals;
estate carries clean n1 1fd82f1d5ad28e36) + engine self-burn 12/12
-> sixgate PRE-FINALIZE ALL PASS 31st consecutive r1091 + finalize one-pass
n1_w268_results.json r1091 ledger 1,013,935 EXACT (1,011,735+2,200) / merged
pool K=587,520 EXACT (585,320+2,200) + fivekeys 6/6 + sec.7/8 backfilled
r1091) -- NO in-flight seat upstream: the W269 FREEZE is UNBLOCKED at seat
time. Universe face = post-W268-REGISTERED (live registry, 258 owner rows:
bm-a 130 / bm-b 41 / bm-c 87 incl W268; W269 candidate = 259th wave).
STAIRCASE CONTINUATION face (W268 probe receipt leg4 note named it; live
re-derive governs r587): naive W269 A continuation 606_901..608_900 is
REFUSED at the REGISTERED W268 B band 606_901..607_100 -> A hops past
607_100 to first-clean 607_101..609_100 (EIGHTEENTH consecutive A-hop
expected); B naive 607_101..607_300 is CLEAN vs registered BUT lands INSIDE
the own-wave A first-clean window -> own-A reservation hops B past 609_100
to first-clean 609_101..609_300 (NINETEENTH consecutive above-own-A
expected; B base==own-A tail+1 floor).
Bloodline: _w268bmc_20261018_probe.py derive machinery verbatim
(walk/gates/constants), W269 facts live-registry-driven, compact re-authoring
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
receipt = {"probe": "W269 pre-seat probe (bm-c loop r1091 window, 2026-10-18 ~14:2x, queue-head supply lane: upstream W268 = bm-c OWN WAVE complete chain (finalize ledger 1,013,935 / K=587,520 landed r1091 chain); NO in-flight seat upstream -- W269 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; universe = post-W268-REGISTERED 258 owner rows)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W266..W268 landed faces + chain-relation anchors ---
keys = sorted(N1_BANDS)
w268_splice_landed = 268 in N1_BANDS
assert w268_splice_landed, "leg0 failed: W268 splice not landed (registry row absent -- r1091 splice face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 269))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert 269 not in N1_BANDS, "leg0 failed: W269 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W269 universe honestly, do not seat on a stale universe)"

W266_A = tuple(N1_BANDS[266]["a"])
W266_B = tuple(N1_BANDS[266]["b_exit"])
assert W266_A == (600_501, 602_500) and W266_B == (602_501, 602_700) and \
    N1_BANDS[266].get("engine_owner") == "bm-c", "leg0 failed: W266 registry row drift (bm-c r1086 absorb-landed splice dc71ecc3f9 face)"

W267_A = tuple(N1_BANDS[267]["a"])
W267_B = tuple(N1_BANDS[267]["b_exit"])
assert W267_A == (602_701, 604_700) and W267_B == (604_701, 604_900) and \
    N1_BANDS[267].get("engine_owner") == "bm-c", "leg0 failed: W267 registry row drift (bm-c r1088 splice 7b9e9377 + setwave root-cure face)"

W268_A = tuple(N1_BANDS[268]["a"])
W268_B = tuple(N1_BANDS[268]["b_exit"])
assert W268_A == (604_901, 606_900) and W268_B == (606_901, 607_100) and \
    N1_BANDS[268].get("engine_owner") == "bm-c", "leg0 failed: W268 registry row drift (bm-c r1091 clean-at-birth splice 8bc7ac759e face)"
assert W268_A[0] == W267_B[1] + 1, \
    "leg0 failed: W268 A base != W267 B tail+1 (staircase-affects-A seventeenth consecutive hop face drift)"
assert W268_B[0] == W268_A[1] + 1, \
    "leg0 failed: W268 B base != own-A tail+1 (above-own-A eighteenth consecutive face drift)"

for _w in (266, 267, 268):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

w266_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w266_results.json"), encoding="utf-8"))
w266_led = (w266_out.get("science_gates") or {}).get("ledger") or {}
w266_total = w266_led.get("total")
w266_merged_n = w266_out["null_pool_cumulative"]["merged"]["n_values"]

w267_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w267_results.json"), encoding="utf-8"))
w267_led = (w267_out.get("science_gates") or {}).get("ledger") or {}
w267_total = w267_led.get("total")
w267_merged_n = w267_out["null_pool_cumulative"]["merged"]["n_values"]

w268_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w268_results.json"), encoding="utf-8"))
w268_led = (w268_out.get("science_gates") or {}).get("ledger") or {}
w268_total = w268_led.get("total")
w268_merged_n = w268_out["null_pool_cumulative"]["merged"]["n_values"]
w268_klift = w268_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
assert w266_total == 1_009_535 and w266_merged_n == 583_120, \
    f"leg0 failed: W266 finalize anchors drift: total={w266_total} merged={w266_merged_n} (expect 1,009,535 / 583,120)"
assert w267_total == 1_011_735 and w267_merged_n == 585_320, \
    f"leg0 failed: W267 finalize anchors drift: total={w267_total} merged={w267_merged_n} (expect 1,011,735 / 585,320)"
assert w268_total == 1_013_935 and w268_merged_n == 587_520, \
    f"leg0 failed: W268 finalize anchors drift: total={w268_total} merged={w268_merged_n} (expect 1,013,935 / 587,520)"
assert w267_total == w266_total + 2_200 and w267_merged_n == w266_merged_n + 2_200, \
    "leg0 failed: W266->W267 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w268_total == w267_total + 2_200 and w268_merged_n == w267_merged_n + 2_200, \
    "leg0 failed: W267->W268 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w268_klift is not None and abs(w268_klift) <= 0.02, \
    f"leg0 failed: W268 K-lift out-of-band at seat time: {w268_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 258 and len(bmc_rows) == 87, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 258/87 post-W268-splice, W269 unregistered)"
ordinal = owner_total + 1
assert ordinal == 259, f"leg0 ordinal derive: {ordinal} != 259"
assert len(bma_rows) == 130, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 130 post-W268-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

# --- leg 0.5: no-skip-claim leg (seat numbering density) + chain-complete face --
out_inbox = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
all_inbox = out_inbox.splitlines()
w269_seats_pre = [ln for ln in all_inbox if "w269" in ln.lower() and "seat" in ln.lower()]
assert w269_seats_pre == [], f"leg0.5 failed: W269 seat already claimed on origin: {w269_seats_pre} (vacancy broken -- yield per fleet README sec.4)"
skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w270", "w271")) and "seat" in ln.lower()]
assert skip_claims == [], f"leg0.5 failed: skip-ahead seat claims exist (W270/W271 numbering density violated): {skip_claims}"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W268-registered+FINALIZED (bm-c own-wave complete r1091 chain)",
    "w268_bands": {"A": list(W268_A), "B": list(W268_B)},
    "w267_bands": {"A": list(W267_A), "B": list(W267_B)},
    "w268_finalize_landed": True,
    "w268_finalize_anchors": {"ledger_total": w268_total, "merged_n": w268_merged_n,
                                "skill_line_delta_k_lift": w268_klift},
    "chain_relation": {"w266_total": w266_total, "w267_total": w267_total,
                       "w268_total": w268_total,
                       "ledger_delta": w268_total - w267_total,
                       "k_delta": w268_merged_n - w267_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W268 complete: registered+FINALIZED r1091 chain; the W269 FREEZE is UNBLOCKED at seat time -- prereg derive = next window FIRST ACTION on the post-W268 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal,
}
print(f"leg0: {len(N1_BANDS)} rows tail=W268-registered+FINALIZED (bm-c own-wave complete r1091 chain, W269 unregistered), W268 face=registry A={W268_A} B={W268_B}, chain-relation W266->W267->W268 ledger 1,009,535->1,011,735->1,013,935 (+2,200/+2,200) K 583,120->585,320->587,520 (+2,200/+2,200) OK, owner={owner_total} -> W269=259th wave candidate")
print("leg0.5: no W269 seat claim on origin (vacancy held) + zero skip-ahead W270/W271 seat claims (numbering density green) + waits-upstream=NONE (W269 freeze UNBLOCKED)")

# --- W269 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox2 = r_vac.stdout.decode("utf-8").splitlines()
w269_seats = [ln for ln in all_inbox2 if "w269" in ln.lower() and "seat" in ln.lower()]
assert w269_seats == [], f"vacancy failed: W269 seats already exist: {w269_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '269: {"a": (' not in out_pf, "vacancy failed: W269 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W269"' not in outn1_vac, "vacancy failed: W269 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W269_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W269 per-wave prereg ALREADY on origin"
print("vacancy: W269 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the W268 REGISTERED tails ------------------
ARITH_A = (W268_A[1] + 1, W268_A[1] + WIDTH_A)
ARITH_B = (W268_B[1] + 1, W268_B[1] + WIDTH_B)


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
assert fc_a == (607_101, 609_100) and hops_a == 1, ("leg1 A staircase face: live walk refused "
                                "the naive start 606_901..608_900 at the REGISTERED W268 B band "
                                "606_901..607_100 (staircase-affects-A EIGHTEENTH consecutive hop; "
                                "the W268 probe receipt leg4 note projection confirmed live per r587 -- "
                                "live walk governs; if this fires the universe changed again: "
                                "re-read the live trace honestly)")
assert not overlaps(fc_a, W266_A) and not overlaps(fc_a, W266_B), \
    "leg1 failed: A overlaps prior-wave W266 registered bands"
assert not overlaps(fc_a, W267_A) and not overlaps(fc_a, W267_B), \
    "leg1 failed: A overlaps prior-wave W267 registered bands"
assert not overlaps(fc_a, W268_A) and not overlaps(fc_a, W268_B), \
    "leg1 failed: A overlaps prior-wave W268 registered bands"
assert fc_a[0] >= W268_B[1] + 1, \
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
# B honest face: naive start 607_101..607_300 CLEAN vs registered BUT lands INSIDE the own-wave
# W269 A first-clean window 607_101..609_100 (own-A reservation face, cascade per the W268
# probe receipt leg4 note projection, superseded live per r587); walk governs.
assert fc_b[0] > ARITH_B[0] or hops_b == 0, \
    "leg1 B walk non-rotational/governance violation"
assert fc_b[0] > W268_B[1], \
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W266_A) and not overlaps(fc_b, W266_B), \
    "leg1 failed: B overlaps prior-wave W266 registered bands"
assert not overlaps(fc_b, W267_A) and not overlaps(fc_b, W267_B), \
    "leg1 failed: B overlaps prior-wave W267 registered bands"
assert not overlaps(fc_b, W268_A) and not overlaps(fc_b, W268_B), \
    "leg1 failed: B overlaps prior-wave W268 registered bands"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace_own,
    "B_naive": list(ARITH_B), "B_naive_refused_at_start": fc_b[0] != ARITH_B[0] or hops_b > 0,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "B_lands_above_own_A": fc_b[0] > fc_a[1],
    "A_semantics": ("A arithmetic continuation from the REGISTERED W268 A tail "
                    "606_900+1 = 606_901..608_900 is REFUSED at naive start on the "
                    "post-W268-REGISTERED universe (the REGISTERED W268 B band "
                    "606_901..607_100 sits INSIDE the naive A window: staircase-"
                    "affects-A EIGHTEENTH consecutive A-hop, confirming the W268 "
                    "probe receipt leg4 note projection live per r587; live walk "
                    "governs); the walk hops past the W268 B tail 607_100 -> A "
                    "first-clean 607_101..609_100 (hops=1); forward-monotone "
                    "non-rotational r587 enforced in-walk; A base >= registered "
                    "prior-wave B tail+1 floor"),
    "B_semantics": ("B walk from the REGISTERED W268 B tail 607_100+1 = 607_101 is "
                    "CLEAN at naive start vs the registered universe but the naive "
                    "window 607_101..607_300 lands INSIDE the own-wave W269 A "
                    "first-clean window 607_101..609_100 (own-A reservation cascade "
                    "face, per the W268 probe receipt leg4 note projection "
                    "confirmed live) -- the own-A reservation standard leg hops B "
                    "past the own-wave A tail 609_100 -> first-clean 609_101..609_300 "
                    "(B lands above own-A, base==own-A tail+1 face, NINETEENTH "
                    "consecutive above-own-A); B_hop lands-inside-A=false leg; live "
                    "trace recorded verbatim"),
    "relation_asserts": {"A_clean_at_naive_start": False,
                          "A_staircase_hop_past_W268_B": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": fc_b[0] == ARITH_B[0] and hops_b == 0,
                          "B_base_above_W268_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "B_lands_above_own_A": True,
                          "W266_W267_W268_bands_respected_A": True,
                          "W266_W267_W268_bands_respected_B": True}}
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

# --- leg 4: W270+ naive projection (pre-W269 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W270p_A_naive": f"{pA[0]}..{pA[1]}", "W270p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W270p_A_naive_refusers_seeds": pA_refusers,
    "W270p_B_naive": f"{pB[0]}..{pB[1]}", "W270p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W270p_B_lands_inside_W270p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W270+ projection on the pre-W269 universe (assuming the W269 seat bands "
             "declared here register verbatim). ONCE W269 REGISTERS, the naive W270 A "
             "start 609_101 is REFUSED by the registered W269 B band 609_101..609_300 "
             "(staircase-affects-A NINETEENTH consecutive A-hop expected) AND the W270 B "
             "naive start lands inside the own-A reservation face; the W270 freezer "
             "MUST re-derive on the post-W269 universe AND reserve the own-wave A "
             "window when deriving B -- never transcribe r587; staircase face "
             "continuing since W251 (A hops over prior B; B lands above own-A): "
             "re-read the live trace, do NOT assume the A-base==prior-B-tail+1 or "
             "B-base==own-A-tail+1 equalities.")}
print(f"leg4: W270+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w269bmc_20261018_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
