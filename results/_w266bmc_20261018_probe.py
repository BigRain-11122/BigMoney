# -*- coding: utf-8 -*-
"""W266 pre-seat probe (bm-c loop window r1084 continuation, 2026-10-18 07:xx;
queue-head supply lane: upstream W265 = bm-c OWN WAVE complete chain
(seat MSG-20261017-2241-bmc-w266[-w265]-seat origin 7343e3650 -> prereg
freeze e57215a2c r1081 -> five-face splice a47517f792 r1084 dead-window
(engine self-burn 12/12 shards batched ledger appends 93298b7e33+c72805837c)
-> sixgate PRE-FINALIZE ALL PASS 27th consecutive r1084 -> finalize one-pass
n1_w265_results.json r1084 ledger 1,007,335 EXACT (1,005,135+2,200) / merged
pool K=580,920 EXACT (578,720+2,200) + fivekeys 6/6 + sec.7/8 backfilled
r1084-continuation THIS WINDOW)
-- NO in-flight seat upstream: the W266 FREEZE is UNBLOCKED at seat time.
Universe face = post-W265-REGISTERED (live registry, 255 owner rows: bm-a 130
/ bm-b 41 / bm-c 84 incl W265; W266 candidate = 256th wave). STAIRCASE
CONTINUATION face (W265 prereg sec.5 item5 pre-disclosure + W265 probe leg4
projection both named it; live re-derive governs r587): naive W266 A
continuation 600_301..602_300 is REFUSED at the REGISTERED W265 B band
600_301..600_500 -> A hops past 600_500 to first-clean 600_501..602_500
(FIFTEENTH consecutive A-hop expected); naive B 600_501..600_700 is CLEAN
at naive BUT lands INSIDE the own-wave A first-clean window -> own-A
reservation hops B past 602_500 to first-clean 602_501..602_700 (SIXTEENTH
consecutive above-own-A expected; B base==own-A tail+1 floor).
Bloodline: _w265bmc_20261017_probe.py derive machinery verbatim
(walk/gates/constants), W266 facts live-registry-driven, compact re-authoring
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
receipt = {"probe": "W266 pre-seat probe (bm-c loop r1084 continuation window, 2026-10-18 07:xx, queue-head supply lane: upstream W265 = bm-c OWN WAVE complete chain (finalize ledger 1,007,335 / K=580,920 landed r1084 chain); NO in-flight seat upstream -- W266 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; universe = post-W265-REGISTERED 255 owner rows)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W263..W265 landed faces + chain-relation anchors ---
keys = sorted(N1_BANDS)
w265_splice_landed = 265 in N1_BANDS
assert w265_splice_landed, "leg0 failed: W265 splice not landed (registry row absent -- r1084 dead-window splice face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 266))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert 266 not in N1_BANDS, "leg0 failed: W266 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W266 universe honestly, do not seat on a stale universe)"

W263_A = tuple(N1_BANDS[263]["a"])
W263_B = tuple(N1_BANDS[263]["b_exit"])
assert W263_A == (593_901, 595_900) and W263_B == (595_901, 596_100) and \
    N1_BANDS[263].get("engine_owner") == "bm-a", "leg0 failed: W263 registry row drift (bm-a r1038 splice face)"

W264_A = tuple(N1_BANDS[264]["a"])
W264_B = tuple(N1_BANDS[264]["b_exit"])
assert W264_A == (596_101, 598_100) and W264_B == (598_101, 598_300) and \
    N1_BANDS[264].get("engine_owner") == "bm-c", "leg0 failed: W264 registry row drift (bm-c r1076 splice face)"

W265_A = tuple(N1_BANDS[265]["a"])
W265_B = tuple(N1_BANDS[265]["b_exit"])
assert W265_A == (598_301, 600_300) and W265_B == (600_301, 600_500) and \
    N1_BANDS[265].get("engine_owner") == "bm-c", "leg0 failed: W265 registry row drift (bm-c r1084 dead-window splice a47517f792 face)"
assert W265_A[0] == W264_B[1] + 1, \
    "leg0 failed: W265 A base != W264 B tail+1 (staircase-affects-A fourteenth consecutive hop face drift)"
assert W265_B[0] == W265_A[1] + 1, \
    "leg0 failed: W265 B base != own-A tail+1 (above-own-A fifteenth consecutive face drift)"

for _w in (263, 264, 265):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

w264_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w264_results.json"), encoding="utf-8"))
w264_led = (w264_out.get("science_gates") or {}).get("ledger") or {}
w264_total = w264_led.get("total")
w264_merged_n = w264_out["null_pool_cumulative"]["merged"]["n_values"]

w265_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w265_results.json"), encoding="utf-8"))
w265_led = (w265_out.get("science_gates") or {}).get("ledger") or {}
w265_total = w265_led.get("total")
w265_merged_n = w265_out["null_pool_cumulative"]["merged"]["n_values"]
w265_klift = w265_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
assert w264_total == 1_005_135 and w264_merged_n == 578_720, \
    f"leg0 failed: W264 finalize anchors drift: total={w264_total} merged={w264_merged_n} (expect 1,005,135 / 578,720)"
assert w265_total == 1_007_335 and w265_merged_n == 580_920, \
    f"leg0 failed: W265 finalize anchors drift: total={w265_total} merged={w265_merged_n} (expect 1,007,335 / 580,920)"
assert w265_total == w264_total + 2_200 and w265_merged_n == w264_merged_n + 2_200, \
    "leg0 failed: W264->W265 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w265_klift is not None and abs(w265_klift) <= 0.02, \
    f"leg0 failed: W265 K-lift out-of-band at seat time: {w265_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 255 and len(bmc_rows) == 84, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 255/84 post-W265-splice, W266 unregistered)"
ordinal = owner_total + 1
assert ordinal == 256, f"leg0 ordinal derive: {ordinal} != 256"
assert len(bma_rows) == 130, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 130 post-W265-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"

# --- leg 0.5: no-skip-claim leg (seat numbering density) + chain-complete face --
out_inbox = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
all_inbox = out_inbox.splitlines()
w266_seats_pre = [ln for ln in all_inbox if "w266" in ln.lower() and "seat" in ln.lower()]
assert w266_seats_pre == [], f"leg0.5 failed: W266 seat already claimed on origin: {w266_seats_pre} (vacancy broken -- yield per fleet README sec.4)"
skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w267", "w268")) and "seat" in ln.lower()]
assert skip_claims == [], f"leg0.5 failed: skip-ahead seat claims exist (W267/W268 numbering density violated): {skip_claims}"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W265-registered+FINALIZED (bm-c own-wave complete r1084 chain)",
    "w265_bands": {"A": list(W265_A), "B": list(W265_B)},
    "w264_bands": {"A": list(W264_A), "B": list(W264_B)},
    "w265_finalize_landed": True,
    "w265_finalize_anchors": {"ledger_total": w265_total, "merged_n": w265_merged_n,
                                "skill_line_delta_k_lift": w265_klift},
    "chain_relation": {"w264_total": w264_total, "w265_total": w265_total,
                       "ledger_delta": w265_total - w264_total,
                       "k_delta": w265_merged_n - w264_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W265 complete: registered+FINALIZED r1084 chain; the W266 FREEZE is UNBLOCKED at seat time -- prereg derive = next window FIRST ACTION on the post-W265 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal,
}
print(f"leg0: {len(N1_BANDS)} rows tail=W265-registered+FINALIZED (bm-c own-wave complete r1084 chain, W266 unregistered), W265 face=registry A={W265_A} B={W265_B}, chain-relation W264->W265 ledger 1,005,135->1,007,335 (+2,200) K 578,720->580,920 (+2,200) OK, owner={owner_total} -> W266=256th wave candidate")
print("leg0.5: no W266 seat claim on origin (vacancy held) + zero skip-ahead W267/W268 seat claims (numbering density green) + waits-upstream=NONE (W266 freeze UNBLOCKED)")

# --- W266 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox2 = r_vac.stdout.decode("utf-8").splitlines()
w266_seats = [ln for ln in all_inbox2 if "w266" in ln.lower() and "seat" in ln.lower()]
assert w266_seats == [], f"vacancy failed: W266 seats already exist: {w266_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '266: {"a": (' not in out_pf, "vacancy failed: W266 row ALREADY on origin (r511 tail-lock)"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W266"' not in outn1_vac, "vacancy failed: W266 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W266_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W266 per-wave prereg ALREADY on origin"
print("vacancy: W266 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the W265 REGISTERED tails ------------------
ARITH_A = (W265_A[1] + 1, W265_A[1] + WIDTH_A)
ARITH_B = (W265_B[1] + 1, W265_B[1] + WIDTH_B)


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
assert fc_a == (600_501, 602_500) and hops_a == 1, ("leg1 A staircase face: live walk refused "
                                "the naive start 600_301..602_300 at the REGISTERED W265 B band "
                                "600_301..600_500 (staircase-affects-A FIFTEENTH consecutive hop; "
                                "the W265 prereg sec.5 item5 + W265 probe leg4 pre-W265-universe "
                                "projection was superseded live per r587; if this "
                                "fires the universe changed again: re-read the live trace honestly)")
assert not overlaps(fc_a, W263_A) and not overlaps(fc_a, W263_B), \
    "leg1 failed: A overlaps prior-wave W263 registered bands"
assert not overlaps(fc_a, W264_A) and not overlaps(fc_a, W264_B), \
    "leg1 failed: A overlaps prior-wave W264 registered bands"
assert not overlaps(fc_a, W265_A) and not overlaps(fc_a, W265_B), \
    "leg1 failed: A overlaps prior-wave W265 registered bands"
assert fc_a[0] >= W265_B[1] + 1, \
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
# B honest face: naive start 600_501..600_700 CLEAN at naive BUT lands INSIDE the own-wave
# W266 A first-clean window 600_501..602_500 (own-A reservation face, cascade per the W265
# probe leg4 + prereg sec.5 item5 projections, superseded live per r587); walk governs.
assert fc_b[0] > ARITH_B[0] or hops_b == 0, \
    "leg1 B walk non-rotational/governance violation"
assert fc_b[0] > W265_B[1], \
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W263_A) and not overlaps(fc_b, W263_B), \
    "leg1 failed: B overlaps prior-wave W263 registered bands"
assert not overlaps(fc_b, W264_A) and not overlaps(fc_b, W264_B), \
    "leg1 failed: B overlaps prior-wave W264 registered bands"
assert not overlaps(fc_b, W265_A) and not overlaps(fc_b, W265_B), \
    "leg1 failed: B overlaps prior-wave W265 registered bands"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace_own,
    "B_naive": list(ARITH_B), "B_naive_refused_at_start": fc_b[0] != ARITH_B[0] or hops_b > 0,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "B_lands_above_own_A": fc_b[0] > fc_a[1],
    "A_semantics": ("A arithmetic continuation from the REGISTERED W265 A tail "
                    "600_300+1 = 600_301..602_300 is REFUSED at naive start on the "
                    "post-W265-REGISTERED universe (the REGISTERED W265 B band "
                    "600_301..600_500 sits INSIDE the naive A window: staircase-"
                    "affects-A FIFTEENTH consecutive A-hop, superseding the W265 "
                    "prereg sec.5 item5 pre-W265-universe projection per r587); "
                    "the walk hops past the W265 B tail 600_500 -> A first-clean "
                    "600_501..602_500 (hops=1); forward-monotone non-rotational r587 "
                    "enforced in-walk; A base >= registered prior-wave B tail+1 floor"),
    "B_semantics": ("B walk from the REGISTERED W265 B tail 600_500+1 = 600_501 is "
                    "CLEAN at naive start but the naive window 600_501..600_700 lands "
                    "INSIDE the own-wave W266 A first-clean window 600_501..602_500 "
                    "(own-A reservation cascade face, per the W265 probe leg4 + "
                    "prereg sec.5 item5 projection faces superseded live) -- the "
                    "own-A reservation standard leg hops B past the own-wave A tail "
                    "602_500 -> first-clean 602_501..602_700 (B lands above own-A, "
                    "base==own-A tail+1 face, SIXTEENTH consecutive above-own-A); "
                    "B_hop lands-inside-A=false leg; live trace recorded verbatim"),
    "relation_asserts": {"A_clean_at_naive_start": False,
                          "A_staircase_hop_past_W265_B": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": fc_b[0] == ARITH_B[0] and hops_b == 0,
                          "B_base_above_W265_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "B_lands_above_own_A": True,
                          "W263_W264_W265_bands_respected_A": True,
                          "W263_W264_W265_bands_respected_B": True}}
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

# --- leg 4: W267+ naive projection (pre-W266 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W267p_A_naive": f"{pA[0]}..{pA[1]}", "W267p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W267p_A_naive_refusers_seeds": pA_refusers,
    "W267p_B_naive": f"{pB[0]}..{pB[1]}", "W267p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W267p_B_lands_inside_W267p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W267+ projection on the pre-W266 universe (assuming the W266 seat bands "
             "declared here register verbatim). ONCE W266 REGISTERS, the naive W267 A "
             "start 602_501 is REFUSED by the registered W266 B band 602_501..602_700 "
             "(staircase-affects-A SIXTEENTH consecutive A-hop expected) AND the W267 B "
             "naive start lands inside the own-A reservation face; the W267 freezer "
             "MUST re-derive on the post-W266 universe AND reserve the own-wave A "
             "window when deriving B -- never transcribe r587; staircase face "
             "continuing since W251 (A hops over prior B; B lands above own-A): "
             "re-read the live trace, do NOT assume the A-base==prior-B-tail+1 or "
             "B-base==own-A-tail+1 equalities.")}
print(f"leg4: W267+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w266bmc_20261018_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
